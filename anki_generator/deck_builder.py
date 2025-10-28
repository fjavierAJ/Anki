"""Anki deck building utilities with shared aesthetics."""
from __future__ import annotations

import base64
import dataclasses
import datetime as _dt
import io
import os
import time
from pathlib import Path
from typing import Iterable, List, Optional

import genanki
from gtts import gTTS
from PIL import Image

from .pexels import PexelsClient, VisualAsset


CARD_MODEL_ID = 1607392360
DECK_ID = 2059401030

CARD_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
    text-align: center;
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    padding: 40px 30px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
}

.spanish-word {
    font-size: 52px;
    font-weight: 600;
    color: white;
    margin: 0 0 30px 0;
    letter-spacing: -0.5px;
}

.image-container {
    margin: 35px auto;
    width: 100%;
    max-width: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.card img {
    width: 280px;
    height: 280px;
    object-fit: cover;
    border-radius: 24px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.25);
    display: block;
    margin: 0 auto;
}

.emoji-display {
    font-size: 100px;
    margin: 35px auto;
    line-height: 1;
    filter: drop-shadow(0 4px 15px rgba(0,0,0,0.2));
    text-align: center;
    display: block;
    width: 100%;
}

.divider {
    width: 90%;
    max-width: 500px;
    height: 1px;
    background: rgba(255,255,255,0.25);
    margin: 35px 0;
}

.english-word {
    font-size: 52px;
    font-weight: 600;
    color: white;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
}

.phonetics {
    font-size: 22px;
    color: rgba(255,255,255,0.8);
    margin: 0 0 25px 0;
    letter-spacing: 0.5px;
}

.example-box {
    background: white;
    border-radius: 28px;
    padding: 32px 28px;
    margin: 30px auto 0;
    max-width: 520px;
    width: 90%;
    text-align: left;
    box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}

.example-en {
    font-size: 18px;
    color: #1F2937;
    margin: 0 0 18px 0;
    line-height: 1.7;
    font-weight: 400;
}

.example-es {
    font-size: 18px;
    color: #9CA3AF;
    line-height: 1.7;
    font-weight: 400;
}

