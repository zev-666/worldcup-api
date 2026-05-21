from fastapi import APIRouter, HTTPException
from database import supabase
from predictor import predict_match

router = APIRouter(prefix="/predict", tags=["predictions"])

@router.get("/{match_id}")
async def predict(match_id: str):
    result = supabase.table("matches").select("*").eq("id", match_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match = result.data[0]
    
    home_elo = 1500
    away_elo = 1500
    
    pred = predict_match(home_elo, away_elo)
    
    return {
        "match_id": match_id,
        "home_team": match.get("home_team"),
        "away_team": match.get("away_team"),
        "home_prob": pred["home_prob"],
        "draw_prob": pred["draw_prob"],
        "away_prob": pred["away_prob"],
        "confidence": pred["confidence"],
        "disclaimer": "此為數據分析，非投注建議。"
    }