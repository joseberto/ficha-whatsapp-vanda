import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WABA_ID = os.getenv("WABA_ID", "")
VERSION = os.getenv("GRAPH_API_VERSION", "v25.0")
BASE = f"https://graph.facebook.com/{VERSION}"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def ensure_settings():
    missing = [name for name, value in {"WHATSAPP_TOKEN": TOKEN, "WABA_ID": WABA_ID}.items() if not value]
    if missing:
        sys.exit("Preencha no .env: " + ", ".join(missing))


def create_flow() -> str:
    response = requests.post(
        f"{BASE}/{WABA_ID}/flows",
        headers=HEADERS,
        json={"name": "ficha_cadastro_vanda", "categories": ["OTHER"]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


def upload_flow(flow_id: str):
    path = ROOT / "flow" / "flow.json"
    with path.open("rb") as stream:
        response = requests.post(
            f"{BASE}/{flow_id}/assets",
            headers=HEADERS,
            data={"name": "flow.json", "asset_type": "FLOW_JSON"},
            files={"file": ("flow.json", stream, "application/json")},
            timeout=60,
        )
    response.raise_for_status()
    result = response.json()
    if not result.get("success"):
        raise RuntimeError(json.dumps(result, ensure_ascii=False, indent=2))


def publish_flow(flow_id: str):
    response = requests.post(f"{BASE}/{flow_id}/publish", headers=HEADERS, timeout=30)
    response.raise_for_status()


if __name__ == "__main__":
    ensure_settings()
    created_id = create_flow()
    upload_flow(created_id)
    publish_flow(created_id)
    print(f"FLOW_ID={created_id}")
