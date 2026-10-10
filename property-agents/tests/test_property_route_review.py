import json, os, tempfile, unittest
from property_route_review import build_review_queue, candidate_to_route_input, write_review_queue, render_review_html, write_review_html

class PropertyRouteReviewTests(unittest.TestCase):
    def test_mapping_does_not_invent_valuation_or_comparables(self):
        mapped = candidate_to_route_input({"Lead ID":"IP-1","Asking Price":140000})
        self.assertIsNone(mapped["estimated_market_value"])
        self.assertEqual(mapped["comparable_sales_count"], 0)
    def test_queue_keeps_both_routes_on_hold_by_default(self):
        report = build_review_queue([{"Lead ID":"IP-2","Area":"Croydon","Asking Price":140000,"Source URL":"https://example.test/listing"}],"SCAN-1")
        record = report["records"][0]
        self.assertEqual(report["candidate_count"],1)
        self.assertEqual(record["routes"]["property_sourcing"]["status"],"HOLD_FOR_REVIEW")
        self.assertEqual(record["routes"]["contract_assignment"]["status"],"HOLD_FOR_LEGAL_REVIEW")
        self.assertFalse(report["guardrails"]["writes_to_smartsheet"])
        self.assertFalse(record["automatic_contracting"])
    def test_html_summary_escapes_untrusted_property_text(self):
        report = build_review_queue([{"Lead ID":"<script>alert(1)</script>", "Area":"Croydon & Sutton"}], "SCAN-X")
        page = render_review_html(report)
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("NOT APPROVED TO TRANSACT", page)
        self.assertIn("Contract assignment", page)

    def test_html_shows_priority_bands_scores_and_reasons(self):
        from datetime import datetime, timezone, timedelta
        sold = (datetime.now(timezone.utc).date() - timedelta(days=45)).isoformat()
        comps = [{"sold_price": 185000, "sale_date": sold, "source_url": f"https://example.test/sold/{i}",
                  "postcode": "CR0 1AA", "property_type": "terraced"} for i in range(3)]
        report = build_review_queue([
            {"Lead ID":"IP-PRIORITY", "Area":"Croydon", "Source URL":"https://example.test/p",
             "Asking Price":140000, "Estimated Market Value":200000,
             "Comparable Sales Evidence":comps, "Proposed Sourcing Fee":3000},
            {"Lead ID":"IP-INCOMPLETE", "Area":"Sutton"}
        ], "SCAN-PRIORITY")
        page = render_review_html(report)
        self.assertIn("Evidence review work order", page)
        self.assertIn("<strong>Review evidence first:</strong> 1", page)
        self.assertIn("<strong>Incomplete record:</strong> 1", page)
        self.assertIn("Evidence score:", page)
        self.assertIn("Market value/comparable evidence incomplete", page)
        self.assertIn("<th>Evidence review priority</th>", page)
        self.assertIn("not indicate property quality", page)

    def test_html_file_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=os.path.join(tmp,"review.html")
            write_review_html(build_review_queue([], "SCAN-HTML"),path)
            with open(path,encoding="utf-8") as fh: page=fh.read()
            self.assertIn("SCAN-HTML",page)
            self.assertIn("No candidates in this run",page)

    def test_missing_source_url_is_scored_without_crashing(self):
        record = build_review_queue([{"Lead ID":"IP-NO-SOURCE"}],"SCAN-NO-SOURCE")["records"][0]
        self.assertEqual(record["review_priority_score"], 0)
        self.assertEqual(record["review_priority_band"], "Incomplete record")
        self.assertIn("No valid HTTPS source link", record["priority_reasons"])

    def test_priority_is_evidence_work_order_only(self):
        from datetime import datetime, timezone
        from datetime import timedelta
        sold = (datetime.now(timezone.utc).date() - timedelta(days=45)).isoformat()
        comps = [{"sold_price": 185000, "sale_date": sold, "source_url": f"https://example.test/sold/{i}",
                  "postcode": "CR0 1AA", "property_type": "terraced"} for i in range(3)]
        report = build_review_queue([{"Lead ID":"IP-P","Source URL":"https://example.test/p","Asking Price":140000,
            "Estimated Market Value":200000,"Comparable Sales Evidence":comps,"Proposed Sourcing Fee":3000}],"SCAN-P")
        record = report["records"][0]
        self.assertEqual(record["review_priority_band"],"Review evidence first")
        self.assertEqual(record["comparable_evidence"]["valid_count"],3)
        self.assertIn("not investment advice", report["priority_meaning"])
        self.assertFalse(record["automatic_offer"])

    def test_raw_comparable_count_does_not_verify_bmv_evidence(self):
        report = build_review_queue([{"Lead ID":"IP-RAW","Source URL":"https://example.test/p",
            "Asking Price":140000,"Estimated Market Value":200000,"Comparable Sales Count":12}], "SCAN-RAW")
        record = report["records"][0]
        self.assertEqual(record["comparable_evidence"]["valid_count"],0)
        self.assertEqual(record["valuation_status"],"review_required")
        self.assertNotEqual(record["review_priority_band"],"Review evidence first")

    def test_comparables_older_than_12_months_are_not_counted(self):
        from datetime import datetime, timezone, timedelta
        old_date = (datetime.now(timezone.utc).date() - timedelta(days=400)).isoformat()
        comps = [{"sold_price": 185000, "sale_date": old_date, "source_url": f"https://example.test/sold/{i}",
                  "postcode": "CR0 1AA", "property_type": "terraced"} for i in range(3)]
        record = build_review_queue([{"Lead ID":"IP-OLD","Asking Price":140000,"Estimated Market Value":200000,
            "Comparable Sales Evidence":comps}], "SCAN-OLD")["records"][0]
        self.assertEqual(record["comparable_evidence"]["valid_count"],0)
        self.assertTrue(any("sale within 12 months" in reason for reason in record["comparable_evidence"]["reasons"]))

    def test_queue_file_is_valid_json_and_audit_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=os.path.join(tmp,"queue.json")
            report=write_review_queue([{"Lead ID":"IP-3"}],"SCAN-2",path)
            with open(path,encoding="utf-8") as fh: loaded=json.load(fh)
            self.assertEqual(loaded["scan_id"],"SCAN-2")
            self.assertFalse(loaded["guardrails"]["writes_to_smartsheet"])
            self.assertEqual(report["mode"],"offline_human_review_queue")

if __name__ == "__main__": unittest.main()
