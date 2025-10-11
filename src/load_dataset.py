from datasets import load_dataset
import pandas as pd
from pathlib import Path

def load_and_clean():
    print("Descargando dataset WikiArt...")
    # huggan/wikiart es el enlace del dataset de hugging face
    ds = load_dataset("huggan/wikiart")["train"]
    data = []
    for ex in ds:
        artist = ex.get("artist") or "Unknown"
        style  = ex.get("style") or "Unknown"
        genre  = ex.get("genre") or "Unknown"
        title  = ex.get("title") or "Untitled"
        text   = f"Artwork titled '{title}'. Style: {style}. Genre: {genre}. Artist: {artist}."
        data.append({"artist": artist, "style": style, "genre": genre, "title": title, "text": text})

    df = pd.DataFrame(data)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/processed/wikiart_clean.csv", index=False)
    print("Dataset limpio guardado en data/processed/wikiart_clean.csv")

if __name__ == "__main__":
    load_and_clean()
