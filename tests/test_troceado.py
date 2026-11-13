import random
import re

from ia_local.llm import Config, estimar_tokens
from ia_local.troceado import ResultadoLargo, procesar_largo, trocear
from tests.falsos import ClienteFalso

FINAL, PARTE, COMBINAR = "prompt final", "prompt de cada parte", "prompt para combinar"


def _sin_espacios(texto):
    return re.sub(r"\s+", "", texto)


def _config(contexto):
    return Config(base_url="x", modelo="m", contexto=contexto, modelo_whisper="base")


def test_texto_corto_es_un_solo_trozo():
    assert trocear("hola mundo", 100) == ["hola mundo"]
    assert trocear("", 100) == []


def test_corta_por_parrafos_sin_perder_nada():
    parrafos = [f"Párrafo {i}: " + "texto de prueba " * 6 for i in range(10)]
    texto = "\n\n".join(parrafos)
    trozos = trocear(texto, 60)
    assert len(trozos) > 1
    assert all(estimar_tokens(t) <= 60 for t in trozos)
    assert _sin_espacios("".join(trozos)) == _sin_espacios(texto)
    enteros = [p.strip() for p in parrafos]
    for t in trozos:  # cada trozo está hecho de párrafos enteros
        assert all(p in enteros for p in t.split("\n\n"))


def test_texto_sin_parrafos_se_corta_por_frases():
    texto = " ".join(f"Esta es la frase número {i} del contrato." for i in range(80))
    trozos = trocear(texto, 50)
    assert len(trozos) > 1
    assert all(estimar_tokens(t) <= 50 for t in trozos)
    assert all(t.endswith(".") for t in trozos)
    assert _sin_espacios("".join(trozos)) == _sin_espacios(texto)


def test_frase_gigante_se_corta_por_caracteres():
    texto = "a" * 1000
    trozos = trocear(texto, 50)
    assert all(estimar_tokens(t) <= 50 for t in trozos)
    assert "".join(trozos) == texto


def test_ningun_trozo_supera_el_maximo():
    azar = random.Random(7)
    palabras = ["contrato", "cláusula", "parte", "penalización.", "riesgo,", "plazo\n\n", "pago"]
    for tamano in range(50):
        texto = " ".join(azar.choice(palabras) for _ in range(tamano * 40))
        maximo = 20 + tamano * 3
        trozos = trocear(texto, maximo)
        assert all(estimar_tokens(t) <= maximo for t in trozos), tamano
        assert _sin_espacios("".join(trozos)) == _sin_espacios(texto)


def test_si_cabe_hace_una_sola_llamada_con_el_prompt_final():
    cliente = ClienteFalso(["informe"])
    r = procesar_largo(cliente, _config(8192), "un contrato corto",
                       sistema_final=FINAL, sistema_parte=PARTE, sistema_combinar=COMBINAR)
    assert r == ResultadoLargo(texto="informe", partes=1, posible_recorte=False)
    assert cliente.sistemas() == [FINAL]
    assert cliente.usuarios() == ["un contrato corto"]


def test_si_no_cabe_procesa_cada_parte_y_combina():
    cliente = ClienteFalso(lambda m: "final" if m[0]["content"] == COMBINAR else "notas de la parte")
    texto = "\n\n".join(f"Cláusula {i}. " + "Texto del contrato. " * 30 for i in range(20))
    r = procesar_largo(cliente, _config(2048), texto,
                       sistema_final=FINAL, sistema_parte=PARTE, sistema_combinar=COMBINAR)
    assert r.partes > 1
    assert cliente.sistemas() == [PARTE] * r.partes + [COMBINAR]
    assert r.texto == "final"
    # Ninguna parte se queda sin leer.
    assert _sin_espacios(texto) in _sin_espacios("".join(u.split("\n\n", 1)[1] for u in cliente.usuarios()[:-1]))


def test_combina_por_tandas_si_los_parciales_no_caben_juntos():
    def responder(mensajes):
        return "resumen " * 300 if mensajes[0]["content"] == PARTE else "combinado"
    cliente = ClienteFalso(responder)
    texto = "\n\n".join("Texto largo de una reunión. " * 25 for _ in range(30))
    r = procesar_largo(cliente, _config(2048), texto,
                       sistema_final=FINAL, sistema_parte=PARTE, sistema_combinar=COMBINAR)
    combinaciones = [s for s in cliente.sistemas() if s == COMBINAR]
    assert len(combinaciones) > 1
    assert cliente.sistemas()[-1] == COMBINAR
    assert all(estimar_tokens(COMBINAR) + estimar_tokens(u) <= 2048 for s, u in
               zip(cliente.sistemas(), cliente.usuarios()) if s == COMBINAR)
    assert r.texto == "combinado"


def test_propaga_el_aviso_de_recorte():
    cliente = ClienteFalso(["informe"], tokens_leidos=8190)
    r = procesar_largo(cliente, _config(8192), "texto",
                       sistema_final=FINAL, sistema_parte=PARTE, sistema_combinar=COMBINAR)
    assert r.posible_recorte is True
