"""Textos que no caben en el contexto: dividirlos y combinar los resultados."""
import math
import re
from dataclasses import dataclass

from ia_local.llm import CARACTERES_POR_TOKEN, Config, estimar_tokens, preguntar

# Tokens que se dejan libres para la respuesta del modelo.
RESERVA_RESPUESTA = 1024
SEPARADOR = "\n\n---\n\n"


@dataclass(frozen=True)
class ResultadoLargo:
    texto: str
    partes: int
    posible_recorte: bool


def _cortar_por_caracteres(texto: str, max_tokens: int) -> list[str]:
    paso = max(1, math.floor(max_tokens * CARACTERES_POR_TOKEN))
    return [texto[i:i + paso] for i in range(0, len(texto), paso)]


def _unidades(texto: str, max_tokens: int) -> list[tuple[str, str]]:
    """Párrafos, o frases si un párrafo no cabe, o trozos de caracteres si una frase no cabe.
    Cada unidad lleva el separador con el que se une a la anterior."""
    unidades = []
    for parrafo in re.split(r"\n\s*\n", texto.strip()):
        parrafo = parrafo.strip()
        if not parrafo:
            continue
        if estimar_tokens(parrafo) <= max_tokens:
            unidades.append(("\n\n", parrafo))
            continue
        for i, frase in enumerate(re.split(r"(?<=[.!?])\s+", parrafo)):
            union = "\n\n" if i == 0 else " "
            if estimar_tokens(frase) <= max_tokens:
                unidades.append((union, frase))
            else:
                for j, pedazo in enumerate(_cortar_por_caracteres(frase, max_tokens)):
                    unidades.append((union if j == 0 else "", pedazo))
    return unidades


def trocear(texto: str, max_tokens: int) -> list[str]:
    """Divide el texto en trozos de como mucho `max_tokens`, sin perder contenido."""
    trozos, actual = [], ""
    for union, unidad in _unidades(texto, max_tokens):
        candidato = actual + union + unidad if actual else unidad
        if estimar_tokens(candidato) <= max_tokens:
            actual = candidato
        else:
            trozos.append(actual)
            actual = unidad
    if actual:
        trozos.append(actual)
    return trozos


def _presupuesto(config: Config, sistema: str) -> int:
    return config.contexto - estimar_tokens(sistema) - RESERVA_RESPUESTA


def _combinar(cliente, config, parciales, sistema_combinar, temperatura) -> tuple[str, bool]:
    """Combina los resultados parciales; si no caben juntos, por tandas hasta que quepan."""
    presupuesto = _presupuesto(config, sistema_combinar)
    recorte = False
    while True:
        unido = SEPARADOR.join(parciales)
        if estimar_tokens(unido) <= presupuesto:
            r = preguntar(cliente, config, sistema_combinar, unido, temperatura)
            return r.texto, recorte or r.posible_recorte
        # Cada parcial cabe en media tanda: así cada tanda junta al menos dos y el número
        # de parciales baja en cada vuelta.
        maximo = (presupuesto - estimar_tokens(SEPARADOR)) // 2
        recortados = []
        for p in parciales:
            if estimar_tokens(p) > maximo:
                p = _cortar_por_caracteres(p, maximo)[0]
                recorte = True
            recortados.append(p)
        tandas, actual = [], []
        for p in recortados:
            if actual and estimar_tokens(SEPARADOR.join(actual + [p])) > presupuesto:
                tandas.append(actual)
                actual = []
            actual.append(p)
        tandas.append(actual)
        parciales = []
        for tanda in tandas:
            r = preguntar(cliente, config, sistema_combinar, SEPARADOR.join(tanda), temperatura)
            recorte = recorte or r.posible_recorte
            parciales.append(r.texto)


def procesar_largo(cliente, config: Config, texto: str, *, sistema_final: str, sistema_parte: str,
                   sistema_combinar: str, temperatura: float = 0.2) -> ResultadoLargo:
    """Si el texto cabe, una sola llamada. Si no, una por parte y una combinación final."""
    if estimar_tokens(texto) <= _presupuesto(config, sistema_final):
        r = preguntar(cliente, config, sistema_final, texto, temperatura)
        return ResultadoLargo(r.texto, 1, r.posible_recorte)

    trozos = trocear(texto, _presupuesto(config, sistema_parte) - estimar_tokens("Parte 999 de 999:\n\n"))
    parciales, recorte = [], False
    for i, trozo in enumerate(trozos, 1):
        r = preguntar(cliente, config, sistema_parte, f"Parte {i} de {len(trozos)}:\n\n{trozo}", temperatura)
        parciales.append(r.texto)
        recorte = recorte or r.posible_recorte
    final, recorte_final = _combinar(cliente, config, parciales, sistema_combinar, temperatura)
    return ResultadoLargo(final, len(trozos), recorte or recorte_final)
