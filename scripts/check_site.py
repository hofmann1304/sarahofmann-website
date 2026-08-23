from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ORIGIN = "https://sarahofmann.de"
NOINDEX_FILES = {"404.html", "danke.html"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = []
        self.missing_alt = []
        self.blank_without_rel = []
        self.canonicals = []
        self.external_resources = []
        self.h1_count = 0
        self.style_attributes = 0
        self.inline_script = False
        self.in_script_without_src = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if "id" in attr:
            self.ids.append(attr["id"])
        if "style" in attr:
            self.style_attributes += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in attr:
            self.missing_alt.append(attr.get("src", "<ohne src>"))
        if attr.get("target") == "_blank" and "noopener" not in attr.get("rel", "").split():
            self.blank_without_rel.append(attr.get("href", "<ohne href>"))
        if tag == "script":
            self.in_script_without_src = "src" not in attr
        if tag == "link" and "canonical" in attr.get("rel", "").split():
            self.canonicals.append(attr.get("href", ""))

        ref_attr = {"a": "href", "img": "src", "script": "src", "link": "href", "form": "action"}.get(tag)
        if ref_attr and attr.get(ref_attr):
            value = attr[ref_attr]
            self.refs.append((tag, value))
            parsed = urlparse(value)
            if parsed.scheme in {"http", "https"} and tag in {"img", "script", "link"}:
                if not value.startswith(PUBLIC_ORIGIN):
                    self.external_resources.append(value)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script_without_src = False

    def handle_data(self, data):
        if self.in_script_without_src and data.strip():
            self.inline_script = True


def local_target(page, value):
    parsed = urlparse(value)
    if parsed.scheme or value.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    raw_path = parsed.path
    if not raw_path:
        return None
    target = (ROOT / raw_path.lstrip("/")) if raw_path.startswith("/") else (page.parent / raw_path)
    target = target.resolve()
    if target.is_dir():
        target = target / "index.html"
    if target.exists():
        return target
    if not target.suffix and target.with_suffix(".html").exists():
        return target.with_suffix(".html")
    return target


def main():
    errors = []
    canonical_urls = set()
    html_files = sorted(ROOT.rglob("*.html"))

    for page in html_files:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        rel = page.relative_to(ROOT).as_posix()

        if parser.h1_count != 1:
            errors.append(f"{rel}: genau eine H1 erwartet, gefunden {parser.h1_count}")
        duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicate_ids:
            errors.append(f"{rel}: doppelte IDs {duplicate_ids}")
        if parser.missing_alt:
            errors.append(f"{rel}: Bilder ohne Alt-Attribut {parser.missing_alt}")
        if parser.blank_without_rel:
            errors.append(f"{rel}: target=_blank ohne rel=noopener {parser.blank_without_rel}")
        if parser.style_attributes:
            errors.append(f"{rel}: Inline-Style-Attribute gefunden")
        if parser.inline_script:
            errors.append(f"{rel}: Inline-Script gefunden")
        if parser.external_resources:
            errors.append(f"{rel}: externe aktive Ressource {parser.external_resources}")

        if rel in NOINDEX_FILES:
            if parser.canonicals:
                errors.append(f"{rel}: Noindex-Seite darf keine Canonical-URL erhalten")
        else:
            if len(parser.canonicals) != 1:
                errors.append(f"{rel}: genau eine Canonical-URL erwartet")
            elif not parser.canonicals[0].startswith(PUBLIC_ORIGIN):
                errors.append(f"{rel}: Canonical verweist nicht auf {PUBLIC_ORIGIN}")
            else:
                canonical_urls.add(parser.canonicals[0])

        for tag, value in parser.refs:
            target = local_target(page, value)
            if target is not None and not target.exists():
                errors.append(f"{rel}: fehlendes lokales Ziel für {tag}={value}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap.findall("sm:url/sm:loc", namespace)}
    if sitemap_urls != canonical_urls:
        errors.append(
            "sitemap.xml: URLs stimmen nicht mit den Canonical-URLs überein; "
            f"nur Sitemap={sorted(sitemap_urls - canonical_urls)}, nur HTML={sorted(canonical_urls - sitemap_urls)}"
        )

    config = tomllib.loads((ROOT / "netlify.toml").read_text(encoding="utf-8"))
    header_values = [entry.get("values", {}) for entry in config.get("headers", []) if entry.get("for") == "/*"]
    required_headers = {
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
    }
    if not header_values or not required_headers.issubset(header_values[0]):
        errors.append("netlify.toml: erforderliche Sicherheitsheader fehlen")

    if errors:
        print("VERÖFFENTLICHUNGSCHECK FEHLGESCHLAGEN")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        f"VERÖFFENTLICHUNGSCHECK BESTANDEN: {len(html_files)} HTML-Seiten, "
        f"{len(canonical_urls)} indexierbare URLs, keine fehlenden lokalen Ziele."
    )


if __name__ == "__main__":
    main()
