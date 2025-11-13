# src/security_images.py
import socket
import ipaddress
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# Ajusta a tus necesidades:
ALLOWED_HOSTS = {"www.wikiart.org", "wikiart.org"}  # o deja set() para permitir externos (no recomendado)
MAX_IMG_BYTES = 800 * 1024
CONNECT_TIMEOUT, READ_TIMEOUT = 2.0, 3.0
MAX_REDIRECTS = 3
MAX_W, MAX_H = 4000, 4000

def _is_private_ip(host: str) -> bool:
    try:
        for fam in (socket.AF_INET, socket.AF_INET6):
            infos = socket.getaddrinfo(host, None, fam, socket.SOCK_STREAM)
            for _, _, _, _, sockaddr in infos:
                ip = ipaddress.ip_address(sockaddr[0])
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return True
        return False
    except Exception:
        # si falla la resolución DNS, deniega
        return True

def safe_fetch_image_bytes(url: str) -> bytes | None:
    """Devuelve bytes de imagen válidos o None. Mitiga SSRF y bombas de imagen."""
    u = urlparse(url or "")
    if u.scheme not in ("http", "https"):
        return None
    host = (u.hostname or "").lower()
    """
    # A) Allowlist estricta (recomendada)
    if ALLOWED_HOSTS and host not in ALLOWED_HOSTS:
        return None
    # B) Bloquea IPs privadas/loopback
    if _is_private_ip(host):
        return None
    """
    s = requests.Session()
    s.max_redirects = MAX_REDIRECTS
    headers = {
        "User-Agent": "Mozilla/5.0",
        # Evita AVIF si Pillow no tiene plugin
        "Accept": "image/jpeg,image/webp,image/png,image/*;q=0.8,*/*;q=0.5",
        "Referer": f"{u.scheme}://{host}/",
    }

    # HEAD para validar tipo y tamaño
    try:
        h = s.head(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), allow_redirects=True)
        if h.status_code >= 400:
            return None
        ctype = (h.headers.get("Content-Type") or "").lower()
        if "image" not in ctype:
            return None
        try:
            clen = int(h.headers.get("Content-Length", "0"))
            if clen and clen > MAX_IMG_BYTES:
                return None
        except Exception:
            pass
    except Exception:
        return None

    # GET acotado
    try:
        with s.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), stream=True) as r:
            if r.status_code != 200:
                return None
            buf = bytearray()
            for chunk in r.iter_content(32768):
                if not chunk:
                    break
                buf.extend(chunk)
                if len(buf) > MAX_IMG_BYTES:
                    return None
            data = bytes(buf)
    except Exception:
        return None

    # Verificación de integridad y dimensiones
    try:
        im = Image.open(BytesIO(data))
        im.verify()  # valida estructura
        im = Image.open(BytesIO(data))
        im.load()
        if im.width > MAX_W or im.height > MAX_H:
            return None
        return data
    except (UnidentifiedImageError, OSError):
        return None
