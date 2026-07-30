import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from dotenv import load_dotenv
from transformers import AutoTokenizer

load_dotenv()


@dataclass
class Chunk:
    chunk_id: str
    text: str
    document: str
    doc_type: str
    chapter: Optional[str]
    section: Optional[str]
    article: Optional[str]
    paragraph: Optional[str]
    citation: str

    def __str__(self) -> str:
        return (
            f"Chunk(chunk_id={self.chunk_id}, document={self.document}, "
            + f"chapter={self.chapter}, section={self.section}, text={self.text[:80]})"
        )


def _find_circular_reference(headings: list[str], filename: str) -> str:
    if headings:
        match = re.search(r"(\d{2}/\d{3})", headings[0])
        if match:
            return match.group(1)

    match = re.search(r"(\d{2})[_/](\d{3})", filename)
    if match:
        return f"{match.group(1)}/{match.group(2)}"

    return "unknown"


def _find(headings: list[str], keyword: str) -> str | None:
    return next((h for h in headings if keyword in h), None)


def _get_cssf_chunks(path: Path, converter: DocumentConverter) -> list[Chunk]:
    doc = converter.convert(path).document

    if os.getenv("EMBEDDING_BACKEND") == "local":
        chunker = HybridChunker(
            tokenizer=HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(os.getenv("LOCAL_MODEL")),
                max_tokens=450,
            ),
            merge_peers=True,
        )
    else:
        chunker = HybridChunker(merge_peers=True, max_tokens=450)

    chunks = []

    for chunk in chunker.chunk(dl_doc=doc):
        text = chunk.text
        heading = chunk.meta.headings or []

        if "TABLE OF CONTENTS" in heading:
            continue

        ref = _find_circular_reference(heading, path.name)
        points = re.compile(r"^(\d{1,3})\.\s(?!\d)", re.M).findall(text)
        chapter = _find(heading, "Chapter")
        section = _find(heading, "Sub-chapter")

        c = Chunk(
            chunk_id=uuid.uuid4().hex,
            text=text,
            document=path.name,
            doc_type="circular",
            chapter=chapter,
            section=section,
            article=chapter or section,
            paragraph=points[0] if points else None,
            citation=f"Circular CSSF {ref}",
        )

        chunks.append(c)

    return chunks


def _determine_doc_type(filename: str) -> str:
    if "cssf" in filename.lower():
        return "cssf"
    return "circular"


def get_chunks(filename: str, converter: DocumentConverter) -> list[Chunk]:
    """
    Parse the given PDF file and return the chunks of that document based on its type.

    Args:
        filename (str): Path to the PDF file.
        converter (DocumentConverter): The converter to use for parsing the PDF.

    Returns:
        list[Chunk]: A list of all chunks extracted from the PDF file.
    """
    chunks = []
    path = Path(filename)

    doc_type = _determine_doc_type(filename)

    if doc_type in ("cssf", "circular"):
        chunks = _get_cssf_chunks(path, converter)

    return chunks


def parse_directory(directory: str) -> list[Chunk]:
    """
    Parse all PDF files in the given directory and return the chunks of those documents.

    Args:
        directory (str): Path to the directory containing PDF files.

    Returns:
        list[Chunk]: A list of all chunks extracted from the PDF files.
    """
    input_path = Path(directory)
    converter = DocumentConverter()

    all_chunks = []

    for pdf in sorted(input_path.glob("*.pdf")):
        chunks = get_chunks(str(pdf), converter)
        all_chunks.extend(chunks)

    return all_chunks
