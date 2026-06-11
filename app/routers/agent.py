"""
app/routers/agent.py
接收來自 Cloudflare Workers / GitHub Actions 的 agent 資料。
"""
import os
import logging
from typing import Any
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)
INTERNAL_TOKEN = os.environ.get("INTERNAL_API_TOKEN", "")


def verify_token(authorization: str):
    if authorization != f"Bearer {INTERNAL_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


class ScrapedData(BaseModel):
    data_type: str
    match_id: str
    content: Any
    date: str


@router.post("/accept", status_code=201)
async def accept_scraped_data(
    data: ScrapedData,
    authorization: str = Header(...)
):
    verify_token(authorization)
    from app.database import get_supabase_admin
    supabase = get_supabase_admin()

    try:
        result = supabase.table("scraped_data").upsert({
            "match_id":     data.match_id,
            "data_type":    data.data_type,
            "content":      data.content,
            "scraped_date": data.date,
        }, on_conflict="match_id,data_type,scraped_date").execute()

        logger.info(f"寫入成功: {data.data_type} match={data.match_id}")
        return {"status": "ok", "rows": len(result.data)}

    except Exception as e:
        logger.error(f"寫入失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", status_code=202)
async def trigger_agent(authorization: str = Header(...)):
    verify_token(authorization)
    return {"status": "accepted"}