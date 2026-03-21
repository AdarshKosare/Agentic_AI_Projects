from sentence_transformers import SentenceTransformer
from config import settings


_model = None


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> list[float]:
    model = get_embedder()
    embedding = model.encode(text)
    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    embeddings = model.encode(texts)
    return embeddings.tolist()