from .document_loader import load_pdf
from .chunker import chunk_text
from .indexer import upsert_chunks

def setup_index():
    text = load_pdf("legal_docs/pca_act.pdf")
    chunks = chunk_text(text)
    upsert_chunks(chunks, source_name="pca_act")

if __name__ == "__main__":
    setup_index()