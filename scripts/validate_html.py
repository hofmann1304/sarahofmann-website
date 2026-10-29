"""Validate explicitly selected public HTML pages with W3C Nu."""
from pathlib import Path
import json
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

if len(sys.argv) < 2:
    raise SystemExit("Usage: python scripts/validate_html.py page.html [page.html ...]")
for filename in sys.argv[1:]:
    page = (ROOT / filename).resolve()
    if not page.is_relative_to(ROOT) or page.suffix != ".html":
        raise SystemExit("Only public HTML sources inside this repository are allowed")
    request = urllib.request.Request(
        "https://validator.w3.org/nu/?out=json",
        data=page.read_bytes(),
        headers={"Content-Type": "text/html; charset=utf-8", "User-Agent": "sarahofmann-site-check"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        messages = json.load(response)["messages"]
    if messages:
        print(json.dumps(messages, indent=2, ensure_ascii=False))
        raise SystemExit(f"FAIL: {filename}")
    print(f"PASS W3C: {filename}, zero messages")
