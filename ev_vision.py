import cv2
import numpy as np
import threading
import time

# --- Configuration & Globals ---
latest_frame = None
detected_objects = []
lock = threading.Lock()
is_running = True

# Initialize OpenCV's built-in Pedestrian Detector (NO DOWNLOADS NEEDED!)
print("[INFO] Initializing built-in HOG Pedestrian Detector...")
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# --- 1. Object Detection Thread ---
def object_detection_worker():
    global latest_frame, detected_objects, is_running
    
    while is_running:
        with lock:
            frame_copy = latest_frame.copy() if latest_frame is not None else None
            
        if frame_copy is None:
            time.sleep(0.05)
            continue

        # Resize the frame to reduce CPU load (Crucial for EV speed)
        # We scale it down to 320x240 just for the AI to scan
        small_frame = cv2.resize(frame_copy, (320, 240))
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # Detect pedestrians
        boxes, weights = hog.detectMultiScale(gray, winStride=(8,8), scale=1.05)
        
        current_objects = []
        for (x, y, w, h) in boxes:
            # Because we scaled the image down by half to process it quickly, 
            # we multiply the bounding box coordinates by 2.0 to draw them correctly 
            # on the original 640x480 video feed.
            startX = int(x * 2.0)
            startY = int(y * 2.0)
            endX = int((x + w) * 2.0)
            endY = int((y + h) * 2.0)
            current_objects.append(("Pedestrian", startX, startY, endX, endY))

        with lock:
            detected_objects = current_objects
            
        time.sleep(0.1) 

# --- 2. Lane Detection Function ---
def process_lanes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Masking the top 50% of the screen (Horizon and sky)
    height, width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[(0, height), (width, height), (int(width*0.6), int(height*0.5)), (int(width*0.4), int(height*0.5))]])
    cv2.fillPoly(mask, polygon, 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=40, minLineLength=30, maxLineGap=20)
    
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
            
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)

# --- 3. Main Loop ---
def main():
    global latest_frame, is_running, detected_objects
    
    print("[INFO] Starting video stream...")
    # Using your laptop camera (Index 0) with DirectShow to prevent MSMF crashes
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    
    t = threading.Thread(target=object_detection_worker)
    t.start()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.resize(frame, (640, 480))
            
            with lock:
                latest_frame = frame
                
            processed_frame = process_lanes(frame)
            
            with lock:
                for obj in detected_objects:
                    label, startX, startY, endX, endY = obj
                    cv2.rectangle(processed_frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    cv2.putText(processed_frame, label, (startX, startY - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("EV Autonomous Vision - V2", processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        print("[INFO] Shutting down...")
        is_running = False
        t.join()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()