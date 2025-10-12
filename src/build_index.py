import pandas as pd
from tqdm import tqdm
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import VectorStoreIndex, Document, StorageContext
from src.config import *

def build_index():
    print("Iniciando construcción del índice vectorial...")

    # Modelos Ollama
    embed_model = OllamaEmbedding(model_name=EMBED_MODEL)
    llm = Ollama(model=LLM_MODEL)

    # Conexión a Neo4j
    vstore = Neo4jVectorStore(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        database="neo4j",
        index_name="wikiart_idx",
        node_label="Artwork",
        text_node_property="text",
        embedding_node_property="embedding",
        embedding_dimension=1024,
        distance_strategy="cosine",
    )

    try:
        vstore.create_new_index()
        print("Índice vectorial creado.")
    except Exception as e:
        if "EquivalentSchemaRuleAlreadyExists" in str(e):
            print("El índice ya existía, continuando sin recrearlo...")
        else:
            raise e

    df = pd.read_csv("data/processed/wikiart_clean.csv").sample(2000, random_state=42)

    docs = [
        Document(
            text=row["text"],
            metadata={
                "artist": row["artist"],
                "style": row["style"],
                "genre": row["genre"],
            },
        )
        for _, row in tqdm(df.iterrows(), total=len(df))
    ]

    # Aquí aseguramos que LlamaIndex use Neo4j como destino
    storage_context = StorageContext.from_defaults(vector_store=vstore)

    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=embed_model
    )

    print("Embeddings generados e indexados correctamente en Neo4j.")

if __name__ == "__main__":
    build_index()
