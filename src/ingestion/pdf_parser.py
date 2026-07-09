import re
from pathlib import Path

from docling.document_converter import DocumentConverter

FOOTNOTE_STARTERS = (
    r"Regulation|ICT services|Reference|The types|The aim|In line|In cases|"
    r"Indeed|Commission|A\s+physical|For the sake|The CSSF relies"
)

def _clean_markdown(text: str) -> str:
    text = re.sub(r"^<!--\s*image\s*-->\s*$", "", text, flags=re.MULTILINE)

    intro = re.search(
        r"^(As of \d{1,2} \w+ \d{4}.*?)(?=^##\s+TABLE OF CONTENTS|^##\s+Chapter\s+1)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    first_chapter = re.search(r"^##\s+Chapter\s+1\s*:", text, re.MULTILINE)

    if first_chapter:
        preamble = ""
        if intro:
            intro_text = intro.group(1).strip()
            intro_text = re.sub(
                rf"^\d{{1,2}}\s{{1,3}}(?:{FOOTNOTE_STARTERS}).*$",
                "",
                intro_text,
                flags=re.MULTILINE,
            )
            intro_text = re.sub(r"\n{3,}", "\n\n", intro_text).strip()
            preamble = f"## CSSF Circular 25/882\n\n{intro_text}\n\n"
        text = preamble + text[first_chapter.start():]

    text = re.sub(
        r"^##\s+TABLE OF CONTENTS\s*$.*?(?=^##\s+Chapter)",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    text = re.sub(r"^\|.*\.{5,}.*\|\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\|[-|\s]+\|\s*$\n(?=\s*$)", "", text, flags=re.MULTILINE)

    text = re.sub(
        rf"^\d{{1,2}}\s{{1,3}}(?:{FOOTNOTE_STARTERS}).*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(r"^\[\d{1,2}\s+.*?\]\(https?://[^)]+\)\s*$", "", text, flags=re.MULTILINE)

    text = re.sub(r"^Claude WAMPACH.*", "", text, flags=re.DOTALL | re.MULTILINE)

    text = re.sub(r"^-\s+([a-z][\)\.]\s)", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r"^-\s+([ivx]+[\)\.]\s)", r"\1", text, flags=re.MULTILINE)

    def _strip_superscripts(line: str) -> str:
        if line.lstrip().startswith(("#", "|", "-")):
            return line

        m = re.match(r"^(\d{1,3}\.\s+)(.*)$", line)
        prefix, body = (m.group(1), m.group(2)) if m else ("", line)

        body = re.sub(r"(?<=[a-z\)\'\"])\s+\d{1,2}\s*(?=[:;,.])", "", body)
        body = re.sub(r"(?<=[a-z])\s+\d{1,2}\s{2,}(?=[a-z])", " ", body)
        body = re.sub(r"(?<=[a-z\)\'\"])\s+\d{1,2}\s*$", "", body)

        return prefix + body

    text = "\n".join(_strip_superscripts(ln) for ln in text.split("\n"))

    text = "\n".join(
        ln if ln.lstrip().startswith("|") else re.sub(r"[ \t]{2,}", " ", ln)
        for ln in text.split("\n")
    )

    text = re.sub(r"^##\s+(\d+\.\d+\.\d+\.?)", r"#### \1", text, flags=re.MULTILINE)
    text = re.sub(r"^##\s+(Sub-chapter\s+\d+\.\d+\.?)", r"### \1", text, flags=re.MULTILINE)
    text = re.sub(r"^##\s+(Chapter\s+\d+\s*:)", r"## \1", text, flags=re.MULTILINE)

    text = text.replace("'", "'")

    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_pdf(path: str, converter: DocumentConverter) -> str:
    """
    Parse a PDF file and return the cleaned text as Markdown. It uses `pymupdf4llm`
    to extract text and applies a series of cleaning operations.

    Args:
        path (str): Path to the PDF file.
        converter (DocumentConverter): The document converter to use.

    Returns:
        str: The cleaned text as Markdown.
    """
    doc = converter.convert(path).document
    md_text = doc.export_to_markdown()
    text = _clean_markdown(str(md_text))
    return text


def parse_directory(directory: str, output: str) -> None:
    """
    Parse all PDF files in the given directory and save the output as Markdown files.

    Args:
        directory (str): Path to the directory containing PDF files.
        output (str): Path to the directory where Markdown files will be saved.
    """
    input_path = Path(directory)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    converter = DocumentConverter()

    for pdf in sorted(input_path.glob("*.pdf")):
        text = parse_pdf(str(pdf), converter)

        out_file = output_path / f"{pdf.stem}.md"
        out_file.write_text(text, encoding="utf-8")
