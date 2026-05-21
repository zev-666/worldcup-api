import pandas as pd
from app.database import supabase

df = pd.read_csv("kaggle_data/former_names.csv")
# 只保留必要欄位非空的列
df = df.dropna(subset=['current', 'former'])

batch = []
for _, row in df.iterrows():
    batch.append({
        "team": row["current"],
        "former_name": row["former"],
        "start_date": row.get("start_date") if pd.notna(row.get("start_date")) else None,
        "end_date": row.get("end_date") if pd.notna(row.get("end_date")) else None
    })
    if len(batch) >= 500:
        supabase.table("former_names").insert(batch).execute()
        batch = []

if batch:
    supabase.table("former_names").insert(batch).execute()

print("✅ Former names imported successfully!")