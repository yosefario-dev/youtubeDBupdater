import os
import feedparser
import requests
import argparse
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def get_channel_title(cid, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={cid}&key={api_key}"
    d = requests.get(url).json()
    return d['items'][0]['snippet']['channelTitle']

def get_video_links_from_rss(api_key):
    rss_file = "rss.txt"
    change_detected = False

    if not os.path.exists(rss_file):
        log("Error: rss.txt not found.")
        return

    with open(rss_file, 'r') as f:
        rss_links = f.read().splitlines()

    for rss_link in rss_links:
        creator_id = rss_link.split('=')[-1]
        creator_name = get_channel_title(creator_id, api_key)
        creator_folder = os.path.join("creators", creator_name)
        os.makedirs(creator_folder, exist_ok=True)

        feed = feedparser.parse(rss_link)
        if 'entries' in feed:
            videos = feed['entries'][:10]
            video_links = [entry['link'] for entry in videos]

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
    parser = argparse.ArgumentParser(description="Get video links from RSS feeds for YouTube channels.")
    parser.add_argument("-api", "--api_key", type=str, required=True, help="YouTube API key")
    args = parser.parse_args()
    
    get_video_links_from_rss(args.api_key)