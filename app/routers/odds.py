from fastapi import APIRouter, Query, HTTPException
from app.database import supabase

router = APIRouter(prefix="/odds", tags=["odds"])

@router.get("/")
def get_odds(fixture_id: str = Query(..., description="比賽的 fixture_id")):
    res = supabase.table("odds_snapshots").select("*").eq("match_id", fixture_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="找不到此比賽的賠率資料")
    return res.data