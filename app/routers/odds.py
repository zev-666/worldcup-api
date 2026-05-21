from fastapi import APIRouter, Depends, Query
from app.database import supabase
from app.dependencies import require_pro

router = APIRouter()

@router.get("/")
async def get_odds(fixture_id: int = Query(None)):
    # 你原本的賠率查詢邏輯（保持不變）
    if fixture_id:
        data = supabase.table("odds_snapshots").select("*").eq("fixture_id", fixture_id).execute()
        return data.data
    data = supabase.table("odds_snapshots").select("*").limit(50).execute()
    return data.data


@router.get("/detailed/{match_id}", summary="Pro 詳細賠率")
async def get_detailed_odds(
    match_id: int,
    current_user: dict = Depends(require_pro)
):
    """
    僅限 Pro 會員：回傳該比賽的詳細賠率市場（讓球、大小球、BTTS）
    此處為模擬資料，實際可從 odds_snapshots 或其他表查詢
    """
    detailed = {
        "match_id": match_id,
        "asian_handicap": {
            "home": -0.5,
            "away": 0.5,
            "home_odds": 1.98,
            "away_odds": 1.88
        },
        "over_under": {
            "line": 2.5,
            "over_odds": 1.90,
            "under_odds": 1.90
        },
        "btts": {
            "yes_odds": 1.75,
            "no_odds": 2.05
        },
        "message": "This data is only available for Pro members."
    }
    return detailed