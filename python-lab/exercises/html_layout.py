#!/usr/bin/env python3
"""A basic semantic HTML exercise scaffold."""

HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ASTERIX Landing Page</title>
  </head>
  <body>
    <header>
      <nav>
        <a href="#">Home</a>
        <a href="#">Features</a>
        <a href="#">Pricing</a>
      </nav>
    </header>
    <main>
      <section>
        <h1>Launch faster with Asterix</h1>
        <p>Build, deploy, and monitor with a clean operational workflow.</p>
      </section>
    </main>
    <footer>
      <p>© 2026 Asterix</p>
    </footer>
  </body>
</html>
"""

if __name__ == "__main__":
    print("Semantic HTML scaffold ready.")
    print(HTML.strip()[:200])
