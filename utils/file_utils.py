from __future__ import annotations

import io
import os
from typing import Tuple

from pypdf import PdfReader
from docx import Document


def read_file_text(path: str) -> Tuple[str, str]:
    """Read a file and return (text, detected_type). Supports .txt, .pdf, .docx"""
    lower = path.lower()
    if lower.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), "txt"
    if lower.endswith(".pdf"):
        return _read_pdf(path), "pdf"
    if lower.endswith(".docx"):
        return _read_docx(path), "docx"
    raise ValueError(f"Unsupported file type for {path}")


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(t.strip() for t in texts if t)


def _read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def save_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)