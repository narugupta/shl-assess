"""
Offline Evaluation Harness
===========================

Replays the 10 provided gold conversation traces
(GenAI_SampleConversations/*.md) against the REAL pipeline
(planner + retriever + reasoner; the LLM call is stubbed so this
runs without network access / an API key) and scores:

  1. Hard evals   - schema compliance, catalog-only URLs, turn cap
  2. Recall@10    - against each trace's final gold shortlist
  3. Behavior probes - a few cheap, high-value checks:
       - no recommendation on turn 1 for a vague query
       - refuses an off-topic question
       - honors a mid-conversation refinement (doesn't reset
         the shortlist to something disjoint from what it had)

This is a *local* proxy for the real grading harness, not a
replacement for it: the real harness drives the conversation with
a simulated LLM user reacting to your actual replies, whereas this
script replays the exact wording from the gold transcripts. Wording
drift (a live user phrasing things differently) can change what the
planner extracts. Treat this as "are the wheels on" before you spend
API credits / deploy, not as your official score.

Usage
-----
    python scripts/evaluate_traces.py [path/to/GenAI_SampleConversations]

Requires GROQ_API_KEY to be set to *something* (any string) since
LLMGenerator reads it at construction time even though the actual
network call is stubbed out.
"""

from __future__ import annotations

import glob
import os
import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple
from unittest.mock import patch

os.environ.setdefault("GROQ_API_KEY", "offline-eval-placeholder")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ================================================================
# Trace parsing
# ================================================================

@dataclass
class TraceTurn:
    turn: int
    user: Optional[str]
    rows: List[Tuple[str, str]]   # (name, url)
    eoc: Optional[bool]


@dataclass
class Trace:
    trace_id: str
    turns: List[TraceTurn]

    @property
    def user_messages(self) -> List[str]:
        return [t.user for t in self.turns if t.user]

    @property
    def gold_shortlist(self) -> List[Tuple[str, str]]:
        with_rows = [t for t in self.turns if t.rows]
        return with_rows[-1].rows if with_rows else []


_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|.*?\|.*?\|.*?\|.*?\|\s*<?(https?://\S+?)>?\s*\|$",
    re.M,
)
_USER_RE = re.compile(r"\*\*User\*\*\s*\n+>\s*(.+?)(?:\n\n|\Z)", re.S)
_EOC_RE = re.compile(r"end_of_conversation.*?\*\*(true|false)\*\*", re.I)
_TURN_HEADER_RE = re.compile(r"^### Turn (\d+)\s*$", re.M)


def parse_trace(path: str) -> Trace:
    text = open(path, encoding="utf-8").read()

    blocks = _TURN_HEADER_RE.split(text)[1:]
    headers, bodies = blocks[0::2], blocks[1::2]

    turns = []

    for header, body in zip(headers, bodies):
        user_match = _USER_RE.search(body)
        user_msg = user_match.group(1).strip() if user_match else None

        rows = [(name.strip(), url.strip()) for _, name, url in _ROW_RE.findall(body)]

        eoc_match = _EOC_RE.search(body)
        eoc = eoc_match.group(1).lower() == "true" if eoc_match else None

        turns.append(TraceTurn(turn=int(header), user=user_msg, rows=rows, eoc=eoc))

    trace_id = os.path.splitext(os.path.basename(path))[0]

    return Trace(trace_id=trace_id, turns=turns)


# ================================================================
# Harness
# ================================================================

def build_pipeline():
    """
    Imports and constructs the real pipeline with the network-bound
    LLM call stubbed out. Recall@10 only depends on `recommendations`,
    which is built from retrieval, not from the LLM's prose - so this
    is a faithful test of retrieval/planner quality without needing
    Groq access.
    """
    from app.generation.response import GenerationResponse

    def fake_generate(self, prompt_type, query, context):
        return GenerationResponse(answer=f"[stub:{prompt_type.value}]")

    patcher = patch("app.generation.generator.LLMGenerator.generate", fake_generate)
    patcher.start()

    from app.api.pipeline import RecommendationPipeline

    return RecommendationPipeline()


def load_catalog_urls(pipeline) -> set:
    try:
        documents = pipeline.retriever.documents
        return {d.url for d in documents}
    except Exception:
        return set()


def replay(pipeline, trace: Trace, max_turns: int = 8):
    """
    Feeds the trace's user turns one at a time through pipeline.chat(),
    accumulating the (stateless) transcript exactly as the real
    evaluator would, and stops early if the agent commits to a
    shortlist (end_of_conversation) - same stopping rule as the real
    harness.
    """
    from app.api.models import ChatMessage, ChatRequest

    history = []
    turn_results = []

    for user_msg in trace.user_messages:

        if len(history) >= max_turns:
            break

        history.append({"role": "user", "content": user_msg})

        request = ChatRequest(
            messages=[ChatMessage(**h) for h in history]
        )

        response = pipeline.chat(request)

        turn_results.append(response)

        history.append({"role": "assistant", "content": response.reply})

        if response.end_of_conversation:
            break

    return turn_results, history