.photo-credit {
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    margin-top: 10px;
    font-style: italic;
    text-align: center;
    width: 100%;
}
"""

EMOJI_MAP = {
    'light': '💡',
    'stars': '⭐',
    'sky': '✨',
    'cielo': '✨',
    'orbit': '🛰️',
    'globe': '🌍',
    'map': '🗺️',
    'compass': '🧭',
    'storm': '⛈️',
    'tornado': '🌪️',
    'volcano': '🌋',
    'tsunami': '🌊',
    'fire': '🔥',
    'earthquake': '📉',
    'drought': '🏜️',
    'flood': '💧',
}


@dataclasses.dataclass
class VocabularyEntry:
    spanish: str
    english: str
    phonetics: str = ""
    example_en: str = ""
    example_es: str = ""
    category: str = "general"


@dataclasses.dataclass
class DeckStats:
    notes: int = 0
    images: int = 0
    emojis: int = 0
    audio: int = 0
    media_files: List[str] = dataclasses.field(default_factory=list)


class DeckBuilder:
    """Builds an Anki deck using the shared aesthetic."""

    def __init__(
        self,
        deck_name: Optional[str] = None,
        output_path: Optional[Path] = None,
        language: str = "en",
        voice_slow: bool = False,
        pexels_client: Optional[PexelsClient] = None,
        rate_limit_seconds: float = 1.0,
    ) -> None:
        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M")
        self.deck_name = deck_name or f"Vocabulary_{timestamp}"
        self.output_path = Path(output_path or f"{self.deck_name}.apkg")
        self.language = language
        self.voice_slow = voice_slow
        self.pexels_client = pexels_client
        self.rate_limit_seconds = rate_limit_seconds

        self._model = genanki.Model(
            CARD_MODEL_ID,
            "Tu Estética con Imágenes",
            fields=[
                {"name": "SpanishWord"},
                {"name": "EnglishWord"},
                {"name": "Phonetics"},
                {"name": "ExampleEN"},
                {"name": "ExampleES"},
                {"name": "Audio"},
                {"name": "VisualContent"},
            ],
            templates=[
                {
                    "name": "Inglés → Español",
                    "qfmt": """
                        <div class=\"english-word\">{{EnglishWord}}</div>
                        <div class=\"phonetics\">{{Phonetics}}</div>
                        {{Audio}}
                    """,
                    "afmt": """
                        {{FrontSide}}
                        <div class=\"divider\"></div>
                        <div class=\"spanish-word\">{{SpanishWord}}</div>
                        {{VisualContent}}
                        <div class=\"example-box\">
                            <div class=\"example-en\">{{ExampleEN}}</div>
                            <div class=\"example-es\">{{ExampleES}}</div>
                        </div>
                    """,
                },
                {
                    "name": "Español → Inglés",
                    "qfmt": """
                        <div class=\"spanish-word\">{{SpanishWord}}</div>
                        {{VisualContent}}
                    """,
                    "afmt": """
                        {{FrontSide}}
                        <div class=\"divider\"></div>
                        <div class=\"english-word\">{{EnglishWord}}</div>
                        <div class=\"phonetics\">{{Phonetics}}</div>
                        {{Audio}}
                        <div class=\"example-box\">
                            <div class=\"example-en\">{{ExampleEN}}</div>
                            <div class=\"example-es\">{{ExampleES}}</div>
                        </div>
                    """,
                },
            ],
            css=CARD_CSS,
        )

    def build(self, entries: Iterable[VocabularyEntry]) -> DeckStats:
        deck = genanki.Deck(DECK_ID, self.deck_name)
        stats = DeckStats()

        for index, entry in enumerate(entries):
            visual_html = self._visual_content(entry)
            if "<img" in visual_html:
                stats.images += 1
            else:
                stats.emojis += 1

            audio_tag, audio_file = self._audio_for_entry(entry, index)
            if audio_file:
                stats.audio += 1
                stats.media_files.append(audio_file)

            note = genanki.Note(
                model=self._model,
                fields=[
                    entry.spanish,
                    entry.english,
                    entry.phonetics,
                    entry.example_en,
                    entry.example_es,
                    audio_tag,
                    visual_html,
                ],
                tags=[f"vocab_{entry.category or 'general'}"],
            )
            deck.add_note(note)
            stats.notes += 1

            if self.rate_limit_seconds:
                time.sleep(self.rate_limit_seconds)

        package = genanki.Package(deck)
        package.media_files = [f for f in stats.media_files if os.path.exists(f)]
        package.write_to_file(str(self.output_path))
        return stats

    def _visual_content(self, entry: VocabularyEntry) -> str:
        if self.pexels_client:
            asset = self.pexels_client.find_asset(entry.english)
            if asset:
                html = self._asset_to_html(asset)
                if html:
                    return html
        emoji = self._emoji_for_word(entry.english, entry.spanish)
        return f'<div class="emoji-display">{emoji}</div>'

    def _asset_to_html(self, asset: VisualAsset) -> Optional[str]:
        if not asset.base64_data:
            asset_base64 = self._download_and_prepare(asset.url)
        else:
            asset_base64 = asset.base64_data
        if not asset_base64:
            return None
        photographer = f"📷 {asset.photographer}" if asset.photographer else ""
        credit_html = f'<div class="photo-credit">{photographer}</div>' if photographer else ""
        return (
            '<div class="image-container">'
            f'<img src="data:image/jpeg;base64,{asset_base64}"/>'
            f"{credit_html}"  # noqa: RUF001
            "</div>"
        )

    def _download_and_prepare(self, url: str) -> Optional[str]:
        try:
            import requests

            response = requests.get(url, timeout=15)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
        except Exception:
            return None

        size = min(img.size)
        left = (img.width - size) // 2
        top = (img.height - size) // 2
        img = img.crop((left, top, left + size, top + size))
        img = img.resize((280, 280), Image.Resampling.LANCZOS)

        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return base64.b64encode(buffer.getvalue()).decode()

    def _emoji_for_word(self, *words: str) -> str:
        combined = " ".join(w.lower() for w in words)
        for key, emoji in EMOJI_MAP.items():
            if key in combined:
                return emoji
        return "📚"

    def _audio_for_entry(self, entry: VocabularyEntry, index: int) -> tuple[str, Optional[str]]:
        try:
            filename = f"audio_{index:03d}.mp3"
            tts = gTTS(entry.english, lang=self.language, slow=self.voice_slow)
            tts.save(filename)
            return f"[sound:{filename}]", filename
        except Exception:
            return "", None


def ensure_entries(dataframe) -> List[VocabularyEntry]:
    """Convert a pandas dataframe into vocabulary entries."""
    entries: List[VocabularyEntry] = []
    for _, row in dataframe.iterrows():
        entries.append(
            VocabularyEntry(
                spanish=str(row.get("SpanishWord") or row.get("TranslationES") or "").strip(),
                english=str(row.get("EnglishWord") or row.get("English") or "").strip(),
                phonetics=str(row.get("Phonetics", "")).strip(),
                example_en=str(row.get("ExampleEN", "")).strip(),
                example_es=str(row.get("ExampleES", "")).strip(),
                category=str(row.get("Category", "general")).strip() or "general",
            )
        )
    return [entry for entry in entries if entry.english and entry.spanish]
