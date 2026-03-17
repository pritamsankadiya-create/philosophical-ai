# ============================================================
# core/pipeline.py
# Central orchestrator — ties all cognitive stages together
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.thinking_engine import translate_hinglish, detect_language
from core.concept_analyzer import analyze_concepts
from core.knowledge_retriever import retrieve_with_question, format_context
from core.prompt_composer import compose_prompt
from core.reflection_engine import reflect
from models.llm_loader import generate_response, generate_stream


def _prepare(question: str, chat_memory=None):
    """
    Shared preparation: translate, detect language, analyze concepts,
    retrieve knowledge, compose prompt.
    Returns (prompt, analysis, translated, language).
    """
    # Stage 1: Language detection
    translated = translate_hinglish(question)
    language = detect_language(question)

    # Stage 2: Concept analysis
    analysis = analyze_concepts(question, language=language, translated=translated)

    # Stage 3: Knowledge retrieval
    results = retrieve_with_question(translated, analysis, chat_memory=chat_memory, top_k=3)
    context = format_context(results, max_items=6)

    # Get conversation history
    history = ""
    if chat_memory and not chat_memory.is_empty():
        history = chat_memory.get_history_as_text()

    # Stage 4: Prompt composition (reasoning + dialectic embedded)
    prompt = compose_prompt(question, translated, context, history, analysis)

    return prompt, analysis, translated, language


def run_pipeline(question: str, chat_memory=None, use_reflection: bool = True) -> str:
    """
    Full pipeline for /chat endpoint (2 LLM calls).
    Flow: prepare → generate → reflect → memory
    """
    prompt, analysis, translated, language = _prepare(question, chat_memory)

    # Stage 5: Draft answer (1 LLM call)
    answer = generate_response(prompt)

    # Stage 6: Reflection / self-check (1 LLM call)
    if use_reflection:
        answer = reflect(answer, question, analysis=analysis)

    # Stage 7: Save to memory with concepts
    if chat_memory is not None:
        chat_memory.add_message("user", question, concepts=analysis.concepts)
        chat_memory.add_message("ai", answer)

    return answer


def run_pipeline_stream(question: str, chat_memory=None):
    """
    Streaming pipeline for /stream endpoint (1 LLM call).
    Yields tokens for SSE streaming.
    Flow: prepare → stream → memory
    """
    prompt, analysis, translated, language = _prepare(question, chat_memory)

    # Stage 5: Stream answer (1 LLM call)
    full_answer = []

    for token in generate_stream(prompt):
        full_answer.append(token)
        yield token

    # Stage 7: Save to memory after stream completes
    if chat_memory is not None:
        chat_memory.add_message("user", question, concepts=analysis.concepts)
        chat_memory.add_message("ai", "".join(full_answer))


def get_pipeline_metadata(question: str):
    """
    Debug endpoint — returns analysis without LLM call.
    """
    translated = translate_hinglish(question)
    language = detect_language(question)
    analysis = analyze_concepts(question, language=language, translated=translated)

    return {
        "question": question,
        "translated": translated,
        "language": language,
        "concepts": analysis.concepts,
        "themes": analysis.themes,
        "philosophers": analysis.philosophers,
        "intent": analysis.intent,
        "question_depth": analysis.question_depth,
    }
