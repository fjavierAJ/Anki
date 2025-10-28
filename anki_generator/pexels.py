"""Utilities for retrieving images from the Pexels API."""
from __future__ import annotations

import dataclasses
import os
from typing import Dict, Optional

import requests

DEFAULT_SEARCH_TERMS: Dict[str, str] = {
    'light': 'sunlight golden rays',
    'be facing': 'person facing camera portrait',
    'spin': 'spinning motion blur',
    'axis': 'earth globe axis',
    'rotation': 'earth rotating planet',
    'stars': 'starry night sky stars',
    'sky': 'beautiful blue sky clouds',
    'slowly': 'slow snail tortoise',
    'quickly': 'fast cheetah running',
    'orbit': 'planet orbit space',
    'revolution': 'earth sun orbit',
    'straight': 'straight highway road',
    'tilted': 'leaning tower pisa',
    'southern hemisphere': 'southern hemisphere earth',
    'northern hemisphere': 'northern hemisphere earth',
    'leap year': 'calendar february',
    'high tide': 'high tide waves ocean',
    'low tide': 'low tide beach',
    'globe': 'globe world map desk',
    'political map': 'world map countries',
    'physical map': 'topographic map',
    'thematic map': 'infographic map data',
    'scale': 'ruler scale measurement',
    'compass rose': 'compass rose vintage',
    'orientation': 'compass navigation',
    'cardinal points': 'compass directions',
    'coordinate': 'gps location pin',
    'grid system': 'grid lines map',
    'parallels': 'latitude lines',
    'meridians': 'longitude lines',
    'equator': 'equator line globe',
    'latitude': 'latitude map',
    'longitude': 'longitude map',
    'north': 'north arrow compass',
    'south': 'south compass',
    'east': 'east sunrise',
    'west': 'west sunset',
    'rise': 'sunrise mountains',
    'time zones': 'world clocks time',
    'natural disasters': 'natural disaster',
    'tsunami': 'tsunami wave',
    'storm': 'storm lightning',
    'tornado': 'tornado twister',
    'volcano': 'volcano erupting',
    'the scariest': 'scary storm',
    'damage': 'damaged building',
    'thunderstorm': 'thunderstorm lightning',
    'flood': 'flood water city',
    'drought': 'drought cracked earth',
    'tidal wave': 'huge wave ocean',
    'predict': 'weather forecast',
    'meteorologist': 'weather scientist',
    'geologist': 'geologist rocks',
    'volcanologist': 'volcano scientist',
    'forest fire': 'wildfire forest',
    'wildlife': 'wildlife animals',
    'biological': 'biology microscope',
    'earthquake': 'earthquake damage',
    'rescuers': 'rescue workers',
    'climate change': 'melting glacier',
}


@dataclasses.dataclass
class VisualAsset:
    url: str
    photographer: Optional[str] = None
    base64_data: Optional[str] = None


class PexelsClient:
    """Client wrapper around the Pexels REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        search_terms: Optional[Dict[str, str]] = None,
        orientation: str = "square",
        per_page: int = 3,
    ) -> None:
        self.api_key = api_key or os.environ.get("PEXELS_API_KEY", "").strip()
        self.search_terms = search_terms or DEFAULT_SEARCH_TERMS
        self.orientation = orientation
        self.per_page = per_page

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def find_asset(self, word: str) -> Optional[VisualAsset]:
        if not self.is_enabled():
            return None

        query = self.search_terms.get(word.lower().strip(), word)
        try:
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": self.api_key},
                params={
                    "query": query,
                    "per_page": self.per_page,
                    "orientation": self.orientation,
                },
                timeout=10,
            )
            response.raise_for_status()
        except Exception:
            return None

        data = response.json()
        photos = data.get("photos") or []
        if not photos:
            return None

        photo = photos[0]
        src = photo.get("src") or {}
        return VisualAsset(
            url=src.get("medium") or src.get("large") or src.get("original"),
            photographer=photo.get("photographer"),
        )
