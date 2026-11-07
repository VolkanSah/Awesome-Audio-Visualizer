# -----------------------------------------------------------------------------
#  Awesome-Audio-Visualizer 1.1.0 by Volkan Sah
#  Datei:        main.py
#  Beschreibung: Hauptlogik und HotVisualizer-Klasse (Rendering, Steuerung)
# -----------------------------------------------------------------------------
#  Copyright (c) 2024-2026 Volkan Sah
#  License:      AGPL-3.0-or-later (siehe LICENSE)
#  https://github.com/VolkanSah/Awesome-Audio-Visualizer
# -----------------------------------------------------------------------------
import pygame
import os
import sys
import numpy as np
import math
import random
import colorsys
from collections import deque
import time
import tkinter as tk
from tkinter import filedialog

# -----------------------------------------------------------------------------
# import dependence
# -----------------------------------------------------------------------------
from audio import AudioDeviceManager, AudioProcessor            # live input
from fileprocessor import FileProcessor, collect_audio_files    # files + playlist
from mui import SettingsManager, UIManager, ScreenshotManager   # UI helpers
from particle import Particle                                   # beat explosion
from exporter import ExportManager                              # mp4 export
# -----------------------------------------------------------------------------
# 5. Main Visualizer Class - class HotVisualizer in main.py (this file!)
# -----------------------------------------------------------------------------
FONT_NAMES = "segoeui,arial,malgungothic,msgothic,microsoftyahei,notosanscjk,dejavusans"


