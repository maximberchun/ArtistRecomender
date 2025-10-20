from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from src.config import *
from llama_index.llms.groq import Groq
from llama_index.core.postprocessor import SimilarityPostprocessor

def build_query_engine():
    llm = Groq(
        model=os.getenv("LLM_MODEL"),         
        api_key=os.getenv("GROQ_API_KEY"),
    ) 
    embed_model = OllamaEmbedding(model_name=os.getenv("EMBED_MODEL"))

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
        "Eres un experto en arte.\n\n"
        "CONTEXTO (puede estar vacío):\n{context_str}\n\n"
        "CONSULTA:\n{query_str}\n\n"
        "Instrucciones:\n"
        "- Si el contexto es útil, úsalo para recomendar artistas realistas y explica por qué (temas, técnica, época).\n"
        "- Si el contexto está vacío o es escaso, da igualmente 5 recomendaciones fundamentadas.\n"
        "- Responde siempre en español y en formato de lista breve."
    )

    retriever = index.as_retriever(similarity_top_k=3)
    hits = retriever.retrieve("realismo")
    print(f"[debug] hits={len(hits)}  ids={[h.node.node_id for h in hits]}")

    query_engine = index.as_query_engine(
        similarity_top_k=8,
        llm=llm,
        text_qa_template=custom_prompt,
        response_mode="tree_summarize",       
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.78),  
        ],
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
        print("\n[fuentes]:")
        for sn in response.source_nodes:
            print(f"- score={sn.score:.3f} | id={sn.node.node_id} | meta={sn.node.metadata}")