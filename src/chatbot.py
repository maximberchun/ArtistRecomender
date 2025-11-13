import os
import re
import unicodedata
from io import BytesIO
from urllib.parse import urlparse
from datetime import datetime
from src.security_images import safe_fetch_image_bytes
import requests
from PIL import Image, ImageFile
import streamlit as st
from dotenv import load_dotenv
from src.query_engine import build_query_engine
from src.auth import login_guard

import warnings
try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.filterwarnings("ignore", category=UnsupportedFieldAttributeWarning)
except Exception:
    # fallback por si la clase cambia en otra versión
    warnings.filterwarnings("ignore", message=".*validate_default.*", category=UserWarning)

warnings.filterwarnings("ignore", message=".*validate_default.*", category=UserWarning)
# Evitar consultas al Hub y limitar hilos
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

load_dotenv()

# ======================== Configuración de página ========================
st.set_page_config(page_title="Recomendador de Artistas", layout="centered")
_ = login_guard()
# ======================== Límites y opciones ========================
IMG_TIMEOUT_S = float(os.getenv("IMG_TIMEOUT_S", "5.0"))        # seg por imagen
MAX_IMG_BYTES = int(os.getenv("MAX_IMG_KB", "350")) * 1024      # KB por imagen
IMG_MAX_W = int(os.getenv("IMG_MAX_W", "960"))                  # ancho máx. en px (visual)
MAX_ARTISTS_DEFAULT = int(os.getenv("MAX_ARTISTS", "6"))        # artistas por respuesta

# Un único ancho interno para TODO (mensajes, cards, input y título)
OUTER_MAX_PX = int(os.getenv("OUTER_MAX_PX", "820"))           # ancho máx. del body
INNER_MAX_PX = int(os.getenv("INNER_MAX_PX", "820"))            # ancho uniforme

ImageFile.LOAD_TRUNCATED_IMAGES = True
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# ======================== CSS: anchuras, título alineado y botones largos ========================
st.markdown("""
<style>
/* Botones del CUERPO principal (no sidebar) — versión compacta */
[data-testid="stAppViewContainer"] .stButton > button{
  padding: .35rem .60rem;   /* menos padding = botón más pequeño */
  min-height: 2.0rem;       /* altura mínima más baja */
  font-size: .70rem;        /* texto más pequeño */
  line-height: 1.1;
  border-radius: 8px;       /* esquinas algo más compactas */
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: normal;
}
</style>
""", unsafe_allow_html=True)

# ======================== Título (alineado con el chat) ========================
st.markdown('<div class="inner-wrap">', unsafe_allow_html=True)
st.title("Recomendador de Artistas")
st.caption("Describe un estilo, técnica o temática que te gustan y obtén recomendaciones de artistas.")
st.markdown('</div>', unsafe_allow_html=True)

# ======================== Motor de consulta ========================
@st.cache_resource
def get_query():
    return build_query_engine()

query = get_query()

# ======================== Helpers ========================
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
    if not url:
        return None
    host = (urlparse(url).hostname or "").lower()
    if "wikiart.org" in host:
        return "https://www.wikiart.org/"
    return None

def looks_like_image(data: bytes) -> bool:
    if not data or len(data) < 12:
        return False
    b = data[:12]
    return (
        b.startswith(b"\xFF\xD8\xFF") or
        b.startswith(b"\x89PNG\r\n\x1a\n") or
        b.startswith(b"GIF87a") or b.startswith(b"GIF89a") or
        (b[:4] == b"RIFF" and b[8:12] == b"WEBP") or
        b.startswith(b"BM")
    )

