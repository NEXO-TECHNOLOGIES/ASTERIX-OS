// =====================================================================
// ASTERIX OS :: Go :: DNS Enumerator & Web HTTP Fingerprinter
// Fast concurrent DNS subdomain brute-force and HTTP banner grabber
// Language: Go 1.21+
// Build: go build -ldflags="-s -w" -o asterix-webrecon ./
// =====================================================================

package main

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// ANSI colors
const (
	Cyan    = "\033[38;5;51m"
	Green   = "\033[38;5;46m"
	Yellow  = "\033[38;5;220m"
	Magenta = "\033[38;5;201m"
	Red     = "\033[38;5;196m"
	White   = "\033[38;5;231m"
	Gray    = "\033[38;5;240m"
	Bold    = "\033[1m"
	Reset   = "\033[0m"
)

var commonSubdomains = []string{
	"www", "mail", "ftp", "smtp", "pop", "imap", "ns1", "ns2", "mx",
	"vpn", "ssh", "dev", "staging", "api", "admin", "portal", "auth",
	"cdn", "static", "assets", "blog", "shop", "store", "forum",
	"git", "gitlab", "jenkins", "ci", "monitor", "panel", "dashboard",
	"test", "beta", "demo", "app", "mobile", "m", "secure", "login",
}

type ReconResult struct {
	Subdomain  string
	IP         string
	StatusCode int
	Server     string
	Title      string
	Headers    map[string]string
}

func printBanner() {
	fmt.Printf("%s%s", Cyan, Bold)
	fmt.Println("  ╔═══════════════════════════════════════════════════════════╗")
	fmt.Println("  ║   ASTERIX OS ⚡ Go DNS ENUMERATOR & WEB FINGERPRINTER    ║")
	fmt.Println("  ╚═══════════════════════════════════════════════════════════╝")
	fmt.Printf("%s\n", Reset)
}

func resolveDomain(subdomain, domain string) (string, bool) {
	full := subdomain + "." + domain
	ips, err := net.LookupHost(full)
	if err != nil || len(ips) == 0 {
		return "", false
	}
	return ips[0], true
}

func httpFingerprint(url string) (int, string, string, map[string]string) {
	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 3 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}

	resp, err := client.Get(url)
	if err != nil {
		return 0, "", "", nil
	}
	defer resp.Body.Close()

	server := resp.Header.Get("Server")
	powered := resp.Header.Get("X-Powered-By")
	if powered != "" && server == "" {
		server = powered
	}

	// Read a small portion for title extraction
	scanner := bufio.NewScanner(resp.Body)
	scanner.Buffer(make([]byte, 4096), 4096)
	title := ""
	lineCount := 0
	for scanner.Scan() && lineCount < 30 {
		line := scanner.Text()
		lineCount++
		lower := strings.ToLower(line)
		if strings.Contains(lower, "<title") {
			start := strings.Index(lower, "<title")
			end := strings.Index(lower, "</title>")
			if start >= 0 && end > start {
				inner := line[start:]
				gt := strings.Index(inner, ">")
				if gt >= 0 && end > 0 {
					title = strings.TrimSpace(inner[gt+1 : end-start])
					if len(title) > 60 {
						title = title[:60] + "..."
					}
				}
			}
		}
	}

	headers := map[string]string{
		"Server":          server,
		"X-Frame-Options": resp.Header.Get("X-Frame-Options"),
		"Content-Type":    resp.Header.Get("Content-Type"),
		"X-Powered-By":    resp.Header.Get("X-Powered-By"),
	}

	return resp.StatusCode, server, title, headers
}

func probeSubdomain(subdomain, domain string, results chan<- ReconResult, wg *sync.WaitGroup, sem chan struct{}) {
	defer wg.Done()
	sem <- struct{}{}
	defer func() { <-sem }()

	ip, found := resolveDomain(subdomain, domain)
	if !found {
		return
	}

	full := subdomain + "." + domain
	result := ReconResult{
		Subdomain: full,
		IP:        ip,
	}

	// Try HTTPS first, fallback to HTTP
	for _, scheme := range []string{"https", "http"} {
		url := scheme + "://" + full
		code, server, title, headers := httpFingerprint(url)
		if code > 0 {
			result.StatusCode = code
			result.Server = server
			result.Title = title
			result.Headers = headers
			break
		}
	}

	results <- result
}

