# ============================================================
# core/uncertainty_engine.py
# v3: Epistemic status classification — pure Python, no LLM
# YES / TRY / UNKNOWN + uncertainty source
# ============================================================

import re
from core.concept_analyzer import ConceptAnalysis


# Uncertainty source types
SOURCES = {
    "disagreement": "Multiple traditions fundamentally disagree on this question.",
    "empirical_limitation": "This question lies beyond empirical verification.",
    "inherent_paradox": "This question contains an inherent paradox that resists resolution.",
    "ambiguity": "The question is genuinely ambiguous — different interpretations lead to different answers.",
    "model_limitation": "The system lacks sufficient data on this specific tradition or thinker.",
}

# Concept combinations that indicate empirically unanswerable questions
EMPIRICAL_LIMIT_CONCEPTS = [
    ({"consciousness", "death"}, "unknown"),    # afterlife / consciousness after death
    ({"soul", "death"}, "unknown"),             # soul survival
    ({"god", "existence"}, "try"),              # does god exist
    ({"consciousness", "god"}, "try"),          # divine consciousness
]

# Keyword patterns for empirically unanswerable questions
EMPIRICAL_LIMIT_PATTERNS = [
    (r"\bafter\s+(physical\s+)?death\b", "unknown"),
    (r"\bcontinue\s+after\b.*\b(death|die|dying)\b", "unknown"),
    (r"\bexist\s+after\b.*\b(death|die)\b", "unknown"),
    (r"\bafter\s+we\s+die\b", "unknown"),
    (r"\bbefore\s+(we\s+were\s+)?born\b", "try"),
    (r"\blife\s+after\s+death\b", "unknown"),
    (r"\bwhat\s+happens\s+when\s+we\s+die\b", "unknown"),
]


def classify_uncertainty(analysis: ConceptAnalysis,
                         confidence_signals: dict = None,
                         question: str = "") -> dict:
    """
    Classify epistemic status based on concept analysis and confidence signals.

    Returns: {
        "status": "yes" | "try" | "unknown",
        "source": str (key from SOURCES),
        "explanation": str
    }
    """
    confidence_signals = confidence_signals or {"strong": 0, "exploratory": 0}

    # Rule 1: Inherent paradox → unknown
    if analysis.is_paradox:
        return {
            "status": "unknown",
            "source": "inherent_paradox",
            "explanation": SOURCES["inherent_paradox"],
        }

    # Rule 2: High ambiguity → try
    if len(analysis.ambiguity_markers) >= 2:
        return {
            "status": "try",
            "source": "ambiguity",
            "explanation": SOURCES["ambiguity"],
        }

    # Rule 3: Compare intent → try (disagreement)
    if analysis.intent == "compare":
        return {
            "status": "try",
            "source": "disagreement",
            "explanation": SOURCES["disagreement"],
        }

    # Rule 4: Empirically unanswerable concept combinations
    concept_set = set(analysis.concepts)
    for required_concepts, status in EMPIRICAL_LIMIT_CONCEPTS:
        if concept_set >= required_concepts:
            return {
                "status": status,
                "source": "empirical_limitation",
                "explanation": SOURCES["empirical_limitation"],
            }

    # Rule 5: Empirically unanswerable keyword patterns (if question provided)
    if question:
        q_lower = question.lower()
        for pattern, status in EMPIRICAL_LIMIT_PATTERNS:
            if re.search(pattern, q_lower):
                return {
                    "status": status,
                    "source": "empirical_limitation",
                    "explanation": SOURCES["empirical_limitation"],
                }

    # Rule 6: Very deep questions → unknown
    if analysis.depth_score >= 0.8:
        return {
            "status": "unknown",
            "source": "empirical_limitation",
            "explanation": SOURCES["empirical_limitation"],
        }

    # Rule 7: Moderately deep → try
    if analysis.depth_score >= 0.6:
        return {
            "status": "try",
            "source": "disagreement",
            "explanation": SOURCES["disagreement"],
        }

    # Rule 8: More exploratory than strong signals → try
    if confidence_signals.get("exploratory", 0) > confidence_signals.get("strong", 0):
        return {
            "status": "try",
            "source": "ambiguity",
            "explanation": SOURCES["ambiguity"],
        }

    # Rule 9: No concepts matched (model limitation)
    if not analysis.concepts:
        return {
            "status": "try",
            "source": "model_limitation",
            "explanation": SOURCES["model_limitation"],
        }

    # Default: yes (confident)
    return {
        "status": "yes",
        "source": "",
        "explanation": "Philosophical traditions broadly converge on this topic.",
    }
