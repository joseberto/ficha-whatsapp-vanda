import os
from pathlib import Path


TEST_DB = Path(__file__).parent / "test.db"
os.environ["DATABASE_PATH"] = str(TEST_DB)
os.environ["PDF_DIRECTORY"] = str(Path(__file__).parent / "pdfs")

from app import database  # noqa: E402
from app.main import share_link, validate_submission  # noqa: E402


def test_validation_and_link():
    data = {
        "nome": "João da Silva",
        "titulo": "123456789012",
        "zona": "1",
        "secao": "2",
        "endereco": "Rua A, 10",
        "nascimento": "1980-01-01",
        "cpf": "123.456.789-09",
        "celular": "85999999999",
        "consentimento": True,
    }
    clean = validate_submission(data)
    assert clean["cpf"] == "12345678909"
    assert "5585920013309" in share_link("REF-ABCDEF12")


def test_direct_referrer():
    if TEST_DB.exists():
        TEST_DB.unlink()
    database.initialize()
    first = database.create_person(
        {"nome": "João", "titulo": "1", "zona": "1", "secao": "1", "endereco": "A", "nascimento": "1980-01-01", "cpf": "1", "celular": "1"},
        "558500000001", "VANDA",
    )
    second = database.create_person(
        {"nome": "Maria", "titulo": "2", "zona": "2", "secao": "2", "endereco": "B", "nascimento": "1990-01-01", "cpf": "2", "celular": "2"},
        "558500000002", first["codigo_proprio"],
    )
    assert second["indicador_nome"] == "João"
