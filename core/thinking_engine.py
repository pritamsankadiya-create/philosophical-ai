# ============================================================
# 📁 core/thinking_engine.py
# 🎯 Purpose: Think + Memory + Hindi/Hinglish/English
# ⚡ Optimized for tinyllama speed!
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_loader import generate_response
from memory.vector_store import search_philosophy


# ─── Step 1: Hinglish to Hindi Translator ───────────────────
def translate_hinglish(text: str) -> str:
    """
    Convert Hinglish words to Hindi word by word.
    Handles: Payar → प्यार, Khushi → खुशी
    """
    hinglish_map = {
        # Love & Relationships
        "payar"          : "प्यार",
        "pyar"           : "प्यार",
        "mohabbat"       : "मोहब्बत",
        "ishq"           : "इश्क़",

        # Life
        "zindagi"        : "ज़िंदगी",
        "jindagi"        : "ज़िंदगी",
        "jiwan"          : "जीवन",
        "jivan"          : "जीवन",
        "maut"           : "मृत्यु",
        "mrityu"         : "मृत्यु",
        "moksha"         : "मोक्ष",

        # Common questions
        "kya hai"        : "क्या है",
        "kya"            : "क्या",
        "kyun"           : "क्यों",
        "kaise"          : "कैसे",
        "kaun"           : "कौन",
        "batao"          : "बताओ",
        "samjhao"        : "समझाओ",
        "bolo"           : "बोलो",
        "aur batao"      : "और बताओ",

        # Philosophy topics
        "khushi"         : "खुशी",
        "dukh"           : "दुख",
        "sukh"           : "सुख",
        "satya"          : "सत्य",
        "dharma"         : "धर्म",
        "karma"          : "कर्म",
        "atma"           : "आत्मा",
        "mann"           : "मन",
        "buddhi"         : "बुद्धि",
        "gyan"           : "ज्ञान",
        "shakti"         : "शक्ति",
        "shanti"         : "शांति",
        "mukti"          : "मुक्ति",
        "safalta"        : "सफलता",
        "asafalta"       : "असफलता",
        "sapna"          : "सपना",
        "sapne"          : "सपने",
        "dar"            : "डर",
        "himmat"         : "हिम्मत",
        "vishwas"        : "विश्वास",
        "sach"           : "सच",
        "jhooth"         : "झूठ",
        "chetna"         : "चेतना",
        "mann"           : "मन",
        "aatma"          : "आत्मा",
        "parmatma"       : "परमात्मा",
        "ishwar"         : "ईश्वर",
        "bhagwan"        : "भगवान",

        # Philosophers
        "osho"           : "ओशो",
        "krishna"        : "कृष्ण",
        "kalam"          : "कलाम",
        "chanakya"       : "चाणक्य",
        "kabir"          : "कबीर",
        "nanak"          : "नानक",
        "vivekanand"     : "विवेकानंद",
        "tagore"         : "टैगोर",
        "patanjali"      : "पतंजलि",
        "shankaracharya" : "शंकराचार्य",
        "buddha"         : "बुद्ध",

        # Grammar words
        "hai"            : "है",
        "hain"           : "हैं",
        "aur"            : "और",
        "mera"           : "मेरा",
        "tera"           : "तेरा",
        "humara"         : "हमारा",
        "tumhara"        : "तुम्हारा",
        "main"           : "मैं",
        "hum"            : "हम",
        "tum"            : "तुम",
        "aap"            : "आप",
        "yeh"            : "यह",
        "woh"            : "वो",
        "nahi"           : "नहीं",
        "haan"           : "हाँ",
        "bahut"          : "बहुत",
        "accha"          : "अच्छा",
        "bura"           : "बुरा",
        "theek"          : "ठीक",
    }

    # Word by word replacement
    result = []
    words = text.split()
    for word in words:
        clean = word.lower().strip('?!.,।')
        if clean in hinglish_map:
            result.append(hinglish_map[clean])
        else:
            result.append(word)

    return ' '.join(result)


