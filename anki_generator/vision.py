"""Extract vocabulary from images using OCR."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from PIL import Image

try:
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore

from .deck_builder import VocabularyEntry


class OCRUnavailableError(RuntimeError):
    pass


def extract_vocabulary_from_image(image_path: Path) -> List[VocabularyEntry]:
    if pytesseract is None:
        raise OCRUnavailableError(
            "pytesseract no está instalado. Instala Tesseract OCR y la librería pytesseract."
        )

    image = Image.open(image_path)
    raw_text = pytesseract.image_to_string(image, lang="spa+eng")
    return parse_text_lines(raw_text.splitlines())


def parse_text_lines(lines: Iterable[str]) -> List[VocabularyEntry]:
    entries: List[VocabularyEntry] = []
    reader = csv.reader(lines, delimiter=';', skipinitialspace=True)
    for row in reader:
        if not row:
            continue
        if len(row) == 1:
            parts = row[0].split('-')
        else:
            parts = row
        parts = [part.strip() for part in parts if part.strip()]
        if len(parts) < 2:
            continue
        spanish, english, *rest = parts
        phonetics = rest[0] if rest else ""
        entries.append(
            VocabularyEntry(
                spanish=spanish,
                english=english,
                phonetics=phonetics,
            )
        )
    return entries