def _fetch_image_bytes(url: str, connect_timeout: float, read_timeout: float, max_bytes: int) -> tuple[bytes | None, bool]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        # evita AVIF si no tienes plugin
        "Accept": "image/jpeg,image/webp,image/png,image/*;q=0.8,*/*;q=0.5",
    }
    ref = _pick_referer(url)
    if ref:
        headers["Referer"] = ref

    try:
        with requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout), stream=True) as r:
            if r.status_code != 200:
                return None, False

            # Si sabemos el tamaño esperado, úsalo para decidir si está completa
            content_len = None
            try:
                content_len = int(r.headers.get("Content-Length", "0")) or None
                if content_len and content_len > max_bytes:
                    # muy grande para nuestro límite
                    return None, False
            except Exception:
                content_len = None

            buf = bytearray()
            for chunk in r.iter_content(chunk_size=32_768):
                if not chunk:
                    break
                buf.extend(chunk)
                if len(buf) > max_bytes:
                    # cortamos por límite
                    return None, False

            data = bytes(buf)
            # completa si coincide con Content-Length
            complete = (content_len is None) or (len(data) == content_len)
            return data, complete
    except Exception:
        return None, False


def show_image_or_message(url: str | None, caption: str,
                          enable_images: bool = True):
    url = clean_url(url)
    if not enable_images:
        st.info("Imágenes desactivadas en Opciones.")
        return
    if not url:
        st.info("Sin imagen disponible para este artista.")
        return

    data = safe_fetch_image_bytes(url)
    if not data:
        st.info("Sin imagen disponible para este artista.")
        return

    try:
        im = Image.open(BytesIO(data))
        im.load()
        st.image(im, caption=caption)
    except Exception:
        st.info("Sin imagen disponible para este artista.")

def render_artist_card(artist, style, genre, img, link, enable_images=True):
    with st.container():
        st.markdown('<div class="artist-card">', unsafe_allow_html=True)
        if img:
            show_image_or_message(img, caption=artist, enable_images=enable_images)
        st.markdown(f"**{artist}** — {style} / {genre}")
        if link:
            st.markdown(f"[Ver en WikiArt ↗]({link})")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="artist-divider"></div>', unsafe_allow_html=True)

def export_chat_as_txt(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        role = m.get("role", "assistant")
        content = (m.get("content") or "").strip()
        artists = m.get("artists") or []
        stamp = m.get("ts") or ""
        lines.append(f"[{stamp}] {role.upper()}: {content}")
        for a in artists:
            artist = pretty_name(a.get("artist"))
            style  = a.get("style") or "-"
            genre  = a.get("genre") or "-"
            link   = clean_url(a.get("artist_wikiart_url"))
            lines.append(f"  - {artist} — {style} / {genre} {('('+link+')' if link else '')}")
        lines.append("")
    return "\n".join(lines)

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ======================== Estado (historial) ========================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Escribe tu descripción abajo y te recomendaré artistas relacionados. Puedes empezar con un ejemplo de la barra lateral.",
        "artists": [],
        "ts": now_iso()
    }]

if "last_user_prompt" not in st.session_state:
    st.session_state.last_user_prompt = ""

if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

# ======================== Sidebar ========================
with st.sidebar:
    st.subheader("Instrucciones")
    with st.expander("Cómo funciona", expanded=False):
        st.markdown(
            """
1) Escribe una descripción del estilo, técnica o temática.  
2) Recibirás un resumen y artistas deduplicados.  
3) Si una imagen no carga rápido, verás un aviso.  
4) Puedes limpiar la conversación.

Ejemplos:
- Realismo ruso psicológico.
- Paisajes urbanos.
- "High Renaissance".
            """
        )

    st.subheader("Opciones")
    max_artists = st.slider("Máx. artistas por respuesta", 1, 10, value=MAX_ARTISTS_DEFAULT)
    show_images_opt = st.checkbox("Mostrar imágenes", value=True)

    with st.expander("Avanzadas", expanded=False):
        st.markdown("Ajusta límites de descarga por imagen (útil para conexiones lentas).")
        _img_timeout = st.number_input("Tiempo máx. por imagen (s)", min_value=0.3, max_value=5.0, value=float(IMG_TIMEOUT_S), step=0.1)
        _img_kb = st.number_input("Tamaño máx. por imagen (KB)", min_value=50, max_value=1024, value=int(MAX_IMG_BYTES/1024), step=50)
        _img_w = st.number_input("Ancho máx. de imagen (px)", min_value=400, max_value=1600, value=int(IMG_MAX_W), step=50)

    st.divider()

    def _reset_chat():
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Conversación reiniciada. ¿Qué estilo te interesa?",
            "artists": [],
            "ts": now_iso()
        }]
        st.session_state.last_user_prompt = ""
        st.session_state.pending_user_input = None
        st.toast("Historial eliminado")

    if st.button("Borrar conversación"):
        _reset_chat()

    st.divider()
    st.subheader("Acciones")
    if st.button("Reintentar última consulta", disabled=(not st.session_state.last_user_prompt.strip())):
        st.session_state.pending_user_input = st.session_state.last_user_prompt
        st.toast("Reintentando última consulta")

