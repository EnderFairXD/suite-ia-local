import os

import streamlit as st

from ia_local.correo import leer_correos
from ia_local.herramientas import correo
from ia_local.interfaz import cliente_y_config, con_errores_legibles

st.title("📨 Correo")
st.markdown("Lee tus últimos correos por IMAP y los clasifica, resume y propone una respuesta. "
            "**Solo lee:** no envía, mueve ni borra nada.")

cantidad = st.slider("Correos que analizar", 1, 10, 3)
if st.button("📥 Leer y analizar la bandeja"):
    cliente, config = cliente_y_config()
    with con_errores_legibles():
        with st.spinner("Conectando con tu correo…"):
            correos = leer_correos(os.environ.get("EMAIL_USER", ""), os.environ.get("EMAIL_PASS", ""),
                                   os.environ.get("IMAP_SERVER", "imap.gmail.com"), cantidad)
        st.success(f"Se han leído {len(correos)} correos.")
        for i, mensaje in enumerate(correos):
            with st.expander(f"✉️ {mensaje['remitente']} · {mensaje['asunto']}", expanded=i == 0):
                original, analisis = st.columns(2)
                with original:
                    st.caption(f"**Fecha:** {mensaje['fecha']}")
                    st.text_area("Cuerpo", mensaje["cuerpo"], height=200, disabled=True, key=f"cuerpo_{i}")
                with analisis, st.spinner("Analizando con Ollama…"):
                    r = correo.analizar(cliente, config, mensaje)
                    if r["senales"]:
                        st.warning("⚠️ Posible intento de manipulación de la IA (prompt injection): "
                                   + "; ".join(r["senales"]) + ". Revisa el correo original antes de fiarte del análisis.")
                    if r["problemas"]:
                        st.warning("La respuesta de la IA no sigue el formato esperado (" + "; ".join(r["problemas"])
                                   + "). Puede que el correo la haya desviado.")
                    st.markdown(r["analisis"])
                    st.caption("La respuesta sugerida es solo un borrador: la app no envía nada.")
