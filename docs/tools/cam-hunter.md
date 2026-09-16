# 🏨 `cam-hunter` — Technical Surveillance Counter-Measures (TSCM)

A defensive privacy suite for detecting unauthorized Wi-Fi IoT cameras, surveillance streams, and RF beacon transmitters in hotel rooms, rental spaces, and sensitive facilities.

---

## 📌 Usage

```bash
ax cam-hunter [hotel|scan|rf|guide]
```

---

## ⚙️ Technical Methodology

1. **Passive Wi-Fi Device Discovery (`scan`)**:
   - Inspects the local network for MAC OUI vendors matching known IP camera manufacturers (Tuya, Hikvision, Dahua, Wyze, Xiongmai).
   - Flags suspicious low-power headless IoT devices maintaining continuous outbound video uplinks.

2. **RTSP Stream Probing**:
   - Audits ports `554`, `8554`, and `8899` to detect unprotected live RTSP camera feeds.

3. **RF RSSI Localization (`rf`)**:
   - Measures Wi-Fi signal attenuation (RSSI) in decibels (`dBm`) as the device is moved around the room to help physically pinpoint hidden transmitters.

4. **Optical Physical Inspection Guide (`guide`)**:
   - Provides step-by-step physical inspection checklists for smoke detectors, power outlets, mirrors, clocks, and pinhole lenses using smartphone IR camera filters.

---

## ⚖️ Legal & Operational Safety
- **No Signal Jamming**: `cam-hunter` does NOT transmit RF jamming signals. RF jamming is illegal under FCC and ITU international regulations and does not disable offline SD-card recording devices. All detection is **100% passive and defensive**.
