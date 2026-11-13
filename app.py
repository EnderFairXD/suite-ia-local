"""Suite de IA local: portada, navegación y estado de Ollama."""
import streamlit as st

from ia_local.llm import Config, crear_cliente, estado_ollama

st.set_page_config(page_title="Suite de IA local", page_icon="🧠", layout="wide")


@st.cache_data(ttl=15, show_spinner=False)
def _estado(base_url: str, modelo: str):
    config = Config(base_url=base_url, modelo=modelo, contexto=0, modelo_whisper="")
    return estado_ollama(crear_cliente(config, timeout=3), config)


config = Config.desde_entorno()
with st.sidebar:
    ok, info = _estado(config.base_url, config.modelo)
    if not ok:
        st.error(info)
    elif config.modelo in info or f"{config.modelo}:latest" in info:
        st.success(f"Ollama conectado · modelo **{config.modelo}** · contexto {config.contexto} tokens")
    else:
        st.warning(f"Ollama responde, pero no tiene el modelo «{config.modelo}». "
                   f"Descárgalo con: ollama pull {config.modelo}")

paginas = [
    st.Page("paginas/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("paginas/contratos.py", title="Contratos", icon="⚖️"),
    st.Page("paginas/documentacion.py", title="Documentación", icon="📝"),
    st.Page("paginas/correo.py", title="Correo", icon="📨"),
    st.Page("paginas/reuniones.py", title="Reuniones", icon="🎙️"),
    st.Page("paginas/estudio.py", title="Estudio", icon="🧠"),
]
st.navigation(paginas).run()
