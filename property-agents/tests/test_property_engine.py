"""Offline tests for the Inspiration Properties property engine."""
import os
import unittest

os.environ["ATLAS_PROPERTY_AGENT_DRY_RUN"] = "true"

from engine import _identity_key, _listing_fields, _stale_band, finance_ready
from open_properties_agent import to_property_lead
from motivated_seller_agent import motivation_score, motivation_trend


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

    def test_open_properties_preserves_portal_id_and_postcode(self):
        lead = to_property_lead({
            "id": "rm-456", "portal": "rightmove",
            "url": "https://example.test/property/rm-456",
            "address": "20 Test Road, London", "postcode": "SW1A 1AA",
            "price": 650000,
        })
        self.assertEqual(lead["Portal Listing ID"], "rm-456")
        self.assertEqual(lead["Postcode"], "SW1A 1AA")

    def test_motivation_trend_detects_repeated_pressure(self):
        history = [{"motivation": 30, "price": 500000}, {"motivation": 45, "price": 475000}]
        self.assertGreater(motivation_trend(history, 60), 0)

    def test_motivation_trend_is_zero_without_history(self):
        self.assertEqual(motivation_trend([], 60), 0)

    def test_motivation_score_is_bounded(self):
        self.assertGreaterEqual(motivation_score({"Lead Type": "Price Reduced"}), 0)
        self.assertLessEqual(motivation_score({"Lead Type": "Price Reduced"}), 100)


class FinanceGateTests(unittest.TestCase):
    def test_finance_gate_requires_source_or_opportunity_evidence(self):
        self.assertFalse(finance_ready({"Asking Price": 250000, "Listing Status": "Active"}))

    def test_finance_gate_requires_asking_price(self):
        self.assertFalse(finance_ready({"Source URL": "https://example.test/property/1", "Listing Status": "Active"}))

    def test_finance_gate_rejects_removed_listing(self):
        self.assertFalse(finance_ready({
            "Source URL": "https://example.test/property/1",
            "Asking Price": 250000,
            "Listing Status": "Removed",
        }))

    def test_finance_gate_rejects_do_not_contact(self):
        self.assertFalse(finance_ready({
            "Source URL": "https://example.test/property/1",
            "Asking Price": 250000,
            "Listing Status": "Active",
            "Do Not Contact": True,
        }))

    def test_finance_gate_accepts_minimum_verified_evidence(self):
        self.assertTrue(finance_ready({
            "Source URL": "https://example.test/property/1",
            "Asking Price": "250000",
            "Listing Status": "Active",
            "Contact Permission": "Unknown",
        }))


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


    def test_identity_key_uses_open_properties_provider_id(self):
        lead = {
            "Lead ID": "OP-abc123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/abc123?foo=bar",
        }
        self.assertEqual(_identity_key(lead), "open-properties/rightmove:id:abc123")

    def test_relisting_is_flagged_for_same_identity_after_removed_status(self):
        previous = {
            "First Seen": "2026-07-01",
            "Original Asking Price": 500000,
            "Current Asking Price": 450000,
            "Reduction Count": 2,
            "Evidence History": "[]",
            "Motivation Score": 60,
            "Listing Status": "Removed",
            "Source URL": "https://example.test/property/old",
        }
        current = {
            "Lead ID": "OP-abc123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/new",
            "Asking Price": 445000,
            "Motivation Score": 65,
        }
        result = _listing_fields(current, previous, relisting=True, relisting_confidence="High")
        self.assertEqual(result["Listing Status"], "Relisted")
        self.assertTrue(result["Relisting Flag"])
        self.assertEqual(result["Relisting Confidence"], "High")

    def test_reappearing_removed_listing_is_relisted_with_medium_confidence(self):
        previous = {
            "First Seen": "2026-07-01", "Original Asking Price": 500000,
            "Current Asking Price": 450000, "Reduction Count": 2,
            "Evidence History": "[]", "Motivation Score": 60,
            "Listing Status": "Removed",
            "Source URL": "https://example.test/property/abc123",
            "Lead ID": "OP-abc123", "Source": "open-properties/rightmove",
            "Property Identity Key": "open-properties/rightmove:id:abc123",
        }
        current = {
            "Lead ID": "OP-abc123", "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/abc123",
            "Asking Price": 445000, "Motivation Score": 65,
            "Property Identity Key": "open-properties/rightmove:id:abc123",
        }
        self.assertEqual(_listing_fields(current, previous, relisting=True, relisting_confidence="Medium")["Listing Status"], "Relisted")

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
