import unittest
from datetime import date, timedelta
from unittest.mock import Mock

import land_registry_comparables as module


class LandRegistryComparablesTests(unittest.TestCase):
    def test_postcode_outcode_normalizes_valid_postcode(self):
        self.assertEqual(module.postcode_outcode("cr0 1aa"), "CR0")
        self.assertEqual(module.postcode_outcode("SW1A 1AA"), "SW1A")

    def test_postcode_outcode_rejects_unverified_place_name(self):
        self.assertIsNone(module.postcode_outcode("Croydon, London"))

    def test_query_requires_valid_outcode_and_bounded_limit(self):
        with self.assertRaises(ValueError):
            module.build_query("Croydon", date.today())
        with self.assertRaises(ValueError):
            module.build_query("CR0", date.today(), 1000)

    def test_normalize_results_filters_outcode_type_and_date(self):
        since = date.today() - timedelta(days=365)
        payload = {"results": {"bindings": [
            {"transaction": {"value": "http://landregistry.data.gov.uk/data/ppi/transaction/a"},
             "price": {"value": "350000"}, "date": {"value": date.today().isoformat()},
             "propertyType": {"value": "http://landregistry.data.gov.uk/def/ppi/Detached"},
             "postcode": {"value": "CR0 1AA"}, "paon": {"value": "12"},
             "street": {"value": "High Street"}, "town": {"value": "Croydon"}},
            {"transaction": {"value": "http://landregistry.data.gov.uk/data/ppi/transaction/b"},
             "price": {"value": "250000"}, "date": {"value": date.today().isoformat()},
             "propertyType": {"value": "http://landregistry.data.gov.uk/def/ppi/Flat"},
             "postcode": {"value": "CR0 1AB"}},
            {"transaction": {"value": "http://landregistry.data.gov.uk/data/ppi/transaction/c"},
             "price": {"value": "200000"}, "date": {"value": (since - timedelta(days=1)).isoformat()},
             "propertyType": {"value": "http://landregistry.data.gov.uk/def/ppi/Detached"},
             "postcode": {"value": "CR0 1AC"}},
            {"transaction": {"value": "http://landregistry.data.gov.uk/data/ppi/transaction/d"},
             "price": {"value": "400000"}, "date": {"value": date.today().isoformat()},
             "propertyType": {"value": "http://landregistry.data.gov.uk/def/ppi/Detached"},
             "postcode": {"value": "DA1 1AA"}},
        ]}}
        result = module.normalize_results(payload, "CR0", "detached", since)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sold_price"], 350000)
        self.assertTrue(result[0]["source_url"].startswith("https://"))
        self.assertIn("HM Land Registry", result[0]["evidence_source"])

    def test_candidate_enrichment_is_disabled_by_default(self):
        from unittest.mock import Mock
        fetcher = Mock()
        candidates = [{"Postcode": "CR0 1AA", "Property Type": "detached"}]
        result = module.enrich_candidates_with_sold_comparables(
            candidates, enabled=False, fetcher=fetcher
        )
        self.assertFalse(result["enabled"])
        fetcher.assert_not_called()
        self.assertNotIn("Comparable Sales Evidence", candidates[0])

    def test_candidate_enrichment_caches_outcode_and_type_and_preserves_attribution(self):
        from unittest.mock import Mock
        fetcher = Mock(return_value={
            "comparables": [{
                "sold_price": 350000,
                "sale_date": date.today().isoformat(),
                "source_url": "https://landregistry.data.gov.uk/data/ppi/transaction/example",
                "postcode": "CR0 1AA",
                "property_type": "detached",
            }],
            "attribution": module.ATTRIBUTION,
            "limitations": ["Human review required"],
        })
        candidates = [
            {"Postcode": "CR0 1AA", "Property Type": "detached"},
            {"Postcode": "CR0 1AB", "Property Type": "detached"},
        ]
        result = module.enrich_candidates_with_sold_comparables(
            candidates, enabled=True, max_lookups=2, fetcher=fetcher
        )
        self.assertEqual(result["lookups"], 1)
        self.assertEqual(result["enriched"], 2)
        fetcher.assert_called_once()
        self.assertEqual(candidates[0]["Comparable Sales Count"], 1)
        self.assertIn("human comparability review", candidates[0]["Comparable Evidence Status"])
        self.assertIn("Crown copyright", candidates[0]["Notes"])

    def test_fetch_posts_bounded_query_and_returns_attribution(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"results": {"bindings": []}}
        session = Mock()
        session.post.return_value = response
        result = module.fetch_sold_comparables("CR0 1AA", "terraced", session=session)
        session.post.assert_called_once()
        self.assertEqual(result["result_count"], 0)
        self.assertIn("Crown copyright", result["attribution"])
        self.assertTrue(result["limitations"])


if __name__ == "__main__":
    unittest.main()
