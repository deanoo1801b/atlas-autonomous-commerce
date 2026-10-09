"""Offline tests for the Inspiration Properties property engine."""
import os
import json
import tempfile
import unittest

os.environ["ATLAS_PROPERTY_AGENT_DRY_RUN"] = "true"

from engine import _identity_key, _listing_fields, _stale_band, finance_ready, compliance, _write_scan_report, removal_updates, classify_relisting, _property_relisting_key
from open_properties_agent import to_property_lead
from motivated_seller_agent import motivation_score, motivation_trend
from planning_opportunity_agent import analyse_planning_candidate, development_profit_scenario


class PlanningOpportunityTests(unittest.TestCase):
    def test_same_road_approved_extension_is_flagged_as_precedent(self):
        result = analyse_planning_candidate(
            {"Area": "12 Acacia Road, Croydon", "Postcode": "CR0 1AA"},
            [{"entity": 123, "address": "18 Acacia Road, Croydon", "description": "Two storey rear extension to provide additional bedroom", "decision": "Granted", "reference": "PL/123"}],
        )
        self.assertEqual(result["Planning Review Status"], "Same-road precedent found - verify")
        self.assertEqual(result["Planning Same-Road Count"], 1)
        self.assertIn("not permission for this property", result["Planning Opportunity Summary"])

    def test_unrelated_road_is_not_same_road_precedent(self):
        result = analyse_planning_candidate(
            {"Area": "12 Acacia Road, Croydon", "Postcode": "CR0 1AA"},
            [{"entity": 123, "address": "18 Elm Avenue, Croydon", "description": "Loft conversion and dormer", "decision": "Granted"}],
        )
        self.assertEqual(result["Planning Review Status"], "No matching records returned")

    def test_profit_scenario_requires_all_cost_inputs(self):
        result = development_profit_scenario(200000, 300000, works_cost=30000)
        self.assertIsNone(result["estimated_net_profit"])

    def test_profit_scenario_costs_contingency_and_net_profit(self):
        result = development_profit_scenario(200000, 300000, 30000, 5000, 6000, 10000, 5000, 10)
        self.assertEqual(result["contingency"], 3000)
        self.assertEqual(result["estimated_total_cost"], 259000)
        self.assertEqual(result["estimated_net_profit_before_tax"], 41000)


class BMVTests(unittest.TestCase):
    def test_30_percent_discount_is_priority_a(self):
        from engine import bmv_discount_pct, bmv_tier
        self.assertEqual(bmv_discount_pct(200000, 140000), 30.0)
        self.assertEqual(bmv_tier(200000, 140000, 3), "Priority A - 30%+ BMV")

    def test_25_percent_discount_is_priority_b(self):
        from engine import bmv_tier
        self.assertEqual(bmv_tier(200000, 150000, 3), "Priority B - 25-29.9% BMV")

    def test_bmv_without_three_comparables_fails_closed(self):
        from engine import bmv_tier
        self.assertEqual(bmv_tier(200000, 140000, 2), "Review - valuation evidence missing")

    def test_bmv_invalid_value_is_review(self):
        from engine import bmv_discount_pct, bmv_tier
        self.assertIsNone(bmv_discount_pct(None, 140000))
        self.assertEqual(bmv_tier(None, 140000, 5), "Review - valuation evidence missing")


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
        self.assertTrue(lead["Property Identity Key"].startswith("address:20 test road, london|postcode:sw1a 1aa"))

    def test_motivation_trend_detects_repeated_pressure(self):
        history = [{"motivation": 30, "price": 500000}, {"motivation": 45, "price": 475000}]
        self.assertGreater(motivation_trend(history, 60), 0)

    def test_motivation_trend_is_zero_without_history(self):
        self.assertEqual(motivation_trend([], 60), 0)

    def test_motivation_score_is_bounded(self):
        self.assertGreaterEqual(motivation_score({"Lead Type": "Price Reduced"}), 0)
        self.assertLessEqual(motivation_score({"Lead Type": "Price Reduced"}), 100)


