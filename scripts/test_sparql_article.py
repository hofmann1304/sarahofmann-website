"""Execute the actual bilingual SPARQL examples on their synthetic data."""
from html import unescape
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest

from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "de": "insights/sparql-fehlende-nachweise-knowledge-graph",
    "en": "en/insights/sparql-missing-evidence-knowledge-graph",
}
EX = Namespace("https://example.org/engineering/")


def source(language):
    return (ROOT / (PAGES[language] + ".html")).read_text(encoding="utf-8")


def blocks(language):
    return [unescape(block) for block in re.findall(
        r'<code class="language-(?:turtle|sparql|python)">(.*?)</code>',
        source(language), re.S,
    )]


class SparqlTests(unittest.TestCase):
    def setUp(self):
        self.data, self.missing, self.qualified, self.report, self.runner = blocks("de")
        self.graph = Graph().parse(data=self.data, format="turtle")

    def ids(self, query):
        return {row.decision for row in self.graph.query(query)}

    def test_translations_match_and_read_only(self):
        self.assertEqual(blocks("de"), blocks("en"))
        before = set(self.graph)
        self.assertEqual(self.ids(self.missing), {EX.d2})
        self.assertEqual(self.ids(self.qualified), {EX.d2, EX.d3, EX.d4})
        self.assertEqual(set(self.graph), before)

    def test_optional_rows_and_unbound(self):
        rows = list(self.graph.query(self.report))
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({row.decision for row in rows}), 4)
        self.assertEqual(sum(row.decision == EX.d1 for row in rows), 2)
        self.assertIsNone(next(row for row in rows if row.decision == EX.d2).evidence)

    def test_add_qualifying_evidence(self):
        self.graph.add((EX.d2, EX.evidence, EX.testA))
        self.assertEqual(self.ids(self.missing), set())
        self.assertEqual(self.ids(self.qualified), {EX.d3, EX.d4})

    def test_extra_source_does_not_change_gap_lists(self):
        self.graph.add((EX.d2, EX.source, EX.docF))
        self.assertEqual(self.ids(self.missing), {EX.d2})
        self.assertEqual(self.ids(self.qualified), {EX.d2, EX.d3, EX.d4})
        self.assertEqual(len(list(self.graph.query(self.report))), 6)

    def test_missing_type_is_a_selection_gap(self):
        self.graph.remove((EX.d2, RDF.type, EX.Decision))
        self.assertEqual(self.ids(self.missing), set())
        self.assertEqual(self.ids(self.qualified), {EX.d3, EX.d4})
        self.assertNotIn(EX.d2, self.ids(self.report))

    def test_empty_graph_is_not_coverage(self):
        self.graph = Graph()
        for query in (self.missing, self.qualified, self.report):
            self.assertEqual(self.ids(query), set())

    def test_external_filter_drops_missing_bindings(self):
        query = self.report.replace(
            "OPTIONAL { ?decision ex:evidence ?evidence . }",
            "OPTIONAL { ?decision ex:evidence ?evidence . }\n"
            "FILTER(?evidence = ex:testA)",
        )
        self.assertEqual(self.ids(query), {EX.d1})

    def test_metadata_and_pair(self):
        for lang, path in PAGES.items():
            text = source(lang)
            article = json.loads(re.search(
                r'<script type="application/ld\+json">(.*?)</script>', text, re.S
            )[1])
            self.assertEqual(article["@type"], "Article")
            self.assertEqual(article["inLanguage"], lang)
            self.assertEqual(article["mainEntityOfPage"], "https://sarahofmann.de/" + path)
            self.assertEqual(article["datePublished"], "2026-11-13")
            self.assertEqual(article["dateModified"], "2026-11-13")
            for hreflang, target in {**PAGES, "x-default": PAGES["de"]}.items():
                self.assertIn(f'hreflang="{hreflang}" href="https://sarahofmann.de/{target}"', text)

    def test_actual_runner_and_input_preservation(self):
        with tempfile.TemporaryDirectory(prefix="sparql-article-") as folder:
            work = Path(folder)
            files = {
                "decisions.ttl": self.data, "missing.rq": self.missing,
                "qualified.rq": self.qualified, "report.rq": self.report,
                "query_decisions.py": self.runner,
            }
            for name, content in files.items():
                (work / name).write_text(content, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "query_decisions.py"], cwd=work,
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(lines[0], "missing")
            self.assertEqual(lines[2], "qualified")
            self.assertEqual(lines[6], "report")
            self.assertEqual(len(lines), 12)
            self.assertIn("None", result.stdout)
            for name, content in files.items():
                self.assertEqual((work / name).read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
