import csv
import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

db_path = os.getenv("DATABASE_PATH", str(ROOT / "data" / "cadastros.db"))
output = ROOT / "output" / "relatorio_cadastros.csv"
output.parent.mkdir(parents=True, exist_ok=True)

db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
rows = db.execute(
    """
    SELECT id, nome, celular, indicador_nome, criado_em
    FROM pessoas ORDER BY id
    """
).fetchall()

with output.open("w", newline="", encoding="utf-8-sig") as stream:
    writer = csv.writer(stream, delimiter=";")
    writer.writerow(["ID", "Nome", "Celular", "Indicado por", "Data"])
    for row in rows:
        writer.writerow([row["id"], row["nome"], row["celular"], row["indicador_nome"], row["criado_em"]])

print(output)
