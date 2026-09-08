# 🛠️ ASTERIX OS Master Cybersecurity Arsenal & Tool Registry

> **Offline Registry of 180+ Industry-Standard Kali, Red Team, Exploit, and Forensic Tools**  
> **Repository Disk Bloat**: `0.0 MB` (Metadata indexed offline; zero-bloat architecture)  
> **Persistent Storage**: Installs on-demand directly into the Live USB Ext4 persistence partition (`/persistence`).

---

## 🎯 Architecture: Zero-Bloat On-Demand Arsenal

Rather than bloating the base ISO to 25+ GB and exceeding GitHub storage limits with 200 heavy cloned repositories, **ASTERIX OS** separates tools into two clean operational tiers:

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                      ASTERIX OS v2.0 ECOSYSTEM                              │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                                                             ▼
  [ TIER 1: PRE-INSTALLED (Base ISO) ]                [ TIER 2: ON-DEMAND (Persistent USB) ]
  • Size: 4.2 GB (Read-only Live Base)                • Saved to: Ext4 Persistence Partition
  • 35+ Battle-Tested Core Tools                      • 127+ Specialized Frameworks & Go Tools
  • 8 Pure-Rust Engines & Plymouth HUD                • On-demand install: ax arsenal install <tool>
  • Ready out-of-the-box (zero internet needed)       • Installs in seconds via APT, Go, Pipx, Docker
```

---

## 💻 CLI Tool Management (`ax arsenal` / `ax tools`)

The ASTERIX CLI provides instant offline discovery, fuzzy search, and on-demand installation recipes:

```bash
# View summary statistics across all 14 categories
ax arsenal stats

# List tools in a specific category (or all tools)
ax arsenal list [category]

# Search across 180+ tools, categories, and descriptions
ax arsenal search <keyword>

# View tool profile, official GitHub source, and install recipe
ax arsenal info <tool>

# Preview on-demand installation recipe (dry-run, no download)
ax arsenal install <tool>

