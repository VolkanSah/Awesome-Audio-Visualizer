# -----------------------------------------------------------------------------
# 6. Export functions - merge_video_audio (Automated)
# File: decoder.py
# Updated for new system_report.json format with audio device endpoints
# -----------------------------------------------------------------------------
import argparse
import subprocess
import os
import json
from datetime import datetime

# Load system configuration from system_report.json
def load_system_config():
    """Load complete system configuration including FFmpeg and audio devices"""
    config_file = 'system_report.json'
    if not os.path.exists(config_file):
        raise FileNotFoundError("system_report.json not found. Please run detector first.")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_ffmpeg_path():
    """Get FFmpeg path from system configuration"""
    config = load_system_config()
    
    # Access FFmpeg path from new JSON structure
    ffmpeg_info = config.get("ffmpeg", {})
    ffmpeg_path = ffmpeg_info.get("path")
    ffmpeg_status = ffmpeg_info.get("status")
    
    if ffmpeg_status != "found" or not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found in system configuration.")
    
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"FFmpeg path invalid: {ffmpeg_path}")
    
    return ffmpeg_path

def get_audio_devices():
    """Get available audio devices with their endpoints"""
    config = load_system_config()
    audio_devices = config.get("audio_devices", {})
    
    return {
        'microphones': audio_devices.get('microphones', []),
        'detection_method': audio_devices.get('detection_method'),
        'count': len(audio_devices.get('microphones', []))
    }

def list_audio_devices():
    """List all available audio devices with their API endpoints"""
    devices = get_audio_devices()
    
    if devices['count'] == 0:
        print("No audio devices found.")
        return
    
    print(f"\nAvailable Audio Devices ({devices['count']} found):")
    print("-" * 50)
    
    for i, device in enumerate(devices['microphones']):
        print(f"{i+1}. {device['name']}")
        print(f"   Description: {device['description']}")
        print(f"   Method: {device['detection_method']}")
        
        # Show endpoint info
        endpoints = device.get('endpoints', {})
        print(f"   API Path: {endpoints.get('api_path', 'N/A')}")
        print(f"   Endpoint ID: {endpoints.get('endpoint_id', 'N/A')}")
        
        if 'ffmpeg_identifier' in endpoints:
            print(f"   FFmpeg ID: {endpoints['ffmpeg_identifier']}")
        if 'pyaudio_index' in endpoints:
            print(f"   PyAudio Index: {endpoints['pyaudio_index']}")
        
        print()

def get_device_by_endpoint(endpoint_id):
    """Get device by its endpoint ID"""
    devices = get_audio_devices()
    
    for device in devices['microphones']:
        if device['endpoints']['endpoint_id'] == endpoint_id:
            return device
    
    return None

def get_device_by_name(device_name):
    """Get device by name (fuzzy match)"""
    devices = get_audio_devices()
    device_name_lower = device_name.lower()
    
    # Exact match first
    for device in devices['microphones']:
        if device['name'].lower() == device_name_lower:
            return device
    
    # Partial match
    for device in devices['microphones']:
        if device_name_lower in device['name'].lower():
            return device
    
    return None

# Merge Video + Audio
def merge_video_audio(video_path, audio_path, output_path=None):
    """Merge video and audio files using FFmpeg"""
    if not os.path.exists(video_path):
        return {"status": "error", "message": f"Video file not found: {video_path}"}
    if not os.path.exists(audio_path):
        return {"status": "error", "message": f"Audio file not found: {audio_path}"}
    
    try:
        ffmpeg_path = get_ffmpeg_path()
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    
    # Default Output-Pfad
    if not output_path:
        base, _ = os.path.splitext(video_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{base}_merged_{timestamp}.mp4"
    
    command = [
        ffmpeg_path,
        '-y',  # overwrite
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return {
            "status": "success", 
            "output": output_path,
            "ffmpeg_path": ffmpeg_path,
            "command_used": ' '.join(command)
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error", 
            "message": f"FFmpeg failed: {e}",
            "stderr": e.stderr if hasattr(e, 'stderr') else str(e)
        }

def record_from_device(device_endpoint_id, duration=10, output_file=None):
    """Record audio from specific device using its endpoint ID"""
    device = get_device_by_endpoint(device_endpoint_id)
    if not device:
        return {"status": "error", "message": f"Device with endpoint '{device_endpoint_id}' not found"}
    
    try:
        ffmpeg_path = get_ffmpeg_path()
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"recording_{device_endpoint_id}_{timestamp}.wav"
    
    # Build FFmpeg command based on detection method
    endpoints = device['endpoints']
    
    if 'ffmpeg_identifier' in endpoints:
        # Use FFmpeg identifier
        ffmpeg_input = endpoints['ffmpeg_identifier']
        
        if device['detection_method'] == 'ffmpeg_directshow':
            command = [ffmpeg_path, '-f', 'dshow', '-i', ffmpeg_input, '-t', str(duration), output_file]
        elif 'pulse' in device['detection_method']:
            command = [ffmpeg_path, '-f', 'pulse', '-i', ffmpeg_input, '-t', str(duration), output_file]
        elif 'alsa' in device['detection_method']:
            command = [ffmpeg_path, '-f', 'alsa', '-i', ffmpeg_input, '-t', str(duration), output_file]
        elif 'avfoundation' in device['detection_method']:
            command = [ffmpeg_path, '-f', 'avfoundation', '-i', ffmpeg_input, '-t', str(duration), output_file]
        else:
            return {"status": "error", "message": f"Unsupported detection method: {device['detection_method']}"}
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return {
                "status": "success",
                "output": output_file,
                "device": device['name'],
                "duration": duration,
                "command": ' '.join(command)
            }
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Recording failed: {e}"}
    
    else:
        return {"status": "error", "message": "No FFmpeg identifier available for this device"}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Video/Audio processing with device endpoint support.")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge video and audio files')
    merge_parser.add_argument('video_path', help="Path to the video file.")
    merge_parser.add_argument('audio_path', help="Path to the audio file.")
    merge_parser.add_argument('--output', help="Optional: Path for the merged output file.")
    
    # List devices command
    list_parser = subparsers.add_parser('devices', help='List available audio devices')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record from audio device')
    record_parser.add_argument('device_id', help="Device endpoint ID (e.g., microphone_0)")
    record_parser.add_argument('--duration', type=int, default=10, help="Recording duration in seconds")
    record_parser.add_argument('--output', help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == 'merge':
        result = merge_video_audio(args.video_path, args.audio_path, args.output)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'devices':
        list_audio_devices()
        
    elif args.command == 'record':
        result = record_from_device(args.device_id, args.duration, args.output)
        print(json.dumps(result, indent=2))
        
    else:
        parser.print_help()
