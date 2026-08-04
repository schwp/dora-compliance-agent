from ingestion.chunker import parse_directory
from rag.embedding import VectorStore
from rag.generator import Generator
from rag.retriever import HybridRetriever

if __name__ == "__main__":
    chunks = parse_directory("./data/raw/cssf")
    print(len(chunks))

    store = VectorStore()
    store.index(chunks, reset=True)

    retriever = HybridRetriever(store)
    generator = Generator()

    for question in [
        "When must the register of information be submitted?",
        "Who is the cloud officer?",
        "What are the deadlines for reporting a major ICT incident?",
    ]:
        print(f"\nQ: {question}")
        chunks = retriever.search(question, top_k=4)

        print("A: ", end="", flush=True)
        for piece in generator.stream(question, chunks):
            print(piece, end="", flush=True)
        print()
