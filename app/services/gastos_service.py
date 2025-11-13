# app/services/gastos_service.py
from typing import List, Optional
from uuid import uuid4
from datetime import date

from dateutil.relativedelta import relativedelta

from app.db.supabase import supabase
from app.models.schemas import LancamentoIn


TABLE = "transactions"


def listar_por_mes(mes: Optional[str] = None) -> List[dict]:
    """
    Lista lançamentos. Se mes for informado (YYYY-MM), filtra por competencia.
    """
    q = supabase.table(TABLE).select("*").order("data", desc=False)
    if mes:
        q = q.eq("competencia", mes)
    resp = q.execute()
    return resp.data or []


def obter(id_: str) -> Optional[dict]:
    resp = supabase.table(TABLE).select("*").eq("id", id_).single().execute()
    return resp.data if resp.data else None


def criar(body: LancamentoIn) -> dict:
    """
    Cria lançamento.
    - Se parcelas_total == 1: insere 1 linha normal.
    - Se parcelas_total > 1: divide o valor e cria N parcelas mensais
      (data + 0, +1, +2 meses...), com o mesmo parent_id.
    Retorna sempre a 1ª parcela criada (a do mês atual).
    """
    payload = body.model_dump()

    # ⚠ normaliza tipos não-JSON (date / Decimal)
    if isinstance(payload.get("data"), date):
        payload["data"] = payload["data"].isoformat()

    # pydantic manda Decimal -> vira float
    payload["valor"] = float(payload["valor"])
    total = float(payload["valor"])
    n_parcelas = int(payload.get("parcelas_total") or 1)

    # ----- caso simples: sem parcelas -----
    if n_parcelas <= 1:
        resp = supabase.table(TABLE).insert(payload).execute()
        data = resp.data or []
        return data[0]

    # ----- caso parcelado -----
    parent = str(uuid4())

    # valor por parcela com ajuste na última (pra não perder centavos)
    base_valor = round(total / n_parcelas, 2)
    valores = []
    acumulado = 0.0
    for i in range(1, n_parcelas + 1):
        if i < n_parcelas:
            valores.append(base_valor)
            acumulado += base_valor
        else:
            # última parcela pega o resto
            valores.append(round(total - acumulado, 2))

    # data base: usa body.data (date) se tiver, senão parseia a string do payload
    if isinstance(body.data, date):
        data_base = body.data
    else:
        data_base = date.fromisoformat(payload["data"])

    linhas = []
    for i in range(1, n_parcelas + 1):
        d = data_base + relativedelta(months=i - 1)
        linha = {
            "data": d.isoformat(),
            "descricao": payload["descricao"],
            "categoria": payload["categoria"],
            "tipo": payload["tipo"],
            "valor": valores[i - 1],
            "forma_pagamento": payload.get("forma_pagamento"),
            "conta": payload.get("conta"),
            "recorrente": False,
            "parcelas_total": n_parcelas,
            "parcela_atual": i,
            "status": payload.get("status") or "pendente",
            # futuras parcelas marcadas como previsão
            "previsao": True if i > 1 else payload.get("previsao", False),
            "parent_id": parent,
        }
        linhas.append(linha)

    resp = supabase.table(TABLE).insert(linhas).execute()
    data_ret = resp.data or []
    # retorna a primeira parcela (mês atual)
    return data_ret[0]


def atualizar(id_: str, body: LancamentoIn) -> Optional[dict]:
    """
    Atualiza apenas a linha informada (não mexe nas demais parcelas).
    """
    payload = body.model_dump()

    if isinstance(payload.get("data"), date):
        payload["data"] = payload["data"].isoformat()

    payload["valor"] = float(payload["valor"])

    resp = supabase.table(TABLE).update(payload).eq("id", id_).execute()
    data = resp.data or []
    return data[0] if data else None


def deletar(id_: str) -> bool:
    """
    Deleta apenas a linha informada.
    Se você quiser futuramente deletar o pacote inteiro de parcelas,
    pode filtrar por parent_id.
    """
    resp = supabase.table(TABLE).delete().eq("id", id_).execute()
    return bool(resp.data)
