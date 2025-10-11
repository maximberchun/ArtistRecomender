from datasets import load_dataset
import pandas as pd
from pathlib import Path

# IMPORTANTE ANTES DE EJECUTAR
# Este archivo tarda mucho en compilarse y almacena aprox 60 gb de cache
# NO ES NECESARIO COMPILARLO salvo que necesita crear nuevo .csv

def load_and_clean():
    print("Descargando solo metadatos del dataset WikiArt...")
    ds = load_dataset("huggan/wikiart", split="train")

    # elimina la columna "image" porque ocupa demasiado
    if "image" in ds.column_names:
        ds = ds.remove_columns("image")

    style_names = ds.features["style"].names
    genre_names = ds.features["genre"].names
    artist_names = ds.features["artist"].names

    df = pd.DataFrame({
        "artist": [artist_names[a] for a in ds["artist"]],
        "style": [style_names[s] for s in ds["style"]],
        "genre": [genre_names[g] for g in ds["genre"]],
    })
    
    for col in ["artist", "style", "genre"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = "Unknown"
            
    df["title"] = ("Untitled")
    df["text"] = df.apply(
        lambda row: f"Artwork titled '{row['title']}'. Style: {row['style']}. Genre: {row['genre']}. Artist: {row['artist']}.",
        axis=1,
    )

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df[["artist", "style", "genre", "title", "text"]].to_csv("data/processed/wikiart_clean.csv", index=False)
    print("Dataset limpio guardado en data/processed/wikiart_clean.csv")

if __name__ == "__main__":
    load_and_clean()
