from pinecone import Pinecone
from data_layer.config import PINECONE_API_KEY, INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)