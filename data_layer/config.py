import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

# print("API KEY:", PINECONE_API_KEY)
# print("INDEX NAME:", INDEX_NAME)