# ─── Step 2: Language Detector ──────────────────────────────
def detect_language(text: str) -> str:
    """
    Detect if question is Hindi/Hinglish or English.

    Process:
    1. Check for explicit Hindi request keywords
    2. Translate Hinglish → Hindi
    3. Count Hindi characters
    4. More than 2 Hindi chars → reply in Hindi
    5. Otherwise → reply in English

    Returns: 'hindi' or 'english'
    """
    lower = text.lower()

    # Explicit Hindi request — user wants Hindi response
    hindi_keywords = [
        'hindi me', 'hindi mein', 'hindi mai',
        'hindi me batao', 'hindi mein batao',
        'hindi me samjhao', 'hindi mein samjhao',
        'in hindi',
    ]
    if any(kw in lower for kw in hindi_keywords):
        return 'hindi'

    translated = translate_hinglish(text)
    hindi_chars = set(
        'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'
        'ङञड़ढ़क्षत्रज्ञश्रफ़ज़'
    )
    count = sum(1 for c in translated if c in hindi_chars)
    return 'hindi' if count > 2 else 'english'


# ─── Step 3: Smart Search Query Builder ─────────────────────
def build_search_query(question: str, chat_memory=None) -> str:
    """
    Build smarter search query using memory context.

    Example:
        User: "Tell me more"
        Last topic: "love"
        Smart query: "Tell me more love"
        → Vector search finds RIGHT philosophy! ✅
    """
    if not chat_memory or chat_memory.is_empty():
        return question

    # Get last user message for context
    last_topic = ""
    for msg in reversed(chat_memory.history):
        if msg["role"] == "user":
            last_topic = msg["content"]
            break

    # Vague words in Hindi + English + Hinglish
    vague_words = [
        # English
        "it", "this", "that", "more", "about it",
        "tell me more", "explain", "elaborate",
        "continue", "and then", "so", "go deeper",
        # Hindi
        "और बताओ", "समझाओ", "इसके बारे में",
        "यह", "इसे", "आगे", "बताओ",
        # Hinglish
        "aur batao", "batao", "samjhao", "aur"
    ]

    is_vague = any(
        word in question.lower()
        for word in vague_words
    )

    if is_vague and last_topic:
        smart = f"{question} {last_topic}"
        print(f"🔍 Smart query: '{smart}'")
        return smart

    return question


# ─── Step 4: Main Think Function ────────────────────────────
def think(question: str, chat_memory=None) -> str:
    """
    Main function — generates philosophical answer.

    ✅ English  → "What is love?"
    ✅ Hindi    → "प्यार क्या है?"
    ✅ Hinglish → "Payar kya hai?"
    ⚡ Fast     → Optimized prompt!

    Args:
        question    : user's question (any language)
        chat_memory : ChatMemory object (optional)

    Returns:
        Philosophical answer string
    """

    # Step 1: Translate Hinglish → Hindi
    translated = translate_hinglish(question)

    # Step 2: Detect language
    language = detect_language(question)
    print(f"🌐 Language  : {language}")
    print(f"🔄 Translated: {translated}")

    # Step 3: Smart search query using memory
    search_query = build_search_query(translated, chat_memory)

    # Step 4: Get relevant philosophy from vector store
    relevant = search_philosophy(search_query, top_k=2)
    context = "\n".join([f"- {r}" for r in relevant])

    # Step 5: Get conversation history
    history = ""
    if chat_memory and not chat_memory.is_empty():
        history = chat_memory.get_history_as_text()

    # Step 6: Clean focused prompt for mistral
    if language == 'hindi':
        prompt = f"""तुम एक दार्शनिक गुरु हो।
नीचे दिए ज्ञान से प्रश्न का उत्तर दो।
केवल हिंदी में। 3-4 वाक्य। सीधे उत्तर दो।

ज्ञान:
{context}

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:"""

    else:
        prompt = f"""You are a wise philosophical guru.
Answer ONLY the question asked using the knowledge below.
Give 3-4 sentences. Stay on topic. Be direct and deep.

Knowledge:
{context}

Previous conversation:
{history}

Question: {question}

Answer:"""

    # Step 7: Get answer from tinyllama ⚡
    return generate_response(prompt)