# 🕳️ `black-hole` — Defensive Privacy & Telemetry Hardener

A privacy hardening and surveillance mitigation layer that evaluates DNS/IP leak exposure, identifies suspicious local endpoints, and checks host microphone/camera status.

---

## 📌 Usage

```bash
ax black-hole audit
ax black-hole mask
ax black-hole report [--json]
```

---

## ⚙️ Key Capabilities

- **DNS/IP Leak Audit**: Tests whether local DNS requests bypass encrypted DoH tunnels and leak cleartext queries to the local ISP.
- **Hardware Sensor Exposure Check**: Probes for active recording locks or open handles on microphones and webcams.
- **Local Network Surveillance Scoring**: Computes a local risk score based on broadcast traffic, open media ports, and unauthenticated device discovery.
- **Emergency Masking (`mask`)**: Drops suspicious unencrypted Wi-Fi connections and resets network interfaces when risk score exceeds safe thresholds.

---

## ⚠️ Important Limitations
- This is a best-effort local hardening and detection layer. It reduces network and physical exposure, but cannot guarantee protection against kernel-level telemetry or specialized hardware wiretaps.
