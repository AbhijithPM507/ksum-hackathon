from data_layer.vector_db.query import query_legal_context

results = query_legal_context("Is demanding bribe illegal?")

print(results)