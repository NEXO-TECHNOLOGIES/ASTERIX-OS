/*
 * =====================================================================
 * ASTERIX OS :: C++ :: Vulnerability Banner Grabber & Pattern Scanner
 * Connects to target ports, grabs service banners, matches CVE patterns
 * Language: C++17
 * =====================================================================
 */

#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <fcntl.h>

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

struct VulnSignature {
    std::string pattern;
    std::string cve;
    std::string description;
    std::string severity;
};

/* Known vulnerable banner pattern signatures */
static const std::vector<VulnSignature> SIGNATURES = {
    { "OpenSSH_7\\.[0-4]",       "CVE-2016-6515", "OpenSSH <7.4 DoS via password auth",      "HIGH"   },
    { "Apache/2\\.2\\.",         "CVE-2011-3192", "Apache 2.2.x Range Header DoS",            "HIGH"   },
    { "Apache/2\\.4\\.[0-2][0-9]","CVE-2021-41773","Apache 2.4.49/50 Path Traversal RCE",    "CRITICAL"},
    { "vsftpd 2\\.3\\.4",        "CVE-2011-2523", "vsftpd 2.3.4 Backdoor Command Execution", "CRITICAL"},
    { "ProFTPD 1\\.3\\.3",       "CVE-2010-4221", "ProFTPD 1.3.3 Telnet IAC Buffer Overflow","HIGH"   },
    { "nginx/1\\.[01]\\.",       "CVE-2013-2028", "nginx chunked transfer buffer overflow",   "HIGH"   },
    { "Microsoft-IIS/6\\.0",     "CVE-2017-7269", "IIS 6.0 WebDAV ScStoragePathFromUrl RCE", "CRITICAL"},
    { "Samba.*3\\.0\\.",         "CVE-2007-2447", "Samba 3.0 username map script injection",  "CRITICAL"},
    { "OpenSSL/1\\.0\\.1[a-f]",  "CVE-2014-0160", "OpenSSL Heartbleed Information Disclosure","CRITICAL"},
    { "PHP/5\\.[0-4]\\.",        "CVE-2012-1823", "PHP-CGI remote code execution",            "HIGH"   },
};

struct ScanResult {
    int         port;
    bool        open;
    std::string banner;
    std::vector<VulnSignature> vulns;
};

std::mutex results_mutex;
std::vector<ScanResult> scan_results;

std::string grab_banner(const std::string& host, int port, int timeout_ms = 3000) {
    struct addrinfo hints{}, *res = nullptr;
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    std::string port_str = std::to_string(port);
    if (getaddrinfo(host.c_str(), port_str.c_str(), &hints, &res) != 0 || !res)
        return "";

    int sock = socket(res->ai_family, res->ai_socktype, 0);
    if (sock < 0) { freeaddrinfo(res); return ""; }

    /* non-blocking connect */
    fcntl(sock, F_SETFL, O_NONBLOCK);
    connect(sock, res->ai_addr, res->ai_addrlen);
    freeaddrinfo(res);

    fd_set wfd; FD_ZERO(&wfd); FD_SET(sock, &wfd);
    struct timeval tv{ timeout_ms / 1000, (timeout_ms % 1000) * 1000 };
    if (select(sock + 1, nullptr, &wfd, nullptr, &tv) <= 0) { close(sock); return ""; }

    int err = 0; socklen_t el = sizeof(err);
    getsockopt(sock, SOL_SOCKET, SO_ERROR, &err, &el);
    if (err) { close(sock); return ""; }

    /* Set back to blocking for recv */
    fcntl(sock, F_SETFL, 0);

    /* Send HTTP HEAD for web ports */
    if (port == 80 || port == 8080 || port == 443 || port == 8443) {
        const char* req = "HEAD / HTTP/1.0\r\nHost: target\r\n\r\n";
        send(sock, req, strlen(req), 0);
    }

    char buf[2048]{};
    fd_set rfd; FD_ZERO(&rfd); FD_SET(sock, &rfd);
    struct timeval rtv{ 2, 0 };
    if (select(sock + 1, &rfd, nullptr, nullptr, &rtv) > 0) {
        recv(sock, buf, sizeof(buf) - 1, 0);
    }
    close(sock);

    /* Collapse whitespace */
    std::string banner(buf);
    if (banner.size() > 256) banner = banner.substr(0, 256);
    return banner;
}

