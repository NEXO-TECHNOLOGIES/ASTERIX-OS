#!/usr/bin/env python3
"""More realistic VM lifecycle logic with validation."""


def vm_transition(current, action):
    valid_actions = {
        "stopped": {"start", "destroy"},
        "running": {"stop", "restart", "snapshot"},
        "deleted": set(),
    }
    if action not in valid_actions.get(current, set()):
        return current

    transitions = {
        ("stopped", "start"): "running",
        ("running", "stop"): "stopped",
        ("running", "restart"): "running",
        ("stopped", "destroy"): "deleted",
    }
    return transitions.get((current, action), current)


def main():
    states = [
        ("stopped", "start"),
        ("running", "stop"),
        ("running", "restart"),
        ("stopped", "destroy"),
    ]
    for current, action in states:
        print(f"{current} + {action} -> {vm_transition(current, action)}")


if __name__ == "__main__":
    main()
