from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import matches, odds, predictions

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",   # 記得換成你真正的 Vercel 網址
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(matches.router)
app.include_router(odds.router)
app.include_router(predictions.router)

# 防休眠
@app.get("/health")
def health():
    return {"status": "ok"}