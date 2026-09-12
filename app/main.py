import hashlib
import hmac
import json
import os
import re
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response

from .database import (
    CENTRAL_CODE,
    create_person,
    initialize,
    normalize_code,
    referrer_details,
    remember_referrer,
    session_referrer,
)
from .pdf_generator import generate_pdf


load_dotenv()
app = FastAPI(title="Ficha de Cadastro WhatsApp")

GRAPH_VERSION = os.getenv("GRAPH_API_VERSION", "v25.0")
TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("PHONE_NUMBER_ID", "")
FLOW_ID = os.getenv("FLOW_ID", "")
APP_SECRET = os.getenv("META_APP_SECRET", "")
VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "")
CENTRAL_PHONE = os.getenv("CENTRAL_PHONE", "5585920013309")


@app.on_event("startup")
def startup():
    initialize()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and hmac.compare_digest(
        params.get("hub.verify_token", ""), VERIFY_TOKEN
    ):
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Token de verificação inválido")


def valid_signature(raw: bytes, signature: str | None) -> bool:
    if not APP_SECRET or not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(APP_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


def graph_post(path: str, payload: dict | None = None, files=None):
    if not TOKEN:
        raise RuntimeError("WHATSAPP_TOKEN não configurado")
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path.lstrip('/')}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(url, headers=headers, json=payload if files is None else None, data=None, files=files, timeout=30)
    response.raise_for_status()
    return response.json()


def send_text(to: str, text: str):
    return graph_post(
        f"{PHONE_ID}/messages",
        {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}},
    )


def send_flow(to: str, ref_code: str):
    ref = referrer_details(ref_code)
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {"type": "text", "text": "FICHA DE CADASTRO"},
            "body": {"text": f"Preencha seus dados. Indicado por: {ref['name']}."},
            "footer": {"text": "Seus dados serão tratados de forma protegida."},
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": ref_code,
                    "flow_id": FLOW_ID,
                    "flow_cta": "PREENCHER FICHA",
                    "flow_action": "navigate",
                    "flow_action_payload": {
                        "screen": "CADASTRO",
                        "data": {"indicado_por": ref["name"], "referral_code": ref_code},
                    },
                },
            },
        },
    }
    return graph_post(f"{PHONE_ID}/messages", payload)


def upload_pdf(path: str) -> str:
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_ID}/media"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    with open(path, "rb") as stream:
        response = requests.post(
            url,
            headers=headers,
            data={"messaging_product": "whatsapp", "type": "application/pdf"},
            files={"file": (os.path.basename(path), stream, "application/pdf")},
            timeout=60,
        )
    response.raise_for_status()
    return response.json()["id"]


def send_pdf(to: str, path: str):
    media_id = upload_pdf(path)
    return graph_post(
        f"{PHONE_ID}/messages",
        {
            "messaging_product": "whatsapp", "to": to, "type": "document",
            "document": {"id": media_id, "filename": os.path.basename(path), "caption": "Sua ficha de cadastro"},
        },
    )


def digits(value) -> str:
    return re.sub(r"\D", "", str(value or ""))


def validate_submission(data: dict) -> dict:
    required = ["nome", "titulo", "zona", "secao", "endereco", "nascimento", "cpf", "celular"]
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        raise ValueError("Campos obrigatórios ausentes: " + ", ".join(missing))
    cpf = digits(data["cpf"])
    if len(cpf) != 11:
        raise ValueError("CPF deve conter 11 números")
    celular = digits(data["celular"])
    if len(celular) not in (10, 11, 12, 13):
        raise ValueError("Celular inválido")
    if data.get("consentimento") not in (True, "true", "True", "on", 1, "1"):
        raise ValueError("É necessário autorizar o uso dos dados")
    clean = {field: str(data[field]).strip() for field in required}
    clean["cpf"] = cpf
    clean["celular"] = celular
    return clean


def share_link(code: str) -> str:
    message = f"CADASTRO {code}"
    return f"https://wa.me/{CENTRAL_PHONE}?text={quote(message)}"


def handle_text(sender: str, body: str):
    match = re.search(r"(?:CADASTRO|REF)\s+(REF-[A-F0-9]{8}|[A-Z0-9_-]{3,32})", body.upper())
    code = normalize_code(match.group(1) if match else CENTRAL_CODE)
    remember_referrer(sender, code)
    send_flow(sender, code)


def handle_flow(sender: str, interactive: dict):
    response_json = interactive.get("nfm_reply", {}).get("response_json", "{}")
    data = json.loads(response_json)
    try:
        clean = validate_submission(data)
    except ValueError as exc:
        send_text(sender, f"Não foi possível concluir: {exc}. Digite CADASTRO para tentar novamente.")
        return
    ref_code = normalize_code(data.get("referral_code") or session_referrer(sender))
    person = create_person(clean, sender, ref_code)
    pdf_path = generate_pdf(person)
    link = share_link(person["codigo_proprio"])
    send_text(
        sender,
        "Cadastro realizado com sucesso!\n\n"
        f"Indicado por: {person['indicador_nome']}\n"
        f"Seu link para indicar outras pessoas:\n{link}\n\n"
        "Encaminhe este link. Cada novo cadastro ficará ligado ao seu nome.",
    )
    send_pdf(sender, pdf_path)


@app.post("/webhook")
async def receive_webhook(request: Request):
    raw = await request.body()
    if not valid_signature(raw, request.headers.get("x-hub-signature-256")):
        raise HTTPException(status_code=401, detail="Assinatura inválida")
    payload = json.loads(raw)
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                sender = message.get("from", "")
                if message.get("type") == "text":
                    handle_text(sender, message.get("text", {}).get("body", ""))
                elif message.get("type") == "interactive" and message.get("interactive", {}).get("type") == "nfm_reply":
                    handle_flow(sender, message["interactive"])
    return {"status": "received"}
