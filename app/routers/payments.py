"""
LemonSqueezy Webhook 端點
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
    接收 LemonSqueezy 付款成功事件，自動升級用戶為 Pro。
    驗證方式：HMAC-SHA256 簽名驗證
    """
    raw_body = await request.body()

    # 驗證簽名
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

    # 解析事件
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_name = payload.get("meta", {}).get("event_name", "")
    logger.info(f"LemonSqueezy event received: {event_name}")

    # 只處理 order_created
    if event_name != "order_created":
        return {"status": "ignored", "event": event_name}

    # 取出購買者 email
    try:
        customer_email = payload["data"]["attributes"]["user_email"]
    except (KeyError, TypeError):
        logger.error("LemonSqueezy webhook: cannot find email in payload")
        return {"status": "error", "detail": "email not found"}

    # 更新 Supabase users 表 tier 為 pro
    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("users")
            .update({"tier": "pro"})
            .eq("email", customer_email)
            .execute()
        )
        if result.data:
            logger.info(f"Upgraded to pro: {customer_email}")
            return {"status": "ok", "email": customer_email}
        else:
            logger.warning(f"User not found: {customer_email}")
            return {"status": "user_not_found"}
    except Exception as e:
        logger.error(f"DB error: {e}")
        return {"status": "db_error"}
