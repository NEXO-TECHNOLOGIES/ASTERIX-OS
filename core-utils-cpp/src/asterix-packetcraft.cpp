/*
 * =====================================================================
 * ASTERIX OS :: C++ :: Raw Network Packet Crafter & Analyzer
 * Crafts and parses TCP/UDP/ICMP packets using raw sockets
 * Language: C++17 (g++ -std=c++17 -O2)
 * =====================================================================
 */

#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <cstring>
#include <csignal>
#include <ctime>
#include <memory>

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>
#include <netdb.h>

namespace Color {
    constexpr const char* CYAN    = "\033[38;5;51m";
    constexpr const char* GREEN   = "\033[38;5;46m";
    constexpr const char* YELLOW  = "\033[38;5;220m";
    constexpr const char* MAGENTA = "\033[38;5;201m";
    constexpr const char* RED     = "\033[38;5;196m";
    constexpr const char* WHITE   = "\033[38;5;231m";
    constexpr const char* GRAY    = "\033[38;5;240m";
    constexpr const char* BOLD    = "\033[1m";
    constexpr const char* RESET   = "\033[0m";
}

static volatile bool g_running = true;
void sig_handler(int) { g_running = false; }

uint16_t checksum(const void* data, size_t len) {
    const uint16_t* ptr = reinterpret_cast<const uint16_t*>(data);
    uint32_t sum = 0;
    while (len > 1) { sum += *ptr++; len -= 2; }
    if (len) sum += *reinterpret_cast<const uint8_t*>(ptr);
    while (sum >> 16) sum = (sum & 0xFFFF) + (sum >> 16);
    return static_cast<uint16_t>(~sum);
}

std::string hex_byte(uint8_t b) {
    std::ostringstream ss;
    ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    return ss.str();
}

void print_banner() {
    std::cout << Color::CYAN << Color::BOLD
              << "  ┌─────────────────────────────────────────────────────────────┐\n"
              << "  │   ASTERIX OS ⚡ C++ RAW PACKET CRAFTER & LAYER-3 ANALYZER  │\n"
              << "  └─────────────────────────────────────────────────────────────┘\n"
              << Color::RESET << "\n";
}

void parse_packet(const uint8_t* buf, ssize_t len) {
    if (len < (ssize_t)sizeof(iphdr)) return;

    const iphdr* ip = reinterpret_cast<const iphdr*>(buf);

    char src[INET_ADDRSTRLEN], dst[INET_ADDRSTRLEN];
    in_addr sa, da;
    sa.s_addr = ip->saddr;
    da.s_addr = ip->daddr;
    inet_ntop(AF_INET, &sa, src, sizeof(src));
    inet_ntop(AF_INET, &da, dst, sizeof(dst));

    std::cout << Color::GRAY << "  [" << std::time(nullptr) << "]  " << Color::RESET;

    std::string proto_name;
    std::string proto_color = Color::WHITE;

    switch (ip->protocol) {
        case IPPROTO_TCP:  proto_name = "TCP";  proto_color = Color::CYAN;    break;
        case IPPROTO_UDP:  proto_name = "UDP";  proto_color = Color::YELLOW;  break;
        case IPPROTO_ICMP: proto_name = "ICMP"; proto_color = Color::MAGENTA; break;
        default:           proto_name = "IP#" + std::to_string(ip->protocol); break;
    }

    std::cout << proto_color << std::left << std::setw(5) << proto_name << Color::RESET
              << "  " << Color::GREEN << std::setw(16) << src << Color::RESET
              << " → " << Color::GREEN << std::setw(16) << dst << Color::RESET;

    size_t ip_hdr_len = ip->ihl * 4;

    if (ip->protocol == IPPROTO_TCP && len >= (ssize_t)(ip_hdr_len + sizeof(tcphdr))) {
        const tcphdr* tcp = reinterpret_cast<const tcphdr*>(buf + ip_hdr_len);
        uint16_t sport = ntohs(tcp->source);
        uint16_t dport = ntohs(tcp->dest);

        std::cout << "  Port " << Color::YELLOW << sport << Color::RESET
                  << " → " << Color::YELLOW << dport << Color::RESET;

        std::string flags;
        if (tcp->syn) flags += "SYN ";
        if (tcp->ack) flags += "ACK ";
        if (tcp->fin) flags += "FIN ";
        if (tcp->rst) flags += "RST ";
        if (tcp->psh) flags += "PSH ";

        if (!flags.empty())
            std::cout << "  [" << Color::MAGENTA << flags << Color::RESET << "]";

    } else if (ip->protocol == IPPROTO_UDP && len >= (ssize_t)(ip_hdr_len + 8)) {
        const uint16_t* udp = reinterpret_cast<const uint16_t*>(buf + ip_hdr_len);
        std::cout << "  Port " << Color::YELLOW << ntohs(udp[0]) << Color::RESET
                  << " → " << Color::YELLOW << ntohs(udp[1]) << Color::RESET;
    }

    std::cout << "  Len=" << Color::GRAY << len << Color::RESET << "\n";
}

