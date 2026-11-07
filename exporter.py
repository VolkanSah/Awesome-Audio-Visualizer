# -----------------------------------------------------------------------------
# Export: records the visualizer to ONE mp4 (video + original audio + chapters)
# File: exporter.py
#
# How it works:
#   1. Frames are piped to ffmpeg while the music plays (video only, temp file).
#   2. The video timeline is driven by the AUDIO position, not by the wall clock.
#      -> frames are duplicated if the app renders slower than 60 FPS, so video
#         and audio always stay in sync (also when you pause).
#   3. When recording stops, the ORIGINAL audio files of all played tracks are
#      concatenated, chapters (one per song) are written, and everything is
#      muxed into a single mp4. Temp files are deleted afterwards.
# -----------------------------------------------------------------------------
import os
import queue
import shutil
import subprocess
import threading
from datetime import datetime


def find_ffmpeg():
    """FFmpeg from system_report.json (detector.py) -> PATH -> plain 'ffmpeg'."""
    try:
        from decoder import get_ffmpeg_path
        return get_ffmpeg_path()
    except Exception:
        pass
    return shutil.which("ffmpeg") or "ffmpeg"


def _meta_escape(text):
    text = str(text).replace("\r", " ").replace("\n", " ")
    for ch in ("\\", "=", ";", "#"):
        text = text.replace(ch, "\\" + ch)
    return text


