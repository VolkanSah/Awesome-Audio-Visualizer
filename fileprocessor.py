# -----------------------------------------------------------------------------
#  Awesome-Audio-Visualizer 1.1.0 by Volkan Sah
#  Copyright (c) 2024-2025 Volkan Sah
#  License:      AGPL-3.0-or-later (siehe LICENSE)
#  https://github.com/VolkanSah/Awesome-Audio-Visualizer
# -----------------------------------------------------------------------------
# 2. Audio FileProcessor: class FileProcessor  (playlist capable)
# File: fileprocessor.py
# -----------------------------------------------------------------------------
import os
import threading

import numpy as np
import pygame
import librosa

AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.flac')


def collect_audio_files(paths):
    """Expands files and folders into a sorted list of playable audio files."""
    result = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for name in sorted(files):
                    if name.lower().endswith(AUDIO_EXTS):
                        result.append(os.path.join(root, name))
        elif os.path.isfile(p) and p.lower().endswith(AUDIO_EXTS):
            result.append(p)
    return result


def read_tags(path):
    """Returns (title, artist). Uses mutagen if installed, else the file name
    ('Artist - Title.mp3' is understood)."""
    title = artist = ""
    try:
        import mutagen
        tags = mutagen.File(path, easy=True)
        if tags:
            title = (tags.get('title') or [''])[0]
            artist = (tags.get('artist') or [''])[0]
    except Exception:
        pass
    if not title:
        stem = os.path.splitext(os.path.basename(path))[0]
        if ' - ' in stem:
            a, t = stem.split(' - ', 1)
            artist = artist or a.strip()
            title = t.strip()
        else:
            title = stem
    return title.strip(), artist.strip()


