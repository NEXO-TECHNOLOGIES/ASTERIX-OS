import sys
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from ax_web_structure import (
        DOMNode,
        StructuralHTMLParser,
        prettify_html,
        prettify_js_css,
        extract_endpoints_from_code,
        WebStructureExtractor,
    )
except ImportError:
    # Try with hyphenated module name via importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("ax_web_structure", str(ROOT / "ax-web-structure.py"))
    ax_web_structure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ax_web_structure)
    DOMNode = ax_web_structure.DOMNode
    StructuralHTMLParser = ax_web_structure.StructuralHTMLParser
    prettify_html = ax_web_structure.prettify_html
    prettify_js_css = ax_web_structure.prettify_js_css
    extract_endpoints_from_code = ax_web_structure.extract_endpoints_from_code
    WebStructureExtractor = ax_web_structure.WebStructureExtractor


SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Asterix Cyber Portal</title>
    <meta name="description" content="Next Gen Security Platform">
    <link rel="stylesheet" href="/assets/style.css">
    <script src="/static/app.bundle.js" type="module"></script>
    <script>
        const API_BASE = '/api/v1/telemetry';
        fetch('/api/v2/auth/token');
    </script>
</head>
<body>
    <header id="main-header" class="header-dark flex-nav">
        <nav class="nav-container">
            <a href="/">Home</a>
            <a href="/login">Login</a>
        </nav>
    </header>
    <main id="content" class="container">
        <h1>Welcome to Asterix OS</h1>
        <form action="/api/v1/submit" method="POST" id="auth-form">
            <input type="text" name="username" value="operator">
            <input type="password" name="token">
            <button type="submit">Deploy</button>
        </form>
    </main>
    <footer>
        <p>Copyright 2026 Asterix</p>
    </footer>
</body>
</html>
"""


def test_html_parser_structure():
    parser = StructuralHTMLParser("https://asterix.os")
    parser.feed(SAMPLE_HTML)

    assert parser.title == "Asterix Cyber Portal"
    assert len(parser.scripts) == 2
    assert len(parser.stylesheets) == 1
    assert len(parser.forms) == 1

    # Check form inputs
    form = parser.forms[0]
    assert form["method"] == "POST"
    assert "/api/v1/submit" in form["action"]
    assert len(form["inputs"]) == 3


def test_prettify_html():
    minified = "<div><h1>Title</h1><p>Paragraph</p></div>"
    beautified = prettify_html(minified)
    assert "\n" in beautified
    assert "  <h1>" in beautified or "<div>\n" in beautified


def test_prettify_js_css():
    min_js = "function test(){console.log(1);return true;}"
    pretty_js = prettify_js_css(min_js)
    assert "\n" in pretty_js
    assert "console.log(1);" in pretty_js


def test_extract_endpoints():
    code = """
    function sync() {
        fetch('/api/v1/stats');
        axios.post('/api/v2/reports', {data: 1});
        const ws = new WebSocket('wss://asterix.os/stream');
    }
    """
    eps = extract_endpoints_from_code(code, "https://asterix.os")
    found_paths = [e["endpoint"] for e in eps]
    assert "/api/v1/stats" in found_paths
    assert "/api/v2/reports" in found_paths
    assert "wss://asterix.os/stream" in found_paths


def test_tech_stack_detection():
    extractor = WebStructureExtractor("https://example.com")
    extractor.html_body = SAMPLE_HTML + '<div data-reactroot=""></div><div class="sm:px-4 md:flex"></div>'
    extractor.headers = {"server": "cloudflare", "strict-transport-security": "max-age=31536000"}
    extractor._detect_technologies()
    extractor._audit_security_headers()

    assert "Cloudflare" in extractor.tech_stack
    assert "React" in extractor.tech_stack
    assert "Tailwind CSS" in extractor.tech_stack
    assert extractor.security_headers["Strict-Transport-Security (HSTS)"] is True
    assert extractor.security_headers["Content-Security-Policy (CSP)"] is False


def test_ascii_tree_generation():
    extractor = WebStructureExtractor("https://asterix.os")
    extractor.status_code = 200
    extractor.html_body = SAMPLE_HTML
    extractor.parse_structure()
    tree = extractor.generate_ascii_tree(max_depth=3)

    assert "Asterix Cyber Portal" in tree
    assert "JAVASCRIPT ARCHITECTURE" in tree
    assert "STYLESHEETS & DESIGN" in tree
    assert "<main>" in tree or "main" in tree


def test_dump_code_structure():
    with tempfile.TemporaryDirectory() as tmp_dir:
        extractor = WebStructureExtractor("https://asterix.os")
        extractor.status_code = 200
        extractor.html_body = SAMPLE_HTML
        extractor.parse_structure()
        res = extractor.dump_code_structure(tmp_dir)

        assert res["status"] == "success"
        out = Path(tmp_dir)
        assert (out / "index.html").exists()
        assert (out / "structure_tree.txt").exists()
        assert (out / "endpoints.json").exists()
        assert (out / "manifest.json").exists()
        assert (out / "tech_stack.json").exists()
        assert (out / "js").is_dir()
        assert (out / "css").is_dir()

        # Check endpoints json
        endpoints = json.loads((out / "endpoints.json").read_text(encoding="utf-8"))
        assert len(endpoints) >= 2


if __name__ == "__main__":
    test_html_parser_structure()
    test_prettify_html()
    test_prettify_js_css()
    test_extract_endpoints()
    test_tech_stack_detection()
    test_ascii_tree_generation()
    test_dump_code_structure()
    print("All Web Structure engine tests passed successfully!")
