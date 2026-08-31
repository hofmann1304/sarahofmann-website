from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ORIGIN = "https://sarahofmann.de"
CLOUDFLARE_ANALYTICS_SRC = "https://static.cloudflareinsights.com/beacon.min.js"
CLOUDFLARE_ANALYTICS_TOKEN = "4eafad2b955d48a8a7260434095148f2"
NOINDEX_FILES = {
    "404.html",
    "agb.html",
    "danke.html",
    "datenschutz.html",
    "impressum.html",
    "lebenslauf.html",
    "widerruf.html",
    "en/cv.html",
    "en/thank-you.html",
}
STRUCTURED_DATA_FILES = {
    "index.html",
    "uebermich.html",
    "consulting.html",
    "dozententaetigkeit.html",
    "nachhilfe.html",
    "insights/3d-druck-in-der-robotik.html",
    "insights/beruf-studium-balance.html",
    "insights/effektive-nachhilfe.html",
    "insights/interdisziplinaeres-denken.html",
    "insights/knowledge-graphs-industrielle-bildverarbeitung.html",
    "insights/matlab-simulink.html",
    "en/index.html",
    "en/about.html",
    "en/consulting.html",
    "en/lecturing.html",
    "en/tutoring.html",
    "en/insights/knowledge-graphs-industrial-machine-vision.html",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = []
        self.missing_alt = []
        self.blank_without_rel = []
        self.canonicals = []
        self.descriptions = []
        self.robots = []
        self.external_resources = []
        self.html_languages = []
        self.main_nav_depth = 0
        self.header_insight_links = []
        self.language_switchers = 0
        self.cloudflare_analytics = []
        self.h1_count = 0
        self.style_attributes = 0
        self.inline_script = False
        self.in_script_without_src = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "html":
            self.html_languages.append(attr.get("lang", ""))
        if tag == "nav" and "main-nav" in attr.get("class", "").split():
            self.main_nav_depth += 1
        if "lang-switcher" in attr.get("class", "").split():
            self.language_switchers += 1
        if tag == "a" and self.main_nav_depth and attr.get("href") in {"/insights", "/en/insights"}:
            self.header_insight_links.append(attr["href"])
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
            if attr.get("src") == CLOUDFLARE_ANALYTICS_SRC:
                self.cloudflare_analytics.append({
                    "type": attr.get("type", ""),
                    "config": attr.get("data-cf-beacon", ""),
                })
            self.in_script_without_src = (
                "src" not in attr
                and attr.get("type", "").lower() != "application/ld+json"
            )
        if tag == "link" and "canonical" in attr.get("rel", "").split():
            self.canonicals.append(attr.get("href", ""))
        if tag == "meta" and attr.get("name", "").lower() == "description":
            self.descriptions.append(attr.get("content", ""))
        if tag == "meta" and attr.get("name", "").lower() == "robots":
            self.robots.append(attr.get("content", "").lower())

        ref_attr = {"a": "href", "img": "src", "script": "src", "link": "href", "form": "action"}.get(tag)
        if ref_attr and attr.get(ref_attr):
            value = attr[ref_attr]
            self.refs.append((tag, value))
            parsed = urlparse(value)
            if parsed.scheme in {"http", "https"} and tag in {"img", "script", "link"}:
                if (
                    not value.startswith(PUBLIC_ORIGIN)
                    and value != CLOUDFLARE_ANALYTICS_SRC
                ):
                    self.external_resources.append(value)

    def handle_endtag(self, tag):
        if tag == "nav":
            self.main_nav_depth = max(0, self.main_nav_depth - 1)
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
    # GitHub Pages serves extensionless URLs from the matching .html file.
    # Check that variant before treating a same-named asset directory as an
    # index directory (for example /insights -> insights.html).
    if not Path(raw_path).suffix and target.with_suffix(".html").exists():
        return target.with_suffix(".html")
    if target.is_dir():
        target = target / "index.html"
    if target.exists():
        return target
    return target


def main():
    errors = []
    canonical_urls = set()
    indexable_titles = {}
    indexable_descriptions = {}
    html_files = sorted(ROOT.rglob("*.html"))

    for page in html_files:
        html_text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html_text)
        rel = page.relative_to(ROOT).as_posix()

        titles = [" ".join(title.split()) for title in re.findall(
            r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL
        )]
        if len(titles) != 1 or not titles[0]:
            errors.append(f"{rel}: genau ein nicht-leerer Seitentitel erwartet")
        if len(parser.descriptions) != 1 or not parser.descriptions[0].strip():
            errors.append(f"{rel}: genau eine nicht-leere Meta-Beschreibung erwartet")

        json_ld_blocks = re.findall(
            r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for block in json_ld_blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: ungültiges JSON-LD ({exc.msg})")
        if rel in STRUCTURED_DATA_FILES and not json_ld_blocks:
            errors.append(f"{rel}: erwartete strukturierte Daten fehlen")

        if parser.h1_count != 1:
            errors.append(f"{rel}: genau eine H1 erwartet, gefunden {parser.h1_count}")
        expected_language = "en" if rel.startswith("en/") else "de"
        if parser.html_languages != [expected_language]:
            errors.append(
                f"{rel}: HTML-Sprache muss genau {expected_language} sein, gefunden {parser.html_languages}"
            )
        if parser.language_switchers != 1:
            errors.append(f"{rel}: genau eine DE/EN-Sprachauswahl erwartet")
        if parser.header_insight_links:
            errors.append(f"{rel}: Insights darf nicht in der Hauptnavigation stehen")
        if "favicon-v2-32.png" not in html_text or "favicon-v2-16.png" not in html_text:
            errors.append(f"{rel}: neues transparentes Favicon fehlt")
        if len(parser.cloudflare_analytics) != 1:
            errors.append(f"{rel}: genau ein Cloudflare-Web-Analytics-Beacon erwartet")
        else:
            analytics = parser.cloudflare_analytics[0]
            try:
                analytics_config = json.loads(analytics["config"])
            except json.JSONDecodeError:
                analytics_config = {}
            if analytics["type"].lower() != "module":
                errors.append(f"{rel}: Cloudflare-Web-Analytics muss als Modul geladen werden")
            if analytics_config != {"token": CLOUDFLARE_ANALYTICS_TOKEN}:
                errors.append(f"{rel}: falsche Cloudflare-Web-Analytics-Konfiguration")
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
            if not any("noindex" in value for value in parser.robots):
                errors.append(f"{rel}: erwartete noindex-Anweisung fehlt")
            if parser.canonicals:
                errors.append(f"{rel}: Noindex-Seite darf keine Canonical-URL erhalten")
        else:
            if any("noindex" in value for value in parser.robots):
                errors.append(f"{rel}: indexierbare Seite enthält noindex")
            if len(parser.canonicals) != 1:
                errors.append(f"{rel}: genau eine Canonical-URL erwartet")
            elif not parser.canonicals[0].startswith(PUBLIC_ORIGIN):
                errors.append(f"{rel}: Canonical verweist nicht auf {PUBLIC_ORIGIN}")
            else:
                canonical_urls.add(parser.canonicals[0])
            if len(titles) == 1:
                indexable_titles.setdefault(titles[0], []).append(rel)
            if len(parser.descriptions) == 1:
                indexable_descriptions.setdefault(parser.descriptions[0], []).append(rel)

        if rel.startswith("insights/"):
            if 'rel="author"' not in html_text:
                errors.append(f"{rel}: verlinkte Autorenangabe fehlt")
            if "<time " not in html_text or "datetime=" not in html_text:
                errors.append(f"{rel}: maschinenlesbares Veröffentlichungsdatum fehlt")

        for tag, value in parser.refs:
            parsed_ref = urlparse(value)
            if (
                tag == "a"
                and not parsed_ref.scheme
                and parsed_ref.path.endswith(".html")
            ):
                errors.append(f"{rel}: interner Link verwendet .html statt Canonical-Pfad ({value})")
            target = local_target(page, value)
            if target is not None and not target.exists():
                errors.append(f"{rel}: fehlendes lokales Ziel für {tag}={value}")

    for title, pages in indexable_titles.items():
        if len(pages) > 1:
            errors.append(f"doppelter Seitentitel in {pages}: {title}")
    for description, pages in indexable_descriptions.items():
        if len(pages) > 1:
            errors.append(f"doppelte Meta-Beschreibung in {pages}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap.findall("sm:url/sm:loc", namespace)}
    if sitemap_urls != canonical_urls:
        errors.append(
            "sitemap.xml: URLs stimmen nicht mit den Canonical-URLs überein; "
            f"nur Sitemap={sorted(sitemap_urls - canonical_urls)}, nur HTML={sorted(canonical_urls - sitemap_urls)}"
        )

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "sarahofmann.de":
        errors.append("CNAME: erwartete GitHub-Pages-Domain sarahofmann.de fehlt")
    if not (ROOT / ".nojekyll").exists():
        errors.append(".nojekyll: Datei für die unveränderte statische Auslieferung fehlt")

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://sarahofmann.de/sitemap.xml" not in robots_text:
        errors.append("robots.txt: Sitemap-Verweis fehlt")
    if re.search(r"^\s*Disallow:\s*/(?:danke|lebenslauf)", robots_text, flags=re.MULTILINE):
        errors.append("robots.txt: Noindex-Seite darf nicht vom Crawling ausgeschlossen werden")

    contact_html = (ROOT / "kontakt.html").read_text(encoding="utf-8")
    if 'action="https://form.taxi/s/' not in contact_html:
        errors.append("kontakt.html: eigener Form.taxi-Endpunkt fehlt")
    if "data-netlify" in contact_html or "netlify-honeypot" in contact_html:
        errors.append("kontakt.html: veraltete Netlify-Formularattribute vorhanden")

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
