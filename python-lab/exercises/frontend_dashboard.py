#!/usr/bin/env python3
"""Dashboard UI concept scaffold."""

DASHBOARD = {
    "title": "Asterix Control Center",
    "cards": [
        {"label": "Hosts", "value": 4, "status": "Online"},
        {"label": "VMs", "value": 12, "status": "Stable"},
        {"label": "Alerts", "value": 3, "status": "Needs review"},
    ],
    "layout": [
        "Header",
        "Metric row",
        "Activity feed",
        "System status",
    ],
}

if __name__ == "__main__":
    print(DASHBOARD)
