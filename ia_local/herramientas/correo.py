"""Análisis de un correo tratándolo como contenido no confiable (prompt injection)."""
from ia_local.llm import preguntar
from ia_local.seguridad import construir_mensajes, nuevo_delimitador, senales_de_inyeccion, validar_analisis


def analizar(cliente, config, correo: dict) -> dict:
    """Clasificación, resumen y borrador de respuesta, más los avisos para el usuario."""
    sistema, usuario = construir_mensajes(correo, nuevo_delimitador())
    r = preguntar(cliente, config, sistema, usuario, temperatura=0.1)
    return {
        "analisis": r.texto,
        "senales": senales_de_inyeccion(correo),
        "problemas": validar_analisis(r.texto),
        "posible_recorte": r.posible_recorte,
    }
