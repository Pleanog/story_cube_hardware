import os
import requests
import shutil
import time

# Firebase Cloud Function URL (Replace with your actual URL)
CLOUD_FUNCTION_URL = "https://pxd-backend-225234343013.europe-west1.run.app/upload"

def upload_audio(file_path, max_retries=3, retry_delay=5):
    """
    Uploads an MP3 file to Firebase Cloud Function.
    Retries if the upload fails.
    
    :param file_path: Path to the audio file (relative or absolute)
    :param max_retries: Maximum number of retries in case of failure
    :param retry_delay: Delay in seconds before retrying
    :return: True if upload succeeds, False otherwise
    """

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return False

    for attempt in range(1, max_retries + 1):
        try:
            with open(file_path, "rb") as file:
                files = {"file": (os.path.basename(file_path), file, "audio/mp3")}
                response = requests.post(CLOUD_FUNCTION_URL, files=files)

            # Check if upload was successful (HTTP 200-299 range)
            if response.status_code >= 200 and response.status_code < 300:
                new_file_path = file_path.replace(".mp3", "-uploaded.mp3")
                os.rename(file_path, new_file_path)  # Rename the file after successful upload
                print(f"Upload successful! File renamed to {new_file_path}")
                return True
            else:
                print(f"Upload failed (Attempt {attempt}/{max_retries}): {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Network error (Attempt {attempt}/{max_retries}): {e}")

        # Wait before retrying
        if attempt < max_retries:
            time.sleep(retry_delay)

    print(f"Upload failed after {max_retries} attempts: {file_path}")
    return False
