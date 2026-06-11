"""
Webhook 端點：LemonSqueezy（保留）+ Gumroad（新增）
檔案位置：app/routers/payments.py
"""

import hashlib
import hmac
import json
import logging
import os

from fastapi import APIRouter, Header, HTTPException, Request
from app.database import get_supabase_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None, alias="X-Signature"),
):
    """
    LemonSqueezy Webhook（已停用，保留備用）
    """
    raw_body = await request.body()

    secret = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")
    if not x_signature or not secret:
        logger.warning("LemonSqueezy webhook: missing signature or secret")
        raise HTTPException(status_code=400, detail="Missing signature")

    expected_sig = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, x_signature):
        logger.warning("LemonSqueezy webhook: invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_name = payload.get("meta", {}).get("event_name", "")
    logger.info(f"LemonSqueezy event received: {event_name}")

    if event_name != "order_created":
        return {"status": "ignored", "event": event_name}

    try:
        customer_email = payload["data"]["attributes"]["user_email"]
    except (KeyError, TypeError):
        logger.error("LemonSqueezy webhook: cannot find email in payload")
        return {"status": "error", "detail": "email not found"}

    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("users")
            .update({"tier": "pro"})
            .eq("email", customer_email)
            .execute()
        )
        if result.data:
            logger.info(f"[LS] Upgraded to pro: {customer_email}")
            return {"status": "ok", "email": customer_email}
        else:
            logger.warning(f"[LS] User not found: {customer_email}")
            return {"status": "user_not_found"}
    except Exception as e:
        logger.error(f"[LS] DB error: {e}")
        return {"status": "db_error"}


@router.post("/gumroad")
async def gumroad_webhook(request: Request):
    """
    Gumroad Webhook（現用金流）
    設定位置：Gumroad Dashboard → Settings → Advanced → Ping
    Ping URL：https://worldcup-api-jryd.onrender.com/webhook/gumroad
    注意：Gumroad 不提供驗簽，直接讀取 email 即可
    """
    try:
        body = await request.json()
    except Exception:
        logger.error("Gumroad webhook: invalid JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    email = body.get("email")
    logger.info(f"Gumroad webhook received, email: {email}")

    if not email:
        logger.warning("Gumroad webhook: no email in payload")
        return {"status": "no_email"}

    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("users")
            .update({"tier": "pro"})
            .eq("email", email)
            .execute()
        )
        if result.data:
            logger.info(f"[Gumroad] Upgraded to pro: {email}")
            return {"status": "ok", "email": email}
        else:
            logger.warning(f"[Gumroad] User not found: {email}")
            return {"status": "user_not_found"}
    except Exception as e:
        logger.error(f"[Gumroad] DB error: {e}")
        return {"status": "db_error"}