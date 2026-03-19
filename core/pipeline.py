# ============================================================
# core/pipeline.py
# v4: Active long-term memory — depth boost + context hints
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import asdict

from core.thinking_engine import translate_hinglish, detect_language
from core.concept_analyzer import analyze_concepts
from core.knowledge_retriever import retrieve_adaptive, format_layered_context
from core.flow_engine import build_flow_prompt, parse_flow_output, FlowTrace, _select_style_mode, _select_opening, _determine_answer_mode
from core.uncertainty_engine import classify_uncertainty
from core.system_awareness import generate_meta_observation
from core.response_synthesizer import synthesize_response, build_flow_trace_data
from core.reflection_engine import reflect_deep
from models.llm_loader import generate_response, generate_stream
from memory.long_term_memory import LongTermMemory


long_term_memory = LongTermMemory()
_flow_traces = []
MAX_TRACES = 50


def _store_trace(trace: FlowTrace):
    _flow_traces.append(trace)
    if len(_flow_traces) > MAX_TRACES:
        _flow_traces.pop(0)


def _prepare_v4(question: str, chat_memory=None):
    """
    v4 preparation: adds active long-term memory signals.
    Returns (context, history, analysis, translated, language, knowledge_results)
    Depth score is boosted for returning users on familiar concepts.
    """
    translated = translate_hinglish(question)
    language = detect_language(question)
    analysis = analyze_concepts(question, language=language, translated=translated)

    # v4: Active memory — boost depth score for returning explorers
    depth_boost = long_term_memory.get_depth_boost(analysis.concepts)
    if depth_boost > 0:
        analysis.depth_score = min(1.0, analysis.depth_score + depth_boost)
        print(f"📈 Depth boost applied: +{depth_boost:.2f} → {analysis.depth_score:.2f}")

    knowledge_results = retrieve_adaptive(translated, analysis, chat_memory=chat_memory, top_k=4)
    context = format_layered_context(knowledge_results)

    # v4: Inject long-term memory context hint into history
    history = ""
    if chat_memory and not chat_memory.is_empty():
        history = chat_memory.get_history_as_text()
        context_summary = chat_memory.get_context_summary()
        if context_summary:
            history += f"\n[Context: {context_summary}]"

    # v4: Add long-term context hint (tells LLM about user's depth)
    context_hint = long_term_memory.get_context_hint(analysis.concepts, language)
    if context_hint:
        context = context_hint + "\n\n" + context

    return context, history, analysis, translated, language, knowledge_results


# ─── Full pipeline (2 LLM calls) ─────────────────────────

def run_pipeline(question: str, chat_memory=None, use_reflection: bool = True) -> str:
    """v4 pipeline — active memory + soul identity."""
    context, history, analysis, translated, language, knowledge_results = \
        _prepare_v4(question, chat_memory)

    style_mode = _select_style_mode(analysis, question)
    opening_strategy = _select_opening(analysis, question)

    prompt = build_flow_prompt(question, translated, context, history, analysis)
    raw_answer = generate_response(prompt)

    flow_output = parse_flow_output(raw_answer)
    uncertainty = classify_uncertainty(analysis, flow_output["confidence_signals"], question=question)
    meta_observation = generate_meta_observation(
        analysis, uncertainty["status"], uncertainty.get("source", "")
    )
    answer = synthesize_response(flow_output, meta_observation, analysis.depth_score)

    trace = build_flow_trace_data(
        question, analysis, knowledge_results, flow_output,
        uncertainty, meta_observation,
        style_mode=style_mode, opening_strategy=opening_strategy
    )
    _store_trace(trace)
    long_term_memory.learn_from_question(analysis, trace)

    if use_reflection:
        answer = reflect_deep(answer, question, analysis=analysis, flow_trace=trace)

    if chat_memory is not None:
        chat_memory.add_message("user", question)
        chat_memory.add_message("ai", answer)
        chat_memory.update_context(
            question_type=analysis.question_type,
            concepts=analysis.concepts,
            emotional_intensity=getattr(analysis, 'emotional_intensity', ''),
            question=question,
        )

    return answer


# ─── Streaming pipeline (1 LLM call) ─────────────────────

def run_pipeline_stream(question: str, chat_memory=None):
    """v4 streaming pipeline."""
    context, history, analysis, translated, language, knowledge_results = \
        _prepare_v4(question, chat_memory)

    style_mode = _select_style_mode(analysis, question)
    opening_strategy = _select_opening(analysis, question)

    prompt = build_flow_prompt(question, translated, context, history, analysis)

    full_answer = []
    for token in generate_stream(prompt):
        full_answer.append(token)
        yield token

    raw_text = "".join(full_answer)
    flow_output = parse_flow_output(raw_text)
    uncertainty = classify_uncertainty(analysis, flow_output["confidence_signals"], question=question)
    meta_observation = generate_meta_observation(
        analysis, uncertainty["status"], uncertainty.get("source", "")
    )

    trace = build_flow_trace_data(
        question, analysis, knowledge_results, flow_output,
        uncertainty, meta_observation,
        style_mode=style_mode, opening_strategy=opening_strategy
    )
    _store_trace(trace)
    long_term_memory.learn_from_question(analysis, trace)

    if chat_memory is not None:
        chat_memory.add_message("user", question)
        chat_memory.add_message("ai", raw_text)
        chat_memory.update_context(
            question_type=analysis.question_type,
            concepts=analysis.concepts,
            emotional_intensity=getattr(analysis, 'emotional_intensity', ''),
            question=question,
        )


# ─── Debug / Metadata endpoints ──────────────────────────

def get_pipeline_metadata(question: str):
    translated = translate_hinglish(question)
    language = detect_language(question)
    analysis = analyze_concepts(question, language=language, translated=translated)

    # Show what active memory would add
    depth_boost = long_term_memory.get_depth_boost(analysis.concepts)
    boosted_depth = min(1.0, analysis.depth_score + depth_boost)

    style_mode = _select_style_mode(analysis, question)
    opening_strategy = _select_opening(analysis, question)

    return {
        "question": question,
        "translated": translated,
        "language": language,
        "concepts": analysis.concepts,
        "themes": analysis.themes,
        "philosophers": analysis.philosophers,
        "intent": analysis.intent,
        "question_depth": analysis.question_depth,
        "depth_score": analysis.depth_score,
        "depth_boost": depth_boost,
        "boosted_depth_score": boosted_depth,
        "is_paradox": analysis.is_paradox,
        "paradox_type": analysis.paradox_type,
        "multi_flow": analysis.multi_flow,
        "knowledge_mode": analysis.knowledge_mode,
        "ambiguity_markers": analysis.ambiguity_markers,
        "style_mode": style_mode,
        "opening_strategy": opening_strategy,
        "question_type": analysis.question_type,
        "answer_mode": str(_determine_answer_mode(analysis)),
        "emotional_intensity": getattr(analysis, 'emotional_intensity', ''),
        "context_hint": long_term_memory.get_context_hint(analysis.concepts, language),
        "detected_rasa": getattr(analysis, 'detected_rasa', ''),
        "rasa_intensity": getattr(analysis, 'rasa_intensity', ''),
        "rasa_target": getattr(analysis, 'rasa_target', ''),
    }


def get_latest_trace() -> dict:
    if not _flow_traces:
        return {"message": "No traces yet. Ask a question first."}
    return asdict(_flow_traces[-1])


def get_all_traces() -> list:
    return [asdict(t) for t in _flow_traces]