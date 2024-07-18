import argparse
import os
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def repair(error_message):
    if "API key not found" in error_message:
        print("API key not found error detected. Trying to repair...")
        create_api_key()
        print("API key file created successfully.")
    elif "API key invalid" in error_message:
        print("Invalid API key error detected. Trying to repair...")
        print("Please update the API key manually.")
    elif "RSS file not found" in error_message:
        print("RSS file not found error detected. Trying to repair...")
        create_rss_file()
        print("RSS file created successfully.")
    else:
        print("Unknown error detected. No repair actions available.")

def create_api_key():
    api_key = input("Enter your YouTube Data API Key: ").strip()
    while True:
        encrypt = input("Do you want to encrypt the API key? (yes/no): ").lower().strip()
        if encrypt in ["yes", "yup", "okay", "sure", "y"]:
            password = get_password()
            encrypt_api_key(api_key, password)
            break
        elif encrypt in ["no", "nope", "nah", "not now", "n"]:
            with open("api.txt", "w") as file:
                file.write(api_key)
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no' or their alternatives.")

def get_password():
    while True:
        password = getpass.getpass("Enter your password: ")
        confirm_password = getpass.getpass("Confirm your password: ")
        if password == confirm_password:
            return password
        print("Passwords do not match. Please try again.")

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

def create_rss_file():
    with open("rss.txt", "w") as file:
        file.write("# Add your RSS feed links here")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair Tool")
    parser.add_argument("-error", "--error", type=str, required=True, help="Error Message")
    args = parser.parse_args()
    error_message = args.error
    repair(error_message)
