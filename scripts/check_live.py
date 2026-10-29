"""Compare the published HTTPS sitemap and pages with this exact checkout."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from check_site import PageParser, CLOUDFLARE_ANALYTICS_TOKEN, PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0", "Referer": PUBLIC_ORIGIN + "/",
    })
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.status, response.url, response.headers, response.read().decode("utf-8")


def normalized(text):
    return text.replace("\r\n", "\n").strip()


def verify(url):
    status, final, headers, text = fetch(url)
    assert status == 200 and final == url, (url, status, final)
    parser = PageParser()
    parser.feed(text)
    assert parser.canonicals == [url], url
    assert not any("noindex" in value for value in parser.robots), url
    assert "noindex" not in headers.get("X-Robots-Tag", "").lower(), url
    assert len(parser.cloudflare_analytics) == 1, url
    beacon = parser.cloudflare_analytics[0]
    assert beacon["type"] == "module", url
    assert json.loads(beacon["config"]) == {"token": CLOUDFLARE_ANALYTICS_TOKEN}, url
    path = urlparse(url).path
    local = ROOT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ".html"))
    assert normalized(text) == normalized(local.read_text(encoding="utf-8")), url
    expected = PageParser()
    expected.feed(local.read_text(encoding="utf-8"))
    assert sorted(parser.hreflangs) == sorted(expected.hreflangs), url
    for block in re.findall(r'<script\b[^>]*type=["\x27]application/ld\+json["\x27][^>]*>(.*?)</script>', text, re.S):
        json.loads(block)
    return url


if __name__ == "__main__":
    status, final, _, sitemap = fetch(PUBLIC_ORIGIN + "/sitemap.xml")
    assert status == 200 and final == PUBLIC_ORIGIN + "/sitemap.xml"
    assert normalized(sitemap) == normalized((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    urls = [node.text for node in ET.fromstring(sitemap).findall("{*}url/{*}loc")]
    assert len(urls) == len(set(urls))
    assert all(url.startswith(PUBLIC_ORIGIN + "/") for url in urls)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(verify, urls))
    for url in ("http://sarahofmann.de/", "https://www.sarahofmann.de/"):
        assert fetch(url)[:2] == (200, PUBLIC_ORIGIN + "/"), url
    assert "Sitemap: " + PUBLIC_ORIGIN + "/sitemap.xml" in fetch(PUBLIC_ORIGIN + "/robots.txt")[3]
    assert fetch("https://static.cloudflareinsights.com/beacon.min.js")[0] == 200
    print(f"PASS LIVE: {len(urls)} URLs, valid TLS/HTTPS, 200, exact content, canonical, hreflang, JSON-LD, beacon, sitemap, redirects.")
    print("Beacon presence does not prove dashboard ingestion or Google indexing.")
