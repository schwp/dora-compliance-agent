from ingestion.chunker import parse_directory
from rag.embedding import VectorStore
from rag.retriever import HybridRetriever

if __name__ == "__main__":
    chunks = parse_directory("./data/raw/cssf")
    print(len(chunks))

    store = VectorStore()
    store.index(chunks, reset=True)

    retriever = HybridRetriever(store)

    for question in [
        "When must the register of information be submitted?",
        "point 18 submission deadline",
        "who is the cloud officer",
        "aggregated reporting of major incidents",
    ]:
        print(f"\nQ: {question}")
        for h in retriever.search(question, top_k=3):
            print(
                f"  [{h.score:.4f}] {h.citation} | {h.section or h.chapter} "
                f"(dense={h.dense_rank or '-'}, sparse={h.sparse_rank or '-'})"
            )
            print(f"           {h.text[:80]!r}")
