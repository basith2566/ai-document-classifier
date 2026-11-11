"""Run from backend/:  python -m unittest discover -s tests -t .

Uses a temporary database. PDF tests are skipped if PyMuPDF is not installed.
"""
import os
import tempfile
import unittest
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = str(Path(_tmp) / "test.db")

from database.db import init_db  # noqa: E402
from ml.preprocess import clean_text  # noqa: E402
from services import document_service as ds  # noqa: E402
from services.classification_service import classifier  # noqa: E402
from services.extraction_service import ExtractionError, extract_text  # noqa: E402
from services.stats_service import get_stats  # noqa: E402

SAMPLES = Path(__file__).resolve().parents[2] / "sample_documents"


class PreprocessTests(unittest.TestCase):
    def test_clean_text_replaces_numbers_urls_emails(self):
        out = clean_text("Pay $1,200.50 to a@b.com via https://x.io NOW!")
        self.assertIn("numtoken", out)
        self.assertIn("emailtoken", out)
        self.assertIn("urltoken", out)
        self.assertEqual(out, out.lower())


class ExtractionTests(unittest.TestCase):
    def test_txt_and_encodings(self):
        self.assertEqual(extract_text("a.txt", "héllo".encode("utf-8")), "héllo")
        self.assertEqual(extract_text("a.txt", "héllo".encode("cp1252")), "héllo")

    def test_unsupported_and_fake_files(self):
        with self.assertRaises(ExtractionError):
            extract_text("a.csv", b"x")
        with self.assertRaises(ExtractionError):
            extract_text("fake.docx", b"not a zip")
        with self.assertRaises(ExtractionError):
            extract_text("fake.pdf", b"not a pdf")

    def test_docx(self):
        text = extract_text("r.docx", (SAMPLES / "resume_meera_nair.docx").read_bytes())
        self.assertIn("MEERA NAIR", text)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        assert classifier.load(), "Train the model first: python -m ml.train"

    def test_rejections(self):
        for name, data in [("e.txt", b""), ("x.csv", b"a,b"), ("blank.txt", b"   \n  ")]:
            with self.assertRaises(ds.DocumentError):
                ds.process_upload(name, data)

    def test_classify_store_search_delete(self):
        before = get_stats()["total_documents"]
        doc = ds.process_upload("email.txt", (SAMPLES / "email_project_sync.txt").read_bytes())
        self.assertEqual(doc["category"], "Email")
        self.assertTrue(0 <= doc["confidence"] <= 1)
        self.assertAlmostEqual(sum(p["probability"] for p in doc["probabilities"]), 1.0, places=2)
        self.assertGreaterEqual(ds.list_documents(search="Project sync")["total"], 1)
        self.assertEqual(get_stats()["total_documents"], before + 1)
        self.assertTrue(ds.delete_document(doc["id"]))
        self.assertIsNone(ds.get_document(doc["id"]))

    def test_ambiguous_text_needs_review(self):
        doc = ds.process_upload("m.txt", (SAMPLES / "meeting_minutes_mixed.txt").read_bytes())
        self.assertTrue(doc["needs_review"])
        self.assertEqual(doc["display_category"], "Needs Manual Review")

    def test_too_short_needs_review(self):
        doc = ds.process_upload("s.txt", b"hello there")
        self.assertTrue(doc["needs_review"])

    def test_pdf(self):
        try:
            import pymupdf  # noqa: F401
        except ImportError:
            try:
                import fitz  # noqa: F401
            except ImportError:
                self.skipTest("PyMuPDF not installed")
        doc = ds.process_upload("i.pdf", (SAMPLES / "invoice_greenfield_supplies.pdf").read_bytes())
        self.assertEqual(doc["category"], "Invoice")


if __name__ == "__main__":
    unittest.main()
