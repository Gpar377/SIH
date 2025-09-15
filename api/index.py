from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="EduAlert")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    try:
        with open("static/complete_frontend.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return {"error": str(e), "message": "File not found"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/test")
async def test():
    files = []
    try:
        files = os.listdir(".")
        static_files = os.listdir("static") if os.path.exists("static") else []
        return {"files": files, "static_files": static_files}
    except Exception as e:
        return {"error": str(e), "files": files}