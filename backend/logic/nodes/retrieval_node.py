from data_layer.vector_db.query import query_legal_context

def retrieval_node(state):

    # 🔎 Vector search handled by Member 3
    docs = query_legal_context(state["complaint_text"])

    state["retrieved_docs"] = docs

    return state