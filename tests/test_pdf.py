import io

from ia_local.pdf import extraer_texto_pdf
from tests.pdf_minimo import pdf_con_texto


def test_extrae_el_texto_de_un_pdf():
    datos = pdf_con_texto(["Contrato de arrendamiento", "Cláusula 1: duración de un año."])
    texto = extraer_texto_pdf(datos)
    assert "Contrato de arrendamiento" in texto
    assert "Cláusula 1: duración de un año." in texto


def test_acepta_un_archivo_abierto():
    assert "Hola" in extraer_texto_pdf(io.BytesIO(pdf_con_texto(["Hola"])))


def test_pdf_sin_texto_devuelve_vacio():
    assert extraer_texto_pdf(pdf_con_texto([])) == ""
