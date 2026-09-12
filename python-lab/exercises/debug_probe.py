#!/usr/bin/env python3
"""Debugging exercise: find and fix the root cause in a small script."""


def compute_total(prices):
    total = 0
    for price in prices:
        total += price
    return total


def main():
    items = [10, 20, 30, "oops", 50]
    try:
        total = compute_total(items)
        print(f"Total: {total}")
    except TypeError as exc:
        print(f"TypeError: {exc}")


if __name__ == "__main__":
    main()
