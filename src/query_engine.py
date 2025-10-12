from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from src.config import *

def build_query_engine():
    llm = Ollama(model=LLM_MODEL, request_timeout=300.0)
    embed_model = OllamaEmbedding(model_name=EMBED_MODEL)

    vstore = Neo4jVectorStore(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        database="neo4j",
        index_name="wikiart_idx",
        node_label="Artwork",
        text_node_property="text",
        embedding_node_property="embedding",
        embedding_dimension=1024
    )

    storage_context = StorageContext.from_defaults(vector_store=vstore)
    index = VectorStoreIndex.from_vector_store(
        vector_store=vstore,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    custom_prompt = PromptTemplate(
        "Eres un experto en arte. "
        "Basándote en los artistas y estilos recuperados del índice, "
        "recomienda artistas o corrientes similares al gusto descrito. "
        "Explica brevemente por qué, siempre en español."
    )

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        llm=llm,
        text_qa_template=custom_prompt
    )

    return query_engine


if __name__ == "__main__":
    engine = build_query_engine()
    print("Motor de recomendación inicializado.")
    while True:
        prompt = input("Describe qué tipo de dibujo te interesa (o 'salir'): ")
        if prompt.lower() == "salir":
            break
        response = engine.query(prompt)
        print("\nRecomendación:\n", response)