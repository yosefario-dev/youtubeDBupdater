import os
import datetime
from pytube import Channel

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def get_info(channel_url):
    if channel_url.startswith('https://www.youtube.com/@'):
        channel_name = channel_url.split('/')[-1].replace('@', '')
        channel_url = f"https://www.youtube.com/c/{channel_name}"
    elif channel_url.startswith('https://www.youtube.com/c/'):
        channel_name = channel_url.split('/')[-1]
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

def build_rss():
    channels_file = "channels.txt"
    rss_file = "rss.txt"

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
        try:
            channel_id, channel_name_api = get_info(channel_url)
        except Exception as e:
            log(f"Error getting channel info: {e}")
            continue

        if channel_id:
            rss_link = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            line = f"{channel_name_api} :: {channel_url} ::: {rss_link}\n"
            if line not in existing_lines:
                with open(rss_file, 'a') as f:
                    f.write(line)
                log(f"Added RSS feed for {channel_name_api}.")
            else:
                log(f"Skipping {channel_name_api} - already exists in rss.txt")

if __name__ == "__main__":
    try:
        build_rss()
    except Exception as e:
        log(f"Error occurred: {e}")