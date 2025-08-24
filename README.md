## Funktionen

### Visuelle Effekte

Der Visualizer bietet fünf einzigartige visuelle Modi, zwischen denen der Benutzer wechseln kann:

  * **Circular Bars**: Audiofrequenzen werden als radiale Balken visualisiert, die sich von einem zentralen Punkt ausdehnen.
  * **Waveform Tunnel**: Erzeugt einen 3D-Tunnel, dessen Form sich dynamisch an die Audio-Wellenform anpasst.
  * **Frequency Spiral**: Visualisiert die Frequenzdaten in Form einer leuchtenden, sich drehenden Spirale.
  * **Beat Explosion**: Bei jedem erkannten Beat wird eine Partikelexplosion ausgelöst, begleitet von sich schnell ändernden Balken.
  * **Matrix Rain**: Ein an den Film „Matrix“ angelehnter Effekt, bei dem fallende Symbole in Intensität und Farbe auf Audio-Eingaben reagieren.

### Farbpaletten

Für jeden Visualisierungsmodus stehen fünf verschiedene Farbpaletten zur Verfügung, um das visuelle Erlebnis anzupassen:

  * `fire` 🔥
  * `electric` ⚡
  * `ocean` 🌊
  * `rainbow` 🌈
  * `neon` ✨

### Audio-Steuerung

Wechsel zwischen Live-Modus und Datei-Modus:

  * **Live-Modus**: Verarbeitet Audio-Eingaben von einem angeschlossenen Mikrofon oder Standard-Eingabegerät in Echtzeit.
  * **Datei-Modus**: Lädt und analysiert eine lokale Audiodatei (z. B. MP3, WAV), um visuelle Effekte zu erzeugen. Die Wiedergabe kann pausiert, fortgesetzt und gestoppt werden.

-----

## Nutzung & Steuerung

Das Programm wird über die Tastatur gesteuert. Hier ist eine Übersicht der Hauptbefehle:

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
| `ESC` | **Beenden/Schließen** | Beendet das Programm oder schließt das aktive Einstellungs-/Geräte-Menü. |

-----

## Code-Struktur

Das Projekt ist in mehrere Komponenten aufgeteilt, um die Übersichtlichkeit zu verbessern:

  * `main.py`: Enthält die Hauptlogik der Anwendung und die **`HotVisualizer`**-Klasse, die die Visualisierungseffekte rendert und die Benutzerinteraktion verwaltet.
  * `audio.py`: Verwaltet die Audio-Verarbeitung und Live-Audio-Streams über die Klassen **`AudioDeviceManager`** und **`AudioProcessor`**.
  * `fileprocessor.py`: Kümmert sich um das Laden und Analysieren von Audiodateien mit der Klasse **`FileProcessor`**.
  * `mui.py`: Enthält UI-relevante Logik wie Einstellungen, Menüs und Screenshot-Funktionalität mit den Klassen **`SettingsManager`**, **`UIManager`**, und **`ScreenshotManager`**.
  * `particle.py`: Definiert die **`Particle`**-Klasse, die für die Partikeleffekte im Beat Explosion-Modus verwendet wird.

-----

## Anforderungen

Um das Projekt auszuführen, werden folgende Bibliotheken benötigt. Du kannst sie mit `pip` installieren:

```bash
pip install pygame numpy pyaudio librosa +++
```
