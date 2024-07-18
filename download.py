import os
import ctypes
import re
from pytube import YouTube
import yt_dlp as youtube_dl
import pytube
import datetime
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
def enable_virtual_terminal_processing():
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    mode.value |= 4
    kernel32.SetConsoleMode(handle, mode)
enable_virtual_terminal_processing()

def log(message, color='white', bg_color='black'):
    colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'bright_black': 90,
        'bright_red': 91,
        'bright_green': 92,
        'bright_yellow': 93,
        'bright_blue': 94,
        'bright_magenta': 95,
        'bright_cyan': 96,
        'bright_white': 97
    }
    bg_colors = {
        'black': 40,
        'red': 41,
        'green': 42,
        'yellow': 43,
        'blue': 44,
        'magenta': 45,
        'cyan': 46,
        'white': 47,
        'bright_black': 100,
        'bright_red': 101,
        'bright_green': 102,
        'bright_yellow': 103,
        'bright_blue': 104,
        'bright_magenta': 105,
        'bright_cyan': 106,
        'bright_white': 107
    }

    color_code = colors.get(color, 37)  # Default to white if color not found
    bg_color_code = bg_colors.get(bg_color, 40)  # Default to black if bg_color not found
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > \033[{color_code};{bg_color_code}m{message}\033[0m")

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

def download_video(video_link, download_folder, yt_title, max_retries, line, creator_name):
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
                    log(f"Downloading '{yt_title}'...    {formatted_filesize}", "blue")
                    stream.download(output_path=download_folder, filename=sanitized_title)
                    os.rename(os.path.join(download_folder, sanitized_title), video_file)  # Ensure proper extension
                    log(f"Download of '{yt_title}' completed.", "green", "white")
                else:
                    log(f"Video '{yt_title}' already exists in '{download_folder}'. Skipping download.")
            else:
                log(f"No suitable streams found for '{yt_title}'")
            return
        except pytube.exceptions.AgeRestrictedError:
            log(f"Error: Video '{yt_title}' is age restricted and cannot be downloaded.", "red")
            return
        except Exception as e:
            log(f"Error downloading '{yt_title}': {e}")
            retries += 1
            if retries < max_retries:
                log(f"Retrying '{yt_title}'... ({retries}/{max_retries})")
                time.sleep(5)  # Wait a bit before retrying
            else:
                log(f"Failed to download '{yt_title}' after {max_retries} attempts.", "red", "white")
                
                # Fallback to yt-dlp
                log(f"Attempting fallback download with yt-dlp for '{yt_title}'", "yellow")
                try:
                    download_video_with_yt_dlp(video_link, download_folder, max_retries)
                except Exception as e:
                    log(f"Fallback download failed for '{yt_title}': {e}", "red", "white")

                with open(os.path.join(download_folder, f"{creator_name}.txt"), 'r') as f:
                    lines = f.readlines()
                with open(os.path.join(download_folder, f"{creator_name}.txt"), 'w') as f:
                    for i, l in enumerate(lines):
                        if i != line - 1:
                            f.write(l)
                return

def download_video_with_yt_dlp(video_url, download_folder, max_retries=3):
    try:
        with youtube_dl.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_title = info_dict.get('title', 'video')
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return
    
    sanitized_title = sanitize_filename(video_title)
    output_template = os.path.join(download_folder, f'{sanitized_title}.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'retries': max_retries,
        'quiet': True,  # Suppress output
        'no_warnings': True  # Suppress warnings
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            log("Started fallback download with yt-dlp", "blue")
            ydl.download([video_url])
            log("Fallback download completed", "green", "white")
        except Exception as e:
            log(f"Error: {e}", "red")
def download_new_videos():
    config = read_config()
    creators_folder = config['creators_folder']
    downloads_folder = config['downloads_folder']
    change_file = config['change_file']
    max_retr = int(config["max_retries"])
    max_simultaneous_downloads = int(config['max_simultaneous_downloads'])

    if not os.path.exists(creators_folder):
        log("Error: creators folder not found.", "red")
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
            download_tasks.append((video_link, download_folder, yt.title, max_retr, len(download_tasks) + 1))

        with ThreadPoolExecutor(max_workers=max_simultaneous_downloads) as executor:
            futures = [executor.submit(download_video, *task, creator_name) for task in download_tasks]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log(f"An error occurred: {e}", "red", "white")

if __name__ == "__main__":
    download_new_videos()
