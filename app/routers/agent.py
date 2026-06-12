import os
import logging
from typing import Any
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.database import get_supabase_admin

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
async def accept_scraped_data(data: ScrapedData, authorization: str = Header(...)):
    verify_token(authorization)
    supabase = get_supabase_admin()
    try:
        result = supabase.table("scraped_data").upsert({
            "match_id": data.match_id,
            "data_type": data.data_type,
            "content": data.content,
            "scraped_date": data.date,
        }, on_conflict="match_id,data_type,scraped_date").execute()
        return {"status": "ok", "rows": len(result.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", status_code=202)
async def trigger_agent(authorization: str = Header(...)):
    verify_token(authorization)
    return {"status": "accepted"}


@router.get("/match/{match_id}")
async def get_scraped_data(match_id: str):
    """取得指定比賽的最新 scraped 資料（前端公開查詢）"""
    supabase = get_supabase_admin()
    try:
        result = supabase.table("scraped_data") \
            .select("data_type, content, scraped_date") \
            .eq("match_id", match_id) \
            .order("scraped_date", desc=True) \
            .limit(10) \
            .execute()

        data = result.data or []

        # 整理成 {odds: {...}, squads: {...}} 格式，只取最新一筆
        output = {}
        for row in data:
            dtype = row["data_type"]
            if dtype not in output:
                output[dtype] = {
                    "content": row["content"],
                    "date": row["scraped_date"]
                }

        return {"match_id": match_id, "data": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))