class IdentityTests(unittest.TestCase):
    def test_canonical_url_removes_query_and_fragment(self):
        a = {
            "Lead ID": "LEGACY-1",
            "Source": "private-source",
            "Source URL": "https://example.test/property/1?utm_source=portal#details",
        }
        b = {
            "Lead ID": "LEGACY-2",
            "Source": "private-source",
            "Source URL": "https://example.test/property/1",
        }
        self.assertEqual(_identity_key(a), _identity_key(b))

    def test_open_market_identity_uses_provider_listing_id_over_url(self):
        a = {
            "Lead ID": "OP-abc123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/old",
        }
        b = {
            "Lead ID": "OP-abc123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/new",
        }
        self.assertEqual(_identity_key(a), _identity_key(b))

    def test_different_open_market_provider_ids_are_distinct(self):
        a = {
            "Lead ID": "OP-abc123",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/a",
        }
        b = {
            "Lead ID": "OP-def456",
            "Source": "open-properties/rightmove",
            "Source URL": "https://example.test/property/a",
        }
        self.assertNotEqual(_identity_key(a), _identity_key(b))


class RemovalGateTests(unittest.TestCase):
    def setUp(self):
        self.cmap = {
            "Lead ID": 1, "Source": 2, "Listing Status": 3,
            "Scan Miss Count": 4, "Last Scan ID": 5, "Removal Evidence": 6,
            "Property Identity Key": 7,
        }

    def _row(self, misses=0, status="Active"):
        return {
            "id": 101,
            "cells": [
                {"columnId": 1, "value": "OP-123"},
                {"columnId": 2, "value": "open-properties/rightmove"},
                {"columnId": 3, "value": status},
                {"columnId": 4, "value": misses},
                {"columnId": 7, "value": "open-properties/rightmove:id:123"},
            ],
        }

    def test_one_missed_complete_scan_does_not_remove(self):
        updates = removal_updates([self._row(0)], self.cmap, set(), True, "SCAN-1")
        values_flat = [cell["value"] for cell in updates[0]["cells"]]
        self.assertIn(1, values_flat)
        self.assertNotIn("Removed", values_flat)

    def test_second_consecutive_miss_marks_removed(self):
        updates = removal_updates([self._row(1)], self.cmap, set(), True, "SCAN-2")
        values_flat = [cell["value"] for cell in updates[0]["cells"]]
        self.assertIn("Removed", values_flat)
        self.assertIn(2, values_flat)

    def test_incomplete_scan_produces_no_removal_updates(self):
        self.assertEqual(
            removal_updates([self._row(1)], self.cmap, set(), False, "SCAN-INCOMPLETE"),
            [],
        )

    def test_seen_identity_is_not_counted_as_a_miss(self):
        self.assertEqual(
            removal_updates(
                [self._row(0)],
                self.cmap,
                {"open-properties/rightmove:id:123"},
                True,
                "SCAN-SEEN",
            ),
            [],
        )

class ScanAuditTests(unittest.TestCase):
    def _read_report(self, status, error=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "scan.json")
            old = os.environ.get("ATLAS_SCAN_REPORT_PATH")
            os.environ["ATLAS_SCAN_REPORT_PATH"] = path
            try:
                _write_scan_report("SCAN-TEST", 12, 9, True, status, error=error)
                with open(path, encoding="utf-8") as fh:
                    return json.load(fh)
            finally:
                if old is None:
                    os.environ.pop("ATLAS_SCAN_REPORT_PATH", None)
                else:
                    os.environ["ATLAS_SCAN_REPORT_PATH"] = old

    def test_success_audit_contains_scan_counts(self):
        report = self._read_report("SUCCESS")
        self.assertEqual(report["scan_id"], "SCAN-TEST")
        self.assertEqual(report["discovered_candidates"], 12)
        self.assertEqual(report["open_market_candidates"], 9)
        self.assertTrue(report["open_market_scan_complete"])
        self.assertEqual(report["status"], "SUCCESS")
        self.assertIsNone(report["error"])

    def test_failed_audit_preserves_error(self):
        report = self._read_report("FAILED", "RuntimeError: test failure")
        self.assertEqual(report["status"], "FAILED")
        self.assertEqual(report["error"], "RuntimeError: test failure")

