import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from predictor import predict_match

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = FastAPI(title="World Cup 2026 API", description="赛程与预测数据", version="0.1.0")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://worldcup-frontend-pi.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchResponse(BaseModel):
    id: str
    external_id: str
    home_team: str
    away_team: str
    kickoff_utc: datetime
    stage: Optional[str] = None
    venue: Optional[str] = None
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

@app.get("/")
def root():
    return {"message": "World Cup 2026 API is running"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}

@app.get("/matches", response_model=List[MatchResponse])
def get_matches(limit: int = 50, skip: int = 0):
    try:
        result = supabase.table("matches") \
            .select("*") \
            .order("kickoff_utc") \
            .range(skip, skip + limit - 1) \
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches/{match_id}")
def get_match(match_id: str):
    try:
        result = supabase.table("matches").select("*").eq("id", match_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Match not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/{match_id}")
async def predict(match_id: str):
    # 從 Supabase 查詢
    result = supabase.table("matches").select("*").eq("id", match_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match = result.data[0]
    
    # 暫時使用預設 ELO
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)