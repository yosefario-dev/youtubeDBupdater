import os
import feedparser
import requests
import argparse
import datetime
import subprocess
import sys

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def handle_error(error):
    error_message = str(error)
    try:
        subprocess.run([sys.executable, "repair_tool.py", "-error", error_message], check=True)
    except FileNotFoundError:
        log(f"Repair tool not found. Error: {error_message}")

def get_channel_title(cid, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={cid}&key={api_key}"
    response = requests.get(url).json()
    if 'error' in response:
        if response['error']['code'] == 403 and response['error']['errors'][0]['reason'] == 'quotaExceeded':
            raise ValueError("You have exceeded your YouTube Data API quota. Please try again later or use a different API key.")
        else:
            raise ValueError(f"API error: {response['error']['message']}")
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['snippet']['channelTitle']
    else:
        raise ValueError(f"No items found in the response for channel ID {cid}. Response: {response}")

def get_video_links_from_rss(api_key):
    rss_file = "rss.txt"
    change_detected = False

    if not os.path.exists(rss_file):
        log("Error: rss.txt not found.")
        return

    with open(rss_file, 'r') as f:
        rss_links = [line.split(' ::: ')[1] for line in f.read().splitlines()]

    for rss_link in rss_links:
        # Extract creator name from RSS link
        channel_id = rss_link.split('=')[-1].split('&')[0]
        try:
            creator_name = get_channel_title(channel_id, api_key)
        except ValueError as e:
            log(str(e))
            continue

        creator_folder = os.path.join("creators", creator_name)
        os.makedirs(creator_folder, exist_ok=True)

        # Parse RSS feed
        feed = feedparser.parse(rss_link)
        if 'entries' in feed:
            videos = feed['entries'][:10]  # Get the last 10 videos
            video_links = [entry['link'] for entry in videos]

            # Check for new video links
            video_links_file = os.path.join(creator_folder, f"{creator_name}.txt")
            existing_video_links = []

            if os.path.exists(video_links_file):
                with open(video_links_file, 'r') as f:
                    existing_video_links = f.read().splitlines()

            new_video_links = [link for link in video_links if link not in existing_video_links]

            if new_video_links:
                change_detected = True
                with open(video_links_file, 'a') as f:
                    for link in new_video_links:
                        f.write(f"{link}\n")

    with open("change.txt", 'w') as cf:
        cf.write("changed" if change_detected else "no change")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Get video links from RSS feeds.')
        parser.add_argument('-api', '--api_key', required=True, help='YouTube Data API Key')
        args = parser.parse_args()

        get_video_links_from_rss(args.api_key)
    except Exception as e:
        log(f"Error occurred: {e}")
        handle_error(e)
