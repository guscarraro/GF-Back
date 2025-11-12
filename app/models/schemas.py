from pydantic import BaseModel, Field, condecimal, constr
from datetime import date
from typing import Optional, List

class LancamentoIn(BaseModel):
    data: date
    descricao: constr(min_length=1)
    categoria: constr(min_length=1)
    tipo: constr(pattern="^(entrada|saida)$")
    valor: condecimal(max_digits=12, decimal_places=2) = Field(ge=0)
    forma_pagamento: Optional[str] = None
    conta: Optional[str] = None
    recorrente: bool = False
    parcelas_total: int = Field(default=1, ge=1)
    parcela_atual: int = Field(default=1, ge=1)
    status: constr(pattern="^(pago|pendente|cancelado)$") = "pendente"
    previsao: bool = False

class Lancamento(LancamentoIn):
    id: str
    competencia: str
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None

Lancamentos = list[Lancamento]
