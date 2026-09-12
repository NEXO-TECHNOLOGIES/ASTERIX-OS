#!/usr/bin/env python3
"""Semantic HTML landing page solution."""

HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ASTERIX Platform</title>
  </head>
  <body>
    <header>
      <nav aria-label="Main navigation">
        <a href="#">Overview</a>
        <a href="#">Solutions</a>
        <a href="#">Pricing</a>
      </nav>
    </header>

    <main>
      <section aria-labelledby="hero-title">
        <h1 id="hero-title">Asterix orchestrates infrastructure cleanly</h1>
        <p>Launch, manage, and monitor hosts and services from a modern control layer.</p>
        <button type="button">Start now</button>
      </section>

      <section aria-labelledby="features-title">
        <h2 id="features-title">Why teams choose Asterix</h2>
        <article>
          <h3>Fast setup</h3>
          <p>Deploy infrastructure with less friction.</p>
        </article>
      </section>
    </main>

    <footer>
      <p>© 2026 Asterix</p>
    </footer>
  </body>
</html>
"""

if __name__ == "__main__":
    print("Semantic HTML solution ready.")
    print(HTML.strip()[:220])
