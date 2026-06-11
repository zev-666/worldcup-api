from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import matches, odds, predictions, users, payments, agent

app = FastAPI(
    title="FIFA World Cup 2026 數據分析平台",
    description="世界盃比賽預測與賠率分析",
    version="1.0.0",
)

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

app.include_router(matches.router)
app.include_router(odds.router, prefix="/odds", tags=["odds"])
app.include_router(predictions.router)
app.include_router(users.router)
app.include_router(payments.router)
app.include_router(agent.router, prefix="/api/scraped-data", tags=["agent"])

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}