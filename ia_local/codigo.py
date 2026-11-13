"""Estructura de un archivo Python (funciones, clases y métodos) mediante su AST."""
import ast

SIN_DOCSTRING = "Sin documentación interna."
FUNCIONES = (ast.FunctionDef, ast.AsyncFunctionDef)


def leer_codigo(datos: bytes) -> tuple[str, bool]:
    """Texto del archivo. El bool dice si había bytes que no eran UTF-8 y se reemplazaron."""
    try:
        return datos.decode("utf-8-sig"), False
    except UnicodeDecodeError:
        return datos.decode("utf-8", errors="replace"), True


def _argumentos(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    a = nodo.args
    nombres = [x.arg for x in a.posonlyargs + a.args]
    if a.vararg:
        nombres.append("*" + a.vararg.arg)
    nombres += [x.arg for x in a.kwonlyargs]
    if a.kwarg:
        nombres.append("**" + a.kwarg.arg)
    return nombres


def _funcion(nodo) -> dict:
    return {
        "nombre": nodo.name,
        "argumentos": _argumentos(nodo),
        "asincrona": isinstance(nodo, ast.AsyncFunctionDef),
        "docstring": ast.get_docstring(nodo) or SIN_DOCSTRING,
    }


def analizar_codigo(codigo: str) -> dict:
    """Funciones de nivel de módulo y clases con sus métodos, o {"error": ...} si no compila."""
    try:
        arbol = ast.parse(codigo)
    except SyntaxError as e:
        return {"error": f"Error de sintaxis en la línea {e.lineno}: {e.msg}"}
    funciones = [_funcion(n) for n in arbol.body if isinstance(n, FUNCIONES)]
    clases = [
        {
            "nombre": n.name,
            "metodos": [_funcion(m) for m in n.body if isinstance(m, FUNCIONES)],
            "docstring": ast.get_docstring(n) or SIN_DOCSTRING,
        }
        for n in arbol.body if isinstance(n, ast.ClassDef)
    ]
    return {"funciones": funciones, "clases": clases}
