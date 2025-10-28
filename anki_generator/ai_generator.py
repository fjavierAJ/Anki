"""Vocabulary generation using the OpenAI API."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from .deck_builder import VocabularyEntry

SYSTEM_PROMPT = """
Eres un asistente que crea listas de vocabulario bilingüe inglés-español.
Devuelve únicamente un objeto JSON con el siguiente formato:
{
  "vocabulary": [
    {
      "english": "palabra en inglés",
      "spanish": "traducción",
      "phonetics": "IPA opcional",
      "example_en": "ejemplo en inglés",
      "example_es": "ejemplo en español",
      "category": "categoría opcional"
    }
  ]
}
No incluyas texto adicional fuera del JSON.
"""


@dataclass
class AIGeneratorConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.6
    max_tokens: int = 1200
    api_key: Optional[str] = None


class AIGenerator:
    """Generate vocabulary via OpenAI's responses API."""

    def __init__(self, config: Optional[AIGeneratorConfig] = None) -> None:
        self.config = config or AIGeneratorConfig()
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY no encontrado. Configura la variable de entorno para usar la generación IA."
            )
        if OpenAI is None:
            raise RuntimeError("La librería openai no está instalada. Ejecuta `pip install openai`." )
        self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, count: int = 20) -> List[VocabularyEntry]:
        response = self._client.responses.create(
            model=self.config.model,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Genera una lista de {count} pares de vocabulario.\n"
                        f"Instrucciones adicionales: {prompt}"
                    ),
                },
            ],
        )

        if not response.output:
            raise RuntimeError("Respuesta vacía del modelo IA")

        content = "".join(item.text for item in response.output if hasattr(item, "text"))
        payload = json.loads(content)
        vocab_items = payload.get("vocabulary", [])
        entries: List[VocabularyEntry] = []
        for item in vocab_items:
            entries.append(
                VocabularyEntry(
                    english=item.get("english", ""),
                    spanish=item.get("spanish", ""),
                    phonetics=item.get("phonetics", ""),
                    example_en=item.get("example_en", ""),
                    example_es=item.get("example_es", ""),
                    category=item.get("category", "general"),
                )
            )
        return [entry for entry in entries if entry.english and entry.spanish]
