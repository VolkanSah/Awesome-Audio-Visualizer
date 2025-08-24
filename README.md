# 🎧 Awesome-Audio-Visualizer

Willkommen bei **Awesome-Audio-Visualizer**, einem Open-Source-Tool, das Audio in faszinierende visuelle Effekte verwandelt. Dieses Projekt wurde aus der Leidenschaft heraus geboren, einen anpassbaren und skalierbaren Visualizer zu erschaffen, der sich nicht nur für persönliche Musik, sondern auch für Videos und Live-Streams eignet.

---

## 💡 Warum dieses Projekt?

Viele existierende Visualizer sind nicht frei zugänglich oder bieten nur begrenzte Anpassungsmöglichkeiten. Mein Ziel war es, ein Tool zu entwickeln, das einfach zu bedienen und gleichzeitig mächtig genug ist, um der Kreativität keine Grenzen zu setzen. Mit diesem Projekt kannst du deiner Musik eine visuelle Seele geben. Zukünftige Updates werden Features wie Video-Export und weitere einzigartige Effekte enthalten – ein K-Pop-Artefakt ist versprochen! 😉

---

## ✨ Features

### Visuelle Effekte

Der Visualizer bietet fünf einzigartige visuelle Modi, zwischen denen du einfach wechseln kannst. Jeder Modus reagiert dynamisch auf deine Audio-Eingabe:

* **Circular Bars**: Visualisiert Audiofrequenzen als radiale Balken, die sich von einem zentralen Punkt ausdehnen.
* **Waveform Tunnel**: Erzeugt einen 3D-Tunnel, dessen Form sich dynamisch an die Audio-Wellenform anpasst.
* **Frequency Spiral**: Visualisiert die Frequenzdaten in Form einer leuchtenden, sich drehenden Spirale.
* **Beat Explosion**: Bei jedem erkannten Beat wird eine Partikelexplosion ausgelöst, begleitet von schnell pulsierenden Balken.
* **Matrix Rain**: Ein an den Film „Matrix“ angelehnter Effekt, bei dem fallende Symbole in Intensität und Farbe auf Audio-Eingaben reagieren.

### Farbpaletten

Für jeden Visualisierungsmodus stehen fünf anpassbare Farbpaletten zur Verfügung:

* `fire` 🔥
* `electric` ⚡
* `ocean` 🌊
* `rainbow` 🌈
* `neon` ✨

### Audio-Steuerung

Das Projekt unterstützt zwei Audio-Eingabemodi:

* **Live-Modus**: Verarbeitet Audio-Eingaben von einem angeschlossenen Mikrofon oder einem Standard-Eingabegerät in Echtzeit.
* **Datei-Modus**: Lädt und analysiert eine lokale Audiodatei (z. B. MP3, WAV), um visuelle Effekte zu erzeugen. Die Wiedergabe kann pausiert, fortgesetzt und gestoppt werden.

---

## ⌨️ Nutzung & Steuerung

Die Steuerung des Programms erfolgt intuitiv über die Tastatur. Hier ist eine Übersicht der wichtigsten Befehle:

| Taste | Aktion | Beschreibung |
| :--- | :--- | :--- |
| `SPACE` | **Modus wechseln** | Schaltet zwischen den 5 Visualisierungsmodi um. |
| `C` | **Farbpalette wechseln** | Wechselt zur nächsten verfügbaren Farbpalette. |
| `A` | **Audio-Datei laden** | Öffnet einen Dialog, um eine lokale Audiodatei zum Visualisieren auszuwählen. |
| `L` | **Zurück in den Live-Modus** | Schaltet vom Datei-Modus zurück zur Live-Audio-Aufnahme. |
| `P` | **Wiedergabe umschalten** | Startet oder pausiert die Wiedergabe einer geladenen Datei. (Nur im Datei-Modus). |
| `K` | **Wiedergabe stoppen** | Stoppt die Wiedergabe einer Datei. (Nur im Datei-Modus). |
| `F` | **Vollbild** | Schaltet zwischen Vollbild- und Fenstermodus um. |
| `S` | **Screenshot** | Speichert einen Screenshot des aktuellen Visualizers. |
| `TAB` | **Einstellungen** | Zeigt ein Menü an, um erweiterte Einstellungen zu ändern. |
| `D` | **Geräte-Menü** | Öffnet ein Menü zur Auswahl des Audio-Eingabegeräts. (Nur im Live-Modus). |
| `Q`/`W` | **Beat-Empfindlichkeit** | Passt die Empfindlichkeit der Beat-Erkennung an. (Nur im Live-Modus). |
| `R` | **Export** | Exportiert Visualisierung + Audio als MP4 . (nicht im Live-Modus). | 
| `ESC` | **Beenden/Schließen** | Beendet das Programm oder schließt das aktive Einstellungs-/Geräte-Menü. |

---

## 📂 Code-Struktur

Das Projekt ist in mehrere Komponenten aufgeteilt, um die Übersichtlichkeit zu verbessern und die Wartung zu erleichtern:

* `main.py`: Enthält die Hauptlogik der Anwendung und die **`HotVisualizer`**-Klasse, die die Visualisierungseffekte rendert und die Benutzerinteraktion verwaltet.
* `audio.py`: Verwaltet die Audio-Verarbeitung und Live-Audio-Streams über die Klassen **`AudioDeviceManager`** und **`AudioProcessor`**.
* `fileprocessor.py`: Kümmert sich um das Laden und Analysieren von Audiodateien mit der Klasse **`FileProcessor`**.
* `mui.py`: Enthält UI-relevante Logik wie Einstellungen, Menüs und Screenshot-Funktionalität mit den Klassen **`SettingsManager`**, **`UIManager`**, und **`ScreenshotManager`**.
* `particle.py`: Definiert die **`Particle`**-Klasse, die für die Partikeleffekte im Beat Explosion-Modus verwendet wird.
* `decoder.py`: Definiert die **`merge_video_audio`** nicht fertig!. in main.py eingebunden schon Shorcode nutzbar aber kein effekt! 

---

## ⚙️ Anforderungen

Um das Projekt auszuführen, werden folgende Bibliotheken benötigt. Du kannst sie einfach mit `pip` installieren:

```bash
pip install pygame numpy pyaudio librosa
````

### Detaillierte Abhängigkeiten

**Erforderliche externe Bibliotheken:**

  * `pygame` - für die Grafik und das Fenster-Management.
  * `numpy` - für die schnelle Fourier-Transformation (FFT) und Array-Operationen.
  * `pyaudio` - für die Verarbeitung von Live-Audio-Eingaben vom Mikrofon.
  * `librosa` - für erweiterte Audio-Analysefunktionen.

**Hinweis zu `pyaudio`:**
Manchmal kann es bei der Installation von `pyaudio` zu Problemen kommen. Hier sind alternative Installationsanweisungen für verschiedene Betriebssysteme:

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

Sollten diese Schritte nicht funktionieren, kannst du stattdessen `sounddevice` verwenden:

```bash
pip install sounddevice
```

-----

## 🤝 Mitwirken

Dieses Projekt ist Open Source. Ich freue mich über jede Unterstützung\! Ob Bug-Reports, Feature-Vorschläge oder Code-Beiträge – jeder Beitrag ist willkommen.

-----

## 📝 Lizenz

Dieses Projekt ist unter der Apache 2-Lizenz lizenziert. Weitere Informationen findest du in der [LICENSE](LICENSE)-Datei.

