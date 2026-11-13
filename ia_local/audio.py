"""Transcripción local con faster-whisper."""
import functools
import os
import tempfile
from typing import Iterable

from faster_whisper import WhisperModel


def _minutos(segundos: float) -> str:
    total = int(segundos)
    return f"{total // 60:02d}:{total % 60:02d}"


def formatear_segmentos(segmentos: Iterable) -> str:
    """Una línea por segmento: [mm:ss -> mm:ss]: texto."""
    return "\n".join(
        f"[{_minutos(s.start)} -> {_minutos(s.end)}]: {s.text.strip()}" for s in segmentos
    )


@functools.lru_cache(maxsize=None)
def cargar_modelo(nombre: str):
    """Carga el modelo de Whisper una vez por nombre y lo reutiliza."""
    return WhisperModel(nombre, device="cpu", compute_type="int8")


def transcribir(datos: bytes, extension: str, nombre_modelo: str, *, cargar=cargar_modelo) -> str:
    """Transcribe un audio en español. El archivo temporal se borra pase lo que pase."""
    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(datos)
        ruta = tmp.name
    try:
        segmentos, _ = cargar(nombre_modelo).transcribe(ruta, beam_size=5, language="es")
        return formatear_segmentos(segmentos)
    finally:
        os.unlink(ruta)
