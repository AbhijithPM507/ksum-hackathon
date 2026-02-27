import sys
import os
sys.path.append(os.path.abspath("."))

from data_layer.vector_db.query import query_legal_context

query = "Officer demanded bribe for land approval."

docs =query_legal_context(query)

print("Retrieved Documents:")
print(docs)