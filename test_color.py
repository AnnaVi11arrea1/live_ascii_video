"""
Test color modes with live camera - Simple version
"""
import cv2
import time
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

print("Color Mode Test")
print("=" * 60)

device = input("Camera device (0 or 1, usually 1): ").strip()
device_id = int(device) if device.isdigit() else 1

print("\nOpening camera...")
cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Cannot open camera!")
    exit(1)

# Warm up
for _ in range(5):
    cap.read()

print("Testing BLACK & WHITE mode first (safest)...")
print("This will show 3 test frames\n")
time.sleep(2)

from ascii_converter import AsciiConverter

converter = AsciiConverter(width=60, aspect_ratio=0.25, color_mode='bw')

for i in range(3):
    ret, frame = cap.read()
    if not ret:
        print(f"Frame {i+1}: Failed")
        continue
    
    ascii_art = converter.image_to_ascii(frame)
    
    clear()
    print(ascii_art)
    print(f"\nFrame {i+1}/3 - Black & White Mode")
    print("Press Ctrl+C to stop")
    time.sleep(1)

cap.release()
print("\nTest complete! If this worked, try:")
print("  python main.py --host --device 1 --color bw")
print("  python main.py --host --device 1 --color rainbow")

