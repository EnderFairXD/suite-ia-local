import streamlit as st

from ia_local.flujos import desde_audio, desde_pdf
from ia_local.herramientas import estudio
from ia_local.interfaz import cliente_y_config, con_errores_legibles, mostrar_resultado

st.title("🧠 Estudio")
st.markdown("Convierte una clase grabada en apuntes, o un temario en PDF en flashcards o en un examen tipo test.")

clase, temario = st.tabs(["🎙️ Clase grabada → apuntes", "📚 Temario en PDF → flashcards o examen"])

with clase:
    audio = st.file_uploader("Grabación de la clase", type=["mp3", "wav", "m4a"])
    if audio and st.button("🚀 Generar apuntes"):
        cliente, config = cliente_y_config()
        with con_errores_legibles(), st.spinner("Transcribiendo y redactando los apuntes… (puede tardar)"):
            _, resultado = desde_audio(cliente, config, audio.getvalue(),
                                       audio.name.rsplit(".", 1)[-1], estudio.apuntes)
            mostrar_resultado(resultado, "apuntes_clase.md")

with temario:
    pdf = st.file_uploader("Temario (PDF)", type="pdf")
    tipo = st.radio("Material", ["Flashcards", "Examen tipo test"], horizontal=True)
    if pdf and st.button("🧠 Generar material"):
        cliente, config = cliente_y_config()
        herramienta, nombre = ((estudio.flashcards, "flashcards.md") if tipo == "Flashcards"
                               else (estudio.examen, "examen.md"))
        with con_errores_legibles(), st.spinner("Generando el material con Ollama…"):
            mostrar_resultado(desde_pdf(cliente, config, pdf.getvalue(), herramienta), nombre)
