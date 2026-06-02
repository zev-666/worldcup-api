"""
LemonSqueezy Webhook 端點
檔案位置：app/routers/payments.py

在 app/main.py 加入：
    from app.routers import payments
    app.include_router(payments.router, prefix="/webhook", tags=["webhook"])
"""

import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from app.config import settings
from app.database import get_supabase_admin

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None, alias="X-Signature"),
):
    """
    接收 LemonSqueezy 付款成功事件，自動升級用戶為 Pro。

    LemonSqueezy 會在以下情況發送 Webhook：
    - order_created：訂單建立（付款成功）
    - 其他事件：直接回傳 200 忽略

    驗證方式：HMAC-SHA256 簽名驗證
    """
    # 1. 讀取原始 body
    raw_body = await request.body()

    # 2. 驗證簽名（防止偽造請求）
    if not x_signature:
        logger.warning("LemonSqueezy webhook: missing X-Signature header")
        raise HTTPException(status_code=400, detail="Missing signature")

    expected_sig = hmac.new(
        settings.lemonsqueezy_webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, x_signature):
        logger.warning("LemonSqueezy webhook: invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 3. 解析事件
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_name = payload.get("meta", {}).get("event_name", "")
    logger.info(f"LemonSqueezy webhook received: {event_name}")

    # 4. 只處理 order_created 事件
    if event_name != "order_created":
        return {"status": "ignored", "event": event_name}

    # 5. 取出購買者 email
    try:
        customer_email = (
            payload["data"]["attributes"]["user_email"]
        )
    except (KeyError, TypeError):
        logger.error(f"LemonSqueezy webhook: cannot find email in payload")
        # 回傳 200 避免 LemonSqueezy 不斷重試
        return {"status": "error", "detail": "email not found in payload"}

    # 6. 更新 Supabase users 表的 tier 為 pro
    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("users")
            .update({"tier": "pro"})
            .eq("email", customer_email)
            .execute()
        )

        if result.data:
            logger.info(f"Upgraded user to pro: {customer_email}")
            return {"status": "ok", "email": customer_email, "tier": "pro"}
        else:
            logger.warning(f"User not found in DB: {customer_email}")
            return {"status": "user_not_found", "email": customer_email}

    except Exception as e:
        logger.error(f"LemonSqueezy webhook DB error: {e}")
        # 回傳 200 避免重試，錯誤記在 log
        return {"status": "db_error"}