class HotVisualizer:
    def __init__(self, width=1200, height=800, start_paths=None):
        pygame.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🔥 AWESOME AUDIO VISUALIZER 🔥")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Initialize managers
        self.device_manager = AudioDeviceManager()
        self.settings = SettingsManager()
        self.ui = UIManager(self.screen, self.font)
        self.screenshot_manager = ScreenshotManager()
        self.export_manager = ExportManager()

        # Visualizer State
        self.time = 0
        self.beat_flash = 0
        self.particles = []
        self.mode = 0
        self.mode_names = ["Circular Bars", "Waveform Tunnel", "Frequency Spiral", "Beat Explosion", "Matrix Rain"]
        self.color_palette_index = 0
        self.palettes = ["fire", "electric", "ocean", "rainbow", "neon"]

        # Effects state
        self.fps_history = deque(maxlen=60)
        self.tunnel_points = []
        self.matrix_drops = []
        self.init_matrix()

        # AUDIO-MODUS-STATUS
        self.audio_mode = "live"
        self.audio_processor = AudioProcessor(self.device_manager.get_default_device())
        self.file_processor = FileProcessor()

        # Playlist / chapters / clean view
        self.clean_mode = False        # H: only visuals + song title/artist
        self.auto_chapter = True       # M: every song gets its own look
        self._seen_index = -1
        self._seen_serial = 0
        self.cur_level = 0
        self.cur_peak = 0
        self._font_cache = {}
        self._title_key = None
        self._title_surfs = None
        self.notice = ""
        self.notice_until = 0
        self._last_export_status = ""

        if start_paths:
            self.load_paths(start_paths, append=False)

    # ------------------------------------------------------------------ helpers
    def notify(self, text, seconds=5):
        self.notice = text
        self.notice_until = time.time() + seconds
        print(text)

    def get_font(self, size, bold=False):
        key = (size, bold)
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont(FONT_NAMES, size, bold=bold)
        return self._font_cache[key]

    def load_paths(self, paths, append):
        files = collect_audio_files(paths)
        if not files:
            self.notify("Keine Audiodateien gefunden (mp3, wav, ogg, flac).")
            return
        fp = self.file_processor
        if self.audio_mode == "live":
            self.audio_processor.stop()
            self.audio_mode = "file"
        if append and fp.playlist:
            fp.add_to_playlist(files)
            self.notify(f"{len(files)} Titel zur Playlist hinzugefügt ({len(fp.playlist)} gesamt)")
        else:
            if fp.set_playlist(files, autoplay=True):
                self._seen_index = -1
                self.notify(f"Playlist: {len(files)} Titel")
            else:
                self.notify("Bitte warten, es wird noch geladen ...")

    def ask_files(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        try:
            return root.tk.splitlist(filedialog.askopenfilenames(
                parent=root, title="Audio auswählen (mehrere möglich)",
                filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")]))
        finally:
            root.destroy()

    def init_matrix(self):
        for x in range(0, self.screen_width, 20):
            self.matrix_drops.append({
                'x': x, 'y': random.randint(-500, 0),
                'speed': random.uniform(2, 8),
                'chars': [chr(random.randint(33, 126)) for _ in range(20)]
            })

    def get_color(self, intensity, palette_name):
        intensity = max(0, min(1, intensity))
        if palette_name == "fire":
            if intensity < 0.3: r = int(255 * intensity / 0.3); return (r, 0, 0)
            elif intensity < 0.6: g = int(255 * (intensity - 0.3) / 0.3); return (255, g, 0)
            else: b = int(255 * (intensity - 0.6) / 0.4); return (255, 255, b)
        elif palette_name in ["electric", "ocean", "rainbow", "neon"]:
            h = {"electric": 0.6 - intensity * 0.15, "ocean": 0.5 + intensity * 0.1,
                 "rainbow": intensity, "neon": 0.8 - intensity * 0.3}[palette_name]
            s = {"ocean": 1.0 - intensity * 0.3}.get(palette_name, 1.0)
            v = {"ocean": 0.3 + intensity * 0.7}.get(palette_name, 1.0)
            rgb = colorsys.hsv_to_rgb(h, s, v)
            return tuple(int(c * 255) for c in rgb)
        return (255, 255, 255)
# ----------------------------------------  draw_mode _x easyl mod this sections or ad more! ---------------------------------------------
    def draw_mode_0_circular_bars(self, fft_data):
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        bars = 120
        chunk_size = len(fft_data) // bars
        reduced_fft = [np.mean(fft_data[i:i+chunk_size]) for i in range(0, len(fft_data), chunk_size)][:bars]
        for i, amplitude in enumerate(reduced_fft):
            angle = (i / bars) * 2 * math.pi
            inner_radius = 80 + math.sin(self.time * 0.02 + i * 0.1) * 20
            outer_radius = inner_radius + amplitude * 0.5
            inner_x, inner_y = center_x + inner_radius * math.cos(angle), center_y + inner_radius * math.sin(angle)
            outer_x, outer_y = center_x + outer_radius * math.cos(angle), center_y + outer_radius * math.sin(angle)
            intensity = min(1, amplitude / 100)
            color = self.get_color(intensity, self.palettes[self.color_palette_index])
            width = max(1, int(3 + amplitude * 0.02))
            pygame.draw.line(self.screen, color, (inner_x, inner_y), (outer_x, outer_y), width)

    def draw_mode_1_waveform_tunnel(self, fft_data):
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        self.tunnel_points.append(fft_data[:200:5])
        if len(self.tunnel_points) > 50: self.tunnel_points.pop(0)
        for z, ring in enumerate(self.tunnel_points):
            z_scale = 1 - z / len(self.tunnel_points)
            if z_scale <= 0: continue
            for i, amplitude in enumerate(ring):
                angle = (i / len(ring)) * 2 * math.pi
                radius = 50 + amplitude * 0.3 * z_scale
                x = center_x + radius * math.cos(angle) * z_scale
                y = center_y + radius * math.sin(angle) * z_scale
                intensity = amplitude / 100 * z_scale
                color = self.get_color(intensity, self.palettes[self.color_palette_index])
                size = max(1, int(3 * z_scale))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

    def draw_mode_2_frequency_spiral(self, fft_data):
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        for i, amplitude in enumerate(fft_data[::5]):
            angle = i * 0.2 + self.time * 0.05
            radius = 20 + i * 0.8 + amplitude * 0.1
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
                intensity = amplitude / 100
                color = self.get_color(intensity, self.palettes[self.color_palette_index])
                size = max(1, int(2 + amplitude * 0.05))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

    def draw_mode_3_beat_explosion(self, fft_data, beat_detected):
        if beat_detected:
            center_x, center_y = self.screen_width // 2, self.screen_height // 2
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(5, 15)
                vx, vy = speed * math.cos(angle), speed * math.sin(angle)
                color = self.get_color(random.random(), self.palettes[self.color_palette_index])
                self.particles.append(Particle(center_x, center_y, vx, vy, 120, color))
            self.beat_flash = 30
        
        bar_width = self.screen_width // min(len(fft_data), 100) if len(fft_data) > 0 else self.screen_width
        for i, amplitude in enumerate(fft_data[:100]):
            bar_height = amplitude * 2
            x, y = i * bar_width, self.screen_height - bar_height
            intensity = amplitude / 100
            color = self.get_color(intensity, self.palettes[self.color_palette_index])
            pygame.draw.rect(self.screen, color, (x, y, bar_width - 1, bar_height))
        
        if self.beat_flash > 0:
            overlay = pygame.Surface((self.screen_width, self.screen_height)); overlay.set_alpha(self.beat_flash * 3); overlay.fill((255, 255, 255)); self.screen.blit(overlay, (0, 0))
            self.beat_flash -= 1

    def draw_mode_4_matrix_rain(self, fft_data):
        for drop in self.matrix_drops:
            drop['y'] += drop['speed']
            if drop['y'] > self.screen_height:
                drop['y'], drop['speed'] = random.randint(-200, -50), random.uniform(2, 8)
        
        for i, drop in enumerate(self.matrix_drops):
            fft_index = i % len(fft_data) if len(fft_data) > 0 else 0
            brightness = min(255, fft_data[fft_index] * 2) if len(fft_data) > 0 else 50
            for j, char in enumerate(drop['chars']):
                y = drop['y'] + j * 20
                if 0 <= y < self.screen_height:
                    alpha = max(0, 255 - j * 12)
                    alpha = min(alpha, brightness)
                    color = self.get_color(alpha / 255, self.palettes[self.color_palette_index])
                    text = self.ui.small_font.render(char, True, color)
                    self.screen.blit(text, (drop['x'], y))
# ----------------------------------------  draw_mode _x end ---------------------------------------------
# ----------------------------------------  update class Particles stored in particles.py ----------------

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(self.screen)

    # ------------------------------------------------------------------ overlays
    def draw_title_overlay(self):
        """Song title + artist. Drawn BEFORE the export frame is grabbed, so it
        is part of the exported video. Nothing else is."""
        fp = self.file_processor
        if self.audio_mode != "file" or not fp.is_analyzed or not (fp.title or fp.artist):
            return
        size = max(24, self.screen_height // 22)
        key = (fp.title, fp.artist, size)
        if key != self._title_key:
            big, small = self.get_font(size, True), self.get_font(int(size * 0.7))
            def make(font, text, color):
                return (font.render(text, True, color), font.render(text, True, (0, 0, 0))) if text else None
            self._title_surfs = (make(big, fp.title, (255, 255, 255)),
                                 make(small, fp.artist, (200, 200, 210)))
            self._title_key = key
        pos = fp.get_position()
        alpha = int(255 * min(1.0, (pos if pos is not None else 1.0) / 1.0))  # 1s fade-in
        y = self.screen_height - int(self.screen_height * 0.12) - size * 2
        for surfs in self._title_surfs:
            if not surfs:
                continue
            main_s, shadow_s = surfs
            x = (self.screen_width - main_s.get_width()) // 2
            shadow_s.set_alpha(alpha // 2)
            main_s.set_alpha(alpha)
            self.screen.blit(shadow_s, (x + 2, y + 2))
            self.screen.blit(main_s, (x, y))
            y += main_s.get_height() + 4

    def draw_status_overlays(self):
        """REC indicator and notices. Drawn AFTER the export frame -> not in the video."""
        ex = self.export_manager
        if ex.status != self._last_export_status:
            self._last_export_status = ex.status
            if ex.status:
                self.notify(ex.status, 8)
        y = 10
        if ex.is_recording:
            secs = ex.frames / ex.fps
            if (self.time // 30) % 2 == 0:
                pygame.draw.circle(self.screen, (255, 40, 40), (self.screen_width // 2 - 60, y + 12), 9)
            txt = self.font.render(f"REC {int(secs // 60):02d}:{int(secs % 60):02d}", True, (255, 80, 80))
            self.screen.blit(txt, (self.screen_width // 2 - 45, y))
            y += 38
        elif ex.is_finalizing:
            txt = self.font.render("Export wird fertiggestellt ...", True, (255, 200, 80))
            self.screen.blit(txt, (self.screen_width // 2 - txt.get_width() // 2, y))
            y += 38
        if self.notice and time.time() < self.notice_until:
            txt = self.get_font(24).render(self.notice, True, (255, 255, 255))
            bg = pygame.Surface((txt.get_width() + 20, txt.get_height() + 10)); bg.set_alpha(160)
            self.screen.blit(bg, (self.screen_width // 2 - bg.get_width() // 2, y))
            self.screen.blit(txt, (self.screen_width // 2 - txt.get_width() // 2, y + 5))

    def draw_ui(self, audio_processor):
        current_fps = self.clock.get_fps()
        self.fps_history.append(current_fps)
        avg_fps = np.mean(self.fps_history) if self.fps_history else 0

        mode_text = f"Mode: {self.mode_names[self.mode]} | Palette: {self.palettes[self.color_palette_index]}"
        text = self.font.render(mode_text, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        if self.settings.show_audio_info and audio_processor:
            beats, bpm = audio_processor.get_beat_stats()
            if self.audio_mode == "live":
                level, peak, sensitivity = audio_processor.current_level, audio_processor.peak_level, audio_processor.beat_sensitivity
            else:  # File Mode (values come from the main loop, no second read)
                level, peak, sensitivity = self.cur_level, self.cur_peak, 0.0
            self.ui.draw_audio_level_meter(level, peak, 10, 50)
            self.ui.draw_beat_info(beats, bpm, sensitivity, 10, 90)

        if self.settings.show_fps:
            fps_text = f"FPS: {avg_fps:.1f}"
            fps_surface = self.font.render(fps_text, True, (255, 255, 0))
            self.screen.blit(fps_surface, (self.screen_width - 120, 10))

        fp = self.file_processor
        if fp.loading:
            loading_surf = self.font.render("Analysiere Audio...", True, (255, 255, 0))
            loading_rect = loading_surf.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(loading_surf, loading_rect)

        if not self.ui.show_settings and not self.ui.show_device_menu:
            controls1 = "TAB: Settings | SPACE: Mode | C: Colors | S: Screenshot | F: Fullscreen | H: Clean view | ESC: Exit"
            text1 = pygame.font.Font(None, 20).render(controls1, True, (200, 200, 200))
            self.screen.blit(text1, (10, self.screen_height - 45))

            if self.audio_mode == 'live':
                controls2 = "MODE: Live | A: Load files | D: Devices | Q/W: Beat Sens."
            else:
                state = fp.playback_state.capitalize() if fp.is_analyzed else "Loading..."
                i, n = fp.playlist_info()
                chap = "on" if self.auto_chapter else "off"
                controls2 = (f"FILE {i}/{n} ({state}) | L: Live | A/Shift+A: Load/Add | P: Play/Pause | K: Stop | "
                             f"N/B: Next/Prev | M: Chapter look ({chap}) | R: Export")
            text2 = pygame.font.Font(None, 20).render(controls2, True, (200, 200, 200))
            self.screen.blit(text2, (10, self.screen_height - 25))

    # ------------------------------------------------------------------ export
    def start_export(self):
        fp = self.file_processor
        ex = self.export_manager
        if self.audio_mode != "file" or not fp.is_analyzed or fp.loading:
            self.notify("Export nur im File-Modus mit geladenem Track (A drücken).")
            return
        if self.ui.show_settings or self.ui.show_device_menu:
            self.ui.show_settings = self.ui.show_device_menu = False
        w, h = self.screen.get_size()
        if not ex.start(w, h):
            self.notify(ex.status)
            return
        fp.restart_track()   # export always starts at 0:00 of the current song
        self.notify("Export läuft: ab jetzt wird die Playlist bis zum Ende aufgenommen (E/R = stoppen)")

    def stop_export(self, natural_end=False):
        if self.export_manager.is_recording:
            self.export_manager.stop(natural_end)

    def grab_export_frame(self):
        ex, fp = self.export_manager, self.file_processor
        if not ex.is_recording:
            return
        if self.screen.get_size() != ex.size:
            self.notify("Fenstergröße geändert - Export gestoppt")
            self.stop_export()
            return
        n = ex.frames_due(fp.get_position())
        if n > 0:
            grab = getattr(pygame.image, 'tobytes', None) or pygame.image.tostring
            ex.write(grab(self.screen, 'RGB'), n)

    # ------------------------------------------------------------------ main loop
    def run(self):
        running = True
        fullscreen = False
        fp = self.file_processor
        ex = self.export_manager

        print("🔥 AWESOME AUDIO VISUALIZER STARTED! 🔥")

        while running:
            menu_open = self.ui.show_settings or self.ui.show_device_menu
            recording = ex.is_recording
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.DROPFILE:
                    if not recording:
                        self.load_paths([event.file], append=bool(fp.playlist) and self.audio_mode == "file")
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                    if key == pygame.K_ESCAPE:
                        if menu_open: self.ui.show_settings = self.ui.show_device_menu = False
                        else: running = False
                    elif key == pygame.K_TAB: self.ui.show_settings = not self.ui.show_settings; self.ui.show_device_menu = False
                    elif key == pygame.K_d: self.ui.show_device_menu = not self.ui.show_device_menu; self.ui.show_settings = False
                    elif key == pygame.K_r:
                        if recording: self.stop_export()
                        else: self.start_export()
                    elif key == pygame.K_e: self.stop_export()
                    elif key == pygame.K_SPACE and not menu_open: self.mode = (self.mode + 1) % len(self.mode_names)
                    elif key == pygame.K_c and not menu_open: self.color_palette_index = (self.color_palette_index + 1) % len(self.palettes)
                    elif key == pygame.K_h: self.clean_mode = not self.clean_mode
                    elif key == pygame.K_m:
                        self.auto_chapter = not self.auto_chapter
                        self.notify("Kapitel-Look: " + ("an (jeder Song bekommt einen neuen Look)" if self.auto_chapter else "aus"))
                    elif key == pygame.K_f:
                        if recording: self.notify("Vollbild-Wechsel während des Exports nicht möglich.")
                        else:
                            fullscreen = not fullscreen
                            self.screen = pygame.display.set_mode((0, 0) if fullscreen else (1200, 800), pygame.FULLSCREEN if fullscreen else 0)
                            self.screen_width, self.screen_height = self.screen.get_size()
                            self.ui.screen = self.screen
                    elif key == pygame.K_s: self.screenshot_manager.capture_and_save(self.screen)
                    elif key in (pygame.K_q, pygame.K_w) and self.audio_mode == "live":
                        change = -0.1 if key == pygame.K_q else 0.1
                        self.audio_processor.beat_sensitivity = np.clip(self.audio_processor.beat_sensitivity + change, 0.5, 3.0)
                    elif key == pygame.K_i: self.settings.show_fps = not self.settings.show_fps
                    elif key == pygame.K_o: self.settings.show_audio_info = not self.settings.show_audio_info
                    elif key == pygame.K_l:
                        if recording: self.notify("Während des Exports nicht möglich (E = Export stoppen).")
                        elif self.audio_mode != "live":
                            fp.stop()
                            self.audio_mode = "live"
                            self.audio_processor.start_stream()
                            print("Switched to Live Mode.")
                    elif key == pygame.K_a:
                        if recording: self.notify("Während des Exports nicht möglich (E = Export stoppen).")
                        elif not fp.loading:
                            files = self.ask_files()
                            if files:
                                self.load_paths(files, append=shift and self.audio_mode == "file")
                    elif key == pygame.K_p and self.audio_mode == "file": fp.toggle_play_pause()
                    elif key == pygame.K_k and self.audio_mode == "file":
                        fp.stop()
                        self.stop_export()
                    elif key == pygame.K_n and self.audio_mode == "file":
                        if recording: self.notify("Überspringen während des Exports nicht möglich.")
                        elif not fp.next_track(): self.notify("Das war der letzte Titel.")
                    elif key == pygame.K_b and self.audio_mode == "file":
                        if recording: self.notify("Zurückspringen während des Exports nicht möglich.")
                        else: fp.prev_track()
                    elif self.ui.show_device_menu:
                        if key == pygame.K_UP: self.ui.selected_menu_item = max(0, self.ui.selected_menu_item - 1)
                        elif key == pygame.K_DOWN: self.ui.selected_menu_item = min(len(self.device_manager.devices) - 1, self.ui.selected_menu_item + 1)
                        elif key == pygame.K_RETURN:
                            if self.ui.selected_menu_item < len(self.device_manager.devices):
                                new_idx = self.device_manager.devices[self.ui.selected_menu_item]['index']
                                self.audio_processor.change_device(new_idx); self.ui.show_device_menu = False

            # ---- audio source
            if self.audio_mode == "live":
                fft_data, beat_detected, _, _ = self.audio_processor.get_all_audio_data()
                active_processor = self.audio_processor
            else:
                fp.update()
                err = fp.pop_error()
                if err: self.notify(err, 8)
                fft_data, beat_detected, self.cur_level, self.cur_peak = fp.get_all_audio_data()
                active_processor = fp

                # chapter handling: a track (re)started at 0:00
                if fp.index != self._seen_index:
                    if self._seen_index != -1 and self.auto_chapter and fp.index >= 0:
                        self.mode = (self.mode + 1) % len(self.mode_names)
                        self.color_palette_index = (self.color_palette_index + 1) % len(self.palettes)
                    self._seen_index = fp.index
                if fp.track_serial != self._seen_serial:
                    self._seen_serial = fp.track_serial
                    if ex.is_recording and fp.is_analyzed:
                        label = f"{fp.artist} - {fp.title}" if fp.artist else fp.title
                        ex.begin_track(fp.file_path, fp.duration, label)
                if ex.is_recording and fp.ended_all:
                    self.stop_export(natural_end=True)

            # ---- draw: visuals + title (these two end up in the export)
            self.screen.fill((10, 10, 20))
            draw_modes = [self.draw_mode_0_circular_bars, self.draw_mode_1_waveform_tunnel, self.draw_mode_2_frequency_spiral,
                          lambda d: self.draw_mode_3_beat_explosion(d, beat_detected), self.draw_mode_4_matrix_rain]
            draw_modes[self.mode](fft_data)
            self.update_particles()
            self.draw_title_overlay()

            self.grab_export_frame()   # <- video frame = visuals + title only

            # ---- draw: everything below is for YOUR eyes only
            if not self.clean_mode:
                self.draw_ui(active_processor)
            current_device_idx = self.audio_processor.device_index if self.audio_processor else -1
            self.ui.draw_device_menu(self.device_manager.devices, current_device_idx, 50, 50)
            self.ui.draw_settings_overlay(self.settings, self.audio_processor)
            self.draw_status_overlays()

            pygame.display.flip()
            self.clock.tick(60)
            self.time += 1

        # ---- shutdown: finish a running export first, so no file is lost
        if ex.is_recording:
            ex.stop()
        ex.wait()
        self.audio_processor.stop()
        fp.stop()
        self.device_manager.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # python main.py                      -> start in live mode
    # python main.py song1.mp3 folder/    -> start directly with a playlist
    visualizer = HotVisualizer(start_paths=sys.argv[1:] or None)
    visualizer.run()
