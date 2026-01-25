#!/usr/bin/env python3
"""
Generate default sound files for the chat application.
Run this script once to create the sound files.
"""
import wave
import math
import os
import sys

def create_beep_sound(filename, frequency, duration_ms, volume=0.5):
    """Create a simple beep WAV file."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)
    
    # Create audio data
    frames = []
    for i in range(num_samples):
        # Generate sine wave
        value = math.sin(2 * math.pi * frequency * i / sample_rate)
        # Apply envelope (fade in and out)
        envelope = min(1, i / (sample_rate * 0.01), (num_samples - i) / (sample_rate * 0.01))
        sample = int(value * envelope * volume * 32767)
        frames.append(sample.to_bytes(2, 'little', signed=True))
    
    # Write WAV file
    filepath = filename
    
    try:
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))
        return True
    except Exception as e:
        print(f"Error creating {filename}: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    sounds_dir = 'sounds'
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
    
    os.chdir(sounds_dir)
    
    print("Creating sound files...")
    
    # Create startup sound
    if create_beep_sound('startup.wav', 800, 150, 0.4):
        print("✓ Created startup.wav")
    
    # Create chat ding sound
    if create_beep_sound('ding.wav', 1000, 100, 0.4):
        print("✓ Created ding.wav")
    
    # Create ping alert sound
    if create_beep_sound('alert.wav', 1200, 250, 0.7):
        print("✓ Created alert.wav")
    
    print("✓ All sound files created successfully")
