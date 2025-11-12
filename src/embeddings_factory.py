import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import warnings
try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.filterwarnings("ignore", category=UnsupportedFieldAttributeWarning)
except Exception:
    # fallback por si la clase cambia en otra versión
    warnings.filterwarnings("ignore", message=".*validate_default.*", category=UserWarning)

# Modo offline/telemetría: activa tras la primera descarga del modelo
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
# Si ya ejecutaste una vez y tienes el modelo en caché, puedes dejarlo en "1"
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Limitar hilos (Windows suele ir mejor con pocos)
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

def make_embed_model():
    provider = os.getenv("EMBED_PROVIDER", "hf").lower()
    if provider in ("hf", "huggingface"):
        model_name = os.getenv("HF_EMBED_MODEL")
        return HuggingFaceEmbedding(model_name=model_name, device="cpu")
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
