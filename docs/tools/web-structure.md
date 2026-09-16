# 🌐 `web-structure` — Deep Web DOM & Source Inspector

An advanced web architecture analyzer that maps the DOM hierarchy, extracts script and stylesheet dependencies, traces API endpoints, and reconstructs website structures offline.

---

## 📌 Usage

```bash
ax web-structure <url>
ax curl-tree <url>
ax webdump <url> <output-dir>
```

Direct script invocation:
```bash
python scripts-hub/ax-web-structure.py <url>
```

---

## ⚙️ Key Capabilities

- **Visual DOM Hierarchy (`ax curl-tree <url>`)**: Renders an ASCII tree of the remote website's HTML document object model with tag depths and node counts.
- **Asset Dependency Mapping**: Extracts all linked `.js`, `.css`, image, font, and API websocket endpoints.
- **Offline Code Reconstructor (`ax webdump <url> <dir>`)**: Recursively fetches HTML and referenced static assets, adjusting relative links for offline code analysis.
- **Zero Third-Party Dependencies**: Built entirely with Python standard library (`urllib`, `html.parser`).
