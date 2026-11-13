import ollama
import pytest

from ia_local.llm import Config, ErrorOllama, estado_ollama, estimar_tokens, preguntar
from tests.falsos import ClienteFalso

CONFIG = Config(base_url="http://localhost:11434", modelo="llama3.1", contexto=8192, modelo_whisper="base")


def test_estimar_tokens_redondea_hacia_arriba():
    assert estimar_tokens("a" * 7) == 2
    assert estimar_tokens("a" * 8) == 3
    assert estimar_tokens("") == 0


def test_preguntar_separa_sistema_y_usuario():
    cliente = ClienteFalso(["respuesta"])
    r = preguntar(cliente, CONFIG, "eres un analista", "el texto del usuario")
    mensajes = cliente.llamadas[0]["messages"]
    assert [m["role"] for m in mensajes] == ["system", "user"]
    assert mensajes[0]["content"] == "eres un analista"
    assert mensajes[1]["content"] == "el texto del usuario"
    assert r.texto == "respuesta"


def test_preguntar_usa_modelo_y_contexto_de_la_config():
    cliente = ClienteFalso()
    config = Config(base_url="x", modelo="mistral", contexto=4096, modelo_whisper="base")
    preguntar(cliente, config, "s", "u", temperatura=0.4)
    llamada = cliente.llamadas[0]
    assert llamada["model"] == "mistral"
    assert llamada["options"] == {"num_ctx": 4096, "temperature": 0.4}


def test_avisa_de_posible_recorte_si_ollama_llena_el_contexto():
    assert preguntar(ClienteFalso(tokens_leidos=8150), CONFIG, "s", "u").posible_recorte is True
    assert preguntar(ClienteFalso(tokens_leidos=2000), CONFIG, "s", "u").posible_recorte is False


def test_ollama_apagado_da_error_en_espanol():
    cliente = ClienteFalso(error=ConnectionError("Failed to connect to Ollama"))
    with pytest.raises(ErrorOllama) as e:
        preguntar(cliente, CONFIG, "s", "u")
    assert "No se puede conectar con Ollama" in str(e.value)
    assert "http://localhost:11434" in str(e.value)


def test_modelo_no_descargado_da_error_en_espanol():
    cliente = ClienteFalso(error=ollama.ResponseError("model 'llama3.1' not found", 404))
    with pytest.raises(ErrorOllama) as e:
        preguntar(cliente, CONFIG, "s", "u")
    assert "ollama pull llama3.1" in str(e.value)


def test_config_por_defecto(monkeypatch):
    for v in ("OLLAMA_BASE_URL", "MODELO", "CONTEXTO", "MODELO_WHISPER"):
        monkeypatch.delenv(v, raising=False)
    assert Config.desde_entorno(cargar_env=False) == Config(
        base_url="http://localhost:11434", modelo="llama3.1", contexto=8192, modelo_whisper="base"
    )


def test_config_lee_el_entorno(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://servidor:11434")
    monkeypatch.setenv("MODELO", "qwen2.5:7b")
    monkeypatch.setenv("CONTEXTO", "16384")
    monkeypatch.setenv("MODELO_WHISPER", "small")
    assert Config.desde_entorno(cargar_env=False) == Config(
        base_url="http://servidor:11434", modelo="qwen2.5:7b", contexto=16384, modelo_whisper="small"
    )


def test_estado_ollama_lista_modelos_o_explica_el_fallo():
    assert estado_ollama(ClienteFalso(modelos=["llama3.1:latest", "qwen2.5:3b"])) == (
        True, ["llama3.1:latest", "qwen2.5:3b"],
    )
    ok, mensaje = estado_ollama(ClienteFalso(error=ConnectionError("x")))
    assert ok is False
    assert "No se puede conectar con Ollama" in mensaje
