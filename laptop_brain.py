import socket
import cv2
import numpy as np
import struct

# --- Configuration ---
# 0.0.0.0 means "Listen on all available network interfaces (Wi-Fi)"
HOST = '0.0.0.0'  
PORT = 5000

def main():
    # 1. Setup the Network Server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[INFO] Laptop Brain is listening on port {PORT}...")
    print("[INFO] Waiting for the Raspberry Pi to connect...")
    
    conn, addr = server_socket.accept()
    print(f"[SUCCESS] Connected to Pi at {addr}!")

    data = b""
    # ">I" enforces a standard 4-byte size so Windows and Linux don't get confused
    payload_size = struct.calcsize(">I") 

    try:
        while True:
            # 2. Receive the size of the incoming video frame
            while len(data) < payload_size:
                data += conn.recv(4096)
                
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">I", packed_msg_size)[0]

            # 3. Receive the actual image data
            while len(data) < msg_size:
                data += conn.recv(4096)
                
            frame_data = data[:msg_size]
            data = data[msg_size:]

            # 4. Decode and Display the Frame
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow("EV Autonomous - Cloud Brain View", frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 5. THE AI DECISION (Dummy logic for now)
            # In the future, your Lane Detection code goes here!
            command = "STEER: LEFT, THROTTLE: 0.5"
            
            # Send the command back to the Pi instantly
            conn.sendall(command.encode('utf-8'))

    finally:
        print("[INFO] Shutting down Brain...")
        conn.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()