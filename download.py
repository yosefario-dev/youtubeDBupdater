import os
import re
from pytube import YouTube
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def sanitize_filename(filename):
    invalid_chars = r'<>:"/\\|?*'
    sanitized_filename = re.sub(f'[{re.escape(invalid_chars)}]', '_', filename)
    return sanitized_filename

def download_new_videos():
    creators_folder = "creators"
    if not os.path.exists(creators_folder):
        log("Error: creators folder not found.")
        return

    with open("change.txt", 'r') as f:
        lines = f.read().splitlines()
        if lines[0] != "Changed":
            log("No changes detected. Skipping download.")
            return

        updated_creators = []
        for line in lines[2:]:
            if line.startswith("- "):
                updated_creators.append(line[2:])

    for creator_name in updated_creators:
        creator_folder = os.path.join(creators_folder, creator_name)
        if not os.path.isdir(creator_folder):
            continue

        download_folder = os.path.join("downloads", creator_name)
        os.makedirs(download_folder, exist_ok=True)

        video_links_file = os.path.join(creator_folder, f"{creator_name}.txt")
        if not os.path.exists(video_links_file):
            continue

        with open(video_links_file, 'r') as f:
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
    download_new_videos()