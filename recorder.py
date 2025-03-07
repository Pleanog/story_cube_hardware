import socket
import wave
import pyaudio
import os
import threading
from datetime import datetime

# Ensure the 'audio' directory exists
os.makedirs("audio", exist_ok=True)

# Constants for socket
SOCKET_ADDRESS = ('localhost', 65434)

# Set up PyAudio
p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Aufnahme-Status
is_recording = False
recording_thread = None  # Aufnahme-Thread
frames = []  # Hier werden die Audio-Daten zwischengespeichert


def record_audio():
    """Nimmt Audio auf, bis is_recording auf False gesetzt wird."""
    global frames
    frames = []
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while is_recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()


def save_audio():
    """Speichert die aufgenommene Audiodatei als WAV."""
    print("Versucht eine Audioaufnahme zu speichern.")
    if not frames:
        print("Keine Audiodaten zum Speichern.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio/recording_{timestamp}.wav"

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio gespeichert: {filename}")


def handle_signals():
    """Hört auf Start-/Stop-Signale und steuert die Aufnahme."""
    global is_recording, recording_thread

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(SOCKET_ADDRESS)
        s.listen(5)
        print("Recorder wartet auf Start/Stop-Signale...")

        while True:
            conn, addr = s.accept()
            with conn:
                message = conn.recv(1024).decode()
                print(f"Empfangenes Signal: {message}")

                if message == "start_recording":
                    if not is_recording:
                        print("Starte Aufnahme...")
                        is_recording = True
                        recording_thread = threading.Thread(target=record_audio)
                        recording_thread.start()

                elif message == "stop_recording_save":
                    if is_recording:
                        print("Stoppe Aufnahme und speichere Datei...")
                        is_recording = False
                        recording_thread.join()  # Warten, bis Thread beendet ist
                        save_audio()

                elif message == "stop_recording_discard":
                    if is_recording:
                        print("Stoppe Aufnahme und verwerfe Datei...")
                        is_recording = False
                        recording_thread.join()
                        print("Aufnahme verworfen.")


if __name__ == "__main__":
    handle_signals()
