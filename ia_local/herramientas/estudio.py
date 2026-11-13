"""Material de estudio: apuntes desde una clase grabada, y flashcards o examen desde un PDF."""
from types import SimpleNamespace

from ia_local.herramientas import DATOS, FIEL
from ia_local.troceado import ResultadoLargo, procesar_largo

_FORMATO_APUNTES = """elabora unos apuntes definitivos en Markdown, en español, con esta estructura:

1. 🎯 **Tema principal**: de qué trata la clase, en 2 líneas.
2. 📚 **Desarrollo teórico**: los conceptos paso a paso, con títulos y subtítulos y **negrita** en
   los términos clave.
3. ⚠️ **Ojo al dato**: lo que el profesor recalcó o dijo que "suele caer en el examen". Si no hay
   nada, omite esta sección.
4. 📝 **Resumen exprés**: 3 viñetas con lo mínimo que hay que saber antes del examen."""

APUNTES = SimpleNamespace(
    SISTEMA_FINAL=f"""Eres un estudiante universitario de matrícula de honor. Te envían la transcripción de
una clase. {DATOS}

A partir de ella, {_FORMATO_APUNTES}""",
    SISTEMA_PARTE=f"""Eres un estudiante universitario de matrícula de honor. Te envían una parte de la
transcripción de una clase larga. {DATOS}

Toma notas detalladas de esta parte: conceptos explicados, definiciones, ejemplos y todo lo que el
profesor recalque. {FIEL}""",
    SISTEMA_COMBINAR=f"""Eres un estudiante universitario de matrícula de honor. Te envían, en orden y
separadas por ---, las notas de las partes de una misma clase. {DATOS}

Con esas notas, {_FORMATO_APUNTES}""",
)

_CONCEPTOS = f"""Te envían una parte de un temario largo. {DATOS}

Extrae en viñetas los conceptos, definiciones y datos más importantes de esta parte. {FIEL}"""

_FORMATO_FLASHCARDS = """Genera como máximo 10 flashcards (pregunta y respuesta corta) con los
conceptos más importantes para memorizar. Usa estrictamente este formato en cada tarjeta:

**P:** [pregunta conceptual y directa]
**R:** [respuesta de 2 líneas como máximo]
---"""

FLASHCARDS = SimpleNamespace(
    SISTEMA_FINAL=f"Eres experto en estudio con repaso espaciado (Anki). Te envían un temario. {DATOS}\n\n"
                  + _FORMATO_FLASHCARDS,
    SISTEMA_PARTE="Eres experto en estudio con repaso espaciado. " + _CONCEPTOS,
    SISTEMA_COMBINAR="Eres experto en estudio con repaso espaciado (Anki). Te envían, en orden y separados "
                     f"por ---, los conceptos clave de las partes de un mismo temario. {DATOS}\n\n"
                     + _FORMATO_FLASHCARDS,
)

_FORMATO_EXAMEN = """Genera 5 preguntas tipo test basándote ÚNICAMENTE en el material. Reglas:

- Cada pregunta tiene 4 opciones (A, B, C y D) y solo una es correcta.
- Las incorrectas deben sonar plausibles pero ser falsas según el material.
- Al final de todas las preguntas, incluye una sección "Plantilla de corrección" con las respuestas."""

EXAMEN = SimpleNamespace(
    SISTEMA_FINAL=f"Eres un profesor universitario diseñando un examen tipo test. Te envían un temario. {DATOS}\n\n"
                  + _FORMATO_EXAMEN,
    SISTEMA_PARTE="Eres un profesor universitario. " + _CONCEPTOS,
    SISTEMA_COMBINAR="Eres un profesor universitario diseñando un examen tipo test. Te envían, en orden y "
                     f"separados por ---, los conceptos clave de las partes de un mismo temario. {DATOS}\n\n"
                     + _FORMATO_EXAMEN,
)


def _procesar(prompts, cliente, config, texto, temperatura) -> ResultadoLargo:
    return procesar_largo(cliente, config, texto, sistema_final=prompts.SISTEMA_FINAL,
                          sistema_parte=prompts.SISTEMA_PARTE, sistema_combinar=prompts.SISTEMA_COMBINAR,
                          temperatura=temperatura)


def apuntes(cliente, config, transcripcion: str) -> ResultadoLargo:
    return _procesar(APUNTES, cliente, config, transcripcion, 0.3)


def flashcards(cliente, config, texto: str) -> ResultadoLargo:
    return _procesar(FLASHCARDS, cliente, config, texto, 0.2)


def examen(cliente, config, texto: str) -> ResultadoLargo:
    return _procesar(EXAMEN, cliente, config, texto, 0.1)
