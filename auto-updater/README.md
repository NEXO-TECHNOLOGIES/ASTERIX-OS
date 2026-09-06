# ASTERIX OS — Live Auto-Updater

> **F-Droid-style automatic repository sync** — detects new commits the moment they land on GitHub and pulls them instantly.

## How It Works

1. The daemon polls the GitHub API every 60 seconds (configurable)
2. It compares the remote `main` branch SHA with local `git rev-parse HEAD`
3. On mismatch → `git pull origin main` is executed automatically
4. All update events are logged to `~/.asterix_vault/auto-updater/update.log`

## Commands

```bash
ax auto-update start       # Start background watcher daemon
ax auto-update start 30    # Custom poll interval (30 seconds)
ax auto-update stop        # Stop the daemon
ax auto-update status      # Show daemon state and last sync info
ax auto-update check       # One-shot manual check + pull
ax auto-update log         # View last 20 update log entries
ax auto-update log 50      # View last 50 entries
```

## Aliases

```bash
auto-update         # alias for: ax auto-update check
```

## Files

| File | Purpose |
|------|---------|
| `update_daemon.py` | Primary daemon (Python 3, zero dependencies) |
| `update_daemon.sh` | Bash fallback (uses curl/wget + git) |
| `asterix-updater.service` | systemd unit for Linux system install |

## systemd Install (Linux, optional)

```bash
sudo cp asterix-updater.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now asterix-updater
sudo systemctl status asterix-updater
```

## Termux / Android

```bash
ax auto-update start &    # Background daemon
```

## State Files

All state is stored in `~/.asterix_vault/auto-updater/`:

| File | Contents |
|------|----------|
| `state.json` | Last known SHA, last checked timestamp, update count |
| `update.log` | Full update history with timestamps |
| `daemon.pid` | PID of running daemon (auto-created/removed) |

---
*Built by NEXO TECHNOLOGIES — engineered for supremacy.*
