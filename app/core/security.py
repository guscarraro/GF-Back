import bcrypt
from fastapi import Header, HTTPException, status
from app.db.supabase import supabase

_auth_hash_cache: str | None = None

def _load_auth_hash() -> str:
    global _auth_hash_cache
    if _auth_hash_cache:
        return _auth_hash_cache
    res = supabase.table("auth_keys").select("hashed_key").limit(1).execute()
    if not res.data:
        raise RuntimeError("Tabela auth_keys vazia. Insira a senha/hash.")
    _auth_hash_cache = res.data[0]["hashed_key"]
    return _auth_hash_cache

def require_key(x_api_key: str | None = Header(None, alias="x-api-key")):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth requerida")
    hashed = _load_auth_hash()
    ok = bcrypt.checkpw(x_api_key.encode(), hashed.encode())
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chave inválida")
