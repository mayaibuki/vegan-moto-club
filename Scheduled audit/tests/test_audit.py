"""Offline tests for vmc_new_product_audit.py (no network, no Notion writes).

Run from the project root:
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
        audit.VALID = {k: list(v) for k, v in audit.FALLBACK_VALID.items()}

    def brand(self, text, url="https://www.revzilla.com/motorcycle/some-jacket", name=""):
        return audit.infer_brand(text.lower(), url, name)

    def test_substrings_inside_other_words_do_not_match(self):
        # Used to return "Icon" / "Bison" via substring matching.
        self.assertIsNone(self.brand("silicone grip panels and lexicon of features"))
        self.assertIsNone(self.brand("bisonte leather alternative, iconic styling"))

    def test_whole_words_match(self):
        self.assertEqual(self.brand("bison synthetic trousers"), "Bison")
        self.assertEqual(self.brand("rev'it! sand 4 h2o"), "REV'IT!")
        self.assertEqual(self.brand("tourmaster transition jacket"), "Tour Master")

    def test_common_word_brands_need_name_or_domain(self):
        # "held" / "icon" in body copy are ordinary words, not the brand.
        self.assertIsNone(self.brand("armor is held in place; tap the cart icon"))
        self.assertEqual(self.brand("", name="Held Air n Dry II Gloves"), "Held")
        self.assertEqual(self.brand("", name="Icon Airflow Jacket"), "Icon")

    def test_new_brands_are_recognised(self):
        self.assertEqual(self.brand("pando moto boss jeans"), "Pando Moto")
        self.assertEqual(self.brand("", "https://www.held.de/en/p/x"), "Held")

    def test_store_domain_wins(self):
        self.assertEqual(self.brand("", "https://www.revitsport.com/products/x"), "REV'IT!")
        self.assertEqual(self.brand("", "https://icon-motosports.com/p/x"), "Icon")
        self.assertIsNone(self.brand("", "https://ridericonic.com/p/x"))


class SchemaTest(unittest.TestCase):
    def test_fallback_matches_known_notion_spelling(self):
        fb = audit.FALLBACK_VALID
        self.assertNotIn("Street", fb["Riding style"])
        self.assertIn("Waterproof (Gore-tex®) ", fb["Level of Waterproof"])
        self.assertIn("Cordura® (Synhtetic fabric)", fb["Materials"])
        self.assertTrue({"Pando Moto", "Held"} <= set(fb["Brand"]))
        self.assertFalse([m for m in fb["Materials"] if audit._is_junk_option(m)])

    def test_keyword_maps_only_emit_valid_options(self):
        fb = audit.FALLBACK_VALID
        styles = audit.infer_riding_style("Streetbike adventure racing jacket", "")
        self.assertTrue(set(styles) <= set(fb["Riding style"]), styles)
        mats = audit.infer_materials(
            "cordura gore-tex kevlar dyneema mesh fabric nylon polyester cotton "
            "denim spandex elastane ykk microfiber vibram carbon fiber titanium "
            "neoprene d3o ripstop amara clarino primaloft thinsulate sas-tec level 1 "
            "sas-tec level 2 ax laredo armalith heavyweight denim")
        self.assertTrue(set(mats) <= set(fb["Materials"]), set(mats) - set(fb["Materials"]))

    def test_filter_to_schema_drops_unknown_values(self):
        audit.VALID = {k: list(v) for k, v in audit.FALLBACK_VALID.items()}
        out = audit.filter_to_schema({
            "Riding style": ["Street", "Commute / Street"],
            "Brand": "Not A Brand",
            "Season": ["☀️ Summer"],
        })
        self.assertEqual(out["Riding style"], ["Commute / Street"])
        self.assertIsNone(out["Brand"])
        self.assertEqual(out["Season"], ["☀️ Summer"])

    def test_options_from_properties_skips_junk(self):
        props = {f: {"type": "multi_select", "multi_select": {"options": [{"name": "A"}]}}
                 for f in audit.FALLBACK_VALID}
        props["Materials"]["multi_select"]["options"] = [
            {"name": "Nylon"}, {"name": "Nylon, Polyester, Ripstop nylon"},
            {"name": "Polyester; Mesh fabric"}]
        self.assertEqual(audit._options_from_properties(props)["Materials"], ["Nylon"])

    def test_falls_back_when_fetch_fails(self):
        with mock.patch.object(audit, "fetch_live_options", side_effect=RuntimeError("boom")), \
             mock.patch.object(audit, "NOTION_TOKEN", "x"):
            self.assertEqual(audit.load_valid_options(), "hardcoded fallback")
        self.assertEqual(audit.VALID, audit.FALLBACK_VALID)


if __name__ == "__main__":
    unittest.main()
