import requests

# 請將下面的字串換成你的真實 API Key（注意只留英數字，不要有空白或換行）
API_KEY = "6e4665f0-f6f3-4886-ae9a-b2dac70cd508"

# 從你的 matches 表中找一個 external_id，例如第一場比賽的 external_id
# 如果不確定，可以先到 Supabase Table Editor 查看 matches 表，複製任一 external_id
FIXTURE_ID = "請替換為實際external_id"

url = f"https://api.oddspapi.io/v1/odds?fixture_id={FIXTURE_ID}"
headers = {"X-API-KEY": API_KEY}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    print("✅ 成功取得資料！JSON 結構如下：")
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ 請求失敗：{e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"HTTP 狀態碼：{e.response.status_code}")
        print(f"回應內容：{e.response.text}")