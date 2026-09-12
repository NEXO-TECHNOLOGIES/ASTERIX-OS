#!/usr/bin/env python3
"""Mock admin dashboard challenge."""

HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>ASTERIX Control Center</title>
    <style>
      body { font-family: Arial, sans-serif; background: #0b1020; color: #e2e8f0; margin: 0; }
      .shell { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; }
      .sidebar { background: #111827; padding: 24px; }
      .main { padding: 24px; }
      .cards { display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: 18px; }
      .card { background: #1f2937; border-radius: 12px; padding: 18px; }
      button { background: #22c55e; color: #04130a; border: none; padding: 10px 16px; border-radius: 8px; }
    </style>
  </head>
  <body>
    <div class="shell">
      <aside class="sidebar">
        <h2>Menu</h2>
        <nav>
          <p>Overview</p>
          <p>Nodes</p>
          <p>Deployments</p>
        </nav>
      </aside>
      <main class="main">
        <header>
          <h1>Control Center</h1>
          <button>Deploy VM</button>
        </header>
        <section class="cards">
          <article class="card"><h3>Hosts</h3><p>4 online</p></article>
          <article class="card"><h3>VMs</h3><p>12 running</p></article>
          <article class="card"><h3>Alerts</h3><p>3 need review</p></article>
        </section>
      </main>
    </div>
  </body>
</html>
"""

if __name__ == "__main__":
    print(HTML.strip())
