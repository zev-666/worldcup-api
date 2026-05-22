# 檔案位置: app/routers/payments.py
import os
import stripe
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from app.dependencies import get_current_user
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY  # 🆕 使用統一的 config

# 設定 logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])

# Stripe 設定
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = "https://worldcup-frontend-pi.vercel.app"

@router.post("/create-checkout-session")
async def create_checkout_session(user: dict = Depends(get_current_user)):
    """
    為已登入的使用者建立 Stripe Checkout Session。
    前端呼叫後得到付款頁面網址。
    """
    try:
        # 從使用者 dict 中取出 id（注意：get_current_user 回傳 dict，不是物件）
        user_id = user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="無法取得使用者 ID")

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv("STRIPE_PRO_PRICE_ID"),
                'quantity': 1,
            }],
            mode='payment',
            success_url=FRONTEND_URL + '/account?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=FRONTEND_URL + '/account',
            client_reference_id=user_id,
            metadata={'user_id': user_id}
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"建立 Checkout Session 失敗: {e}")
        raise HTTPException(status_code=500, detail="建立付款 session 時發生錯誤")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    接收 Stripe Webhook 事件，驗證簽名後處理付款完成。
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Webhook 錯誤: 無效的 payload - {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook 錯誤: 無效的簽名 - {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 處理付款成功事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        if user_id:
            logger.info(f"使用者 {user_id} 付款成功，正在升級會員...")
            await upgrade_user_to_pro(user_id)
        else:
            logger.warning("收到付款完成事件，但找不到 user_id")

    return {"status": "success"}

async def upgrade_user_to_pro(user_id: str):
    """
    使用 config 中的 Supabase 連線，將使用者 tier 改為 'pro'。
    """
    try:
        # 使用共用的 Supabase 配置初始化
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        response = supabase.table("users").update({"tier": "pro"}).eq("id", user_id).execute()
        logger.info(f"已成功將使用者 {user_id} 升級為 Pro。")
        return response
    except Exception as e:
        logger.error(f"升級使用者 {user_id} 時發生錯誤: {e}")
        # 此處可加入通知機制（例如發送警報）
        raise e  # 讓 webhook 回傳錯誤，Stripe 會自動重試