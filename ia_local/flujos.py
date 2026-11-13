"""De un archivo subido a una herramienta, comprobando antes que hay algo que analizar."""
from ia_local import audio
from ia_local.pdf import extraer_texto_pdf
from ia_local.troceado import ResultadoLargo


class EntradaVacia(Exception):
    """El archivo no tiene nada que analizar. Se avisa sin llamar a Ollama."""


class ErrorArchivo(Exception):
    """El archivo no se puede leer (corrupto, renombrado o en un formato no admitido)."""


def desde_pdf(cliente, config, datos: bytes, herramienta) -> ResultadoLargo:
    try:
        texto = extraer_texto_pdf(datos)
    except Exception as e:  # pdfplumber/pdfminer lanzan varios tipos según el fallo
        raise ErrorArchivo(f"No se pudo leer el PDF: {e or type(e).__name__}") from e
    if not texto.strip():
        raise EntradaVacia("El PDF no tiene texto que leer. Si es un escaneado, pásale antes un OCR.")
    return herramienta(cliente, config, texto)


def desde_audio(cliente, config, datos: bytes, extension: str, herramienta, *,
                transcribir=audio.transcribir) -> tuple[str, ResultadoLargo]:
    try:
        transcripcion = transcribir(datos, extension, config.modelo_whisper)
    except Exception as e:  # ffmpeg/Whisper con un audio ilegible
        raise ErrorArchivo(f"No se pudo transcribir el audio: {e or type(e).__name__}") from e
    if not transcripcion.strip():
        raise EntradaVacia("No se ha detectado voz en el audio.")
    return transcripcion, herramienta(cliente, config, transcripcion)
