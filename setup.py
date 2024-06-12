import subprocess
import time
import sys
import os

def install_libraries():
    required_libraries = ["pytube", "feedparser", "argparse"]
    missing_libraries = []
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            missing_libraries.append(library)

    if missing_libraries:
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_libraries, check=True)

def setup_channels_file():
    if not os.path.exists("channels.txt"):
        with open("channels.txt", "w") as file:
            file.write("# Add your YouTube channel links here, one per line\n")
            file.write("# Example:\n")
            file.write("# https://www.youtube.com/user/example_channel\n")

def print_application_info():
    print("YouTube Channel Updater Setup")
    print("=============================")
    print("The YouTube Channel Updater automates monitoring and downloading videos from specified YouTube channels.")
    print("This script will install necessary libraries and set up the channels.txt file.")
    print("\nFollow these instructions to complete the setup:")
    print("1. Libraries will be installed automatically.")
    print("2. Edit channels.txt later to add your YouTube channel links.")
    print("\nSetup completed successfully.")

def main():
    install_libraries()
    setup_channels_file()
    print_application_info()
    time.sleep(120)

    try:
        subprocess.run(["start", "channels.txt"], check=True, shell=True)
    except subprocess.CalledProcessError:
        pass

if __name__ == "__main__":
    main()
