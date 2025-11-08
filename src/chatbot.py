import re
import unicodedata
import os
import time
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
from src.query_engine import build_query_engine
import re

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
    for p in (" De ", " Del ", " La ", " Las ", " El ", " Los ", " Y ", " Van ", " Von ", " Da ", " Di "):
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
    """Normaliza nombre para deduplicar: minúsculas, sin acentos, solo [a-z0-9-]."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

STYLE_MAP = {
    "renacimiento": "Renaissance",
    "barroco": "Baroque",
    "neoclasicismo": "Neoclassicism",
    "rococo": "Rococo",
    "gotico": "Gothic", "gótico": "Gothic",
    "romanticismo": "Romanticism",
    "impresionismo": "Impressionism",
    "postimpresionismo": "Post-Impressionism", "post-impresionismo": "Post-Impressionism",
    "realismo": "Realism",
    "surrealismo": "Surrealism",
    "cubismo": "Cubism",
    "expresionismo": "Expressionism",
    "fauvismo": "Fauvism",
    "simbolismo": "Symbolism",
    "modernismo": "Art Nouveau",
}

def styles_from_prompt(p: str) -> set[str]:
    txt = norm_key(p)
    cands = set()
    for es, en in STYLE_MAP.items():
        if norm_key(es) in txt:
            cands.add(en.lower())
    return cands

def show_image_with_status(url: str | None, caption: str, slow_threshold: float = 1.5, timeout: int = 12):
    url = clean_url(url)
    if not url:
        st.info("Sin imagen disponible para este artista.")
        return
    status_ph = st.empty()
    status_ph.info("Cargando imagen...")
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.wikiart.org/"},
                         stream=True)
        r.raise_for_status()
        if "image" not in r.headers.get("Content-Type", "").lower():
            status_ph.warning("No se pudo cargar la imagen.")
            return
        data = r.content
        dt = time.time() - t0
        status_ph.empty()
        img = Image.open(BytesIO(data))
        st.image(img, caption=caption, width="stretch")
        if dt > slow_threshold:
            st.caption(f"Nota: la imagen tardó {dt:.1f}s en cargarse.")
    except Exception:
        status_ph.warning("No se pudo cargar la imagen.")

# ---------- UI ----------
prompt = st.text_input("Describe qué estilo de dibujo o pintura te interesa:")

if st.button("Recomendar"):
    with st.spinner("Generando recomendación..."):
        try:
            result = query(prompt)

            # ÚNICO lugar donde pintamos el resumen
            summary_box = st.empty()
            text = (result.get("text") or "").strip()
            if is_empty_response(text):
                recs = result.get("artists", [])[:5]
                bullets = "\n".join(
                    f"- {pretty_name(a.get('artist'))} ({a.get('style','-')})"
                    for a in recs
                ) or "- Sin resultados suficientes, prueba con otra descripción."
                text = f"Te propongo estos artistas relacionados con “{prompt}”:\n{bullets}"
            summary_box.success(text)

            # ===== listado visual =====
            st.subheader("Artistas sugeridos:")

            # deduplicar por artista y limitar a 6
            seen, artists = set(), []
            for a in result.get("artists", []):
                key = a.get("artist")
                if key and key not in seen:
                    artists.append(a)
                    seen.add(key)
                if len(artists) == 6:
                    break

            for a in artists:
                artist = pretty_name(a.get("artist"))
                style  = a.get("style") or "-"
                genre  = a.get("genre") or "-"
                img    = a.get("image_url")
                link   = clean_url(a.get("artist_wikiart_url"))

                # Muestra estado, avisa si tarda y si falla
                show_image_with_status(img, caption=artist)

                st.markdown(f"**{artist}** — {style} / {genre}")
                if link:
                    st.markdown(f"[Ver en WikiArt ↗]({link})")
                st.markdown("---")

        except Exception as e:
            st.error(f"Error al obtener la recomendación: {e}")
