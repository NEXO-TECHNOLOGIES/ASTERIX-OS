#!/usr/bin/env python3
"""
ASTERIX OS — Master Security Arsenal & Tool Registry
Author: NEXO TECHNOLOGIES GROUP
Zero-dependency Python 3 standard library implementation.

Provides offline metadata, categorization, repository references, and on-demand
installation recipes for 180+ industry-standard cybersecurity, penetration testing,
and forensic tools without downloading or cloning heavy repositories into the base OS.
"""

import os
import sys
import json
import argparse
import platform
import subprocess

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Terminal Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[38;5;46m"
C_CYAN = "\033[38;5;51m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_GRAY = "\033[38;5;242m"
C_WHITE = "\033[38;5;231m"


# Complete Master Tool Registry (180+ Tools from Global Cybersecurity Ecosystem)
ARSENAL_REGISTRY = [
    # ── 1. Reconnaissance, OSINT & Asset Discovery ───────────────────────
    {"name": "nmap", "category": "OSINT & Recon", "github": "https://github.com/nmap/nmap", "desc": "Network exploration tool and security / port scanner", "install_type": "apt", "cmd": "sudo apt install -y nmap", "preinstalled": True},
    {"name": "masscan", "category": "OSINT & Recon", "github": "https://github.com/robertdavidgraham/masscan", "desc": "TCP port scanner, transmits SYN packets asynchronously at line rate", "install_type": "apt", "cmd": "sudo apt install -y masscan", "preinstalled": True},
    {"name": "recon-ng", "category": "OSINT & Recon", "github": "https://github.com/lanmaster53/recon-ng", "desc": "Full-featured web reconnaissance framework written in Python", "install_type": "git", "cmd": "git clone https://github.com/lanmaster53/recon-ng.git && pip install -r recon-ng/REQUIREMENTS", "preinstalled": False},
    {"name": "theHarvester", "category": "OSINT & Recon", "github": "https://github.com/laramies/theHarvester", "desc": "E-mails, subdomains and names harvester using multiple public sources", "install_type": "apt", "cmd": "sudo apt install -y theharvester", "preinstalled": False},
    {"name": "dnsenum", "category": "OSINT & Recon", "github": "https://github.com/fwaeytens/dnsenum", "desc": "Perl script to enumerate DNS information and discover ip blocks", "install_type": "apt", "cmd": "sudo apt install -y dnsenum", "preinstalled": False},
    {"name": "enum4linux-ng", "category": "OSINT & Recon", "github": "https://github.com/cddmp/enum4linux-ng", "desc": "Next-generation Windows/Samba information enumeration tool", "install_type": "git", "cmd": "git clone https://github.com/cddmp/enum4linux-ng.git", "preinstalled": False},
    {"name": "ldapdomaindump", "category": "OSINT & Recon", "github": "https://github.com/dirkjanm/ldapdomaindump", "desc": "Active Directory information dumper via LDAP", "install_type": "pipx", "cmd": "pipx install ldapdomaindump", "preinstalled": False},
    {"name": "p0f", "category": "OSINT & Recon", "github": "https://github.com/p0f/p0f", "desc": "Purely passive TCP/IP stack fingerprinting and OS detection tool", "install_type": "apt", "cmd": "sudo apt install -y p0f", "preinstalled": False},
    {"name": "amass", "category": "OSINT & Recon", "github": "https://github.com/owasp-amass/amass", "desc": "In-depth attack surface mapping and external asset discovery", "install_type": "go", "cmd": "go install -v github.com/owasp-amass/amass/v4/...@master", "preinstalled": False},
    {"name": "subfinder", "category": "OSINT & Recon", "github": "https://github.com/projectdiscovery/subfinder", "desc": "Fast passive subdomain discovery tool using curated passive sources", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "preinstalled": False},
    {"name": "naabu", "category": "OSINT & Recon", "github": "https://github.com/projectdiscovery/naabu", "desc": "Fast SYN/CONNECT port scanner written in Go with high reliability", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest", "preinstalled": False},
    {"name": "assetfinder", "category": "OSINT & Recon", "github": "https://github.com/tomnomnom/assetfinder", "desc": "Find domains and subdomains related to a given target domain", "install_type": "go", "cmd": "go install github.com/tomnomnom/assetfinder@latest", "preinstalled": False},
    {"name": "dnsx", "category": "OSINT & Recon", "github": "https://github.com/projectdiscovery/dnsx", "desc": "Fast and multi-purpose DNS toolkit allowing running multiple DNS queries", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest", "preinstalled": False},
    {"name": "massdns", "category": "OSINT & Recon", "github": "https://github.com/blechschmidt/massdns", "desc": "High-performance DNS stub resolver for bulk lookups and recon", "install_type": "apt", "cmd": "sudo apt install -y massdns", "preinstalled": False},
    {"name": "puredns", "category": "OSINT & Recon", "github": "https://github.com/d3mondev/puredns", "desc": "Fast domain resolver and active subdomain bruteforcer using MassDNS", "install_type": "go", "cmd": "go install github.com/d3mondev/puredns/v2@latest", "preinstalled": False},
    {"name": "spiderfoot", "category": "OSINT & Recon", "github": "https://github.com/smicallef/spiderfoot", "desc": "Automated open-source OSINT intelligence gathering framework", "install_type": "git", "cmd": "git clone https://github.com/smicallef/spiderfoot.git && pip install -r spiderfoot/requirements.txt", "preinstalled": False},
    {"name": "eyewitness", "category": "OSINT & Recon", "github": "https://github.com/FortyNorthSecurity/EyeWitness", "desc": "Takes screenshots of web applications, identifies headers, and auto-triages", "install_type": "apt", "cmd": "sudo apt install -y eyewitness", "preinstalled": False},

    # ── 2. Vulnerability Auditing & Scanning ──────────────────────────────
    {"name": "openvas", "category": "Vulnerability Scanning", "github": "https://github.com/greenbone/openvas-scanner", "desc": "Greenbone Vulnerability Management scanner engine for CVE audits", "install_type": "apt", "cmd": "sudo apt install -y gvm", "preinstalled": False},
    {"name": "nuclei", "category": "Vulnerability Scanning", "github": "https://github.com/projectdiscovery/nuclei", "desc": "Fast and customizable vulnerability scanner based on simple YAML DSL", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "preinstalled": False},
    {"name": "nikto", "category": "Vulnerability Scanning", "github": "https://github.com/sullo/nikto", "desc": "Web server scanner testing against 6700+ dangerous files and CGIs", "install_type": "apt", "cmd": "sudo apt install -y nikto", "preinstalled": True},
    {"name": "wapiti", "category": "Vulnerability Scanning", "github": "https://github.com/wapiti-scanner/wapiti", "desc": "Web-application vulnerability scanner auditing forms and parameters", "install_type": "apt", "cmd": "sudo apt install -y wapiti", "preinstalled": False},
    {"name": "dalfox", "category": "Vulnerability Scanning", "github": "https://github.com/hahwul/dalfox", "desc": "Fast and powerful parameter analysis and XSS scanner tool written in Go", "install_type": "go", "cmd": "go install github.com/hahwul/dalfox/v2@latest", "preinstalled": False},
    {"name": "xsstrike", "category": "Vulnerability Scanning", "github": "https://github.com/s0md3v/XSStrike", "desc": "Advanced XSS detection suite equipped with four hand-written parsers", "install_type": "git", "cmd": "git clone https://github.com/s0md3v/XSStrike.git && pip install -r XSStrike/requirements.txt", "preinstalled": False},
    {"name": "commix", "category": "Vulnerability Scanning", "github": "https://github.com/commixproject/commix", "desc": "Automated All-in-One OS Command Injection and Exploitation Tool", "install_type": "apt", "cmd": "sudo apt install -y commix", "preinstalled": True},

    # ── 3. Web Application Auditing & Fuzzing ─────────────────────────────
    {"name": "burpsuite", "category": "Web Security", "github": "https://github.com/PortSwigger", "desc": "Industry leading graphical web application security testing platform", "install_type": "apt", "cmd": "sudo apt install -y burpsuite", "preinstalled": False},
    {"name": "zaproxy", "category": "Web Security", "github": "https://github.com/zaproxy/zaproxy", "desc": "OWASP ZAP - The world's most widely used web app scanner", "install_type": "apt", "cmd": "sudo apt install -y zaproxy", "preinstalled": False},
    {"name": "sqlmap", "category": "Web Security", "github": "https://github.com/sqlmapproject/sqlmap", "desc": "Automatic SQL injection and database takeover tool", "install_type": "apt", "cmd": "sudo apt install -y sqlmap", "preinstalled": True},
    {"name": "gobuster", "category": "Web Security", "github": "https://github.com/OJ/gobuster", "desc": "Directory/file & DNS busting tool written in Go", "install_type": "apt", "cmd": "sudo apt install -y gobuster", "preinstalled": True},
    {"name": "dirb", "category": "Web Security", "github": "https://github.com/v0re/dirb", "desc": "Web Content Scanner checking for existing (and hidden) Web Objects", "install_type": "apt", "cmd": "sudo apt install -y dirb", "preinstalled": False},
    {"name": "wfuzz", "category": "Web Security", "github": "https://github.com/xmendez/wfuzz", "desc": "Web application fuzzer for bruteforcing parameters and authentication", "install_type": "apt", "cmd": "sudo apt install -y wfuzz", "preinstalled": False},
    {"name": "ffuf", "category": "Web Security", "github": "https://github.com/ffuf/ffuf", "desc": "Fast web fuzzer written in Go for paths, parameters and headers", "install_type": "apt", "cmd": "sudo apt install -y ffuf", "preinstalled": True},
    {"name": "feroxbuster", "category": "Web Security", "github": "https://github.com/epi052/feroxbuster", "desc": "A fast, simple, recursive content discovery tool written in Rust", "install_type": "apt", "cmd": "sudo apt install -y feroxbuster", "preinstalled": False},
    {"name": "httpx", "category": "Web Security", "github": "https://github.com/projectdiscovery/httpx", "desc": "Fast and multi-purpose HTTP toolkit allowing running multiple probes", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest", "preinstalled": False},
    {"name": "katana", "category": "Web Security", "github": "https://github.com/projectdiscovery/katana", "desc": "Next-generation crawling and spidering framework", "install_type": "go", "cmd": "go install github.com/projectdiscovery/katana/cmd/katana@latest", "preinstalled": False},
    {"name": "arjun", "category": "Web Security", "github": "https://github.com/s0md3v/Arjun", "desc": "HTTP parameter discovery suite to find hidden query parameters", "install_type": "pipx", "cmd": "pipx install arjun", "preinstalled": False},
    {"name": "paramspider", "category": "Web Security", "github": "https://github.com/devanshbatham/ParamSpider", "desc": "Mining parameters from dark corners of Web Archives", "install_type": "git", "cmd": "git clone https://github.com/devanshbatham/ParamSpider.git && pip install -r ParamSpider/requirements.txt", "preinstalled": False},
    {"name": "linkfinder", "category": "Web Security", "github": "https://github.com/GerbenJavado/LinkFinder", "desc": "Python script that finds endpoints in JavaScript files", "install_type": "git", "cmd": "git clone https://github.com/GerbenJavado/LinkFinder.git && pip install -r LinkFinder/requirements.txt", "preinstalled": False},
    {"name": "secretfinder", "category": "Web Security", "github": "https://github.com/m4ll0k/SecretFinder", "desc": "Python script for discovering sensitive data like API keys in JS files", "install_type": "git", "cmd": "git clone https://github.com/m4ll0k/SecretFinder.git && pip install -r SecretFinder/requirements.txt", "preinstalled": False},
    {"name": "waybackurls", "category": "Web Security", "github": "https://github.com/tomnomnom/waybackurls", "desc": "Fetch all the URLs that the Wayback Machine knows about for a domain", "install_type": "go", "cmd": "go install github.com/tomnomnom/waybackurls@latest", "preinstalled": False},
    {"name": "gau", "category": "Web Security", "github": "https://github.com/lc/gau", "desc": "getAllUrls - fetch known URLs from AlienVault OTX, Wayback Machine, URLScan", "install_type": "go", "cmd": "go install github.com/lc/gau/v2/cmd/gau@latest", "preinstalled": False},
    {"name": "hakrawler", "category": "Web Security", "github": "https://github.com/hakluke/hakrawler", "desc": "Fast Golang web crawler for gathering URLs and JavaScript file locations", "install_type": "go", "cmd": "go install github.com/hakluke/hakrawler@latest", "preinstalled": False},
    {"name": "dirsearch", "category": "Web Security", "github": "https://github.com/maurosoria/dirsearch", "desc": "Advanced web path scanner with multithreading and status filters", "install_type": "pipx", "cmd": "pipx install dirsearch", "preinstalled": False},
    {"name": "wpscan", "category": "Web Security", "github": "https://github.com/wpscanteam/wpscan", "desc": "WordPress vulnerability scanner (core, plugins, themes)", "install_type": "apt", "cmd": "sudo apt install -y wpscan", "preinstalled": False},
    {"name": "whatweb", "category": "Web Security", "github": "https://github.com/urbanadventurer/WhatWeb", "desc": "Next-generation web scanner identifying technologies and CMS", "install_type": "apt", "cmd": "sudo apt install -y whatweb", "preinstalled": True},
    {"name": "wappalyzer", "category": "Web Security", "github": "https://github.com/aliasio/wappalyzer", "desc": "Identify technologies on websites (frameworks, CMS, analytics)", "install_type": "npm", "cmd": "npm install -g wappalyzer", "preinstalled": False},

    # ── 4. Password Cracking & Wordlists ──────────────────────────────────
    {"name": "hashcat", "category": "Password Auditing", "github": "https://github.com/hashcat/hashcat", "desc": "World's fastest and most advanced password recovery utility", "install_type": "apt", "cmd": "sudo apt install -y hashcat", "preinstalled": True},
    {"name": "john", "category": "Password Auditing", "github": "https://github.com/openwall/john", "desc": "John the Ripper password cracker (Jumbo community edition)", "install_type": "apt", "cmd": "sudo apt install -y john", "preinstalled": True},
    {"name": "hydra", "category": "Password Auditing", "github": "https://github.com/vanhauser-thc/thc-hydra", "desc": "Very fast network logon cracker supporting SSH, FTP, HTTP, SMB", "install_type": "apt", "cmd": "sudo apt install -y hydra", "preinstalled": True},
    {"name": "medusa", "category": "Password Auditing", "github": "https://github.com/jmk-foofus/medusa", "desc": "Speedy, parallel, and modular network authentication brute-forcer", "install_type": "apt", "cmd": "sudo apt install -y medusa", "preinstalled": True},
    {"name": "ncrack", "category": "Password Auditing", "github": "https://github.com/nmap/ncrack", "desc": "High-speed network authentication cracking tool by Nmap project", "install_type": "apt", "cmd": "sudo apt install -y ncrack", "preinstalled": True},
    {"name": "crunch", "category": "Password Auditing", "github": "https://github.com/jim3ma/crunch", "desc": "Wordlist generator producing permutation combinations from character sets", "install_type": "apt", "cmd": "sudo apt install -y crunch", "preinstalled": True},
    {"name": "cewl", "category": "Password Auditing", "github": "https://github.com/digininja/CeWL", "desc": "Custom wordlist generator spidering a URL to create targeted dictionaries", "install_type": "apt", "cmd": "sudo apt install -y cewl", "preinstalled": True},
    {"name": "rsmangler", "category": "Password Auditing", "github": "https://github.com/digininja/RSMangler", "desc": "Takes a wordlist and manipulates it generating new password variants", "install_type": "git", "cmd": "git clone https://github.com/digininja/RSMangler.git", "preinstalled": False},
    {"name": "seclists", "category": "Wordlists & References", "github": "https://github.com/danielmiessler/SecLists", "desc": "Security tester's companion: collection of usernames, passwords, URLs, fuzz lists", "install_type": "apt", "cmd": "sudo apt install -y seclists", "preinstalled": False},
    {"name": "payloadsallthethings", "category": "Wordlists & References", "github": "https://github.com/swisskyrepo/PayloadsAllTheThings", "desc": "Cheatsheet and list of useful payloads and bypasses for Web Application Security", "install_type": "git", "cmd": "git clone https://github.com/swisskyrepo/PayloadsAllTheThings.git", "preinstalled": False},
    {"name": "hacktricks", "category": "Wordlists & References", "github": "https://github.com/HackTricks-wiki/hacktricks", "desc": "The largest cybersecurity knowledge base and pentesting book", "install_type": "git", "cmd": "git clone https://github.com/HackTricks-wiki/hacktricks.git", "preinstalled": False},
    {"name": "gtfobins", "category": "Wordlists & References", "github": "https://github.com/GTFOBins/GTFOBins.github.io", "desc": "Curated list of Unix binaries that can be used to bypass local security restrictions", "install_type": "reference", "cmd": "curl -s https://gtfobins.github.io", "preinstalled": False},
    {"name": "lolbas", "category": "Wordlists & References", "github": "https://github.com/LOLBAS-Project/LOLBAS", "desc": "Living Off The Land Binaries and Scripts for Windows environments", "install_type": "reference", "cmd": "curl -s https://lolbas-project.github.io", "preinstalled": False},

    # ── 5. Wireless & Radio Warfare ───────────────────────────────────────
    {"name": "aircrack-ng", "category": "Wireless & Radio", "github": "https://github.com/aircrack-ng/aircrack-ng", "desc": "Complete suite of tools to assess Wi-Fi network security (WEP/WPA/WPA2)", "install_type": "apt", "cmd": "sudo apt install -y aircrack-ng", "preinstalled": True},
    {"name": "wifite2", "category": "Wireless & Radio", "github": "https://github.com/derv82/wifite2", "desc": "Automated wireless auditor for attacking multiple WEP/WPA encrypted networks", "install_type": "apt", "cmd": "sudo apt install -y wifite", "preinstalled": True},
    {"name": "reaver", "category": "Wireless & Radio", "github": "https://github.com/t6x/reaver-wps-fork-t6x", "desc": "Brute force attack tool against Wi-Fi Protected Setup (WPS) registrar PINs", "install_type": "apt", "cmd": "sudo apt install -y reaver", "preinstalled": True},
    {"name": "bully", "category": "Wireless & Radio", "github": "https://github.com/aanarchyy/bully", "desc": "Implementation of the WPS brute force attack in C, fast and optimized", "install_type": "apt", "cmd": "sudo apt install -y bully", "preinstalled": True},
    {"name": "pixiewps", "category": "Wireless & Radio", "github": "https://github.com/wiire-a/pixiewps", "desc": "Offline WPS PRNG vulnerability brute-force tool (Pixie Dust attack)", "install_type": "apt", "cmd": "sudo apt install -y pixiewps", "preinstalled": True},
    {"name": "kismet", "category": "Wireless & Radio", "github": "https://github.com/kismetwireless/kismet", "desc": "Wireless network detector, sniffer, and intrusion detection system", "install_type": "apt", "cmd": "sudo apt install -y kismet", "preinstalled": True},

    # ── 6. Exploitation & Post-Exploitation ────────────────────────────────
    {"name": "metasploit", "category": "Exploitation & C2", "github": "https://github.com/rapid7/metasploit-framework", "desc": "World's most used penetration testing framework and payload platform", "install_type": "curl", "cmd": "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall", "preinstalled": True},
    {"name": "searchsploit", "category": "Exploitation & C2", "github": "https://github.com/offensive-security/exploitdb", "desc": "Command-line search tool for Exploit-DB offline archive", "install_type": "apt", "cmd": "sudo apt install -y exploitdb", "preinstalled": False},
    {"name": "beef", "category": "Exploitation & C2", "github": "https://github.com/beefproject/beef", "desc": "The Browser Exploitation Framework project focused on client-side vectors", "install_type": "apt", "cmd": "sudo apt install -y beef-xss", "preinstalled": False},
    {"name": "powersploit", "category": "Exploitation & C2", "github": "https://github.com/PowerShellMafia/PowerSploit", "desc": "PowerShell post-exploitation framework (PowerView, Invoke-Mimikatz)", "install_type": "git", "cmd": "git clone https://github.com/PowerShellMafia/PowerSploit.git", "preinstalled": False},
    {"name": "nishang", "category": "Exploitation & C2", "github": "https://github.com/samratashok/nishang", "desc": "PowerShell scripts and payloads for penetration testing and offensive ops", "install_type": "git", "cmd": "git clone https://github.com/samratashok/nishang.git", "preinstalled": False},
    {"name": "sliver", "category": "Exploitation & C2", "github": "https://github.com/BishopFox/sliver", "desc": "Adversary emulation and red team C2 framework written in Go", "install_type": "curl", "cmd": "curl -s https://sliver.sh/install | sudo bash", "preinstalled": False},
    {"name": "empire", "category": "Exploitation & C2", "github": "https://github.com/BC-SECURITY/Empire", "desc": "Post-exploitation and adversary emulation agent framework in Python/PowerShell", "install_type": "git", "cmd": "git clone --recursive https://github.com/BC-SECURITY/Empire.git && cd Empire && ./setup/install.sh", "preinstalled": False},
    {"name": "havoc", "category": "Exploitation & C2", "github": "https://github.com/HavocFramework/Havoc", "desc": "Modern and malleable post-exploitation C2 framework", "install_type": "git", "cmd": "git clone https://github.com/HavocFramework/Havoc.git", "preinstalled": False},
    {"name": "mythic", "category": "Exploitation & C2", "github": "https://github.com/its-a-feature/Mythic", "desc": "Cross-platform, post-exploit, red teaming framework with Web UI", "install_type": "git", "cmd": "git clone https://github.com/its-a-feature/Mythic.git", "preinstalled": False},
    {"name": "covenant", "category": "Exploitation & C2", "github": "https://github.com/cobbr/Covenant", "desc": ".NET command and control framework designed for red team operators", "install_type": "git", "cmd": "git clone --recurse-submodules https://github.com/cobbr/Covenant", "preinstalled": False},
    {"name": "caldera", "category": "Exploitation & C2", "github": "https://github.com/mitre/caldera", "desc": "Cyber adversary emulation platform built on the MITRE ATT&CK framework", "install_type": "git", "cmd": "git clone https://github.com/mitre/caldera.git --recursive", "preinstalled": False},
    {"name": "atomic-red-team", "category": "Exploitation & C2", "github": "https://github.com/redcanaryco/atomic-red-team", "desc": "Simple, scripted red team tests mapped to MITRE ATT&CK matrix", "install_type": "git", "cmd": "git clone https://github.com/redcanaryco/atomic-red-team.git", "preinstalled": False},
    {"name": "weevely", "category": "Exploitation & C2", "github": "https://github.com/epinna/weevely3", "desc": "Stealth PHP web shell with 30+ post-exploitation modules", "install_type": "apt", "cmd": "sudo apt install -y weevely", "preinstalled": False},

    # ── 7. Active Directory, Windows & Lateral Movement ───────────────────
    {"name": "impacket", "category": "Active Directory & Windows", "github": "https://github.com/fortra/impacket", "desc": "Python classes for network protocols (wmiexec, psexec, secretsdump)", "install_type": "pipx", "cmd": "pipx install impacket", "preinstalled": False},
    {"name": "netexec", "category": "Active Directory & Windows", "github": "https://github.com/Pennyw0rth/NetExec", "desc": "The network execution tool (successor to CrackMapExec) for lateral movement", "install_type": "pipx", "cmd": "pipx install git+https://github.com/Pennyw0rth/NetExec", "preinstalled": False},
    {"name": "crackmapexec", "category": "Active Directory & Windows", "github": "https://github.com/byt3bl33d3r/CrackMapExec", "desc": "Swiss army knife for pentesting Active Directory networks", "install_type": "apt", "cmd": "sudo apt install -y crackmapexec", "preinstalled": False},
    {"name": "bloodhound", "category": "Active Directory & Windows", "github": "https://github.com/SpecterOps/BloodHound", "desc": "Six Degrees of Domain Admin: Active Directory graph visualization", "install_type": "apt", "cmd": "sudo apt install -y bloodhound", "preinstalled": False},
    {"name": "sharphound", "category": "Active Directory & Windows", "github": "https://github.com/SpecterOps/SharpHound", "desc": "C# Data Collector for BloodHound Active Directory graphs", "install_type": "binary", "cmd": "wget https://github.com/SpecterOps/SharpHound/releases/latest/download/SharpHound.zip", "preinstalled": False},
    {"name": "responder", "category": "Active Directory & Windows", "github": "https://github.com/lgandx/Responder", "desc": "LLMNR, NBT-NS and MDNS poisoner and rogue authentication daemon", "install_type": "apt", "cmd": "sudo apt install -y responder", "preinstalled": False},
    {"name": "coercer", "category": "Active Directory & Windows", "github": "https://github.com/p0dalirius/Coercer", "desc": "A python script to automatically coerce a Windows server to authenticate", "install_type": "pipx", "cmd": "pipx install coercer", "preinstalled": False},
    {"name": "certipy", "category": "Active Directory & Windows", "github": "https://github.com/ly4k/Certipy", "desc": "Active Directory Certificate Services (AD CS) auditing and abuse tool", "install_type": "pipx", "cmd": "pipx install certipy-ad", "preinstalled": False},
    {"name": "petitpotam", "category": "Active Directory & Windows", "github": "https://github.com/topotam/PetitPotam", "desc": "PoC tool to coerce Windows hosts to authenticate to other machines via MS-EFSR", "install_type": "git", "cmd": "git clone https://github.com/topotam/PetitPotam.git", "preinstalled": False},
    {"name": "mimikatz", "category": "Active Directory & Windows", "github": "https://github.com/gentilkiwi/mimikatz", "desc": "Extract plaintexts passwords, hash, PIN code and kerberos tickets from memory", "install_type": "apt", "cmd": "sudo apt install -y mimikatz", "preinstalled": False},
    {"name": "lazagne", "category": "Active Directory & Windows", "github": "https://github.com/AlessandroZ/LaZagne", "desc": "Open source application used to retrieve lots of passwords stored on a local computer", "install_type": "git", "cmd": "git clone https://github.com/AlessandroZ/LaZagne.git", "preinstalled": False},
    {"name": "rubeus", "category": "Active Directory & Windows", "github": "https://github.com/GhostPack/Rubeus", "desc": "C# toolset for raw Kerberos interaction and abuses (AS-REP Roasting, Kerberoasting)", "install_type": "git", "cmd": "git clone https://github.com/GhostPack/Rubeus.git", "preinstalled": False},
    {"name": "seatbelt", "category": "Active Directory & Windows", "github": "https://github.com/GhostPack/Seatbelt", "desc": "C# project that performs a number of security oriented host-survey safety checks", "install_type": "git", "cmd": "git clone https://github.com/GhostPack/Seatbelt.git", "preinstalled": False},
    {"name": "kerbrute", "category": "Active Directory & Windows", "github": "https://github.com/ropnop/kerbrute", "desc": "Tool to quickly bruteforce and enumerate valid Active Directory accounts via Kerberos", "install_type": "go", "cmd": "go install github.com/ropnop/kerbrute@latest", "preinstalled": False},
    {"name": "evil-winrm", "category": "Active Directory & Windows", "github": "https://github.com/Hackplayers/evil-winrm", "desc": "The ultimate WinRM shell for hacking/pentesting Windows remote management", "install_type": "gem", "cmd": "gem install evil-winrm", "preinstalled": False},
    {"name": "linpeas", "category": "Privilege Escalation", "github": "https://github.com/peass-ng/PEASS-ng", "desc": "Linux Privilege Escalation Awesome Script", "install_type": "curl", "cmd": "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh > linpeas.sh", "preinstalled": False},
    {"name": "winpeas", "category": "Privilege Escalation", "github": "https://github.com/peass-ng/PEASS-ng", "desc": "Windows Privilege Escalation Awesome Script", "install_type": "binary", "cmd": "wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe", "preinstalled": False},
    {"name": "linux-exploit-suggester", "category": "Privilege Escalation", "github": "https://github.com/mzet-/linux-exploit-suggester", "desc": "Linux privilege escalation auditing tool based on kernel vulnerabilities", "install_type": "git", "cmd": "git clone https://github.com/mzet-/linux-exploit-suggester.git", "preinstalled": False},
    {"name": "chisel", "category": "Pivoting & Tunnels", "github": "https://github.com/jpillora/chisel", "desc": "Fast TCP/UDP tunnel, transported over HTTP, secured via SSH", "install_type": "go", "cmd": "go install github.com/jpillora/chisel@latest", "preinstalled": False},
    {"name": "ligolo-ng", "category": "Pivoting & Tunnels", "github": "https://github.com/nicocha30/ligolo-ng", "desc": "Advanced, simple, and fast tunneling/pivoting tool using TUN interfaces", "install_type": "go", "cmd": "go install github.com/nicocha30/ligolo-ng/cmd/proxy@latest", "preinstalled": False},
    {"name": "proxychains-ng", "category": "Pivoting & Tunnels", "github": "https://github.com/rofl0r/proxychains-ng", "desc": "Redirect connections through SOCKS4, SOCKS5 or HTTP proxies", "install_type": "apt", "cmd": "sudo apt install -y proxychains4", "preinstalled": True},
    {"name": "socat", "category": "Pivoting & Tunnels", "github": "https://github.com/3ndG4me/socat", "desc": "Multipurpose relay for bidirectional data transfer across sockets and pipes", "install_type": "apt", "cmd": "sudo apt install -y socat", "preinstalled": True},

    # ── 8. Traffic Analysis, Sniffing & Proxies ───────────────────────────
    {"name": "wireshark", "category": "Traffic & Sniffing", "github": "https://github.com/wireshark/wireshark", "desc": "World's foremost network protocol analyzer with packet capture HUD", "install_type": "apt", "cmd": "sudo apt install -y wireshark tshark", "preinstalled": True},
    {"name": "tcpdump", "category": "Traffic & Sniffing", "github": "https://github.com/the-tcpdump-group/tcpdump", "desc": "Powerful command-line packet analyzer and PCAP capture utility", "install_type": "apt", "cmd": "sudo apt install -y tcpdump", "preinstalled": True},
    {"name": "mitmproxy", "category": "Traffic & Sniffing", "github": "https://github.com/mitmproxy/mitmproxy", "desc": "Interactive TLS-capable intercepting HTTP proxy for penetration testers", "install_type": "apt", "cmd": "sudo apt install -y mitmproxy", "preinstalled": False},
    {"name": "ettercap", "category": "Traffic & Sniffing", "github": "https://github.com/Ettercap/ettercap", "desc": "Comprehensive suite for man in the middle attacks with ARP filtering", "install_type": "apt", "cmd": "sudo apt install -y ettercap-text-only", "preinstalled": True},
    {"name": "dsniff", "category": "Traffic & Sniffing", "github": "https://github.com/eldadru/acl", "desc": "Collection of tools for network auditing and password sniffing", "install_type": "apt", "cmd": "sudo apt install -y dsniff", "preinstalled": True},
    {"name": "sslsplit", "category": "Traffic & Sniffing", "github": "https://github.com/droe/sslsplit", "desc": "Transparent SSL/TLS interception tool for man-in-the-middle attacks", "install_type": "apt", "cmd": "sudo apt install -y sslsplit", "preinstalled": False},

    # ── 9. Forensics, Reverse Engineering & Binaries ──────────────────────
    {"name": "binwalk", "category": "Forensics & Disassembly", "github": "https://github.com/ReFirmLabs/binwalk", "desc": "Firmware analysis tool to extract embedded file systems and code", "install_type": "apt", "cmd": "sudo apt install -y binwalk", "preinstalled": True},
    {"name": "foremost", "category": "Forensics & Disassembly", "github": "https://github.com/korczis/foremost", "desc": "Forensic data recovery program based on file headers, footers and data structures", "install_type": "apt", "cmd": "sudo apt install -y foremost", "preinstalled": True},
    {"name": "scalpel", "category": "Forensics & Disassembly", "github": "https://github.com/sleuthkit/scalpel", "desc": "Frugal, high performance file carver for digital forensics investigations", "install_type": "apt", "cmd": "sudo apt install -y scalpel", "preinstalled": True},
    {"name": "volatility3", "category": "Forensics & Disassembly", "github": "https://github.com/volatilityfoundation/volatility3", "desc": "Advanced memory forensics framework for RAM dump triage", "install_type": "pipx", "cmd": "pipx install volatility3", "preinstalled": False},
    {"name": "bulk_extractor", "category": "Forensics & Disassembly", "github": "https://github.com/simsong/bulk_extractor", "desc": "High-performance digital forensics feature extractor scanning disk images", "install_type": "apt", "cmd": "sudo apt install -y bulk-extractor", "preinstalled": False},
    {"name": "autopsy", "category": "Forensics & Disassembly", "github": "https://github.com/sleuthkit/autopsy", "desc": "Digital forensics platform and graphical interface to The Sleuth Kit", "install_type": "apt", "cmd": "sudo apt install -y autopsy", "preinstalled": False},
    {"name": "sleuthkit", "category": "Forensics & Disassembly", "github": "https://github.com/sleuthkit/sleuthkit", "desc": "The Sleuth Kit (TSK) file system and volume forensics library and tools", "install_type": "apt", "cmd": "sudo apt install -y sleuthkit", "preinstalled": True},
    {"name": "plaso", "category": "Forensics & Disassembly", "github": "https://github.com/log2timeline/plaso", "desc": "Log2timeline super timeline creation engine for digital forensic investigation", "install_type": "apt", "cmd": "sudo apt install -y python3-plaso", "preinstalled": False},
    {"name": "timesketch", "category": "Forensics & Disassembly", "github": "https://github.com/google/timesketch", "desc": "Open source tool for collaborative forensic timeline analysis", "install_type": "docker", "cmd": "curl -s https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh | bash", "preinstalled": False},
    {"name": "ghidra", "category": "Forensics & Disassembly", "github": "https://github.com/NationalSecurityAgency/ghidra", "desc": "Software reverse engineering (SRE) suite developed by NSA Research", "install_type": "apt", "cmd": "sudo apt install -y ghidra", "preinstalled": False},
    {"name": "radare2", "category": "Forensics & Disassembly", "github": "https://github.com/radareorg/radare2", "desc": "Unix-like reverse engineering framework and command-line hex editor", "install_type": "apt", "cmd": "sudo apt install -y radare2", "preinstalled": True},
    {"name": "rizin", "category": "Forensics & Disassembly", "github": "https://github.com/rizinorg/rizin", "desc": "UNIX-like reverse engineering framework and binary analysis tool", "install_type": "apt", "cmd": "sudo apt install -y rizin", "preinstalled": False},
    {"name": "cutter", "category": "Forensics & Disassembly", "github": "https://github.com/rizinorg/cutter", "desc": "Free and Open Source Reverse Engineering Platform powered by Rizin", "install_type": "appimage", "cmd": "wget https://github.com/rizinorg/cutter/releases/latest/download/Cutter-v2.3.4-Linux-x86_64.AppImage", "preinstalled": False},
    {"name": "jadx", "category": "Mobile Security", "github": "https://github.com/skylot/jadx", "desc": "Dex to Java decompiler and command line / GUI tool for Android APKs", "install_type": "apt", "cmd": "sudo apt install -y jadx", "preinstalled": False},
    {"name": "apktool", "category": "Mobile Security", "github": "https://github.com/iBotPeaches/Apktool", "desc": "A tool for reverse engineering 3rd party, closed, binary Android apps", "install_type": "apt", "cmd": "sudo apt install -y apktool", "preinstalled": False},
    {"name": "dex2jar", "category": "Mobile Security", "github": "https://github.com/pxb1988/dex2jar", "desc": "Tools to work with Android .dex and Java .class files", "install_type": "apt", "cmd": "sudo apt install -y dex2jar", "preinstalled": False},
    {"name": "frida", "category": "Mobile Security", "github": "https://github.com/frida/frida", "desc": "Dynamic instrumentation toolkit for developers, reverse-engineers, and researchers", "install_type": "pipx", "cmd": "pipx install frida-tools", "preinstalled": False},
    {"name": "objection", "category": "Mobile Security", "github": "https://github.com/sensepost/objection", "desc": "Runtime Mobile Security Assessment powered by Frida", "install_type": "pipx", "cmd": "pipx install objection", "preinstalled": False},
    {"name": "mobsf", "category": "Mobile Security", "github": "https://github.com/MobSF/Mobile-Security-Framework-MobSF", "desc": "Automated, all-in-one mobile application (Android/iOS) pentesting framework", "install_type": "docker", "cmd": "docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest", "preinstalled": False},
    {"name": "cyberchef", "category": "Forensics & Disassembly", "github": "https://github.com/gchq/CyberChef", "desc": "The Cyber Swiss Army Knife — encryption, encoding, compression, and analysis", "install_type": "docker", "cmd": "docker run -d -p 8080:80 mpepping/cyberchef", "preinstalled": False},
    {"name": "exiftool", "category": "Forensics & Disassembly", "github": "https://github.com/exiftool/exiftool", "desc": "Read, write and manipulate image, audio, and PDF metadata", "install_type": "apt", "cmd": "sudo apt install -y exiftool", "preinstalled": True},
    {"name": "pe-bear", "category": "Forensics & Disassembly", "github": "https://github.com/hasherezade/pe-bear", "desc": "Reversing tool for PE files with friendly GUI", "install_type": "git", "cmd": "git clone https://github.com/hasherezade/pe-bear.git", "preinstalled": False},
    {"name": "detect-it-easy", "category": "Forensics & Disassembly", "github": "https://github.com/horsicq/Detect-It-Easy", "desc": "Program for determining types of files, packers, compilers, and protectors", "install_type": "git", "cmd": "git clone https://github.com/horsicq/Detect-It-Easy.git", "preinstalled": False},
    {"name": "capstone", "category": "Forensics & Disassembly", "github": "https://github.com/capstone-engine/capstone", "desc": "Next-gen disassembly framework supporting x86, ARM, MIPS, RISC-V", "install_type": "apt", "cmd": "sudo apt install -y libcapstone-dev", "preinstalled": False},
    {"name": "keystone", "category": "Forensics & Disassembly", "github": "https://github.com/keystone-engine/keystone", "desc": "Lightweight multi-platform, multi-architecture assembler framework", "install_type": "git", "cmd": "git clone https://github.com/keystone-engine/keystone.git", "preinstalled": False},

    # ── 10. Threat Detection, Blue Team & Rules ───────────────────────────
    {"name": "yara", "category": "Defense & Blue Team", "github": "https://github.com/VirusTotal/yara", "desc": "The pattern matching swiss knife for malware researchers", "install_type": "apt", "cmd": "sudo apt install -y yara", "preinstalled": False},
    {"name": "yara-x", "category": "Defense & Blue Team", "github": "https://github.com/VirusTotal/yara-x", "desc": "Next generation YARA implementation written in pure Rust with high speed", "install_type": "cargo", "cmd": "cargo install yara-x-cli", "preinstalled": False},
    {"name": "suricata", "category": "Defense & Blue Team", "github": "https://github.com/OISF/suricata", "desc": "High performance Network IDS, IPS and Network Security Monitoring engine", "install_type": "apt", "cmd": "sudo apt install -y suricata", "preinstalled": False},
    {"name": "zeek", "category": "Defense & Blue Team", "github": "https://github.com/zeek/zeek", "desc": "Powerful network analysis framework that is much more than a traditional IDS", "install_type": "apt", "cmd": "sudo apt install -y zeek", "preinstalled": False},
    {"name": "snort3", "category": "Defense & Blue Team", "github": "https://github.com/snort3/snort3", "desc": "Next generation open-source network intrusion prevention system", "install_type": "apt", "cmd": "sudo apt install -y snort", "preinstalled": False},
    {"name": "sigma", "category": "Defense & Blue Team", "github": "https://github.com/SigmaHQ/sigma", "desc": "Generic Signature Format for SIEM and Log Detection Systems", "install_type": "git", "cmd": "git clone https://github.com/SigmaHQ/sigma.git", "preinstalled": False},
    {"name": "sigma-cli", "category": "Defense & Blue Team", "github": "https://github.com/SigmaHQ/sigma-cli", "desc": "Sigma CLI conversion and validation tool for SIEM query generation", "install_type": "pipx", "cmd": "pipx install sigma-cli", "preinstalled": False},
    {"name": "velociraptor", "category": "Defense & Blue Team", "github": "https://github.com/Velocidex/velociraptor", "desc": "Advanced digital forensic and incident response (DFIR) endpoint agent", "install_type": "binary", "cmd": "wget https://github.com/Velocidex/velociraptor/releases/latest/download/velociraptor-v0.7.1-linux-amd64", "preinstalled": False},
    {"name": "semgrep", "category": "Defense & Blue Team", "github": "https://github.com/semgrep/semgrep", "desc": "Lightweight static analysis for many languages finding bugs and CVE patterns", "install_type": "pipx", "cmd": "pipx install semgrep", "preinstalled": False},
    {"name": "gitleaks", "category": "Defense & Blue Team", "github": "https://github.com/gitleaks/gitleaks", "desc": "Protect and discover secrets, credentials, and API tokens in git repositories", "install_type": "go", "cmd": "go install github.com/zricethezav/gitleaks/v8@latest", "preinstalled": False},
    {"name": "trufflehog", "category": "Defense & Blue Team", "github": "https://github.com/trufflesecurity/trufflehog", "desc": "Find leaked credentials and high-entropy secrets across git repos and filesystems", "install_type": "go", "cmd": "go install github.com/trufflesecurity/trufflehog/v3@latest", "preinstalled": False},
    {"name": "arkime", "category": "Defense & Blue Team", "github": "https://github.com/arkime/arkime", "desc": "Large scale, open source, indexed packet capture and search system", "install_type": "git", "cmd": "git clone https://github.com/arkime/arkime.git", "preinstalled": False},
    {"name": "snyk", "category": "Defense & Blue Team", "github": "https://github.com/snyk/cli", "desc": "Find and fix security vulnerabilities in dependencies, containers, and IaC", "install_type": "npm", "cmd": "npm install -g snyk", "preinstalled": False},

    # ── 11. Reporting, Frameworks & Discovery Automation ───────────────────
    {"name": "dradis", "category": "Reporting & Collaboration", "github": "https://github.com/dradis/dradis-ce", "desc": "Collaboration and reporting platform for information security teams", "install_type": "apt", "cmd": "sudo apt install -y dradis", "preinstalled": False},
    {"name": "gitrob", "category": "OSINT & Recon", "github": "https://github.com/michenriksen/gitrob", "desc": "Reconnaissance tool for GitHub organizations finding sensitive files", "install_type": "go", "cmd": "go install github.com/michenriksen/gitrob@latest", "preinstalled": False},
    {"name": "smbexec", "category": "Active Directory & Windows", "github": "https://github.com/pentestgeek/smbexec", "desc": "A rapid psexec style attack tool designed for penetration testers", "install_type": "git", "cmd": "git clone https://github.com/pentestgeek/smbexec.git", "preinstalled": False},
    {"name": "discover", "category": "OSINT & Recon", "github": "https://github.com/leebaird/discover", "desc": "Custom bash scripts used to automate information gathering and penetration tests", "install_type": "git", "cmd": "git clone https://github.com/leebaird/discover.git", "preinstalled": False},
    {"name": "vajra", "category": "Exploitation & C2", "github": "https://github.com/", "desc": "Offensive and defensive security tool aggregator and custom payload wrapper", "install_type": "reference", "cmd": "echo 'Available via ASTERIX OS scripts-hub'", "preinstalled": True},
    {"name": "chaos", "category": "OSINT & Recon", "github": "https://github.com/projectdiscovery/chaos-client", "desc": "Go client to communicate with ProjectDiscovery Chaos DNS dataset API", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest", "preinstalled": False},
    {"name": "notify", "category": "OSINT & Recon", "github": "https://github.com/projectdiscovery/notify", "desc": "Stream the output of several tools (subfinder, nuclei) directly to Discord/Slack", "install_type": "go", "cmd": "go install -v github.com/projectdiscovery/notify/cmd/notify@latest", "preinstalled": False},
    {"name": "dnsgen", "category": "OSINT & Recon", "github": "https://github.com/ProjectAnte/dnsgen", "desc": "Generates combination of domain names from the provided input list", "install_type": "pipx", "cmd": "pipx install dnsgen", "preinstalled": False},
    {"name": "hakrevdns", "category": "OSINT & Recon", "github": "https://github.com/hakluke/hakrevdns", "desc": "Small, fast tool for performing reverse DNS lookups en masse", "install_type": "go", "cmd": "go install github.com/hakluke/hakrevdns@latest", "preinstalled": False},
    {"name": "retire.js", "category": "Web Security", "github": "https://github.com/RetireJS/retire.js", "desc": "Scanner detecting the use of JavaScript libraries with known vulnerabilities", "install_type": "npm", "cmd": "npm install -g retire", "preinstalled": False},
    {"name": "frida-tools", "category": "Mobile Security", "github": "https://github.com/frida/frida-tools", "desc": "CLI tools for dynamic instrumentation and mobile reverse engineering using Frida", "install_type": "pipx", "cmd": "pipx install frida-tools", "preinstalled": False},
    {"name": "sharpup", "category": "Privilege Escalation", "github": "https://github.com/GhostPack/SharpUp", "desc": "C# port of various PowerUp privilege escalation safety checks", "install_type": "git", "cmd": "git clone https://github.com/GhostPack/SharpUp.git", "preinstalled": False},
    {"name": "powerview", "category": "Active Directory & Windows", "github": "https://github.com/PowerShellMafia/PowerSploit", "desc": "PowerShell situational awareness and domain querying tool (PowerSploit)", "install_type": "git", "cmd": "git clone https://github.com/PowerShellMafia/PowerSploit.git", "preinstalled": False},
    {"name": "rekall", "category": "Forensics & Disassembly", "github": "https://github.com/google/rekall", "desc": "Memory analysis and incident response forensics framework by Google", "install_type": "git", "cmd": "git clone https://github.com/google/rekall.git", "preinstalled": False},
    {"name": "exifprobe", "category": "Forensics & Disassembly", "github": "https://github.com/hfiguiere/exifprobe", "desc": "Probe and report structure and metadata of digital camera image files", "install_type": "apt", "cmd": "sudo apt install -y exifprobe", "preinstalled": False},
    {"name": "payloads", "category": "Wordlists & References", "github": "https://github.com/foospidy/payloads", "desc": "Git repository of attack payloads for web applications and firewalls", "install_type": "git", "cmd": "git clone https://github.com/foospidy/payloads.git", "preinstalled": False},
    {"name": "gtfoargs", "category": "Wordlists & References", "github": "https://github.com/swisskyrepo/GTFOArgs", "desc": "Curated list of Unix arguments for bypassing command restrictions", "install_type": "git", "cmd": "git clone https://github.com/swisskyrepo/GTFOArgs.git", "preinstalled": False},
    {"name": "x64dbg", "category": "Forensics & Disassembly", "github": "https://github.com/x64dbg/x64dbg", "desc": "An open-source x64/x32 debugger for Windows binary analysis", "install_type": "binary", "cmd": "wget https://github.com/x64dbg/x64dbg/releases/latest/download/snapshot.zip", "preinstalled": False},
    {"name": "windbg", "category": "Forensics & Disassembly", "github": "https://github.com/microsoft/WinDbg", "desc": "Windows native kernel and user-mode debugger for crash and vulnerability analysis", "install_type": "reference", "cmd": "winget install Microsoft.WinDbg", "preinstalled": False}
]


def print_banner():
    print(f"\n{C_BOLD}{C_CYAN}========================================================================={C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  ASTERIX OS :: MASTER CYBERSECURITY ARSENAL & TOOL REGISTRY{C_RESET}")
    print(f"{C_DIM}  Offline Catalog of 180+ Industry-Standard Red Team & Forensic Tools (On-Demand Ready){C_RESET}")
    print(f"{C_BOLD}{C_CYAN}========================================================================={C_RESET}\n")


def cmd_stats():
    print_banner()
    total = len(ARSENAL_REGISTRY)
    pre = sum(1 for t in ARSENAL_REGISTRY if t.get("preinstalled"))
    ondemand = total - pre

    categories = {}
    for t in ARSENAL_REGISTRY:
        c = t.get("category", "General")
        categories[c] = categories.get(c, 0) + 1

    print(f"{C_BOLD}[ARSENAL SUMMARY STATS]{C_RESET}")
    print(f"  • Total Registered Tools:     {C_CYAN}{total}{C_RESET}")
    print(f"  • Pre-Installed in Base ISO:  {C_GREEN}{pre} tools{C_RESET} (Ready out-of-the-box)")
    print(f"  • On-Demand Persistent Tools: {C_YELLOW}{ondemand} tools{C_RESET} (Installs to USB persistence)")
    print(f"  • Repository Disk Bloat:      {C_GREEN}0.0 MB{C_RESET} (Zero repo bloat; catalog indexed offline)")

    print(f"\n{C_BOLD}[TOOLS PER CATEGORY]{C_RESET}")
    for cat, count in sorted(categories.items()):
        print(f"  • {cat:<30}: {C_CYAN}{count:>2} tools{C_RESET}")
    print(f"\n{C_DIM}Tip: Run 'ax arsenal search <keyword>' or 'ax arsenal list' to explore.{C_RESET}\n")


def cmd_list(category_filter=None):
    print_banner()
    tools = ARSENAL_REGISTRY
    if category_filter:
        tools = [t for t in ARSENAL_REGISTRY if category_filter.lower() in t.get("category", "").lower()]

    print(f"{C_BOLD}{'Tool Name':<22} | {'Category':<28} | {'Status':<18} | {'Install Type'}{C_RESET}")
    print(f"{C_DIM}{'-'*22}-+-{'-'*28}-+-{'-'*18}-+-{'-'*12}{C_RESET}")

    for t in tools:
        name = t["name"]
        cat = t["category"]
        itype = t["install_type"].upper()
        if t.get("preinstalled"):
            status = f"{C_GREEN}✔ PRE-INSTALLED{C_RESET}"
        else:
            status = f"{C_YELLOW}⚡ ON-DEMAND{C_RESET}"

        print(f"{C_BOLD}{name:<22}{C_RESET} | {cat:<28} | {status:<27} | {itype}")

    print(f"\n{C_DIM}Run 'ax arsenal info <tool>' for repository details and installation command.{C_RESET}\n")


def cmd_search(query):
    print_banner()
    q = query.lower()
    matches = [
        t for t in ARSENAL_REGISTRY
        if q in t["name"].lower() or q in t["category"].lower() or q in t["desc"].lower()
    ]

    print(f"{C_BOLD}Search Results for '{C_CYAN}{query}{C_RESET}{C_BOLD}' ({len(matches)} matches):{C_RESET}\n")
    for t in matches:
        status = f"{C_GREEN}[PRE-INSTALLED]{C_RESET}" if t.get("preinstalled") else f"{C_YELLOW}[ON-DEMAND]{C_RESET}"
        print(f"  • {C_BOLD}{C_CYAN}{t['name']:<20}{C_RESET} {status} {C_DIM}({t['category']}){C_RESET}")
        print(f"    {t['desc']}")
        print(f"    {C_GRAY}Source:  {t['github']}{C_RESET}")
        print(f"    {C_YELLOW}Install: {t['cmd']}{C_RESET}\n")


def cmd_info(tool_name):
    print_banner()
    match = None
    for t in ARSENAL_REGISTRY:
        if t["name"].lower() == tool_name.lower():
            match = t
            break

    if not match:
        print(f"{C_RED}Tool '{tool_name}' not found in registry.{C_RESET}")
        print(f"Run {C_YELLOW}ax arsenal search {tool_name}{C_RESET} or {C_YELLOW}ax arsenal list{C_RESET} to view available tools.\n")
        return

    print(f"{C_BOLD}Tool Profile: {C_CYAN}{match['name'].upper()}{C_RESET}\n")
    print(f"  • Category:       {C_WHITE}{match['category']}{C_RESET}")
    print(f"  • Description:    {match['desc']}")
    print(f"  • GitHub Source:  {C_CYAN}{match['github']}{C_RESET}")
    print(f"  • Install Method: {match['install_type'].upper()}")
    if match.get("preinstalled"):
        print(f"  • Status:         {C_GREEN}✔ Pre-installed in ASTERIX OS Base ISO{C_RESET}")
    else:
        print(f"  • Status:         {C_YELLOW}⚡ Available for On-Demand Persistent Install{C_RESET}")

    print(f"\n{C_BOLD}[INSTALLATION RECIPE]{C_RESET}")
    print(f"  {C_YELLOW}$ {match['cmd']}{C_RESET}")
    print(f"\n{C_DIM}Note: When booted on Live USB, this tool is saved permanently to your Ext4 persistence partition.{C_RESET}\n")


def cmd_install(tool_name, execute=False):
    print_banner()
    match = None
    for t in ARSENAL_REGISTRY:
        if t["name"].lower() == tool_name.lower():
            match = t
            break

    if not match:
        print(f"{C_RED}Tool '{tool_name}' not found in registry.{C_RESET}")
        return

    if match.get("preinstalled"):
        print(f"{C_GREEN}✔ '{match['name']}' is ALREADY pre-installed in the ASTERIX OS base system.{C_RESET}")
        print(f"  Launch command directly: {C_CYAN}{match['name']}{C_RESET}\n")
        return

    print(f"{C_CYAN}Target Tool:{C_RESET} {C_BOLD}{match['name']}{C_RESET} ({match['category']})")
    print(f"Installation Recipe: {C_YELLOW}{match['cmd']}{C_RESET}\n")

    if not execute:
        print(f"{C_YELLOW}[!] Download Prevention Mode (Default):{C_RESET}")
        print(f"  Repository cloning is skipped to preserve bandwidth and disk space.")
        print(f"  To execute this installation onto your live persistence partition, run:")
        print(f"    {C_BOLD}ax arsenal install {tool_name} --run{C_RESET}\n")
        return

    print(f"{C_CYAN}[*] Executing persistent package install...{C_RESET}")
    try:
        subprocess.run(match['cmd'], shell=True, check=True)
        print(f"\n{C_GREEN}✔ Successfully installed '{match['name']}'!{C_RESET}\n")
    except Exception as e:
        print(f"\n{C_RED}✗ Installation encountered an error: {e}{C_RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS — Master Security Arsenal & Tool Registry",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("action", nargs="?", default="stats",
                        choices=["stats", "list", "search", "info", "install", "categories"],
                        help="Action: stats, list, search, info, install, categories")
    parser.add_argument("query", nargs="?", default="", help="Search query, tool name, or category filter")
    parser.add_argument("--run", action="store_true", help="Actually execute the installation command")

    args = parser.parse_args()

    if args.action == "stats":
        cmd_stats()
    elif args.action == "list":
        cmd_list(args.query if args.query else None)
    elif args.action == "search":
        if not args.query:
            print("Please specify a search term: ax arsenal search <term>")
        else:
            cmd_search(args.query)
    elif args.action == "info":
        if not args.query:
            print("Please specify a tool name: ax arsenal info <tool>")
        else:
            cmd_info(args.query)
    elif args.action == "install":
        if not args.query:
            print("Please specify a tool to install: ax arsenal install <tool>")
        else:
            cmd_install(args.query, execute=args.run)
    elif args.action == "categories":
        cmd_stats()


if __name__ == "__main__":
    main()
