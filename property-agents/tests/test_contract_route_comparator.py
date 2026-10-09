import unittest
from contract_route_comparator import compare_routes


class ContractRouteComparatorTests(unittest.TestCase):
    def test_missing_data_fails_closed(self):
        result = compare_routes({"deal_id": "D-1"})
        self.assertEqual(result["overall_status"], "HUMAN_AND_SOLICITOR_REVIEW_REQUIRED")
        self.assertEqual(result["routes"]["contract_assignment"]["status"], "HOLD_FOR_LEGAL_REVIEW")
        self.assertFalse(result["automatic_commitment"])
        self.assertIsNone(result["market_value_discount_pct"])

    def test_discount_needs_three_comparables(self):
        result = compare_routes({"asking_price": 140000, "estimated_market_value": 200000,
                                 "comparable_sales_count": 2})
        self.assertEqual(result["market_value_discount_pct"], 30.0)
        self.assertEqual(result["valuation_status"], "review_required")
        self.assertTrue(any("Fewer than three" in x for x in result["routes"]["property_sourcing"]["risks"]))

    def test_assignment_rights_and_solicitor_are_hard_stops(self):
        result = compare_routes({
            "assignment_fee": 5000, "contract_purchase_price": 140000, "deposit_at_risk": 5000,
            "assignment_permitted": False, "seller_consent_required": True,
            "seller_consent_obtained": False, "solicitor_reviewed": False,
            "title_checked": False, "aml_status": "registered", "redress_status": "member",
            "fee_disclosed": True, "marketing_authority_confirmed": True,
        })
        route = result["routes"]["contract_assignment"]
        self.assertEqual(route["status"], "HOLD_FOR_LEGAL_REVIEW")
        self.assertTrue(any("assignment rights" in x for x in route["blockers"]))
        self.assertTrue(any("seller consent" in x for x in route["blockers"]))
        self.assertTrue(any("solicitor" in x for x in route["blockers"]))

    def test_sourcing_route_still_requires_regulatory_gates(self):
        result = compare_routes({
            "sourcing_fee": 3000, "buyer_identified": True, "buyer_funding_reviewed": True,
            "human_reviewed": True, "fee_disclosed": True, "marketing_authority_confirmed": True,
            "aml_status": "unknown", "redress_status": "unknown",
        })
        route = result["routes"]["property_sourcing"]
        self.assertEqual(route["status"], "HOLD_FOR_REVIEW")
        self.assertEqual(len(route["blockers"]), 2)

    def test_green_checks_still_do_not_auto_approve(self):
        result = compare_routes({
            "deal_id": "D-2", "asking_price": 140000, "estimated_market_value": 200000,
            "comparable_sales_count": 3, "source_evidence_url": "https://example.com/listing",
            "sourcing_fee": 3000, "assignment_fee": 5000, "contract_purchase_price": 140000,
            "deposit_at_risk": 5000, "assignment_permitted": True,
            "seller_consent_required": False, "solicitor_reviewed": True, "title_checked": True,
            "buyer_identified": True, "buyer_funding_reviewed": True, "fee_disclosed": True,
            "aml_status": "registered", "redress_status": "member",
            "marketing_authority_confirmed": True, "human_reviewed": True,
        })
        self.assertEqual(result["routes"]["property_sourcing"]["status"], "ELIGIBLE_FOR_SOLICITOR/COMPLIANCE_REVIEW")
        self.assertEqual(result["routes"]["contract_assignment"]["status"], "ELIGIBLE_FOR_SOLICITOR/COMPLIANCE_REVIEW")
        self.assertEqual(result["overall_status"], "HUMAN_AND_SOLICITOR_REVIEW_REQUIRED")
        self.assertFalse(result["automatic_commitment"])
        self.assertFalse(result["automatic_contracting"])


if __name__ == "__main__":
    unittest.main()
