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

# Konfiguriere Aufnahmeparameter
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # 44.1 kHz ist Standard für Audio
CHUNK = 1024
audio_dir = "audio"
os.makedirs(audio_dir, exist_ok=True)

# Globale Variable für die Aufnahme
recording = False

# Funktion zum Starten der Audioaufnahme
def start_recording():
    global recording
    print("Aufnahme gestartet...")

    filename = os.path.join(audio_dir, f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

    # PyAudio-Instanz erstellen
    p = pyaudio.PyAudio()

    # Passendes Mikrofon-Device suchen (optional)
    device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "USB" in info["name"]:  # Beispiel für USB-Mikrofon
            device_index = i
            break

    # Aufnahme starten
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)
    print("Aufnahme läuft...")
    frames = []
    try:
        while recording:
            data = stream.read(CHUNK, exception_on_overflow=False)  # Verhindert Overflow-Fehler
            frames.append(data)
    except Exception as e:
        print(f"Fehler während der Aufnahme: {e}")

    print("Aufnahme beendet.")

    # Stream und PyAudio schließen
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Datei speichern
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Datei gespeichert: {filename}")

# Funktion zum Stoppen der Audioaufnahme
def stop_recording():
    global recording
    recording = False

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
                        print("Shake detected!")
                        set_led_color("red")
                    elif message.startswith("face:"):
                        print(f"Dice Face Up: {message[5:]}")  # e.g. "Dice Face Up: 3"
                        set_led_color("blue")
    except OSError as e:
        print(f"Socket bind failed: {e}")

# Main function
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
