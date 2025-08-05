from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import temu, blue, config

app = FastAPI()

# 允许跨域访问，方便前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temu.router, prefix="/api/temu")
app.include_router(blue.router, prefix="/api/blue")
app.include_router(config.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Temu Toolkit backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
