#  `ax-doctor` — System & Network Health Engine

An autonomous diagnostic engine that evaluates local networking, identifies blocked ports, cleans leaked developer secrets, and verifies system dependencies.

---

##  Usage

```bash
ax doctor [--fix]
ax unblock <port>
ax secrets [path]
```

---

## [*] Key Capabilities

- **Port Unblocking (`ax unblock <port>`)**: Identifies zombie processes binding development or proxy ports (e.g. 8080, 4888, 8888) and safely terminates them.
- **Leaked Secret Auditor (`ax secrets [path]`)**: Recursively scans codebase for accidentally committed private keys, AWS tokens, JWTs, and API credentials.
- **Environment Doctor (`ax doctor`)**: Tests DNS latency, gateway reachability, package repository health, and user-space filesystem permissions.
