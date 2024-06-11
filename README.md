YouTube Channel Updater Setup Guide
Overview:
The YouTube Channel Updater application streamlines the process of monitoring and downloading videos from specified YouTube channels. It operates seamlessly in the background, periodically checking for new uploads and saving them locally for convenient access.

Setup Steps:
Installation:

Execute the provided setup script to ensure the application's prerequisites are met.
This script automatically installs required libraries and initializes the channels.txt file for channel listing.
Acquiring a YouTube Data API Key:

Access the Google Cloud Console and create a new project.
In the "APIs & Services" section, navigate to "Credentials" and generate an API key.
Copy the generated API key for use with the YouTube Channel Updater application.
Securing the API Key (Optional):

During setup, you have the option to enhance security by encrypting the API key.
Encryption utilizes the Fernet symmetric encryption scheme, ensuring confidentiality.
If encryption is selected, the API key is encrypted with a user-provided password for added protection.
Channel Listing:

Open the channels.txt file, which was automatically created during setup.
Here, list the YouTube channels you wish to monitor, with each channel link on a separate line.
Executing the Application:

Launch the application by running the app.py script.
The application will commence its automated monitoring of the listed channels for new video uploads.
It operates discreetly in the background, seamlessly managing the download process without user intervention.
Customization (Optional):

For advanced users, the application offers customization options.
Adjust resolution preferences for downloaded videos and fine-tune the frequency of checks for new uploads as needed.
These modifications can be made directly within the script to suit individual preferences.
Conclusion:
The YouTube Channel Updater application simplifies the task of staying up-to-date with your favorite YouTube content creators. By automating the monitoring and downloading process, it ensures timely access to new videos, enhancing user convenience and efficiency.
