# 🎧 Awesome-Audio-Visualizer
#### v. 1.0.0 
###### AI compatible - teste, works!
> German verison, sorry.. soon multi lingua.. i craft always in german first.
> 
 Welcome to Awesome-Audio-Visualizer, an open-source tool that transforms audio into stunning visual effects.
Born from passion, this project delivers a customizable and scalable visualizer that works for personal music, videos, and live streams.

---



<details><summary>💡 Why this project?</summary>

Most existing visualizers are either closed-source or offer limited customization. My goal was to build a tool that is easy to use yet powerful enough to unleash your creativity.
With this project, you can give your music a visual soul. Future updates will include features like video export and more unique effects – a **K-Pop artifact** is promised! 😉

---

## 🎨 Creative Freedom & Simple City Design

Most visualization projects force artists to fight proprietary codebases. Our **Simple City** design is the antidote. We built Awesome-Audio-Visualizer to be the most accessible, high-performance canvas for your creativity.

### Unleash Your Creativity with Draw-Mode Elements

The project's **modular architecture** makes it incredibly easy for anyone—from seasoned developers to artists leveraging **AI assistance**—to create stunning new visualization effects or patterns.

The complexity of system integration is handled by the **`detector.py`** and core modules, leaving you free to focus solely on the aesthetics.

### How to Create Your Own Visualizer Mode:

The logic is simple and contained:

1.  **Isolated Functionality:** Every effect is isolated in its own method, following the simple naming convention: `draw_mode_X(self, fft_data)`.
2.  **Focus on the Core:** You only need to focus on how the core **audio data input** (`fft_data`—a NumPy array of frequency amplitudes) translates into **visual output** (Pygame drawing commands on `self.screen`).
3.  **AI Integration:** Your favorite AI can instantly generate new visual patterns because the required input/output specifications are clear and minimal. The AI doesn't need to touch the complicated audio, UI, or export logic.

This design ensures that the path to **unleashing creativity is short and direct**, making this project the superior choice for visual artists who value **performance over complexity**.



</details>

---

## ✨ Features

### Visual Effects

The visualizer includes **five unique visual modes** that dynamically react to audio input:

* **Circular Bars** – Displays audio frequencies as radial bars expanding from a central point.
* **Waveform Tunnel** – Creates a 3D tunnel that morphs with the audio waveform.
* **Frequency Spiral** – Visualizes frequency data as a glowing, rotating spiral.
* **Beat Explosion** – Triggers particle explosions on every detected beat, with pulsing bars.
* **Matrix Rain** – Inspired by *The Matrix*, falling symbols change intensity and color with the sound.

Built so you can easily create your own modes without much knowledge. Show your favorite AI the structure and let it modify them.
For the pros – have fun! I’m open to cool ideas, as long as this project stays **open source** and doesn’t turn into bloated garbage.

### Color Palettes

Each visualization mode supports five customizable color palettes:

* `fire` 🔥
* `electric` ⚡
* `ocean` 🌊
* `rainbow` 🌈
* `neon` ✨

### Audio Control

Two input modes supported:

* **Live Mode** – Processes real-time audio input from a connected microphone or standard device.
* **File Mode** – Plays and analyzes local audio files (MP3, WAV, OGG, FLAC) as a **playlist**.
  Select several files at once (`A`), add more later (`Shift+A`), drop files/folders into the window,
  or start with `python main.py song1.mp3 song2.mp3 myfolder/`.
  The next song is analyzed in the background while the current one plays, so there is no gap.

### 🎬 Chapters & Clean View

* **Chapter look** (`M`) – every song is a chapter: when the next song starts, the visual mode and color palette switch automatically.
* **Clean view** (`H`) – hides all data (FPS, meters, beats, help text). Only the visualization and the **song title + artist** remain.
  Title/artist are read from the file tags (install `mutagen`), otherwise from the file name (`Artist - Title.mp3`).

### 🎥 Export (one MP4: video + original audio + chapters)

* `R` starts the export **from the beginning of the current song** and records the playlist until the end. `E` (or `R` again) stops it early.
* The exported video always shows only the visualization + title/artist (no UI), the REC indicator is for your eyes only.
* Audio is the **original file(s)**, not a microphone recording. Video and audio stay in sync even if your PC renders below 60 FPS or you pause.
* Every song becomes an MP4 **chapter** (visible in VLC, mpv, ...).
* Result: `exports/visualizer_<timestamp>.mp4` (an `ffmpeg_*.log` is kept only if something fails).
* While exporting, skip/load/fullscreen are disabled to keep the file consistent.

---

## ⌨️ Controls

