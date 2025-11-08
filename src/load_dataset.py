from datasets import load_dataset  # type: ignore
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def load_and_clean():
    print("Cargando dataset WikiArt (modo normal)...")

    ds = load_dataset(
        "huggan/wikiart",
        split="train",
        download_mode="reuse_dataset_if_exists"
    )

    print(f"Dataset cargado correctamente: {len(ds):,} obras encontradas.\n")

    features = ds.features
    artist_names = features["artist"].names
    style_names = features["style"].names
    genre_names = features["genre"].names

    print("Procesando dataset completo...\n")

    rows = []

    for item in tqdm(ds, desc="Extrayendo metadatos", total=len(ds), unit="obra", dynamic_ncols=True):
        try:
            artist_idx = item.get("artist")
            style_idx = item.get("style")
            genre_idx = item.get("genre")

            if None in (artist_idx, style_idx, genre_idx):
                continue

            artist = artist_names[artist_idx]
            style = style_names[style_idx]
            genre = genre_names[genre_idx]

            if any(x.startswith("Unknown") for x in (artist, style, genre)):
                continue

            title = item.get("title", "Untitled")

            rows.append({
                "artist": artist,
                "style": style,
                "genre": genre,
                "title": title
            })
        except Exception:
            pass

    print(f"\nFilas cargadas (antes de limpieza): {len(rows):,}")
    df = pd.DataFrame(rows)

    df = df.dropna(subset=["artist", "style", "genre"])
    invalid_values = {"Unknown", "Unknown Artist", "Unknown Genre", "Unknown Style"}
    df = df[~df["artist"].isin(invalid_values)]
    df = df[~df["style"].isin(invalid_values)]
    df = df[~df["genre"].isin(invalid_values)]
    df = df.drop_duplicates(subset=["artist", "title", "style", "genre"], keep="first").reset_index(drop=True)

    df["text"] = df.apply(
        lambda r: f"Artwork titled '{r['title']}'. Style: {r['style']}. Genre: {r['genre']}. Artist: {r['artist']}.",
        axis=1
    )

    output_path = Path("data/processed/wikiart_metadata_clean.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n Dataset limpio guardado en: {output_path}")
    print(f"Registros finales: {len(df):,}")
    print(df.head(10).to_string(index=False))

if __name__ == "__main__":
    load_and_clean()
