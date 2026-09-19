#  `self-evolve` — Autonomous Threat Feed Ingestion Engine

An autonomous knowledge aggregator that updates local security rules and diagnostic signatures by ingesting public CVE feeds, CISA KEV alerts, and threat bulletins.

---

##  Usage

```bash
ax self-evolve evolve
ax self-evolve status
ax self-evolve daemon [hours]
```

---

## [*] Technical Architecture

1. **Threat Feed Aggregation**:
   - Parses public RSS/Atom feeds from CISA Known Exploited Vulnerabilities (KEV), NVD CVE bulletins, and security advisories.
   - Extracts vulnerability IDs, affected software versions, and recommended mitigations.
2. **Local JSON Knowledge Graph**:
   - Formats parsed threat intelligence into structured JSON signatures stored locally in `custom_rules.json`.
3. **100% Offline Capability**:
   - Once feeds are ingested, diagnostic and detection engines query the local JSON rules completely offline without telemetry or external cloud calls.
