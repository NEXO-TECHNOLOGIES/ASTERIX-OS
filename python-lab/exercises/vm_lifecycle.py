#!/usr/bin/env python3
"""A small lifecycle model for VM states."""


def vm_transition(current, action):
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
