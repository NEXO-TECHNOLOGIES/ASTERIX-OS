#!/usr/bin/env python3
import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXERCISES = ROOT / "exercises"
SOLUTIONS = ROOT / "solutions"
PROMPTS = ROOT / "prompts"
TASKS = [
    "debug_probe",
    "shell_runner",
    "api_client",
    "vm_lifecycle",
    "dashboard_data",
    "html_layout",
    "css_responsive",
    "ui_ux_wireframe",
    "frontend_dashboard",
]


def load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(script_path):
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def print_prompt(task_name):
    prompt_path = PROMPTS / f"task_{TASKS.index(task_name) + 1}_{task_name.split('_')[0]}.md"
    if prompt_path.exists():
        print(f"\nPrompt: {prompt_path.name}")
        print(prompt_path.read_text(encoding="utf-8").strip()[:600])


def run_task(task_name):
    exercise = EXERCISES / f"{task_name}.py"
    if not exercise.exists():
        print(f"Exercise not found: {exercise}")
        return 1

    print(f"\n=== TASK: {task_name} ===")
    print_prompt(task_name)

    code, out, err = run_script(exercise)
    print(f"Exercise exit: {code}")
    if out:
        print(out)
    if err:
        print(err)

    solution = SOLUTIONS / f"{task_name}_solution.py"
    if solution.exists():
        print(f"\nReference solution for {task_name}:")
        code2, out2, err2 = run_script(solution)
        print(f"Solution exit: {code2}")
        if out2:
            print(out2)
        if err2:
            print(err2)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Python lab runner")
    parser.add_argument("task", nargs="?", choices=TASKS + ["all", "list"], help="Choose a task or run the whole training loop.")
    args = parser.parse_args()

    if args.task in (None, "list"):
        print("Available tasks:")
        for name in TASKS:
            print(f"- {name}")
        return 0

    if args.task == "all":
        for task in TASKS:
            status = run_task(task)
            if status != 0:
                return status
        return 0

    return run_task(args.task)


if __name__ == "__main__":
    raise SystemExit(main())
