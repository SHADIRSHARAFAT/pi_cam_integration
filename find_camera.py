import cv2

print("Scanning for cameras...")
for i in range(5): # Test ports 0 through 4
    # Try default backend first
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"SUCCESS: Camera found at index {i} (Default Backend)")
        cap.release()
    
    # Try DirectShow backend
    cap_dshow = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap_dshow.isOpened():
        ret, frame = cap_dshow.read()
        if ret:
            print(f"SUCCESS: Camera found at index {i} (DirectShow Backend)")
        cap_dshow.release()

print("Scan complete.")