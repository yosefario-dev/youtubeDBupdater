import os
import subprocess
import time
import datetime
def handle_error(error):
    error_message = str(error)
    subprocess.run(["python", "repair_tool.py -error", error_message])

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} > {message}")

def clear_console():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

def main():
    while True:
        try:
            log("Updating Channel List...")
            subprocess.run(["python", "build_rss.py"], check=True)
            
            log("Checking For New Videos...")
            subprocess.run(["python", "get_video_links.py"], check=True)
            
            with open("change.txt", 'r') as cf:
                change_status = cf.read().strip()

            if change_status == "changed":
                log("New Videos Detected. Starting Downloading:")
                subprocess.run(["python", "download.py"], check=True)
            else:
                log("No New Videos Detected. Skipping download.")
            log("Sleeping for 2 minutes...")
            time.sleep(120)
            clear_console()
        
        except Exception as e:
            log(f"Error occurred: {e}")
            handle_error(e)

if __name__ == "__main__":
    main()