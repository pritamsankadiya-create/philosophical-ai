# ============================================================
# core/reflection_engine.py
# Self-critique engine — checks depth, deepens if superficial
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_loader import generate_fast


def detect_language(text: str) -> str:
    hindi_chars = set(
        'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'
        'ङञड़ढ़क्षत्रज्ञश्रफ़ज़'
    )
    count = sum(1 for c in text if c in hindi_chars)
    return 'hindi' if count > 2 else 'english'


def reflect(answer: str, question: str = "", analysis=None) -> str:
    """
    Self-critique: Is this answer superficial? If yes, deepen it.

    The AI critiques its own answer:
    1. Is the answer superficial or generic?
    2. Intent-specific critique (define→clarity, compare→fairness, etc.)
    3. If shallow → rewrite with depth. If good → polish and return.

    Uses generate_fast() — 200 tokens max.
    """
    language = detect_language(question)

    # Build intent-specific critique focus
    critique_focus = ""
    if analysis is not None:
        intent = getattr(analysis, 'intent', 'explore')
        if intent == "define":
            critique_focus = "Does it define clearly with philosophical depth, or just repeat common knowledge?"
        elif intent == "compare":
            critique_focus = "Does it fairly present both sides with a real synthesis, or just list differences?"
        elif intent == "apply":
            critique_focus = "Does it give actionable wisdom rooted in philosophy, or just vague advice?"
        elif intent == "challenge":
            critique_focus = "Does it steelman the opposing view before countering, or dismiss it?"
        else:
            critique_focus = "Does it explore with genuine depth, or stay on the surface?"

    if language == 'hindi':
        critique_hindi = ""
        if critique_focus:
            critique_hindi = f"\nआलोचना का केंद्र: {critique_focus}"

        prompt = f"""तुम एक दार्शनिक आलोचक हो। नीचे दिए उत्तर की आत्म-आलोचना करो।

क्या यह उत्तर उथला है? क्या यह सिर्फ सामान्य बात दोहराता है?
अगर हाँ — तो इसे गहरा करो, दार्शनिक अंतर्दृष्टि जोड़ो।
अगर नहीं — तो इसे और स्पष्ट और प्रभावशाली बनाओ।
{critique_hindi}

केवल शुद्ध हिंदी में। 4-6 वाक्य। सीधे बेहतर उत्तर दो।
कोई अनुवाद मत दो। कोई brackets मत लगाओ। "बेहतर उत्तर:" मत लिखो।

प्रश्न: {question}
उत्तर: {answer}

गहरा उत्तर:"""

    else:
        critique_eng = ""
        if critique_focus:
            critique_eng = f"\nCritique focus: {critique_focus}"

        prompt = f"""You are a philosophical self-critic. Critique the answer below.

Is this answer superficial? Does it just repeat common knowledge without real insight?
If YES — rewrite it with genuine philosophical depth. Add insight the reader wouldn't expect.
If NO — polish it for clarity and impact.
{critique_eng}

4-6 sentences. English only. Be wise and direct.
No translation. No brackets. Don't write "Improved answer:".

Question: {question}
Answer: {answer}

Deeper answer:"""

    return generate_fast(prompt)
