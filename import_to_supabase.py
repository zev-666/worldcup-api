from supabase import create_client, Client
import requests
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的变量

# 获取环境变量
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# 创建 Supabase 客户端
supabase: Client = create_client(url, key)

def parse_kickoff(date_str, time_str):
    """专门处理 2026 世界杯数据中的时间格式，如 '13:00 UTC-6'"""
    parts = time_str.split()
    if len(parts) == 2 and parts[1].startswith("UTC"):
        time_part = parts[0]
        # 解析偏移量，例如 'UTC-6' 就是 -6
        offset = int(parts[1].replace("UTC", ""))
        dt = datetime.strptime(f"{date_str} {time_part}", "%Y-%m-%d %H:%M")
        dt_utc = dt - timedelta(hours=offset)
        return dt_utc.replace(tzinfo=timezone.utc).isoformat()
    # 如果没有时区信息，就当作 UTC 时间（这种情况应该很少）
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").isoformat()

def fetch_and_insert_matches():
    print("正在从网络获取比赛数据...")
    # 从 GitHub 获取最新的 JSON 数据
    resp = requests.get("https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json")
    data = resp.json()
    
    matches = []
    for match in data.get("matches", []):
        # 准备要插入的数据
        match_data = {
            "external_id": f"2026_{match['team1']}_{match['team2']}_{match['date']}".replace(" ", "_"),
            "home_team": match["team1"],
            "away_team": match["team2"],
            "kickoff_utc": parse_kickoff(match["date"], match["time"]),
            "stage": match.get("group") or match.get("round", ""),
            "venue": match.get("ground", ""),
            "status": "scheduled"
        }
        matches.append(match_data)

    print(f"成功解析到 {len(matches)} 场比赛，准备导入数据库...")
    
    # 插入数据，并自动跳过已存在的（基于 external_id）
    inserted_count = 0
    for match in matches:
        # 检查是否已存在
        existing = supabase.table("matches").select("id").eq("external_id", match["external_id"]).execute()
        if existing.data:
            continue
        # 插入新数据
        supabase.table("matches").insert(match).execute()
        inserted_count += 1
        print(f"已导入: {match['home_team']} vs {match['away_team']}")

    print(f"完成！共新导入 {inserted_count} 场比赛。")

if __name__ == "__main__":
    fetch_and_insert_matches()