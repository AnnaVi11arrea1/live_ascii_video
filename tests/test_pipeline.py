"""
Test the video capture + ASCII conversion pipeline
"""
import time
import os
from video_capture import VideoCapture
from ascii_converter import AsciiConverter


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def test_ascii_video():
    """Test live ASCII video conversion."""
    print("ASCII Video Pipeline Test")
    print("=" * 50)
    print("Starting in 2 seconds...")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    converter = AsciiConverter(width=100, char_set="simple")
    
    try:
        with VideoCapture(device_id=0, fps_target=15) as cap:
            frame_count = 0
            start_time = time.time()
            
            while True:
                frame = cap.read_frame_throttled()
                
                if frame is None:
                    time.sleep(0.01)  # Small delay to avoid busy waiting
                    continue
                
                # Convert to ASCII
                ascii_art = converter.image_to_ascii(frame)
                
                # Clear screen and display
                clear_screen()
                print(ascii_art)
                
                # Show stats
                frame_count += 1
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"\nFPS: {fps:.1f} | Frames: {frame_count} | Press Ctrl+C to stop")
                
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    test_ascii_video()
