import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")   # 必須是 SERVICE_KEY
supabase: Client = create_client(url, key)
from supabase import create_client, Client
from app.config import settings
 
 
def get_supabase_admin() -> Client:
    """
    回傳使用 service_role key 的 Supabase client。
    只用於後端 Webhook，不可暴露給前端。
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
    )