import os
from types import SimpleNamespace

import pytest

from ia_local import audio


def _segmento(inicio, fin, texto):
    return SimpleNamespace(start=inicio, end=fin, text=texto)


class ModeloFalso:
    def __init__(self, segmentos=(), error=None):
        self.segmentos, self.error, self.rutas, self.opciones = list(segmentos), error, [], []

    def transcribe(self, ruta, **opciones):
        self.rutas.append(ruta)
        self.opciones.append(opciones)
        assert os.path.exists(ruta), "el temporal debe existir mientras se transcribe"
        if self.error:
            raise self.error
        return iter(self.segmentos), SimpleNamespace(language="es")


def test_formato_de_marcas_de_tiempo():
    texto = audio.formatear_segmentos([_segmento(0, 75.4, " hola"), _segmento(75.4, 3725, " adiós ")])
    assert texto == "[00:00 -> 01:15]: hola\n[01:15 -> 62:05]: adiós"


def test_transcribe_en_espanol_y_devuelve_el_texto():
    modelo = ModeloFalso([_segmento(0, 2, " buenos días")])
    texto = audio.transcribir(b"audio", "mp3", "base", cargar=lambda nombre: modelo)
    assert texto == "[00:00 -> 00:02]: buenos días"
    assert modelo.opciones[0] == {"beam_size": 5, "language": "es"}
    assert modelo.rutas[0].endswith(".mp3")


def test_audio_sin_voz_da_texto_vacio():
    assert audio.transcribir(b"audio", "wav", "base", cargar=lambda nombre: ModeloFalso([])) == ""


def test_borra_el_temporal_cuando_va_bien():
    modelo = ModeloFalso([_segmento(0, 1, " hola")])
    audio.transcribir(b"audio", "wav", "base", cargar=lambda nombre: modelo)
    assert not os.path.exists(modelo.rutas[0])


def test_borra_el_temporal_aunque_falle_la_transcripcion():
    modelo = ModeloFalso(error=RuntimeError("audio corrupto"))
    with pytest.raises(RuntimeError):
        audio.transcribir(b"audio", "m4a", "base", cargar=lambda nombre: modelo)
    assert not os.path.exists(modelo.rutas[0])


def test_el_modelo_se_carga_una_sola_vez(monkeypatch):
    creados = []
    monkeypatch.setattr(audio, "WhisperModel", lambda *a, **k: creados.append((a, k)) or object())
    audio.cargar_modelo.cache_clear()
    primero = audio.cargar_modelo("base")
    segundo = audio.cargar_modelo("base")
    assert primero is segundo
    assert creados == [(("base",), {"device": "cpu", "compute_type": "int8"})]
    audio.cargar_modelo.cache_clear()
