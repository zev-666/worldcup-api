from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        user = supabase.auth.get_user(token)
    except Exception as e:
        # 暫時印出詳細錯誤，方便排查
        print("=== SUPABASE AUTH ERROR ===")
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # 查詢 public.users 取得 tier
    db_user = supabase.table("users").select("*").eq("id", user.user.id).execute()
    if not db_user.data:
        raise HTTPException(status_code=404, detail="User not found in database")
    
    return {
        "id": user.user.id,
        "email": user.user.email,
        "tier": db_user.data[0].get("tier", "free")
    }


async def require_pro(current_user: dict = Depends(get_current_user)):
    if current_user.get("tier") != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required. Upgrade your account to access this feature."
        )
    return current_user