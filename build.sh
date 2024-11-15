#!/bin/bash

# Define file names for the server and client source files
SERVER_SRC="server.c"
CLIENT_SRC="client.c"
SERVER_EXEC="server"
CLIENT_EXEC="client"

# Function to create the server source code
create_server_code() {
    cat << 'EOF' > $SERVER_SRC
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define PORT 8080
#define CLIENT_LIMIT 5

void handle_client(int client_sock) {
    char *menu = "Select a command:\n"
                 "1. Download a file (URL)\n"
                 "2. Shutdown client\n"
                 "3. Print system info\n"
                 "4. Send a custom message\n"
                 "Enter command number: ";
    char command[1024];

    // Send menu options to the client
    send(client_sock, menu, strlen(menu), 0);

    // Receive the command selection from the client
    int bytes_received = recv(client_sock, command, sizeof(command), 0);
    if (bytes_received <= 0) {
        printf("Failed to receive command from client\n");
        close(client_sock);
        return;
    }

    command[bytes_received] = '\0';  // Null-terminate the command

    // Check which command the user selected and send corresponding action
    if (strcmp(command, "1") == 0) {
        // Download file command
        char *message = "download http://example.com/file.txt\n";
        send(client_sock, message, strlen(message), 0);
        printf("Sent download command to client\n");
    } else if (strcmp(command, "2") == 0) {
        // Shutdown command
        char *message = "shutdown\n";
        send(client_sock, message, strlen(message), 0);
        printf("Sent shutdown command to client\n");
    } else if (strcmp(command, "3") == 0) {
        // Print system info command
        char *message = "sysinfo\n";
        send(client_sock, message, strlen(message), 0);
        printf("Sent system info command to client\n");
    } else if (strcmp(command, "4") == 0) {
        // Send custom message command
        char *message = "Hello, client! This is a custom message.\n";
        send(client_sock, message, strlen(message), 0);
        printf("Sent custom message to client\n");
    } else {
        printf("Invalid command selected.\n");
    }

    // Close the client connection after sending the command
    close(client_sock);
}

int main() {
    int server_sock, client_sock;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    // Create socket
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == -1) {
        perror("Socket creation failed");
        return -1;
    }

    // Configure server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // Bind the socket
    if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        return -1;
    }

    // Listen for incoming connections
    if (listen(server_sock, CLIENT_LIMIT) < 0) {
        perror("Listen failed");
        return -1;
    }
    printf("Server listening on port %d\n", PORT);

    // Accept incoming connections from clients
    while ((client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &client_len)) >= 0) {
        printf("Client connected\n");
        handle_client(client_sock);
    }

    if (client_sock < 0) {
        perror("Accept failed");
    }

    close(server_sock);
    return 0;
}
EOF
}

# Function to create the client source code
create_client_code() {
    cat << 'EOF' > $CLIENT_SRC
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <curl/curl.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8080

// Function to download a file using curl with Tor or another proxy
void download_file(const char *url, const char *output_filename, const char *proxy) {
    CURL *curl;
    CURLcode res;
    FILE *fp;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if (curl) {
        fp = fopen(output_filename, "wb");
        if (!fp) {
            perror("Failed to open file for writing");
            return;
        }

        // If the proxy is Tor (SOCKS5)
        if (strcmp(proxy, "tor") == 0) {
            curl_easy_setopt(curl, CURLOPT_URL, url);
            curl_easy_setopt(curl, CURLOPT_PROXY, "socks5h://127.0.0.1:9050");  // Tor's SOCKS5 proxy
        } else {
            curl_easy_setopt(curl, CURLOPT_URL, url);
            curl_easy_setopt(curl, CURLOPT_PROXY, proxy);  // External proxy
        }
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        fclose(fp);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
}

// Function to execute received commands
void execute_command(const char *command) {
    if (strncmp(command, "download", 8) == 0) {
        // Extract URL from the command (skip the "download " part)
        char *url = command + 9;
        download_file(url, "downloaded_file.txt", "tor");  // Use Tor for download
    } else if (strcmp(command, "shutdown") == 0) {
        printf("Shutting down client...\n");
        exit(0);  // Exit the client program
    } else if (strcmp(command, "sysinfo") == 0) {
        printf("System info: This is a simulated response.\n");
    } else {
        printf("Unknown command received: %s\n", command);
    }
}

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[1024];
    int read_size;

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("Socket creation failed");
        return -1;
    }

    // Configure server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Connect to the server
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection failed");
        return -1;
    }

    printf("Connected to server at %s:%d\n", SERVER_IP, SERVER_PORT);

    // Receive menu
    read_size = recv(sock, buffer, sizeof(buffer), 0);
    if (read_size > 0) {
        buffer[read_size] = '\0';
        printf("%s", buffer);  // Display menu to the client
    }

    // Get client command input (for example, "1", "2", "3", or "4")
    printf("Enter command number: ");
    fgets(buffer, sizeof(buffer), stdin);

    // Send selected command to the server
    send(sock, buffer, strlen(buffer), 0);

    // Wait for command response
    read_size = recv(sock, buffer, sizeof(buffer), 0);
    if (read_size > 0) {
        buffer[read_size] = '\0';
        execute_command(buffer);
    }

    close(sock);
    return 0;
}
EOF
}

# Function to check if Tor is running and start it if not
start_tor_if_needed() {
    if ! pgrep -x "tor" > /dev/null; then
        echo "Tor is not running. Starting Tor..."
        sudo service tor start
    else
        echo "Tor is already running."
    fi
}

# Function to compile both server and client
compile_code() {
    # Compile the server and client C files
    echo "Compiling server and client..."
    gcc -o $SERVER_EXEC $SERVER_SRC
    gcc -o $CLIENT_EXEC $CLIENT_SRC -lcurl
}

# Function to start the server and client
start_server_and_client() {
    echo "Starting the server..."
    ./$SERVER_EXEC &  # Start server in the background

    # Wait a moment to ensure server is up
    sleep 2

    echo "Starting the client..."
    ./$CLIENT_EXEC  # Start client
}

# Main script execution
echo "Creating source code files for the server and client..."
create_server_code
create_client_code

echo "Compiling the source code..."
compile_code

# Ensure Tor is running if required
start_tor_if_needed

echo "Running the server and client..."
start_server_and_client

echo "Script completed successfully."
