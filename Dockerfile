FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HF_HUB_DISABLE_TELEMETRY=1 \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    PYTHONPATH=/app

ARG HF_EMBED_MODEL=intfloat/multilingual-e5-small
ENV HF_EMBED_MODEL=${HF_EMBED_MODEL}

# Descarga e inicializa el modelo de embeddings EN BUILD
RUN python - <<'EOF'
import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

model_name = os.environ.get("HF_EMBED_MODEL")
if not model_name:
    raise SystemExit("HF_EMBED_MODEL no definido en build")

print(f"Descargando / calentando modelo de embeddings: {model_name}")
embed = HuggingFaceEmbedding(model_name=model_name)
vec = embed.get_text_embedding("warmup")
print(f"Modelo {model_name} inicializado. Dimensión: {len(vec)}")
EOF

ENV TRANSFORMERS_OFFLINE=1

EXPOSE 8501

CMD ["streamlit", "run", "src/chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]
