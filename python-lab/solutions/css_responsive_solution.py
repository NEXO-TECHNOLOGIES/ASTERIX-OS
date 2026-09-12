#!/usr/bin/env python3
"""Responsive CSS solution scaffold."""

CSS = """
:root {
  --bg: #020817;
  --panel: #0f172a;
  --text: #f8fafc;
  --muted: #cbd5e1;
  --accent: #38bdf8;
  --success: #22c55e;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Segoe UI", sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.card {
  padding: 20px;
  background: var(--panel);
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.15);
}

@media (max-width: 600px) {
  .container { padding: 20px 16px; }
}
"""

if __name__ == "__main__":
    print("Responsive CSS solution ready.")
    print(CSS.strip()[:250])
