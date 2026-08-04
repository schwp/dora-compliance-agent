from src.ingestion.chunker import parse_directory
from src.rag.embedding import VectorStore

if __name__ == "__main__":
    chunks = parse_directory("./data/raw/cssf")

    store = VectorStore()
    store.index(chunks, reset=True)
