import os
import subprocess
import time
import datetime
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
def load_api_key():
    if os.path.exists("api.txt"):
        with open("api.txt", "r") as file:
            return file.read().strip()

    elif os.path.exists("api.encrypted"):
        attempts_left = 5
        while attempts_left > 0:
            password = get_password()
            api_key = decrypt_api_key(password)
            if api_key:
                return api_key
            else:
                log(f"Incorrect password. {attempts_left} attempts left.")
                attempts_left -= 1
        log("Maximum attempts reached. Deleting api.encrypted.")
        os.remove("api.encrypted")
        sys.exit()

    else:
        api_key = input("Enter your YouTube Data API Key: ").strip()
        time.sleep(1)
        while True:
            encrypt = input("Do you want to encrypt the API key? (yes/no): ").lower().strip()
            if encrypt in ["yes", "yup", "okay", "sure", "y"]:
                break
            elif encrypt in ["no", "nope", "nah", "not now", "n"]:
                break
            else:
                log("Invalid input. Please enter 'yes' or 'no' or their alternatives.")

        if encrypt in ["yes", "yup", "okay", "sure", "y"]:
            password = get_password()
            encrypt_api_key(api_key, password)
        else:
            with open("api.txt", "w") as file:
                file.write(api_key)
        return api_key
    
def get_password():
    while True:
        password = getpass.getpass("Enter your password: ")
        confirm_password = getpass.getpass("Confirm your password: ")
        if password == confirm_password:
            return password
        log("Passwords do not match. Please try again.")

def encrypt_api_key(api_key, password):
    key = derive_key(password)
    f = Fernet(key)
    encrypted_api_key = f.encrypt(api_key.encode())
    with open("api.encrypted", "wb") as file:
        file.write(encrypted_api_key)

def decrypt_api_key(password):
    key = derive_key(password)
    try:
        with open("api.encrypted", "rb") as file:
            encrypted_api_key = file.read()
        f = Fernet(key)
        api_key = f.decrypt(encrypted_api_key).decode()
        return api_key
    except Exception:
        return None

def derive_key(password):
    password = password.encode()
    salt = b'salt_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Encode the key to make it URL safe
    return key

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
    api_key = load_api_key()
    while True:
        try:
            log("Updating Channel List...")
            subprocess.run(["python", "build_rss.py", "-api", api_key], check=True)
            
            log("Checking For New Videos...")
            subprocess.run(["python", "get_video_links.py", "-api", api_key], check=True)
            
            with open("change.txt", 'r') as cf:
                change_status = cf.read().strip()

            if change_status == "changed":
                log("New Videos Detected. Starting Downloading:")
                subprocess.run(["python", "download.py"], check=True)
            else:
                log("No New Videos Detected. Skipping download.")
            log("Sleeping for 1 minute...")
            time.sleep(60)            
            clear_console()
        
        except Exception as e:
            log(f"Error occurred: {e}")
            handle_error(e)

if __name__ == "__main__":
    main()