# ================================================================
# Scoring
# ================================================================

def name_key(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def recall_at_k(predicted: List[Tuple[str, str]], gold: List[Tuple[str, str]]) -> float:
    if not gold:
        return None

    gold_names = {name_key(n) for n, _ in gold}
    pred_names = {name_key(n) for n, _ in predicted}

    hits = len(gold_names & pred_names)

    return hits / len(gold_names)


def run():
    traces_dir = sys.argv[1] if len(sys.argv) > 1 else "GenAI_SampleConversations"

    paths = sorted(glob.glob(os.path.join(traces_dir, "*.md")))

    if not paths:
        print(f"No .md traces found under: {traces_dir}")
        return

    print("Building pipeline (real planner + retriever, LLM call stubbed)...")
    pipeline = build_pipeline()
    catalog_urls = load_catalog_urls(pipeline)
    print(f"Catalog loaded: {len(catalog_urls)} documents\n")

    recalls = []
    hard_fail_count = 0

    print(f"{'Trace':<8}{'Turns':<7}{'Recall@10':<12}{'HardEvals':<12}Notes")
    print("-" * 90)

    for path in paths:
        trace = parse_trace(path)
        gold = trace.gold_shortlist

        turn_results, history = replay(pipeline, trace)

        final = turn_results[-1] if turn_results else None
        predicted = [(r.name, r.url) for r in final.recommendations] if final else []

        # ---------------- Hard evals ----------------
        notes = []
        hard_pass = True

        if len(history) > 8:
            hard_pass = False
            notes.append(f"turn cap exceeded ({len(history)})")

        if catalog_urls:
            bad_urls = [u for _, u in predicted if u not in catalog_urls]
            if bad_urls:
                hard_pass = False
                notes.append(f"{len(bad_urls)} URL(s) not in catalog")

        for tr in turn_results:
            if not (0 <= len(tr.recommendations) <= 10):
                hard_pass = False
                notes.append("recommendations count outside [0,10]")

        if not hard_pass:
            hard_fail_count += 1

        # ---------------- Recall@10 ----------------
        recall = recall_at_k(predicted, gold)
        if recall is not None:
            recalls.append(recall)

        recall_str = f"{recall:.2f}" if recall is not None else "n/a"

        print(
            f"{trace.trace_id:<8}{len(history):<7}{recall_str:<12}"
            f"{'PASS' if hard_pass else 'FAIL':<12}{'; '.join(notes)}"
        )

        if recall is not None and recall < 1.0:
            gold_names = {name_key(n) for n, _ in gold}
            pred_names = {name_key(n) for n, _ in predicted}
            missing = gold_names - pred_names
            if missing:
                print(f"         missing from prediction: {sorted(missing)}")

    print("-" * 90)

    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0

    print(f"\nMean Recall@10 across {len(recalls)} traces: {mean_recall:.3f}")
    print(f"Hard eval failures: {hard_fail_count}/{len(paths)} traces")

    # ---------------- Behavior probes ----------------
    print("\nBehavior probes:")
    run_behavior_probes(pipeline)


def run_behavior_probes(pipeline):
    from app.api.models import ChatMessage, ChatRequest

    # Probe 1: vague first turn should NOT recommend
    resp = pipeline.chat(ChatRequest(messages=[
        ChatMessage(role="user", content="I need an assessment"),
    ]))
    ok = len(resp.recommendations) == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] no recommendation on vague turn-1 query")

    # Probe 2: off-topic should be refused, not answered
    resp = pipeline.chat(ChatRequest(messages=[
        ChatMessage(role="user", content="What's the weather like in Paris today?"),
    ]))
    ok = len(resp.recommendations) == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] refuses off-topic question")

    # Probe 3: refinement should extend, not discard, prior shortlist
    history = [
        {"role": "user", "content": "Hiring a mid-level Java developer"},
    ]
    r1 = pipeline.chat(ChatRequest(messages=[ChatMessage(**h) for h in history]))
    history.append({"role": "assistant", "content": r1.reply})
    if len(r1.recommendations) == 0:
        # planner asked a clarifying question first - answer it once
        history.append({"role": "user", "content": "3 to 5 years experience"})
        r1 = pipeline.chat(ChatRequest(messages=[ChatMessage(**h) for h in history]))
        history.append({"role": "assistant", "content": r1.reply})

    history.append({"role": "user", "content": "Actually, also add a personality assessment"})
    r2 = pipeline.chat(ChatRequest(messages=[ChatMessage(**h) for h in history]))

    before = {r.name for r in r1.recommendations}
    after = {r.name for r in r2.recommendations}
    overlap = before & after
    ok = len(before) > 0 and len(overlap) > 0 and len(after) >= len(before)
    print(f"  [{'PASS' if ok else 'FAIL'}] refinement keeps prior shortlist and extends it "
          f"(before={len(before)}, after={len(after)}, overlap={len(overlap)})")


if __name__ == "__main__":
    run()
