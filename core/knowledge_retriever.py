# ============================================================
# core/knowledge_retriever.py
# Multi-strategy knowledge retrieval using extracted concepts
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.vector_store import search_philosophy
from core.concept_analyzer import ConceptAnalysis


# Vague follow-up words (English, Hindi, Hinglish)
VAGUE_WORDS = [
    "it", "this", "that", "more", "about it",
    "tell me more", "explain", "elaborate",
    "continue", "and then", "so", "go deeper",
    "और बताओ", "समझाओ", "इसके बारे में",
    "यह", "इसे", "आगे", "बताओ",
    "aur batao", "batao", "samjhao", "aur",
]


def _is_vague(question: str) -> bool:
    lower = question.lower()
    return any(word in lower for word in VAGUE_WORDS)


def _resolve_vague_query(question: str, chat_memory) -> str:
    """Resolve vague follow-ups using chat memory context."""
    if not chat_memory or chat_memory.is_empty():
        return question

    if not _is_vague(question):
        return question

    last_topic = ""
    for msg in reversed(chat_memory.history):
        if msg["role"] == "user":
            last_topic = msg["content"]
            break

    if last_topic:
        return f"{question} {last_topic}"
    return question


def retrieve_knowledge(analysis: ConceptAnalysis, chat_memory=None, top_k: int = 3) -> list:
    """
    Multi-strategy search using extracted concepts.

    Strategy 1: Direct question search
    Strategy 2: Concept-enriched search
    Strategy 3: Philosopher-specific search (if mentioned)

    Returns deduplicated list of relevant quotes.
    """
    all_results = []
    seen = set()

    def _add_unique(results):
        for r in results:
            text = r.strip()
            if text and text not in seen:
                seen.add(text)
                all_results.append(text)

    # Strategy 1: Direct question search (existing behavior)
    # The question itself is passed through the pipeline,
    # we search with the resolved query
    # (caller provides the resolved query as first concept or via chat_memory)

    # Strategy 2: Concept-enriched search
    if analysis.concepts:
        concept_query = " ".join(analysis.concepts[:5])
        results = search_philosophy(concept_query, top_k=top_k)
        _add_unique(results)

    # Strategy 3: Philosopher-specific search
    if analysis.philosophers:
        for philosopher in analysis.philosophers[:2]:
            results = search_philosophy(philosopher, top_k=2)
            _add_unique(results)

    return all_results


def retrieve_with_question(question: str, analysis: ConceptAnalysis,
                           chat_memory=None, top_k: int = 3) -> list:
    """
    Full retrieval: resolves vague queries + multi-strategy search.
    """
    all_results = []
    seen = set()

    def _add_unique(results):
        for r in results:
            text = r.strip()
            if text and text not in seen:
                seen.add(text)
                all_results.append(text)

    # Strategy 1: Direct question search (with vague resolution)
    resolved = _resolve_vague_query(question, chat_memory)
    results = search_philosophy(resolved, top_k=top_k)
    _add_unique(results)

    # Strategy 2: Concept-enriched search
    if analysis.concepts:
        concept_query = " ".join(analysis.concepts[:5])
        results = search_philosophy(concept_query, top_k=top_k)
        _add_unique(results)

    # Strategy 3: Philosopher-specific search
    if analysis.philosophers:
        for philosopher in analysis.philosophers[:2]:
            results = search_philosophy(philosopher, top_k=2)
            _add_unique(results)

    return all_results


def format_context(results: list, max_items: int = 6) -> str:
    """Format search results into a prompt-ready string."""
    limited = results[:max_items]
    if not limited:
        return "No specific knowledge found."
    return "\n".join([f"- {r}" for r in limited])
