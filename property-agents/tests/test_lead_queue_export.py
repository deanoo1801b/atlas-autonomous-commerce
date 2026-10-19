import csv
import tempfile
import unittest
from pathlib import Path

from lead_queue_export import export_review_queues, _spreadsheet_safe


class LeadQueueExportTests(unittest.TestCase):
    def test_separates_leads_into_review_queues(self):
        candidates = [
            {"Lead ID": "P1", "Lead Type": "Private Seller", "Source": "Owner Direct"},
            {"Lead ID": "P2", "Lead Type": "Open Market Listing", "Source": "open-properties/rightmove"},
            {"Lead ID": "P3", "Lead Type": "Developer Site", "Opportunity Type": "Development"},
            {"Lead ID": "F1", "Lead Type": "Finance Enquiry", "Opportunity Type": "Bridging"},
            {"Lead ID": "A1", "Lead Type": "Auction", "Opportunity Type": "Property Acquisition"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            result = export_review_queues(candidates, tmp)
            self.assertEqual(result["candidate_count"], 5)
            self.assertEqual(result["queues"]["private_seller_review.csv"]["count"], 1)
            self.assertEqual(result["queues"]["open_market_review.csv"]["count"], 1)
            self.assertEqual(result["queues"]["development_review.csv"]["count"], 1)
            self.assertEqual(result["queues"]["finance_review.csv"]["count"], 1)
            self.assertEqual(result["queues"]["property_acquisition_review.csv"]["count"], 1)
            for filename in result["queues"]:
                self.assertTrue((Path(tmp) / filename).exists())

    def test_csv_is_excel_compatible_and_formula_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_review_queues(
                [{"Lead ID": "P1", "Opportunity Evidence": "=HYPERLINK(\"https://example.com\",\"click\")"}],
                tmp,
            )
            with (Path(tmp) / "property_acquisition_review.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["Opportunity Evidence"], "'=HYPERLINK(\"https://example.com\",\"click\")")
        self.assertEqual(_spreadsheet_safe("-10"), "'-10")
        self.assertEqual(_spreadsheet_safe(10), 10)

    def test_export_reports_local_only_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = export_review_queues([], tmp)
        self.assertIn("no contact", result["safety"].lower())
        self.assertEqual(result["candidate_count"], 0)


if __name__ == "__main__":
    unittest.main()
