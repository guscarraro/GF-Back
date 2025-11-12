# app/core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# tenta carregar .env a partir da raiz do projeto (gf-back/.env)
ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
# fallback: cwd
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados")
