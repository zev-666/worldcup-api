from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.predictor import predict_match

router = APIRouter(prefix="/predict", tags=["predictions"])

DEFAULT_ELO = 1500

def get_team_elo(team_name: str) -> float:
    """
    從 team_features 表中取得指定球隊最近的 elo_rating。
    若無資料則回傳 DEFAULT_ELO。
    """
    # 依照 feature_date 降冪排序，取第一筆
    res = (
        supabase.table("team_features")
        .select("elo_rating")
        .eq("team_name", team_name)
        .order("feature_date", desc=True)
        .limit(1)
        .execute()
    )
    if res.data and len(res.data) > 0:
        return float(res.data[0]["elo_rating"])
    else:
        # 可選：印出 log 提醒無資料
        print(f"⚠️ 找不到 {team_name} 的 ELO 資料，使用預設值 {DEFAULT_ELO}")
        return DEFAULT_ELO


@router.get("/{match_id}")
def get_prediction(match_id: str):
    # 1. 查詢比賽基本資料
    match_res = supabase.table("matches").select("*").eq("id", match_id).execute()
    if not match_res.data:
        raise HTTPException(status_code=404, detail="Match not found")
    match = match_res.data[0]

    home_team = match["home_team"]
    away_team = match["away_team"]

    # 2. 取得兩隊 ELO
    home_elo = get_team_elo(home_team)
    away_elo = get_team_elo(away_team)

    # 3. 進行預測
    prediction = predict_match(home_elo, away_elo)

    return {
        "match": {
            "home_team": home_team,
            "away_team": away_team,
            "kickoff_utc": match["kickoff_utc"],
        },
        "elo": {
            "home": home_elo,
            "away": away_elo,
        },
        "prediction": prediction,
        "disclaimer": "此為數據分析，非投注建議。"
    }