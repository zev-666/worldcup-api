import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_KEY")

supabase: Client = create_client(url, key)