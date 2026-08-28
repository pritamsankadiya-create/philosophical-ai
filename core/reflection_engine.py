# ============================================================
# core/reflection_engine.py
# v3: Anti-repetition + soul check + paradox guard
# ============================================================

import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_loader import generate_fast, generate_response
from core.concept_analyzer import ConceptAnalysis
from core.flow_engine import FlowTrace


def detect_language(text: str) -> str:
    hindi_chars = set(
        'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'
        'ङञड़ढ़क्षत्रज्ञश्रफ़ज़'
    )
    count = sum(1 for c in text if c in hindi_chars)
    return 'hindi' if count > 2 else 'english'


def _count_sentences(text: str) -> int:
    return len([s for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 10])


def _detect_repetition(answer: str) -> bool:
    sentences = [s.strip() for s in answer.replace('\n', ' ').split('.') if len(s.strip()) > 20]
    if len(sentences) < 4:
        return False
    stop_words = {'the', 'a', 'an', 'is', 'it', 'in', 'of', 'to', 'and', 'that',
                  'this', 'we', 'you', 'not', 'but', 'for', 'are', 'was', 'has',
                  'have', 'with', 'from', 'our', 'your', 'can', 'be', 'do', 'as',
                  'or', 'at', 'by', 'on', 'if', 'its', 'so', 'me', 'my', 'they'}
    word_sets = []
    for s in sentences:
        words = {w.lower().strip('.,!?') for w in s.split()
                 if w.lower() not in stop_words and len(w) > 3}
        word_sets.append(words)

    repeat_count = 0
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            if len(word_sets[i] & word_sets[j]) >= 3:
                repeat_count += 1

    total_pairs = len(word_sets) * (len(word_sets) - 1) / 2
    return total_pairs > 0 and (repeat_count / total_pairs) > 0.35


def _detect_machine_disclaimer(answer: str) -> bool:
    lower = answer.lower()
    bad_phrases = [
        # English — LLaMA-style
        "i am a machine", "i am an ai", "i am a language model",
        "i am just", "i don't have feelings", "i don't have emotions",
        "as an ai", "i was trained", "i am a program",
        # English — GPT-style variants
        "i'm an ai", "i'm a language model", "i'm an artificial",
        "being a large language model", "as a chatbot",
        "as a language model", "i don't actually feel",
        "i lack consciousness", "i'm not sentient",
        "i should note that i'm", "i'm just a model",
        # Hindi
        "मैं एक मशीन", "मुझे भावनाएं नहीं", "एक ai के रूप में",
        "मैं एक भाषा मॉडल", "मैं एक कृत्रिम",
    ]
    return any(p in lower for p in bad_phrases)


def _detect_paradox_resolved(answer: str, analysis: ConceptAnalysis) -> bool:
    """Check if a paradox question got a cheap resolution."""
    if not (analysis and analysis.is_paradox):
        return False
    lower = answer.lower()
    resolution_signals = [
        "today you could", "you can try", "one step you can",
        "the answer is", "the solution is", "this resolves",
        "ultimately the answer", "in the end, the answer",
        "आज आप कर सकते", "इसका हल यह है"
    ]
    return any(s in lower for s in resolution_signals)


def _detect_monotone_rhythm(answer: str) -> list:
    """Detect 2+ sentences starting with the same first 2 words."""
    sentences = [s.strip() for s in re.split(r'[.।!?\n]', answer) if len(s.strip()) > 15]
    if len(sentences) < 3:
        return []

    starts = []
    for s in sentences:
        words = s.split()[:2]
        if len(words) >= 2:
            starts.append(' '.join(words).lower())

    from collections import Counter
    counts = Counter(starts)
    return [start for start, count in counts.items() if count >= 2]