func enumSubdomains(domain string, wordlist []string, threads int) {
	fmt.Printf("%s[*] Enumerating subdomains for: %s%s%s\n", Yellow, White, domain, Reset)
	fmt.Printf("%s[*] Wordlist size: %d | Threads: %d%s\n\n", Yellow, len(wordlist), threads, Reset)
	fmt.Printf("  %s%-45s %-16s %s %-10s %s%s\n",
		Yellow, "SUBDOMAIN", "IP ADDRESS", "STATUS", "SERVER", "TITLE", Reset)
	fmt.Printf("  %s%s%s\n", Gray, strings.Repeat("─", 100), Reset)

	results := make(chan ReconResult, 200)
	var wg sync.WaitGroup
	sem := make(chan struct{}, threads)

	go func() {
		for _, sub := range wordlist {
			wg.Add(1)
			go probeSubdomain(sub, domain, results, &wg, sem)
		}
		wg.Wait()
		close(results)
	}()

	found := 0
	for r := range results {
		found++
		statusColor := Green
		if r.StatusCode >= 400 {
			statusColor = Yellow
		} else if r.StatusCode >= 500 {
			statusColor = Red
		}

		fmt.Printf("  %s%-45s%s %s%-16s%s %s[%d]%s  %-20s %s\n",
			Cyan, r.Subdomain, Reset,
			Green, r.IP, Reset,
			statusColor, r.StatusCode, Reset,
			r.Server,
			r.Title)
	}

	fmt.Printf("\n%s[✔] Found %d live subdomains.%s\n\n", Green, found, Reset)
}

func fingerprint(target string) {
	fmt.Printf("%s[*] Fingerprinting: %s%s%s\n\n", Yellow, White, target, Reset)

	for _, scheme := range []string{"https", "http"} {
		url := scheme + "://" + target
		code, server, title, headers := httpFingerprint(url)
		if code > 0 {
			fmt.Printf("%s[ HTTP FINGERPRINT ]%s\n", Cyan, Reset)
			fmt.Printf("  • URL:           %s%s%s\n", White, url, Reset)
			fmt.Printf("  • Status Code:   %s%d%s\n", Green, code, Reset)
			fmt.Printf("  • Server:        %s%s%s\n", Yellow, server, Reset)
			fmt.Printf("  • Page Title:    %s%s%s\n", White, title, Reset)
			fmt.Printf("\n%s[ SECURITY HEADERS ]%s\n", Cyan, Reset)
			for k, v := range headers {
				if v == "" {
					fmt.Printf("  • %-25s %s[MISSING]%s\n", k, Red, Reset)
				} else {
					fmt.Printf("  • %-25s %s%s%s\n", k, Green, v, Reset)
				}
			}
			return
		}
	}
	fmt.Printf("%s[!] No HTTP response from target%s\n", Red, Reset)
}

func main() {
	printBanner()

	if len(os.Args) < 3 {
		fmt.Printf("%sUsage:%s\n", Cyan, Reset)
		fmt.Println("  asterix-webrecon --enum   <domain> [threads]")
		fmt.Println("  asterix-webrecon --finger <host>")
		fmt.Println("\nExamples:")
		fmt.Println("  asterix-webrecon --enum   example.com 20")
		fmt.Println("  asterix-webrecon --finger target.htb")
		return
	}

	mode := os.Args[1]
	target := os.Args[2]

	switch mode {
	case "--enum":
		threads := 20
		if len(os.Args) >= 4 {
			fmt.Sscanf(os.Args[3], "%d", &threads)
		}
		enumSubdomains(target, commonSubdomains, threads)

	case "--finger":
		fingerprint(target)

	default:
		fmt.Printf("%s[!] Unknown mode: %s%s\n", Red, mode, Reset)
	}
}
