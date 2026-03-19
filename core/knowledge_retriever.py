# ============================================================
# core/knowledge_retriever.py
# v3: Adaptive 3-layer knowledge retrieval with reasoning seeds
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.vector_store import search_philosophy, search_by_layer
from core.concept_analyzer import ConceptAnalysis


# Vague follow-up words (English, Hindi, Hinglish)
VAGUE_WORDS = [
    # English
    "it", "this", "that", "more", "about it",
    "tell me more", "explain", "elaborate",
    "continue", "and then", "so", "go deeper",
    "what do you mean", "like what", "how so",
    # Hindi (Devanagari)
    "और बताओ", "समझाओ", "इसके बारे में",
    "यह", "इसे", "आगे", "बताओ",
    # Hinglish follow-up/clarification patterns
    "aur batao", "batao", "samjhao", "aur",
    "matlab", "matlab kya", "kya matlab",
    "ye kya", "yeh kya", "ye kaise",
    "kisse", "kiski", "kyu", "kyun", "kyon", "kaise",
    "ye baat", "yeh baat", "iska matlab", "kiski baat", "kisse ho rahi",
    "wo kya", "woh kya", "acha", "achha",
    "to phir", "lekin", "par", "lene dene",
]

# Layer weights by knowledge_mode
LAYER_WEIGHTS = {
    "abstract":    {"philosophical": 4, "scientific": 1, "experiential": 1},
    "grounded":    {"philosophical": 1, "scientific": 3, "experiential": 3},
    "conflicting": {"philosophical": 3, "scientific": 2, "experiential": 2},
    "balanced":    {"philosophical": 2, "scientific": 2, "experiential": 2},
}


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


def _generate_reasoning_seeds(analysis: ConceptAnalysis) -> list:
    """Generate mode-aware reasoning seeds that prime the LLM's cognitive direction."""
    seeds = []
    mode = analysis.knowledge_mode

    if mode == "abstract":
        seeds.append("Consider what lies beyond the observable — what can only be approached through contemplation.")
        if analysis.concepts:
            seeds.append(f"Examine the metaphysical nature of {analysis.concepts[0]}.")
    elif mode == "grounded":
        seeds.append("Ground this in lived human experience — what does this look like in actual life?")
        if analysis.concepts:
            seeds.append(f"How does {analysis.concepts[0]} manifest in daily practice?")
    elif mode == "conflicting":
        seeds.append("Hold the tension between opposing perspectives without premature resolution.")
        if analysis.is_paradox:
            seeds.append("Name the paradox clearly — which assumptions create the contradiction?")
    else:  # balanced
        seeds.append("Weave together philosophical depth with practical relevance.")

    if analysis.philosophers:
        names = " and ".join(analysis.philosophers[:2])
        seeds.append(f"What would {names} say about this?")

    return seeds


def retrieve_adaptive(question: str, analysis: ConceptAnalysis,
                      chat_memory=None, top_k: int = 4) -> dict:
    """
    v3: Adaptive 3-layer retrieval with mode-based weighting.
    Returns {"philosophical": [...], "scientific": [...], "experiential": [...], "reasoning_seeds": [...]}
    """
    resolved = _resolve_vague_query(question, chat_memory)
    mode = analysis.knowledge_mode
    weights = LAYER_WEIGHTS.get(mode, LAYER_WEIGHTS["balanced"])

    results = {"philosophical": [], "scientific": [], "experiential": [], "reasoning_seeds": []}
    seen = set()

    def _add_unique(layer: str, items: list):
        for item in items:
            content = item["content"].strip() if isinstance(item, dict) else item.strip()
            if content and content not in seen:
                seen.add(content)
                results[layer].append(content)

    for layer_name, weight in weights.items():
        if weight == 0:
            continue

        # Determine how many results per layer based on weight
        layer_k = max(2, min(top_k, weight + 1))

        # Strategy 1: Direct question search
        layer_results = search_by_layer(resolved, layer=layer_name, top_k=layer_k)
        _add_unique(layer_name, layer_results)

        # Strategy 2: Concept-enriched search
        if analysis.concepts:
            concept_query = " ".join(analysis.concepts[:5])
            layer_results = search_by_layer(concept_query, layer=layer_name, top_k=max(1, layer_k - 1))
            _add_unique(layer_name, layer_results)

        # Strategy 3: Philosopher-specific search (philosophical layer only)
        if layer_name == "philosophical" and analysis.philosophers:
            for philosopher in analysis.philosophers[:2]:
                layer_results = search_by_layer(philosopher, layer="philosophical", top_k=2)
                _add_unique("philosophical", layer_results)

    # Generate reasoning seeds
    results["reasoning_seeds"] = _generate_reasoning_seeds(analysis)

    return results


def format_layered_context(results: dict, max_per_layer: int = 4) -> str:
    """Format 3-layer results as structured text block for the prompt."""
    sections = []

    layer_labels = {
        "philosophical": "Philosophical Wisdom",
        "scientific": "Scientific Insights",
        "experiential": "Lived Experience",
    }

    for layer in ["philosophical", "scientific", "experiential"]:
        items = results.get(layer, [])[:max_per_layer]
        if items:
            label = layer_labels[layer]
            lines = "\n".join([f"  - {item}" for item in items])
            sections.append(f"[{label}]\n{lines}")

    # Add reasoning seeds
    seeds = results.get("reasoning_seeds", [])
    if seeds:
        seed_lines = "\n".join([f"  * {s}" for s in seeds])
        sections.append(f"[Reasoning Seeds]\n{seed_lines}")

    return "\n\n".join(sections) if sections else "No specific knowledge found."


# ─── Backward compatible functions ────────────────────────

def retrieve_knowledge(analysis: ConceptAnalysis, chat_memory=None, top_k: int = 3) -> list:
    """Legacy: multi-strategy search (backward compat)."""
    all_results = []
    seen = set()

    def _add_unique(items):
        for r in items:
            text = r.strip()
            if text and text not in seen:
                seen.add(text)
                all_results.append(text)

    if analysis.concepts:
        concept_query = " ".join(analysis.concepts[:5])
        results = search_philosophy(concept_query, top_k=top_k)
        _add_unique(results)

    if analysis.philosophers:
        for philosopher in analysis.philosophers[:2]:
            results = search_philosophy(philosopher, top_k=2)
            _add_unique(results)

    return all_results


def retrieve_with_question(question: str, analysis: ConceptAnalysis,
                           chat_memory=None, top_k: int = 3) -> list:
    """Legacy: full retrieval (backward compat)."""
    all_results = []
    seen = set()

    def _add_unique(items):
        for r in items:
            text = r.strip()
            if text and text not in seen:
                seen.add(text)
                all_results.append(text)

    resolved = _resolve_vague_query(question, chat_memory)
    results = search_philosophy(resolved, top_k=top_k)
    _add_unique(results)

    if analysis.concepts:
        concept_query = " ".join(analysis.concepts[:5])
        results = search_philosophy(concept_query, top_k=top_k)
        _add_unique(results)

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
