#!/usr/bin/env python3
"""UX scoring rubric for dashboard and front-end exercises."""

RUBRIC = {
    "semantic_structure": 25,
    "visual_hierarchy": 20,
    "responsive_layout": 20,
    "action_clarity": 15,
    "status_readability": 10,
    "overall_polish": 10,
}


def score_ux_quality(output_text):
    text = (output_text or "").lower()
    score = 0
    checks = {
        "semantic_structure": ["header", "main", "nav", "section", "footer"],
        "visual_hierarchy": ["h1", "h2", "card", "metric", "panel"],
        "responsive_layout": ["grid", "flex", "media", "responsive", "mobile"],
        "action_clarity": ["button", "cta", "primary", "action", "start"],
        "status_readability": ["online", "healthy", "warning", "alert", "status"],
        "overall_polish": ["shadow", "spacing", "contrast", "radius", "clean"],
    }

    for category, keywords in checks.items():
        matches = sum(1 for keyword in keywords if keyword in text)
        if matches:
            score += min(RUBRIC[category], matches * (RUBRIC[category] // max(1, len(keywords))))

    return min(score, 100)


def audit_ui(text):
    score = score_ux_quality(text)
    report = {
        "score": score,
        "grade": "Excellent" if score >= 85 else "Good" if score >= 70 else "Needs work",
        "rubric": RUBRIC,
    }
    return report


if __name__ == "__main__":
    sample = """
    <header><nav>Home</nav></header>
    <main>
      <section>
        <h1>Control Center</h1>
        <div class="card">
          <p>Online</p>
          <button>Deploy VM</button>
        </div>
      </section>
    </main>
    <footer>Footer</footer>
    """
    print(audit_ui(sample))