class FileProcessor:
    def __init__(self):
        pygame.mixer.init()
        # playlist
        self.playlist = []
        self.index = -1
        # current track
        self.file_path = None
        self.title = ""
        self.artist = ""
        self.log_spectrogram = None
        self.beat_times = []
        self.duration = 0
        self.sr = 44100
        # state
        self.is_analyzed = False
        self.loading = False
        self.load_failed = False
        self.error_msg = ""
        self.playback_state = 'stopped'  # 'stopped', 'playing', 'paused'
        self.ended_all = False           # True when the last track ran out
        self.track_serial = 0            # +1 every time a track starts at 0:00
        self.beats_detected = 0
        self.beat_index = 0
        # background pre-analysis of the next track (no gap between songs)
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._prefetch_path = None
        self._prefetch_thread = None

    # ------------------------------------------------------------ analysis
    def _analyze(self, path):
        audio_data, sr = librosa.load(path, sr=self.sr, mono=True)
        duration = librosa.get_duration(y=audio_data, sr=sr)
        _, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        spectrogram = np.abs(librosa.stft(audio_data, n_fft=2 * 1024, hop_length=1024))
        log_spec = librosa.amplitude_to_db(spectrogram, ref=np.max)
        title, artist = read_tags(path)
        return {'path': path, 'sr': sr, 'duration': duration, 'beat_times': beat_times,
                'log_spectrogram': log_spec, 'title': title, 'artist': artist}

    def _activate(self, data, autoplay):
        self.file_path = data['path']
        self.sr = data['sr']
        self.duration = data['duration']
        self.beat_times = data['beat_times']
        self.log_spectrogram = data['log_spectrogram']
        self.title = data['title']
        self.artist = data['artist']
        pygame.mixer.music.load(data['path'])
        self.playback_state = 'stopped'
        self.is_analyzed = True
        self.loading = False
        if autoplay:
            self._play_from_start()
        self._start_prefetch()

    def _play_from_start(self):
        self.beat_index = 0
        self.beats_detected = 0
        self.ended_all = False
        pygame.mixer.music.play()
        self.playback_state = 'playing'
        self.track_serial += 1

    def _start_prefetch(self):
        nxt = self.index + 1
        if nxt >= len(self.playlist):
            return
        path = self.playlist[nxt]
        with self._cache_lock:
            if path in self._cache or self._prefetch_path == path:
                return
        self._prefetch_path = path

        def task():
            try:
                data = self._analyze(path)
                with self._cache_lock:
                    self._cache = {path: data}  # keep only one track in memory
            except Exception as e:
                print(f"Prefetch fehlgeschlagen ({os.path.basename(path)}): {e}")
            finally:
                self._prefetch_path = None

        self._prefetch_thread = threading.Thread(target=task, daemon=True)
        self._prefetch_thread.start()

    # ------------------------------------------------------------ playlist
    def set_playlist(self, paths, autoplay=True):
        """Replaces the playlist and starts the first track."""
        if self.loading:
            return False
        pygame.mixer.music.stop()
        self.playback_state = 'stopped'
        self.playlist = list(paths)
        with self._cache_lock:
            self._cache = {}
        return self.play_index(0, autoplay)

    def add_to_playlist(self, paths):
        old_len = len(self.playlist)
        self.playlist.extend(paths)
        if not self.playlist:
            return
        if old_len == 0:
            self.play_index(0, True)
        elif self.ended_all and not self.loading:   # list was finished -> continue
            self.play_index(old_len, True)
        elif not self.loading and self.index == old_len - 1:
            self._start_prefetch()

    def play_index(self, i, autoplay=True):
        if self.loading or not (0 <= i < len(self.playlist)):
            return False
        path = self.playlist[i]
        pygame.mixer.music.stop()
        self.playback_state = 'stopped'
        self.index = i
        self.is_analyzed = False
        self.load_failed = False
        self.loading = True

        def task():
            try:
                t = self._prefetch_thread
                if t is not None and self._prefetch_path == path and t.is_alive():
                    t.join()                       # same track is being analysed already
                with self._cache_lock:
                    data = self._cache.pop(path, None)
                if data is None:
                    print(f"Lade und analysiere '{os.path.basename(path)}' ...")
                    data = self._analyze(path)
                self._activate(data, autoplay)
            except Exception as e:
                self.error_msg = f"Fehler bei '{os.path.basename(path)}': {e}"
                print(self.error_msg)
                self.is_analyzed = False
                self.loading = False
                self.load_failed = True

        threading.Thread(target=task, daemon=True).start()
        return True

    def next_track(self):
        if self.index + 1 < len(self.playlist):
            return self.play_index(self.index + 1, True)
        return False

    def prev_track(self):
        pos = self.get_position()
        if self.index <= 0 or (pos is not None and pos > 3.0):
            self.restart_track()
        else:
            self.play_index(self.index - 1, True)

    def restart_track(self):
        """Plays the current track from 0:00 (used by export)."""
        if not self.is_analyzed or self.loading:
            return
        pygame.mixer.music.stop()
        self._play_from_start()

    def update(self):
        """Call once per frame: handles track end -> next track."""
        if self.load_failed:
            self.load_failed = False
            if self.index + 1 < len(self.playlist):
                self.play_index(self.index + 1, True)
            else:
                self.playback_state = 'stopped'
                self.ended_all = True
            return
        if (self.playback_state == 'playing' and not self.loading
                and not pygame.mixer.music.get_busy()):
            self.playback_state = 'stopped'
            if self.index + 1 < len(self.playlist):
                self.play_index(self.index + 1, True)
            else:
                self.ended_all = True

    def pop_error(self):
        msg, self.error_msg = self.error_msg, ""
        return msg

    def playlist_info(self):
        return self.index + 1, len(self.playlist)

    # ------------------------------------------------------------ playback
    def toggle_play_pause(self):
        if not self.is_analyzed:
            return
        if self.playback_state == 'playing':
            pygame.mixer.music.pause()
            self.playback_state = 'paused'
        elif self.playback_state == 'paused':
            pygame.mixer.music.unpause()
            self.playback_state = 'playing'
        elif self.playback_state == 'stopped':
            self._play_from_start()

    def stop(self):
        """Stops playback (P starts the current track again from the start)."""
        if not self.is_analyzed:
            return
        pygame.mixer.music.stop()
        self.playback_state = 'stopped'

    def get_position(self):
        """Seconds since the track started (pause not counted) or None."""
        if self.playback_state in ('playing', 'paused') and self.is_analyzed:
            ms = pygame.mixer.music.get_pos()
            if ms >= 0:
                return min(ms / 1000.0, self.duration)
        return None

    def get_all_audio_data(self):
        if not self.is_analyzed or self.log_spectrogram is None:
            return np.zeros(1024), False, 0, 0
        if self.playback_state != 'playing' or self.duration == 0:
            return np.zeros(self.log_spectrogram.shape[0]), False, 0, 0

        current_time = max(pygame.mixer.music.get_pos(), 0) / 1000.0
        frame_index = int(current_time * self.log_spectrogram.shape[1] / self.duration)
        frame_index = min(max(0, frame_index), self.log_spectrogram.shape[1] - 1)

        fft_data = self.log_spectrogram[:, frame_index]
        fft_data = np.interp(fft_data, (fft_data.min(), fft_data.max()), (0, 100))

        is_beat = False
        if self.beat_index < len(self.beat_times) and current_time >= self.beat_times[self.beat_index]:
            is_beat = True
            self.beat_index += 1
            self.beats_detected += 1

        return fft_data, is_beat, np.mean(fft_data), np.max(fft_data)

    def get_beat_stats(self):
        pos = self.get_position()
        if pos and pos > 0 and self.beats_detected > 0:
            bpm = self.beats_detected / (pos / 60)
        else:
            bpm = 0
        return self.beats_detected, int(bpm)
