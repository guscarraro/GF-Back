from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.core.security import require_key
from app.models.schemas import Lancamento, LancamentoIn, Lancamentos
from app.services import gastos_service as svc

router = APIRouter(prefix="/gastos", tags=["gastos"])

@router.get("", response_model=Lancamentos)
def listar(mes: Optional[str] = None, _: None = Depends(require_key)):
    return svc.listar(mes)

@router.post("", response_model=Lancamento)
def criar(body: LancamentoIn, _: None = Depends(require_key)):
    return svc.criar(body)

@router.put("/{id}", response_model=Lancamento)
def atualizar(id: str, body: LancamentoIn, _: None = Depends(require_key)):
    data = svc.atualizar(id, body)
    if not data:
        raise HTTPException(404, "Não encontrado")
    return data

@router.delete("/{id}")
def deletar(id: str, _: None = Depends(require_key)):
    ok = svc.deletar(id)
    if not ok:
        raise HTTPException(404, "Não encontrado")
    return {"deleted": id}

@router.get("/resumo/mes")
def resumo_mes(mes: str, _: None = Depends(require_key)):
    return svc.resumo_mes(mes)
