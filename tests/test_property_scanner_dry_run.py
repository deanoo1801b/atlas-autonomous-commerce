import importlib.util
import tempfile
import unittest

from agents.property_query_classifier import is_rent_to_buy_query
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "agents" / "property_scanner_dry_run.py"
spec = importlib.util.spec_from_file_location("dryrun", MODULE_PATH)
dryrun = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dryrun)

class RentToBuyClassificationTests(unittest.TestCase):
    def test_classifies_common_rent_to_buy_query_variants(self):
        queries = [
            '"Rent to Buy" house "Dartford"',
            '"rent-to-buy" home "Grays Essex"',
            '"rent then buy" house "Dartford"',
            '"intermediate rent" "purchase" "Grays Essex"',
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertTrue(is_rent_to_buy_query(query))

    def test_does_not_classify_general_property_search(self):
        self.assertFalse(is_rent_to_buy_query('"property auction" house "Dartford"'))


class CanonicalUrlTests(unittest.TestCase):
    def test_rejects_non_http(self):
        self.assertEqual(dryrun.canonical_url("javascript:alert(1)"), "")

    def test_removes_tracking_and_fragment(self):
        self.assertEqual(
            dryrun.canonical_url("HTTPS://Example.com/property/?utm_source=x&ref=abc#top"),
            "https://example.com/property?ref=abc"
        )

    def test_rejects_missing_host(self):
        self.assertEqual(dryrun.canonical_url("https:///bad"), "")

if __name__ == "__main__":
    unittest.main()
