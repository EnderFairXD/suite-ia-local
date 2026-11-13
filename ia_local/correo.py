"""Lectura de los últimos correos por IMAP. Solo lee: no envía, mueve ni borra nada."""
from imap_tools import MailBox

LIMITE_CUERPO = 1500
SOLO_HTML = "El correo solo contiene HTML o está vacío."


class ErrorCorreo(Exception):
    """Fallo al leer el correo, con un mensaje en español listo para mostrar."""


def leer_correos(usuario: str, contrasena: str, servidor: str, limite: int, *, buzon=MailBox) -> list[dict]:
    """Los `limite` correos más recientes de la bandeja de entrada."""
    try:
        with buzon(servidor).login(usuario, contrasena, "INBOX") as bandeja:
            return [
                {
                    "remitente": m.from_,
                    "asunto": m.subject,
                    "fecha": m.date_str,
                    "cuerpo": (m.text or SOLO_HTML)[:LIMITE_CUERPO],
                }
                for m in bandeja.fetch(limit=limite, reverse=True)
            ]
    except Exception as e:  # imaplib, sockets y errores de login: todos se explican igual
        raise ErrorCorreo(f"No se pudo leer el correo: {e}") from e
