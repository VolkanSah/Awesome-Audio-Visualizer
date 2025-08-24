# detector.py run first this script it will generate your system file, it will be needed for the main funktion
import sys
import subprocess
import json
import os

def run_system_check():
    report = {}
    report['os'] = sys.platform
    report['python_version'] = sys.version
    report['dependencies'] = {}

    # Check for core dependencies
    deps = ['pygame', 'numpy', 'pyaudio', 'librosa']
    for dep in deps:
        try:
            __import__(dep)
            report['dependencies'][dep] = {'installed': True, 'version': 'N/A'} # You can add version check here later
        except ImportError:
            report['dependencies'][dep] = {'installed': False, 'version': None}

    # Check for FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        report['ffmpeg_status'] = 'found'
    except (subprocess.CalledProcessError, FileNotFoundError):
        report['ffmpeg_status'] = 'not_found'
    
    # Write report to JSON file
    with open('system_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("System check complete. Report saved to system_report.json")

if __name__ == "__main__":
    run_system_check()
