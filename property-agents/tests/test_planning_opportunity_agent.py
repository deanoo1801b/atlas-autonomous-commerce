import unittest

from planning_opportunity_agent import development_profit_scenario


class DevelopmentProfitScenarioTests(unittest.TestCase):
    def setUp(self):
        self.complete = {
            "asking_price": 200000,
            "estimated_completed_value": 300000,
            "works_cost": 30000,
            "professional_fees": 5000,
            "finance_and_holding": 6000,
            "purchase_costs": 10000,
            "selling_costs": 9000,
        }

    def test_complete_costed_scenario_calculates_contingency_and_net_profit(self):
        result = development_profit_scenario(**self.complete)
        self.assertIn("Illustrative only", result["status"])
        self.assertEqual(result["contingency"], 4500)
        self.assertEqual(result["estimated_total_cost"], 264500)
        self.assertEqual(result["estimated_net_profit_before_tax"], 35500)
        self.assertEqual(result["estimated_margin_on_end_value_pct"], 11.83)

    def test_missing_any_required_cost_fails_closed(self):
        for field in ("works_cost", "professional_fees", "finance_and_holding",
                      "purchase_costs", "selling_costs"):
            with self.subTest(field=field):
                inputs = dict(self.complete)
                inputs[field] = None
                result = development_profit_scenario(**inputs)
                self.assertIsNone(result["estimated_net_profit"])
                self.assertIn("no profit estimate published", result["status"])

    def test_zero_or_invalid_purchase_and_completed_value_fail_closed(self):
        for field, value in (("asking_price", 0), ("asking_price", -1),
                             ("estimated_completed_value", 0),
                             ("estimated_completed_value", "nan"),
                             ("estimated_completed_value", "inf")):
            with self.subTest(field=field, value=value):
                inputs = dict(self.complete)
                inputs[field] = value
                result = development_profit_scenario(**inputs)
                self.assertIsNone(result["estimated_net_profit"])

    def test_invalid_costs_fail_closed(self):
        for value in (-1, "nan", "inf", "not a cost"):
            with self.subTest(value=value):
                inputs = dict(self.complete)
                inputs["works_cost"] = value
                result = development_profit_scenario(**inputs)
                self.assertIsNone(result["estimated_net_profit"])

    def test_contingency_rate_must_be_finite_and_between_zero_and_100(self):
        for value in (-1, 100.01, "nan", "inf", "unknown"):
            with self.subTest(value=value):
                result = development_profit_scenario(**self.complete, contingency_pct=value)
                self.assertIsNone(result["estimated_net_profit"])
                self.assertIn("invalid inputs", result["status"].lower())

    def test_zero_contingency_is_allowed_and_explicit(self):
        result = development_profit_scenario(**self.complete, contingency_pct=0)
        self.assertEqual(result["contingency"], 0)
        self.assertEqual(result["estimated_total_cost"], 260000)


if __name__ == "__main__":
    unittest.main()