# ======================== Render historial ========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
        artists = msg.get("artists") or []
        if artists:
            st.markdown("**Artistas sugeridos:**")
            for a in artists:
                artist = pretty_name(a.get("artist"))
                style  = a.get("style") or "-"
                genre  = a.get("genre") or "-"
                img    = a.get("image_url")
                link   = clean_url(a.get("artist_wikiart_url"))
                render_artist_card(artist, style, genre, img, link, enable_images=show_images_opt)

# ======================== Entrada de usuario ========================
def _is_duplicate(prev: str, current: str) -> bool:
    return norm_key(prev) == norm_key(current)

raw_user_input = st.chat_input("Describe qué estilo de dibujo o pintura te interesa")
user_input = (raw_user_input or st.session_state.pending_user_input or "").strip()
if st.session_state.pending_user_input:
    st.session_state.pending_user_input = None

if user_input:
    if _is_duplicate(st.session_state.last_user_prompt, user_input):
        st.info("Has enviado la misma consulta dos veces seguidas. Continúo igualmente.")

    st.session_state.messages.append({"role": "user", "content": user_input, "artists": [], "ts": now_iso()})
    st.session_state.last_user_prompt = user_input

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Generando recomendación..."):
            try:
                result = query(user_input)

                text = (result.get("text") or "").strip()
                if is_empty_response(text):
                    recs = result.get("artists", [])[:max_artists]
                    bullets = "\n".join(
                        f"- {pretty_name(a.get('artist'))} ({a.get('style','-')})" for a in recs
                    ) or "- Sin resultados suficientes, prueba con otra descripción (p. ej., añade técnica o época)."
                    text = f'Te propongo estos artistas relacionados con "{user_input}":\n{bullets}'

                seen, artists = set(), []
                for a in result.get("artists", []):
                    key = norm_key(a.get("artist"))
                    if key and key not in seen:
                        artists.append(a)
                        seen.add(key)
                    if len(artists) == max_artists:
                        break

                if text:
                    st.markdown(text)
                if artists:
                    st.markdown("**Artistas sugeridos:**")
                for a in artists:
                    artist = pretty_name(a.get("artist"))
                    style  = a.get("style") or "-"
                    genre  = a.get("genre") or "-"
                    img    = a.get("image_url")
                    link   = clean_url(a.get("artist_wikiart_url"))
                    render_artist_card(artist, style, genre, img, link, enable_images=show_images_opt)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": text if text else "(Sin contenido)",
                    "artists": artists,
                    "ts": now_iso()
                })

                c1, c2, c3 = st.columns([1,1,4])
                with c1:
                    st.button("Resultado útil", key=f"fb-up-{len(st.session_state.messages)}")
                with c2:
                    st.button("No me sirve", key=f"fb-down-{len(st.session_state.messages)}")

            except Exception as e:
                err = f"Error al obtener la recomendación: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err, "artists": [], "ts": now_iso()})