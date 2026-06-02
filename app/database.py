import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

# 一般用途 client（使用 service key，可繞過 RLS）
supabase: Client = create_client(url, key)


def get_supabase_admin() -> Client:
    """
    回傳使用 service_role key 的 Supabase client。
    專門給 Webhook 使用，可直接更新 users.tier。
    """
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY"),
    )
