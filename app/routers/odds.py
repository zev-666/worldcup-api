from fastapi import APIRouter, Depends, Query, HTTPException
from app.database import supabase
from app.dependencies import require_pro

router = APIRouter()


@router.get("/")
async def get_odds(fixture_id: int = Query(None)):
    """
    取得賠率快照。
    可用 fixture_id 篩選特定比賽。
    免費用戶可存取（1X2 基本賠率）。
    """
    if fixture_id:
        data = (
            supabase.table("odds_snapshots")
            .select("*")
            .eq("fixture_id", fixture_id)
            .execute()
        )
        return data.data

    data = (
        supabase.table("odds_snapshots")
        .select("*")
        .limit(50)
        .execute()
    )
    return data.data


@router.get("/detailed/{match_id}", summary="Pro 詳細賠率")
async def get_detailed_odds(
    match_id: str,
    current_user: dict = Depends(require_pro),
):
    """
    Pro 專屬：取得讓球、大小球、BTTS 詳細賠率。
    先從 Supabase odds_snapshots 查詢，
    找不到時回傳預設示意數據。
    """
    # 嘗試從資料庫取得真實賠率
    try:
        data = (
            supabase.table("odds_snapshots")
            .select("*")
            .eq("match_id", match_id)
            .order("snapshot_at", desc=True)
            .limit(1)
            .execute()
        )

        if data.data and len(data.data) > 0:
            odds_data = data.data[0].get("odds_data", {})
            return {
                "match_id": match_id,
                "source": "supabase",
                "asian_handicap": odds_data.get("asian_handicap", {
                    "home": -0.5,
                    "away": 0.5,
                    "home_odds": 1.98,
                    "away_odds": 1.88,
                }),
                "over_under": odds_data.get("over_under", {
                    "line": 2.5,
                    "over_odds": 1.90,
                    "under_odds": 1.90,
                }),
                "btts": odds_data.get("btts", {
                    "yes_odds": 1.75,
                    "no_odds": 2.05,
                }),
                "message": "Pro member detailed odds.",
            }
    except Exception as e:
        print(f"⚠️ 查詢詳細賠率失敗: {e}")

    # 找不到時回傳預設示意數據
    return {
        "match_id": match_id,
        "source": "default",
        "asian_handicap": {
            "home": -0.5,
            "away": 0.5,
            "home_odds": 1.98,
            "away_odds": 1.88,
        },
        "over_under": {
            "line": 2.5,
            "over_odds": 1.90,
            "under_odds": 1.90,
        },
        "btts": {
            "yes_odds": 1.75,
            "no_odds": 2.05,
        },
        "message": "Pro member detailed odds (default data).",
    }
