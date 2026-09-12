#!/usr/bin/env python3
import json
import urllib.request


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "asterix-python-lab"})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = response.read().decode("utf-8")
        return json.loads(data)


def main():
    data = fetch_json("https://jsonplaceholder.typicode.com/todos/1")
    print(data["title"])


if __name__ == "__main__":
    main()
