from types import SimpleNamespace

import pytest

from ia_local.correo import ErrorCorreo, leer_correos


def _mensaje(asunto, remitente="ana@empresa.es", texto="Hola", fecha="13 Nov 2026"):
    return SimpleNamespace(subject=asunto, from_=remitente, date_str=fecha, text=texto)


class BuzonFalso:
    """Imita `imap_tools.MailBox(servidor).login(usuario, contrasena, carpeta)`."""

    def __init__(self, mensajes=(), error_login=None):
        self.mensajes, self.error_login, self.llamadas = list(mensajes), error_login, []

    def __call__(self, servidor):
        self.llamadas.append(("servidor", servidor))
        return self

    def login(self, usuario, contrasena, carpeta):
        self.llamadas.append(("login", usuario, carpeta))
        if self.error_login:
            raise self.error_login
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def fetch(self, limit, reverse):
        self.llamadas.append(("fetch", limit, reverse))
        return iter(self.mensajes[:limit])


def test_lee_los_ultimos_correos_y_limita_el_cuerpo():
    buzon = BuzonFalso([_mensaje("Reunión", texto="x" * 5000), _mensaje("Factura")])
    correos = leer_correos("yo@correo.es", "secreta", "imap.correo.es", 2, buzon=buzon)
    assert [c["asunto"] for c in correos] == ["Reunión", "Factura"]
    assert correos[0] == {"remitente": "ana@empresa.es", "asunto": "Reunión", "fecha": "13 Nov 2026",
                          "cuerpo": "x" * 1500}
    assert ("servidor", "imap.correo.es") in buzon.llamadas
    assert ("login", "yo@correo.es", "INBOX") in buzon.llamadas
    assert ("fetch", 2, True) in buzon.llamadas


def test_correo_solo_html_lo_indica():
    correos = leer_correos("u", "p", "s", 1, buzon=BuzonFalso([_mensaje("Boletín", texto="")]))
    assert correos[0]["cuerpo"] == "El correo solo contiene HTML o está vacío."


def test_fallo_de_login_da_error_legible():
    buzon = BuzonFalso(error_login=RuntimeError("AUTHENTICATIONFAILED Invalid credentials"))
    with pytest.raises(ErrorCorreo) as e:
        leer_correos("u", "secreta", "s", 3, buzon=buzon)
    assert str(e.value).startswith("No se pudo leer el correo:")
    assert "secreta" not in str(e.value)
