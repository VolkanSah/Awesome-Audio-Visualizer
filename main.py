# -----------------------------------------------------------------------------
#     Awesome-Audio-Visualizer 1.0.1 by Volkan Sah
# -----------------------------------------------------------------------------
# https://github.com/VolkanSah/Awesome-Audio-Visualizer/
import pygame
import os
import sys
import numpy as np
import pyaudio
import math
import random
import colorsys
from collections import deque
import threading
import time
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import librosa
import librosa.display

# new
import subprocess
from queue import Queue
import wave


# import dependence
# -----------------------------------------------------------------------------
# 1. Audio Component:  class AudioDeviceManager, AudioProcessor in audio.py
# -----------------------------------------------------------------------------
from audio import AudioDeviceManager , AudioProcessor
# -----------------------------------------------------------------------------
# 2. Audio FileProcessor: class FileProcessor in fileprocessor.py
# -----------------------------------------------------------------------------
from fileprocessor import FileProcessor
# -----------------------------------------------------------------------------------------------
# 3. Management and UI Components : class SettingsManager, UIManager in mui.py
# -----------------------------------------------------------------------------------------------
from mui import SettingsManager , UIManager , ScreenshotManager
# -----------------------------------------------------------------------------
# 4. Visualizer Effects - class Particle in particle.py
# -----------------------------------------------------------------------------
from particle import Particle
# -----------------------------------------------------------------------------
# 6. Export functions - merge_video_audio , merge_video_audio in decoder.py
# -----------------------------------------------------------------------------
from decoder import merge_video_audio , merge_video_audio
# -----------------------------------------------------------------------------
# import dependence end start main app core below
# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
# 5. Main Visualizer Class - class HotVisualizer in main.py (this file!)
# -----------------------------------------------------------------------------
class HotVisualizer:
    def __init__(self, width=1200, height=800):
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
        # Neu: Initialisiere den Export-Manager
        self.export_manager = ExportManager(self)
        
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
        self.loading_thread = None

    def _load_file_task(self, file_path):
        """Diese Funktion wird im Hintergrund-Thread ausgeführt, um eine Datei zu analysieren."""
        self.file_processor.load_and_analyze(file_path)
        self.loading_thread = None # Signalisiert, dass das Laden beendet ist

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
            else: # File Mode
                _, _, level, peak = audio_processor.get_all_audio_data()
                sensitivity = 0.0
            self.ui.draw_audio_level_meter(level, peak, 10, 50)
            self.ui.draw_beat_info(beats, bpm, sensitivity, 10, 90)
        
        if self.settings.show_fps:
            fps_text = f"FPS: {avg_fps:.1f}"
            fps_surface = self.font.render(fps_text, True, (255, 255, 0))
            self.screen.blit(fps_surface, (self.screen_width - 120, 10))
        
        if self.loading_thread and self.loading_thread.is_alive():
            loading_surf = self.font.render("Analysiere Audio...", True, (255, 255, 0))
            loading_rect = loading_surf.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(loading_surf, loading_rect)
            
        if not self.ui.show_settings and not self.ui.show_device_menu:
            controls1 = "TAB: Settings | SPACE: Mode | C: Colors | S: Screenshot | F: Fullscreen | ESC: Exit"
            text1 = pygame.font.Font(None, 20).render(controls1, True, (200, 200, 200))
            self.screen.blit(text1, (10, self.screen_height - 45))

            if self.audio_mode == 'live':
                controls2 = "MODE: Live | A: Load File | D: Devices | Q/W: Beat Sens."
            else:
                state = self.file_processor.playback_state.capitalize() if self.file_processor.is_analyzed else "Loading..."
                controls2 = f"MODE: File ({state}) | L: To Live | P: Play/Pause | K: Stop"
            
            text2 = pygame.font.Font(None, 20).render(controls2, True, (200, 200, 200))
            self.screen.blit(text2, (10, self.screen_height - 25))
