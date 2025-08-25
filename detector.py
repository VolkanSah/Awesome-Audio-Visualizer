# Universal Audio Device Detector
# A simple tool for detection stuff, later more features but so its easier for develop and system 
# specs so the system don't need to scan all time and so don't need to change always all stuff!
# Copyright Volkan Sah!

import sys
import subprocess
import json
import os
import platform
import tempfile
from datetime import datetime

def check_workdir_writable():
    """Check if current working directory is writable"""
    try:
        # Try to create a temporary file in current directory
        test_file = os.path.join(os.getcwd(), '.write_test_temp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return {
            'writable': True,
            'path': os.getcwd(),
            'error': None
        }
    except Exception as e:
        return {
            'writable': False,
            'path': os.getcwd(),
            'error': str(e)
        }

def find_ffmpeg():
    """Attempt to find ffmpeg using system commands"""
    if sys.platform == "win32":
        try:
            # `where` command for Windows
            result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, check=True)
            return result.stdout.strip().split('\n')[0]  # get the first path found
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    else:  # Linux or macOS
        try:
            # `which` command for Linux/macOS
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

def create_device_endpoint(device_name, device_type, index=None, method=None):
    """Create API-like endpoint identifier for device"""
    # Clean device name for endpoint
    clean_name = device_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    
    # Create endpoint structure
    endpoint = {
        'endpoint_id': f"{device_type}_{index if index is not None else clean_name}",
        'api_path': f"/audio/devices/{device_type}/{index if index is not None else clean_name}",
        'rest_endpoint': f"GET /api/v1/audio/{device_type}/{clean_name}",
        'direct_access': clean_name
    }
    
    # Add method-specific identifiers
    if method == 'ffmpeg_directshow':
        endpoint['ffmpeg_identifier'] = f'audio="{device_name}"'
    elif method == 'ffmpeg_pulse':
        endpoint['ffmpeg_identifier'] = f'pulse:{clean_name}'
    elif method == 'ffmpeg_alsa':
        endpoint['ffmpeg_identifier'] = f'alsa:{clean_name}'
    elif method == 'ffmpeg_avfoundation':
        endpoint['ffmpeg_identifier'] = f'avfoundation:{index if index is not None else clean_name}'
    elif method == 'pyaudio':
        endpoint['pyaudio_index'] = index
    
    return endpoint

