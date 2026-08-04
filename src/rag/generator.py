import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

from mistralai.client import Mistral
from mistralai.client.models import SystemMessage, UserMessage


@dataclass
class Answer:
    text: str
    citations: list[str]
    backend: str


class GeneratorBackend(ABC):
    @abstractmethod
    def generate(self, sys: str, user: str) -> Iterator[str]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class LocalBackend(GeneratorBackend):
    def __init__(self) -> None:
        raise NotImplementedError("LocalBackend(Generator) is not yet implemented")

    def generate(self, sys: str, user: str) -> Iterator[str]:
        yield from []

    @property
    def name(self) -> str:
        return "..."


class MistralBackend(GeneratorBackend):
    def __init__(self) -> None:
        model_name = os.getenv("AGENT_MODEL", None)
        api_key = os.getenv("MISTRAL_KEY", None)

        if model_name is None or model_name.strip() == "":
            raise ValueError(
                "MistralBackend(Generator): model_name must be provided and set in `.env`"
            )

        if api_key is None or api_key.strip() == "":
            raise ValueError(
                "MistralBackend(Generator): api_key must be provided and set in `.env`"
            )

        try:
            self._client = Mistral(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Mistral client: {e}")

        try:
            self._model = self._client.models.retrieve(model_id=model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to get Mistral model: {e}")

        self._model_name = model_name

    def generate(self, sys: str, user: str) -> Iterator[str]:
        messages = [SystemMessage(content=sys), UserMessage(content=user)]

        for chunk in self._client.chat.stream(
            model=self._model_name, messages=messages
        ):
            content = chunk.data.choices[0].delta.content
            if content and isinstance(content, str):
                yield content

    @property
    def name(self) -> str:
        return f"mistral:{self._model_name}"


def select_backend() -> GeneratorBackend:
    """
    Select the appropriate embedding backend based on the environment variables.

    Returns:
        GeneratorBackend: The selected generator backend.
    """
    embedding_backend = os.getenv("AGENT_BACKEND", None)

    if embedding_backend is None:
        raise ValueError(
            "Unknown AGENT_BACKEND: set it in `.env` by using 'local' or 'mistral'"
        )

    mistral_model = os.getenv("MISTRAL_MODEL", None)

    if embedding_backend == "mistral" and mistral_model is not None:
        return MistralBackend()
    return LocalBackend()


SYSTEM_PROMPT = """You are a DORA compliance assistant for Luxembourg financial \
entities regulated by the CSSF. You answer questions about CSSF circulars.

Rules you must follow:
1. Answer ONLY using the numbered sources provided. Do not use outside knowledge.
2. Cite every claim inline with the source's citation in square brackets, like \
"Financial entities must submit the register annually [Circular CSSF 25/882, pt. 17]."
3. If the sources do not contain the answer, say so plainly: "The provided sources \
do not cover this." Do not guess or invent requirements.
4. Be precise and concise. Use the regulation's own terms. Explain briefly when helpful.
5. When two circulars cover the same point, cite both."""


def _format_sources(chunks: list) -> str:
    """
    Turn the retrieved chunks into a numbered source list for the prompt.
    Each source shows its citation (so the model can reference it) and its text.
    Accepts RetrievedChunk objects or dicts.
    """
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        citation = getattr(chunk, "citation", None) or chunk.get("citation", "")
        text = getattr(chunk, "text", None) or chunk.get("text", "")
        blocks.append(f"[Source {i} — {citation}]\n{text.strip()}")
    return "\n\n".join(blocks)


def build_user_prompt(question: str, chunks: list) -> str:
    """Assemble the user turn: the sources, then the question."""
    sources = _format_sources(chunks)
    return (
        f"Sources:\n\n{sources}\n\n"
        f"---\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the sources above, with inline citations:"
    )


class Generator:
    def __init__(self) -> None:
        self._backend = select_backend()

    def stream(self, question: str, chunks: list) -> Iterator[str]:
        """
        Stream the answer piece by piece. If no chunks were retrieved, we don't
        call the model at all — there's nothing to ground an answer in.
        """
        if not chunks:
            yield "No relevant sources were found for this question."
            return

        user_prompt = build_user_prompt(question, chunks)
        yield from self._backend.generate(SYSTEM_PROMPT, user_prompt)

    def answer(self, question: str, chunks: list) -> Answer:
        """Collect the full streamed answer into one Answer object."""
        pieces = list(self.stream(question, chunks))
        citations = [
            getattr(c, "citation", None) or c.get("citation", "") for c in chunks
        ]
        return Answer(
            text="".join(pieces),
            citations=citations,
            backend=self._backend.name,
        )
