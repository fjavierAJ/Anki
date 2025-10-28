"""Command line interface for the Anki vocabulary generator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from .ai_generator import AIGenerator, AIGeneratorConfig
from .csv_utils import read_csv, write_csv
from .deck_builder import DeckBuilder, VocabularyEntry, ensure_entries
from .pexels import PexelsClient
from .vision import OCRUnavailableError, extract_vocabulary_from_image


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera mazos Anki desde múltiples fuentes")
    parser.add_argument("--source", choices=["csv", "image", "ai"], required=True)
    parser.add_argument("--input", help="Ruta al archivo de entrada (CSV, imagen o texto)")
    parser.add_argument("--output", help="Ruta del archivo .apkg", default=None)
    parser.add_argument("--deck-name", help="Nombre del mazo", default=None)
    parser.add_argument("--save-csv", help="Guardar CSV generado", default=None)
    parser.add_argument("--count", type=int, default=20, help="Cantidad de términos a generar (IA)")
    parser.add_argument("--prompt", default="", help="Instrucciones para la IA")
    parser.add_argument("--pexels-key", default=None, help="API Key de Pexels")
    parser.add_argument("--tts-lang", default="en", help="Idioma para la síntesis de voz")
    parser.add_argument("--tts-slow", action="store_true", help="Audio en modo lento")
    parser.add_argument("--rate", type=float, default=1.0, help="Pausa entre tarjetas (segundos)")

    args = parser.parse_args(argv)

    if args.source in {"csv", "image"} and not args.input:
        parser.error("--input es obligatorio para las fuentes csv e image")

    entries: List[VocabularyEntry]

    if args.source == "csv":
        df = read_csv(Path(args.input))
        entries = ensure_entries(df)
    elif args.source == "image":
        try:
            entries = extract_vocabulary_from_image(Path(args.input))
        except OCRUnavailableError as exc:
            parser.error(str(exc))
    else:
        config = AIGeneratorConfig()
        generator = AIGenerator(config)
        prompt = args.prompt or Path(args.input).read_text(encoding="utf-8") if args.input else ""
        entries = generator.generate(prompt, count=args.count)

    if not entries:
        parser.error("No se pudieron generar entradas de vocabulario")

    if args.save_csv:
        write_csv(Path(args.save_csv), entries)

    pexels_client = None
    if args.pexels_key:
        pexels_client = PexelsClient(api_key=args.pexels_key)
    else:
        pexels_client = PexelsClient()
        if not pexels_client.is_enabled():
            pexels_client = None

    builder = DeckBuilder(
        deck_name=args.deck_name,
        output_path=args.output,
        language=args.tts_lang,
        voice_slow=args.tts_slow,
        pexels_client=pexels_client,
        rate_limit_seconds=args.rate,
    )

    stats = builder.build(entries)

    print("✅ Mazo creado:", builder.output_path)
    print("📊 Estadísticas:")
    print("   • Notas:", stats.notes)
    print("   • Imágenes reales:", stats.images)
    print("   • Emojis:", stats.emojis)
    print("   • Audios:", stats.audio)

    if args.save_csv:
        print("📄 CSV guardado en:", args.save_csv)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
