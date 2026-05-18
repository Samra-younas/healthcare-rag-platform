import os
import requests
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# ── Pinecone Setup ────────────────────────────────────────
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "healthcare-rag"))

HF_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
HF_TOKEN = os.getenv("HF_TOKEN")

# ── Embedding ─────────────────────────────────────────────
def get_embedding(text: str) -> list:
    """Text ko 384-dim vector mein convert karo."""
    try:
        r = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": text},
            timeout=30
        )
        result = r.json()
        if isinstance(result, list) and isinstance(result[0], float):
            return result
        if isinstance(result, list) and isinstance(result[0], list):
            return result[0]
        return [0.0] * 384
    except Exception as e:
        print(f"Embedding error: {e}")
        return [0.0] * 384

# ── Search ────────────────────────────────────────────────
def search_medical_literature(query: str, top_k: int = 3) -> list:
    """
    Pinecone se relevant medical chunks dhundo.
    Returns top 3 relevant chunks.
    """
    try:
        # Query ko vector mein convert karo
        query_vector = get_embedding(query)

        # Pinecone search
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        # Chunks extract karo
        chunks = []
        for match in results.get("matches", []):
            meta = match.get("metadata", {})
            chunks.append({
                "score":   round(match.get("score", 0), 3),
                "text":    meta.get("text", ""),
                "source":  meta.get("source", "Unknown"),
            })

        if not chunks:
            return _mock_chunks(query)

        return chunks

    except Exception as e:
        print(f"Pinecone search error: {e}")
        return _mock_chunks(query)


def _mock_chunks(query: str) -> list:
    """Development ke liye fake chunks."""
    return [
        {
            "score": 0.89,
            "text": f"Medical literature about {query}: Treatment involves lifestyle changes and medication.",
            "source": "PubMed-2024-001"
        },
        {
            "score": 0.75,
            "text": f"Clinical guidelines for {query}: Regular monitoring is recommended.",
            "source": "WHO-Guidelines-2024"
        }
    ]


# Test karo
if __name__ == "__main__":
    results = search_medical_literature("diabetes treatment")
    for r in results:
        print(f"Score: {r['score']} | {r['text'][:80]}")