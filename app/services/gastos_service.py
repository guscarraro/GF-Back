from app.db.supabase import supabase
from app.models.schemas import LancamentoIn

TABLE = "transactions"

def listar(mes: str | None):
    q = supabase.table(TABLE).select("*")
    if mes:
        q = q.eq("competencia", mes)
    return q.order("data", desc=True).execute().data

def criar(body: LancamentoIn):
    return supabase.table(TABLE).insert(body.model_dump()).execute().data[0]

def atualizar(id: str, body: LancamentoIn):
    data = supabase.table(TABLE).update(body.model_dump()).eq("id", id).execute().data
    return data[0] if data else None

def deletar(id: str):
    data = supabase.table(TABLE).delete().eq("id", id).execute().data
    return bool(data)

def resumo_mes(mes: str):
    base = supabase.table(TABLE).select("tipo, valor, categoria").eq("competencia", mes).execute().data
    total_entrada = sum(float(x["valor"]) for x in base if x["tipo"] == "entrada")
    total_saida   = sum(float(x["valor"]) for x in base if x["tipo"] == "saida")
    por_categoria: dict[str, float] = {}
    for x in base:
        if x["tipo"] == "saida":
            por_categoria[x["categoria"]] = por_categoria.get(x["categoria"], 0.0) + float(x["valor"])
    return {
        "mes": mes,
        "entrada": round(total_entrada, 2),
        "saida": round(total_saida, 2),
        "saldo": round(total_entrada - total_saida, 2),
        "por_categoria": por_categoria,
    }
