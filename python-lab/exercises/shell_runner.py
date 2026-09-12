#!/usr/bin/env python3
import subprocess


def get_uptime():
    result = subprocess.run(["bash", "-lc", "uptime"], capture_output=True, text=True)
    return result.stdout.strip()


def main():
    print(get_uptime())


if __name__ == "__main__":
    main()
