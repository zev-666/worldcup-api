import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDSPAPI_KEY = os.getenv("ODDSPAPI_KEY")

print(f"API Key 前 10 碼：{ODDSPAPI_KEY[:10] if ODDSPAPI_KEY else '❌ 未讀取'}")

if not all([SUPABASE_URL, SUPABASE_KEY, ODDSPAPI_KEY]):
    raise ValueError("缺少環境變數，請檢查 .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

WORLD_CUP_TOURNAMENT_ID = 16
BOOKMAKERS = ["pinnacle", "bet365"]   # 要抓的兩家公司

def fetch_odds_for_bookmaker(bookmaker_name):
    """針對一家博彩公司拉取所有比賽賠率"""
    url = "https://api.oddspapi.io/v4/odds-by-tournaments"
    params = {
        "apiKey": ODDSPAPI_KEY,
        "tournamentIds": WORLD_CUP_TOURNAMENT_ID,
        "bookmaker": bookmaker_name
    }
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"  ❌ {bookmaker_name} 請求失敗，狀態碼：{resp.status_code}")
        return []
    fixtures = resp.json()
    print(f"  {bookmaker_name}: 取得 {len(fixtures)} 場比賽")
    return fixtures

def store_odds(fixtures, bookmaker_name, all_matches):
    """將一家博彩公司的賠率寫入資料庫"""
    count = 0
    for fix in fixtures:
        fixture_id = fix["fixtureId"]
        start_time_str = fix.get("startTime", "")
        # 轉換為台北日期
        try:
            start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            taipei_date = (start_dt + timedelta(hours=8)).strftime("%Y-%m-%d")
        except:
            taipei_date = None

        # 用日期比對 matches
        matched_match_id = None
        if taipei_date:
            for m in all_matches:
                if m["kickoff_utc"][:10] == taipei_date:
                    matched_match_id = m["id"]
                    break

        # 提取 1X2 市場 (key = "101")
        bookmaker_data = fix.get("bookmakerOdds", {}).get(bookmaker_name, {})
        if not bookmaker_data.get("bookmakerIsActive"):
            continue
        market_1x2 = bookmaker_data.get("markets", {}).get("101")
        if not market_1x2:
            continue

        outcomes = market_1x2.get("outcomes", {})
        odds_dict = {}
        for out_key in ["101", "102", "103"]:
            if out_key in outcomes:
                player = outcomes[out_key]["players"]["0"]
                outcome_name = player.get("bookmakerOutcomeId", out_key)
                odds_dict[outcome_name] = player.get("price")

        if not odds_dict:
            continue

        try:
            supabase.table("odds_snapshots").insert({
                "match_id": matched_match_id,
                "fixture_id": fixture_id,
                "bookmaker": bookmaker_name,
                "market": "1X2",
                "snapshot_type": "prematch",
                "snapshot_at": "now()",
                "odds_data": odds_dict
            }).execute()
            count += 1
        except Exception as e:
            print(f"    ❌ 寫入失敗 ({fixture_id}): {e}")

    print(f"  {bookmaker_name}: 成功寫入 {count} 筆賠率")

def main():
    # 先讀取 matches 表（只讀一次）
    all_matches = supabase.table("matches").select("id, home_team, away_team, kickoff_utc").execute().data
    print(f"資料庫中有 {len(all_matches)} 場比賽\n")

    for bookmaker in BOOKMAKERS:
        print(f"正在抓取 {bookmaker} 的賠率...")
        fixtures = fetch_odds_for_bookmaker(bookmaker)
        if fixtures:
            store_odds(fixtures, bookmaker, all_matches)
        print()

    print("📦 本次賠率快照完成！（Pinnacle + Bet365）")

if __name__ == "__main__":
    main()