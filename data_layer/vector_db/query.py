from sentence_transformers import SentenceTransformer
from .pinecone_client import index

model = SentenceTransformer("all-MiniLM-L6-v2")

def query_legal_context(query_text: str, top_k: int = 3):
    query_vector = model.encode(query_text).tolist()

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    extracted_texts = [
        match["metadata"]["text"]
        for match in results["matches"]
    ]

    return extracted_texts