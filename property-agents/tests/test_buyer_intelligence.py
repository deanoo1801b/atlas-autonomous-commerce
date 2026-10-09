import unittest
from datetime import date
from buyer_intelligence import buyer_verification_status, match_buyer_to_deal

class BuyerIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.buyer = {"buyer_id":"B1","buyer_name":"Example Investor Ltd","identity_verified":True,"funding_evidence_status":"verified","verification_date":"2026-10-01","consent_status":"recorded","budget_max":250000,"areas":["Croydon"],"strategies":["flip refurb"],"minimum_profit_before_tax":20000}
        self.deal = {"asking_price":160000,"area":"Croydon, London","strategy":"flip refurb","estimated_net_profit_before_tax":30000,"comparable_sales_count":3,"valuation_review_status":"human_reviewed"}
    def test_current_verified_buyer_passes(self):
        self.assertEqual(buyer_verification_status(self.buyer, today=date(2026,10,9)), "Verified - human review recorded")
    def test_missing_identity_fails_closed(self):
        b = dict(self.buyer, identity_verified=False)
        self.assertEqual(buyer_verification_status(b, today=date(2026,10,9)), "Unverified identity")
    def test_stale_evidence_requires_reverification(self):
        b = dict(self.buyer, verification_date="2026-01-01")
        self.assertEqual(buyer_verification_status(b, today=date(2026,10,9)), "Re-verification required")
    def test_missing_consent_fails_closed(self):
        b = dict(self.buyer, consent_status="unknown")
        self.assertEqual(buyer_verification_status(b, today=date(2026,10,9)), "Buyer consent not recorded")
    def test_good_match_is_candidate_not_automatic_approval(self):
        result = match_buyer_to_deal(self.buyer, self.deal, today=date(2026,10,9))
        self.assertEqual(result["match_score"], 100)
        self.assertEqual(result["match_status"], "Strong candidate - human review required")
    def test_unverified_buyer_cannot_match(self):
        b = dict(self.buyer, identity_verified=False)
        result = match_buyer_to_deal(b, self.deal, today=date(2026,10,9))
        self.assertEqual(result["match_score"], 0)
        self.assertEqual(result["match_status"], "Not qualified")
    def test_over_budget_buyer_cannot_match(self):
        b = dict(self.buyer, budget_max=150000)
        result = match_buyer_to_deal(b, self.deal, today=date(2026,10,9))
        self.assertEqual(result["match_status"], "Not qualified")
    def test_missing_valuation_review_reduces_score(self):
        d = dict(self.deal, comparable_sales_count=1, valuation_review_status="unreviewed")
        result = match_buyer_to_deal(self.buyer, d, today=date(2026,10,9))
        self.assertEqual(result["match_score"], 90)

if __name__ == "__main__":
    unittest.main()
