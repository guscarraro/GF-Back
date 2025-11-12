from typing import List, Dict
from app.db.supabase import supabase
from app.models.schemas import MetaIn

TABLE = "metas"
TRANS_TABLE = "transactions"

def listar(ativo: bool | None = None) -> List[dict]:
    q = supabase.table(TABLE).select("*").order("valid_from", desc=True)
    if ativo is not None:
        q = q.eq("ativo", ativo)
    return q.execute().data or []

def criar(body: MetaIn) -> dict:
    # regra opcional: impedir soma > 100 nas ativas
    if body.ativo:
        ativas = listar(True)
        soma = sum(float(x["percentual"]) for x in ativas) + float(body.percentual)
        if soma > 100.0:
            raise ValueError("Soma dos percentuais das metas ativas excede 100%")
    return supabase.table(TABLE).insert(body.model_dump()).execute().data[0]

def atualizar(id: str, body: MetaIn) -> dict | None:
    if body.ativo:
        ativas = [m for m in listar(True) if m["id"] != id]
        soma = sum(float(x["percentual"]) for x in ativas) + float(body.percentual)
        if soma > 100.0:
            raise ValueError("Soma dos percentuais das metas ativas excede 100%")
    data = supabase.table(TABLE).update(body.model_dump()).eq("id", id).execute().data
    return data[0] if data else None

def deletar(id: str) -> bool:
    data = supabase.table(TABLE).delete().eq("id", id).execute().data
    return bool(data)

def _receita_do_mes(mes: str) -> float:
    # soma entradas do mês (competencia = 'YYYY-MM')
    res = (supabase.table(TRANS_TABLE)
           .select("tipo,valor")
           .eq("competencia", mes)
           .eq("tipo", "entrada")
           .execute()).data or []
    total = 0.0
    for r in res:
        total += float(r["valor"])
    return round(total, 2)

def _gasto_por_categoria_mes(mes: str) -> Dict[str, float]:
    res = (supabase.table(TRANS_TABLE)
           .select("tipo,valor,categoria")
           .eq("competencia", mes)
           .eq("tipo", "saida")
           .execute()).data or []
    out: Dict[str, float] = {}
    for r in res:
        cat = r["categoria"]
        val = float(r["valor"])
        out[cat] = out.get(cat, 0.0) + val
    return out

def planejamento(mes: str) -> dict:
    receita = _receita_do_mes(mes)
    metas_ativas = listar(True)
    gastos_cat = _gasto_por_categoria_mes(mes)

    metas_dict: Dict[str, dict] = {}
    total_alvo = 0.0
    total_gasto = 0.0

    for m in metas_ativas:
        pct = float(m["percentual"])
        teto = float(m["teto_mensal"]) if m.get("teto_mensal") is not None else None
        alvo = round((pct/100.0) * receita, 2)
        if teto is not None:
            alvo = min(alvo, teto)
        gasto = round(gastos_cat.get(m["categoria"], 0.0), 2)
        saldo = round(alvo - gasto, 2)
        metas_dict[m["categoria"]] = {
            "percentual": pct,
            "teto": teto if teto is not None else 0.0,
            "alvo": alvo,
            "gasto": gasto,
            "saldo": saldo
        }
        total_alvo += alvo
        total_gasto += gasto

    return {
        "mes": mes,
        "receita_mes": receita,
        "metas": metas_dict,
        "total_alvo": round(total_alvo, 2),
        "total_gasto": round(total_gasto, 2),
        "saldo_meta": round(total_alvo - total_gasto, 2)
    }
