import os
import feedparser
import datetime
from pytube import Playlist
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def read_config(config_file='config.txt'):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split(' = ')
                config[key.strip()] = value.strip()
    return config
def get_playlist_links(link):
    playlist = Playlist(link)
    video_urls = [video.watch_url for video in playlist.videos]
    return video_urls
def get_channel_title_from_rss(rss_link):
    config = read_config()
    rss_file = config['rss_file']
    
    with open(rss_file, 'r') as f:
        for line in f.read().splitlines():
            parts = line.split(' ::: ')
            if len(parts) != 2:
                log(f"Error: Invalid line format in {rss_file}: {line}")
                continue
            channel_info, rss_url = parts
            channel_name, _ = channel_info.split(' :: ')
            if rss_url == rss_link:
                return channel_name
    return None
def get_playlist_title(playlist_link):
    config = read_config()
    rss_file = config['rss_file']
    
    with open(rss_file, 'r') as f:
        for line in f.read().splitlines():
            parts = line.split(' ::: ')
            if len(parts) != 2:
                log(f"Error: Invalid line format in {rss_file}: {line}")
                continue
            channel_info, rss_url = parts
            channel_name, _ = channel_info.split(' :: ')
            if rss_url == playlist_link:
                return channel_name
    return None

def get_video_links_from_rss():
    config = read_config()
    rss_file = config['rss_file']
    change_file = config['change_file']
    creators_folder = config['creators_folder']
    num_videos_from_rss = int(config['num_videos_from_rss'])
    
    change_detected = False
    updated_creators = []

    if not os.path.exists(rss_file):
        log("Error: rss.txt not found.")
        return

    with open(rss_file, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        parts = line.split(' ::: ')
        if len(parts) != 2:
            log(f"Error: Invalid line format in {rss_file}: {line}")
            continue
        channel_info, rss_link = parts
        channel_name, _ = channel_info.split(' :: ')

        creator_folder = os.path.join(creators_folder, channel_name)
        if not os.path.exists(creator_folder):
            os.makedirs(creator_folder, exist_ok=True)
        else:
            change_detected = True
        video_links_file = os.path.join(creator_folder, f"{channel_name}.txt")
        if not os.path.exists(video_links_file):
            change_detected = True

        if "/playlist" in line:
            video_links = get_playlist_links(rss_link)
        else:
            feed = feedparser.parse(rss_link)
            if 'entries' in feed:
                videos = feed['entries'][:num_videos_from_rss]
                video_links = [entry['link'] for entry in videos]

        existing_video_links = []
        if os.path.exists(video_links_file):
            with open(video_links_file, 'r') as f:
                existing_video_links = f.read().splitlines()

        with open(video_links_file, 'w') as f:
            for link in video_links:
                f.write(f"{link}\n")

        if set(video_links) != set(existing_video_links):
            change_detected = True
            updated_creators.append(channel_name)
            log(f"Change detected for {channel_name}!")

    with open(change_file, 'w') as cf:
        if updated_creators:
            if change_detected:
                cf.write("Changed\n")
                cf.write("Updated Creators:\n")
                for creator in updated_creators:
                    cf.write(f"- {creator}\n")
        else:
            cf.write("No change")

if __name__ == "__main__":
    try:
        get_video_links_from_rss()
    except Exception as e:
        log(f"Error occurred: {e}")
