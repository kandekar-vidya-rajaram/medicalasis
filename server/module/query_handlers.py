def query_chain(chain, question):
    result = chain.invoke({"query": question})
    return {
        "response": result["result"],
        "sources": [
            document.metadata.get("source", "")
            for document in result.get("source_documents", [])
            if document.metadata.get("source")
        ],
    }