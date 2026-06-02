from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import matches, odds, predictions, users, payments

app = FastAPI(
    title="FIFA World Cup 2026 數據分析平台",
    description="賽事預測、賠率監控、會員分層",
    version="1.0.0",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://worldcup-frontend-pi.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 所有路由
app.include_router(matches.router)
app.include_router(odds.router, prefix="/odds", tags=["odds"])
app.include_router(predictions.router)
app.include_router(users.router)
app.include_router(payments.router)

# Health check（支援 GET 和 HEAD，UptimeRobot 需要 HEAD）
@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """UptimeRobot keep-alive ping endpoint。"""
    return {"status": "ok"}
