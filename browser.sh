#!/bin/bash

# Update package list and install dependencies
echo "Updating package list..."
sudo apt update

echo "Installing Tor, Privoxy, Python, and curl..."
sudo apt install -y tor privoxy python3 curl

# Configure Privoxy to forward traffic to Tor's SOCKS5 proxy
echo "Configuring Privoxy..."
sudo sed -i "s|# forward-socks5 / 127.0.0.1:9050 .|forward-socks5 / 127.0.0.1:9050 .|" /etc/privoxy/config

# Start Tor and Privoxy services
echo "Starting Tor and Privoxy..."
sudo systemctl start tor
sudo systemctl start privoxy

# Enable Tor and Privoxy to start on boot
echo "Enabling Tor and Privoxy on boot..."
sudo systemctl enable tor
sudo systemctl enable privoxy

# Fetch external IP address using a public API (e.g., ipify or ifconfig.me)
echo "Fetching external IP address..."
EXTERNAL_IP=$(curl -s https://api.ipify.org)

# Create a basic HTML page for the proxy site with the external IP
echo "Creating proxy website..."
mkdir -p /home/$(whoami)/proxy_site
cat > /home/$(whoami)/proxy_site/index.html <<EOL
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Proxy Through Tor</title>
</head>
<body>
  <h1>Welcome to the Tor Proxy Site</h1>
  <p>Your proxy server's public IP: <strong>$EXTERNAL_IP</strong></p>
  <p>Enter a URL to browse through the Tor network:</p>
  <form action="/search" method="GET">
    <label for="url">Enter URL:</label><br>
    <input type="text" id="url" name="url" required><br><br>
    <input type="submit" value="Browse">
  </form>

  <!-- If a URL was provided, show the result below -->
  <div id="result">
    <!-- The search result will be displayed here -->
    <p id="searchResult"></p>
  </div>
</body>
</html>
EOL

# Start a Python HTTP server to serve the proxy site
echo "Starting web server..."
cd /home/$(whoami)/proxy_site
python3 -m http.server 8080 &

echo "Proxy website is available at http://$(hostname -I | awk '{print $1}'):8080"
