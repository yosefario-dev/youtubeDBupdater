import os
import subprocess
import time
import datetime
import time
import random

def type_p(text, avg_chars_per_second=30, random_delay=True):
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

def handle_error(error):
    error_message = str(error)
    subprocess.run(["python", "repair_tool.py -error", error_message])

def read_config(config_file='config.txt'):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split(' = ')
                config[key.strip()] = value.strip()
    return config

def clear_console():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

def main():
    config = read_config()
    change_file = config['change_file']
    check_interval = int(config['check_interval'])
    
    while True:
        try:
            log("Updating Channel List...")
            subprocess.run(["python", "build_rss.py"], check=True)
            
            log("Checking For New Videos...")
            subprocess.run(["python", "get_video_links.py"], check=True)
            
            with open(change_file, 'r') as cf:
                change_status = cf.read().strip()

            if "Changed" in change_status:
                log("New Videos Detected. Starting Downloading:")
                subprocess.run(["python", "download.py"], check=True)
            else:
                log("No New Videos Detected. Skipping download.")
            
            time.sleep(check_interval)
            clear_console()
        except Exception as e:
            log(f"Error occurred: {e}")
            handle_error(e)

if __name__ == "__main__":
    main()
