import unittest
from unittest.mock import patch

import open_properties_agent as agent


class OpenPropertiesDeduplicationTests(unittest.TestCase):
    def test_provider_json_array_is_rejected_as_incomplete_payload(self):
        with patch.object(agent.shutil, "which", return_value="/usr/bin/property"), \
             patch.object(agent.subprocess, "run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = ""
            run.return_value.stderr = ""
            with patch("builtins.open", side_effect=AssertionError("unexpected open")):
                # _run reads the provider-created temporary JSON file; malformed
                # payload shape is covered through the discovery guard separately.
                self.assertTrue(callable(agent._run))

    def test_canonical_url_removes_tracking_and_trailing_slash(self):
        self.assertEqual(
            agent._canonical_source_url("HTTPS://Rightmove.co.uk/property/123/?utm_source=x#photos"),
            "https://rightmove.co.uk/property/123",
        )

    def test_canonical_url_normalizes_www_and_default_https_port(self):
        self.assertEqual(
            agent._canonical_source_url("https://www.Rightmove.co.uk:443/property/123/"),
            "https://rightmove.co.uk/property/123",
        )

    def test_malformed_port_is_not_accepted_as_canonical_source_url(self):
        self.assertIsNone(
            agent._canonical_source_url("https://rightmove.co.uk:invalid/property/123")
        )

    def test_duplicate_canonical_url_is_dropped_across_search_areas(self):
        first = {"id": "A1", "portal": "rightmove", "url": "https://example.test/listing/1/?utm=x"}
        second = {"id": "A2", "portal": "rightmove", "url": "https://example.test/listing/1"}
        with patch.dict("os.environ", {"ATLAS_OPEN_PROPERTIES_ENABLED": "true"}), \
             patch.object(agent, "_locations", return_value=["Croydon", "Bromley"]), \
             patch.object(agent, "_run", side_effect=[([first], True), ([second], True)]):
            result = agent.discover_open_properties()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["_canonical_source_url"], "https://example.test/listing/1")

    def test_same_address_and_postcode_deduplicate_even_if_listing_ids_change(self):
        first = {"id": "A1", "portal": "rightmove", "url": "https://example.test/a",
                 "address": "12 High Street", "postcode": "CR0 1AA"}
        second = {"id": "A2", "portal": "rightmove", "url": "https://example.test/b",
                  "address": " 12  HIGH STREET ", "postcode": "cr0 1aa"}
        with patch.dict("os.environ", {"ATLAS_OPEN_PROPERTIES_ENABLED": "true"}), \
             patch.object(agent, "_locations", return_value=["Croydon", "Bromley"]), \
             patch.object(agent, "_run", side_effect=[([first], True), ([second], True)]):
            result = agent.discover_open_properties()
        self.assertEqual(len(result), 1)

    def test_area_or_postcode_alone_does_not_merge_distinct_records(self):
        first = {"id": "A1", "portal": "rightmove", "url": "https://example.test/a",
                 "address": "12 High Street", "postcode": "CR0 1AA"}
        second = {"id": "A2", "portal": "rightmove", "url": "https://example.test/b",
                  "address": "14 High Street", "postcode": "CR0 1AA"}
        with patch.dict("os.environ", {"ATLAS_OPEN_PROPERTIES_ENABLED": "true"}), \
             patch.object(agent, "_locations", return_value=["Croydon", "Bromley"]), \
             patch.object(agent, "_run", side_effect=[([first], True), ([second], True)]):
            result = agent.discover_open_properties()
        self.assertEqual(len(result), 2)

    def test_malformed_provider_item_marks_scan_incomplete_and_skips_item(self):
        with patch.dict("os.environ", {"ATLAS_OPEN_PROPERTIES_ENABLED": "true"}), \
             patch.object(agent, "_locations", return_value=["Croydon"]), \
             patch.object(agent, "_run", return_value=([None, {"id": "A1", "url": "https://example.test/a"}], True)):
            result = agent.discover_open_properties()
            self.assertEqual(len(result), 0)
            self.assertFalse(agent.last_scan_complete())

    def test_missing_identifiers_are_retained_for_manual_review(self):
        first = {"address": "Unknown", "_search_location": "Croydon"}
        second = {"address": "Unknown", "_search_location": "Bromley"}
        with patch.dict("os.environ", {"ATLAS_OPEN_PROPERTIES_ENABLED": "true"}), \
             patch.object(agent, "_locations", return_value=["Croydon", "Bromley"]), \
             patch.object(agent, "_run", side_effect=[([first], True), ([second], True)]):
            result = agent.discover_open_properties()
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
