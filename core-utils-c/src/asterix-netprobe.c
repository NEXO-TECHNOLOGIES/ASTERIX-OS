/*
 * =====================================================================
 * ASTERIX OS - Native C Network Latency & Port Prober (netprobe)
 * Asynchronous non-blocking socket connectivity & latency benchmark
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

double get_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec * 1000.0) + (tv.tv_usec / 1000.0);
}

int probe_port(const char *host, int port, int timeout_ms) {
    struct addrinfo hints, *res;
    char port_str[16];
    snprintf(port_str, sizeof(port_str), "%d", port);

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port_str, &hints, &res) != 0) {
        return -1;
    }

    int sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sock < 0) {
        freeaddrinfo(res);
        return -1;
    }

    // Set non-blocking
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);

    double start = get_time_ms();
    int rc = connect(sock, res->ai_addr, res->ai_addrlen);

    if (rc < 0 && errno == EINPROGRESS) {
        fd_set wfds;
        FD_ZERO(&wfds);
        FD_SET(sock, &wfds);

        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;

        int sel = select(sock + 1, NULL, &wfds, NULL, &tv);
        if (sel > 0) {
            int err = 0;
            socklen_t len = sizeof(err);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, &err, &len);
            if (err == 0) {
                double latency = get_time_ms() - start;
                close(sock);
                freeaddrinfo(res);
                return (int)latency;
            }
        }
    } else if (rc == 0) {
        double latency = get_time_ms() - start;
        close(sock);
        freeaddrinfo(res);
        return (int)latency;
    }

    close(sock);
    freeaddrinfo(res);
    return -2; // Closed/Timeout
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("%sASTERIX OS - High-Performance Network & Port Prober%s\n", C_CYAN, C_RESET);
        printf("Usage: %s <host> [port_start] [port_end] [timeout_ms]\n", argv[0]);
        printf("Example: %s 127.0.0.1 20 100 500\n", argv[0]);
        return 1;
    }

    const char *target = argv[1];
    int start_port = 80;
    int end_port = 80;
    int timeout = 500;

    if (argc >= 3) start_port = atoi(argv[2]);
    if (argc >= 4) end_port = atoi(argv[3]); else end_port = start_port;
    if (argc >= 5) timeout = atoi(argv[4]);

    printf("\n%s[*] Probing %s (Ports %d..%d, Timeout %dms)...%s\n\n", 
           C_CYAN, target, start_port, end_port, timeout, C_RESET);

    int open_count = 0;
    for (int p = start_port; p <= end_port; p++) {
        int res = probe_port(target, p, timeout);
        if (res >= 0) {
            printf("  • Port %s%5d/tcp%s : %s[ OPEN ]%s (Latency: %s%d ms%s)\n", 
                   C_WHITE, p, C_RESET, C_GREEN, C_RESET, C_YELLOW, res, C_RESET);
            open_count++;
        }
    }

    printf("\n%s[✔] Probe Completed: %d open ports discovered.%s\n\n", 
           C_GREEN, open_count, C_RESET);
    return 0;
}
