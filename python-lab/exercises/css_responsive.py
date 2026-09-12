#!/usr/bin/env python3
"""Responsive CSS exercise scaffold."""

CSS = """
:root {
  --bg: #0f172a;
  --card: #111827;
  --text: #e5e7eb;
  --muted: #94a3b8;
  --accent: #22c55e;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Arial, sans-serif;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.card {
  background: var(--card);
  border-radius: 12px;
  padding: 18px;
}
"""

if __name__ == "__main__":
    print("Responsive CSS scaffold ready.")
    print(CSS.strip()[:220])
