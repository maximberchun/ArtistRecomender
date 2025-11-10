import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.llms.groq import Groq

from src.embeddings_factory import make_embed_model, detect_embedding_dim
from src.config import *  # si te aporta constantes, mantenlo

def build_index():
    print("Iniciando construcción del índice vectorial...")

    # === LLM: Groq ===
    llm_model = os.getenv("LLM_MODEL")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("Falta GROQ_API_KEY en el entorno.")
    llm = Groq(model=llm_model, api_key=groq_api_key)
    # (Si en otro sitio usas Settings.llm = llm, hazlo allí.)

    # === Embeddings: HuggingFace ===
    embed_model = make_embed_model()
    emb_dim = detect_embedding_dim(embed_model)
    print(f"Dimensión de embeddings detectada: {emb_dim}")

    # === Neo4j Vector Store ===
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_db = os.getenv("NEO4J_DATABASE")

    vstore = Neo4jVectorStore(
        url=neo4j_uri,
        username=neo4j_user,
        password=neo4j_password,
        database=neo4j_db,
        index_name="wikiart_index",
        node_label="Artwork",
        text_node_property="text",
        embedding_node_property="embedding",
        embedding_dimension=emb_dim,    # <- clave
        distance_strategy="cosine",
    )

    # Crear índice si no existe
    try:
        vstore.create_new_index()
        print("Índice vectorial creado.")
    except Exception as e:
        if "EquivalentSchemaRuleAlreadyExists" in str(e):
            print("El índice ya existía, continuando sin recrearlo...")
        else:
            raise

    # === Carga de datos ===
    csv_path = Path("data/processed/wikiart_metadata.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {csv_path}")

    df = pd.read_csv(csv_path)
    df = df.sample(min(len(df), 2000), random_state=42)

    docs = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Creando documentos"):
        text = row.get("text", "")
        if not isinstance(text, str) or not text.strip():
            continue
        metadata = {
            "artist": row.get("artist"),
            "style": row.get("style"),
            "genre": row.get("genre"),
            "artist_wikiart_url": row.get("artist_wikiart_url"),
            "image_url": row.get("image_url"),
        }
        docs.append(Document(text=text, metadata=metadata))

    print(f"Total de documentos listos para indexar: {len(docs):,}")

    storage_context = StorageContext.from_defaults(vector_store=vstore)

    # Construcción del índice con el embedder HF
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    print("Embeddings generados e indexados correctamente en Neo4j.")

if __name__ == "__main__":
    build_index()
