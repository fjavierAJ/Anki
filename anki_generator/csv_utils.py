"""Helper functions for reading and writing vocabulary CSV files."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .deck_builder import VocabularyEntry

REQUIRED_COLUMNS = [
    "SpanishWord",
    "EnglishWord",
    "Phonetics",
    "ExampleEN",
    "ExampleES",
    "Category",
]


def read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except Exception:
            continue
    raise ValueError(f"No se pudo leer el archivo CSV: {path}")


def write_csv(path: Path, entries: Iterable[VocabularyEntry]) -> None:
    rows: List[dict] = []
    for entry in entries:
        rows.append(
            {
                "SpanishWord": entry.spanish,
                "EnglishWord": entry.english,
                "Phonetics": entry.phonetics,
                "ExampleEN": entry.example_en,
                "ExampleES": entry.example_es,
                "Category": entry.category,
            }
        )
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df.to_csv(path, index=False, encoding="utf-8")
