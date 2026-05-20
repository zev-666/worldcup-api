import requests
import json

API_KEY = "6e4665f0-f6f3-4886-ae9a-b2dac70cd508"
url = f"https://api.oddspapi.io/v4/tournaments?sportId=10&apiKey={API_KEY}"
resp = requests.get(url)
data = resp.json()

# 搜尋所有可能的世界盃關鍵字
keywords = ["world cup", "fifa", "world championship", "2026", "international"]
found = []

for t in data:
    name = t.get("tournamentName", "").lower()
    slug = t.get("tournamentSlug", "").lower()
    category = t.get("categoryName", "").lower()

    for kw in keywords:
        if kw in name or kw in slug or kw in category:
            found.append(t)
            break

print(f"找到 {len(found)} 個可能相關的聯賽：\n")
for t in found:
    print(f"ID: {t['tournamentId']}, Name: {t['tournamentName']}, Slug: {t['tournamentSlug']}, Category: {t.get('categoryName','')}")

# 如果沒有找到，印出 categoryName 是 "International" 的所有聯賽（世界盃通常在這個分類）
if not found:
    print("\n未找到，列出所有 International 分類的聯賽：")
    for t in data:
        if "international" in t.get("categoryName", "").lower():
            print(f"ID: {t['tournamentId']}, Name: {t['tournamentName']}, Slug: {t['tournamentSlug']}")