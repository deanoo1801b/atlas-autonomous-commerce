import json
import tempfile
import unittest
from pathlib import Path
from buyer_prospecting import load_buyer_prospects, buyer_candidates

class BuyerProspectingTests(unittest.TestCase):
    def test_seed_register_loads_with_all_prospects_unverified(self):
        data = load_buyer_prospects()
        self.assertGreaterEqual(len(data["records"]), 5)
        self.assertTrue(all(r["identity_verified"] is False for r in data["records"]))
        self.assertTrue(all(not r["verification_status"].startswith("Verified") for r in data["records"]))
    def test_networks_are_not_misclassified_as_buyers(self):
        data = load_buyer_prospects()
        self.assertTrue(all(not r["record_type"].startswith("Investor-network") for r in buyer_candidates(data["records"])))
    def test_geography_filter_returns_relevant_public_candidates(self):
        data = load_buyer_prospects()
        self.assertTrue(any(r["name"] == "No.12 London" for r in buyer_candidates(data["records"], geography=["London"])))
    def test_register_rejects_accidental_verified_status(self):
        data = {"contacting_enabled":False,"referral_enabled":False,"publishing_enabled":False,"records":[{"prospect_id":"X","verification_status":"Verified","identity_verified":False,"evidence_url":"https://example.org"}]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"register.json"; p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): load_buyer_prospects(p)
    def test_register_requires_https_evidence(self):
        data = {"contacting_enabled":False,"referral_enabled":False,"publishing_enabled":False,"records":[{"prospect_id":"X","verification_status":"Public profile found","identity_verified":False,"evidence_url":"http://example.org"}]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"register.json"; p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): load_buyer_prospects(p)

if __name__ == "__main__": unittest.main()
