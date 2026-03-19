# ============================================================
# core/system_awareness.py
# v3: Meta-cognition layer — pure Python, no LLM
# Generates one-sentence observation about HOW the system
# approached the question. Shown only for deep questions.
# ============================================================

from core.concept_analyzer import ConceptAnalysis


def generate_meta_observation(analysis: ConceptAnalysis,
                              uncertainty_status: str = "",
                              uncertainty_source: str = "") -> str:
    """
    Generate a one-sentence meta-cognitive observation.
    Only meaningful for deep questions (depth_score >= 0.6).
    Returns empty string for shallow questions.
    """
    if analysis.depth_score < 0.6:
        return ""

    # Paradox path
    if analysis.is_paradox:
        if analysis.paradox_type == "existential":
            return "I chose to illuminate the paradox rather than resolve it — some tensions are more honest when held open."
        if analysis.paradox_type == "moral":
            return "I held the moral tension without collapsing it into a simple answer — ethical paradoxes deserve that respect."
        if analysis.paradox_type == "logical":
            return "I traced the logical contradiction to its root rather than arguing past it."
        return "I chose to name the paradox rather than pretend to resolve it."

    # Unknown status path
    if uncertainty_status == "unknown":
        if uncertainty_source == "empirical_limitation":
            return "I am approaching the boundary of what structured thinking can reach — beyond here lies contemplation, not analysis."
        if uncertainty_source == "inherent_paradox":
            return "I reached a point where the question itself resists any single coherent answer."
        return "I acknowledge the limits of what I can confidently say here."

    # Multi-flow path
    if analysis.multi_flow:
        if analysis.intent == "compare":
            return "I gave each perspective its strongest voice before looking for where they converge and where they genuinely clash."
        if len(analysis.concepts) >= 3:
            return "I traced the intersections between these ideas rather than treating them separately."
        return "The complexity of this question required holding multiple threads simultaneously."

    # Try status path
    if uncertainty_status == "try":
        return "I offered directions rather than destinations — this question rewards continued exploration."

    # Deep exploration
    if analysis.depth_score >= 0.7:
        return "I went beneath the surface question to find what it is really asking."

    return "I approached this with both rigor and openness to what the traditions actually say."
