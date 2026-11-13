import streamlit as st

from ia_local.flujos import desde_audio
from ia_local.herramientas import reuniones
from ia_local.interfaz import cliente_y_config, con_errores_legibles, mostrar_resultado

st.title("🎙️ Reuniones")
st.markdown("Sube la grabación de una reunión: se transcribe en tu equipo con Whisper y se redacta la minuta.")

audio = st.file_uploader("Grabación", type=["mp3", "wav", "m4a"])
if audio and st.button("🚀 Procesar la reunión"):
    cliente, config = cliente_y_config()
    with con_errores_legibles(), st.spinner("Transcribiendo y redactando la minuta… (puede tardar)"):
        transcripcion, resultado = desde_audio(cliente, config, audio.getvalue(),
                                               audio.name.rsplit(".", 1)[-1], reuniones.minuta)
        minuta, texto = st.tabs(["📋 Minuta", "📝 Transcripción"])
        with minuta:
            mostrar_resultado(resultado, "minuta_reunion.md")
        with texto:
            st.text_area("Transcripción con marcas de tiempo", transcripcion, height=400)
