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
        "void error(const c
