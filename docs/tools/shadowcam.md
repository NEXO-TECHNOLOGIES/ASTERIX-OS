# 📹 `shadowcam` — Local RTSP & ONVIF Stream Discovery

A network inspection tool designed to identify IP surveillance endpoints, RTSP media streams, and ONVIF device service ports on authorized local subnets.

---

## 📌 Usage

```bash
ax shadowcam discover
ax shadowcam scan <subnet-cidr>
ax shadowcam audit <ip> [port]
```

---

## ⚙️ How It Works

- **Discovery (`discover`)**: Automatically identifies the local subnet (`/24`) and probes hosts for standard video surveillance ports:
  - `554` (RTSP - Real Time Streaming Protocol)
  - `8554` (Alternative RTSP)
  - `8000` / `8081` (Hikvision / Generic DVR HTTP)
  - `8899` / `3702` (ONVIF WS-Discovery)
  - `80` / `8080` (Camera Web Admin Portals)
- **JSON Output (`--json`)**: Emits structured machine-readable logs detailing detected ports, responsive hostnames, and latency metrics.

---

## ⚠️ Safety Boundaries & Limitations
- **Read-Only Probe**: `shadowcam` only checks for open TCP connection states. It does not attempt credential bruteforcing, exploit execution, or unauthorized stream interception.
- **Local Networks Only**: Designed exclusively for assessing security camera posture on authorized private local area networks.
