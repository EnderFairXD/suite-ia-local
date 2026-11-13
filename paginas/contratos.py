import streamlit as st

from ia_local.flujos import desde_pdf
from ia_local.herramientas import contratos
from ia_local.interfaz import cliente_y_config, con_errores_legibles, mostrar_resultado

st.title("⚖️ Contratos")
st.markdown("Sube un contrato en PDF y obtén un informe con el resumen, las cláusulas clave y los riesgos.")

archivo = st.file_uploader("Contrato (PDF)", type="pdf")
if archivo and st.button("🚀 Analizar el contrato"):
    cliente, config = cliente_y_config()
    with con_errores_legibles(), st.spinner("Leyendo el contrato y analizándolo con Ollama…"):
        resultado = desde_pdf(cliente, config, archivo.getvalue(), contratos.analizar)
        mostrar_resultado(resultado, "informe_contrato.md")
