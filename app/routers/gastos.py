# app/routers/gastos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from app.core.security import require_key
from app.models.schemas import Lancamento, LancamentoIn, Lancamentos
from app.services import gastos_service as svc

router = APIRouter(prefix="/gastos", tags=["gastos"])


@router.get("", response_model=Lancamentos)
def listar(mes: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}$"), _: None = Depends(require_key)):
    """
    Lista lançamentos; se mes (YYYY-MM) for informado, filtra pela competencia.
    """
    return svc.listar_por_mes(mes)


@router.get("/{id}", response_model=Lancamento)
def obter(id: str, _: None = Depends(require_key)):
    item = svc.obter(id)
    if not item:
        raise HTTPException(404, "Lançamento não encontrado")
    return item


@router.post("", response_model=Lancamento)
def criar(body: LancamentoIn, _: None = Depends(require_key)):
    created = svc.criar(body)
    return created


@router.put("/{id}", response_model=Lancamento)
def atualizar(id: str, body: LancamentoIn, _: None = Depends(require_key)):
    updated = svc.atualizar(id, body)
    if not updated:
        raise HTTPException(404, "Lançamento não encontrado")
    return updated


@router.delete("/{id}")
def deletar(id: str, _: None = Depends(require_key)):
    ok = svc.deletar(id)
    if not ok:
        raise HTTPException(404, "Lançamento não encontrado")
    return {"deleted": id}
