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

    if 'error' in data:
        if data['error']['code'] == 403 and data['error']['errors'][0]['reason'] == 'quotaExceeded':
            raise ValueError("You have exceeded your YouTube Data API quota. Please try again later or use a different API key.")
        else:
            raise ValueError(f"API error: {data['error']['message']}")

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
        log("Created empty rss.txt file.")

    with open(channels_file, 'r') as f:
        channels = f.read().splitlines()

    rss_table = {}
    with open(rss_file, 'r') as f:
        for line in f:
            youtube_url, rss_url = line.strip().split(' ::: ')
            rss_table[youtube_url] = rss_url

    for channel_url in channels:
        if channel_url in rss_table:
            log(f"RSS feed for @{channel_url.split('@')[-1]} already exists.")
        else:
            channel_title = channel_url.split('@')[-1]
            try:
                channel_id = get_channel_id(channel_title, api_key)
            except ValueError as e:
                log(str(e))
                continue

            if channel_id:
                rss_link = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                with open(rss_file, 'a') as f:
                    f.write(f"{channel_url} ::: {rss_link}\n")
                log(f"Added RSS feed for @{channel_title}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build RSS feeds for YouTube channels.")
    parser.add_argument("-api", "--api_key", type=str, required=True, help="YouTube API key")
    args = parser.parse_args()

    try:
        build_rss(args.api_key)
    except Exception as e:
        log(f"Error occurred: {e}")
