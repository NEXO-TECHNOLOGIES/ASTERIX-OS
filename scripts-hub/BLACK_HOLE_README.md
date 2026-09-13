# Black Hole

Black Hole is ASTERIX OS's local privacy-hardening and hostile-surveillance detection tool. It is designed to provide a best-effort assessment of whether the host is exposing suspicious wireless, USB, or device-signal patterns that could indicate monitoring or covert tracking.

This tool does not claim to guarantee invisibility or prevent all forms of surveillance. It focuses on local risk detection, host hygiene, and best-effort masking of obvious leak points.

## What Black Hole does

- Checks for camera-like or surveillance-like devices on the local subnet
- Scans nearby Wi‑Fi beacons and classifies likely patterns
- Reviews local device signal indicators such as webcam or audio nodes
- Checks for suspicious USB or peripheral attachments
- Performs local network exposure checks for commonly exposed service ports
- Produces a risk score and targeted-surveillance verdict
- Can trigger a best-effort internet masking flow for local mitigation

## Core files

- `scripts-hub/black_hole.py` — primary implementation
- `scripts-hub/test_black_hole.py` — regression tests

## Quick usage

From the repository root:

```bash
python scripts-hub/black_hole.py --status
python scripts-hub/black_hole.py --scan
python scripts-hub/black_hole.py --full --json
python scripts-hub/black_hole.py --full --verbose --query "I think I am being tracked and watched"
python scripts-hub/black_hole.py --mask --aggressive
python scripts-hub/black_hole.py --disconnect
```

Typical output includes:

- risk score
- risk level
- Wi‑Fi beacon list
- camera-like host detections
- local exposure summary
- trace assessment verdict
- masking actions

## Risk model

Black Hole computes a score from 0 to 100 using a layered model:

- suspicious camera hosts on the subnet
- nearby Wi‑Fi beacon counts and fingerprints
- local open service ports
- host camera/audio signal indicators
- USB or peripheral suspicion

The tool then converts that into a verdict such as:

- `normal_environment`
- `monitoring_risk`
- `targeted_surveillance`

## Best-effort masking mode

The masking flow uses the Asterix Protocol 156 logic and is intentionally honest about its limits:

- it may disconnect a wireless connection when requested
- it reduces obvious local exposure patterns
- it does not guarantee total invisibility against all surveillance methods

This is designed as a local defensive aid, not a complete anti-surveillance system.

## Example JSON output

```json
{
  "overall": "critical",
  "report": {
    "risk_score": 84,
    "risk_level": "critical",
    "wifi_beacons": [],
    "camera_scan": [],
    "network_exposure": {
      "local_open_ports": []
    },
    "trace_assessment": {
      "decision": "high",
      "confidence": "high"
    }
  }
}
```

## Safety note

This tool is intended for defensive, privacy-hardening, and forensic analysis in controlled environments. It should be used responsibly and only where the user has a legitimate need to assess local exposure or hostile surveillance indicators.
