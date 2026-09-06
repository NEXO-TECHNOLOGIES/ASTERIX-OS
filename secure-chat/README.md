# ASTERIX OS — Secure Localhost Chatting Vault v2.0

> **Military-grade, zero-knowledge, end-to-end encrypted (E2EE) communications bridge.**
> Supports **Direct 1-on-1** & **Group Vaults**, customized room passwords on creation, full Admin Controls, and a built-in **3-Strike Intrusion Detection System (IDS)** with OS-level counter-attack alerts.

---

## Key Security & Architectural Features

1. **Client-Side End-to-End Encryption (E2EE):**
   - Built on the native browser **Web Crypto API** (`crypto.subtle`).
   - Keys derived via **PBKDF2-HMAC-SHA256** (100,000 iterations) from user secret passphrase + cryptographic salt.
   - Encrypted with **256-bit AES-GCM** using unique 96-bit random IVs per message.
   - Plaintext **never leaves the browser**; server only handles encrypted envelopes.

2. **Group Vaults & Direct 1-on-1:**
   - **Group Vault:** Multi-operative room for teams over localhost or LAN.
   - **Direct 1-on-1:** Strict 2-party peer limit ("u and the person"). Additional connections are automatically blocked.

3. **Custom Password Configuration on Room Creation:**
   - When creating a vault, the creator sets a custom secret password.
   - Joining operatives must authenticate with the exact password to enter.

4. **🚨 3-Strike Intrusion Detection System (IDS) & OS Alerts:**
   - Tracks failed password attempts per remote IP.
   - If an unauthorized snooper fails authentication **3 times**:
     - An **OS-level alarm banner** is triggered in the terminal:  
       `🚨 [ALERT] ASTERIX CAUGHT A THIEF SNOOPING INTO THE PRIVATE CHAT!`
     - Displays the attacker's **Target IP and Port**, targeted room, and timestamp.
     - Outlines recommended countermeasures with preinstalled tools:
       - `ax nmap -sV -O <IP>` — Fingerprint & vulnerability scan
       - `ax killswitch` — Instant network isolation
       - `ax decoy <PORT>` — Deploy trap listener
       - `ax traceroute <IP>` — Geolocation & routing trace
     - Pushes a real-time flashing **INTRUSION ALERT** to all connected web room members.

5. **👑 Group Admin Controls:**
   - The creator receives a cryptographically secure `admin_token`.
   - **Kick:** Force-disconnect and remove suspicious members.
   - **Mute/Unmute:** Prevent specific members from transmitting messages.
   - **Purge:** Instantly wipe chat history across all connected screens.
   - **Member List:** View active operatives, endpoints (IP:Port), and status.

6. **Anti-Forensics & Ephemeral RAM:**
   - 100% In-Memory RAM storage (zero disk logs, zero database).
   - Message self-destruct timers (5s, 15s, 30s, 60s) with visual countdown bars.
   - ☣ 1-Click **Panic Burn** killswitch immediately destroys the room from RAM and redirects to `about:blank`.

7. **Synthesized Web Audio API SFX:**
   - Mathematically generated audio for message transmit, receive, and intrusion alarm siren.

---

## Commands

```bash
ax secure-chat               # Start localhost vault on http://127.0.0.1:8765 and open browser
ax secure-chat start 9000    # Start on custom port 9000
ax secure-chat lan           # Bind to 0.0.0.0 for LAN group access
ax secure-chat client        # Launch interactive CLI terminal client
ax secure-chat status        # Check vault server health
```

## Quick Aliases

```bash
ax-chat                      # Quick alias for: ax secure-chat
ax-secure-chat               # Quick alias for: ax secure-chat
secure-chat                  # Quick alias for: ax secure-chat
chat-room                    # Quick alias for: ax secure-chat
```

---
*Built by NEXO TECHNOLOGIES — engineered for supremacy.*
