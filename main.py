import time
import socket
import subprocess
import threading
import signal
import sys
import pyaudio
import wave
import os
import requests
from datetime import datetime
from led_control import set_led_color, led_shutdown
from audio_post_processor import process_audio
from audio_uploader import upload_audio
from data_cleaner import delete_old_uploaded_files, get_unuploaded_files

# Konfiguriere Aufnahmeparameter
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # 44.1 kHz ist Standard für Audio
CHUNK = 1024
audio_dir = "audio"
os.makedirs(audio_dir, exist_ok=True)

# Globale Variable für die Aufnahme
recording = False

def start_recording():
    global recording
    print("Aufnahme gestartet...")

    filename = os.path.join(audio_dir, f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

    # Starte die Aufnahme mit arecord
    process = subprocess.Popen(["arecord", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "16000", "-c", "1", filename])

    start_time = time.time()

    while recording:
        elapsed_time = int(time.time() - start_time)
        sys.stdout.write(f"\rRecording since {elapsed_time} sec...")  # Overwrite the same line
        sys.stdout.flush()  # Make sure it updates immediately
        time.sleep(1)

    # Beende die Aufnahme
    print("\nAufnahme beendet.")  # Move to the next line
    process.terminate()

    print(f"Datei gespeichert: {filename}")
    manage_audio_lifecycle(filename)

# Funktion zum Stoppen der Audioaufnahme
def stop_recording():
    global recording
    recording = False

def manage_audio_lifecycle(original_file):
    print(f"Verarbeite Audio-Datei: {original_file}")
    louderaudioasmp3 = process_audio(original_file)
    succes = upload_audio(louderaudioasmp3)
    if not succes:
        set_led_color("red", mode="blink", repeat=5, blink_interval=0.1)
        # set_led_color("red")
        # time.sleep(0.1)
        # set_led_color("white")
        # time.sleep(0.1)
        # set_led_color("red")
        # time.sleep(0.1)
        # set_led_color("white")
        # time.sleep(0.1)
        # set_led_color("red")
        # time.sleep(0.1)
        # set_led_color("white")
        # time.sleep(0.1)
        # set_led_color("red")
    else: 
        print("Audio-Verarbeitung abgeschlossen.")
        set_led_color("green", mode="static")
        time.sleep(1)
        set_led_color("white", mode="static")
        # set_led_color("white")

# Start the button handler as a separate process
button_handler_process = subprocess.Popen(["python3", "button_handler.py"])
gyro_handler_process = subprocess.Popen(["python3", "gyro_handler.py"])

SOCKET_ADDRESS_BUTTON = ('localhost', 65432)  # Socket for button press events
SOCKET_ADDRESS_GYRO = ('localhost', 65433)  # Socket for gyro events


# Knopf gedrückt -> Aufnahme starten
def on_button_pressed():
    global recording
    if not recording:
        recording = True
        # Startet die Audioaufnahme in einem neuen Thread
        recording_thread = threading.Thread(target=start_recording)
        recording_thread.start()

# Knopf losgelassen -> Aufnahme stoppen
def on_button_released():
    if recording:
        stop_recording()

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
                        on_button_pressed()  # Start recording
                        set_led_color("green", mode="static")
                    elif message == 'button_released':
                        on_button_released()  # Stop the recording and save
                        print("Button released in main program!")
                        set_led_color("green", mode="pulse", repeat=10)
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
                        print("\033[1;33mShake detected!\033[0m")
                        set_led_color("yellow", mode="fade",repeat=10)
                        time.sleep(3)
                        set_led_color("white", mode="static")
                    elif message.startswith("face:"):
                        print(f"Dice Face Up: \033[1;31m{message[5:]}\033[0m")
                        set_led_color("blue", mode="blink", repeat=2, blink_interval=0.1)

    except OSError as e:
        print(f"Socket bind failed: {e}")

def manage_old_audiofiles():
    delete_old_uploaded_files()
    unuploaded_files = get_unuploaded_files()
    for file in unuploaded_files:
        upload_audio(file)
        time.sleep(1)

# Function to handle cleanup when the program is interrupted
def cleanup_and_exit(signum, frame):
    print("Firmware interrupted. Cleaning up...")
    button_handler_process.terminate()
    gyro_handler_process.terminate()
    led_shutdown()
    sys.exit(0)

# def wait_for_internet():
#     # Define a timeout and check interval for better responsiveness
#     timeout = 5  # Retry interval in seconds
#     check_interval = 1  # How often to check for the connection (in seconds)

#     while True:
#         try:
#             # Try to connect to a reliable server (e.g., Google's DNS server)
#             socket.create_connection(("8.8.8.8", 53), timeout=timeout)  # Google's DNS server (port 53)
#             print("Internet connection detected.")
#             set_led_color("white", mode="static")
#             # set_led_color("white")
#             break  # Break out of the loop once connected
#         except (socket.timeout, socket.gaierror, ConnectionRefusedError):
#             print("No internet connection. Retrying in {} seconds...".format(check_interval))
#             set_led_color("orange-red", mode="static")
#             # set_led_color("orange-red")  # Set LEDs to white when connected
#             time.sleep(check_interval)  # Wait for a while before retrying

# Main function
def main():
    # wait_for_internet()

    manage_old_audiofiles_thread = threading.Thread(target=manage_old_audiofiles)
    manage_old_audiofiles_thread.start()
    # Set up signal handler for cleanup on Ctrl+C
    signal.signal(signal.SIGINT, cleanup_and_exit)

    # Start socket listeners in separate threads
    button_thread = threading.Thread(target=listen_for_button_data)
    gyro_thread = threading.Thread(target=listen_for_gyro_data)

    button_thread.daemon = True  # Daemonize thread so it exits when main program exits
    gyro_thread.daemon = True  # Daemonize thread so it exits when main program exits

    button_thread.start()
    gyro_thread.start()
    
    # Main program ca continue with other tasks
    while True:
        print('Firmware wating for inputs ...')  
        time.sleep(2)

if __name__ == "__main__":
    main()
