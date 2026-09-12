#!/usr/bin/env python3
import json
import urllib.request


def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        data = response.read().decode()
        return json.loads(data)


def main():
    data = fetch_json("https://jsonplaceholder.typicode.com/todos/1")
    print(data["title"])


if __name__ == "__main__":
    main()