def get_audio_devices():
    """Get all audio input devices using various methods"""
    devices = {
        'microphones': [],
        'all_audio_inputs': [],
        'detection_method': None,
        'error': None
    }
    
    # Method 1: Try ffmpeg first (most reliable)
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        try:
            if sys.platform == "win32":
                # Windows: Use DirectShow
                result = subprocess.run([
                    ffmpeg_path, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'
                ], capture_output=True, text=True)
                
                lines = result.stderr.split('\n')  # FFmpeg outputs to stderr
                current_type = None
                device_index = 0
                
                for line in lines:
                    line = line.strip()
                    if '"DirectShow video devices"' in line:
                        current_type = 'video'
                    elif '"DirectShow audio devices"' in line:
                        current_type = 'audio'
                        device_index = 0
                    elif current_type == 'audio' and '] "' in line:
                        # Extract device name from ffmpeg output
                        device_name = line.split('] "')[1].split('"')[0]
                        endpoint = create_device_endpoint(device_name, 'microphone', device_index, 'ffmpeg_directshow')
                        
                        device_info = {
                            'name': device_name,
                            'description': device_name,
                            'type': 'microphone',
                            'detection_method': 'ffmpeg_directshow',
                            'endpoints': endpoint
                        }
                        devices['microphones'].append(device_info)
                        devices['all_audio_inputs'].append(device_info)
                        device_index += 1
                
                devices['detection_method'] = 'ffmpeg_directshow'
                
            else:
                # Linux/macOS: Try different audio systems
                methods = []
                
                # Try PulseAudio (Linux)
                if platform.system() == "Linux":
                    methods.append(('pulse', 'ffmpeg_pulse'))
                    methods.append(('alsa', 'ffmpeg_alsa'))
                
                # Try AVFoundation (macOS)
                elif platform.system() == "Darwin":
                    methods.append(('avfoundation', 'ffmpeg_avfoundation'))
                
                for method_name, detection_method in methods:
                    try:
                        if method_name == 'avfoundation':
                            result = subprocess.run([
                                ffmpeg_path, '-f', 'avfoundation', '-list_devices', 'true', '-i', ''
                            ], capture_output=True, text=True)
                        else:
                            result = subprocess.run([
                                ffmpeg_path, '-f', method_name, '-list_devices', 'true', '-i', ''
                            ], capture_output=True, text=True)
                        
                        lines = result.stderr.split('\n')
                        device_index = 0
                        
                        for line in lines:
                            if ('microphone' in line.lower() or 'input' in line.lower()) and '] [' in line:
                                # Parse device info
                                parts = line.split('] ')
                                if len(parts) >= 2:
                                    device_name = parts[1].strip()
                                    endpoint = create_device_endpoint(device_name, 'microphone', device_index, detection_method)
                                    
                                    device_info = {
                                        'name': device_name,
                                        'description': device_name,
                                        'type': 'microphone',
                                        'detection_method': detection_method,
                                        'endpoints': endpoint
                                    }
                                    devices['microphones'].append(device_info)
                                    devices['all_audio_inputs'].append(device_info)
                                    device_index += 1
                        
                        if devices['microphones']:
                            devices['detection_method'] = detection_method
                            break
                            
                    except Exception:
                        continue
                        
        except Exception as e:
            devices['error'] = f"FFmpeg detection failed: {str(e)}"
    
    # Method 2: Try system-specific commands if ffmpeg failed
    if not devices['microphones']:
        try:
            if sys.platform == "win32":
                # Windows: Try PowerShell WMI
                ps_command = '''
                Get-WmiObject -Class Win32_SoundDevice | Where-Object {$_.Name -ne $null} | Select-Object Name, Description | ConvertTo-Json
                '''
                result = subprocess.run(['powershell', '-Command', ps_command], 
                                      capture_output=True, text=True, check=True)
                
                if result.stdout.strip():
                    ps_devices = json.loads(result.stdout)
                    if not isinstance(ps_devices, list):
                        ps_devices = [ps_devices]
                    
                    for i, device in enumerate(ps_devices):
                        device_name = device.get('Name', 'Unknown')
                        endpoint = create_device_endpoint(device_name, 'microphone', i, 'powershell_wmi')
                        
                        device_info = {
                            'name': device_name,
                            'description': device.get('Description', device_name),
                            'type': 'microphone',
                            'detection_method': 'powershell_wmi',
                            'endpoints': endpoint
                        }
                        devices['microphones'].append(device_info)
                        devices['all_audio_inputs'].append(device_info)
                    
                    devices['detection_method'] = 'powershell_wmi'
                    
            elif platform.system() == "Linux":
                # Linux: Try arecord
                try:
                    result = subprocess.run(['arecord', '-l'], capture_output=True, text=True, check=True)
                    lines = result.stdout.split('\n')
                    device_index = 0
                    
                    for line in lines:
                        if 'card' in line and ':' in line:
                            # Parse arecord output
                            parts = line.split(':')
                            if len(parts) >= 2:
                                device_name = parts[1].strip()
                                endpoint = create_device_endpoint(device_name, 'microphone', device_index, 'arecord')
                                endpoint['alsa_identifier'] = line.split('[')[0].strip() if '[' in line else line
                                
                                device_info = {
                                    'name': device_name,
                                    'description': device_name,
                                    'type': 'microphone',
                                    'detection_method': 'arecord',
                                    'endpoints': endpoint
                                }
                                devices['microphones'].append(device_info)
                                devices['all_audio_inputs'].append(device_info)
                                device_index += 1
                    
                    if devices['microphones']:
                        devices['detection_method'] = 'arecord'
                        
                except Exception:
                    pass
                    
            elif platform.system() == "Darwin":
                # macOS: Try system_profiler
                try:
                    result = subprocess.run(['system_profiler', 'SPAudioDataType', '-json'], 
                                          capture_output=True, text=True, check=True)
                    audio_data = json.loads(result.stdout)
                    device_index = 0
                    
                    for item in audio_data.get('SPAudioDataType', []):
                        if 'input' in item.get('_name', '').lower() or 'microphone' in item.get('_name', '').lower():
                            device_name = item.get('_name', 'Unknown')
                            endpoint = create_device_endpoint(device_name, 'microphone', device_index, 'system_profiler')
                            
                            device_info = {
                                'name': device_name,
                                'description': device_name,
                                'type': 'microphone',
                                'detection_method': 'system_profiler',
                                'endpoints': endpoint
                            }
                            devices['microphones'].append(device_info)
                            devices['all_audio_inputs'].append(device_info)
                            device_index += 1
                    
                    if devices['microphones']:
                        devices['detection_method'] = 'system_profiler'
                        
                except Exception:
                    pass
                    
        except Exception as e:
            if not devices['error']:
                devices['error'] = f"System-specific detection failed: {str(e)}"
    
    # Method 3: Try Python libraries as fallback
    if not devices['microphones']:
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            
            for i in range(device_count):
                device_info_raw = p.get_device_info_by_index(i)
                if device_info_raw['maxInputChannels'] > 0:  # Input device
                    device_name = device_info_raw['name']
                    endpoint = create_device_endpoint(device_name, 'microphone', i, 'pyaudio')
                    endpoint['pyaudio_index'] = i
                    endpoint['channels'] = device_info_raw['maxInputChannels']
                    endpoint['sample_rate'] = device_info_raw['defaultSampleRate']
                    
                    device_info = {
                        'name': device_name,
                        'description': device_name,
                        'type': 'microphone',
                        'detection_method': 'pyaudio',
                        'endpoints': endpoint
                    }
                    devices['microphones'].append(device_info)
                    devices['all_audio_inputs'].append(device_info)
            
            p.terminate()
            devices['detection_method'] = 'pyaudio'
            
        except ImportError:
            if not devices['error']:
                devices['error'] = "PyAudio not available and other methods failed"
        except Exception as e:
            if not devices['error']:
                devices['error'] = f"PyAudio detection failed: {str(e)}"
    
    return devices

