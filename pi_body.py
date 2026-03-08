import socket
import cv2
import struct
import time

# --- Configuration ---
# CRITICAL: Change this to your laptop's actual Wi-Fi IPv4 address!
LAPTOP_IP = ' 172.17.208.117'
PORT = 5000

def main():
    # 1. Connect to the Laptop Brain
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[INFO] Attempting to connect to Brain at {LAPTOP_IP}...")
    
    try:
        client_socket.connect((LAPTOP_IP, PORT))
        print("[SUCCESS] Connected to Brain!")
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")
        return

    # 2. Initialize the Camera
    # Use 0 for built-in/first USB, might need to be 1 or 2 depending on the Pi's USB mapping
    cap = cv2.VideoCapture(0)
    print("[INFO] Camera warmed up. Streaming video to Brain...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 3. Compress the image for fast Wi-Fi transfer
            # Shrinking it to 320x240 is the secret to zero-lag streaming
            small_frame = cv2.resize(frame, (320, 240))
            _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            # 4. Send size, then the image
            image_data = buffer.tobytes()
            client_socket.sendall(struct.pack(">I", len(image_data)) + image_data)
            
            # 5. Receive the driving command from the laptop
            # (We use a short timeout so the Pi doesn't freeze if the network blips)
            client_socket.settimeout(0.5) 
            try:
                command = client_socket.recv(1024).decode('utf-8')
                print(f"[COMMAND RECEIVED] -> {command}")
                # Future code: This is where you tell your motor controller what to do!
                
            except socket.timeout:
                print("[WARNING] Connection lag! Applying brakes for safety.")

    finally:
        print("[INFO] Shutting down Body...")
        cap.release()
        client_socket.close()

if __name__ == "__main__":
    main()