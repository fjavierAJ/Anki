# Generador automático de tarjetas Anki

Aplicación web ligera para convertir tus apuntes en tarjetas importables desde Anki.

## Características

- Analiza tus notas buscando patrones `término - definición` o `término: definición`.
- Genera automáticamente tarjetas de tipo cloze en frases donde detecta palabras clave largas.
- Permite ajustar la longitud mínima del término a ocultar y el límite máximo de tarjetas.
- Descarga un archivo TSV compatible con la importación estándar de Anki.

## Requisitos

- Python 3.10 o superior
- `pip` para instalar dependencias

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Ejecución

```bash
flask --app app.app run --host 0.0.0.0 --port 8000 --debug
```

Luego abre [http://localhost:8000](http://localhost:8000) para acceder a la interfaz.

## Uso

1. Pega tus apuntes o listas de conceptos en el área de texto.
2. Ajusta los parámetros opcionales:
   - **Longitud mínima del término cloze**: controla cuántos caracteres debe tener la palabra a ocultar.
   - **Límite de tarjetas**: define cuántas tarjetas como máximo se mostrarán o descargarán.
3. Pulsa **Generar vista previa** para revisar las tarjetas creadas.
4. Pulsa **Descargar TSV** para obtener un archivo `anki_cards.tsv` con las tarjetas separadas por tabuladores.
5. En Anki, ve a *Archivo → Importar* y selecciona el archivo descargado.

## Pruebas rápidas

Puedes verificar que el código compila correctamente ejecutando:

```bash
python -m compileall app
```

## Salud del servicio

El endpoint `/health` devuelve `ok` y puede emplearse para verificaciones básicas.
