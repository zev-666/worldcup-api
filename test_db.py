import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 直接使用参数构造连接
conn = psycopg2.connect(
    host="aws-0-ap-southeast-1.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="postgres",
    password=os.getenv("DB_PASSWORD")  # 你需要将密码单独放在 .env 的 DB_PASSWORD 变量中
)
print("连接成功！")