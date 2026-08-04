import pytest

from src.rag.embedding import LocalBackend as LocalEmbeddingBackend
from src.rag.embedding import MistralBackend as MistralEmbeddingBackend
from src.rag.embedding import select_backend as select_embedding_backend
from src.rag.generator import LocalBackend as LocalGeneratorBackend
from src.rag.generator import MistralBackend as MistralGeneratorBackend
from src.rag.generator import select_backend as select_generator_backend


class TestEmbeddingBackend:
    def test_select_backend_local_success(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "local")
        monkeypatch.setenv("LOCAL_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        backend = select_embedding_backend()

        assert isinstance(backend, LocalEmbeddingBackend)
        assert backend.name == "local:sentence-transformers/all-MiniLM-L6-v2"

    def test_select_backend_local_failed_not_found(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "local")
        monkeypatch.setenv("LOCAL_MODEL", "test-user/test-model")

        with pytest.raises(Exception):
            _ = select_embedding_backend()

    def test_select_backend_mistral_success(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("MISTRAL_MODEL", "mistral-embed")

        backend = select_embedding_backend()

        assert isinstance(backend, MistralEmbeddingBackend)
        assert backend.name == "mistral:mistral-embed"

    def test_select_backend_mistral_not_set_with_local_fallback(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("LOCAL_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        monkeypatch.delenv("MISTRAL_MODEL", raising=False)

        backend = select_embedding_backend()

        assert isinstance(backend, LocalEmbeddingBackend)

    def test_select_backend_mistral_failed_not_found(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("MISTRAL_MODEL", "test-user/test-model")

        with pytest.raises(RuntimeError):
            _ = select_embedding_backend()

    def test_select_backend_embedding_backend_not_set(self, monkeypatch):
        monkeypatch.delenv("EMBEDDING_BACKEND", raising=False)

        with pytest.raises(ValueError):
            _ = select_embedding_backend()


class TestGeneratorBackend:
    def test_select_backend_local_generator_success(self, monkeypatch):
        monkeypatch.setenv("AGENT_BACKEND", "local")
        monkeypatch.setenv("AGENT_MODEL", "...")

        with pytest.raises(NotImplementedError):
            backend = select_generator_backend()

        # This part must replace the NotImplementedError check when the local
        # generator implementation is available
        # assert isinstance(
        #     backend,
        #     LocalGeneratorBackend,
        # )

    def test_select_backend_mistral_generator_success(self, monkeypatch):
        monkeypatch.setenv("AGENT_BACKEND", "mistral")
        monkeypatch.setenv("AGENT_MODEL", "mistral-large-latest")

        backend = select_generator_backend()

        assert isinstance(
            backend,
            MistralGeneratorBackend,
        )

    def test_select_backend_mistral_generator_unknown(self, monkeypatch):
        monkeypatch.setenv("AGENT_BACKEND", "mistral")
        monkeypatch.setenv("AGENT_MODEL", "mistral-unknown")

        with pytest.raises(RuntimeError):
            _ = select_generator_backend()
