# ASTERIX OS — Secure Localhost Chatting Vault

> **Military-grade, zero-knowledge, end-to-end encrypted (E2EE) private communications bridge.**
> Strict 2-party peer limit ("u and the person"), ephemeral in-memory storage, self-destruct timers, and 1-click panic burn killswitch.

---

## Key Security Features

1. **Client-Side End-to-End Encryption (E2EE):**
   - Implemented using the native **Web Crypto API** (`crypto.subtle`).
   - Keys are derived in your browser using **PBKDF2-HMAC-SHA256** with 100,000 iterations from your shared secret passphrase.
   - Every message is encrypted using **256-bit AES-GCM** with a unique 96-bit Initialization Vector (`IV`).
   - Plaintext **NEVER** leaves your browser. The server only sees encrypted ciphertext envelopes.

2. **Strict 2-Party Peer Limit:**
   - Designed exclusively for private two-party communication ("u and the person").
   - Rooms strictly reject any third party attempt to join.

3. **Zero Disk Persistence (100% In-Memory RAM):**
   - Zero logs written to disk.
   - Zero message databases.
   - Terminating the server or closing the room instantly eradicates all active sessions.

4. **Cryptographic Safety Numbers / Fingerprint:**
   - Displays a visual SHA-256 fingerprint formatted in 4-character blocks.
   - Compare out-of-band to mathematically verify 0% Man-in-the-Middle (MITM).

5. **Self-Destruct / Burn Timers:**
   - Configurable message burn timers: 5s, 15s, 30s, 60s.
   - Smooth animated countdown bar followed by DOM and memory wipe.

6. **☣ 1-Click Panic Burn Killswitch:**
   - Instantly wipes encryption keys from browser memory.
   - Sends emergency purge signal to erase the room from server RAM.
   - Clears the DOM and immediately redirects to a blank decoy page (`about:blank`).

7. **Synthesized Tactical SFX (Web Audio API):**
   - Transmit, receive, burn, and alarm sound effects generated mathematically in real time with zero external audio assets.

---

## Commands

```bash
ax secure-chat               # Start localhost encrypted vault (http://127.0.0.1:8765)
ax secure-chat start 9000    # Start on custom port 9000
ax secure-chat lan           # Bind to 0.0.0.0 for LAN sharing
ax secure-chat client        # Launch interactive CLI terminal client
ax secure-chat status        # Check if vault server is online
```

## Quick Aliases

```bash
ax-chat                      # Quick alias for: ax secure-chat
ax-secure-chat               # Quick alias for: ax secure-chat
secure-chat                  # Quick alias for: ax secure-chat
chat-room                    # Quick alias for: ax secure-chat
```

## Connecting Across Machines

### Option A: Local Network (LAN)
```bash
ax secure-chat lan
# Share: http://<your-lan-ip>:8765
```

### Option B: Encrypted SSH Tunnel (Remote)
```bash
ssh -L 8765:localhost:8765 user@remote-host
# Open on your machine: http://127.0.0.1:8765
```

---
*Built by NEXO TECHNOLOGIES — engineered for supremacy.*
