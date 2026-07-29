import os
from abc import ABC, abstractmethod
from dataclasses import asdict

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv
from mistralai.client import Mistral
from sentence_transformers import SentenceTransformer

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", None)
CHROMA_HOST = os.getenv("CHROMA_HOST", None)
CHROMA_PORT = os.getenv("CHROMA_PORT", None)


class EmbeddingBackend(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def output_dimension(self) -> int | None: ...


class LocalBackend(EmbeddingBackend):
    def __init__(self) -> None:
        model_name = os.getenv("LOCAL_MODEL", None)

        if model_name is None or model_name.strip() == "":
            raise ValueError(
                "LocalBackend: model_name must be provided and set in `.env`"
            )

        if os.getenv("HF_TOKEN") is None:
            raise ValueError(
                "LocalBackend: The local backend runs on Hugging Face models, so "
                "HF_TOKEN must be set in `.env` or in your environment"
            )

        self._model_name = f"local:{model_name}"
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts)
        return vectors.tolist()

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def output_dimension(self) -> int | None:
        return self._model.get_embedding_dimension()


class MistralBackend(EmbeddingBackend):
    def __init__(self) -> None:
        model_name = os.getenv("MISTRAL_MODEL", None)
        api_key = os.getenv("MISTRAL_KEY", None)

        if model_name is None or model_name.strip() == "":
            raise ValueError(
                "MistralBackend: model_name must be provided and set in `.env`"
            )

        if api_key is None or api_key.strip() == "":
            raise ValueError(
                "MistralBackend: api_key must be provided and set in `.env`"
            )

        try:
            self._client = Mistral(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Mistral client: {e}")

        try:
            self._model = self._client.models.retrieve(model_id=model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to get Mistral model: {e}")

        self._model_name = f"mistral:{model_name}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return []

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def output_dimension(self) -> int | None:
        return None


def select_backend() -> EmbeddingBackend:
    """
    Select the appropriate embedding backend based on the environment variables.

    Returns:
        EmbeddingBackend: The selected embedding backend.
    """
    embedding_backend = os.getenv("EMBEDDING_BACKEND", None)

    if embedding_backend is None:
        raise ValueError(
            "Unknown EMBEDDING_BACKEND: set it in `.env` by using 'local' or 'mistral'"
        )

    mistral_model = os.getenv("MISTRAL_MODEL", None)

    if embedding_backend == "mistral" and mistral_model is not None:
        return MistralBackend()
    return LocalBackend()


class _ChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, backend: EmbeddingBackend):
        self._backend = backend

    def __call__(self, input: Documents) -> Embeddings:
        return self._backend.embed(list(input))


def contextualize(chunk) -> str:
    data = chunk if isinstance(chunk, dict) else asdict(chunk)

    header_parts = [
        data.get("citation") or "",
        data.get("chapter") or "",
        data.get("section") or "",
    ]
    header = " | ".join(p for p in header_parts if p)
    text = data.get("text", "")
    return f"{header}\n{text}" if header else text


class Embedder:
    def __init__(
        self,
        collection_name: str | None = COLLECTION_NAME,
        host: str | None = CHROMA_HOST,
        port: str | None = CHROMA_PORT,
    ):
        if host is None or port is None:
            raise ValueError(
                "Embedder: ChromaDB host and port must be provided in the `.env` file"
            )

        self.client = chromadb.HttpClient(host=host, port=int(port))

        self.backend = select_backend()
        self._embed_fn = _ChromaEmbeddingFunction(self.backend)

        if collection_name is None or collection_name.strip() == "":
            raise ValueError(
                "Embedder: collection_name must be provided in the `.env` file"
            )

        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def index(self, chunks: list, batch_size: int = 100, reset: bool = False) -> int:
        """
        Index the given chunks into the collection.

        Args:
            chunks (list): The list of chunks to index.
            batch_size (int, optional): The batch size for upserting. Defaults to 100.
            reset (bool, optional): Whether to reset the collection before indexing. Defaults to False.

        Returns:
            int: The number of chunks indexed.
        """
        if reset:
            self._reset_collection()

        if not chunks or len(chunks) == 0:
            return 0

        ids, documents, metadatas = [], [], []

        for chunk in chunks:
            chunk_id, document, metadata = self._get_chunk_data(chunk)
            ids.append(chunk_id)
            documents.append(document)
            metadatas.append(metadata)

        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

        return len(ids)

    def _get_chunk_data(self, chunk) -> tuple[str, str, dict]:
        data = chunk if isinstance(chunk, dict) else asdict(chunk)

        document = contextualize(chunk)
        metadata = {
            "document": data.get("document", ""),
            "doc_type": data.get("doc_type", ""),
            "chapter": data.get("chapter") or "",
            "section": data.get("section") or "",
            "article": data.get("article") or "",
            "paragraph": data.get("paragraph") or "",
            "citation": data.get("citation", ""),
            "raw_text": data.get("text", ""),
        }
        return data["chunk_id"], document, metadata

    def _reset_collection(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def query(self, question: str, top_k: int = 5) -> list[dict]: ...

    def stats(self) -> dict:
        """
        Get the statistics of the collection.

        Returns:
            dict: A dictionary containing the backend, collection name, and count of items.
        """
        return {
            "backend": self.backend.name,
            "collection": self.collection.name,
            "count": self.collection.count(),
        }
