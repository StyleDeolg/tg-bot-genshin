from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, wheel, profile, referral, tasks

app = FastAPI(title="Genshin Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(auth.router)
app.include_router(wheel.router)
app.include_router(profile.router)
app.include_router(referral.router)
app.include_router(tasks.router)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running on Python 3.14!"}