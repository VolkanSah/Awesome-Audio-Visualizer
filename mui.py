# -----------------------------------------------------------------------------------------------
# 3. Management and UI Components : class SettingsManager, UIManage, ScreenshotManager 
# File: mui.py
# -----------------------------------------------------------------------------------------------
import pygame
import os
from datetime import datetime
import tkinter


class SettingsManager:
    def __init__(self):
        self.show_fps = True
        self.show_audio_info = True
        self.screenshot_path = "screenshots"
        self.ensure_screenshot_dir()

    def ensure_screenshot_dir(self):
        if not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)

class UIManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 20)
        self.show_settings = False
        self.show_device_menu = False
        self.selected_menu_item = 0

    def draw_audio_level_meter(self, level, peak, x, y, width=200, height=20):
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))
        level_width = int(width * level / 100)
        color = (0, 255, 0) if level < 70 else (255, 255, 0) if level < 90 else (255, 0, 0)
        if level_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, level_width, height))
        peak_x = int(x + width * peak / 100)
        pygame.draw.line(self.screen, (255, 255, 255), (peak_x, y), (peak_x, y + height), 2)
        level_text = f"Level: {level:.1f}% Peak: {peak:.1f}%"
        text = self.small_font.render(level_text, True, (255, 255, 255))
        self.screen.blit(text, (x, y + height + 5))

    def draw_beat_info(self, beats, bpm, sensitivity, x, y):
        beat_text = f"Beats: {beats} | BPM: {bpm} | Sensitivity: {sensitivity:.1f}"
        text = self.small_font.render(beat_text, True, (255, 255, 255))
        self.screen.blit(text, (x, y))

    def draw_device_menu(self, devices, current_device_index, x, y):
        if not self.show_device_menu:
            return
        menu_height = min(300, len(devices) * 25 + 40)
        menu_rect = pygame.Rect(x, y, 400, menu_height)
        pygame.draw.rect(self.screen, (30, 30, 30), menu_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), menu_rect, 2)
        title = self.font.render("Audio Device Selection", True, (255, 255, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        for i, device in enumerate(devices[:10]):
            device_y = y + 40 + i * 25
            is_current = device['index'] == current_device_index
            is_selected = i == self.selected_menu_item
            if is_selected:
                pygame.draw.rect(self.screen, (60, 60, 60), (x + 5, device_y - 2, 390, 22))
            color = (0, 255, 0) if is_current else (255, 255, 255)
            device_text = f"{device['name'][:40]}{'...' if len(device['name']) > 40 else ''}"
            text = self.small_font.render(device_text, True, color)
            self.screen.blit(text, (x + 10, device_y))
            info_text = f"({device['channels']}ch, {device['sample_rate']}Hz)"
            info = self.small_font.render(info_text, True, (150, 150, 150))
            self.screen.blit(info, (x + 300, device_y))

    def draw_settings_overlay(self, settings, audio_processor):
        if not self.show_settings:
            return
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        panel_width, panel_height = 500, 400
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        pygame.draw.rect(self.screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 3)
        title = self.font.render("🔥 SETTINGS 🔥", True, (255, 255, 0))
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        y_offset = 80
        settings_text = [

            f"Beat Sensitivity: {audio_processor.beat_sensitivity:.1f} (Q/W to adjust)",
            f"Show FPS: {'ON' if settings.show_fps else 'OFF'} (Toggle: I)",
            f"Show Audio Info: {'ON' if settings.show_audio_info else 'OFF'} (Toggle: O)",
            "",
            "Controls:",
            "ESC - Close Settings / Exit",
            "D - Audio Device Menu",
            "S - Take Screenshot",
            "P - Play/Pause File",
            "K - Stop File",
            "",
            "",
            "AWESOME AUDIO VISUALIZER 1.0.0",
            "Copyright VolkanSah",
        ]
        
        for text in settings_text:
            color = (255, 255, 255) if not text.startswith("Controls:") else (255, 255, 0)
            rendered = self.small_font.render(text, True, color)
            self.screen.blit(rendered, (panel_x + 20, panel_y + y_offset))
            y_offset += 25


class ScreenshotManager:
    """Manages the capturing and saving of screenshots."""
    
    def __init__(self, save_path="screenshots"):
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def capture_and_save(self, screen):
        """Captures a screenshot from the given screen surface and saves it."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.save_path, filename)
        
        try:
            pygame.image.save(screen, filepath)
            print(f"Screenshot saved to: {filepath}")
        except pygame.error as e:
            print(f"Error saving screenshot: {e}")

