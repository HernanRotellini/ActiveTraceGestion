"""Parser de archivos LMS (Moodle) para calificaciones.

Detecta formato (xlsx/csv), identifica columnas de identificación
de alumnos y columnas de actividades (numéricas/textuales).
"""

import csv
import io
import re
from dataclasses import dataclass, field


class LmsParseError(ValueError):
    """Error al parsear un archivo LMS."""


@dataclass(frozen=True)
class ActivityColumn:
    nombre: str
    header_raw: str
    tipo: str  # "numeric" | "textual"


@dataclass(frozen=True)
class IdentityColumn:
    nombre: str
    header_raw: str
    mapeo: str  # nombre, apellidos, email


@dataclass(frozen=True)
class ParsedRow:
    fila: int
    datos_identidad: dict[str, str]  # {mapeo: valor}
    datos_actividades: dict[str, str | None]  # {nombre_actividad: valor}


@dataclass
class LmsParseResult:
    columnas_identidad: list[IdentityColumn] = field(default_factory=list)
    columnas_actividad: list[ActivityColumn] = field(default_factory=list)
    filas: list[ParsedRow] = field(default_factory=list)
    total_filas: int = 0


# Mapeo de columnas de identidad (case-insensitive)
IDENTITY_ALIASES: dict[str, str] = {
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
    "direccion de email": "email",
    "dirección de email": "email",
    "user_email": "email",
}

COLUMNAS_IDENTIDAD_REQUERIDAS = {"nombre", "apellidos", "email"}


