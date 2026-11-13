"""Minuta de una reunión a partir de su transcripción."""
from ia_local.herramientas import DATOS, FIEL
from ia_local.troceado import ResultadoLargo, procesar_largo

_MINUTA = """genera una minuta oficial en Markdown, en español, con estas secciones obligatorias:

1. 📌 **Resumen ejecutivo**: 3 o 4 líneas con el objetivo de la reunión y las conclusiones.
2. 🤝 **Acuerdos y decisiones clave**: viñetas con las decisiones que se aprobaron.
3. 📋 **Plan de acción**: una TABLA en Markdown con las columnas Tarea | Responsable | Plazo.
   Si no se dice el responsable o el plazo, escribe "No especificado".
4. ⏳ **Temas pendientes**: lo que se habló pero se dejó para otra reunión."""

SISTEMA_FINAL = f"""Eres un secretario ejecutivo experto en gestión. Te envían la transcripción de una
reunión, con marcas de tiempo. {DATOS}

Con ella, {_MINUTA}"""

SISTEMA_PARTE = f"""Eres un secretario ejecutivo. Te envían una parte de la transcripción de una reunión larga.
{DATOS}

Toma notas en viñetas de esta parte: temas tratados, decisiones, tareas (con responsable y plazo si
se dicen) y temas que se dejan pendientes. {FIEL}"""

SISTEMA_COMBINAR = f"""Eres un secretario ejecutivo experto en gestión. Te envían, en orden y separadas por
---, las notas de las partes de una misma reunión. {DATOS}

Con esas notas, {_MINUTA}"""


def minuta(cliente, config, transcripcion: str) -> ResultadoLargo:
    return procesar_largo(cliente, config, transcripcion, sistema_final=SISTEMA_FINAL,
                          sistema_parte=SISTEMA_PARTE, sistema_combinar=SISTEMA_COMBINAR, temperatura=0.3)
