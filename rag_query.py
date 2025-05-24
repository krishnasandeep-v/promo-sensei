import json
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_DIM = 1536
INDEX_FILE = "faiss.index"
META_FILE = "metadata.json"
TOP_K = 5  # Number of relevant docs to retrieve

# Load FAISS index and metadata
index = faiss.read_index(INDEX_FILE)
with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

def embed_text(text: str) -> np.ndarray:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32)
    return embedding

def retrieve_offers(query: str):
    query_vec = embed_text(query)
    D, I = index.search(np.array([query_vec]), TOP_K)
    results = [metadata[i] for i in I[0] if i < len(metadata)]
    return results

def build_context_text(offers):
    texts = []
    for offer in offers:
        texts.append(f"Title: {offer['title']}\nDescription: {offer['description']}\nBrand: {offer['brand']}\nExpiry: {offer['expiry']}\nLink: {offer['link']}\n")
    return "\n\n".join(texts)

def generate_answer(query: str):
    relevant_offers = retrieve_offers(query)
    context = build_context_text(relevant_offers)

    system_prompt = (
        "You are Promo Sensei, a helpful assistant that provides details about current promotional offers. "
        "Use the following offers as context to answer the user's question."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    user_query = input("Enter your promo query: ")
    answer = generate_answer(user_query)
    print("\nPromoSensei says:\n", answer)
