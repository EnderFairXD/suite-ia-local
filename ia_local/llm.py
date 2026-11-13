"""Cliente de Ollama: configuración, una pregunta y aviso de recorte."""
import math
import os
from dataclasses import dataclass

import ollama
from dotenv import load_dotenv

# Por el lado prudente: en español sale algo más de 3,5 caracteres por token.
CARACTERES_POR_TOKEN = 3.5
# Si Ollama leyó tantos tokens que solo quedan estos libres, probablemente recortó.
MARGEN_RECORTE = 64


@dataclass(frozen=True)
class Config:
    base_url: str
    modelo: str
    contexto: int
    modelo_whisper: str

    @classmethod
    def desde_entorno(cls, cargar_env: bool = True) -> "Config":
        if cargar_env:
            load_dotenv()
        return cls(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            modelo=os.environ.get("MODELO", "llama3.1"),
            contexto=int(os.environ.get("CONTEXTO", "8192")),
            modelo_whisper=os.environ.get("MODELO_WHISPER", "base"),
        )


@dataclass(frozen=True)
class Respuesta:
    texto: str
    tokens_leidos: int
    posible_recorte: bool


class ErrorOllama(Exception):
    """Fallo al hablar con Ollama, con un mensaje en español listo para mostrar."""


def estimar_tokens(texto: str) -> int:
    return math.ceil(len(texto) / CARACTERES_POR_TOKEN)


def crear_cliente(config: Config) -> ollama.Client:
    return ollama.Client(host=config.base_url)


def _traducir_error(error: Exception, config: Config) -> ErrorOllama:
    if isinstance(error, ollama.ResponseError) and error.status_code == 404:
        return ErrorOllama(
            f"El modelo «{config.modelo}» no está descargado en Ollama. "
            f"Descárgalo con: ollama pull {config.modelo}"
        )
    if isinstance(error, ConnectionError):
        return ErrorOllama(
            f"No se puede conectar con Ollama en {config.base_url}. "
            "Comprueba que está arrancado y que OLLAMA_BASE_URL apunta a él."
        )
    return ErrorOllama(f"Ollama devolvió un error: {error}")


def preguntar(cliente, config: Config, sistema: str, usuario: str, temperatura: float = 0.2) -> Respuesta:
    """Una llamada a Ollama con las instrucciones en `sistema` y el contenido en `usuario`."""
    try:
        r = cliente.chat(
            model=config.modelo,
            messages=[{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
            options={"num_ctx": config.contexto, "temperature": temperatura},
        )
    except (ConnectionError, ollama.ResponseError) as e:
        raise _traducir_error(e, config) from e
    leidos = r.prompt_eval_count or 0
    return Respuesta(
        texto=r.message.content,
        tokens_leidos=leidos,
        posible_recorte=leidos >= config.contexto - MARGEN_RECORTE,
    )


def estado_ollama(cliente, config: Config | None = None) -> tuple[bool, list[str] | str]:
    """(True, modelos disponibles) si Ollama responde; (False, explicación) si no."""
    try:
        return True, [m.model for m in cliente.list().models]
    except (ConnectionError, ollama.ResponseError) as e:
        return False, str(_traducir_error(e, config or Config.desde_entorno(cargar_env=False)))
