import time
import random
import pandas as pd
from pathlib import Path
from ddgs import DDGS
from tqdm import tqdm


# === CONFIGURACIÓN ===
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "wikiart_metadata_clean.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "wikiart_metadata.csv"

# Número máximo de artistas a procesar (para pruebas)
LIMIT = None


def build_wikiart_url(artist_name: str) -> str:
    """Construye la URL del artista en WikiArt (versión en español)."""
    slug = artist_name.strip().lower().replace(" ", "-")
    return f"https://www.wikiart.org/es/{slug}"


def buscar_imagen_duckduckgo(artist, style, genre):
    """Busca una imagen usando DuckDuckGo y devuelve la URL de la primera."""
    query = f"{artist} {style} {genre} artwork painting"
    try:
        with DDGS() as ddgs:
            for r in ddgs.images(query, max_results=1, safesearch="moderate"):
                return r["image"]
    except Exception:
        return None
    return None


def main():
    print("Cargando dataset limpio...")
    df = pd.read_csv(INPUT_FILE)

    # Añadir columnas nuevas si no existen
    if "image_url" not in df.columns:
        df["image_url"] = None
    if "artist_wikiart_url" not in df.columns:
        df["artist_wikiart_url"] = None

    df_pending = df[df["image_url"].isna() | (df["image_url"] == "")]
    df_target = df_pending.head(LIMIT) if LIMIT else df_pending

    print("Buscando imágenes y generando URLs de artistas...\n")

    for idx, row in tqdm(
        df_target.iterrows(),
        total=len(df_target),
        desc="Procesando obras",
        unit="obra",
        dynamic_ncols=True,
    ):
        artist = row["artist"]
        style = row["style"]
        genre = row["genre"]

        # Generar URL de artista
        df.at[idx, "artist_wikiart_url"] = build_wikiart_url(artist)

        # Buscar imagen (DuckDuckGo)
        img_url = buscar_imagen_duckduckgo(artist, style, genre)
        df.at[idx, "image_url"] = img_url

        # Guardado incremental cada 100 filas
        if idx % 100 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

        # Espera aleatoria ligera para evitar bloqueos
        time.sleep(random.uniform(0.2, 0.5))

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n CSV enriquecido guardado en: {OUTPUT_FILE}")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
