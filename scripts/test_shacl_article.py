"""Regression tests for the bilingual SHACL teaching example.

Requires pyshacl==0.40.1 and rdflib==7.6.0 in a separate test environment.
No project data or remote documents are loaded.
"""
from html import unescape
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest

from rdflib import Graph, Literal, Namespace, RDF
from pyshacl import validate

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "de": "insights/shacl-knowledge-graph-validierung-python",
    "en": "en/insights/shacl-knowledge-graph-validation-python",
}
EX = Namespace("https://example.org/engineering/")


def blocks(language):
    text = (ROOT / (PATHS[language] + ".html")).read_text(encoding="utf-8")
    return [unescape(block) for block in re.findall(
        r'<code class="language-(?:turtle|python)">(.*?)</code>',
        text, re.S
    )]


class ArticleTests(unittest.TestCase):
    def setUp(self):
        self.data_text, self.shapes_text, self.code = blocks("de")
        self.data = Graph().parse(data=self.data_text, format="turtle")
        self.shapes = Graph().parse(data=self.shapes_text, format="turtle")

    def conforms(self):
        result, _, _ = validate(
            self.data, shacl_graph=self.shapes, inference="none",
            meta_shacl=True, advanced=False,
            allow_infos=False, allow_warnings=False,
        )
        return result

    def test_translation_code_identical(self):
        self.assertEqual(blocks("de"), blocks("en"))

    def test_metadata(self):
        for language, path in PATHS.items():
            text = (ROOT / (path + ".html")).read_text(encoding="utf-8")
            article = json.loads(re.search(
                r'<script type="application/ld\+json">(.*?)</script>',
                text, re.S
            )[1])
            self.assertEqual(article["@type"], "Article")
            self.assertEqual(article["inLanguage"], language)
            self.assertEqual(article["mainEntityOfPage"], "https://sarahofmann.de/" + path)
            self.assertEqual(article["datePublished"], "2026-09-25")
            for alternate, target in {**PATHS, "x-default": PATHS["de"]}.items():
                self.assertIn(
                    f'hreflang="{alternate}" href="https://sarahofmann.de/{target}"',
                    text,
                )

    def test_valid(self):
        self.assertTrue(self.conforms())

    def test_missing_source(self):
        self.data.remove((EX["decision-17"], EX.source, None))
        self.assertFalse(self.conforms())

    def test_literal_evidence(self):
        self.data.set((EX["decision-17"], EX.evidence, Literal("test-9")))
        self.assertFalse(self.conforms())

    def test_second_status(self):
        self.data.add((EX["decision-17"], EX.status, EX.Draft))
        self.assertFalse(self.conforms())

    def test_missing_type(self):
        self.data.remove((EX["decision-17"], RDF.type, None))
        self.assertFalse(self.conforms())

    def test_target_gap_is_explicit(self):
        self.data.remove((EX["decision-17"], RDF.type, None))
        self.data.remove((EX["decision-17"], EX.status, None))
        self.assertTrue(self.conforms())

    def test_unresolved_reference_passes(self):
        self.data.set((EX["decision-17"], EX.evidence, EX["not-described"]))
        self.assertTrue(self.conforms())

    def test_empty_graph_passes_shape_only(self):
        self.data = Graph()
        self.assertTrue(self.conforms())

    def test_actual_script_exit_codes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="shacl-article-test-") as folder:
            work = Path(folder)
            inputs = {
                "data.ttl": self.data_text,
                "shapes.ttl": self.shapes_text,
                "validate_graph.py": self.code,
            }
            for name, content in inputs.items():
                (work / name).write_text(content, encoding="utf-8")
            run = subprocess.run(
                [sys.executable, "validate_graph.py"], cwd=work,
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            for name, content in inputs.items():
                self.assertEqual((work / name).read_text(encoding="utf-8"), content)
            invalid = self.data_text.replace("ex:source ex:document-4 ;", "")
            (work / "data.ttl").write_text(invalid, encoding="utf-8")
            run = subprocess.run(
                [sys.executable, "validate_graph.py"], cwd=work,
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertIn("Conforms: False", run.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
