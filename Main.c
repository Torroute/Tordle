#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

// Function to create the server listener script
void create_listener_script() {
    FILE *file = fopen("server_listener.c", "w");

    if (file == NULL) {
        printf("Error creating the listener script!\n");
        return;
    }

    // Write the basic listener code to the file
    const char *script = 
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "#include <string.h>\n"
        "#include <unistd.h>\n"
        "#include <sys/types.h>\n"
        "#include <sys/socket.h>\n"
        "#include <netinet/in.h>\n\n"
        "void error(const char *msg) {\n"
        "    perror(msg);\n"
        "    exit(1);\n"
        "}\n\n"
        "int main() {\n"
        "    int sockfd, newsockfd, portno;\n"
        "    socklen_t clilen;\n"
        "    char buffer[256];\n"
        "    struct sockaddr_in serv_addr, cli_addr;\n\n"
        "    // Ask for the port to listen on\n"
        "    printf(\"Enter port to listen on: \");\n"
        "    scanf(\"%d\", &portno);\n\n"
        "    sockfd = socket(AF_INET, SOCK_STREAM, 0);\n"
        "    if (sockfd < 0) {\n"
        "        error(\"ERROR opening socket\");\n"
        "    }\n\n"
        "    bzero((char *) &serv_addr, sizeof(serv_addr));\n"
        "    serv_addr.sin_family = AF_INET;\n"
        "    serv_addr.sin_addr.s_addr = INADDR_ANY;\n"
        "    serv_addr.sin_port = htons(portno);\n\n"
        "    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {\n"
        "        error(\"ERROR on binding\");\n"
        "    }\n\n"
        "    listen(sockfd, 5);\n"
        "    clilen = sizeof(cli_addr);\n\n"
        "    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);\n"
        "    if (newsockfd < 0) {\n"
        "        error(\"ERROR on accept\");\n"
        "    }\n\n"
        "    bzero(buffer, 256);\n"
        "    while (1) {\n"
        "        int n = read(newsockfd, buffer, 255);\n"
        "        if (n < 0) {\n"
        "            error(\"ERROR reading from socket\");\n"
        "        }\n\n"
        "        printf(\"Received command: %s\", buffer);\n\n"
        "        // Execute the command received\n"
        "        system(buffer);  // Be careful, this runs any command sent!\n\n"
        "        bzero(buffer, 256);\n"
        "    }\n\n"
        "    close(newsockfd);\n"
        "    close(sockfd);\n\n"
        "    return 0;\n"
        "}\n";

    fprintf(file, "%s", script);
    fclose(file);

    printf("Listener script created as 'server_listener.c'. You can compile and run it on another server.\n");
}

// Function to run nmap to scan for a specific port
void run_nmap() {
    char target_ip[100];
    int target_port;

    printf("Enter the target IP: ");
    scanf("%s", target_ip);
    printf("Enter the target port: ");
    scanf("%d", &target_port);

    // Build the nmap command
    char command[256];
    snprintf(command, sizeof(command), "nmap -p %d %s > nmap_results.txt &", target_port, target_ip);
    
    // Run nmap in the background
    system(command);

    printf("Nmap scan started in the background. Results will be saved to 'nmap_results.txt'.\n");
}

// Function to send a command to a listening server
void send_command_to_server() {
    int sockfd, portno;
    struct sockaddr_in serv_addr;
    char server_ip[100], command[256];

    printf("Enter server IP to send command to: ");
    scanf("%s", server_ip);
    printf("Enter port to connect to: ");
    scanf("%d", &portno);
    printf("Enter the command to send: ");
    getchar();  // Clear newline from buffer
    fgets(command, sizeof(command), stdin);

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("ERROR opening socket");
        return;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(portno);
    if (inet_pton(AF_INET, server_ip, &serv_addr.sin_addr) <= 0) {
        perror("ERROR invalid server IP address");
        return;
    }

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("ERROR connecting to server");
        return;
    }

    // Send command to the server
    write(sockfd, command, strlen(command));
    printf("Command sent to server.\n");

    close(sockfd);
}

int main() {
    int choice;

    while (1) {
        printf("\nMenu:\n");
        printf("1. Create listener script\n");
        printf("2. Run nmap in the background\n");
        printf("3. Send command to listening server\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                create_listener_script();
                break;
            case 2:
                run_nmap();
                break;
            case 3:
                send_command_to_server();
                break;
            case 4:
                printf("Exiting...\n");
                exit(0);
            default:
                printf("Invalid choice.\n");
        }
    }

    return 0;
}

