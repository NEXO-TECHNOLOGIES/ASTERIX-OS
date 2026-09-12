#!/usr/bin/env python3
"""Daily training plan for AI skill progression."""

from dataclasses import dataclass
from typing import List


@dataclass
class DailyPlan:
    day: str
    title: str
    focus: str
    goals: List[str]
    challenges: List[str]
    xp: int
    badge: str
    milestone: str


PLAN: List[DailyPlan] = [
    DailyPlan(
        day="Day 1",
        title="Core debugging and shell grips",
        focus="foundation",
        goals=[
            "Fix broken logic and explain root cause",
            "Run a real shell command safely",
            "Capture and interpret command output",
        ],
        challenges=[
            "debug_probe",
            "shell_runner",
        ],
        xp=120,
        badge="Debugger",
        milestone="Root cause tracing and shell confidence",
    ),
    DailyPlan(
        day="Day 2",
        title="API, automation, and service logic",
        focus="infrastructure logic",
        goals=[
            "Request JSON from a real endpoint",
            "Model system states and transitions",
            "Reason about automation workflows",
        ],
        challenges=[
            "api_client",
            "vm_lifecycle",
        ],
        xp=160,
        badge="Operator",
        milestone="Working with services and lifecycle workflows",
    ),
    DailyPlan(
        day="Day 3",
        title="Front-end, UX, and dashboard polish",
        focus="product interface",
        goals=[
            "Build semantic HTML layouts",
            "Create a responsive CSS interface",
            "Evaluate UX clarity and dashboard polish",
        ],
        challenges=[
            "html_layout",
            "css_responsive",
            "ui_ux_wireframe",
            "frontend_dashboard",
        ],
        xp=220,
        badge="UI Engineer",
        milestone="A clean operator-facing dashboard and UX flow",
    ),
]


def print_daily_plan(day_name: str = None):
    if day_name:
        selected = [day for day in PLAN if day.day.lower() == day_name.lower()]
        if not selected:
            print(f"Unknown day: {day_name}")
            return
        days = selected
    else:
        days = PLAN

    for day in days:
        print(f"{day.day}: {day.title}")
        print(f"Focus: {day.focus}")
        print("Goals:")
        for goal in day.goals:
            print(f"- {goal}")
        print(f"Challenges: {', '.join(day.challenges)}")
        print(f"XP: {day.xp}")
        print(f"Badge: {day.badge}")
        print(f"Milestone: {day.milestone}")
        print()


def main():
    print("ASTERIX AI Daily Training Plan")
    print("=" * 30)
    print_daily_plan()


if __name__ == "__main__":
    main()
