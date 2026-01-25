"""
Video Capture - Webcam capture wrapper using OpenCV
"""
import cv2
import time


class VideoCapture:
    """Manages webcam capture."""
    
    def __init__(self, device_id=0, fps_target=15):
        """
        Initialize video capture.
        
        Args:
            device_id: Camera device ID (0 for default camera)
            fps_target: Target frames per second
        """
        self.device_id = device_id
        self.fps_target = fps_target
        self.frame_delay = 1.0 / fps_target
        self.cap = None
        self.is_open = False
        self.last_frame_time = 0
        
    def open(self):
        """Open the video capture device."""
        # Try DirectShow backend on Windows for better compatibility
        import platform
        if platform.system() == 'Windows':
            self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(self.device_id)
        
        if not self.cap.isOpened():
            # Try without backend specification
            self.cap = cv2.VideoCapture(self.device_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera device {self.device_id}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
        
        self.is_open = True
        
        # Warm up camera - capture a few frames
        for _ in range(5):
            self.cap.read()
        
        return True
    
    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
            numpy array (BGR format) or None if failed
        """
        if not self.is_open:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        return frame
    
    def read_frame_throttled(self):
        """
        Read a frame respecting the FPS target.
        Returns None if not enough time has passed since last frame.
        
        Returns:
            numpy array (BGR format) or None
        """
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        if elapsed < self.frame_delay:
            return None
        
        frame = self.read_frame()
        if frame is not None:
            self.last_frame_time = current_time
        
        return frame
    
    def close(self):
        """Release the video capture device."""
        if self.cap is not None:
            self.cap.release()
            self.is_open = False
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test video capture
    print("Testing Video Capture...")
    print("Press 'q' to quit\n")
    
    try:
        with VideoCapture(device_id=0, fps_target=15) as cap:
            print("Camera opened successfully!")
            print("Capturing frames... (this will show in a CV2 window)")
            
            frame_count = 0
            start_time = time.time()
            
            while True:
                frame = cap.read_frame()
                
                if frame is None:
                    print("Failed to read frame")
                    break
                
                frame_count += 1
                
                # Show frame in window
                cv2.imshow('Video Capture Test', frame)
                
                # Calculate FPS
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"FPS: {fps:.2f}")
                
                # Break on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyAllWindows()
            print(f"\nTotal frames captured: {frame_count}")
            
    except Exception as e:
        print(f"Error: {e}")
