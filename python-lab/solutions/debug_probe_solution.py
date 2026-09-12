#!/usr/bin/env python3
"""Fixed version: filter invalid numeric values before summing."""


def compute_total(prices):
    total = 0
    for price in prices:
        if isinstance(price, (int, float)):
            total += price
    return total


def main():
    items = [10, 20, 30, "oops", 50]
    total = compute_total(items)
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
