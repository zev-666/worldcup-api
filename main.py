from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import matches, predictions

app = FastAPI(title="World Cup 2026 API", description="赛程与预测数据", version="0.1.0")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://worldcup-frontend-pi.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {"message": "World Cup 2026 API is running"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)