"""La librería `ollama` de verdad, contra un servidor HTTP local que imita la API de Ollama.

Comprueba lo que el cliente falso no puede: qué viaja por la red y cómo se lee la respuesta.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from ia_local.herramientas import contratos
from ia_local.llm import Config, ErrorOllama, crear_cliente, estado_ollama, preguntar


class _Ollama(BaseHTTPRequestHandler):
    peticiones = []
    modelo_existe = True

    def log_message(self, *_):
        pass

    def _responder(self, codigo, cuerpo):
        datos = json.dumps(cuerpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path == "/api/tags":
            self._responder(200, {"models": [{"name": "llama3.1:latest", "model": "llama3.1:latest"}]})

    def do_POST(self):
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).peticiones.append((self.path, cuerpo))
        if not type(self).modelo_existe:
            return self._responder(404, {"error": f"model '{cuerpo['model']}' not found"})
        usuario = cuerpo["messages"][-1]["content"]
        self._responder(200, {
            "model": cuerpo["model"], "created_at": "2026-11-13T00:00:00Z", "done": True,
            "message": {"role": "assistant", "content": f"recibidos {len(usuario)} caracteres"},
            "prompt_eval_count": len(usuario) // 4, "eval_count": 5,
        })


@pytest.fixture
def servidor():
    _Ollama.peticiones, _Ollama.modelo_existe = [], True
    http = HTTPServer(("127.0.0.1", 0), _Ollama)
    hilo = threading.Thread(target=http.serve_forever, daemon=True)
    hilo.start()
    yield Config(base_url=f"http://127.0.0.1:{http.server_port}", modelo="llama3.1", contexto=2048,
                 modelo_whisper="base")
    http.shutdown()


def test_la_peticion_lleva_modelo_contexto_y_roles(servidor):
    r = preguntar(crear_cliente(servidor), servidor, "instrucciones", "hola", temperatura=0.3)
    ruta, cuerpo = _Ollama.peticiones[0]
    assert ruta == "/api/chat"
    assert cuerpo["model"] == "llama3.1" and cuerpo["stream"] is False
    assert cuerpo["options"] == {"num_ctx": 2048, "temperature": 0.3}
    assert [m["role"] for m in cuerpo["messages"]] == ["system", "user"]
    assert r.texto == "recibidos 4 caracteres" and r.tokens_leidos == 1


def test_un_contrato_largo_viaja_en_varias_peticiones(servidor):
    texto = "\n\n".join(f"Cláusula {i}. " + "Obligaciones de las partes. " * 30 for i in range(15))
    r = contratos.analizar(crear_cliente(servidor), servidor, texto)
    assert r.partes > 1
    assert len(_Ollama.peticiones) == r.partes + 1
    assert all(len(c["messages"][-1]["content"]) / 3.5 <= 2048 for _, c in _Ollama.peticiones)


def test_modelo_no_descargado_llega_como_error_legible(servidor):
    _Ollama.modelo_existe = False
    with pytest.raises(ErrorOllama) as e:
        preguntar(crear_cliente(servidor), servidor, "s", "u")
    assert "ollama pull llama3.1" in str(e.value)


def test_estado_con_el_servidor_real(servidor):
    assert estado_ollama(crear_cliente(servidor, timeout=3), servidor) == (True, ["llama3.1:latest"])
