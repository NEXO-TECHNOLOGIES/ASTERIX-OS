#!/usr/bin/env python3
"""UX audit example for dashboard-like interfaces."""

from scoring_system import audit_ui

SAMPLE = """
<header>
  <nav>Overview</nav>
</header>
<main>
  <section>
    <h1>System health</h1>
    <div class="card">
      <p>Healthy</p>
      <button>Deploy VM</button>
    </div>
  </section>
</main>
<footer>All systems nominal</footer>
"""

if __name__ == "__main__":
    print(audit_ui(SAMPLE))
