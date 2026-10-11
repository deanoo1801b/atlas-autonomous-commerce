import json
import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.cli import main


class CliTests(unittest.TestCase):
    def test_business_build_and_qa_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "spec.json"
            spec.write_text(json.dumps({
                "title": "CLI Test",
                "sections": [{"heading": "Overview", "paragraphs": ["Test content"]}],
            }), encoding="utf-8")
            pdf = root / "cli-test.pdf"
            report = root / "qa.json"
            self.assertEqual(main(["build-business", "--spec", str(spec), "--output", str(pdf)]), 0)
            self.assertTrue(pdf.is_file())
            self.assertEqual(main(["qa", "--pdf", str(pdf), "--expected-pages", "2", "--trim-size", "A4", "--report", str(report)]), 0)
            self.assertEqual(json.loads(report.read_text())["technical_status"], "passed")


if __name__ == "__main__":
    unittest.main()
