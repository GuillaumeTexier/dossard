from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date, datetime

from pydantic import ValidationError

from app.categories import age_category
from app.errors import ApiError, ConflictError
from app.repositories.common import fetch_or_404
from app.schemas import AthleteCreate, AthleteOut, ImportLineError, ImportReport

IMPORT_COLUMNS = (
    "nom",
    "prenom",
    "date_naissance",
    "sexe",
    "club",
    "licence",
    "certificat_valide_jusqu",
)


def _to_athlete(row: sqlite3.Row) -> AthleteOut:
    birth_date = date.fromisoformat(row["birth_date"])
    certificate = row["medical_certificate_valid_until"]
    return AthleteOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_date=birth_date,
        sex=row["sex"],
        club=row["club"],
        license_number=row["license_number"],
        medical_certificate_valid_until=date.fromisoformat(certificate) if certificate else None,
        category=age_category(birth_date),
    )


def list_athletes(conn: sqlite3.Connection, club: str | None = None) -> list[AthleteOut]:
    sql = "SELECT * FROM athletes"
    params: tuple[str, ...] = ()
    if club is not None:
        sql += " WHERE club = ?"
        params = (club,)
    sql += " ORDER BY last_name, first_name, id"
    return [_to_athlete(row) for row in conn.execute(sql, params)]


def get_athlete(conn: sqlite3.Connection, athlete_id: int) -> AthleteOut:
    row = fetch_or_404(
        conn,
        "SELECT * FROM athletes WHERE id = ?",
        (athlete_id,),
        f"Athlète {athlete_id} introuvable",
    )
    return _to_athlete(row)


def create_athlete(conn: sqlite3.Connection, data: AthleteCreate) -> AthleteOut:
    existing = conn.execute(
        "SELECT id FROM athletes WHERE license_number = ?", (data.license_number,)
    ).fetchone()
    if existing is not None:
        raise ConflictError(f"Licence {data.license_number} déjà enregistrée")

    certificate = data.medical_certificate_valid_until
    cursor = conn.execute(
        "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
        " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.first_name,
            data.last_name,
            data.birth_date.isoformat(),
            data.sex.value,
            data.club,
            data.license_number,
            certificate.isoformat() if certificate else None,
        ),
    )
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_athlete(row)


def _parse_import_date(value: str, column: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"{column} invalide : « {value} » (format jj/mm/aaaa attendu)") from None


def _row_to_athlete(row: dict[str, str | None]) -> AthleteCreate:
    """Convertit une ligne du CSV en AthleteCreate ; lève ValueError (message lisible)."""
    values = {column: (row[column] or "").strip() for column in IMPORT_COLUMNS}
    try:
        return AthleteCreate(
            last_name=values["nom"],
            first_name=values["prenom"],
            birth_date=_parse_import_date(values["date_naissance"], "date_naissance"),
            sex=values["sexe"],
            club=values["club"] or None,
            license_number=values["licence"],
            medical_certificate_valid_until=_parse_import_date(
                values["certificat_valide_jusqu"], "certificat_valide_jusqu"
            ),
        )
    except ValidationError as exc:
        raise ValueError(
            "; ".join(f"{'.'.join(map(str, e['loc']))} : {e['msg']}" for e in exc.errors())
        ) from None


def import_athletes(conn: sqlite3.Connection, content: bytes) -> ImportReport:
    """Importe un CSV de licenciés (séparateur « ; », dates jj/mm/aaaa).

    Une licence déjà enregistrée est ignorée ; une ligne invalide est signalée sans bloquer
    les autres. Les numéros de ligne sont ceux du fichier (l'en-tête est la ligne 1).
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ApiError("Le fichier doit être encodé en UTF-8", code="invalid_encoding") from None

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    missing = [column for column in IMPORT_COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        raise ApiError(f"Colonnes manquantes : {', '.join(missing)}", code="invalid_csv")

    created = skipped = 0
    errors: list[ImportLineError] = []
    for row in reader:
        try:
            data = _row_to_athlete(row)
            create_athlete(conn, data)
        except ConflictError:
            skipped += 1
        except ValueError as exc:
            errors.append(ImportLineError(line=reader.line_num, message=str(exc)))
        else:
            created += 1
    return ImportReport(created=created, skipped=skipped, errors=errors)
