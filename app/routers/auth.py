from fastapi import APIRouter, Depends
from app.core.security import require_key
from app.db.supabase import supabase

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(_: None = Depends(require_key)):
    # se passou na dependência, a chave está válida
    return {"auth": "ok"}

@router.post("/rotate")
def rotate_key(_: None = Depends(require_key)):
    # exemplo: rota para confirmar que o usuário autenticado pode iniciar rotação manual
    # (a rotação real do hash você faz rodando SQL no Supabase)
    return {"status": "ready_to_rotate"}
