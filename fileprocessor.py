import pygame
import numpy as np
import librosa
import threading
import os

# -----------------------------------------------------------------------------
# 2. Audio FileProcessor: class FileProcessor in fileprocessor.py
# -----------------------------------------------------------------------------
class FileProcessor:
    def __init__(self):
        pygame.mixer.init()
        self.file_path = None
        self.log_spectrogram = None
        self.beat_times = []
        self.duration = 0
        self.sr = 44100
        
        self.is_analyzed = False
        self.playback_state = 'stopped'  # Mögliche Zustände: 'stopped', 'playing', 'paused'
        self.beats_detected = 0
        self.beat_index = 0

    def load_and_analyze(self, file_path):
        """
        Lädt und analysiert die Audiodatei.
        Diese Methode ist langsam und sollte in einem separaten Thread ausgeführt werden.
        """
        try:
            print(f"Lade und analysiere '{os.path.basename(file_path)}'...")
            self.file_path = file_path
            
            # --- Librosa Analyse ---
            audio_data, self.sr = librosa.load(file_path, sr=self.sr, mono=True)
            self.duration = librosa.get_duration(y=audio_data, sr=self.sr)
            
            _, beat_frames = librosa.beat.beat_track(y=audio_data, sr=self.sr)
            self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
            
            spectrogram = np.abs(librosa.stft(audio_data, n_fft=2*1024, hop_length=1024))
            self.log_spectrogram = librosa.amplitude_to_db(spectrogram, ref=np.max)

            # --- Pygame Mixer vorbereiten ---
            pygame.mixer.music.load(file_path)

            self.is_analyzed = True
            self.playback_state = 'stopped'
            print("Analyse abgeschlossen. Bereit zum Abspielen.")
        except Exception as e:
            print(f"Fehler bei der Analyse der Datei: {e}")
            self.is_analyzed = False

    def toggle_play_pause(self):
        """Wechselt zwischen Play und Pause oder startet die Wiedergabe."""
        if not self.is_analyzed:
            return

        if self.playback_state == 'playing':
            pygame.mixer.music.pause()
            self.playback_state = 'paused'
            print("Wiedergabe pausiert.")
        elif self.playback_state == 'paused':
            pygame.mixer.music.unpause()
            self.playback_state = 'playing'
            print("Wiedergabe fortgesetzt.")
        elif self.playback_state == 'stopped':
            self.beat_index = 0
            self.beats_detected = 0
            pygame.mixer.music.play()
            self.playback_state = 'playing'
            print("Wiedergabe gestartet.")

    def stop(self):
        """Stoppt die Wiedergabe und setzt sie zurück."""
        if not self.is_analyzed:
            return
        pygame.mixer.music.stop()
        self.playback_state = 'stopped'
        print("Wiedergabe gestoppt.")

    def get_all_audio_data(self):
        if self.playback_state != 'playing' or not pygame.mixer.music.get_busy():
            if self.playback_state == 'playing': # Musik ist von selbst zu Ende
                self.playback_state = 'stopped'
            # Leere Daten zurückgeben, wenn nichts abgespielt wird
            default_shape = self.log_spectrogram.shape[0] if self.is_analyzed else 1024
            return np.zeros(default_shape), False, 0, 0
        
        current_time = pygame.mixer.music.get_pos() / 1000.0
        
        if self.duration == 0: return np.zeros(self.log_spectrogram.shape[0]), False, 0, 0
            
        frame_index = int(current_time * self.log_spectrogram.shape[1] / self.duration)
        frame_index = min(max(0, frame_index), self.log_spectrogram.shape[1] - 1)
        
        fft_data = self.log_spectrogram[:, frame_index]
        fft_data = np.interp(fft_data, (fft_data.min(), fft_data.max()), (0, 100))
        
        is_beat = False
        if self.beat_index < len(self.beat_times) and current_time >= self.beat_times[self.beat_index]:
            is_beat = True
            self.beat_index += 1
            self.beats_detected += 1
            
        level = np.mean(fft_data)
        peak = np.max(fft_data)
        
        return fft_data, is_beat, level, peak

    def get_beat_stats(self):
        current_time = pygame.mixer.music.get_pos() / 1000.0
        if current_time > 0 and self.beats_detected > 0:
            bpm = self.beats_detected / (current_time / 60)
        else:
            bpm = 0
        return self.beats_detected, int(bpm)
