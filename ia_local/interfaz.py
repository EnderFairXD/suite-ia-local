"""Piezas de interfaz comunes a las páginas."""
from contextlib import contextmanager

import streamlit as st

from ia_local.correo import ErrorCorreo
from ia_local.flujos import EntradaVacia
from ia_local.llm import Config, ErrorOllama, crear_cliente
from ia_local.troceado import ResultadoLargo


def cliente_y_config():
    config = Config.desde_entorno()
    return crear_cliente(config), config


@contextmanager
def con_errores_legibles():
    """Los fallos previstos se muestran como un mensaje, no como una traza."""
    try:
        yield
    except (ErrorOllama, ErrorCorreo, EntradaVacia) as e:
        st.error(str(e))


def avisos(resultado: ResultadoLargo):
    if resultado.partes > 1:
        st.info(f"El texto no cabía entero en el contexto del modelo: se ha procesado en "
                f"{resultado.partes} partes y después se han combinado.")
    if resultado.posible_recorte:
        st.warning("Puede que el modelo haya recortado parte del texto. Revisa el resultado con cuidado "
                   "o sube CONTEXTO en el .env si tu equipo lo permite.")


def mostrar_resultado(resultado: ResultadoLargo, nombre_archivo: str):
    avisos(resultado)
    st.download_button(f"💾 Descargar {nombre_archivo}", data=resultado.texto,
                       file_name=nombre_archivo, mime="text/markdown")
    st.markdown(resultado.texto)
