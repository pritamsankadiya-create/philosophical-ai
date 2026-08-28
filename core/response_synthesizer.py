# ============================================================
# core/response_synthesizer.py
# v3: Assembles final layered response + builds flow trace data
# ============================================================

from datetime import datetime, timezone
from core.concept_analyzer import ConceptAnalysis
from core.flow_engine import FlowTrace, _determine_answer_mode
from models.llm_loader import get_last_call_info


def synthesize_response(flow_output: dict, meta_observation: str = "",
                        depth_score: float = 0.0) -> str:
    """
    Assemble flow output + meta-observation (for deep questions only).
    Adaptive: if the insight is simple but deep, keep it minimal.
    """
    response = flow_output.get("response", "")

    # Add meta-observation only for deep questions
    if meta_observation and depth_score >= 0.6:
        response = response.rstrip()
        response += f"\n\n_{meta_observation}_"

    return response


def _classify_insight_type(analysis: ConceptAnalysis, confidence_signals: dict) -> str:
    """Classify insight as convergent, divergent, or paradoxical."""
    if analysis.is_paradox:
        return "paradoxical"
    if analysis.intent == "compare":
        return "divergent"
    if confidence_signals.get("exploratory", 0) > confidence_signals.get("strong", 0):
        return "divergent"
    return "convergent"


def build_flow_trace_data(question: str, analysis: ConceptAnalysis,
                          knowledge_results: dict, flow_output: dict,
                          uncertainty: dict, meta_observation: str,
                          style_mode: str = "", opening_strategy: str = "",
                          contract_type: str = "", contract_violations: dict = None,
                          prajna_hint: str = "") -> FlowTrace:
    """
    Build complete trace dict with all analysis, knowledge layers,
    confidence signals, uncertainty, meta-observation, and timestamp.
    """
    confidence = flow_output.get("confidence_signals", {"strong": 0, "exploratory": 0})
    insight_type = _classify_insight_type(analysis, confidence)

    # Count knowledge items per layer
    knowledge_layers = {}
    for layer in ["philosophical", "scientific", "experiential"]:
        knowledge_layers[layer] = len(knowledge_results.get(layer, []))

    # Get model info from the most recent LLM call
    call_info = get_last_call_info()

    trace = FlowTrace(
        question=question,
        language=analysis.language,
        depth_score=analysis.depth_score,
        knowledge_mode=analysis.knowledge_mode,
        is_paradox=analysis.is_paradox,
        paradox_type=analysis.paradox_type,
        multi_flow=analysis.multi_flow,
        intent=analysis.intent,
        style_mode=style_mode,
        opening_strategy=opening_strategy,
        concepts=analysis.concepts,
        philosophers=analysis.philosophers,
        themes=analysis.themes,
        ambiguity_markers=analysis.ambiguity_markers,
        knowledge_layers=knowledge_layers,
        confidence_signals=confidence,
        uncertainty_status=uncertainty.get("status", ""),
        uncertainty_source=uncertainty.get("source", ""),
        meta_observation=meta_observation,
        insight_type=insight_type,
        reflection_question=flow_output.get("reflection_question", ""),
        timestamp=datetime.now(timezone.utc).isoformat(),
        # v3
        question_type=analysis.question_type,
        answer_mode=str(_determine_answer_mode(analysis)),
        emotional_intensity=getattr(analysis, 'emotional_intensity', ''),
        # v3: Navarasa
        detected_rasa=getattr(analysis, 'detected_rasa', ''),
        rasa_intensity=getattr(analysis, 'rasa_intensity', ''),
        rasa_target=getattr(analysis, 'rasa_target', ''),
        # Model tracking
        model_used=call_info.get("model_used", ""),
        was_fallback=call_info.get("was_fallback", False),
        fallback_reason=call_info.get("fallback_reason", ""),
        # Prajna + Contract tracking
        prajna_hint=prajna_hint,
        contract_type=contract_type,
        contract_violations=contract_violations or {},
    )

    return trace
