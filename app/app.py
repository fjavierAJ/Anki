from __future__ import annotations

from flask import Flask, render_template, request, send_file, Response
from io import BytesIO

from .card_generator import cards_to_tsv, generate_cards


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        text = ""
        min_length = 6
        max_cards = 50
        cards = []
        error = None

        if request.method == "POST":
            text = request.form.get("notes", "")
            min_length = int(request.form.get("min_length", min_length) or min_length)
            max_cards_value = request.form.get("max_cards", "")
            max_cards = int(max_cards_value) if max_cards_value else None

            if not text.strip():
                error = "Por favor ingresa algún contenido para analizar."
            else:
                cards = generate_cards(text, min_cloze_length=min_length, max_cards=max_cards)
                if not cards:
                    error = "No se pudieron generar tarjetas con el texto proporcionado."

            if request.form.get("action") == "download" and cards:
                buffer = BytesIO()
                buffer.write(cards_to_tsv(cards).encode("utf-8"))
                buffer.seek(0)
                return send_file(
                    buffer,
                    mimetype="text/tab-separated-values",
                    as_attachment=True,
                    download_name="anki_cards.tsv",
                )

        return render_template(
            "index.html",
            text=text,
            cards=cards,
            error=error,
            min_length=min_length,
            max_cards=max_cards if max_cards is not None else "",
        )

    @app.route("/health")
    def health() -> Response:
        return Response("ok", mimetype="text/plain")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