std::vector<VulnSignature> match_signatures(const std::string& banner) {
    std::vector<VulnSignature> matches;
    for (const auto& sig : SIGNATURES) {
        try {
            std::regex re(sig.pattern, std::regex::icase);
            if (std::regex_search(banner, re))
                matches.push_back(sig);
        } catch (...) {}
    }
    return matches;
}

void scan_port(const std::string& host, int port) {
    std::string banner = grab_banner(host, port);
    ScanResult r;
    r.port   = port;
    r.open   = !banner.empty();
    r.banner = banner;
    if (r.open) r.vulns = match_signatures(banner);

    std::lock_guard<std::mutex> lock(results_mutex);
    scan_results.push_back(r);
}

void print_banner_header() {
    std::cout << Color::CYAN << Color::BOLD
              << "\n  ┌─────────────────────────────────────────────────────────┐\n"
              << "  │   ASTERIX OS :: C++ VULNERABILITY SCANNER & BANNER GRAB │\n"
              << "  └─────────────────────────────────────────────────────────┘\n"
              << Color::RESET << "\n";
}

int main(int argc, char** argv) {
    print_banner_header();

    if (argc < 2) {
        std::cout << Color::CYAN << "Usage:\n" << Color::RESET
                  << "  asterix-vulnscan <host> [start_port] [end_port] [threads]\n"
                  << "  asterix-vulnscan 192.168.1.1 1 1024 16\n\n";
        return 1;
    }

    std::string host     = argv[1];
    int start_port       = (argc >= 3) ? atoi(argv[2]) : 1;
    int end_port         = (argc >= 4) ? atoi(argv[3]) : 1024;
    int max_threads      = (argc >= 5) ? atoi(argv[4]) : 16;

    std::cout << Color::YELLOW << "[*] Target:  " << Color::WHITE << host << "\n" << Color::RESET;
    std::cout << Color::YELLOW << "[*] Ports:   " << Color::WHITE << start_port << " - " << end_port << "\n" << Color::RESET;
    std::cout << Color::YELLOW << "[*] Threads: " << Color::WHITE << max_threads << "\n\n" << Color::RESET;

    std::vector<std::thread> threads;
    std::atomic<int> next_port(start_port);

    auto worker = [&]() {
        while (true) {
            int port = next_port.fetch_add(1);
            if (port > end_port) break;
            scan_port(host, port);
        }
    };

    for (int i = 0; i < max_threads; i++)
        threads.emplace_back(worker);
    for (auto& t : threads) t.join();

    /* Sort results */
    std::sort(scan_results.begin(), scan_results.end(),
              [](const ScanResult& a, const ScanResult& b){ return a.port < b.port; });

    int total_open = 0, total_vulns = 0;
    for (const auto& r : scan_results) {
        if (!r.open) continue;
        total_open++;

        std::cout << "  " << Color::GREEN << "[OPEN]" << Color::RESET
                  << "  Port " << Color::YELLOW << std::setw(5) << r.port << Color::RESET;

        /* Show first line of banner */
        std::string first_line = r.banner.substr(0, r.banner.find('\n'));
        if (first_line.size() > 60) first_line = first_line.substr(0, 60);
        std::cout << "  " << Color::WHITE << first_line << Color::RESET;

        if (!r.vulns.empty()) {
            std::cout << "\n";
            for (const auto& v : r.vulns) {
                std::string sev_color = (v.severity == "CRITICAL") ? Color::RED : Color::YELLOW;
                std::cout << "        " << sev_color << Color::BOLD
                          << "⚠ " << v.cve << " [" << v.severity << "] "
                          << v.description << Color::RESET << "\n";
                total_vulns++;
            }
        } else {
            std::cout << "\n";
        }
    }

    std::cout << "\n" << Color::CYAN << "────────────────────────────────────────────\n" << Color::RESET;
    std::cout << Color::GREEN  << "  Open Ports:   " << total_open  << "\n" << Color::RESET;
    std::cout << Color::RED    << "  Vulnerabilities Found: " << total_vulns << "\n" << Color::RESET;
    return 0;
}
