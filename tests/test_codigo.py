from ia_local.codigo import analizar_codigo, leer_codigo

CODIGO = '''
def suelta(a, b=1):
    """Una función de módulo."""

async def descargar(url):
    pass

class Servicio:
    """Un servicio."""

    def iniciar(self, puerto):
        """Arranca."""

    async def parar(self):
        pass
'''


def test_los_metodos_no_aparecen_como_funciones_sueltas():
    estructura = analizar_codigo(CODIGO)
    assert [f["nombre"] for f in estructura["funciones"]] == ["suelta", "descargar"]
    assert [m["nombre"] for m in estructura["clases"][0]["metodos"]] == ["iniciar", "parar"]


def test_reconoce_funciones_y_metodos_async():
    estructura = analizar_codigo(CODIGO)
    funciones = {f["nombre"]: f for f in estructura["funciones"]}
    metodos = {m["nombre"]: m for m in estructura["clases"][0]["metodos"]}
    assert funciones["descargar"]["asincrona"] is True
    assert funciones["suelta"]["asincrona"] is False
    assert metodos["parar"]["asincrona"] is True


def test_guarda_argumentos_y_docstrings():
    estructura = analizar_codigo(CODIGO)
    suelta = estructura["funciones"][0]
    assert suelta["argumentos"] == ["a", "b"]
    assert suelta["docstring"] == "Una función de módulo."
    assert estructura["funciones"][1]["docstring"] == "Sin documentación interna."
    assert estructura["clases"][0]["docstring"] == "Un servicio."


def test_error_de_sintaxis_dice_la_linea():
    resultado = analizar_codigo("def roto(:\n    pass\n")
    assert resultado.keys() == {"error"}
    assert "línea 1" in resultado["error"]


def test_codigo_no_utf8_se_lee_con_aviso():
    texto, hubo_reemplazos = leer_codigo("print('año')".encode("latin-1"))
    assert hubo_reemplazos is True
    assert texto.startswith("print('a")
    assert leer_codigo("print('año')".encode("utf-8")) == ("print('año')", False)
