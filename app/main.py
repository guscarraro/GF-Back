from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, gastos
from app.routers import metas  # << NOVO

app = FastAPI(title="GF-back")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.get("/", tags=["health"])
def health():
    return {"ok": True, "service": "GF-back"}

app.include_router(auth.router)
app.include_router(gastos.router)
app.include_router(metas.router)   # << NOVO
