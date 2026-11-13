import streamlit as st

from ia_local.codigo import analizar_codigo, leer_codigo
from ia_local.herramientas import documentacion
from ia_local.interfaz import cliente_y_config, con_errores_legibles, mostrar_resultado

st.title("📝 Documentación")
st.markdown("Analiza un archivo Python (su estructura con AST) y genera un README técnico con diagrama Mermaid.")

modo = st.radio("Entrada", ["Pegar código", "Subir archivo .py"], horizontal=True)
codigo = ""
if modo == "Pegar código":
    codigo = st.text_area("Código Python", height=250, placeholder="def mi_funcion():\n    ...")
else:
    archivo = st.file_uploader("Archivo Python", type="py")
    if archivo:
        codigo, reemplazos = leer_codigo(archivo.getvalue())
        if reemplazos:
            st.warning("El archivo no estaba en UTF-8: algunos caracteres se han sustituido.")

if codigo.strip() and st.button("🚀 Generar README"):
    estructura = analizar_codigo(codigo)
    if "error" in estructura:
        st.error(estructura["error"])
    else:
        cliente, config = cliente_y_config()
        with con_errores_legibles(), st.spinner("Generando la documentación con Ollama…"):
            mostrar_resultado(documentacion.generar_readme(cliente, config, codigo, estructura), "README.md")
