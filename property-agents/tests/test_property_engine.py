"""Offline tests for the Inspiration Properties property engine."""
import unittest

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


if __name__ == "__main__":
    unittest.main()
