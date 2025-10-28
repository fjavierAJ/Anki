"""Utility functions to transform raw study notes into Anki-friendly cards."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import re


@dataclass
class Card:
    """Representation of a single flashcard."""

    front: str
    back: str
    source: str


def _clean_text(value: str) -> str:
    """Normalize whitespace in the provided value."""

    return re.sub(r"\s+", " ", value.strip())


def _split_candidates(text: str) -> List[str]:
    """Split free-form text into candidate sentences."""

    sentences: List[str] = []
    buffer = []
    for char in text:
        buffer.append(char)
        if char in ".!?":
            sentence = _clean_text("".join(buffer))
            if sentence:
                sentences.append(sentence)
            buffer = []
    remainder = _clean_text("".join(buffer))
    if remainder:
        sentences.append(remainder)
    return sentences


def _extract_keyword(sentence: str, min_length: int = 6) -> str | None:
    """Pick a keyword from the sentence to create a cloze deletion."""

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", sentence)
    words.sort(key=len, reverse=True)
    for word in words:
        if len(word) >= min_length:
            return word
    return None


def _create_cloze(sentence: str, keyword: str) -> Card:
    placeholder = "_____"
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    front = pattern.sub(placeholder, sentence, count=1)
    return Card(front=front, back=sentence, source="Auto cloze")


def _parse_explicit_pairs(lines: Iterable[str]) -> List[Card]:
    cards: List[Card] = []
    for line in lines:
        clean_line = _clean_text(line)
        if not clean_line:
            continue
        if " - " in clean_line:
            front, back = clean_line.split(" - ", 1)
            cards.append(Card(front=front, back=back, source="Pair"))
        elif ":" in clean_line:
            front, back = clean_line.split(":", 1)
            cards.append(Card(front=front, back=back, source="Pair"))
    return cards


def generate_cards(
    raw_text: str,
    min_cloze_length: int = 6,
    max_cards: int | None = 50,
) -> List[Card]:
    """Generate a list of flashcards from raw text.

    The function first looks for explicit "Term - Definition" or "Term: Definition"
    patterns. Remaining text is used to create simple cloze deletions by blanking the
    longest keyword in each sentence.
    """

    lines = raw_text.splitlines()
    explicit_cards = _parse_explicit_pairs(lines)

    used_sentences = {card.back for card in explicit_cards}

    sentences = _split_candidates(raw_text)
    cloze_cards: List[Card] = []
    for sentence in sentences:
        if sentence in used_sentences:
            continue
        keyword = _extract_keyword(sentence, min_length=min_cloze_length)
        if not keyword:
            continue
        cloze_cards.append(_create_cloze(sentence, keyword))

    cards = explicit_cards + cloze_cards

    if max_cards is not None:
        cards = cards[:max_cards]

    return cards


def cards_to_tsv(cards: Iterable[Card]) -> str:
    """Serialize cards into the tab-separated format that Anki imports."""

    rows: List[str] = []
    for card in cards:
        rows.append(f"{card.front}\t{card.back}")
    return "\n".join(rows)