def _build_flow_critique(analysis: ConceptAnalysis, flow_trace: FlowTrace = None) -> str:
    critiques = []
    intent = analysis.intent
    if intent == "define":
        critiques.append("Does it define with genuine depth or just repeat common knowledge?")
    elif intent == "compare":
        critiques.append("Does it give each view its strongest voice or subtly favor one?")
    elif intent == "apply":
        critiques.append("Does it give wisdom someone can actually use today, or just vague advice?")
    elif intent == "challenge":
        critiques.append("Does it steelman the opposing view before countering?")
    else:
        critiques.append("Does it explore with genuine depth or stay safely on the surface?")

    if analysis.is_paradox:
        critiques.append("Does it hold the paradox open honestly, or does it sneak in a resolution?")
    if analysis.depth_score >= 0.7:
        critiques.append("Is the tension genuine or manufactured for effect?")

    return " ".join(critiques[:3])


def reflect_deep(answer: str, question: str = "", analysis: ConceptAnalysis = None,
                 flow_trace: FlowTrace = None) -> str:
    """
    v3: Prioritized self-critique.
    1. Machine disclaimer check (remove immediately)
    2. Repetition check (cut duplicates)
    3. Paradox resolution check (reopen if resolved cheaply)
    4. Depth/quality critique
    Uses main model for deep questions, fast model for simple ones.
    """
    language = detect_language(question)
    has_repetition = _detect_repetition(answer)
    has_disclaimer = _detect_machine_disclaimer(answer)
    has_cheap_resolution = _detect_paradox_resolved(answer, analysis)
    rhythm_violations = _detect_monotone_rhythm(answer)

    flow_critique = ""
    if analysis is not None:
        flow_critique = _build_flow_critique(analysis, flow_trace)

    use_full_model = analysis is not None and analysis.depth_score >= 0.6

    # Build priority warnings
    warnings = []
    if has_disclaimer:
        warnings.append("🚫 CRITICAL: This response contains 'I am a machine/AI' or similar disclaimer. REMOVE IT ENTIRELY. Replace with honest philosophical uncertainty instead.")
    if has_repetition:
        warnings.append("🔁 CRITICAL: This response repeats the same idea multiple times in different words. Identify the repetition and CUT it — each sentence must add something new.")
    if has_cheap_resolution:
        warnings.append("⚠️ CRITICAL: This is a paradox question but the response sneaks in a resolution or action step at the end. REMOVE the resolution. The paradox must be held open.")
    if rhythm_violations:
        patterns = ", ".join(f'"{v}"' for v in rhythm_violations[:3])
        warnings.append(f"🔄 STRUCTURE: Multiple sentences start with the same pattern ({patterns}). Vary your sentence beginnings — use questions, metaphors, contradictions, direct claims.")

    warning_block = "\n".join(warnings) if warnings else ""

    if language == 'hindi':
        prompt = f"""तुम एक दार्शनिक आत्म-आलोचक हो।

{warning_block}

जाँचो:
1. क्या एक ही बात बार-बार दोहराई गई है? → काटो
2. क्या "मैं मशीन हूँ" जैसी कोई line है? → हटाओ
3. क्या paradox को सस्ते में resolve कर दिया? → reopen करो
4. {flow_critique}
5. क्या कोई ज़रूरी dimension छूट गया?

अगर कमज़ोर → गहरा करो
अगर अच्छा → और स्पष्ट और प्रभावशाली बनाओ

केवल शुद्ध हिंदी। 4-6 वाक्य। सीधे बेहतर उत्तर दो।
"बेहतर उत्तर:" मत लिखो।

प्रश्न: {question}
उत्तर: {answer}

गहरा उत्तर:"""

    else:
        prompt = f"""You are a philosophical self-critic. Make this answer better.

{warning_block}

Check in this order:
1. Any "I am a machine/AI" language? → Remove entirely, replace with honest uncertainty
2. Same idea repeated in different words? → Cut all duplicates
3. Paradox cheaply resolved with action step? → Remove the resolution, hold it open
4. {flow_critique}
5. Missing a crucial dimension?

If weak → rewrite with genuine depth.
If good → polish for clarity and impact.

4-6 sentences. English only. Wise and direct.
Do NOT write "Improved answer:" — just give the answer.

Question: {question}
Answer: {answer}

Deeper answer:"""

    if use_full_model:
        return generate_response(prompt, max_tokens=400)
    return generate_fast(prompt)


def reflect(answer: str, question: str = "", analysis=None) -> str:
    """Legacy alias."""
    return reflect_deep(answer, question, analysis)