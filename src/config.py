# src/config.py
import os
from dotenv import load_dotenv

# Carga .env temprano
load_dotenv()

def require_env(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Falta variable de entorno: {key}")
    return v

# === Neo4j ===
NEO4J_URI = require_env("NEO4J_URI")
NEO4J_USER = require_env("NEO4J_USER")
NEO4J_PASSWORD = require_env("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# === LLM ===
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = require_env("LLM_MODEL")
GROQ_API_KEY = require_env("GROQ_API_KEY")

# === Embeddings ===
# Si usas HF: HF_EMBED_MODEL debe existir (p.ej. intfloat/multilingual-e5-small)
HF_EMBED_MODEL = require_env("HF_EMBED_MODEL")

# Dim por si algún sitio la necesita fija (mejor detectarla en runtime)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# Log mínimo (no imprimimos secretos)
print(f"Configuración cargada -> Provider: {LLM_PROVIDER}, Modelo: {LLM_MODEL}, Neo4j DB: {NEO4J_DATABASE}")
