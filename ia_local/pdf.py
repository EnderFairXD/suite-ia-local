"""Texto de un PDF."""
import io
from typing import BinaryIO

import pdfplumber


def extraer_texto_pdf(archivo: BinaryIO | bytes) -> str:
    """Texto de todas las páginas, separadas por una línea en blanco. Vacío si no hay texto
    (por ejemplo, un PDF escaneado sin OCR)."""
    if isinstance(archivo, (bytes, bytearray)):
        archivo = io.BytesIO(archivo)
    with pdfplumber.open(archivo) as pdf:
        paginas = [p.extract_text() or "" for p in pdf.pages]
    return "\n\n".join(t for t in paginas if t.strip())
