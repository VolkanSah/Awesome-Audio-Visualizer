# -----------------------------------------------------------------------------
# 1. Audio Component:  class AudioDeviceManager, AudioProcessor 
# File: audio.py
# -----------------------------------------------------------------------------

import pyaudio
import numpy as np
import threading

# In audio.py
from collections import deque

# ... rest of code ...?

class AudioDeviceManager:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.devices = self.get_audio_devices()

    def get_audio_devices(self):
        """Fetches all available audio input devices."""
        devices = []
        for i in range(self.p.get_device_count()):
            try:
                device_info = self.p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
            except:
                continue
        return devices

    def get_default_device(self):
        """Returns the default audio input device index."""
        try:
            default_info = self.p.get_default_input_device_info()
            return default_info['index']
        except:
            return 0 if self.devices else None

    def close(self):
        self.p.terminate()

class AudioProcessor:
    def __init__(self, device_index=None, chunk_size=2048, format=pyaudio.paInt16, channels=1, rate=44100):
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.device_index = device_index
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_active = False
        
        # Audio analysis state
        self.fft_history = deque(maxlen=10)
        self.bass_history = deque(maxlen=5)
        self.beat_sensitivity = 1.5
        
        # UI stats
        self.current_level = 0
        self.peak_level = 0
        self.beats_detected = 0
        self.last_beat_time = 0
        
        self.start_stream()

    def start_stream(self):
        """Starts or restarts the audio stream."""
        try:
            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
            
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            self.is_active = True
            print(f"Audio stream started for device index: {self.device_index}")
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_active = False
            
    def change_device(self, device_index):
        """Changes the audio input device."""
        self.device_index = device_index
        self.start_stream()

    def get_all_audio_data(self):
        if not self.is_active or not self.stream:
            return np.zeros(self.chunk_size // 2), False, 0, 0
        
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            windowed_data = audio_data * np.hanning(len(audio_data))
            fft_raw = np.abs(np.fft.fft(windowed_data))[:self.chunk_size // 2]
            fft_data = np.log10(fft_raw + 1) * 10
            
            self.fft_history.append(fft_data)
            smoothed_fft = np.mean(self.fft_history, axis=0) if self.fft_history else fft_data
            
            bass_end_index = int(250 * self.chunk_size / self.rate)
            bass_energy = np.sum(fft_raw[:bass_end_index])
            self.bass_history.append(bass_energy)
            
            is_beat = False
            if len(self.bass_history) > 2:
                avg_bass = np.mean(list(self.bass_history)[:-1])
                is_beat = bass_energy > avg_bass * self.beat_sensitivity
            
            current_time = time.time()
            if is_beat and (current_time - self.last_beat_time) > 0.1:
                self.beats_detected += 1
                self.last_beat_time = current_time
            
            rms = np.sqrt(np.mean(audio_data**2))
            self.current_level = min(100, rms / 327.67)
            
            if self.current_level > self.peak_level:
                self.peak_level = self.current_level
            else:
                self.peak_level *= 0.98
                
            return smoothed_fft, is_beat, self.current_level, self.peak_level
            
        except IOError:
            return np.zeros(self.chunk_size // 2), False, 0, 0

    def get_beat_stats(self):
        return self.beats_detected, 0 # BPM calculation can be improved

    def stop(self):
        """Closes the audio stream."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.is_active = False
