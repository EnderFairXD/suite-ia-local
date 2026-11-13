# Suite de IA local

[![Tests](https://github.com/EnderFairXD/suite-ia-local/actions/workflows/tests.yml/badge.svg)](https://github.com/EnderFairXD/suite-ia-local/actions/workflows/tests.yml)

Cinco herramientas de IA que funcionan en tu propio equipo, con **Ollama** para el texto y
**Whisper** para el audio. Tus contratos, grabaciones y correos no se envían a ningún servicio en
la nube.

| Herramienta | Entrada | Resultado |
|---|---|---|
| ⚖️ **Contratos** | PDF | Resumen, cláusulas clave, riesgos y explicación en lenguaje sencillo |
| 📝 **Documentación** | Código Python | README técnico con diagrama Mermaid, a partir de su AST |
| 📨 **Correo** | Bandeja IMAP | Clasificación, prioridad, resumen y borrador de respuesta por correo |
| 🎙️ **Reuniones** | Audio | Transcripción con marcas de tiempo y minuta con acuerdos y tareas |
| 🧠 **Estudio** | Audio o PDF | Apuntes de una clase grabada; flashcards o examen tipo test de un temario |

## Textos largos

Cada modelo tiene una ventana de contexto. Si un texto no cabe, Ollama lo recorta **sin avisar** y
la respuesta parece completa aunque el modelo solo haya leído una parte. Aquí no pasa:

1. Antes de llamar al modelo se estima el tamaño del texto y se compara con lo que cabe.
2. Si no cabe, se divide por párrafos (o por frases, si no hay párrafos) y cada parte se procesa
   con un prompt de extracción. Después, una última llamada combina los resultados en el formato
   final; si los resultados tampoco caben juntos, se combinan por tandas.
3. La app dice en cuántas partes lo ha procesado, y avisa si aun así el modelo ha podido recortar
   algo (lo detecta con el número de tokens que Ollama dice haber leído).

## Privacidad y seguridad

- Lo único que sale del equipo es la conexión con tu servidor de Ollama (`OLLAMA_BASE_URL`) y, en
  la herramienta de correo, la conexión IMAP con tu propio correo.
- La herramienta de correo **solo lee**: no envía, mueve ni borra nada, y la respuesta sugerida es
  un borrador.
- Un correo lo escribe cualquiera, así que puede traer instrucciones escondidas para la IA
  (*prompt injection indirecta*). Las defensas salen de lo que medí en
  [llm-agent-prompt-injection-lab](https://github.com/EnderFairXD/llm-agent-prompt-injection-lab):
  el correo va como dato, entre etiquetas con un nombre aleatorio en cada análisis, y la app avisa
  de frases típicas de inyección y de respuestas que se salen del formato pedido. Reducen el
  riesgo, pero se pueden esquivar; lo que de verdad protege es que la IA no tenga herramientas para
  actuar.
- En todas las herramientas, las instrucciones van en el mensaje de sistema y el documento en el de
  usuario, con la indicación de tratarlo solo como datos.

## Instalación

Necesitas Python 3.12 y [Ollama](https://ollama.com/) con un modelo descargado:

```bash
ollama pull llama3.1
```

```bash
git clone https://github.com/EnderFairXD/suite-ia-local.git
cd suite-ia-local
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # ajusta el servidor de Ollama y, si usas el correo, tus credenciales
streamlit run app.py
```

La primera transcripción descarga el modelo de Whisper elegido; después se reutiliza.

## Configuración (`.env`)

| Variable | Por defecto | Para qué |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Servidor de Ollama (puede estar en otro equipo de tu red) |
| `MODELO` | `llama3.1` | Modelo de Ollama |
| `CONTEXTO` | `8192` | Ventana de contexto en tokens; si tu equipo lo permite, súbela |
| `MODELO_WHISPER` | `base` | `tiny`, `base`, `small`, `medium`…: más grande, más preciso y más lento |
| `EMAIL_USER`, `EMAIL_PASS`, `IMAP_SERVER` | — | Correo para la herramienta de correo (en Gmail, contraseña de aplicación) |

La barra lateral muestra si Ollama responde y si tiene el modelo configurado.

## Estructura

```
app.py              portada, navegación y estado de Ollama
paginas/            una página de Streamlit por herramienta (solo interfaz)
ia_local/           la lógica, sin Streamlit
  llm.py            cliente de Ollama, configuración y aviso de recorte
  troceado.py       división de textos largos y combinación de resultados
  pdf.py, audio.py, codigo.py, correo.py
  seguridad.py      defensas contra prompt injection
  flujos.py         de un archivo subido a una herramienta, comprobando que hay algo que analizar
  herramientas/     los prompts y el flujo de cada herramienta
tests/
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

No necesitan Ollama ni Whisper: usan un cliente falso, un servidor HTTP local que imita la API de
Ollama y PDFs generados en el propio test.

## Licencia

MIT © Javier Cortés Vidal
