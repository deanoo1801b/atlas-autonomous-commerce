import json
import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.package_manifest import create_package_manifest, sha256_file


class PackageManifestTests(unittest.TestCase):
    def test_manifest_records_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "01-KKAM-Sample.pdf"
            pdf.write_bytes(b"%PDF-sample")
            out = root / "manifest.json"
            manifest = create_package_manifest("KKAM-0001", "1.0.0", [pdf], out)
            self.assertEqual(manifest["file_count"], 1)
            self.assertEqual(manifest["files"][0]["sha256"], sha256_file(pdf))
            self.assertEqual(json.loads(out.read_text())["product_id"], "KKAM-0001")

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                create_package_manifest("KKAM-0001", "1.0", [Path(tmp) / "missing"], Path(tmp) / "manifest.json")

    def test_duplicate_basenames_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            one, two = root / "a", root / "b"
            one.mkdir(); two.mkdir()
            f1, f2 = one / "same.png", two / "same.png"
            f1.write_bytes(b"a"); f2.write_bytes(b"b")
            with self.assertRaises(ValueError):
                create_package_manifest("KKAM-0001", "1.0", [f1, f2], root / "manifest.json")


if __name__ == "__main__":
    unittest.main()
