default:
    @just -l

eval TYPE:
    @uv run python3 -m scripts.eval_{{TYPE}}

populate:
    @uv run python3 -m scripts.populate_chromadb

run-app:
    @uv run python3 -m streamlit run src/app.py

test:
    @uv run pytest
