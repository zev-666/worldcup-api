from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.predictor import predict_match

router = APIRouter(prefix="/predict", tags=["predictions"])

DEFAULT_ELO = 1500

def get_team_elo(team_name: str) -> float:
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
        print(f"⚠️ 找不到 {team_name} 的 ELO 資料，使用預設值 {DEFAULT_ELO}")
        return DEFAULT_ELO

@router.get("/{match_id}")
def get_prediction(match_id: str):
    match_res = supabase.table("matches").select("*").eq("id", match_id).execute()
    if not match_res.data:
        raise HTTPException(status_code=404, detail="Match not found")
    match = match_res.data[0]

    home_team = match["home_team"]
    away_team = match["away_team"]

    home_elo = get_team_elo(home_team)
    away_elo = get_team_elo(away_team)

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