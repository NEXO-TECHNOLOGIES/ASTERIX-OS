#!/usr/bin/env python3
import subprocess


def get_uptime():
    result = subprocess.run(["uptime"], capture_output=True, text=True, shell=False)
    return result.stdout.strip() if result.stdout else "uptime unavailable"


def main():
    print(get_uptime())


if __name__ == "__main__":
    main()
