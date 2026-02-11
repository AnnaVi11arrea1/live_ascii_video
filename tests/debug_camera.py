"""
Debug script - Simple camera test without terminal UI
"""
import cv2
import time

print("Simple Camera Debug Test")
print("=" * 60)

# Get device
device = input("Camera device ID (usually 1): ").strip()
device_id = int(device) if device.isdigit() else 1

# Get color mode
print("\nColor mode:")
print("  1. Black & White (safest)")
print("  2. Rainbow")
print("  3. Normal colors")
choice = input("Choose (1-3): ").strip()
mode_map = {'1': 'bw', '2': 'rainbow', '3': 'normal'}
color_mode = mode_map.get(choice, 'bw')

print(f"\nOpening camera {device_id}...")
cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

print("Camera opened! Warming up...")
# Warm up
for i in range(5):
    ret, frame = cap.read()
    time.sleep(0.1)

print(f"Testing with {color_mode} mode...")
print("Capturing and converting 5 frames...\n")

# Import after we know camera works
from ascii_converter import AsciiConverter
converter = AsciiConverter(width=60, char_set="simple", aspect_ratio=0.25, color_mode=color_mode)

for i in range(5):
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print(f"Frame {i+1}: FAILED to capture")
        continue
    
    print(f"Frame {i+1}: Captured {frame.shape}")
    
    try:
        ascii_art = converter.image_to_ascii(frame)
        lines = ascii_art.split('\n')
        print(f"  ASCII: {len(lines)} lines generated")
        print(f"  First line length: {len(lines[0]) if lines else 0} chars")
        
        # Print first few lines
        print("  Preview (first 3 lines):")
        for j, line in enumerate(lines[:3]):
            # Show a snippet without colors for debugging
            clean_line = line.replace('\033[38;2;', '').replace('m', '').replace('\033[0', '')
            print(f"    Line {j+1} ({len(line)} chars): {clean_line[:40]}...")
        
    except Exception as e:
        print(f"  ERROR converting: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    time.sleep(0.5)

cap.release()
print("Test complete!")
