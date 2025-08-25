# specks so the system dont needt to scan all time and sou dont need to change always all   stuuf!
import sys
import subprocess
import json
import os
def find_ffmpeg():
    # Attempt to find ffmpeg using system commands
    if sys.platform == "win32":
        try:
            # where command for Windows
            result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, check=True)
            return result.stdout.strip().split('\n')[0] # get the first path found
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    else: # Linux or macOS
        try:
            # which command for Linux/macOS
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
def run_system_check():
    report = {}
    # ... (other checks) ...
    # Find and save the absolute path of FFmpeg
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        report['ffmpeg_path'] = ffmpeg_path
        report['ffmpeg_status'] = 'found'
    else:
        report['ffmpeg_path'] = None
        report['ffmpeg_status'] = 'not_found'

    with open('system_report.json', 'w') as f:
        json.dump(report, f, indent=4)

    print("System check complete. Report saved to system_report.json")
if name == "main":
    run_system_check()
