"""Parser de archivos de padrón: soporte para .xlsx y .csv."""

import csv
import io
import re
from dataclasses import dataclass


class FileParseError(ValueError):
    """Error al parsear el archivo de padrón."""


@dataclass(frozen=True)
class ColumnaDetectada:
    nombre: str
    mapeo: str  # nombre, apellidos, email, comision, regional


@dataclass(frozen=True)
class FilaParseada:
    fila: int
    datos: dict[str, str]  # {mapeo: valor}


@dataclass(frozen=True)
class ResultadoParseo:
    columnas: list[ColumnaDetectada]
    filas: list[FilaParseada]
    total_filas: int


COLUMNAS_REQUERIDAS = {"nombre", "apellidos", "email"}
COLUMNAS_OPCIONALES = {"comision", "regional"}
COLUMNAS_VALIDAS = COLUMNAS_REQUERIDAS | COLUMNAS_OPCIONALES

# Mapeo de nombres de columna posibles (case-insensitive) a mapeo canónico
COLUMN_ALIASES: dict[str, str] = {
    "nombre": "nombre",
    "nombres": "nombre",
    "name": "nombre",
    "firstname": "nombre",
    "apellido": "apellidos",
    "apellidos": "apellidos",
    "surname": "apellidos",
    "lastname": "apellidos",
    "apellido y nombre": "apellidos",
    "email": "email",
    "e-mail": "email",
    "mail": "email",
    "correo": "email",
    "comision": "comision",
    "commission": "comision",
    "grupo": "comision",
    "group": "comision",
    "regional": "regional",
    "sede": "regional",
    "delegacion": "regional",
}


def _normalizar_nombre_columna(raw: str) -> str:
    """Normaliza un nombre de columna y devuelve su mapeo canónico."""
    cleaned = re.sub(r"[^a-záéíóúñ0-9]", "", raw.strip().lower())
    return COLUMN_ALIASES.get(cleaned, cleaned)


def _detectar_delimitador_csv(primera_linea: str) -> str:
    """Detecta el delimitador de un CSV: ; o , o tab."""
    if "\t" in primera_linea:
        return "\t"
    punto_y_coma = primera_linea.count(";")
    coma = primera_linea.count(",")
    if punto_y_coma > coma:
        return ";"
    return ","


def parsear_csv(contenido: bytes) -> ResultadoParseo:
    """Parsea contenido CSV y devuelve resultado estructurado."""
    text_content = contenido.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text_content))
    rows = list(reader)
    if not rows:
        raise FileParseError("El archivo CSV está vacío")

    raw_headers = rows[0]
    delimitador = _detectar_delimitador_csv(text_content.split("\n")[0] if "\n" in text_content else "")

    if delimitador != ",":
        reader = csv.reader(io.StringIO(text_content), delimiter=delimitador)
        rows = list(reader)
        if not rows:
            raise FileParseError("El archivo CSV está vacío")
        raw_headers = rows[0]

    headers = [_normalizar_nombre_columna(h) for h in raw_headers]
    _validar_columnas(headers, raw_headers)

    columnas = []
    for i, h in enumerate(headers):
        if h in COLUMNAS_VALIDAS:
            columnas.append(ColumnaDetectada(nombre=raw_headers[i], mapeo=h))

    filas = []
    for i, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue  # saltar filas vacías
        datos = {}
        for j, h in enumerate(headers):
            if h in COLUMNAS_VALIDAS and j < len(row):
                datos[h] = row[j].strip()
        filas.append(FilaParseada(fila=i, datos=datos))

    preview = filas[:5]
    return ResultadoParseo(columnas=columnas, filas=preview, total_filas=len(filas))


def parsear_xlsx(contenido: bytes) -> ResultadoParseo:
    """Parsea contenido .xlsx usando openpyxl."""
    try:
        import openpyxl  # noqa: PLC0415
    except ImportError:
        raise FileParseError("openpyxl no está instalado. Instale con: pip install openpyxl") from None

    try:
        wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    except Exception as exc:
        raise FileParseError(f"No se pudo leer el archivo .xlsx: {exc}") from exc

    ws = wb.active
    if ws is None:
        raise FileParseError("El archivo .xlsx no tiene hojas de cálculo")

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise FileParseError("El archivo .xlsx está vacío")

    raw_headers = [str(cell or "") for cell in rows[0]]
    headers = [_normalizar_nombre_columna(h) for h in raw_headers]
    _validar_columnas(headers, raw_headers)

    columnas = []
    for i, h in enumerate(headers):
        if h in COLUMNAS_VALIDAS:
            columnas.append(ColumnaDetectada(nombre=raw_headers[i], mapeo=h))

    filas = []
    for i, row in enumerate(rows[1:], start=2):
        values = [str(cell or "").strip() for cell in row]
        if not any(values):
            continue
        datos = {}
        for j, h in enumerate(headers):
            if h in COLUMNAS_VALIDAS and j < len(values):
                datos[h] = values[j]
        filas.append(FilaParseada(fila=i, datos=datos))

    wb.close()
    preview = filas[:5]
    return ResultadoParseo(columnas=columnas, filas=preview, total_filas=len(filas))


def _validar_columnas(headers: list[str], raw_headers: list[str]) -> None:
    """Valida que las columnas requeridas estén presentes."""
    encontradas = set()
    for h in headers:
        if h in COLUMNAS_REQUERIDAS:
            encontradas.add(h)
    faltantes = COLUMNAS_REQUERIDAS - encontradas
    if faltantes:
        raise FileParseError(
            f"Columnas requeridas faltantes: {', '.join(sorted(faltantes))}. "
            f"Columnas detectadas: {', '.join(raw_headers)}"
        )


def parsear_archivo(nombre: str, contenido: bytes) -> ResultadoParseo:
    """Parsea un archivo de padrón detectando el formato por extensión.

    Args:
        nombre: Nombre del archivo (para detectar extensión).
        contenido: Contenido binario del archivo.

    Returns:
        ResultadoParseo con columnas detectadas y filas.

    Raises:
        FileParseError: Si el formato no es soportado o el archivo es inválido.
    """
    if nombre.lower().endswith(".xlsx"):
        return parsear_xlsx(contenido)
    elif nombre.lower().endswith(".csv"):
        return parsear_csv(contenido)
    else:
        raise FileParseError(f"Formato no soportado: {nombre}. Use .xlsx o .csv")
