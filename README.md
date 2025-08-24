# 🎧 Awesome-Audio-Visualizer

Welcome to **Awesome-Audio-Visualizer**, an open-source tool that transforms audio into stunning visual effects.  
This project was born from the passion to create a customizable and scalable visualizer that works not only for personal music but also for videos and live streams.

⚠️ **No official Apple support!** It might run on macOS, but honestly, I don't care.  
> Best experience on **Linux**. Works on **Windows** too, but enjoy the combo of Realtek + FFMPEG + Windows. Good luck! 😏  



#### 💡 Why this project?

Most existing visualizers are either closed-source or offer limited customization. My goal was to build a tool that is easy to use yet powerful enough to unleash your creativity.  
With this project, you can give your music a visual soul. Future updates will include features like video export and more unique effects – a **K-Pop artifact** is promised! 😉

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

---

### Color Palettes

Each visualization mode supports five customizable color palettes:

* `fire` 🔥  
* `electric` ⚡  
* `ocean` 🌊  
* `rainbow` 🌈  
* `neon` ✨  

---

### Audio Control

Two input modes supported:

* **Live Mode** – Processes real-time audio input from a connected microphone or standard device.
* **File Mode** – Loads and analyzes a local audio file (e.g., MP3, WAV) to generate visuals. Playback can be paused, resumed, or stopped.

---

## ⌨️ Controls

The program is controlled via an intuitive keyboard interface:

| Key | Action | Description |
| :--- | :--- | :--- |
| `SPACE` | **Switch Mode** | Cycles through the 5 visualization modes. |
| `C` | **Change Color Palette** | Switches to the next available color palette. |
| `A` | **Load Audio File** | Opens a dialog to choose a local audio file for visualization. |
| `L` | **Back to Live Mode** | Switches from file mode to live audio input. |
| `P` | **Play / Pause** | Starts or pauses playback of the loaded file. *(File mode only)* |
| `K` | **Stop** | Stops file playback. *(File mode only)* |
| `F` | **Fullscreen** | Toggles fullscreen mode. |
| `S` | **Screenshot** | Saves a screenshot of the current visualizer. |
| `TAB` | **Settings** | Opens an advanced settings menu. |
| `D` | **Device Menu** | Select an audio input device. *(Live mode only)* |
| `Q` / `W` | **Beat Sensitivity** | Adjusts beat detection sensitivity. *(Live mode only)* |
| `R` | **Export** | Exports visualization + audio as MP4. *(Not available in live mode)* |
| `ESC` | **Exit** | Closes the program or the active settings/device menu. |

---

## 📂 Project Structure

The project is modular for better organization and maintainability:

* `main.py` – Core logic and **`HotVisualizer`** class handling rendering and user interaction.
* `audio.py` – Audio processing and live audio stream handling via **`AudioDeviceManager`** and **`AudioProcessor`**.
* `fileprocessor.py` – Loads and analyzes audio files with the **`FileProcessor`** class.
* `mui.py` – UI-related logic: settings, menus, screenshot functionality via **`SettingsManager`**, **`UIManager`**, **`ScreenshotManager`**.
* `particle.py` – Defines the **`Particle`** class for the Beat Explosion mode.
* `detector.py` – Generates **`system_report.json`** with required FFmpeg paths based on OS (must run first for export to work).
* `decoder.py` – Defines **`merge_video_audio`** (not finished yet). Integrated in `main.py` with shortcode but no final effect.

---

## ⚙️ Requirements

Install the required dependencies via `pip`:

```bash
pip install pygame numpy pyaudio librosa
````

### Detailed Dependencies:

* `pygame` – Graphics and window management.
* `numpy` – Fast Fourier Transform (FFT) and array operations.
* `pyaudio` – Live audio input handling.
* `librosa` – Advanced audio analysis functions.

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

---

## 🤝 Contributing

This project is **open source**, and contributions are welcome!
Bug reports, feature suggestions, and pull requests are highly appreciated.

---

## 📝 License

Licensed under **Apache 2.0**. See [LICENSE](LICENSE) for details.


