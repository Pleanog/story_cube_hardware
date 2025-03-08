import os
from pydub import AudioSegment

def process_audio(original_file):
    """Erhöht die Lautstärke einer WAV-Datei und speichert sie als MP3."""
    
    # Prüfen, ob die Datei existiert
    if not os.path.exists(original_file):
        print(f"Fehler: Datei '{original_file}' nicht gefunden.")
        return

    # Generiere Namen für die neuen Dateien
    file_base = os.path.splitext(original_file)[0]  # Entfernt .wav
    backup_file = f"{file_base}_original.wav"
    output_mp3 = f"{file_base}.mp3"

    # Original umbenennen
    os.rename(original_file, backup_file)
    print(f"Original umbenannt in: {backup_file}")

    # WAV-Datei laden
    audio = AudioSegment.from_wav(backup_file)

    # Lautstärke um 40 dB erhöhen
    louder_audio = audio + 40

    # Als MP3 speichern
    louder_audio.export(output_mp3, format="mp3")
    print(f"Lautere Datei gespeichert als: {output_mp3}")

    return output_mp3  # Gibt den neuen Dateinamen zurück
