from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.predictor import predict_match

router = APIRouter(prefix="/predict", tags=["predictions"])

DEFAULT_ELO = 1500


def get_team_elo(team_name: str) -> float:
    """
    從 team_features 表查詢最新 ELO 分數。
    找不到時回傳預設值 DEFAULT_ELO。
    """
    res = (
        supabase.table("team_features")
        .select("elo_rating")
        .eq("team_name", team_name)
        .order("feature_date", desc=True)
        .limit(1)
        .execute()
    )
    if res.data and len(res.data) > 0:
        return float(res.data[0]["elo_rating"])
    print(f"⚠️ 找不到 {team_name} 的 ELO，使用預設值 {DEFAULT_ELO}")
    return DEFAULT_ELO


@router.get("/{match_id}")
def get_prediction(match_id: str):
    """
    回傳指定比賽的預測結果，包含 1X2、O/U 2.5、BTTS 機率。
    所有用戶皆可存取（免費功能）。
    """
    # 1. 查詢比賽資料
    match_res = (
        supabase.table("matches")
        .select("*")
        .eq("id", match_id)
        .execute()
    )
    if not match_res.data:
        raise HTTPException(status_code=404, detail="Match not found")

    match = match_res.data[0]
    home_team = match["home_team"]
    away_team = match["away_team"]

    # 2. 查詢 ELO
    home_elo = get_team_elo(home_team)
    away_elo = get_team_elo(away_team)

    # 3. 計算預測
    prediction = predict_match(home_elo, away_elo)

    # 4. 檢查是否使用預設 ELO（給前端顯示警示用）
    model_warning = None
    if home_elo == DEFAULT_ELO or away_elo == DEFAULT_ELO:
        model_warning = "部分隊伍使用預設 ELO，預測準確度較低"

    return {
        "match": {
            "home_team": home_team,
            "away_team": away_team,
            "kickoff_utc": match.get("kickoff_utc"),
            "stage": match.get("stage"),
        },
        "elo": {
            "home": home_elo,
            "away": away_elo,
        },
        "prediction": {
            **prediction,
            "model_warning": model_warning,
        },
        "disclaimer": "此為數據分析，非投注建議。",
    }
