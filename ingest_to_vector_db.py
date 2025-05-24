import json
from typing import List, Dict
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_DIM = 1536  # OpenAI embedding dimension for text-embedding-ada-002

def embed_text(text: str) -> np.ndarray:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32)
    return embedding

def ingest_offers_to_faiss(offers: List[Dict], index_file="faiss.index", meta_file="metadata.json"):
    embeddings = []
    metadata = []

    for offer in offers:
        text_to_embed = offer.get("title", "") + " " + offer.get("description", "")
        emb = embed_text(text_to_embed)
        embeddings.append(emb)
        metadata.append({
            "title": offer.get("title"),
            "description": offer.get("description"),
            "brand": offer.get("brand"),
            "expiry": offer.get("expiry"),
            "link": offer.get("link")
        })

    embeddings_np = np.vstack(embeddings)

    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(embeddings_np)
    faiss.write_index(index, index_file)

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Ingested {len(offers)} offers to FAISS index and saved metadata.")

if __name__ == "__main__":
    with open("data/raw_offers.json", "r", encoding="utf-8") as f:
        offers = json.load(f)
    ingest_offers_to_faiss(offers)
