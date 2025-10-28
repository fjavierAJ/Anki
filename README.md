# Generador de Mazos Anki con IA

Esta herramienta permite crear mazos de Anki con la estética personalizada descrita, generando imágenes reales desde Pexels cuando se proporciona una API Key y produciendo audios con `gTTS`. El flujo completo puede partir de tres orígenes de vocabulario:

1. **CSV existente** – lee el archivo y construye el mazo automáticamente.
2. **Imagen o foto** – aplica OCR (Tesseract) para extraer pares de vocabulario.
3. **Generación con IA** – utiliza el modelo de OpenAI configurado mediante `OPENAI_API_KEY` para crear vocabulario bajo demanda.

## Requisitos

```bash
pip install -r requirements.txt
```

Para la funcionalidad de OCR es necesario instalar [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) en el sistema operativo.

## Uso

```bash
python -m anki_generator --source csv --input vocabulario.csv --pexels-key TU_API_KEY --save-csv salida.csv
```

### Extraer desde imagen

```bash
python -m anki_generator --source image --input foto.jpg --pexels-key TU_API_KEY
```

### Generar con IA

```bash
export OPENAI_API_KEY="sk-..."
python -m anki_generator --source ai --input prompt.txt --count 30 --pexels-key TU_API_KEY
```

Parámetros principales:

- `--output`: ruta del archivo `.apkg` a generar (por defecto `Vocabulary_YYYYMMDD_HHMM.apkg`).
- `--deck-name`: nombre del mazo.
- `--tts-lang`: idioma para la síntesis de voz (por defecto inglés).
- `--tts-slow`: genera audio a velocidad lenta.
- `--rate`: pausa en segundos entre notas (controla peticiones a Pexels y gTTS).
- `--save-csv`: guarda el vocabulario final en CSV.

## Módulos principales

- `anki_generator/deck_builder.py`: estética de tarjetas, creación de notas y empaquetado `.apkg`.
- `anki_generator/pexels.py`: búsqueda de imágenes reales en Pexels.
- `anki_generator/vision.py`: extracción OCR desde imágenes o fotos.
- `anki_generator/ai_generator.py`: interacción con OpenAI para generar vocabulario.
- `anki_generator/csv_utils.py`: lectura y escritura de CSVs compatibles con Anki.
- `anki_generator/cli.py`: punto de entrada CLI.

## Limitaciones

- La generación de audio y las consultas a Pexels requieren conexión a Internet.
- La extracción OCR depende de la calidad de la imagen y del entrenamiento de Tesseract.
- La generación con IA requiere un modelo compatible con la API de OpenAI Responses.
