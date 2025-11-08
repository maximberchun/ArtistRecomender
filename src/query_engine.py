import os
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.groq import Groq
from llama_index.core.postprocessor import SimilarityPostprocessor
from src.config import *

def build_query_engine():
    # Modelos
    llm = Groq(model=os.getenv("LLM_MODEL"), api_key=os.getenv("GROQ_API_KEY"))
    embed_model = OllamaEmbedding(model_name=os.getenv("EMBED_MODEL"))

    # Vector store Neo4j
    vstore = Neo4jVectorStore(
        url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD,
        database="neo4j", index_name="wikiart_idx",
        node_label="Artwork", text_node_property="text",
        embedding_node_property="embedding", embedding_dimension=1024
    )

    storage_context = StorageContext.from_defaults(vector_store=vstore)
    index = VectorStoreIndex.from_vector_store(
        vector_store=vstore, storage_context=storage_context, embed_model=embed_model
    )

    prompt = PromptTemplate(
        "Eres un experto en arte.\n\n"
        "CONTEXTO (puede estar vacío):\n{context_str}\n\n"
        "CONSULTA:\n{query_str}\n\n"
        "Instrucciones:\n"
        "- Usa el contexto si ayuda y explica brevemente por qué.\n"
        "- Si no hay contexto, da 5 recomendaciones razonadas.\n"
        "- Responde en español, claro y conciso."
    )

    # Se crean una sola vez y se reutilizan en el closure
    retriever = index.as_retriever(similarity_top_k=25)
    qe = index.as_query_engine(
        similarity_top_k=10,
        llm=llm,
        text_qa_template=prompt,
        response_mode="compact",  # evita respuestas vacías por tree_summarize
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.55),  # antes 0.78
        ],
    )
    
    def query(user_text: str):
        """Devuelve texto del LLM + lista de artistas con metadatos."""
        resp = qe.query(user_text)

        results = retriever.retrieve(user_text)
        artists = []
        for r in results:
            meta = r.node.metadata or {}
            artists.append({
                "artist": meta.get("artist"),
                "style": meta.get("style"),
                "genre": meta.get("genre"),
                "image_url": meta.get("image_url"),
                "artist_wikiart_url": meta.get("artist_wikiart_url"),
                "score": float(getattr(r, "score", 0.0) or 0.0),
            })
        artists.sort(key=lambda x: x["score"], reverse=True)
        return {"text": str(resp), "artists": artists}

    return query
