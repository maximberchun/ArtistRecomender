import os
import re
import unicodedata
import time
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image, ImageFile
import streamlit as st

from src.query_engine import build_query_engine

# ============ Límites de carga ============
# Máximo tiempo por imagen (segundos). Puedes cambiarlo con IMG_TIMEOUT_S=1.2
IMG_TIMEOUT_S = float(os.getenv("IMG_TIMEOUT_S", "1.2"))
# Máximo tamaño descargado por imagen (KB). Puedes cambiarlo con MAX_IMG_KB=350
MAX_IMG_BYTES = int(os.getenv("MAX_IMG_KB", "350")) * 1024

# Permitir abrir imágenes incompletas si cortamos la descarga por tamaño/tiempo
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Silenciar aviso de transformers
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

st.title("Recomendador de Artistas")

@st.cache_resource
def get_query():
    return build_query_engine()
query = get_query()

# ---------- Helpers ----------
def pretty_name(name: str) -> str:
    if not name:
        return "Artista desconocido"
    s = name.replace("-", " ").strip()
    s = re.sub(r"\s+", " ", s).title()
    for p in (" De ", " Del ", " La ", " Las ", " El ", " Los ", " Y ",
              " Van ", " Von ", " Da ", " Di "):
        s = s.replace(p, p.lower())
    return s

def is_empty_response(txt: str | None) -> bool:
    t = (txt or "").strip().lower()
    t2 = re.sub(r"\W+", "", t)
    return (not t) or t.startswith("empty response") or (t2 == "emptyresponse")

def clean_url(u: str | None) -> str | None:
    if not u:
        return None
    u = str(u).strip().replace("\n", "").replace("\r", "").replace(" ", "%20")
    return u if u.lower().startswith(("http://", "https://")) else None

def norm_key(s: str | None) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def _pick_referer(url: str | None) -> str | None:
    """Referer básico para hosts que bloquean hotlink. (sin reintentos)"""
    if not url:
        return None
    host = (urlparse(url).hostname or "").lower()
    if "wikiart.org" in host:
        return "https://www.wikiart.org/"
    return None

def looks_like_image(data: bytes) -> bool:
    """Detección rápida por cabecera binaria si el servidor no envía Content-Type."""
    if not data or len(data) < 12:
        return False
    b = data[:12]
    return (
        b.startswith(b"\xFF\xD8\xFF") or                   # JPG
        b.startswith(b"\x89PNG\r\n\x1a\n") or              # PNG
        b.startswith(b"GIF87a") or b.startswith(b"GIF89a") or  # GIF
        (b[:4] == b"RIFF" and b[8:12] == b"WEBP") or       # WEBP
        b.startswith(b"BM")                                # BMP
    )

def show_image_or_message(url: str | None, caption: str,
                          connect_timeout: float | None = None,
                          read_timeout: float | None = None,
                          max_bytes: int | None = None):
    """
    Descarga una imagen con límites estrictos de tiempo y tamaño.
    - Tiempo total por imagen ≈ connect_timeout + read_timeout (por operación de lectura).
    - Corta si supera 'max_bytes'.
    - Si no se puede mostrar rápidamente, enseña 'Sin imagen disponible...' y continúa.
    """
    url = clean_url(url)
    if not url:
        st.info("Sin imagen disponible para este artista.")
        return

    # Defaults desde las constantes
    connect_timeout = connect_timeout if connect_timeout is not None else max(0.2, IMG_TIMEOUT_S * 0.35)
    read_timeout = read_timeout if read_timeout is not None else max(0.4, IMG_TIMEOUT_S * 0.65)
    max_bytes = max_bytes if max_bytes is not None else MAX_IMG_BYTES

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    ref = _pick_referer(url)
    if ref:
        headers["Referer"] = ref

    start = time.time()
    try:
        # timeout=(conn, read) limita handshake+lectura
        with requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout), stream=True) as r:
            if r.status_code != 200:
                st.info("Sin imagen disponible para este artista.")
                return

            ctype = (r.headers.get("Content-Type") or "").lower()
            # Leer en trozos controlando tiempo y tamaño
            buf = bytearray()
            for chunk in r.iter_content(chunk_size=16_384):
                if not chunk:
                    break
                buf.extend(chunk)
                # límite de tamaño
                if len(buf) >= max_bytes:
                    break
                # límite de tiempo total
                if (time.time() - start) >= IMG_TIMEOUT_S:
                    break

            data = bytes(buf)

        # Validar imagen: por Content-Type o firma binaria
        if ("image" not in ctype) and not looks_like_image(data):
            st.info("Sin imagen disponible para este artista.")
            return

        # Intentar abrir con PIL (aceptando truncadas)
        try:
            img = Image.open(BytesIO(data))
            # Cargar por si viene lazy
            img.load()
        except Exception:
            st.info("Sin imagen disponible para este artista.")
            return

        st.image(img, caption=caption, width="stretch")

    except requests.exceptions.Timeout:
        st.info("Sin imagen disponible para este artista.")
    except Exception:
        st.info("Sin imagen disponible para este artista.")

# ---------- UI ----------
prompt = st.text_input("Describe qué estilo de dibujo o pintura te interesa:")

if st.button("Recomendar"):
    with st.spinner("Generando recomendación..."):
        try:
            result = query(prompt)

            # Resumen (con respaldo si viene vacío)
            summary_box = st.empty()
            text = (result.get("text") or "").strip()
            if is_empty_response(text):
                recs = result.get("artists", [])[:5]
                bullets = "\n".join(
                    f"- {pretty_name(a.get('artist'))} ({a.get('style','-')})" for a in recs
                ) or "- Sin resultados suficientes, prueba con otra descripción."
                text = f"Te propongo estos artistas relacionados con “{prompt}”:\n{bullets}"
            summary_box.success(text)

            st.subheader("Artistas sugeridos:")

            # Deduplicar por artista y limitar a 6
            seen, artists = set(), []
            for a in result.get("artists", []):
                key = norm_key(a.get("artist"))
                if key and key not in seen:
                    artists.append(a)
                    seen.add(key)
                if len(artists) == 6:
                    break

            # Pintar tarjetas con límite de carga por imagen
            for a in artists:
                artist = pretty_name(a.get("artist"))
                style  = a.get("style") or "-"
                genre  = a.get("genre") or "-"
                img    = a.get("image_url")
                link   = clean_url(a.get("artist_wikiart_url"))

                show_image_or_message(img, caption=artist)

                st.markdown(f"**{artist}** — {style} / {genre}")
                if link:
                    st.markdown(f"[Ver en WikiArt ↗]({link})")
                st.markdown("---")

        except Exception as e:
            st.error(f"Error al obtener la recomendación: {e}")
