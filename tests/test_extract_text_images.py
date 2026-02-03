from pathlib import Path
import types
import sys
import numpy as np


def test_extract_text_txt(tools, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("ciao mondo")
    out = tools._extract_text(f)
    assert "ciao mondo" in out


def test_extract_text_unknown_extension_fallback(tools, tmp_path):
    f = tmp_path / "test.unknown"
    f.write_text("contenuto generico")
    out = tools._extract_text(f)
    assert "contenuto generico" in out


def test_extract_images_from_pdf_mocked(tools, tmp_path, monkeypatch):
    # mock di fitz (PyMuPDF)
    fake_fitz = types.ModuleType("fitz")

    class FakePixmap:
        def __init__(self, doc, xref):
            self.n = 3

        def tobytes(self, fmt):
            return b"fakepng"

    class FakePage:
        def get_images(self, full=True):
            return [(1,)]

    class FakeDoc:
        def __iter__(self):
            return iter([FakePage()])

    def fake_open(path):
        return FakeDoc()

    fake_fitz.Pixmap = FakePixmap
    fake_fitz.open = fake_open
    fake_fitz.csRGB = None

    sys.modules["fitz"] = fake_fitz

    f = tmp_path / "test.pdf"
    f.write_bytes(b"%PDF-1.4 fake")

    images = tools._extract_images_from_pdf(f)
    assert len(images) == 1
    assert images[0]["page"] == 0
    assert images[0]["index"] == 0
    assert isinstance(images[0]["bytes"], bytes)

