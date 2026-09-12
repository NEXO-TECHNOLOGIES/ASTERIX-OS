#!/usr/bin/env python3
"""Progress tracker with progression gating, XP, badges, and daily milestones."""

import argparse
import json
from pathlib import Path

from curriculum import LEVELS, TASKS, get_unlocked_tasks

PROGRESS_FILE = Path(__file__).resolve().parent / "progress.json"


def compute_level(score):
    if score >= LEVELS["Advanced"]:
        return "Advanced"
    if score >= LEVELS["Intermediate"]:
        return "Intermediate"
    return "Beginner"


def load_progress():
    if not PROGRESS_FILE.exists():
        return {
            "completed": [],
            "score": 0,
            "level": "Beginner",
            "badge": "Starter",
            "day": "Day 1",
            "unlocked": [TASKS[0].name],
        }
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        data.setdefault("completed", [])
        data.setdefault("score", 0)
        data.setdefault("level", "Beginner")
        data.setdefault("badge", "Starter")
        data.setdefault("day", "Day 1")
        data.setdefault("unlocked", [TASKS[0].name])
        return data
    except json.JSONDecodeError:
        return {
            "completed": [],
            "score": 0,
            "level": "Beginner",
            "badge": "Starter",
            "day": "Day 1",
            "unlocked": [TASKS[0].name],
        }


def save_progress(data):
    PROGRESS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def unlock_tasks(data):
    unlocked = get_unlocked_tasks(data["completed"])
    data["unlocked"] = unlocked
    data["level"] = compute_level(data["score"])
    if data["score"] >= 220:
        data["badge"] = "UI Engineer"
        data["day"] = "Day 3"
    elif data["score"] >= 160:
        data["badge"] = "Operator"
        data["day"] = "Day 2"
    else:
        data["badge"] = "Debugger"
        data["day"] = "Day 1"
    return data


def mark_complete(task_name, score):
    data = load_progress()
    if task_name not in data["completed"]:
        data["completed"].append(task_name)
        data["score"] += score
    data = unlock_tasks(data)
    save_progress(data)
    print(f"Completed: {task_name}")
    print(f"Score: {data['score']}")
    print(f"Level: {data['level']}")
    print(f"Badge: {data['badge']}")
    print(f"Current day: {data['day']}")
    print(f"Unlocked: {', '.join(data['unlocked'])}")


def show_progress():
    data = load_progress()
    data = unlock_tasks(data)
    save_progress(data)
    print("Progress Summary")
    print("-" * 20)
    print(f"Completed: {', '.join(data['completed']) if data['completed'] else 'none'}")
    print(f"Score: {data['score']}")
    print(f"Level: {data['level']}")
    print(f"Badge: {data['badge']}")
    print(f"Current day: {data['day']}")
    print(f"Unlocked: {', '.join(data['unlocked'])}")


def reset_progress():
    data = {
        "completed": [],
        "score": 0,
        "level": "Beginner",
        "badge": "Starter",
        "day": "Day 1",
        "unlocked": [TASKS[0].name],
    }
    save_progress(data)
    print("Progress reset to the first challenge.")


def main():
    parser = argparse.ArgumentParser(description="Track the AI curriculum progression.")
    parser.add_argument("--show", action="store_true", help="Display progress")
    parser.add_argument("--reset", action="store_true", help="Reset the curriculum progress")
    parser.add_argument("--complete", metavar="TASK", help="Mark a task as complete and unlock the next challenge")
    parser.add_argument("--score", type=int, default=0, help="Task score value to add when completing a task")
    args = parser.parse_args()

    if args.reset:
        reset_progress()
        return
    if args.complete:
        mark_complete(args.complete, args.score)
        return
    show_progress()


if __name__ == "__main__":
    main()
