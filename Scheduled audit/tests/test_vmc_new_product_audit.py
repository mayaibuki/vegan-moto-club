"""Tests for the deterministic matching in vmc_new_product_audit.py.

Run from the project root (no network, no Notion token needed):
    python3 -m unittest discover -s "Scheduled audit/tests" -v
"""
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import vmc_new_product_audit as audit  # noqa: E402


class BrandMatcherTest(unittest.TestCase):
    def setUp(self):
        audit.OPTIONS.clear()
        audit.OPTIONS.update({k: list(v) for k, v in audit.VALID.items()})

    def brand(self, text, url="https://www.revzilla.com/p/x", name=""):
        return audit.infer_brand(text.lower(), url, name)

    def test_no_substring_matches(self):
        # "icon" inside "silicon", "bison" inside "bisonte": no brand.
        self.assertIsNone(self.brand("Silicone grip palm with silicon print"))
        self.assertIsNone(self.brand("Bisonte-style stitching"))

    def test_ambiguous_word_brands_ignored_in_page_text(self):
        self.assertIsNone(self.brand("Armor is held in place. Click the cart icon. Five stars."))
        self.assertIsNone(self.brand("Not made with bison leather"))

    def test_ambiguous_brand_from_product_name_or_domain(self):
        self.assertEqual(self.brand("", name="Held Air n Dry II Gloves"), "Held")
        self.assertEqual(self.brand("", url="https://www.rideicon.com/products/airform"), "Icon")

    def test_whole_word_and_punctuation_variants(self):
        self.assertEqual(self.brand("The Rev'it Eclipse 2 jacket"), "REV'IT!")
        self.assertEqual(self.brand("Pando Moto Boss jeans"), "Pando Moto")
        self.assertEqual(self.brand("Bull it Jeans SR6"), "Bull-it Jeans")

    def test_domain_beats_text(self):
        self.assertEqual(
            self.brand("Also pairs well with Alpinestars boots",
                       url="https://www.revitsport.com/en-us/products/x"),
            "REV'IT!")


class SchemaFilterTest(unittest.TestCase):
    def setUp(self):
        audit.OPTIONS.clear()
        audit.OPTIONS.update({k: list(v) for k, v in audit.VALID.items()})

    def test_unknown_options_are_dropped(self):
        out = audit.filter_to_schema({
            "Riding style": ["Street", "Commute / Street"],
            "Brand": "Speed and Strenght",
            "Materials": ["Polyester; Mesh fabric", "Polyester"],
        })
        self.assertEqual(out["Riding style"], ["Commute / Street"])
        self.assertIsNone(out["Brand"])
        self.assertEqual(out["Materials"], ["Polyester"])

    def test_exact_notion_spelling_kept(self):
        out = audit.filter_to_schema({"Level of Waterproof": "Waterproof (Gore-tex®) "})
        self.assertEqual(out["Level of Waterproof"], "Waterproof (Gore-tex®) ")

    def test_junk_options(self):
        self.assertTrue(audit.is_junk_option("Nylon, Polymer, Electronics"))
        self.assertTrue(audit.is_junk_option("Mesh fabric; Polyester"))
        self.assertFalse(audit.is_junk_option("Cordura® (Synhtetic fabric)"))


class LoadSchemaTest(unittest.TestCase):
    def test_fallback_when_fetch_fails(self):
        with mock.patch.object(audit, "_fetch_notion_schema", side_effect=RuntimeError("HTTP 401")):
            src = audit.load_schema_options("db", "token")
        self.assertIn("hardcoded", src)
        self.assertEqual(audit.OPTIONS["Brand"], audit.VALID["Brand"])

    def test_live_schema_wins_and_junk_is_ignored(self):
        props = {
            "Brand": {"type": "select", "select": {"options": [
                {"name": "Held"}, {"name": "Brand New Co"}]}},
            "Materials": {"type": "multi_select", "multi_select": {"options": [
                {"name": "Polyester"}, {"name": "Polyester; Mesh fabric"}]}},
        }
        with mock.patch.object(audit, "_fetch_notion_schema", return_value=props):
            src = audit.load_schema_options("db", "token")
        self.assertTrue(src.startswith("live Notion schema"))
        self.assertEqual(audit.OPTIONS["Brand"], ["Held", "Brand New Co"])
        self.assertEqual(audit.OPTIONS["Materials"], ["Polyester"])
        # Fields missing from the response keep the hardcoded list.
        self.assertEqual(audit.OPTIONS["Season"], audit.VALID["Season"])


if __name__ == "__main__":
    unittest.main()
