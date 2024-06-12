import os
import feedparser
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def get_channel_title_from_rss(rss_link):
    with open("rss.txt", 'r') as f:
        for line in f.read().splitlines():
            parts = line.split(' ::: ')
            if len(parts) < 3:
                log(f"Error: Invalid line format in rss.txt: {line}")
                continue
            _, channel_name, rss_url = parts
            if rss_url == rss_link:
                return channel_name
    return None
def get_video_links_from_rss():
    rss_file = "rss.txt"
    change_detected = False
    updated_creators = []
    updated_videos = []

    if not os.path.exists(rss_file):
        log("Error: rss.txt not found.")
        return

    with open(rss_file, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        channel_name, rss_link = line.split(' ::: ')
        creator, _ = channel_name.split(' :: ')

        creator_folder = os.path.join("creators", creator)
        os.makedirs(creator_folder, exist_ok=True)

        feed = feedparser.parse(rss_link)
        if 'entries' in feed:
            videos = feed['entries'][:10]
            video_links = [entry['link'] for entry in videos]

            video_links_file = os.path.join(creator_folder, f"{creator}.txt")
            existing_video_links = []

            if os.path.exists(video_links_file):
                with open(video_links_file, 'r') as f:
                    existing_video_links = f.read().splitlines()

            new_video_links = [link for link in video_links if link not in existing_video_links]

            if new_video_links:
                change_detected = True
                updated_creators.append(creator)
                updated_videos.extend(new_video_links)
                with open(video_links_file, 'a') as f:
                    for link in new_video_links:
                        f.write(f"{link}\n")

    with open("change.txt", 'w') as cf:
        if change_detected:
            cf.write("Changed\n")
            cf.write("Updated Creators:\n")
            for creator in updated_creators:
                cf.write(f"- {creator}\n")
            cf.write("Updated Videos:\n")
            for video in updated_videos:
                cf.write(f"- {video}\n")
        else:
            cf.write("No change")

if __name__ == "__main__":
    try:
        get_video_links_from_rss()
    except Exception as e:
        log(f"Error occurred: {e}")