import cv2
import time
import numpy as np

class QRScanner:
    def __init__(self):
        self.cap = None
        # Use OpenCV's QR code detector
        self.qr_detector = cv2.QRCodeDetector()
        
    def start_camera(self, camera_index=0):
        """Start the webcam capture."""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Could not open camera at index {camera_index}")
                
            # Set camera properties for better detection
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus if available
            
            return self.cap.isOpened()
        except Exception as e:
            print(f"Error starting camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Release the webcam."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
    def get_frame(self):
        """Capture a frame from the webcam."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def scan_qr_code(self, frame):
        """Scan for QR codes in the given frame."""
        if frame is None:
            return []
            
        results = []
        
        try:
            # First, try with standard QR code detector
            data, bbox, _ = self.qr_detector.detectAndDecode(frame)
            
            if data:
                results.append({'data': data, 'type': 'QR'})
                return results
                
            # If no QR code found, try with image processing to enhance detection
            processed_frame = self._preprocess_frame(frame)
            data, bbox, _ = self.qr_detector.detectAndDecode(processed_frame)
            
            if data:
                results.append({'data': data, 'type': 'QR'})
                
        except Exception as e:
            print(f"Error detecting QR code: {e}")
            
        return results
    
    def _preprocess_frame(self, frame):
        """Preprocess the frame to enhance QR code detection."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply slight Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding for better contrast
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up the image
            kernel = np.ones((3, 3), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
            
            return morph
        except Exception as e:
            print(f"Error preprocessing frame: {e}")
            return frame
    
    def scan_continuously(self, callback, stop_after_detection=True, timeout=30):
        """
        Continuously scan for QR codes until one is found or timeout.
        
        Args:
            callback: Function to call with QR code data when detected
            stop_after_detection: Whether to stop scanning after detecting a QR code
            timeout: Maximum time to scan in seconds
            
        Returns:
            The detected QR code data or None if timeout
        """
        if not self.cap or not self.cap.isOpened():
            self.start_camera()
            
        start_time = time.time()
        qr_data = None
        
        while time.time() - start_time < timeout:
            frame = self.get_frame()
            if frame is None:
                continue
                
            qr_codes = self.scan_qr_code(frame)
            
            if qr_codes:
                qr_data = qr_codes[0]['data']  # Take the first detected code
                callback(qr_data)
                if stop_after_detection:
                    break
                    
            # Small delay to not hog CPU
            time.sleep(0.1)
            
        return qr_data 