class ConfigurationTests(unittest.TestCase):
    def test_compliance_defaults_to_amber(self):
        self.assertEqual(compliance({"Contact Permission": "Unknown"}), "Amber")

    def test_runtime_sheet_ids_are_not_hard_coded_in_engine(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "engine.py"), encoding="utf-8") as fh:
            source = fh.read()
        self.assertNotIn("95VHjPc74mJh2Q6485MHCqGjQP5p97wmW4x54Rg1", source)
        self.assertNotIn("3007077934124932", source)
        self.assertNotIn("890673877438340", source)


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


    def test_active_same_identity_is_not_relisted(self):
        previous = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/abc123","Property Identity Key":"open-properties/rightmove:id:abc123","Listing Status":"Active"}
        self.assertEqual(classify_relisting(previous, dict(previous)), (False, "Unknown"))

    def test_removed_same_identity_same_url_is_medium_relist(self):
        previous = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/abc123","Property Identity Key":"open-properties/rightmove:id:abc123","Listing Status":"Removed"}
        self.assertEqual(classify_relisting(previous, dict(previous)), (True, "Medium"))

    def test_removed_same_identity_changed_url_is_high_relist(self):
        previous = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/old","Property Identity Key":"open-properties/rightmove:id:abc123","Listing Status":"Removed"}
        current = dict(previous); current["Source URL"]="https://example.test/property/new"
        self.assertEqual(classify_relisting(previous, current), (True, "High"))
        self.assertEqual(_identity_key(current), "open-properties/rightmove:id:abc123")

    def test_removed_new_listing_id_same_property_is_relisted(self):
        previous = {"Lead ID":"OP-old","Source":"open-properties/rightmove","Source URL":"https://example.test/property/old","Property Identity Key":"open-properties/rightmove:id:old","Listing Status":"Removed","Area":"10 Test Street","Postcode":"SW1A 1AA"}
        current = {"Lead ID":"OP-new","Source":"open-properties/rightmove","Source URL":"https://example.test/property/new","Property Identity Key":"open-properties/rightmove:id:new","Listing Status":"Active","Area":"10 Test Street","Postcode":"SW1A 1AA"}
        self.assertEqual(_property_relisting_key(previous), _property_relisting_key(current))
        self.assertEqual(classify_relisting(previous, current), (True, "High"))

    def test_missing_postcode_does_not_create_soft_relist_match(self):
        previous = {"Lead ID":"OP-old","Source":"open-properties/rightmove","Listing Status":"Removed","Area":"10 Test Street"}
        current = {"Lead ID":"OP-new","Source":"open-properties/rightmove","Area":"10 Test Street"}
        self.assertIsNone(_property_relisting_key(previous))
        self.assertEqual(classify_relisting(previous, current), (False, "Unknown"))

    def test_broad_area_does_not_create_property_relist_match(self):
        previous = {"Lead ID":"OP-old","Source":"open-properties/rightmove","Listing Status":"Removed","Area":"Hampstead","Postcode":"NW3 1AA"}
        current = {"Lead ID":"OP-new","Source":"open-properties/rightmove","Listing Status":"Active","Area":"Hampstead","Postcode":"NW3 1AA"}
        self.assertIsNone(_property_relisting_key(previous))
        self.assertEqual(classify_relisting(previous, current), (False, "Unknown"))

    def test_removed_different_identity_is_not_relisted(self):
        previous = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/old","Property Identity Key":"open-properties/rightmove:id:abc123","Listing Status":"Removed"}
        current = {"Lead ID":"OP-def456","Source":"open-properties/rightmove","Source URL":"https://example.test/property/new","Property Identity Key":"open-properties/rightmove:id:def456","Listing Status":"Active"}
        self.assertEqual(classify_relisting(previous, current), (False, "Unknown"))

    def test_relisting_preserves_original_history(self):
        previous = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/old","Property Identity Key":"open-properties/rightmove:id:abc123","Listing Status":"Removed","First Seen":"2026-07-01","Original Asking Price":500000,"Current Asking Price":450000,"Reduction Count":2,"Evidence History":'[{"date":"2026-07-01","price":500000}]',"Motivation Score":60}
        current = {"Lead ID":"OP-abc123","Source":"open-properties/rightmove","Source URL":"https://example.test/property/new","Property Identity Key":"open-properties/rightmove:id:abc123","Asking Price":445000,"Motivation Score":65}
        result = _listing_fields(current, previous, *classify_relisting(previous, current))
        self.assertEqual(result["Listing Status"], "Relisted")
        self.assertEqual(result["First Seen"], "2026-07-01")
        self.assertEqual(result["Original Asking Price"], 500000)
        self.assertEqual(result["Reduction Count"], 3)
        self.assertIn('"price":500000', result["Evidence History"])

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
        self.assertEqual(result["Stale Band"], "Stale")
        self.assertIn('"price":465000.0', result["Evidence History"])


if __name__ == "__main__":
    unittest.main()
