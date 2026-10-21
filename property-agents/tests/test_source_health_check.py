"""Offline tests for the read-only source health report."""
import unittest
from unittest.mock import Mock, patch

import source_health_check as health


class SourceHealthCheckTests(unittest.TestCase):
    def test_empty_planning_dataset_is_reported_as_coverage_warning(self):
        response = Mock()
        response.json.return_value = {"entities": []}
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response

        result = health.check_planning_data(session=session)

        self.assertEqual(result["status"], "reachable_but_empty")
        self.assertIn("local council register", result["warning"])

    def test_planning_api_failure_is_not_misreported_as_empty_dataset(self):
        session = Mock()
        session.get.side_effect = TimeoutError("timeout")

        result = health.check_planning_data(session=session)

        self.assertEqual(result["status"], "unavailable_or_query_failed")
        self.assertEqual(result["error_type"], "TimeoutError")

    def test_land_registry_query_failure_is_reported(self):
        result = health.check_land_registry(fetcher=Mock(side_effect=RuntimeError("endpoint error")))

        self.assertEqual(result["status"], "unavailable_or_query_failed")
        self.assertEqual(result["error_type"], "RuntimeError")

    def test_report_never_claims_to_have_created_leads_or_contacted_sellers(self):
        report = health.build_report(
            {"source": "HMLR", "status": "reachable_with_records"},
            {"source": "Planning", "status": "reachable_but_empty"},
        )

        self.assertEqual(report["overall_status"], "PARTIAL_DATA_COVERAGE")
        self.assertEqual(report["explicit_non_actions"]["property_candidates_created"], 0)
        self.assertEqual(report["explicit_non_actions"]["seller_contacts_sent"], 0)
        self.assertEqual(report["explicit_non_actions"]["production_writes"], 0)


if __name__ == "__main__":
    unittest.main()
