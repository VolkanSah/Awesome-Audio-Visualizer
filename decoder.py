# -----------------------------------------------------------------------------
# 6. Export functions - merge_video_audio , merge_video_audio 
# File: decoder.py
# -----------------------------------------------------------------------------
import argparse
import subprocess
import os

def merge_video_audio(video_path, audio_path, output_path):
    """
    Fügt Video- und Audiodateien zusammen.
    """
    # Überprüfe, ob die Dateien existieren
    if not os.path.exists(video_path):
        print(f"Fehler: Videodatei nicht gefunden: {video_path}")
        return
    if not os.path.exists(audio_path):
        print(f"Fehler: Audiodatei nicht gefunden: {audio_path}")
        return

    # FFmpeg-Kommando zum Mergen
    command = [
        'ffmpeg',
        '-y',  # Überschreibt Ausgabedatei ohne Nachfrage
        '-i', video_path,  # Eingabe Video
        '-i', audio_path,  # Eingabe Audio
        '-c:v', 'copy',  # Video-Codec kopieren
        '-c:a', 'aac',  # Audio-Codec
        '-map', '0:v:0',  # Mappe Video Stream
        '-map', '1:a:0',  # Mappe Audio Stream
        output_path  # Ausgabe
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Erfolgreich gemerged: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei FFmpeg-Ausführung: {e}")
    except FileNotFoundError:
        print("Fehler: FFmpeg nicht im Systempfad gefunden. Bitte installieren Sie es.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merges a video and an audio file.")
    parser.add_argument('video_path', help="Path to the video file.")
    parser.add_argument('audio_path', help="Path to the audio file.")
    parser.add_argument('output_path', help="Path for the final merged output.")

    args = parser.parse_args()
    merge_video_audio(args.video_path, args.audio_path, args.output_path)
