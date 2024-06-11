# YouTubeDBUpdater Setup Guide

## Overview:
The YouTubeDBUpdater application streamlines the process of monitoring and downloading videos from specified YouTube channels. It operates seamlessly in the background, periodically checking for new uploads and saving them locally for convenient access.

## Setup Steps:

### Installation:
1. Execute the provided setup script to ensure the application's prerequisites are met.
2. This script automatically installs required libraries and initializes the channels.txt file for channel listing.

### Acquiring a YouTube Data API Key:
1. Access the Google Cloud Console and create a new project.
2. In the "APIs & Services" section, navigate to "Credentials" and generate an API key.
3. Copy the generated API key for use with the YouTubeDBUpdater application.

### Securing the API Key (Optional):
1. During setup, you have the option to enhance security by encrypting the API key.
2. Encryption utilizes the Fernet symmetric encryption scheme, ensuring confidentiality.
3. If encryption is selected, the API key is encrypted with a user-provided password for added protection.

### Channel Listing:
1. Open the channels.txt file, which was automatically created during setup.
2. Here, list the YouTube channels you wish to monitor, with each channel link on a separate line.
3. Example of YoutTube channel URL: https://www.youtube.com/@Psych2go
If a channel doesn't have @ type URL, type a channel title (it will search for the title in the YouTube Database.).

### Executing the Application:
1. Launch the application by running the app.py script.
2. The application will commence its automated monitoring of the listed channels for new video uploads.
3. It operates discreetly in the background, seamlessly managing the download process without user intervention.

### Customization (Optional):
1. For advanced users, the application offers customization options.
2. Adjust resolution preferences for downloaded videos and fine-tune the frequency of checks for new uploads as needed.
3. These modifications can be made directly within the script to suit individual preferences.

## Conclusion:
The YouTubeDBUpdater application simplifies the task of staying up-to-date with your favorite YouTube content creators. By automating the monitoring and downloading process, it ensures timely access to new videos, enhancing user convenience and efficiency.
