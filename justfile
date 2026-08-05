default:
    @just -l

eval TYPE:
    @uv run python3 -m scripts.eval_{{TYPE}}

populate:
    @uv run python3 -m scripts.populate_chromadb

run-app UI="streamlit":
    @uv run python3 {{ if UI == "streamlit" { "-m streamlit run src/app.py" } else { "src/app.py" } }}

test:
    @uv run pytest
