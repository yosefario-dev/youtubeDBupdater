import os
import datetime
from pytube import Channel, Playlist
import time
import random

def type_p(text, avg_chars_per_second=60, random_delay=True):
    delay = 1 / avg_chars_per_second
    for char in text:
        print(char, end='', flush=True)
        if random_delay:
            time.sleep(delay + random.uniform(-delay/2, delay/2))
        else:
            time.sleep(delay)
    print()
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    type_p(f"{timestamp} > {message}")

def read_config(config_file='config.txt'):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split(' = ')
                config[key.strip()] = value.strip()
    return config

def get_channel_info(channel_url):
    if channel_url.startswith('https://www.youtube.com/@'):
        channel_name = channel_url.split('/')[-1].replace('@', '')
        channel_url = f"https://www.youtube.com/c/{channel_name}"
    elif channel_url.startswith('https://www.youtube.com/c/'):
        channel_name = channel_url.split('/')[-1]
    elif channel_url.startswith('https://www.youtube.com/channel/'):
        channel_name = "Unknown Channel Name"
    else:
        log("Error: Invalid channel URL format.")
        return None, None

    try:
        channel = Channel(channel_url)
        channel_id = channel.channel_id
        channel_name = channel.channel_name
        return channel_id, channel_name
    except Exception as e:
        log(f"Error getting channel info: {e}")
        return None, None

def get_playlist_info(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        playlist_name = playlist.title
        return playlist_name, playlist_url
    except Exception as e:
        log(f"Error getting playlist info: {e}")
        return None, None

def build_rss():
    config = read_config()
    channels_file = config['channels_file']
    rss_file = config['rss_file']

    if not os.path.exists(channels_file):
        log("Error: channels.txt not found.")
        return

    if not os.path.exists(rss_file):
        open(rss_file, 'w').close()  # Create an empty rss.txt if it doesn't exist
        log("Created empty rss.txt file.")

    with open(channels_file, 'r') as f:
        channels = f.read().splitlines()

    with open(rss_file, 'r') as f:
        existing_lines = f.readlines()

    for channel_url in channels:
        if "youtube.com/playlist" in channel_url:
            playlist_name, playlist_url = get_playlist_info(channel_url)
            if playlist_name and playlist_url:
                line = f"{playlist_name} :: {playlist_url} ::: {playlist_url}\n"
                if line not in existing_lines:
                    with open(rss_file, 'a') as f:
                        f.write(line)
                    log(f"Added playlist {playlist_name}.")
                else:
                    log(f"Skipping playlist {playlist_name} - already exists.")
        else:
            channel_id, channel_name_api = get_channel_info(channel_url)
            if channel_id:
                rss_link = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                line = f"{channel_name_api} :: {channel_url} ::: {rss_link}\n"
                if line not in existing_lines:
                    with open(rss_file, 'a') as f:
                        f.write(line)
                    log(f"Added RSS feed for {channel_name_api}.")
                else:
                    log(f"Skipping {channel_name_api} - already exists.")

if __name__ == "__main__":
    try:
        build_rss()
    except Exception as e:
        log(f"Error occurred: {e}")
