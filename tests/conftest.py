import os

import chromadb
import pytest


@pytest.fixture(scope="session")
def chroma_client():
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
    )
    return client


@pytest.fixture(scope="session")
def pdf_example():
    return "./data/raw/cssf25_880eng.pdf"
