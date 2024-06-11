import os
import re
from pytube import YouTube
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def sanitize_filename(filename):
    # Define a pattern for invalid characters
    invalid_chars = r'<>:"/\\|?*'
    # Replace invalid characters with an underscore
    sanitized_filename = re.sub(f'[{re.escape(invalid_chars)}]', '_', filename)
    return sanitized_filename

def download_videos():
    creators_folder = "creators"
    if not os.path.exists(creators_folder):
        log("Error: creators folder not found.")
        return

    for creator_name in os.listdir(creators_folder):
        creator_folder = os.path.join(creators_folder, creator_name)
        if not os.path.isdir(creator_folder):
            continue

        download_folder = os.path.join("downloads", creator_name)
        os.makedirs(download_folder, exist_ok=True)

        for txt_file in os.listdir(creator_folder):
            if not txt_file.endswith(".txt"):
                continue

            with open(os.path.join(creator_folder, txt_file), 'r') as f:
                video_links = f.read().splitlines()

            for video_link in video_links:
                yt = YouTube(video_link)
                sanitized_title = sanitize_filename(yt.title)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    video_file = os.path.join(download_folder, f"{sanitized_title}.mp4")
                    if not os.path.exists(video_file):
                        log(f"Downloading '{yt.title}'...")
                        stream.download(output_path=download_folder, filename=sanitized_title)
                        os.rename(os.path.join(download_folder, sanitized_title), video_file)  # Ensure proper extension
                        log(f"Download of '{yt.title}' completed.")
                    else:
                        log(f"Video '{yt.title}' already exists in '{download_folder}'. Skipping download.")
                else:
                    log(f"No suitable streams found for '{yt.title}'")

if __name__ == "__main__":
    download_videos()
