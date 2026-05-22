from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import matches, odds, predictions, users
from app.routers import payments  # 🆕 匯入金流路由

app = FastAPI()

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

# 註冊路由
app.include_router(matches.router)
app.include_router(odds.router, prefix="/odds", tags=["odds"])
app.include_router(predictions.router)
app.include_router(users.router)
app.include_router(payments.router)  # 🆕 註冊金流路由（prefix 已在 payments.py 中定義）

# 防休眠健康檢查
@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}