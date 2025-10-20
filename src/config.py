import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
LLM_MODEL = os.getenv("LLM_MODEL")
EMBED_MODEL = os.getenv("EMBED_MODEL")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 1024))
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not NEO4J_URI or not NEO4J_USER:
    raise ValueError("Faltan variables de entorno para conectar con Neo4j. Verifica tu archivo .env")

print(f"Configuración cargada correctamente -> Provider: {LLM_PROVIDER}, Modelo: {LLM_MODEL}")
