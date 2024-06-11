import os
from pytube import YouTube
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

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
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    video_file = os.path.join(download_folder, f"{yt.title}.mp4")
                    if not os.path.exists(video_file):
                        log(f"Downloading '{yt.title}'...")
                        stream.download(output_path=download_folder, filename=yt.title)
                        os.rename(os.path.join(download_folder, f"{yt.title}"), video_file)  # Ensure proper extension
                        log(f"Download of '{yt.title}' completed.")
                    else:
                        log(f"Video '{yt.title}' already exists in '{download_folder}'. Skipping download.")
                else:
                    log(f"No suitable streams found for '{yt.title}'")

if __name__ == "__main__":
    download_videos()