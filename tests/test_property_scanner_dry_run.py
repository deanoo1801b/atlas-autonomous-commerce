import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "agents" / "property_scanner_dry_run.py"
spec = importlib.util.spec_from_file_location("dryrun", MODULE_PATH)
dryrun = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dryrun)

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
