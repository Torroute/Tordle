import os
import subprocess
import sys
import requests

# List of required dependencies
REQUIRED_DEPENDENCIES = [
    "requests", "aiohttp", "scapy", "socks", "bcrypt", "stem"
]

# Function to check if a package is installed
def check_and_install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", package])
        print(f"{package} is already installed.")
    except subprocess.CalledProcessError:
        print(f"{package} is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check if all required dependencies are installed
def install_requirements():
    for package in REQUIRED_DEPENDENCIES:
        check_and_install(package)

# Function to download the main script from GitHub
def download_script():
    url = "https://raw.githubusercontent.com/Torroute/Tordle/refs/heads/main/Tordlev2.py"
    script_filename = "Tordlev2.py"
    
    print(f"Downloading the script from {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(script_filename, "wb") as file:
            file.write(response.content)
        print(f"Script downloaded successfully as {script_filename}.")
    else:
        print(f"Failed to download the script. HTTP status code: {response.status_code}")
        sys.exit(1)

# Function to execute the downloaded script
def run_script():
    script_filename = "Tordlev2.py"
    
    if os.path.exists(script_filename):
        print(f"Running the downloaded script: {script_filename}")
        subprocess.check_call([sys.executable, script_filename])
    else:
        print(f"Error: {script_filename} not found.")
        sys.exit(1)

# Main function to check dependencies, download, and run the script
def main():
    print("Checking for required dependencies...")
    install_requirements()  # Install any missing dependencies
    
    download_script()  # Download the main script from GitHub
    run_script()  # Run the downloaded script

if __name__ == "__main__":
    main()
