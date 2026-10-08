"""Offline tests for the Inspiration Properties property engine."""
import os
import unittest

os.environ["ATLAS_PROPERTY_AGENT_DRY_RUN"] = "true"

from engine import _listing_fields, _stale_band
from open_properties_agent import to_property_lead
from motivated_seller_agent import motivation_score


class AdapterTests(unittest.TestCase):
    def test_open_properties_maps_to_valid_picklists(self):
        lead = to_property_lead({
            "id": "123",
            "portal": "rightmove",
            "url": "https://example.test/property/123",
            "address": "10 Test Street, London",
            "price": 500000,
            "listing_date": "2026-07-01T00:00:00+00:00",
        })
        self.assertEqual(lead["Lead Type"], "Open Market Listing")
        self.assertEqual(lead["Opportunity Type"], "Property Acquisition")
        self.assertEqual(lead["Contact Permission"], "Unknown")
        self.assertIn("listing_date", lead["Notes"])

    def test_motivation_score_is_bounded(self):
        self.assertGreaterEqual(motivation_score({"Lead Type": "Price Reduced"}), 0)
        self.assertLessEqual(motivation_score({"Lead Type": "Price Reduced"}), 100)


class HistoryTests(unittest.TestCase):
    def test_stale_bands_match_required_thresholds(self):
        self.assertEqual(_stale_band(60), "Normal")
        self.assertEqual(_stale_band(61), "Watch")
        self.assertEqual(_stale_band(90), "Watch")
        self.assertEqual(_stale_band(91), "Stale")
        self.assertEqual(_stale_band(120), "Stale")
        self.assertEqual(_stale_band(121), "Strong")
        self.assertEqual(_stale_band(180), "Strong")
        self.assertEqual(_stale_band(181), "Very Strong")
        self.assertEqual(_stale_band(270), "Very Strong")
        self.assertEqual(_stale_band(271), "Exceptional")

    def test_price_reduction_history_accumulates(self):
        previous = {
            "First Seen": "2026-07-01",
            "Original Asking Price": 500000,
            "Current Asking Price": 485000,
            "Reduction Count": 1,
            "Evidence History": "[]",
            "Motivation Score": 40,
            "Listing Status": "Active",
            "Source URL": "https://example.test/property/123",
        }
        current = {
            "Lead ID": "OP-123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/123",
            "Asking Price": 465000,
            "Motivation Score": 55,
        }
        result = _listing_fields(current, previous)
        self.assertEqual(result["Reduction Count"], 2)
        self.assertEqual(result["Reduction Amount"], 35000)
        self.assertEqual(result["Stale Band"], "Normal")
        self.assertIn('"price":465000.0', result["Evidence History"])


if __name__ == "__main__":
    unittest.main()