void send_icmp_ping(const char* target, int count) {
    in_addr_t dst_addr = inet_addr(target);
    if (dst_addr == INADDR_NONE) {
        struct hostent* he = gethostbyname(target);
        if (!he) { std::cerr << Color::RED << "[!] DNS resolution failed\n" << Color::RESET; return; }
        dst_addr = *reinterpret_cast<in_addr_t*>(he->h_addr);
    }

    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock < 0) {
        std::cerr << Color::RED << "[!] Raw socket requires root privileges\n" << Color::RESET;
        return;
    }

    struct sockaddr_in dst{};
    dst.sin_family = AF_INET;
    dst.sin_addr.s_addr = dst_addr;

    std::cout << "\n" << Color::CYAN << "[*] Sending " << count << " ICMP pings to " << target << Color::RESET << "\n\n";

    for (int i = 0; i < count && g_running; i++) {
        uint8_t pkt[64]{};
        icmphdr* icmp = reinterpret_cast<icmphdr*>(pkt);
        icmp->type = ICMP_ECHO;
        icmp->code = 0;
        icmp->un.echo.id = htons(getpid() & 0xFFFF);
        icmp->un.echo.sequence = htons(i + 1);
        memcpy(pkt + sizeof(icmphdr), "ASTERIX-PING-PAYLOAD-XYZ!", 25);
        icmp->checksum = checksum(pkt, sizeof(pkt));

        struct timespec ts_start, ts_end;
        clock_gettime(CLOCK_MONOTONIC, &ts_start);
        sendto(sock, pkt, sizeof(pkt), 0, reinterpret_cast<sockaddr*>(&dst), sizeof(dst));

        uint8_t recv_buf[256];
        sockaddr_in from{};
        socklen_t from_len = sizeof(from);
        ssize_t received = recvfrom(sock, recv_buf, sizeof(recv_buf), 0,
                                    reinterpret_cast<sockaddr*>(&from), &from_len);
        clock_gettime(CLOCK_MONOTONIC, &ts_end);

        double rtt_ms = (ts_end.tv_sec - ts_start.tv_sec) * 1000.0
                      + (ts_end.tv_nsec - ts_start.tv_nsec) / 1e6;

        char from_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &from.sin_addr, from_str, sizeof(from_str));

        if (received > 0) {
            std::cout << "  " << Color::GREEN << "[✔]" << Color::RESET
                      << " Reply from " << Color::YELLOW << from_str << Color::RESET
                      << "  RTT=" << Color::CYAN << std::fixed << std::setprecision(2)
                      << rtt_ms << "ms" << Color::RESET << "\n";
        } else {
            std::cout << "  " << Color::RED << "[✗] No reply (seq=" << i + 1 << ")" << Color::RESET << "\n";
        }
        sleep(1);
    }
    close(sock);
}

void sniff_packets(int count) {
    int sock = socket(AF_PACKET, SOCK_RAW, htons(0x0800)); /* IPv4 */
    if (sock < 0) {
        std::cerr << Color::RED << "[!] Raw packet sniffing requires root privileges\n" << Color::RESET;
        return;
    }

    std::cout << Color::CYAN << "[*] Sniffing " << count << " IPv4 packets...\n" << Color::RESET;
    std::cout << Color::YELLOW << "    (Ctrl+C to stop)\n\n" << Color::RESET;

    uint8_t buf[65536];
    int captured = 0;
    while (captured < count && g_running) {
        ssize_t len = recv(sock, buf, sizeof(buf), 0);
        if (len > 14) {  /* Skip 14-byte Ethernet header */
            parse_packet(buf + 14, len - 14);
            captured++;
        }
    }
    close(sock);
    std::cout << "\n" << Color::GREEN << "[✔] Captured " << captured << " packets.\n" << Color::RESET;
}

int main(int argc, char** argv) {
    print_banner();
    signal(SIGINT, sig_handler);

    if (argc >= 2 && std::string(argv[1]) == "--ping" && argc >= 3) {
        int count = (argc >= 5 && std::string(argv[3]) == "--count") ? atoi(argv[4]) : 4;
        send_icmp_ping(argv[2], count);
        return 0;
    }

    if (argc >= 2 && std::string(argv[1]) == "--sniff") {
        int count = (argc >= 4 && std::string(argv[2]) == "--count") ? atoi(argv[3]) : 100;
        sniff_packets(count);
        return 0;
    }

    std::cout << Color::CYAN << "Usage:\n" << Color::RESET;
    std::cout << "  asterix-packetcraft --ping <host> [--count N]\n";
    std::cout << "  asterix-packetcraft --sniff [--count N]\n";
    std::cout << "\nExamples:\n";
    std::cout << "  asterix-packetcraft --ping 8.8.8.8 --count 5\n";
    std::cout << "  asterix-packetcraft --sniff --count 200\n";
    return 0;
}
