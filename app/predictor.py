import math

def poisson_pmf(lam, k):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def predict_match(home_elo, away_elo):
    # 預期進球數
    home_lambda = 1.5 + (home_elo - away_elo) / 400.0
    away_lambda = 1.5 - (home_elo - away_elo) / 400.0

    # 避免負值
    home_lambda = max(0.1, home_lambda)
    away_lambda = max(0.1, away_lambda)

    # 各隊進 0～5 球的機率（>=5 全累加至 5）
    max_g = 5
    home_pmf = [poisson_pmf(home_lambda, i) for i in range(max_g)]
    away_pmf = [poisson_pmf(away_lambda, i) for i in range(max_g)]
    home_pmf.append(1 - sum(home_pmf))
    away_pmf.append(1 - sum(away_pmf))

    # 計算聯合機率
    home_win = draw = away_win = 0.0
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            p = home_pmf[i] * away_pmf[j]
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p

    # 信心值：ELO 差距 / 400，上限 1.0
    elo_diff = abs(home_elo - away_elo)
    confidence = min(elo_diff / 400.0, 1.0)

    return {
        "home_prob": round(home_win, 4),
        "draw_prob": round(draw, 4),
        "away_prob": round(away_win, 4),
        "confidence": round(confidence, 4)
    }