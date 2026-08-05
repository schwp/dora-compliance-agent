import gradio as gr

from rag.embedding import VectorStore
from rag.generator import Generator
from rag.retriever import HybridRetriever

store = VectorStore()
retriever = HybridRetriever(store)
generator = Generator()


def respond(message: str, history: list):
    chunks = retriever.search(message, top_k=4)

    if not chunks:
        yield "I couldn't find anything relevant in the indexed circulars."
        return

    partial = ""
    for piece in generator.stream(message, chunks):
        partial += piece
        yield partial


demo = gr.ChatInterface(
    fn=respond,
    title="CSSF / DORA Compliance Assistant",
    description=(
        "Ask about CSSF circulars implementing DORA (Digital Operational "
        "Resilience Act) for Luxembourg financial entities. Answers are grounded "
        "in the circular text and cite the exact point numbers. Demo, not legal advice."
    ),
    examples=[
        "When must the register of information be submitted?",
        "Who is the cloud officer and what are their responsibilities?",
        "What are the deadlines for reporting a major ICT incident?",
        "What are the requirements for intragroup outsourcing?",
    ],
)


if __name__ == "__main__":
    demo.launch()