# ----------------------------------------  end class Particles stored in particles.py ----------------

    def run(self):
        running = True
        fullscreen = False
        
        print("🔥 AWESOME AUDIO VISUALIZER STARTED! 🔥")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.ui.show_settings or self.ui.show_device_menu: self.ui.show_settings = self.ui.show_device_menu = False
                        else: running = False
                    elif event.key == pygame.K_TAB: self.ui.show_settings = not self.ui.show_settings; self.ui.show_device_menu = False
                    elif event.key == pygame.K_d: self.ui.show_device_menu = not self.ui.show_device_menu; self.ui.show_settings = False
                    elif event.key == pygame.K_r: self.export_manager.start_recording()
                    elif event.key == pygame.K_e: self.export_manager.stop_recording("my_awesome_visualizer_video.mp4")
                    elif event.key == pygame.K_SPACE and not self.ui.show_settings and not self.ui.show_device_menu: self.mode = (self.mode + 1) % len(self.mode_names)
                    elif event.key == pygame.K_c and not self.ui.show_settings and not self.ui.show_device_menu: self.color_palette_index = (self.color_palette_index + 1) % len(self.palettes)
                    elif event.key == pygame.K_f:
                        fullscreen = not fullscreen
                        self.screen = pygame.display.set_mode((0,0) if fullscreen else (1200, 800), pygame.FULLSCREEN if fullscreen else 0)
                        self.screen_width, self.screen_height = self.screen.get_size()
                    elif event.key == pygame.K_s: self.screenshot_manager.capture_and_save(self.screen)
                    elif event.key in (pygame.K_q, pygame.K_w) and self.audio_mode == "live":
                        change = -0.1 if event.key == pygame.K_q else 0.1
                        self.audio_processor.beat_sensitivity = np.clip(self.audio_processor.beat_sensitivity + change, 0.5, 3.0)
                    elif event.key == pygame.K_i: self.settings.show_fps = not self.settings.show_fps
                    elif event.key == pygame.K_o: self.settings.show_audio_info = not self.settings.show_audio_info
                    elif event.key == pygame.K_l:
                         if self.audio_mode != "live":
                            if self.file_processor: self.file_processor.stop()
                            self.audio_mode = "live"
                            self.audio_processor.start_stream()
                            print("Switched to Live Mode.")
                    elif event.key == pygame.K_a:
                        if not (self.loading_thread and self.loading_thread.is_alive()):
                            if self.audio_mode == "live": self.audio_processor.stop()
                            root = tk.Tk(); root.withdraw()
                            file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
                            if file_path:
                                self.audio_mode = "file"
                                self.loading_thread = threading.Thread(target=self._load_file_task, args=(file_path,))
                                self.loading_thread.start()
                            else:
                                if self.audio_mode != "live": self.audio_mode = "live"; self.audio_processor.start_stream()
                    elif event.key == pygame.K_p and self.audio_mode == "file" and self.file_processor.is_analyzed: self.file_processor.toggle_play_pause()
                    elif event.key == pygame.K_k and self.audio_mode == "file" and self.file_processor.is_analyzed: self.file_processor.stop()
                    elif self.ui.show_device_menu:
                        if event.key == pygame.K_UP: self.ui.selected_menu_item = max(0, self.ui.selected_menu_item - 1)
                        elif event.key == pygame.K_DOWN: self.ui.selected_menu_item = min(len(self.device_manager.devices) - 1, self.ui.selected_menu_item + 1)
                        elif event.key == pygame.K_RETURN:
                            if self.ui.selected_menu_item < len(self.device_manager.devices):
                                new_idx = self.device_manager.devices[self.ui.selected_menu_item]['index']
                                self.audio_processor.change_device(new_idx); self.ui.show_device_menu = False
            
            if self.audio_mode == "live":
                fft_data, beat_detected, _, _ = self.audio_processor.get_all_audio_data()
                active_processor = self.audio_processor
            else:
                if self.file_processor and self.file_processor.is_analyzed: fft_data, beat_detected, _, _ = self.file_processor.get_all_audio_data()
                else: fft_data, beat_detected = np.zeros(1024), False
                active_processor = self.file_processor
            
            self.screen.fill((10, 10, 20))
            
            draw_modes = [self.draw_mode_0_circular_bars, self.draw_mode_1_waveform_tunnel, self.draw_mode_2_frequency_spiral, lambda d: self.draw_mode_3_beat_explosion(d, beat_detected), self.draw_mode_4_matrix_rain]
            draw_modes[self.mode](fft_data)
            self.update_particles()
            
            current_device_idx = self.audio_processor.device_index if self.audio_processor else -1
             
            self.draw_ui(active_processor)
            
            self.ui.draw_device_menu(self.device_manager.devices, current_device_idx, 50, 50)
            self.ui.draw_settings_overlay(self.settings, self.audio_processor)

            # HIER ist der richtige Platz, um den Frame für die Aufnahme zu senden
            self.export_manager.capture_frame(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
            self.time += 1
            

        self.audio_processor.stop()
        if self.file_processor: self.file_processor.stop()
        self.device_manager.close()
        pygame.quit()
        sys.exit()


# main.py

# ... (Deine vorhandenen Imports und Klassen) ...

# -----------------------------------------------------------------------------
# 6. Export Manager
# -----------------------------------------------------------------------------
#import subprocess
#import threading
#from queue import Queue
#import pyaudio
#import wave

class ExportManager:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.is_recording = False
        self.video_thread = None
        self.audio_thread = None
        self.video_process = None
        self.audio_file = None
        self.temp_video_path = "temp_video.mp4"
        self.temp_audio_path = "temp_audio.wav"
        self.start_time = None
        self.frame_count = 0

    def start_recording(self, output_filename="export.mp4"):
        if self.is_recording:
            print("Export läuft bereits.")
            return

        print("Starte Export...")
        self.is_recording = True
        self.output_filename = output_filename
        self.start_time = time.time()
        self.frame_count = 0

        # Starte den FFmpeg-Prozess für die Videoaufnahme
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.visualizer.screen_width}x{self.visualizer.screen_height}',
            '-pix_fmt', 'rgb24',
            '-r', '60', # 60 FPS für das Video
            '-i', '-',
            '-an', # Vorerst ohne Audio
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            self.temp_video_path
        ]
        self.video_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Starte Audio-Thread
        self.audio_thread = threading.Thread(target=self._record_audio_task)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def _record_audio_task(self):
        """Separate thread to record audio to a temporary WAV file."""
        try:
            p = pyaudio.PyAudio()
            audio_format = pyaudio.paInt16
            channels = 2 # Stereo
            rate = 44100
            chunk = 1024
            
            stream = p.open(format=audio_format,
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=chunk)
            
            waveFile = wave.open(self.temp_audio_path, 'wb')
            waveFile.setnchannels(channels)
            waveFile.setsampwidth(p.get_sample_size(audio_format))
            waveFile.setframerate(rate)

            while self.is_recording:
                data = stream.read(chunk, exception_on_overflow=False)
                waveFile.writeframes(data)
                
            stream.stop_stream()
            stream.close()
            waveFile.close()
            p.terminate()

        except Exception as e:
            print(f"Fehler bei Audio-Aufnahme: {e}")
            self.is_recording = False

    def capture_frame(self, screen):
        """Sendet einen Frame an FFmpeg."""
        if not self.is_recording or not self.video_process:
            return
        
        try:
            frame = pygame.surfarray.array3d(screen)
            frame = np.transpose(frame, (1, 0, 2))
            
            # önntest hier auch np.rot90(np.flipud(frame)) verwenden.
            # Transpose sollte bei 3D-Arrays schneller sein.
            
            self.video_process.stdin.write(frame.tobytes())
            self.frame_count += 1
            
        except BrokenPipeError:
            print("FFmpeg Pipe gebrochen. Beende Aufnahme.")
            self.stop_recording()
        except Exception as e:
            print(f"Fehler beim Schreiben des Frames: {e}")
            self.stop_recording()
            
    def stop_recording(self):
        if not self.is_recording:
            return

        print("Beende Video- und Audio-Aufnahme...")
        self.is_recording = False
        
        # Schließe Video-Pipe
        if self.video_process:
            self.video_process.stdin.close()
            self.video_process.wait()

        # Warte, bis der Audio-Thread fertig ist
        if self.audio_thread:
            self.audio_thread.join()

        # Starte den Merger-Prozess in einem neuen Thread, um die UI nicht zu blockieren
        merge_thread = threading.Thread(target=self._merge_files_task)
        merge_thread.start()

    def _merge_files_task(self):
        """Task to merge video and audio in a separate thread."""
        print("Starte den Merging-Prozess...")
        
        # Aufruf des externen decoder.py Skripts
        cmd = [
            sys.executable,  # Stellt sicher, dass das richtige Python-Executable verwendet wird
            'decoder.py',
            self.temp_video_path,
            self.temp_audio_path,
            self.output_filename
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print("Merging-Prozess abgeschlossen. Temporäre Dateien werden gelöscht.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Mergen: {e}")
        
        # Aufräumen
        if os.path.exists(self.temp_video_path):
            os.remove(self.temp_video_path)
        if os.path.exists(self.temp_audio_path):
            os.remove(self.temp_audio_path)


if __name__ == "__main__":
    visualizer = HotVisualizer()
    visualizer.run()
