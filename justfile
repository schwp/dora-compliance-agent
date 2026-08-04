default:
    @just -l

eval TYPE:
    @uv run python3 -m scripts.eval_{{TYPE}}

test:
    @uv run pytest
