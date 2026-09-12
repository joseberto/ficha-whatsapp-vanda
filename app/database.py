import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


DB_PATH = os.getenv("DATABASE_PATH", "data/cadastros.db")
CENTRAL_NAME = os.getenv("CENTRAL_NAME", "Vanda Silva")
CENTRAL_CODE = os.getenv("CENTRAL_REF_CODE", "VANDA").upper()


@contextmanager
def connect():
    directory = os.path.dirname(DB_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize():
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                titulo TEXT NOT NULL,
                zona TEXT NOT NULL,
                secao TEXT NOT NULL,
                endereco TEXT NOT NULL,
                nascimento TEXT NOT NULL,
                cpf TEXT NOT NULL,
                celular TEXT NOT NULL,
                whatsapp_sender TEXT NOT NULL,
                codigo_proprio TEXT NOT NULL UNIQUE,
                codigo_indicador TEXT NOT NULL,
                indicador_nome TEXT NOT NULL,
                consentimento INTEGER NOT NULL,
                criado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessoes_indicacao (
                whatsapp_sender TEXT PRIMARY KEY,
                codigo_indicador TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );
            """
        )


def normalize_code(value: str | None) -> str:
    value = (value or CENTRAL_CODE).upper().strip()
    return "".join(ch for ch in value if ch.isalnum() or ch in "-_")[:32] or CENTRAL_CODE


def remember_referrer(sender: str, code: str):
    code = normalize_code(code)
    now = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute(
            """
            INSERT INTO sessoes_indicacao (whatsapp_sender, codigo_indicador, atualizado_em)
            VALUES (?, ?, ?)
            ON CONFLICT(whatsapp_sender) DO UPDATE SET
              codigo_indicador = excluded.codigo_indicador,
              atualizado_em = excluded.atualizado_em
            """,
            (sender, code, now),
        )


def session_referrer(sender: str) -> str:
    with connect() as db:
        row = db.execute(
            "SELECT codigo_indicador FROM sessoes_indicacao WHERE whatsapp_sender = ?",
            (sender,),
        ).fetchone()
    return normalize_code(row[0] if row else CENTRAL_CODE)


def referrer_details(code: str) -> dict:
    code = normalize_code(code)
    if code == CENTRAL_CODE:
        return {"name": CENTRAL_NAME}
    with connect() as db:
        row = db.execute(
            "SELECT nome FROM pessoas WHERE codigo_proprio = ?",
            (code,),
        ).fetchone()
    if not row:
        return {"name": CENTRAL_NAME}
    return {"name": row["nome"]}


def new_referral_code() -> str:
    return "REF-" + secrets.token_hex(4).upper()


def create_person(data: dict, sender: str, referrer_code: str) -> dict:
    referrer_code = normalize_code(referrer_code)
    referrer = referrer_details(referrer_code)
    code = new_referral_code()
    now = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO pessoas (
              nome, titulo, zona, secao, endereco, nascimento, cpf, celular,
              whatsapp_sender, codigo_proprio, codigo_indicador, indicador_nome,
              consentimento, criado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["nome"], data["titulo"], data["zona"], data["secao"],
                data["endereco"], data["nascimento"], data["cpf"], data["celular"],
                sender, code, referrer_code, referrer["name"], 1, now,
            ),
        )
        person_id = cursor.lastrowid
    return {
        "id": person_id,
        **data,
        "whatsapp_sender": sender,
        "codigo_proprio": code,
        "codigo_indicador": referrer_code,
        "indicador_nome": referrer["name"],
        "criado_em": now,
    }
