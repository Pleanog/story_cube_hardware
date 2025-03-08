import os
import time

AUDIO_DIR = "audio"

def delete_old_uploaded_files():
    """
    Deletes all .mp3 files in the /audio folder that are older than 3 days and have '-uploaded' in their name.
    Deletes all .wav files in the /audio folder that are older than 14 days
    """
    now = time.time()
    three_days_ago = now - (3 * 24 * 60 * 60)  # 3 days in seconds
    fourteen_days_ago = now - (14 * 24 * 60 * 60)  # 3 days in seconds
    if os.path.isdir(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(".mp3") and "-uploaded" in filename:
                file_path = os.path.join(AUDIO_DIR, filename)
                file_mtime = os.path.getmtime(file_path)  # Get last modified time
                if file_mtime < three_days_ago:
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
            if filename.endswith(".wav"):
                file_path = os.path.join(AUDIO_DIR, filename)
                file_mtime = os.path.getmtime(file_path)  # Get last modified time
                if file_mtime < fourteen_days_ago:
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
    else:
        print(f"The directory {AUDIO_DIR} does not exist, nothing to delete.")

def get_unuploaded_files():
    """
    Returns a list of .mp3 files in /audio that do not have '-uploaded' in their name.
    Prints the names of unuploaded files for debugging.
    """
    if os.path.isdir(AUDIO_DIR):
        unuploaded_files = []

        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(".mp3") and "-uploaded" not in filename:
                file_path = os.path.join(AUDIO_DIR, filename)
                unuploaded_files.append(file_path)

        for file in unuploaded_files:
            print(f"Unuploaded files: {file}")

        return unuploaded_files
    else:
        print(f"The directory {AUDIO_DIR} does not exist, nothing old, that is not uploaded.")
