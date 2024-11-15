TORDLE

Automatic Setup Script:
The script is hosted on GitHub 
and can be downloaded directly from 
the GitHub URL using either wget or curl.
Upon download, it checks for necessary 
dependencies, installs missing ones, 
and then executes the core script
(Tordlev2.py).
link below


wget -q https://raw.githubusercontent.com/Torroute/Tordle/refs/heads/main/Setup.py -O Setup.py && python3 Setup.py


Functionality:
The main script (once downloaded and run) handles actions such as packet sending, proxy usage, .onion routing, and Tor integration.
It features login functionality, 
user management, and the ability 
to send packets through different 
channels, including SOCKS proxies,
DNS, and Tor hidden services (.onion).
The script also supports real-time 
changes to the route 
(e.g., switching .onion domains, proxies, and DNS IPs while running).
Automatic Script Download and Execution:
You can quickly download and execute 
this script using the provided command.
The automatic setup script will ensure 
that the environment is ready
(by installing missing dependencies)
and immediately runs the core tool.
(refer to link above)



Manual Setup Instructions:
To manually set up the environment and run the script, follow these steps:

Step 1: Install Python and Dependencies

Ensure Python 3 is installed on your system:
python3 --version
Install the required Python packages manually. Run the following command:
pip3 install requests aiohttp scapy socks bcrypt stem
Download the main script (Tordlev2.py) using wget or curl:

wget https://raw.githubusercontent.com/Torroute/Tordle/refs/heads/main/Tordlev2.py -O Tordlev2.py
Step 2: Run the Script

Once the script is downloaded, execute it with:

python3 Tordlev2.py




How to Use the System:
After Downloading and Running the Script

Login: After running the script, 
you’ll be prompted to log in 
using a username and password.
Main Menu: Once logged in, you’ll be presented with a menu to:
Send UDP/TCP packets.
Initiate a Tordle attack (through Tor).
Access the admin panel to manage users.
Monitoring: The script will provide real-time feedback, showing which .onion domains, DNS servers, and proxies are being used, and how much data is being sent.




