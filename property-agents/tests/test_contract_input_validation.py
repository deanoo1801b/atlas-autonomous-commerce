import unittest

from contract_route_comparator import compare_routes
from property_route_review import _bmv_review_tier


class ContractInputValidationTests(unittest.TestCase):
    def test_non_finite_money_does_not_produce_discount(self):
        for value in ("nan", "inf", "-inf", -1):
            with self.subTest(value=value):
                result = compare_routes({
                    "deal_id": "IP-INVALID-PRICE",
                    "asking_price": value,
                    "estimated_market_value": 200000,
                    "comparable_sales_count": 3,
                })
                self.assertIsNone(result["market_value_discount_pct"])
                self.assertEqual(result["valuation_status"], "review_required")

    def test_invalid_comparable_counts_do_not_meet_three_sale_threshold(self):
        for count in ("3.5", -1, True, "nan", "inf", "unknown"):
            with self.subTest(count=count):
                result = compare_routes({
                    "deal_id": "IP-INVALID-COMPS",
                    "asking_price": 140000,
                    "estimated_market_value": 200000,
                    "comparable_sales_count": count,
                })
                self.assertEqual(result["valuation_status"], "review_required")

    def test_non_finite_and_boolean_discounts_cannot_receive_bmv_tier(self):
        for discount in (float("nan"), float("inf"), float("-inf"), True, False, None):
            with self.subTest(discount=discount):
                self.assertIn("REVIEW_REQUIRED", _bmv_review_tier(discount, 3))


if __name__ == "__main__":
    unittest.main()
