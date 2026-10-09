import json, os, tempfile, unittest
from property_route_review import build_review_queue, candidate_to_route_input, write_review_queue

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
    def test_queue_file_is_valid_json_and_audit_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=os.path.join(tmp,"queue.json")
            report=write_review_queue([{"Lead ID":"IP-3"}],"SCAN-2",path)
            with open(path,encoding="utf-8") as fh: loaded=json.load(fh)
            self.assertEqual(loaded["scan_id"],"SCAN-2")
            self.assertFalse(loaded["guardrails"]["writes_to_smartsheet"])
            self.assertEqual(report["mode"],"offline_human_review_queue")

if __name__ == "__main__": unittest.main()
