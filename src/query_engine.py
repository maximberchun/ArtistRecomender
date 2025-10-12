from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from src.config import *
import requests, time

def wait_for_ollama():
    for _ in range(10):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                print("Ollama disponible.")
                return
        except:
            print("Esperando que Ollama esté disponible...")
            time.sleep(2)
    raise ConnectionError("Ollama no responde en localhost:11434")

wait_for_ollama()

def start_recommender():
    print("Inicializando motor de recomendación...")

    llm = Ollama(model=LLM_MODEL, request_timeout=300.0, keep_alive="30m")
    embed_model = OllamaEmbedding(model_name=EMBED_MODEL)

    # Conectar con Neo4j y el índice existente
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
        "Eres un experto en historia del arte. "
        "Responde siempre en el idioma en que se te habla. "
        "Basándote en la siguiente información recuperada de una base de datos de obras y artistas:\n\n"
        "{context_str}\n\n"
        "Y teniendo en cuenta esta consulta del usuario:\n"
        "{query_str}\n\n"
        "Recomienda artistas o estilos similares y explica brevemente por qué."
    )

    query_engine = index.as_query_engine(
        similarity_top_k=5, 
        llm=llm,
        text_qa_template=custom_prompt
    )

    print("Listo. Escribe una descripción para obtener recomendaciones.")
    while True:
        prompt = input("\nDescribe qué tipo de dibujo te interesa (o escribe 'salir'): ")
        if prompt.lower() == "salir":
            break

        response = query_engine.query(prompt)
        print("\nRecomendación:")
        print(response)

if __name__ == "__main__":
    start_recommender()
