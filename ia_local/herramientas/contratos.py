"""Análisis de contratos en PDF."""
from ia_local.herramientas import DATOS, FIEL
from ia_local.troceado import ResultadoLargo, procesar_largo

_INFORME = """Proporciona un informe estructurado en Markdown, en español, con estas secciones:

1. **Resumen automático**: un resumen de 3 o 4 líneas sobre de qué trata el contrato.
2. **Cláusulas importantes**: viñetas con las 3 o 4 cláusulas más críticas.
3. **Riesgos potenciales**: cualquier trampa, penalización o riesgo oculto para las partes.
4. **Explicación en lenguaje sencillo**: el contrato explicado como a alguien de 15 años."""

SISTEMA_FINAL = f"""Eres un abogado experto y analista de riesgos. Analiza el contrato que te envía el usuario.
{DATOS}

{_INFORME}"""

SISTEMA_PARTE = f"""Eres un abogado experto. Te envían una parte de un contrato largo.
{DATOS}

Extrae en viñetas, de esta parte: de qué trata; las cláusulas importantes (con su número si
aparece); obligaciones, plazos, importes y penalizaciones; y cualquier riesgo para las partes.
{FIEL}"""

SISTEMA_COMBINAR = f"""Eres un abogado experto y analista de riesgos. Te envían, en orden, las notas
extraídas de las partes de un mismo contrato, separadas por ---.
{DATOS}

Con esas notas, {_INFORME[0].lower()}{_INFORME[1:]}"""


def analizar(cliente, config, texto: str) -> ResultadoLargo:
    return procesar_largo(cliente, config, texto, sistema_final=SISTEMA_FINAL,
                          sistema_parte=SISTEMA_PARTE, sistema_combinar=SISTEMA_COMBINAR, temperatura=0.2)
