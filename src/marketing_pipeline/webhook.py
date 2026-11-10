from __future__ import annotations

import hashlib
import hmac
import json
import uuid

from fastapi import FastAPI, Header, HTTPException, Request

from .config import settings
from .database import Database

app = FastAPI(title="Simulated CRM Webhook Receiver", version="0.1.0")


def valid_signature(body: bytes, signature: str | None, secret: str) -> bool:
    if not signature: return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.removeprefix("sha256="))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "simulated_portfolio"}


@app.post("/webhooks/crm", status_code=202)
async def crm_webhook(request: Request, x_webhook_signature: str | None = Header(default=None)) -> dict:
    body = await request.body()
    if not valid_signature(body, x_webhook_signature, settings.webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try: payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc
    if not isinstance(payload, dict) or "event_type" not in payload:
        raise HTTPException(status_code=422, detail="event_type is required")
    db = Database(settings); db.initialize(); event_id = str(uuid.uuid4()); p = db.placeholder
    db.execute(f"INSERT INTO webhook_events(event_id,event_type,payload_json) VALUES({p},{p},{p})",
               (event_id, str(payload["event_type"]), json.dumps(payload)))
    return {"accepted": True, "event_id": event_id, "simulated": True}