def get_system_info():
    """Get basic system information"""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'timestamp': datetime.now().isoformat()
    }

def run_system_check():
    """Main function to run all system checks"""
    print("Starting Universal Audio Device Detection...")
    
    # Build report in exact format requested
    report = {
        'system_info': get_system_info(),
        'workdir_check': check_workdir_writable(),
        'ffmpeg': {},
        'audio_devices': {}
    }
    
    # FFmpeg detection
    print("Checking for FFmpeg...")
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        report['ffmpeg']['path'] = ffmpeg_path
        report['ffmpeg']['status'] = 'found'
        print(f"✓ FFmpeg found at: {ffmpeg_path}")
    else:
        report['ffmpeg']['path'] = None
        report['ffmpeg']['status'] = 'not_found'
        print("✗ FFmpeg not found in PATH")
    
    # Working directory check
    workdir_status = report['workdir_check']
    if workdir_status['writable']:
        print(f"✓ Working directory is writable: {workdir_status['path']}")
    else:
        print(f"✗ Working directory not writable: {workdir_status['error']}")
    
    # Audio device detection
    print("Detecting audio devices and creating endpoints...")
    audio_devices = get_audio_devices()
    report['audio_devices'] = audio_devices
    
    if audio_devices['microphones']:
        print(f"✓ Found {len(audio_devices['microphones'])} audio input device(s):")
        for i, device in enumerate(audio_devices['microphones'], 1):
            print(f"  {i}. {device['name']}")
            print(f"     Endpoint: {device['endpoints']['api_path']}")
            if 'ffmpeg_identifier' in device['endpoints']:
                print(f"     FFmpeg: {device['endpoints']['ffmpeg_identifier']}")
    else:
        print("✗ No audio input devices found")
        if audio_devices['error']:
            print(f"  Error: {audio_devices['error']}")
    
    # Save complete report (only one file as requested)
    try:
        with open('system_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"\n✓ System check complete. Report saved to system_report.json")
        
    except Exception as e:
        print(f"✗ Failed to save report: {str(e)}")
        return False
    
    return True

def print_summary():
    """Print a summary of what was detected"""
    if os.path.exists('system_report.json'):
        try:
            with open('system_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            print("\n" + "="*60)
            print("DETECTION SUMMARY")
            print("="*60)
            
            print(f"System: {report['system_info']['platform']} {report['system_info']['architecture']}")
            print(f"Python: {report['system_info']['python_version']}")
            
            print(f"\nWorking Directory: {'✓ Writable' if report['workdir_check']['writable'] else '✗ Not writable'}")
            
            print(f"FFmpeg: {'✓ Available' if report['ffmpeg']['status'] == 'found' else '✗ Not found'}")
            if report['ffmpeg']['path']:
                print(f"  Path: {report['ffmpeg']['path']}")
            
            audio_count = len(report['audio_devices']['microphones'])
            print(f"Audio Devices: {'✓' if audio_count > 0 else '✗'} {audio_count} input device(s)")
            
            if report['audio_devices']['detection_method']:
                print(f"  Detection method: {report['audio_devices']['detection_method']}")
            
            # Show API endpoints
            if audio_count > 0:
                print(f"\nAPI ENDPOINTS:")
                for device in report['audio_devices']['microphones']:
                    endpoints = device['endpoints']
                    print(f"  Device: {device['name']}")
                    print(f"    REST: {endpoints['rest_endpoint']}")
                    print(f"    Path: {endpoints['api_path']}")
                    print(f"    ID: {endpoints['endpoint_id']}")
            
        except Exception as e:
            print(f"Error reading summary: {str(e)}")

def print_usage_examples():
    """Print usage examples for the universal platform tool"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES FOR YOUR UNIVERSAL PLATFORM TOOL:")
    print("="*60)
    print("1. Load settings once at startup:")
    print("   with open('system_report.json', 'r') as f:")
    print("       config = json.load(f)")
    print("")
    print("2. Access devices by endpoint:")
    print("   devices = config['audio_devices']['microphones']")
    print("   first_mic = devices[0]['endpoints']['direct_access']")
    print("")
    print("3. Use with FFmpeg:")
    print("   ffmpeg_cmd = devices[0]['endpoints']['ffmpeg_identifier']")
    print("")
    print("4. Check if re-scan needed:")
    print("   last_scan = config['system_info']['timestamp']")
    print("   # Compare with current time")
    print("")
    print("5. Access by API-style endpoint:")
    print("   GET /api/v1/audio/microphone/realtek_high_definition_audio")

if __name__ == "__main__":
    success = run_system_check()
    if success:
        print_summary()
        print_usage_examples()
    else:
        print("System check failed!")
        sys.exit(1)
