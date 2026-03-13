# ============================================================
# 📁 core/reflection_engine.py
# ⚡ Uses generate_fast() — 150 tokens only!
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_loader import generate_fast  # ⚡ fast version!


def detect_language(text: str) -> str:
    hindi_chars = set(
        'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'
        'ङञड़ढ़क्षत्रज्ञश्रफ़ज़'
    )
    count = sum(1 for c in text if c in hindi_chars)
    return 'hindi' if count > 2 else 'english'


def reflect(answer: str, question: str = "") -> str:
    """
    Quickly improve the answer.
    ⚡ Uses generate_fast() — 150 tokens max!

    What reflection does:
    ✅ Makes answer clearer
    ✅ Adds depth
    ✅ Fixes language quality
    ✅ Keeps same language (Hindi/English)
    """

    language = detect_language(question)

    if language == 'hindi':
        prompt = f"""नीचे दिए उत्तर को बेहतर और विस्तृत बनाओ।
केवल शुद्ध हिंदी में। 3-4 वाक्य। सीधे उत्तर दो।
कोई अनुवाद मत दो। कोई brackets मत लगाओ।

उत्तर: {answer}

बेहतर उत्तर:"""

    else:
        prompt = f"""Improve this philosophical answer.
3-4 sentences. English only. Be wise and direct.
No translation. No brackets.

Answer: {answer}

Improved answer:"""

    return generate_fast(prompt)  # ⚡ fast 150 token call!