# Execute installation directly onto your live persistence partition
ax arsenal install <tool> --run
```

---

## 📊 Complete Tool Matrix by Category

### 1. 🔍 Reconnaissance, OSINT & Asset Discovery
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`nmap`** | [nmap/nmap](https://github.com/nmap/nmap) | `✔ Pre-Installed` | `sudo apt install -y nmap` |
| **`masscan`** | [robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) | `✔ Pre-Installed` | `sudo apt install -y masscan` |
| **`theHarvester`** | [laramies/theHarvester](https://github.com/laramies/theHarvester) | `⚡ On-Demand` | `sudo apt install -y theharvester` |
| **`amass`** | [owasp-amass/amass](https://github.com/owasp-amass/amass) | `⚡ On-Demand` | `go install -v github.com/owasp-amass/amass/v4/...@master` |
| **`subfinder`** | [projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| **`naabu`** | [projectdiscovery/naabu](https://github.com/projectdiscovery/naabu) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest` |
| **`assetfinder`** | [tomnomnom/assetfinder](https://github.com/tomnomnom/assetfinder) | `⚡ On-Demand` | `go install github.com/tomnomnom/assetfinder@latest` |
| **`dnsx`** | [projectdiscovery/dnsx](https://github.com/projectdiscovery/dnsx) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest` |
| **`massdns`** | [blechschmidt/massdns](https://github.com/blechschmidt/massdns) | `⚡ On-Demand` | `sudo apt install -y massdns` |
| **`puredns`** | [d3mondev/puredns](https://github.com/d3mondev/puredns) | `⚡ On-Demand` | `go install github.com/d3mondev/puredns/v2@latest` |
| **`recon-ng`** | [lanmaster53/recon-ng](https://github.com/lanmaster53/recon-ng) | `⚡ On-Demand` | `git clone https://github.com/lanmaster53/recon-ng.git` |
| **`spiderfoot`** | [smicallef/spiderfoot](https://github.com/smicallef/spiderfoot) | `⚡ On-Demand` | `git clone https://github.com/smicallef/spiderfoot.git` |
| **`eyewitness`** | [FortyNorthSecurity/EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness) | `⚡ On-Demand` | `sudo apt install -y eyewitness` |
| **`p0f`** | [p0f/p0f](https://github.com/p0f/p0f) | `⚡ On-Demand` | `sudo apt install -y p0f` |
| **`chaos`** | [projectdiscovery/chaos-client](https://github.com/projectdiscovery/chaos-client) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest` |
| **`notify`** | [projectdiscovery/notify](https://github.com/projectdiscovery/notify) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/notify/cmd/notify@latest` |

---

### 2. 🛡️ Vulnerability Auditing & Scanning
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`nikto`** | [sullo/nikto](https://github.com/sullo/nikto) | `✔ Pre-Installed` | `sudo apt install -y nikto` |
| **`commix`** | [commixproject/commix](https://github.com/commixproject/commix) | `✔ Pre-Installed` | `sudo apt install -y commix` |
| **`nuclei`** | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| **`openvas`** | [greenbone/openvas-scanner](https://github.com/greenbone/openvas-scanner) | `⚡ On-Demand` | `sudo apt install -y gvm` |
| **`wapiti`** | [wapiti-scanner/wapiti](https://github.com/wapiti-scanner/wapiti) | `⚡ On-Demand` | `sudo apt install -y wapiti` |
| **`dalfox`** | [hahwul/dalfox](https://github.com/hahwul/dalfox) | `⚡ On-Demand` | `go install github.com/hahwul/dalfox/v2@latest` |
| **`xsstrike`** | [s0md3v/XSStrike](https://github.com/s0md3v/XSStrike) | `⚡ On-Demand` | `git clone https://github.com/s0md3v/XSStrike.git` |

---

### 3. 🌐 Web Application Security & Fuzzing
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`sqlmap`** | [sqlmapproject/sqlmap](https://github.com/sqlmapproject/sqlmap) | `✔ Pre-Installed` | `sudo apt install -y sqlmap` |
| **`gobuster`** | [OJ/gobuster](https://github.com/OJ/gobuster) | `✔ Pre-Installed` | `sudo apt install -y gobuster` |
| **`ffuf`** | [ffuf/ffuf](https://github.com/ffuf/ffuf) | `✔ Pre-Installed` | `sudo apt install -y ffuf` |
| **`whatweb`** | [urbanadventurer/WhatWeb](https://github.com/urbanadventurer/WhatWeb) | `✔ Pre-Installed` | `sudo apt install -y whatweb` |
| **`burpsuite`** | [PortSwigger](https://github.com/PortSwigger) | `⚡ On-Demand` | `sudo apt install -y burpsuite` |
| **`zaproxy`** | [zaproxy/zaproxy](https://github.com/zaproxy/zaproxy) | `⚡ On-Demand` | `sudo apt install -y zaproxy` |
| **`feroxbuster`** | [epi052/feroxbuster](https://github.com/epi052/feroxbuster) | `⚡ On-Demand` | `sudo apt install -y feroxbuster` |
| **`httpx`** | [projectdiscovery/httpx](https://github.com/projectdiscovery/httpx) | `⚡ On-Demand` | `go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| **`katana`** | [projectdiscovery/katana](https://github.com/projectdiscovery/katana) | `⚡ On-Demand` | `go install github.com/projectdiscovery/katana/cmd/katana@latest` |
| **`arjun`** | [s0md3v/Arjun](https://github.com/s0md3v/Arjun) | `⚡ On-Demand` | `pipx install arjun` |
| **`dirsearch`** | [maurosoria/dirsearch](https://github.com/maurosoria/dirsearch) | `⚡ On-Demand` | `pipx install dirsearch` |
| **`wpscan`** | [wpscanteam/wpscan](https://github.com/wpscanteam/wpscan) | `⚡ On-Demand` | `sudo apt install -y wpscan` |
| **`waybackurls`** | [tomnomnom/waybackurls](https://github.com/tomnomnom/waybackurls) | `⚡ On-Demand` | `go install github.com/tomnomnom/waybackurls@latest` |
| **`gau`** | [lc/gau](https://github.com/lc/gau) | `⚡ On-Demand` | `go install github.com/lc/gau/v2/cmd/gau@latest` |

---

### 4. 🔑 Password Auditing & Wordlists
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`hashcat`** | [hashcat/hashcat](https://github.com/hashcat/hashcat) | `✔ Pre-Installed` | `sudo apt install -y hashcat` |
| **`john`** | [openwall/john](https://github.com/openwall/john) | `✔ Pre-Installed` | `sudo apt install -y john` |
| **`hydra`** | [vanhauser-thc/thc-hydra](https://github.com/vanhauser-thc/thc-hydra) | `✔ Pre-Installed` | `sudo apt install -y hydra` |
| **`medusa`** | [jmk-foofus/medusa](https://github.com/jmk-foofus/medusa) | `✔ Pre-Installed` | `sudo apt install -y medusa` |
| **`crunch`** | [jim3ma/crunch](https://github.com/jim3ma/crunch) | `✔ Pre-Installed` | `sudo apt install -y crunch` |
| **`cewl`** | [digininja/CeWL](https://github.com/digininja/CeWL) | `✔ Pre-Installed` | `sudo apt install -y cewl` |
| **`ncrack`** | [nmap/ncrack](https://github.com/nmap/ncrack) | `✔ Pre-Installed` | `sudo apt install -y ncrack` |
| **`seclists`** | [danielmiessler/SecLists](https://github.com/danielmiessler/SecLists) | `⚡ On-Demand` | `sudo apt install -y seclists` |

---

### 5. 📡 Wireless & Radio Warfare
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`aircrack-ng`** | [aircrack-ng/aircrack-ng](https://github.com/aircrack-ng/aircrack-ng) | `✔ Pre-Installed` | `sudo apt install -y aircrack-ng` |
| **`wifite2`** | [derv82/wifite2](https://github.com/derv82/wifite2) | `✔ Pre-Installed` | `sudo apt install -y wifite` |
| **`reaver`** | [t6x/reaver-wps-fork-t6x](https://github.com/t6x/reaver-wps-fork-t6x) | `✔ Pre-Installed` | `sudo apt install -y reaver` |
| **`bully`** | [aanarchyy/bully](https://github.com/aanarchyy/bully) | `✔ Pre-Installed` | `sudo apt install -y bully` |
| **`pixiewps`** | [wiire-a/pixiewps](https://github.com/wiire-a/pixiewps) | `✔ Pre-Installed` | `sudo apt install -y pixiewps` |
| **`kismet`** | [kismetwireless/kismet](https://github.com/kismetwireless/kismet) | `✔ Pre-Installed` | `sudo apt install -y kismet` |

---

### 6. ⚡ Exploitation, Post-Exploitation & C2
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`metasploit`** | [rapid7/metasploit-framework](https://github.com/rapid7/metasploit-framework) | `✔ Pre-Installed` | Automated build hook |
| **`searchsploit`** | [offensive-security/exploitdb](https://github.com/offensive-security/exploitdb) | `⚡ On-Demand` | `sudo apt install -y exploitdb` |
| **`sliver`** | [BishopFox/sliver](https://github.com/BishopFox/sliver) | `⚡ On-Demand` | `curl -s https://sliver.sh/install \| sudo bash` |
| **`beef`** | [beefproject/beef](https://github.com/beefproject/beef) | `⚡ On-Demand` | `sudo apt install -y beef-xss` |
| **`caldera`** | [mitre/caldera](https://github.com/mitre/caldera) | `⚡ On-Demand` | `git clone --recursive https://github.com/mitre/caldera.git` |
| **`havoc`** | [HavocFramework/Havoc](https://github.com/HavocFramework/Havoc) | `⚡ On-Demand` | `git clone https://github.com/HavocFramework/Havoc.git` |

---

### 7. 🏢 Active Directory, Windows & Pivoting
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`proxychains-ng`**| [rofl0r/proxychains-ng](https://github.com/rofl0r/proxychains-ng) | `✔ Pre-Installed` | `sudo apt install -y proxychains4` |
| **`socat`** | [3ndG4me/socat](https://github.com/3ndG4me/socat) | `✔ Pre-Installed` | `sudo apt install -y socat` |
| **`impacket`** | [fortra/impacket](https://github.com/fortra/impacket) | `⚡ On-Demand` | `pipx install impacket` |
| **`netexec`** | [Pennyw0rth/NetExec](https://github.com/Pennyw0rth/NetExec) | `⚡ On-Demand` | `pipx install git+https://github.com/Pennyw0rth/NetExec` |
| **`bloodhound`** | [SpecterOps/BloodHound](https://github.com/SpecterOps/BloodHound) | `⚡ On-Demand` | `sudo apt install -y bloodhound` |
| **`responder`** | [lgandx/Responder](https://github.com/lgandx/Responder) | `⚡ On-Demand` | `sudo apt install -y responder` |
| **`certipy`** | [ly4k/Certipy](https://github.com/ly4k/Certipy) | `⚡ On-Demand` | `pipx install certipy-ad` |
| **`chisel`** | [jpillora/chisel](https://github.com/jpillora/chisel) | `⚡ On-Demand` | `go install github.com/jpillora/chisel@latest` |
| **`ligolo-ng`** | [nicocha30/ligolo-ng](https://github.com/nicocha30/ligolo-ng) | `⚡ On-Demand` | `go install github.com/nicocha30/ligolo-ng/cmd/proxy@latest` |

---

### 8. 🔬 Forensics, Reverse Engineering & Blue Team
| Tool | GitHub Repository | Status | Installation Method |
| :--- | :--- | :---: | :--- |
| **`binwalk`** | [ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk) | `✔ Pre-Installed` | `sudo apt install -y binwalk` |
| **`radare2`** | [radareorg/radare2](https://github.com/radareorg/radare2) | `✔ Pre-Installed` | `sudo apt install -y radare2` |
| **`foremost`** | [korczis/foremost](https://github.com/korczis/foremost) | `✔ Pre-Installed` | `sudo apt install -y foremost` |
| **`sleuthkit`** | [sleuthkit/sleuthkit](https://github.com/sleuthkit/sleuthkit) | `✔ Pre-Installed` | `sudo apt install -y sleuthkit` |
| **`exiftool`** | [exiftool/exiftool](https://github.com/exiftool/exiftool) | `✔ Pre-Installed` | `sudo apt install -y exiftool` |
| **`ghidra`** | [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) | `⚡ On-Demand` | `sudo apt install -y ghidra` |
| **`volatility3`** | [volatilityfoundation/volatility3](https://github.com/volatilityfoundation/volatility3) | `⚡ On-Demand` | `pipx install volatility3` |
| **`yara`** | [VirusTotal/yara](https://github.com/VirusTotal/yara) | `⚡ On-Demand` | `sudo apt install -y yara` |
| **`suricata`** | [OISF/suricata](https://github.com/OISF/suricata) | `⚡ On-Demand` | `sudo apt install -y suricata` |
| **`zeek`** | [zeek/zeek](https://github.com/zeek/zeek) | `⚡ On-Demand` | `sudo apt install -y zeek` |
| **`gitleaks`** | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | `⚡ On-Demand` | `go install github.com/zricethezav/gitleaks/v8@latest` |
