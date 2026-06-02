import math


def predict_match(home_elo: float, away_elo: float, max_goals: int = 5) -> dict:
    """
    使用 Poisson 分佈計算主勝、平局、客勝機率，以及大小球預測。

    公式：
        home_expected = 1.5 + (home_elo - away_elo) / 400
        away_expected = 1.5 - (home_elo - away_elo) / 400
    信心度 = min(|elo_diff| / 400, 1.0)
    """
    elo_diff = home_elo - away_elo

    # 確保預期進球數不為負
    home_exp = max(0.3, 1.5 + elo_diff / 400)
    away_exp = max(0.3, 1.5 - elo_diff / 400)

    def poisson_pmf(lmbda: float, k: int) -> float:
        return math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)

    home_prob = 0.0
    away_prob = 0.0
    draw_prob = 0.0
    over_prob = 0.0   # 大球（總進球 > 2.5）
    under_prob = 0.0  # 小球（總進球 <= 2.5）
    btts_yes = 0.0    # 雙隊得分（兩隊都進球）
    btts_no = 0.0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson_pmf(home_exp, i) * poisson_pmf(away_exp, j)

            # 1X2
            if i > j:
                home_prob += p
            elif i < j:
                away_prob += p
            else:
                draw_prob += p

            # O/U 2.5
            if i + j > 2:
                over_prob += p
            else:
                under_prob += p

            # BTTS
            if i > 0 and j > 0:
                btts_yes += p
            else:
                btts_no += p

    expected_goals = round(home_exp + away_exp, 2)
    confidence = round(min(abs(elo_diff) / 400, 1.0), 4)

    return {
        # 1X2
        "home_prob": round(home_prob, 4),
        "draw_prob": round(draw_prob, 4),
        "away_prob": round(away_prob, 4),
        # O/U 2.5
        "over_prob": round(over_prob, 4),
        "under_prob": round(under_prob, 4),
        "expected_goals": expected_goals,
        # BTTS
        "btts_yes": round(btts_yes, 4),
        "btts_no": round(btts_no, 4),
        # 信心度
        "confidence": confidence,
    }
