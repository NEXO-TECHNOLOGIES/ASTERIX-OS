# 🌐 ASTERIX ProxyChains Creator // Proxy Validation & Dynamic Chain Engine

The **ProxyChains Creator** (`proxychains-creator/`) is an automated proxy discovery, handshake validation, and dynamic routing chain synthesis tool built for ASTERIX OS.

It probes SOCKS4, SOCKS5, and HTTP proxies via native socket greetings, evaluates round-trip latency, identifies the target country/geolocation, filters out dead or high-latency nodes, and generates a valid `proxychains.conf` file ready for instant use.

---

## ⚡ Key Capabilities

- **RFC 1928 SOCKS5 & SOCKS4 Handshake Probing**: Sends native binary protocol greeting frames to verify actual proxy functionality, not just open ports.
- **Detailed IP Telemetry**: Displays `[STATUS] [IP ADDRESS] [PORT] [TYPE: SOCKS4/SOCKS5] [COUNTRY] [LATENCY ms] [CHAIN ORDER]`.
- **Dynamic Chain Generation**: Automatically formats and exports alive proxies into `~/.asterix_vault/proxychains/proxychains.conf` using `dynamic_chain` with `proxy_dns` enabled to stop DNS leaking.
- **Custom Ingestion**: Accepts external proxy lists (format: `ip:port` or `ip port socks5`).

---

## 🚀 CLI Usage

```bash
# Scan and test default curated SOCKS proxy nodes
ax proxychains scan

# Test custom proxy list from file
ax proxychains scan /path/to/proxies.txt

# Test a single endpoint and add to chain
ax proxychains add 188.166.49.208 1080 socks5

# View active proxy chain configuration
ax proxychains status

# Execute any command anonymously through the generated chain
proxychains4 -f ~/.asterix_vault/proxychains/proxychains.conf curl https://ifconfig.me
```
