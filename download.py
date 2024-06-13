import os
import re
from pytube import YouTube
import pytube
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def sanitize_filename(filename):
    invalid_chars = r'<>:"/\\|?*'
    sanitized_filename = re.sub(f'[{re.escape(invalid_chars)}]', '_', filename)
    return sanitized_filename

def read_config(config_file='config.txt'):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split(' = ')
                config[key.strip()] = value.strip()
    return config

def format_filesize(filesize):
    if filesize >= 1_000_000_000:
        return f"{filesize / 1_000_000_000:.2f} GB"
    elif filesize >= 1_000_000:
        return f"{filesize / 1_000_000:.2f} MB"
    else:
        return f"{filesize / 1_000:.2f} KB"

def download_video(video_link, download_folder, yt_title, max_retries):
    retries = 0
    while retries < max_retries:
        try:
            yt = YouTube(video_link)
            sanitized_title = sanitize_filename(yt_title)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if stream:
                video_file = os.path.join(download_folder, f"{sanitized_title}.mp4")
                if not os.path.exists(video_file):
                    filesize = stream.filesize
                    formatted_filesize = format_filesize(filesize)
                    log(f"Downloading '{yt_title}'...    {formatted_filesize}")
                    stream.download(output_path=download_folder, filename=sanitized_title)
                    os.rename(os.path.join(download_folder, sanitized_title), video_file)  # Ensure proper extension
                    log(f"Download of '{yt_title}' completed.")
                else:
                    log(f"Video '{yt_title}' already exists in '{download_folder}'. Skipping download.")
            else:
                log(f"No suitable streams found for '{yt_title}'")
            return
        except pytube.exceptions.AgeRestrictedError:
            log(f"Error: Video '{yt_title}' is age restricted and cannot be downloaded.")
            return
        except Exception as e:
            log(f"Error downloading '{yt_title}': {e}")
            retries += 1
            if retries < max_retries:
                log(f"Retrying '{yt_title}'... ({retries}/{max_retries})")
                time.sleep(5)  # Wait a bit before retrying
            else:
                log(f"Failed to download '{yt_title}' after {max_retries} attempts.")
                return

def download_new_videos():
    config = read_config()
    creators_folder = config['creators_folder']
    downloads_folder = config['downloads_folder']
    change_file = config['change_file']
    max_retr = int(config["max_retries"])
    max_simultaneous_downloads = int(config['max_simultaneous_downloads'])

    if not os.path.exists(creators_folder):
        log("Error: creators folder not found.")
        return

    with open(change_file, 'r') as f:
        lines = f.read().splitlines()
        if lines[0] != "Changed":
            log("No changes detected. Skipping download.")
            return

        updated_creators = []
        for line in lines[2:]:
            if line.startswith("- "):
                updated_creators.append(line[2:])

    download_tasks = []

    for creator_name in updated_creators:
        creator_folder = os.path.join(creators_folder, creator_name)
        if not os.path.isdir(creator_folder):
            continue

        download_folder = os.path.join(downloads_folder, creator_name)
        os.makedirs(download_folder, exist_ok=True)

        video_links_file = os.path.join(creator_folder, f"{creator_name}.txt")
        if not os.path.exists(video_links_file):
            continue

        with open(video_links_file, 'r') as f:
            video_links = f.read().splitlines()

        for video_link in video_links:
            yt = YouTube(video_link)
            download_tasks.append((video_link, download_folder, yt.title, max_retr))

    with ThreadPoolExecutor(max_workers=max_simultaneous_downloads) as executor:
        futures = [executor.submit(download_video, *task) for task in download_tasks]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log(f"An error occurred: {e}")

if __name__ == "__main__":
    download_new_videos()
