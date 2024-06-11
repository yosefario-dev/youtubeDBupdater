import argparse
import os
import requests
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def get_channel_id(channel_title, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q={channel_title}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data and data['items']:
        item = data['items'][0]
        if 'id' in item and 'channelId' in item['id']:
            return item['id']['channelId']
    log("Error: Channel ID not found.")
    return None

def build_rss(api_key):
    channels_file = "channels.txt"
    rss_file = "rss.txt"
    
    if not os.path.exists(channels_file):
        log("Error: channels.txt not found.")
        return
    
    if not os.path.exists(rss_file):
        open(rss_file, 'w').close()  # Create an empty rss.txt if it doesn't exist
    
    with open(channels_file, 'r') as f:
        channels = f.read().splitlines()
    
    existing_rss = set()
    with open(rss_file, 'r') as f:
        existing_rss = set(f.read().splitlines())
    
    new_rss = set()
    for channel_url in channels:
        channel_title = channel_url.split('@')[-1]
        channel_id = get_channel_id(channel_title, api_key)
        if channel_id:
            rss_link = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            if rss_link not in existing_rss:
                new_rss.add(rss_link)
    
    if new_rss:
        with open(rss_file, 'a') as f:
            for rss_link in new_rss:
                f.write(rss_link + '\n')
        log("RSS feeds updated.")
    else:
        log("No new RSS feeds to add.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build RSS feeds for YouTube channels.")
    parser.add_argument("-api", "--api_key", type=str, required=True, help="YouTube API key")
    args = parser.parse_args()
    
    build_rss(args.api_key)
