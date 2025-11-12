from pydantic import BaseModel, Field, condecimal, constr
from datetime import date
from typing import Optional, List, Dict


# ===================== Lançamentos =====================

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
    # front não precisa mandar, o back preenche para parcelados
    parent_id: Optional[str] = None


class Lancamento(LancamentoIn):
    id: str
    competencia: str
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None


Lancamentos = List[Lancamento]


# ===================== Metas (Targets) =====================

class MetaIn(BaseModel):
    categoria: constr(min_length=1)
    # percentual da receita do mês (0–100)
    percentual: condecimal(max_digits=5, decimal_places=2) = Field(ge=0, le=100)
    # limite em R$ opcional
    teto_mensal: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    ativo: bool = True
    # a partir de quando essa meta vale (se nulo, hoje)
    valid_from: Optional[date] = None


class Meta(MetaIn):
    id: str
    created_at: Optional[str] = None


# resumo por categoria no planejamento
class MetaResumo(BaseModel):
    percentual: float   # % da meta
    teto: float         # teto em R$ (0 se não tiver)
    alvo: float         # quanto "poderia gastar" nessa categoria
    gasto: float        # quanto já foi gasto
    saldo: float        # alvo - gasto (positivo = ainda pode gastar)


# ===================== Planejamento =====================

class PlanejamentoOut(BaseModel):
    mes: constr(regex=r"^\d{4}-\d{2}$")  # ex: "2025-11"
    receita_mes: float
    metas: Dict[str, MetaResumo]         # chave = categoria
    total_alvo: float
    total_gasto: float
    saldo_meta: float
