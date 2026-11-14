"""Tests for the discovery scout, Scheduled audit/discovery/harvest_shopify.py.

Run from the project root (no network):
    python3 -m unittest discover -s "Scheduled audit/tests" -v
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "discovery"))
import harvest_shopify as hs  # noqa: E402

BASE = "https://revitsport.com/en-us"


def product(title, ptype="Jackets", tags=("RegularUS", "Men's"), body="", available=True,
            price="499.99", handle=None, images=2):
    colour = title.split(" | ", 1)[1] if " | " in title else "Black"
    return {
        "title": title,
        "handle": handle or hs.slugify("en " + title),
        "product_type": ptype,
        "tags": list(tags),
        "body_html": body,
        "options": [{"name": "Color", "values": [colour]},
                    {"name": "Size", "values": ["S", "M"]},
                    {"name": "Length", "values": ["standard"]}],
        "variants": [{"price": price, "available": available}],
        "images": [{"src": f"https://cdn.example/{i}.jpg"} for i in range(images)],
    }


class UsFilterTest(unittest.TestCase):
    def test_regular_and_outlet_are_us(self):
        self.assertTrue(hs.is_us(product("Jacket A | Black", tags=["RegularUS"])))
        self.assertTrue(hs.is_us(product("Jacket A | Black", tags=["OutletUS"])))

    def test_other_markets_dropped(self):
        self.assertFalse(hs.is_us(product("Jacket A | Black", tags=["RegularEU", "Men's"])))
        models, _ = hs.build_models([product("Jacket A | Black", tags=["RegularEU"])], BASE)
        self.assertEqual(models, [])


class GroupingTest(unittest.TestCase):
    def setUp(self):
        self.products = [
            product("Jacket Fractal H2O | Blue-White", tags=["RegularUS", "Men's", "PS-FJT428"], available=False),
            product("Jacket Fractal H2O | Black", tags=["RegularUS", "Men's", "PS-FJT428"]),
            product("Jacket Fractal H2O | Dark Blue", tags=["OutletUS", "Men's", "PS-FJT428"]),
            product("Jacket Fractal H2O Ladies | Black", tags=["RegularUS", "Women's", "PS-FJT429"]),
            product("Pants Fractal H2O | Black", ptype="Pants", tags=["RegularUS", "Men's", "PS-FPT100"]),
            product("Smock Photon |  Dark Blue-Green", ptype="Rain gear", tags=["RegularUS", "Unisex"]),
        ]
        self.models, self.doubts = hs.build_models(self.products, BASE)
        self.by_name = {m["model_name"]: m for m in self.models}

    def test_colourways_collapse_into_one_model(self):
        m = self.by_name["Jacket Fractal H2O"]
        self.assertEqual(len(m["colourways"]), 3)
        self.assertEqual({c["colour"] for c in m["colourways"]}, {"Blue-White", "Black", "Dark Blue"})

    def test_ladies_and_pants_are_separate_models(self):
        self.assertIn("Jacket Fractal H2O Ladies", self.by_name)
        self.assertIn("Pants Fractal H2O", self.by_name)
        self.assertEqual(len(self.models), 4)

    def test_extra_space_after_pipe(self):
        self.assertIn("Smock Photon", self.by_name)
        self.assertEqual(self.by_name["Smock Photon"]["colourways"][0]["colour"], "Dark Blue-Green")

    def test_title_without_pipe_strips_colour(self):
        p = product("Gloves Sand 5 | Black")
        p["title"] = "Gloves Sand 5 Black"
        self.assertEqual(hs.base_title(p), "Gloves Sand 5")

    def test_representative_prefers_stock_then_black(self):
        rep = self.by_name["Jacket Fractal H2O"]["representative"]
        self.assertEqual(rep["colour"], "Black")
        cws = [{"colour": "Red", "available": True}, {"colour": "Black", "available": False}]
        self.assertEqual(hs.pick_representative(cws)["colour"], "Red")

    def test_record_fields(self):
        m = self.by_name["Jacket Fractal H2O"]
        self.assertFalse(m["outlet"])  # only one colourway is OutletUS
        self.assertEqual(m["gender_tags"], ["Men's"])
        self.assertTrue(m["in_scope"])
        cw = m["colourways"][0]
        self.assertTrue(cw["url"].startswith(BASE + "/products/"))
        self.assertEqual(len(cw["images"]), 2)

    def test_scope(self):
        models, _ = hs.build_models([product("Hoodie Colin | Black", ptype="Casuals")], BASE)
        self.assertFalse(models[0]["in_scope"])

    def test_style_code_split_is_doubtful(self):
        ps = [product("Jacket X | Black", tags=["RegularUS", "PS-1"]),
              product("Jacket X Pro | Red", tags=["RegularUS", "PS-1"])]
        _, doubts = hs.build_models(ps, BASE)
        self.assertTrue(any("split across" in r for d in doubts for r in d["reasons"]))


class PrefilterTest(unittest.TestCase):
    def status(self, **kw):
        models, _ = hs.build_models([product("Gloves Test | Black", ptype="Gloves", **kw)], BASE)
        return models[0]["prefilter"]

    def test_leather_tag_drops(self):
        pf = self.status(tags=["RegularUS", "Leather"])
        self.assertEqual(pf["status"], "leather_tag")

    def test_leather_tag_on_one_colourway_drops_model(self):
        ps = [product("Gloves T | Black", ptype="Gloves", tags=["RegularUS"]),
              product("Gloves T | Brown", ptype="Gloves", tags=["RegularUS", "Leather"])]
        models, doubts = hs.build_models(ps, BASE)
        self.assertEqual(models[0]["prefilter"]["status"], "leather_tag")
        self.assertTrue(doubts)

    def test_keyword_makes_suspect(self):
        pf = self.status(body="<p>Palm in <b>drum dyed goatskin</b> for grip.</p>")
        self.assertEqual(pf["status"], "suspect")
        self.assertEqual(pf["keyword_hits"][0]["term"], "goatskin")
        self.assertIn("goatskin", pf["keyword_hits"][0]["snippet"])
        self.assertLessEqual(len(pf["keyword_hits"][0]["snippet"]), 80)

    def test_word_boundaries(self):
        pf = self.status(body="Further ventilation, a cowl collar and downtube clearance.")
        self.assertEqual(pf["status"], "candidate")

    def test_clean_textile_is_candidate(self):
        self.assertEqual(self.status(body="PWR|Shell and polyester mesh.")["status"], "candidate")


def tab(head, items):
    body = "".join(f"<h2>{h}</h2><p class=\"feature-item\">{p}</p>" for h, p in items)
    return (
        '<div class="collapsible-tabs__block"><div class="collapsible-tabs__tab"><details-disclosure>'
        f'<details class="disclosure"><summary class="disclosure__title"> {head} </summary>'
        '<div class="disclosure__panel has-motion"><div class="disclosure__content rte">'
        f'<div class="product-features"><div class="feature-group"><div class="feature-list">{body}'
        "</div></div></div></div></div></details></details-disclosure></div></div>"
    )


def page(h1, tabs, price='<span class="price__was"></span><span class="price__current"><span>$669.99 USD</span></span>',
         cert="Class AA certified according to standard EN 17092-3:2020", desc="A riding jacket."):
    return f"""<html><head><title>{h1} | Black &ndash; REV'IT!</title>