| Key | Action | Description |
| :--- | :--- | :--- |
| `SPACE` | **Switch Mode** | Cycles through the 5 visualization modes. |
| `C` | **Change Color Palette** | Switches to the next available color palette. |
| `A` | **Load Audio Files** | Choose one or more files (replaces the playlist). `Shift+A` adds to the playlist. |
| `L` | **Back to Live Mode** | Switches from file mode to live audio input. |
| `P` | **Play / Pause** | Starts or pauses playback. *(File mode only)* |
| `K` | **Stop** | Stops playback (also stops a running export). *(File mode only)* |
| `N` / `B` | **Next / Previous song** | `B` restarts the song if it already played >3 s. *(File mode only)* |
| `M` | **Chapter look** | Toggle: new look for every song. |
| `H` | **Clean view** | Only visualization + song title/artist. |
| `F` | **Fullscreen** | Toggles fullscreen mode. |
| `S` | **Screenshot** | Saves a screenshot of the current visualizer. |
| `TAB` | **Settings** | Opens an advanced settings menu. |
| `D` | **Device Menu** | Select an audio input device. *(Live mode only)* |
| `Q` / `W` | **Beat Sensitivity** | Adjusts beat detection sensitivity. *(Live mode only)* |
| `R` | **Export** | Start/stop MP4 export. *(File mode only)* |
| `E` | **Stop export** | Stops a running export. |
| `ESC` | **Exit** | Closes the program or the active settings/device menu. |

---

## 📂 Project Structure

The project is modular for better organization and maintainability:

* `main.py` – Core logic and **`HotVisualizer`** class handling rendering and user interaction.
* `audio.py` – Audio processing and live audio stream handling via **`AudioDeviceManager`** and **`AudioProcessor`**.
* `fileprocessor.py` – Playlist, analysis, title/artist tags and playback with the **`FileProcessor`** class.
* `mui.py` – UI-related logic: settings, menus, screenshot functionality via **`SettingsManager`**, **`UIManager`**, **`ScreenshotManager`**.
* `particle.py` – Defines the **`Particle`** class for the Beat Explosion mode.
* `detector.py` – Generates **`system_report.json`** with required FFmpeg/Audio paths -needed- based on OS (must run first for export to work).
* `exporter.py` – **`ExportManager`**: records frames, concatenates the original audio of all played songs, writes chapters and muxes everything into one MP4 via FFmpeg.
* `decoder.py` – FFmpeg helpers (`merge_video_audio`, device list). Also usable standalone: `python decoder.py merge video.mp4 audio.mp3`.

---

## ⚙️ Requirements

Install the required dependencies via `pip`:

```bash
pip install -r requirements.txt
# or: pip install pygame numpy pyaudio librosa mutagen
````

### Detailed Dependencies:

  * `pygame` – Graphics and window management.
  * `numpy` – Fast Fourier Transform (FFT) and array operations.
  * `pyaudio` – Live audio input handling.
  * `librosa` – Advanced audio analysis functions.
  * `mutagen` – *(optional)* reads title/artist tags from MP3/FLAC/OGG.
  * **FFmpeg** – needed for export. Run `detector.py` once, or just have `ffmpeg` in your PATH.

#### **Note about `pyaudio`:**

Installation may fail on some systems. Alternative steps:

**Windows:**

```bash
pip install pipwin
pipwin install pyaudio
```

**Linux/Ubuntu:**

```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**macOS:**

```bash
brew install portaudio
pip install pyaudio
```

If issues persist, use:

```bash
pip install sounddevice
```

-----

### Why Pygame? Performance That Actually Works!
This project showcases the **true power of Pygame** for modern desktop applications:
- **60+ FPS** smooth visuals (while most audio visualizers crawl at 24-30 FPS)
- **Native performance** without Electron bloat, memory leaks and startup delays
- **Real-time responsiveness** that web-based tools simply can't deliver
- **Pure Python power** - no JavaScript framework chaos needed!

**Pygame isn't just for retro games!** It's the superior framework for high-performance visual applications, scientific tools, and creative projects.

> **For real developers who value performance over convenience.**
> While others struggle with Electron memory issues, we deliver buttery-smooth 60+ FPS experiences. Feel the difference! 💪


> [!WARNING]
> **No official Apple support!** It might run on macOS, but honestly, I don't care.
> Best experience on **Linux**. Works on **Windows** fine, too.


## 🤝 Contributing

This project is **open source**, and contributions are welcome\!
Bug reports, feature suggestions, and pull requests are highly appreciated.

-----

## 📝 License

Licensed under **AGPL 3.0**. See [LICENSE](LICENSE) for details.

Credits: Checked with Claude today and find a solution after 1 year! Thx. Now its alife 😄
> sorry dont have time befor. Readme.md updated by Claude Sonnet 5.5

