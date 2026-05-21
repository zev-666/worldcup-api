import pandas as pd
from app.database import supabase
import os

DATA_DIR = "kaggle_data"

def import_results():
    print("📥 Importing results...")
    df = pd.read_csv(os.path.join(DATA_DIR, "results.csv"))
    # 只保留有分數的列（過濾掉未來賽程或缺失值）
    df = df.dropna(subset=['home_score', 'away_score'])
    df['home_score'] = df['home_score'].astype(int)
    df['away_score'] = df['away_score'].astype(int)

    batch = []
    for _, row in df.iterrows():
        batch.append({
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "tournament": row.get("tournament") if pd.notna(row.get("tournament")) else None,
            "city": row.get("city") if pd.notna(row.get("city")) else None,
            "country": row.get("country") if pd.notna(row.get("country")) else None,
            "neutral": bool(row.get("neutral")) if pd.notna(row.get("neutral")) else False
        })
        if len(batch) >= 500:
            supabase.table("historical_results").insert(batch).execute()
            batch = []
    if batch:
        supabase.table("historical_results").insert(batch).execute()
    print("✅ Results imported.")

def import_goalscorers():
    print("📥 Importing goalscorers...")
    df = pd.read_csv(os.path.join(DATA_DIR, "goalscorers.csv"))
    # 過濾掉必要欄位為空的列
    df = df.dropna(subset=['date', 'team', 'scorer'])
    batch = []
    for _, row in df.iterrows():
        batch.append({
            "date": row["date"],
            "home_team": row.get("home_team") if pd.notna(row.get("home_team")) else None,
            "away_team": row.get("away_team") if pd.notna(row.get("away_team")) else None,
            "team": row["team"],
            "scorer": row["scorer"],
            "minute": int(row["minute"]) if pd.notna(row.get("minute")) else None,
            "own_goal": bool(row["own_goal"]) if pd.notna(row.get("own_goal")) else False,
            "penalty": bool(row["penalty"]) if pd.notna(row.get("penalty")) else False
        })
        if len(batch) >= 500:
            supabase.table("goalscorers").insert(batch).execute()
            batch = []
    if batch:
        supabase.table("goalscorers").insert(batch).execute()
    print("✅ Goalscorers imported.")

def import_shootouts():
    print("📥 Importing shootouts...")
    df = pd.read_csv(os.path.join(DATA_DIR, "shootouts.csv"))
    df = df.dropna(subset=['date', 'home_team', 'away_team', 'winner'])
    batch = []
    for _, row in df.iterrows():
        batch.append({
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "winner": row["winner"],
            "first_shooter": row.get("first_shooter") if pd.notna(row.get("first_shooter")) else None
        })
        if len(batch) >= 500:
            supabase.table("shootouts").insert(batch).execute()
            batch = []
    if batch:
        supabase.table("shootouts").insert(batch).execute()
    print("✅ Shootouts imported.")

def import_former_names():
    print("📥 Importing former names...")
    df = pd.read_csv(os.path.join(DATA_DIR, "former_names.csv"))
    df = df.dropna(subset=['team', 'former_name'])
    batch = []
    for _, row in df.iterrows():
        batch.append({
            "team": row["team"],
            "former_name": row["former_name"],
            "start_date": row.get("start_date") if pd.notna(row.get("start_date")) else None,
            "end_date": row.get("end_date") if pd.notna(row.get("end_date")) else None
        })
        if len(batch) >= 500:
            supabase.table("former_names").insert(batch).execute()
            batch = []
    if batch:
        supabase.table("former_names").insert(batch).execute()
    print("✅ Former names imported.")

if __name__ == "__main__":
    import_results()
    import_goalscorers()
    import_shootouts()
    import_former_names()
    print("🎉 All Kaggle data imported successfully!")