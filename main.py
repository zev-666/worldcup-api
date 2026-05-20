import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 新增
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
            raise HTTPException(status_code=404, detail="比赛未找到")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)