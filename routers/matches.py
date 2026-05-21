from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database import supabase

router = APIRouter(prefix="/matches", tags=["matches"])

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

@router.get("/", response_model=List[MatchResponse])
def get_matches(limit: int = Query(50), skip: int = Query(0)):
    try:
        result = supabase.table("matches") \
            .select("*") \
            .order("kickoff_utc") \
            .range(skip, skip + limit - 1) \
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{match_id}", response_model=MatchResponse)
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