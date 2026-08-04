import re
from dataclasses import dataclass, field

from src.ingestion.chunker import parse_directory
from src.rag.embedding import VectorStore
from src.rag.retriever import HybridRetriever


@dataclass
class EvalCase:
    query: str
    expect_circulars: list[str]
    section_hint: str = ""
    note: str = ""


EVALUATION_CASES = [
    # Register of information (25/882)
    EvalCase(
        query="When must the register of information be submitted?",
        expect_circulars=["25/882"],
        section_hint="Register of information",
        note="Core 25/882 content - submission deadline.",
    ),
    EvalCase(
        query="What must the register of information contain?",
        expect_circulars=["25/882"],
        section_hint="Register of information",
    ),
    EvalCase(
        query="Can the CSSF request the register outside the submission period?",
        expect_circulars=["25/882"],
        note="Point 20 — CSSF may request at any time.",
    ),
    # Incident reporting (25/893)
    EvalCase(
        query="What are the deadlines for reporting a major ICT incident?",
        expect_circulars=["25/893"],
        section_hint="notification",
        note="25/893 is the incident-notification circular.",
    ),
    EvalCase(
        query="Is aggregated reporting of major incidents permitted?",
        expect_circulars=["25/893"],
        note="25/893 states no aggregated report is permitted.",
    ),
    EvalCase(
        query="How should a major ICT incident be classified?",
        expect_circulars=["25/893"],
    ),
    # Cloud officer (25/882 and 22/806)
    EvalCase(
        query="Who is the cloud officer and what are their responsibilities?",
        expect_circulars=["25/882", "22/806"],
        section_hint="loud officer",
        note="Defined in BOTH circulars - either is an acceptable top hit.",
    ),
    # Cost estimation (25/892)
    EvalCase(
        query="How should aggregated annual costs of ICT incidents be estimated?",
        expect_circulars=["25/892"],
        note="25/892 - cost/loss estimation. Tests the annex strip worked.",
    ),
    EvalCase(
        query="What reporting template is used for annual costs and losses?",
        expect_circulars=["25/892"],
    ),
    # Outsourcing (22/806)
    EvalCase(
        query="What are the requirements for intragroup outsourcing?",
        expect_circulars=["22/806"],
        section_hint="Intragroup",
    ),
    EvalCase(
        query="When is an arrangement considered outsourcing to a cloud provider?",
        expect_circulars=["22/806"],
    ),
    # Third-party ICT / scope (25/882)
    EvalCase(
        query="What are the rules for using a third party for ICT operations?",
        expect_circulars=["25/882"],
    ),
    EvalCase(
        query="What backup of accounting positions is required?",
        expect_circulars=["25/882"],
        note="25/882 Sub-chapter 1.3.",
    ),
    #  Cross-circular / general
    EvalCase(
        query="What must be notified to the CSSF before a contractual arrangement?",
        expect_circulars=["25/882"],
        note="Point 11-13 - notification of planned arrangements.",
    ),
]


@dataclass
class CaseResult:
    query: str
    hit: bool
    rank: int | None
    reciprocal_rank: float
    top_citations: list[str] = field(default_factory=list)


def _circular_of(citation: str) -> str:
    m = re.search(r"(\d{2}/\d{3})", citation or "")
    return m.group(1) if m else ""


def evaluate(retriever: HybridRetriever, cases: list[EvalCase], top_k: int = 3) -> dict:
    """Run every case, return metrics + per-case detail."""
    results = []

    for case in cases:
        hits = retriever.search(case.query, top_k=top_k)
        citations = [h.citation for h in hits]

        rank = None
        for i, h in enumerate(hits, start=1):
            if _circular_of(h.citation) in case.expect_circulars:
                rank = i
                break

        results.append(
            CaseResult(
                query=case.query,
                hit=rank is not None,
                rank=rank,
                reciprocal_rank=(1.0 / rank) if rank else 0.0,
                top_citations=citations,
            )
        )

    n = len(results)
    hit_at_k = sum(r.hit for r in results) / n
    mrr = sum(r.reciprocal_rank for r in results) / n

    return {"hit_at_k": hit_at_k, "mrr": mrr, "top_k": top_k, "results": results}


def print_report(report: dict, cases: list[EvalCase]) -> None:
    k = report["top_k"]
    print("=" * 66)
    print(
        f"Retrieval eval  -  Hit@{k} = {report['hit_at_k']:.0%}   MRR = {report['mrr']:.3f}"
    )
    print("=" * 66)

    for case, r in zip(cases, report["results"]):
        mark = "OK " if r.hit else "MISS"
        rank = f"rank {r.rank}" if r.rank else "not found"
        print(f"[{mark}] {rank:11s} | {case.query[:52]}")
        if not r.hit:
            print(f"        expected {case.expect_circulars}, got:")
            for c in r.top_citations:
                print(f"          - {c}")

    misses = [c.query for c, r in zip(cases, report["results"]) if not r.hit]
    if misses:
        print(f"\n{len(misses)} miss(es) to investigate.")
    else:
        print("\nAll cases passed.")


if __name__ == "__main__":
    chunks = parse_directory("./data/raw/cssf")
    store = VectorStore()
    store.index(chunks, reset=True)

    retriever = HybridRetriever(store)

    report = evaluate(retriever, EVALUATION_CASES, top_k=3)
    print_report(report, EVALUATION_CASES)
