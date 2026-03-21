import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings
from rag.embedder import embed_text, embed_texts


# Singleton Client
_client = None
_collection = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
        )
    return _client

def get_collection(collection_name: str = "research_docs"):
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection

def add_documents(texts: list[str], ids: list[str], metadatas: list[dict] = None):
    """
    Store documents in Chromadb with their embeddings.
    texts - the actual text chunks
    ids - unique id for each chunk
    metadatas - optional dict per chunk (source, data, etc.)
    """

    collection = get_collection()
    embeddings = embed_texts(texts)

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas or [{"source": "unknown"} for _ in texts],
    )

    return len(texts)

def search(query: str, n_results: int = 5) -> list[dict]:
    """
    Search ChromaDB for documents similar to the query.
    Returns list of dicts with text, score and metadata.
    """
    collection =get_collection()
    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=n_results,
    )

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "text": doc,
            "score": results["distances"][0][i],
            "metadata": results["metadatas"][0][i],
            "id": results["ids"][0][i],
        })

    return output

def get_collection_count() -> int:
    """Returns number of document stored."""
    return get_collection().count()