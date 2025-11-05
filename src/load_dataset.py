from datasets import load_dataset #type: ignore
import pandas as pd
from pathlib import Path

def load_and_clean():
    print("Descargando metadatos del dataset WikiArt...")

    # Cargar solo los metadatos, sin descargar los archivos de imagen
    ds_stream = load_dataset("huggan/wikiart", split="train", streaming=True)

    # Convertir el stream en una lista limitada (para no consumir toda la memoria)
    rows = []
    max_rows = 20000  # puedes ajustar este valor (ej. 20000 si tu RAM lo permite)
    for i, item in enumerate(ds_stream):
        if i >= max_rows:
            break
        try:
            url = item.get("image", {}).get("path") if isinstance(item.get("image"), dict) else None
            if not url or not url.startswith("https"):
                continue
            artist = item.get("artist")
            style = item.get("style")
            genre = item.get("genre")
            if None in (artist, style, genre):
                continue
            rows.append({
                "artist": artist,
                "style": style,
                "genre": genre,
                "title": "Untitled",
                "url": url
            })
        except Exception:
            continue

    print(f"Filas cargadas: {len(rows)}")

    df = pd.DataFrame(rows)

    # Limpiar valores vacíos o duplicados
    df = df.dropna(subset=["artist", "style", "genre", "url"])
    df = df[df["url"].str.startswith("https")]
    df = df.drop_duplicates(subset=["artist", "style", "genre", "url"], keep="first").reset_index(drop=True)

    # Añadir campo 'text' para embeddings
    df["text"] = df.apply(
        lambda row: f"Artwork titled '{row['title']}'. Style: {row['style']}. Genre: {row['genre']}. Artist: {row['artist']}.",
        axis=1
    )

    output_path = Path("data/processed/wikiart_clean.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Dataset limpio guardado en {output_path}")
    print(f"Registros finales: {len(df)}")

if __name__ == "__main__":
    load_and_clean()
