import math

def predict_match(home_elo: float, away_elo: float, max_goals: int = 5):
    """
    使用 Poisson 分佈計算主勝、平局、客勝機率。
    公式：
        home_expected = 1.5 + (home_elo - away_elo) / 400
        away_expected = 1.5 - (home_elo - away_elo) / 400
    信心度 = min(|elo_diff| / 400, 1.0)
    """
    elo_diff = home_elo - away_elo
    home_exp = 1.5 + elo_diff / 400
    away_exp = 1.5 - elo_diff / 400

    # 計算 Poisson 機率密度函數
    def poisson_pmf(lmbda, k):
        return math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)

    home_prob = 0.0
    away_prob = 0.0
    draw_prob = 0.0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson_pmf(home_exp, i) * poisson_pmf(away_exp, j)
            if i > j:
                home_prob += p
            elif i < j:
                away_prob += p
            else:
                draw_prob += p

    # 信心度：ELO 差距絕對值除以 400，最高 1.0
    confidence = min(abs(elo_diff) / 400, 1.0)

    return {
        "home_prob": round(home_prob, 4),
        "draw_prob": round(draw_prob, 4),
        "away_prob": round(away_prob, 4),
        "confidence": round(confidence, 4)
    }