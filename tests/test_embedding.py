import pytest

from src.rag.embedding import LocalBackend, MistralBackend, select_backend


class TestEmbedding:
    def test_select_backend_local_success(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "local")
        monkeypatch.setenv("LOCAL_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        backend = select_backend()

        assert isinstance(backend, LocalBackend)
        assert backend.name == "local:sentence-transformers/all-MiniLM-L6-v2"

    def test_select_backend_local_failed_not_found(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "local")
        monkeypatch.setenv("LOCAL_MODEL", "test-user/test-model")

        with pytest.raises(Exception):
            _ = select_backend()

    def test_select_backend_mistral_success(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("MISTRAL_MODEL", "mistral-embed")

        backend = select_backend()

        assert isinstance(backend, MistralBackend)
        assert backend.name == "mistral:mistral-embed"

    def test_select_backend_mistral_not_set_with_local_fallback(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("LOCAL_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        monkeypatch.delenv("MISTRAL_MODEL", raising=False)

        backend = select_backend()

        assert isinstance(backend, LocalBackend)

    def test_select_backend_mistral_failed_not_found(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_BACKEND", "mistral")
        monkeypatch.setenv("MISTRAL_MODEL", "test-user/test-model")

        with pytest.raises(RuntimeError):
            _ = select_backend()

    def test_select_backend_embedding_backend_not_set(self, monkeypatch):
        monkeypatch.delenv("EMBEDDING_BACKEND", raising=False)

        with pytest.raises(ValueError):
            _ = select_backend()


class TestIndexing:
    def test_indexing(self):
        assert True


class TestRetrieval:
    def test_retrieval(self):
        assert True