class LMSFileParser:
    """Parser de archivos de calificaciones exportados del LMS."""

    @staticmethod
    def parse(filename: str, contenido: bytes) -> LmsParseResult:
        """Parsea un archivo LMS detectando el formato por extensión.

        Args:
            filename: Nombre del archivo (para detectar extensión).
            contenido: Contenido binario del archivo.

        Returns:
            LmsParseResult con columnas y filas detectadas.

        Raises:
            LmsParseError: Si el formato no es soportado o el archivo es inválido.
        """
        if filename.lower().endswith(".xlsx"):
            return LMSFileParser._parse_xlsx(contenido)
        elif filename.lower().endswith(".csv"):
            return LMSFileParser._parse_csv(contenido)
        else:
            raise LmsParseError(f"Formato no soportado: {filename}. Use .xlsx o .csv")

    @staticmethod
    def _normalizar_columna(raw: str) -> str:
        """Normaliza un nombre de columna: lowercase, sin caracteres especiales."""
        return re.sub(r"[^a-záéíóúñ0-9]", "", raw.strip().lower())

    @staticmethod
    def _detect_column_type(header: str) -> str:
        """Detecta el tipo de columna basado en el header.

        Args:
            header: Nombre raw de la columna.

        Returns:
            "numeric" si el header termina en "(Real)",
            "textual" en caso contrario,
            "identity" si es columna de identificación del alumno.
        """
        cleaned = header.strip().lower()
        if cleaned.endswith("(real)"):
            return "numeric"
        normalizado = LMSFileParser._normalizar_columna(header)
        if normalizado in IDENTITY_ALIASES:
            return "identity"
        return "textual"

    @staticmethod
    def _detectar_delimitador_csv(primera_linea: str) -> str:
        """Detecta el delimitador de un CSV: ; o , o tab."""
        if "\t" in primera_linea:
            return "\t"
        punto_y_coma = primera_linea.count(";")
        coma = primera_linea.count(",")
        if punto_y_coma > coma:
            return ";"
        return ","

    @staticmethod
    def _parse_csv(contenido: bytes) -> LmsParseResult:
        """Parsea contenido CSV."""
        text_content = contenido.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text_content))
        rows = list(reader)
        if not rows:
            raise LmsParseError("El archivo CSV está vacío")

        delimitador = LMSFileParser._detectar_delimitador_csv(
            text_content.split("\n")[0] if "\n" in text_content else ""
        )
        if delimitador != ",":
            reader = csv.reader(io.StringIO(text_content), delimiter=delimitador)
            rows = list(reader)
            if not rows:
                raise LmsParseError("El archivo CSV está vacío")

        return LMSFileParser._procesar_header_filas(rows[0], rows[1:])

    @staticmethod
    def _parse_xlsx(contenido: bytes) -> LmsParseResult:
        """Parsea contenido .xlsx usando openpyxl."""
        try:
            import openpyxl  # noqa: PLC0415
        except ImportError:
            raise LmsParseError("openpyxl no está instalado") from None

        try:
            wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
        except Exception as exc:
            raise LmsParseError(f"No se pudo leer el archivo .xlsx: {exc}") from exc

        ws = wb.active
        if ws is None:
            raise LmsParseError("El archivo .xlsx no tiene hojas de cálculo")

        rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if not rows:
            raise LmsParseError("El archivo .xlsx está vacío")

        raw_headers = [str(cell or "").strip() for cell in rows[0]]
        data_rows = []
        for row in rows[1:]:
            values = [str(cell or "").strip() if cell is not None else "" for cell in row]
            if any(values):
                data_rows.append(values)

        return LMSFileParser._procesar_header_filas(raw_headers, data_rows)

    @staticmethod
    def _procesar_header_filas(
        raw_headers: list[str], data_rows: list[list[str]]
    ) -> LmsParseResult:
        """Procesa headers y filas de datos para construir el resultado.

        Args:
            raw_headers: Lista de nombres de columna raw.
            data_rows: Lista de filas de datos (listas de strings).

        Returns:
            LmsParseResult estructurado.

        Raises:
            LmsParseError: Si no se detectan columnas de identidad requeridas.
        """
        result = LmsParseResult()

        # Clasificar columnas
        identity_indices: list[tuple[int, str]] = []  # (index, mapeo)
        activity_indices: list[tuple[int, str, str]] = []  # (index, nombre, tipo)

        for i, header in enumerate(raw_headers):
            col_type = LMSFileParser._detect_column_type(header)
            if col_type == "identity":
                normalizado = LMSFileParser._normalizar_columna(header)
                mapeo = IDENTITY_ALIASES.get(normalizado, normalizado)
                identity_indices.append((i, mapeo))
                result.columnas_identidad.append(
                    IdentityColumn(nombre=mapeo, header_raw=header, mapeo=mapeo)
                )
            elif col_type in ("numeric", "textual"):
                # Extraer nombre limpio de actividad (sin "(Real)")
                nombre_actividad = re.sub(r"\s*\(Real\)$", "", header, flags=re.IGNORECASE).strip()
                activity_indices.append((i, nombre_actividad, col_type))
                result.columnas_actividad.append(
                    ActivityColumn(nombre=nombre_actividad, header_raw=header, tipo=col_type)
                )

        # Validar columnas de identidad requeridas
        mapeos_encontrados = {m for _, m in identity_indices}
        faltantes = COLUMNAS_IDENTIDAD_REQUERIDAS - mapeos_encontrados
        if faltantes:
            raise LmsParseError(
                f"Columnas de identidad requeridas faltantes: {', '.join(sorted(faltantes))}. "
                f"Columnas detectadas: {', '.join(raw_headers)}"
            )

        # Procesar filas
        for i, row in enumerate(data_rows):
            datos_id: dict[str, str] = {}
            for idx, mapeo in identity_indices:
                if idx < len(row):
                    datos_id[mapeo] = row[idx]
            datos_act: dict[str, str | None] = {}
            for idx, nombre, _ in activity_indices:
                if idx < len(row):
                    val = row[idx]
                    datos_act[nombre] = val if val else None
            result.filas.append(ParsedRow(
                fila=i + 2,
                datos_identidad=datos_id,
                datos_actividades=datos_act,
            ))

        result.total_filas = len(data_rows)
        return result
