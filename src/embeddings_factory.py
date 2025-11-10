import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def make_embed_model():
    provider = os.getenv("EMBED_PROVIDER", "hf").lower()
    if provider in ("hf", "huggingface"):
        model_name = os.getenv("HF_EMBED_MODEL", "intfloat/multilingual-e5-large")
        return HuggingFaceEmbedding(model_name=model_name)
    raise ValueError(f"Proveedor de embeddings no soportado: {provider}")

def detect_embedding_dim(embed_model) -> int:
    """
    Intenta obtener la dimensión del modelo de forma robusta.
    """
    try:
        st_model = getattr(embed_model, "_model", None)
        if st_model and hasattr(st_model, "get_sentence_embedding_dimension"):
            return int(st_model.get_sentence_embedding_dimension())
    except Exception:
        pass

    # probar a embedir un texto y medir la longitud
    vec = embed_model.get_text_embedding("dimension-probe")
    return len(vec)
