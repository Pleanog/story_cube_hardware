import pyaudio
import wave
import os
from datetime import datetime

# Konfiguriere Aufnahmeparameter
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # 44.1 kHz ist Standard für Audio
CHUNK = 1024
RECORD_SECONDS = 10

# Speicherort für die Aufnahme
audio_dir = "audio"
os.makedirs(audio_dir, exist_ok=True)
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
                input_device_index=device_index,  # Falls None, nimmt er das Standardgerät
                frames_per_buffer=CHUNK)

print("Aufnahme läuft...")

frames = []
try:
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
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
