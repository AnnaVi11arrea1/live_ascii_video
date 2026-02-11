"""
Test ASCII density and aspect ratio
"""
import cv2
import time
import os
from ascii_converter import AsciiConverter

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

print("ASCII Density Test")
print("=" * 60)

device = input("Camera device (usually 1): ").strip()
device_id = int(device) if device.isdigit() else 1

print("\nTesting different aspect ratios...")
print("Lower aspect ratio = more vertical lines = more detail\n")

print("Opening camera...")
cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("ERROR: Cannot open camera")
    exit(1)

# Warm up
for _ in range(5):
    cap.read()

# Test different aspect ratios
aspect_ratios = [
    (0.25, "Normal (0.25)"),
    (0.12, "Double density (0.12)"),
    (0.06, "Quad density (0.06)")
]

for aspect, name in aspect_ratios:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    converter = AsciiConverter(width=80, aspect_ratio=aspect, color_mode='bw')
    
    ret, frame = cap.read()
    if ret:
        ascii_art = converter.image_to_ascii(frame)
        lines = ascii_art.split('\n')
        
        clear()
        print(ascii_art)
        print(f"\n{name} - Generated {len(lines)} lines")
        print("Press Enter to continue...")
        input()

cap.release()
print("\nDone! The 0.12 aspect ratio gives 2x more lines than 0.25")
