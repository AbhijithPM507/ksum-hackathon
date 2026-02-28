from sentence_transformers import SentenceTransformer
from .pinecone_client import index

model = SentenceTransformer("all-MiniLM-L6-v2")

def upsert_chunks(chunks, source_name="legal_doc"):
    records = []

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        records.append({
            "id": f"{source_name}_{i}",
            "values": embedding,
            "metadata": {
                "source": source_name,
                "text": chunk
            }
        })

    index.upsert(records)
    print(f"Uploaded {len(records)} chunks to Pinecone.")