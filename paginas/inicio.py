import streamlit as st

st.title("🧠 Suite de IA local")
st.markdown("""
Cinco herramientas de IA que funcionan en tu equipo, con **Ollama** para el texto y
**Whisper** para el audio. Tus documentos no se envían a ningún servicio en la nube.

| Herramienta | Qué hace |
|---|---|
| ⚖️ **Contratos** | Lee un contrato en PDF y saca un resumen, las cláusulas clave y los riesgos. |
| 📝 **Documentación** | Analiza un archivo Python y genera su README con un diagrama Mermaid. |
| 📨 **Correo** | Lee tus últimos correos por IMAP y los clasifica, resume y propone respuesta. |
| 🎙️ **Reuniones** | Transcribe una reunión y redacta la minuta con acuerdos y tareas. |
| 🧠 **Estudio** | Convierte una clase grabada en apuntes, y un temario en flashcards o un test. |

**Textos largos:** si un documento no cabe en el contexto del modelo, se divide en partes y los
resultados se combinan. La app te dice cuándo lo ha hecho.

**Privacidad:** lo único que sale del equipo es la conexión con tu servidor de Ollama (el de
`OLLAMA_BASE_URL`) y, en la herramienta de correo, la conexión IMAP con tu propio correo.
""")
