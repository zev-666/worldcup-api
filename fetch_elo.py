import pandas as pd
import requests
from datetime import date

# 1. 取得 eloratings.net 的 HTML
url = "https://www.eloratings.net/"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# 2. 用 pandas 讀取網頁中的表格（通常第一個表格就是排名表）
tables = pd.read_html(response.text, attrs={"class": "ratings"})  # 如果 class 不對，可能要用別的方式定位
# 如果上面找不到，直接試試抓所有表格： tables = pd.read_html(response.text)
df = tables[0]  # 假設第一個表格是我們要的

# 3. 檢查欄位，可能欄位名稱是 'Rank', 'Team', 'Rating', ...
print(df.head())
# 依照你貼的內容，欄位可能為：Rank, Team, Rating, ... （沒有標準英文名稱）
# 你需要依照實際欄位名稱調整下面的程式碼

# 假設欄位依序為：Rank, Team, Rating, ...
df = df.rename(columns={df.columns[0]: "rank", df.columns[1]: "team_name", df.columns[2]: "elo_rating"})

# 4. 定義 2026 世界盃 48 隊名單（請依照實際晉級隊伍更新！）
worldcup_teams = [
    "Argentina", "Brazil", "England", "France", "Spain",
    "Germany", "Portugal", "Netherlands", "Japan", "South Korea",
    "USA", "Mexico", "Canada", "Morocco", "Senegal",
    "Czech Republic", "South Africa", "Saudi Arabia", "Australia",
    "Croatia", "Uruguay", "Switzerland", "Denmark", "Belgium",
    "Colombia", "Ecuador", "Iran", "Wales", "Poland",
    "Serbia", "Tunisia", "Cameroon", "Ghana", "Qatar",
    "Egypt", "Nigeria", "Algeria", "Ivory Coast", "Mali",
    "Burkina Faso", "DR Congo", "Gabon", "Guinea", "Zambia",
    "Cape Verde", "Angola", "Iraq", "United Arab Emirates"
]

# 5. 篩選世界盃隊伍
df_wc = df[df["team_name"].isin(worldcup_teams)].copy()

# 6. 加上 feature_date（今天）
df_wc["feature_date"] = date.today()  # 例如 2026-05-21

# 7. 只保留需要的欄位
df_import = df_wc[["team_name", "feature_date", "elo_rating"]]

# 8. 儲存為 CSV
df_import.to_csv("team_elo_import.csv", index=False)
print(f"✅ 成功抓取 {len(df_import)} 隊的 ELO，並存成 team_elo_import.csv")