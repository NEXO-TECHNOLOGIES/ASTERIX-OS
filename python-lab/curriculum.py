#!/usr/bin/env python3
"""Small curriculum model for the Python training lab."""

from dataclasses import dataclass
from typing import List


@dataclass
class Challenge:
    name: str
    difficulty: str
    score: int
    focus: str
    checkpoint: str


TASKS: List[Challenge] = [
    Challenge(
        name="debug_probe",
        difficulty="Beginner",
        score=20,
        focus="debugging and root-cause tracing",
        checkpoint="Identify invalid types and fix the data flow",
    ),
    Challenge(
        name="shell_runner",
        difficulty="Beginner",
        score=25,
        focus="OS + shell automation",
        checkpoint="Handle command results safely and platform-aware",
    ),
    Challenge(
        name="api_client",
        difficulty="Intermediate",
        score=30,
        focus="API and request handling",
        checkpoint="Parse JSON and add resilience to the client",
    ),
    Challenge(
        name="vm_lifecycle",
        difficulty="Intermediate",
        score=35,
        focus="VM lifecycle automation",
        checkpoint="Model valid transitions and state validation",
    ),
    Challenge(
        name="dashboard_data",
        difficulty="Advanced",
        score=40,
        focus="dashboard logic and metrics",
        checkpoint="Aggregate data into a clean monitoring payload",
    ),
    Challenge(
        name="html_layout",
        difficulty="Beginner",
        score=30,
        focus="semantic HTML and page structure",
        checkpoint="Build a clear semantic layout with meaningful sections",
    ),
    Challenge(
        name="css_responsive",
        difficulty="Intermediate",
        score=35,
        focus="CSS layout and responsive design",
        checkpoint="Design a responsive interface with readable spacing and hierarchy",
    ),
    Challenge(
        name="ui_ux_wireframe",
        difficulty="Intermediate",
        score=40,
        focus="UI/UX thinking and product flow",
        checkpoint="Create a clear user flow with calls to action and hierarchy",
    ),
    Challenge(
        name="frontend_dashboard",
        difficulty="Advanced",
        score=45,
        focus="dashboard UI and interface polish",
        checkpoint="Assemble a polished dashboard with cards, metrics, and clear states",
    ),
]

LEVELS = {
    "Beginner": 0,
    "Intermediate": 100,
    "Advanced": 170,
}


def get_unlocked_tasks(completed_names):
    completed_set = set(completed_names)
    unlocked = []
    for task in TASKS:
        index = TASKS.index(task)
        if index == 0:
            unlocked.append(task.name)
            continue
        if TASKS[index - 1].name in completed_set:
            unlocked.append(task.name)
    return unlocked


def show_curriculum():
    print("ASTERIX AI Training Curriculum")
    print("=" * 32)
    total = sum(task.score for task in TASKS)
    print(f"Total possible score: {total}")
    print()
    for idx, task in enumerate(TASKS, start=1):
        print(f"{idx}. {task.name}")
        print(f"   Difficulty: {task.difficulty}")
        print(f"   Score: {task.score}")
        print(f"   Focus: {task.focus}")
        print(f"   Checkpoint: {task.checkpoint}")
        print()


if __name__ == "__main__":
    show_curriculum()
