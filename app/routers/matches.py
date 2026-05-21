from fastapi import APIRouter, HTTPException
from app.database import supabase

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/")
def get_matches():
    try:
        res = supabase.table("matches").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{match_id}")
def get_match(match_id: str):
    try:
        res = supabase.table("matches").select("*").eq("id", match_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Match not found")
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))