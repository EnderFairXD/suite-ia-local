import pytest

from ia_local.flujos import EntradaVacia, desde_audio, desde_pdf
from ia_local.herramientas import contratos, reuniones
from ia_local.llm import Config
from tests.falsos import ClienteFalso
from tests.pdf_minimo import pdf_con_texto

CONFIG = Config(base_url="x", modelo="m", contexto=8192, modelo_whisper="small")


def test_pdf_con_texto_llega_a_la_herramienta():
    cliente = ClienteFalso(["informe"])
    r = desde_pdf(cliente, CONFIG, pdf_con_texto(["Cláusula primera: el alquiler es de un año."]), contratos.analizar)
    assert r.texto == "informe"
    assert "Cláusula primera" in cliente.usuarios()[0]


def test_pdf_escaneado_no_llama_a_ollama():
    cliente = ClienteFalso()
    with pytest.raises(EntradaVacia) as e:
        desde_pdf(cliente, CONFIG, pdf_con_texto([]), contratos.analizar)
    assert "no tiene texto" in str(e.value)
    assert cliente.llamadas == []


def test_audio_con_voz_devuelve_transcripcion_y_resultado():
    cliente = ClienteFalso(["minuta"])
    usados = []
    transcribir = lambda datos, ext, modelo: usados.append((ext, modelo)) or "[00:00 -> 00:05]: buenos días"
    transcripcion, r = desde_audio(cliente, CONFIG, b"audio", "mp3", reuniones.minuta, transcribir=transcribir)
    assert transcripcion == "[00:00 -> 00:05]: buenos días"
    assert r.texto == "minuta"
    assert usados == [("mp3", "small")]


def test_audio_sin_voz_no_llama_a_ollama():
    cliente = ClienteFalso()
    with pytest.raises(EntradaVacia) as e:
        desde_audio(cliente, CONFIG, b"audio", "wav", reuniones.minuta, transcribir=lambda *a: "  ")
    assert "voz" in str(e.value)
    assert cliente.llamadas == []


def test_pdf_corrupto_da_error_legible_sin_llamar_a_ollama():
    from ia_local.flujos import ErrorArchivo

    cliente = ClienteFalso()
    with pytest.raises(ErrorArchivo) as e:
        desde_pdf(cliente, CONFIG, b"esto no es un pdf", contratos.analizar)
    assert str(e.value).startswith("No se pudo leer el PDF")
    assert cliente.llamadas == []


def test_audio_ilegible_da_error_legible_sin_llamar_a_ollama():
    from ia_local.flujos import ErrorArchivo

    def transcribir(*_):
        raise RuntimeError("Invalid data found when processing input")

    cliente = ClienteFalso()
    with pytest.raises(ErrorArchivo) as e:
        desde_audio(cliente, CONFIG, b"x", "mp3", reuniones.minuta, transcribir=transcribir)
    assert str(e.value).startswith("No se pudo transcribir el audio")
    assert cliente.llamadas == []
