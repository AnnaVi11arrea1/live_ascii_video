"""
Find available camera devices
"""
import cv2

print("Searching for camera devices...")
print("="*60)

found_cameras = []

# Try devices 0-5
for i in range(6):
    print(f"\nTrying device {i}...", end=" ")
    
    # Try with DirectShow (Windows)
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ FOUND! Resolution: {frame.shape[1]}x{frame.shape[0]}")
            found_cameras.append(i)
        else:
            print("✗ Opened but no frames")
        cap.release()
    else:
        # Try without DirectShow
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ FOUND! Resolution: {frame.shape[1]}x{frame.shape[0]}")
                found_cameras.append(i)
            else:
                print("✗ Opened but no frames")
            cap.release()
        else:
            print("✗ Not available")

print("\n" + "="*60)
if found_cameras:
    print(f"\nFound {len(found_cameras)} camera(s): {found_cameras}")
    print(f"\nUse: python main.py --host --device {found_cameras[0]}")
else:
    print("\n❌ No cameras found!")
    print("\nTroubleshooting:")
    print("1. Check if camera is connected")
    print("2. Close apps using camera (Zoom, Teams, Skype, etc.)")
    print("3. Check Windows Privacy Settings:")
    print("   Settings → Privacy → Camera → Allow apps to access camera")
    print("4. Try external USB webcam if using laptop")
    print("5. Check Device Manager for camera driver issues")
