FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY --chown=user . .

ENV CHROMA_MODE=persistent \
    CHROMA_PATH=/home/user/app/data/vectordb \
    EMBEDDING_BACKEND=local \
    LOCAL_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    AGENT_BACKEND=mistral \
    AGENT_MODEL=mistral-large-latest

EXPOSE 7860
CMD ["streamlit", "run", "src/ui/streamlit_app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
