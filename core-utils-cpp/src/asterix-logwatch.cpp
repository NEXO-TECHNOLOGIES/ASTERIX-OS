/*
 * =====================================================================
 * ASTERIX OS :: C++ :: Real-Time Log Watcher & Pattern Alerter
 * Tails any log file and highlights/alerts on configurable regex patterns
 * Language: C++17
 * =====================================================================
 */

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <chrono>
#include <thread>
#include <csignal>
#include <ctime>
#include <iomanip>

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

struct Pattern {
    std::string label;
    std::regex  re;
    std::string color;
    int         hits = 0;
};

static volatile bool g_running = true;
void sig_handler(int) { g_running = false; }

std::string timestamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::ostringstream ss;
    ss << std::put_time(std::localtime(&t), "%H:%M:%S");
    return ss.str();
}

void tail_file(const std::string& path, std::vector<Pattern>& patterns) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << Color::RED << "[!] Cannot open: " << path << Color::RESET << "\n";
        return;
    }

    /* Seek to end to only tail new lines */
    file.seekg(0, std::ios::end);
    std::streampos last_pos = file.tellg();

    std::cout << Color::CYAN << Color::BOLD
              << "\n  ┌──────────────────────────────────────────────────────┐\n"
              << "  │   ASTERIX OS ⚡ LIVE LOG WATCHER & THREAT ALERTER    │\n"
              << "  │   File: " << std::left << std::setw(42) << path << " │\n"
              << "  └──────────────────────────────────────────────────────┘\n"
              << Color::RESET << "\n";

    long long line_count = 0;

    while (g_running) {
        file.clear();
        file.seekg(0, std::ios::end);
        std::streampos cur_pos = file.tellg();

        if (cur_pos > last_pos) {
            file.seekg(last_pos);
            std::string line;
            while (std::getline(file, line)) {
                line_count++;
                bool matched = false;

                for (auto& p : patterns) {
                    if (std::regex_search(line, p.re)) {
                        p.hits++;
                        matched = true;
                        std::cout << Color::GRAY << "[" << timestamp() << "]  "
                                  << Color::RESET
                                  << p.color << Color::BOLD << "[" << p.label << "]"
                                  << Color::RESET << "  " << Color::WHITE
                                  << line << Color::RESET << "\n";
                        break;
                    }
                }

                if (!matched) {
                    std::cout << Color::GRAY << "[" << timestamp() << "]  "
                              << line << Color::RESET << "\n";
                }
            }
            last_pos = file.tellg();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    std::cout << "\n" << Color::CYAN << "── Session Summary ──────────────────────────\n" << Color::RESET;
    std::cout << "  Lines processed: " << Color::GREEN << line_count << Color::RESET << "\n";
    for (const auto& p : patterns) {
        std::cout << "  " << p.color << p.label << Color::RESET
                  << " hits: " << Color::YELLOW << p.hits << Color::RESET << "\n";
    }
}

int main(int argc, char** argv) {
    signal(SIGINT, sig_handler);

    std::string log_path = "/var/log/syslog";
    if (argc >= 2) log_path = argv[1];

    /* Built-in threat detection patterns */
    std::vector<Pattern> patterns = {
        { "FAILED_AUTH",   std::regex("(failed password|authentication failure|invalid user)", std::regex::icase), Color::RED,     0 },
        { "ROOT_ACCESS",   std::regex("(sudo|su\\[|root login)",                               std::regex::icase), Color::MAGENTA, 0 },
        { "SSH_BRUTE",     std::regex("(preauth|repeated login failure|maxauthtries)",         std::regex::icase), Color::RED,     0 },
        { "PORT_SCAN",     std::regex("(nmap|port scan|connect.*refused)",                     std::regex::icase), Color::YELLOW,  0 },
        { "KERNEL_OOPS",   std::regex("(kernel panic|oops|BUG:|segfault)",                    std::regex::icase), Color::RED,     0 },
        { "CRON_JOB",      std::regex("(cron|CMD)",                                           std::regex::icase), Color::CYAN,    0 },
        { "SERVICE_START", std::regex("(started|starting|loaded|active)",                      std::regex::icase), Color::GREEN,   0 },
        { "UFW_BLOCK",     std::regex("(UFW BLOCK|iptables|DROP)",                            std::regex::icase), Color::YELLOW,  0 },
        { "DISK_ERROR",    std::regex("(I/O error|bad block|filesystem error)",               std::regex::icase), Color::RED,     0 },
    };

    /* Allow extra custom patterns from args */
    for (int i = 2; i < argc; i++) {
        try {
            patterns.push_back({ "CUSTOM-" + std::to_string(i - 1),
                                  std::regex(argv[i], std::regex::icase),
                                  Color::MAGENTA, 0 });
            std::cout << Color::GREEN << "[+] Added custom pattern: " << argv[i] << Color::RESET << "\n";
        } catch (...) {
            std::cerr << Color::YELLOW << "[!] Invalid regex: " << argv[i] << Color::RESET << "\n";
        }
    }

    tail_file(log_path, patterns);
    return 0;
}
