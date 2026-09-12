#!/usr/bin/env python3
"""UI/UX wireframe planning scaffold."""

FLOW = {
    "goal": "Monitor system health and launch actions quickly",
    "primary_action": "Create VM",
    "sections": [
        "Overview stats",
        "Recent alerts",
        "Controls and quick actions",
        "Recent activity",
    ],
    "ux_notes": [
        "Keep critical actions visible",
        "Use strong hierarchy for status and warnings",
        "Minimize clicks for common tasks",
    ],
}

if __name__ == "__main__":
    print(FLOW)
