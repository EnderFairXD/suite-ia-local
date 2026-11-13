"""README técnico de un archivo Python a partir de su estructura (AST) y su código."""
import json

from ia_local.herramientas import DATOS
from ia_local.llm import CARACTERES_POR_TOKEN, estimar_tokens, preguntar
from ia_local.troceado import RESERVA_RESPUESTA, ResultadoLargo

SISTEMA_FINAL = f"""Eres ingeniero de software principal y experto en arquitectura. Genera un README.md
técnico en español a partir de la estructura analizada y el código que te envía el usuario.
{DATOS}

El documento Markdown debe tener estas secciones obligatorias:

1. 🚀 **Descripción general**: qué resuelve este código y su propósito.
2. 📊 **Diagrama de flujo o arquitectura**: un diagrama en sintaxis **Mermaid.js**, solo dentro de un
   bloque ```mermaid ... ```, que muestre cómo interactúan las funciones o cómo fluyen los datos.
3. 🛠️ **Componentes**: las funciones y clases según la estructura analizada, con qué hace cada
   parámetro.
4. 💡 **Ejemplo de integración**: un bloque de código que muestre cómo importar y usar este archivo.

Si el usuario indica que el código está recortado, básate en la estructura para lo que falte."""

AVISO_RECORTE = "\n# […código recortado: no cabía entero en el contexto del modelo…]\n"


def _mensaje(estructura: dict, codigo: str) -> str:
    return (f"Estructura analizada (JSON):\n{json.dumps(estructura, indent=2, ensure_ascii=False)}\n\n"
            f"Código fuente:\n```python\n{codigo}\n```")


def generar_readme(cliente, config, codigo: str, estructura: dict) -> ResultadoLargo:
    """Si el código no cabe, se envía la estructura entera y el código recortado, con aviso."""
    presupuesto = config.contexto - estimar_tokens(SISTEMA_FINAL) - RESERVA_RESPUESTA
    recortado = False
    if estimar_tokens(_mensaje(estructura, codigo)) > presupuesto:
        libre = presupuesto - estimar_tokens(_mensaje(estructura, AVISO_RECORTE))
        codigo = codigo[:max(0, int(libre * CARACTERES_POR_TOKEN))] + AVISO_RECORTE
        recortado = True
    r = preguntar(cliente, config, SISTEMA_FINAL, _mensaje(estructura, codigo), temperatura=0.2)
    return ResultadoLargo(r.texto, 1, recortado or r.posible_recorte)
