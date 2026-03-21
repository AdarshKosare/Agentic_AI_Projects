from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vectorstore import add_documents, search
from config import settings

def chunk_text(text: str):
    """
    Split a long document into overlapping chunks.
    chunk_size = max character per chunk
    chunk_overlap = charcters shared  between adjacent chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = settings.chunk_size,
        chunk_overlap = settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)

def ingest_text(text:str, source: str = "manual") -> int:
    """
    Chunk a document and store all chunks in ChromaDB.
    Returns number of chunks stored.
    """

    chunks = chunk_text(text)
    ids = [f"{source}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]

    add_documents(
        texts=chunks,
        ids=ids,
        metadatas=metadatas,
    )

    return len(chunks)

def ingest_file(filepath: str) -> int:
    """
    Read a text file and ingest it into ChromaDB.
    """

    with open(filepath,"r",encoding="utf=8") as f:
        text = f.read()

    source = filepath.split("\\")[-1].split[-1]
    return ingest_text(text, source=source)

def query_knowledge_base(query: str, n_results: int = 3) -> str:
    """
    Search ChromaDB and return formatted context string.
    This is what gets injected into the LLM context window.
    """
    results = search(query, n_results=n_results)

    if not results:
        return "No relevant documents found."

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {r['metadata'].get('source', 'unknown')}]\n{r['text']}"
        )

    return "\n\n---\n\n".join(context_parts)
