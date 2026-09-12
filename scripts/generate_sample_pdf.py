import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.pdf_generator import generate_pdf  # noqa: E402


sample = {
    "id": "MODELO",
    "nome": "Nome da pessoa cadastrada",
    "titulo": "0000 0000 0000",
    "zona": "000",
    "secao": "0000",
    "endereco": "Rua, número, complemento, bairro, cidade - UF",
    "nascimento": "00/00/0000",
    "cpf": "000.000.000-00",
    "celular": "(85) 90000-0000",
    "indicador_nome": "Vanda Silva",
    "codigo_proprio": "MODELO",
}

path = ROOT / "output" / "pdf" / "ficha_cadastro_modelo.pdf"
generate_pdf(sample, str(path))
print(path)