class ExportManager:
    def __init__(self, out_dir="exports", fps=60, ffmpeg_path=None):
        self.out_dir = out_dir
        self.fps = fps
        self._ffmpeg_override = ffmpeg_path

        self.is_recording = False
        self.is_finalizing = False
        self.status = ""          # last message, shown in the UI
        self.last_output = None
        self.size = (0, 0)
        self.frames = 0

        self._lock = threading.Lock()
        self._proc = None
        self._log = None
        self._queue = None
        self._writer = None
        self._failed = False
        self._finalizer = None

        self._tracks = []         # audio file paths in play order
        self._chapters = []       # {'start': sec, 'title': str}
        self._cur = None          # {'duration': sec}
        self._offset = 0.0

    # ------------------------------------------------------------------ start
    def start(self, width, height):
        if self.is_recording or self.is_finalizing:
            self.status = "Export läuft bereits."
            return False

        self.ffmpeg = self._ffmpeg_override or find_ffmpeg()
        os.makedirs(self.out_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_video = os.path.join(self.out_dir, f"tmp_video_{stamp}.mp4")
        self.meta_path = os.path.join(self.out_dir, f"tmp_meta_{stamp}.txt")
        self.final_path = os.path.join(self.out_dir, f"visualizer_{stamp}.mp4")
        self.log_path = os.path.join(self.out_dir, f"ffmpeg_{stamp}.log")

        cmd = [
            self.ffmpeg, "-y", "-loglevel", "warning",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", str(self.fps),
            "-i", "-", "-an",
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",   # yuv420p needs even size
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            self.temp_video,
        ]
        try:
            # stderr goes to a log FILE. A PIPE that nobody reads would fill up
            # and freeze ffmpeg (and with it the whole app).
            self._log = open(self.log_path, "w", encoding="utf-8", errors="replace")
            self._proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                stderr=self._log, **self._popen_flags())
        except Exception as e:
            self.status = f"FFmpeg konnte nicht gestartet werden: {e}"
            if self._log:
                self._log.close()
                self._log = None
            return False

        self.size = (width, height)
        self.frames = 0
        self._failed = False
        self._tracks, self._chapters = [], []
        self._cur, self._offset = None, 0.0
        self._last_frame = None
        self._queue = queue.Queue(maxsize=180)
        self._writer = threading.Thread(target=self._writer_task, daemon=True)
        self._writer.start()
        self.is_recording = True
        self.status = "Export gestartet"
        return True

    @staticmethod
    def _popen_flags():
        if os.name == "nt":
            return {"creationflags": subprocess.CREATE_NO_WINDOW}
        return {}

    # ----------------------------------------------------------------- tracks
    def begin_track(self, path, duration, title):
        """Call whenever a track starts playing from 0:00 while recording."""
        with self._lock:
            if not self.is_recording:
                return
            if self._cur is not None:
                self._offset += self._cur["duration"]
            self._cur = {"duration": max(float(duration), 0.1)}
            self._tracks.append(path)
            self._chapters.append({"start": self._offset, "title": title or os.path.basename(path)})

    # ----------------------------------------------------------------- frames
    def frames_due(self, track_pos):
        """How many video frames must be written so the video catches up with
        the audio position. 0 -> no need to even grab a frame."""
        if not self.is_recording or self._cur is None or track_pos is None or self._failed:
            return 0
        t = self._offset + min(max(track_pos, 0.0), self._cur["duration"])
        return max(0, int(t * self.fps) - self.frames)

    def write(self, rgb_bytes, count):
        """rgb_bytes: raw RGB frame (w*h*3). It is written `count` times."""
        if count <= 0 or not self.is_recording:
            return
        self.frames += count
        self._last_frame = rgb_bytes
        self._queue.put((rgb_bytes, count))

    def _writer_task(self):
        stdin = self._proc.stdin
        while True:
            item = self._queue.get()
            if item is None:
                break
            if self._failed:
                continue                      # keep draining, never block the app
            data, count = item
            try:
                for _ in range(count):
                    stdin.write(data)
            except (BrokenPipeError, OSError):
                self._failed = True
        try:
            stdin.close()
        except Exception:
            pass

    # ------------------------------------------------------------------- stop
    def stop(self, natural_end=False):
        """natural_end=True: the last song ran out -> top the video up to the
        exact end of the audio (otherwise it stops at the current position)."""
        if not self.is_recording:
            return
        if natural_end and self._cur is not None and getattr(self, "_last_frame", None):
            missing = int((self._offset + self._cur["duration"]) * self.fps) - self.frames
            if missing > 0:
                self.write(self._last_frame, missing)
        self.is_recording = False
        self.is_finalizing = True
        self.status = "Export wird fertiggestellt ..."
        self._finalizer = threading.Thread(target=self._finalize_task)
        self._finalizer.start()

    def wait(self):
        """Block until the export is completely written (call on app exit)."""
        if self._finalizer and self._finalizer.is_alive():
            self._finalizer.join()

    def _finalize_task(self):
        try:
            self._queue.put(None)
            self._writer.join()
            self._proc.wait()
            self._log.close()
            self._log = None

            if self._failed or self._proc.returncode != 0:
                self.status = f"Export fehlgeschlagen (siehe {self.log_path})"
                return
            if self.frames == 0 or not self._tracks:
                self.status = "Export abgebrochen: nichts aufgenommen"
                self._cleanup(keep_log=False)
                return

            self._write_meta()
            ok, err = self._mux()
            if ok:
                self.last_output = self.final_path
                self.status = f"Export fertig: {self.final_path}"
                self._cleanup(keep_log=False)
            else:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write("\n--- mux ---\n" + err)
                self.status = f"Merge fehlgeschlagen (Video bleibt: {self.temp_video})"
        except Exception as e:
            self.status = f"Export-Fehler: {e}"
        finally:
            self.is_finalizing = False

    def _write_meta(self):
        # real end of the video (differs from the song end if you stopped early)
        total_end = max(self.frames / self.fps, self._chapters[-1]["start"] + 0.001)
        lines = [";FFMETADATA1", "title=Awesome Audio Visualizer Export"]
        for i, ch in enumerate(self._chapters):
            start = int(ch["start"] * 1000)
            end = int((self._chapters[i + 1]["start"] if i + 1 < len(self._chapters) else total_end) * 1000)
            end = max(end, start + 1)
            lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}",
                      f"title={_meta_escape(ch['title'])}"]
        with open(self.meta_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _mux(self):
        n = len(self._tracks)
        cmd = [self.ffmpeg, "-y", "-loglevel", "warning", "-i", self.temp_video]
        for t in self._tracks:
            cmd += ["-i", t]
        cmd += ["-i", self.meta_path]
        meta_idx = 1 + n

        if n == 1:
            cmd += ["-map", "0:v:0", "-map", "1:a:0"]
        else:
            # normalise every track first, concat needs identical formats
            parts = "".join(
                f"[{i + 1}:a:0]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}];"
                for i in range(n))
            joined = "".join(f"[a{i}]" for i in range(n))
            cmd += ["-filter_complex", f"{parts}{joined}concat=n={n}:v=0:a=1[aout]",
                    "-map", "0:v:0", "-map", "[aout]"]

        cmd += ["-map_metadata", str(meta_idx), "-map_chapters", str(meta_idx),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", self.final_path]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", **self._popen_flags())
        return r.returncode == 0, (r.stderr or "")

    def _cleanup(self, keep_log=False):
        paths = [self.temp_video, self.meta_path]
        if not keep_log:
            paths.append(self.log_path)
        for p in paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                pass
