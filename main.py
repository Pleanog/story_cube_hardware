import time
import socket
import subprocess
import threading
import signal
import sys
import pyaudio
import wave
import os
from datetime import datetime
from led_control import set_led_color
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
    upload_audio(louderaudioasmp3)
    print("Audio-Verarbeitung abgeschlossen.")

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

# Function to handle cleanup when the program is interrupted
def cleanup_and_exit(signum, frame):
    print("Program interrupted. Cleaning up...")
    set_led_color("off")  # Turn off the LEDs when exiting
    # Clean up subprocesses
    button_handler_process.terminate()
    gyro_handler_process.terminate()
    sys.exit(0)

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
                        set_led_color("red")
                    elif message == 'button_released':
                        on_button_released()  # Stop the recording and save
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
                        print("\033[1;33mShake detected!\033[0m")
                        set_led_color("red")
                    elif message.startswith("face:"):
                        print(f"Dice Face Up: \033[1;31m{message[5:]}\033[0m")
                        set_led_color("blue")
    except OSError as e:
        print(f"Socket bind failed: {e}")


def manage_old_audiofiles():
    delete_old_uploaded_files()
    unuploaded_files = get_unuploaded_files()
    for file in unuploaded_files:
        upload_audio(file)
        time.sleep(2)

# Main function
def main():
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

    
    # Main program logic (do other tasks while listening for button press and gyro events)
    while True:
        print('Doing something else...')  # Main program continues with other tasks
        time.sleep(1)  # Simulate doing other tasks (adjust timing as needed)

if __name__ == "__main__":
    main()
