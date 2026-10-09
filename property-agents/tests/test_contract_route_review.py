import unittest
from contract_route_review import build_review_report


class ContractRouteReviewTests(unittest.TestCase):
    def test_accepts_list_and_keeps_actions_disabled(self):
        report = build_review_report([{"deal_id": "A"}, {"deal_id": "B"}])
        self.assertEqual(report["record_count"], 2)
        self.assertFalse(report["automatic_contacting"])
        self.assertFalse(report["automatic_offers"])
        self.assertFalse(report["automatic_contracting"])
        self.assertFalse(report["automatic_payments"])
        self.assertFalse(report["smartsheet_write"])

    def test_accepts_deals_object(self):
        report = build_review_report({"deals": [{"deal_id": "A"}]})
        self.assertEqual(report["record_count"], 1)
        self.assertEqual(report["review_items"][0]["deal_id"], "A")

    def test_rejects_ambiguous_input(self):
        with self.assertRaises(ValueError):
            build_review_report({"items": []})

    def test_rejects_non_object_deal(self):
        with self.assertRaises(ValueError):
            build_review_report({"deals": [{"deal_id": "A"}, "not-a-deal"]})


if __name__ == "__main__":
    unittest.main()
