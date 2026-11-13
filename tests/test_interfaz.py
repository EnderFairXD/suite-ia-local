from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APAGADO = "http://127.0.0.1:9"  # puerto cerrado: Ollama "apagado"

PAGINAS = {
    "inicio.py": "Suite de IA local",
    "contratos.py": "Contratos",
    "documentacion.py": "Documentación",
    "correo.py": "Correo",
    "reuniones.py": "Reuniones",
    "estudio.py": "Estudio",
}


@pytest.fixture(autouse=True)
def sin_ollama(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", APAGADO)


@pytest.mark.parametrize("archivo, titulo", PAGINAS.items(), ids=list(PAGINAS))
def test_cada_pagina_carga_sin_errores(archivo, titulo):
    at = AppTest.from_file(str(RAIZ / "paginas" / archivo), default_timeout=30).run()
    assert not at.exception, at.exception
    assert any(titulo in t.value for t in at.title)


def test_la_app_arranca_en_la_portada():
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=30).run()
    assert not at.exception, at.exception
    assert any("Suite de IA local" in t.value for t in at.title)


def test_sin_ollama_la_barra_lateral_lo_dice_sin_traza():
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=30).run()
    assert not at.exception
    errores = [e.value for e in at.sidebar.error]
    assert any("No se puede conectar con Ollama" in e and APAGADO in e for e in errores)
