import requests
import json

API_KEY = "6e4665f0-f6f3-4886-ae9a-b2dac70cd508"
TOURNAMENT_ID = 16  # 先試 16

url = "https://api.oddspapi.io/v4/odds-by-tournaments"
params = {
    "apiKey": API_KEY,
    "tournamentIds": TOURNAMENT_ID,
    "bookmaker": "pinnacle"   # 指定一家博彩公司以減少資料量
}

resp = requests.get(url, params=params)
if resp.status_code != 200:
    print(f"❌ 請求失敗，狀態碼：{resp.status_code}")
    print(resp.text)
    exit()

data = resp.json()
print(f"✅ 共取得 {len(data)} 場比賽。\n")

# 顯示前 3 場比賽的關鍵資訊，確認是否為世界盃
for i, match in enumerate(data[:3]):
    fixture_id = match.get("fixtureId")
    start_time = match.get("startTime")
    # participant1Id, participant2Id 是 ID，我們還不知道隊名
    # 但我們可以觀察 bookmakerOdds 內的 market 是否有 1X2
    bookmakers = match.get("bookmakerOdds", {})
    print(f"比賽 {i+1}:")
    print(f"  fixtureId: {fixture_id}")
    print(f"  時間: {start_time}")
    # 顯示有哪些博彩公司
    print(f"  博彩公司: {list(bookmakers.keys())}")
    # 如果有 pinnacle，顯示其市場列表
    if "pinnacle" in bookmakers:
        markets = bookmakers["pinnacle"].get("markets", {})
        print(f"  市場 keys: {list(markets.keys())}")
        # 若市場 101 存在，顯示賠率
        if "101" in markets:
            outcomes = markets["101"].get("outcomes", {})
            print("  1X2 odds (home/draw/away):")
            for out_key in ["101","102","103"]:
                if out_key in outcomes:
                    price = outcomes[out_key]["players"]["0"]["price"]
                    outcome_name = outcomes[out_key]["players"]["0"]["bookmakerOutcomeId"]
                    print(f"    {outcome_name}: {price}")
    print("---")

# 印出第一場比賽的完整 JSON（方便檢查結構）
print("\n第一場比賽完整資料（部分）：")
print(json.dumps(data[0], indent=2, ensure_ascii=False)[:2000])  # 限制長度