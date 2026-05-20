import requests

url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
response = requests.get(url)
data = response.json()

print(f"成功！赛事: {data.get('name')}")
print(f"比赛场次: {len(data.get('matches', []))}")

first = data['matches'][0]
print(f"\n示例比赛: {first['team1']} vs {first['team2']} 于 {first['date']} {first['time']}")