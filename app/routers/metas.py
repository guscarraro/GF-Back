from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.security import require_key
from app.models.schemas import Meta, MetaIn, PlanejamentoOut
from app.services import metas_service as svc

router = APIRouter(prefix="/metas", tags=["metas"])

@router.get("", response_model=list[Meta])
def listar(ativo: Optional[bool] = None, _: None = Depends(require_key)):
    return svc.listar(ativo)

@router.post("", response_model=Meta)
def criar(body: MetaIn, _: None = Depends(require_key)):
    try:
        return svc.criar(body)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.put("/{id}", response_model=Meta)
def atualizar(id: str, body: MetaIn, _: None = Depends(require_key)):
    try:
        data = svc.atualizar(id, body)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not data:
        raise HTTPException(404, "Não encontrado")
    return data

@router.delete("/{id}")
def deletar(id: str, _: None = Depends(require_key)):
    ok = svc.deletar(id)
    if not ok:
        raise HTTPException(404, "Não encontrado")
    return {"deleted": id}

@router.get("/planejamento", response_model=PlanejamentoOut)
def planejamento(mes: str = Query(..., regex=r"^\d{4}-\d{2}$"), _: None = Depends(require_key)):
    # mes no formato YYYY-MM
    return svc.planejamento(mes)