<link rel="canonical" href="https://revitsport.com/en-us/products/x"></head><body>
<div class="title-row"><h1 class="product-title">
     {h1}   </h1></div>
<div class="product-info__price product-price"><div class="price"><div class="price__default">{price}</div></div></div>
<details class="disclosure"><summary class="disclosure__title">Description</summary>
<div class="disclosure__panel"><div class="disclosure__content rte cf">{desc}<br><br>Second paragraph.</div></div></details>
<details class="disclosure"><summary class="disclosure__title">Specs and features</summary>
<div class="disclosure__content"><a href="#faq-extra-information">View all specs and features</a></div></details>
<div class="wrap_certified_container"><div class="wrap_certified"><div class="wrap_cert_content"><div><h5></h5><p>{cert}</p></div></div></div>
<div class="wrap_certified sustainability-icon"><div class="wrap_cert_content"><div><p>We want to shape a sustainable future.</p></div></div></div></div>
<footer>Leather jackets | Suede gloves</footer>
<div class="collapsible-tabs"><h3 id="faq-extra-information">Extra information</h3>{''.join(tabs)}</div>
</body></html>"""


class SpecExtractorTest(unittest.TestCase):
    def test_fractal_vegan_label_without_outer_shell(self):
        html = page("Jacket Fractal H2O", [
            tab("Lining", [("3D mesh", ""), ("Mesh", "")]),
            tab("Protection inserts", [("SEEFLEX CE-level 2 Elbow Protectors",
                                        "Certified CE-level 2 according to the new norm EN 1621-1:2012 the SEEFLEX "
                                        "protector is new. It is comfortable.")]),
            tab("Sustainability", [("Vegan", ""), ("Outer shell made with recycled polyamide", "Strong.")]),
        ])
        out = hs.extract_specs(html, "u")
        self.assertEqual(out["h1"], "Jacket Fractal H2O")
        self.assertNotIn("Outer shell", out["accordions"])
        self.assertTrue(out["vegan_label"]["present"])
        self.assertEqual(out["vegan_label"]["quote"], "Vegan")
        self.assertEqual(out["accordions"]["Lining"], ["3D mesh", "Mesh"])
        self.assertIn("Class AA certified according to standard EN 17092-3:2020", out["certifications"])
        self.assertTrue(any("EN 1621-1:2012" in c and "comfortable" not in c for c in out["certifications"]))
        self.assertEqual(out["price"], {"current": "$669.99 USD", "original": "", "on_sale": False})
        self.assertEqual(out["description"], "A riding jacket.\nSecond paragraph.")
        self.assertFalse(out["is_404"])

    def test_leather_materials_listed_and_chrome_ignored(self):
        html = page("Gloves Cassini H2O", [
            tab("Outer shell", [("Flock PU", "Flocking adheres small fibre particles."),
                                ("Drum dyed goatskin", "This goatskin has been drum dyed.")]),
            tab("Sustainability", [("DWR C0 Sustainable water repellent finish", "")]),
        ], price='<span class="price__was"><span>$109.99 USD</span></span>'
                 '<span class="price__current has-sale"><span>$76.99 USD</span></span>',
            cert="Level 1 KP certified according to standard EN 13594:2015")
        out = hs.extract_specs(html, "u")
        self.assertEqual(out["accordions"]["Outer shell"][1],
                         "Drum dyed goatskin: This goatskin has been drum dyed.")
        self.assertFalse(out["vegan_label"]["present"])
        self.assertEqual(out["vegan_mentions"], [])
        self.assertTrue(out["price"]["on_sale"])
        self.assertEqual(out["price"]["original"], "$109.99 USD")
        self.assertEqual(out["certifications"], ["Level 1 KP certified according to standard EN 13594:2015"])
        flat = " ".join(line for lines in out["accordions"].values() for line in lines)
        self.assertNotIn("Suede", flat)

    def test_404_page(self):
        html = ("<html><head><title>404 Not Found &ndash; REV'IT! Sport International</title></head>"
                '<body><div class="product-info__price"><span class="price__current">$42.99 USD</span></div></body></html>')
        out = hs.extract_specs(html, "u")
        self.assertTrue(out["is_404"])
        self.assertEqual(out["h1"], "")
        self.assertEqual(out["price"]["current"], "")


if __name__ == "__main__":
    unittest.main()
