"""PDF de una página hecho a mano, sin dependencias, para los tests."""


def _escapar(linea: str) -> str:
    return linea.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_con_texto(lineas: list[str]) -> bytes:
    """Una página A4 con cada línea escrita en Helvetica. Sin líneas, la página queda vacía."""
    if lineas:
        cuerpo = "BT /F1 12 Tf 14 TL 72 770 Td " + " ".join(f"({_escapar(l)}) Tj T*" for l in lineas) + " ET"
    else:
        cuerpo = ""
    contenido = cuerpo.encode("cp1252")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(contenido) + contenido + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    salida = bytearray(b"%PDF-1.4\n")
    posiciones = []
    for n, obj in enumerate(objetos, 1):
        posiciones.append(len(salida))
        salida += b"%d 0 obj\n" % n + obj + b"\nendobj\n"
    xref = len(salida)
    salida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    salida += b"".join(b"%010d 00000 n \n" % p for p in posiciones)
    salida += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    return bytes(salida)
