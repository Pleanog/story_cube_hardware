import time
import socket
import subprocess
import threading
import signal
import sys
from led_control import set_led_color


# Start the button handler as a separate process
button_handler_process = subprocess.Popen(["python3", "button_handler.py"])
gyro_handler_process = subprocess.Popen(["python3", "gyro_handler.py"])
recorder_process = subprocess.Popen(["python3", "recorder.py"])

SOCKET_ADDRESS_BUTTON = ('localhost', 65432)  # Socket for button press events
SOCKET_ADDRESS_GYRO = ('localhost', 65433)  # Socket for gyro events
SOCKET_ADDRESS_RECORDER = ('localhost', 65434)  # Socket for recorder events

recorderSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recorderSock.connect(SOCKET_ADDRESS_RECORDER)

def send_start_signal():
    print("Sending start signal to recorder...")
    recorderSock.sendall("button_released".encode())

def send_stop_signal(action="save"):
    print(f"Sending stop signal to recorder with action: {action}")
    if action == "save":
        recorderSock.sendall("stop_recording_save".encode())
    else:
        recorderSock.sendall("stop_recording_discard".encode())

def listen_for_button_data():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(SOCKET_ADDRESS_BUTTON)  # Bind the socket to the button address
            s.listen(1)  # Listen for one connection
            print("Main program waiting for button press...")

            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    print(f"Received Button Data: {message}")
                    if message == 'button_pressed':
                        print("Button pressed in main program!")
                        send_start_signal()  # Start recording
                        set_led_color("red")
                    elif message == 'button_released':
                        send_stop_signal(action="save")  # Save the recording
                        set_led_color("green")
                        print("Button released in main program!")
    except OSError as e:
        print(f"Socket bind failed: {e}")

def listen_for_gyro_data():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(SOCKET_ADDRESS_GYRO)  # Bind the socket to the gyro address
            s.listen(1)  # Listen for one connection
            print("Main program waiting for gyro events...")

            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    print(f"Received Gyro Data: {message}")
                    if message == "shake:1":
                        print("Shake detected!")
                        set_led_color("red")
                    elif message.startswith("face:"):
                        print(f"Dice Face Up: {message[5:]}")  # e.g. "Dice Face Up: 3"
                        set_led_color("blue")
    except OSError as e:
        print(f"Socket bind failed: {e}")

# Function to handle cleanup when the program is interrupted
def cleanup_and_exit(signum, frame):
    print("Program interrupted. Cleaning up...")
    set_led_color("off")  # Turn off the LEDs when exiting
    # Clean up subprocesses
    button_handler_process.terminate()
    gyro_handler_process.terminate()
    recorder_process.terminate()
    sys.exit(0)

def main():
    # Set up signal handler for cleanup on Ctrl+C
    signal.signal(signal.SIGINT, cleanup_and_exit)

    # Start socket listeners in separate threads
    button_thread = threading.Thread(target=listen_for_button_data)
    gyro_thread = threading.Thread(target=listen_for_gyro_data)

    button_thread.daemon = True  # Daemonize thread so it exits when main program exits
    gyro_thread.daemon = True  # Daemonize thread so it exits when main program exits

    button_thread.start()
    gyro_thread.start()

    # Main program logic (do other tasks while listening for button press and gyro events)
    while True:
        print('Doing something else...')  # Main program continues with other tasks
        time.sleep(1)  # Simulate doing other tasks (adjust timing as needed)

if __name__ == "__main__":
    main()
