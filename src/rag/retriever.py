import re
from dataclasses import dataclass
from typing import Optional

from rank_bm25 import BM25Okapi

from .embedding import VectorStore


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    citation: str
    chapter: str
    section: str
    score: float
    dense_rank: Optional[int]
    sparse_rank: Optional[int]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class HybridRetriever:
    def __init__(self, store: VectorStore, rff_k: int = 60):
        self.store = store
        self.rff_k = rff_k

        self._chunk_ids: list[str] = []
        self._chunks_by_id: dict[str, dict] = {}
        self._bm25: Optional[BM25Okapi] = None
        self._build_indexer()

    def _build_indexer(self):
        all = self.store.collection.get(include=["metadatas"])

        ids = all["ids"]
        metadatas = all["metadatas"]

        corpus = []
        for chunk_id, meta in zip(ids, metadatas):
            self._chunk_ids.append(chunk_id)
            self._chunks_by_id[chunk_id] = meta
            corpus.append(_tokenize(meta.get("raw_text", "")))

        self._bm25 = BM25Okapi(corpus)

    def search(self, question: str, top_k: int = 5) -> list[RetrievedChunk]:
        """
        Search for the top-k chunks that best match the given question.

        Args:
            question: The search query question.
            top_k: The number of top results to return.

        Returns:
            A list of RetrievedChunk objects, sorted by score in descending order.
        """
        dense = self._dense_search(question, top_k)
        sparse = self._sparse_search(question, top_k)
        fused = self._fuse(dense, sparse)

        top_fused = sorted(fused, key=lambda idx: fused[idx], reverse=True)[:top_k]

        results = []
        for chunk_id in top_fused:
            meta = self._chunks_by_id[chunk_id]
            results.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=meta.get("raw_text", ""),
                    citation=meta.get("citation", ""),
                    chapter=meta.get("chapter", ""),
                    section=meta.get("section", ""),
                    score=fused[chunk_id],
                    dense_rank=dense.get(chunk_id),
                    sparse_rank=sparse.get(chunk_id),
                )
            )
        return results

    def _dense_search(self, question: str, nb_results: int = 5) -> dict[str, int]:
        hits = self.store.query(question=question, nb_results=nb_results)
        return {hit["chunk_id"]: rank for rank, hit in enumerate(hits, start=1)}

    def _sparse_search(self, question: str, nb_results: int = 5) -> dict[str, int]:
        scores = self._bm25.get_scores(_tokenize(question))

        ranked = sorted(zip(self._chunk_ids, scores), key=lambda p: p[1], reverse=True)

        return {
            chunk_id: rank
            for rank, (chunk_id, score) in enumerate(ranked[:nb_results], start=1)
            if score > 0
        }

    def _fuse(self, dense: dict[str, int], sparse: dict[str, int]) -> dict[str, float]:
        fused = {}

        for element in (dense, sparse):
            for chunk_id, score in element.items():
                fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (self.rff_k + score)

        return fused
