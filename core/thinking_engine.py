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

        # Breath / Prana
        "saans"          : "साँस",
        "swas"           : "श्वास",
        "swansh"         : "श्वास",
        "prana"          : "प्राण",
        "praana"         : "प्राण",
        "sukoon"         : "सुकून",
        "sukun"          : "सुकून",
        "ladai"          : "लड़ाई",
        "ladaai"         : "लड़ाई",
        "sangharsh"      : "संघर्ष",

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
        # v3: expanded Hinglish coverage
        "dhyan"          : "ध्यान",
        "dhyaan"         : "ध्यान",
        "insaan"         : "इंसान",
        "insano"         : "इंसानों",
        "kamjori"        : "कमज़ोरी",
        "kamzori"        : "कमज़ोरी",
        "takleef"        : "तकलीफ़",
        "taklif"         : "तकलीफ़",
        "umeed"          : "उम्मीद",
        "ummeed"         : "उम्मीद",
        "matlab"         : "मतलब",
        "matlb"          : "मतलब",
        "matalb"         : "मतलब",
        "virakti"        : "विरक्ति",
        "vairagya"       : "वैराग्य",
        "kalpna"         : "कल्पना",
        "kalpnao"        : "कल्पनाओं",
        "samajh"         : "समझ",
        "disha"          : "दिशा",
        "sansar"         : "संसार",
        "duniya"         : "दुनिया",
        "rishta"         : "रिश्ता",
        "rishte"         : "रिश्ते",
        "bhavna"         : "भावना",
        "ehsaas"         : "एहसास",
        "anubhav"        : "अनुभव",
        "vichar"         : "विचार",
        "soch"           : "सोच",
        "yakeen"         : "यकीन",
        "hausla"         : "हौसला",
        "irada"          : "इरादा",
        "manzil"         : "मंज़िल",
        "rasta"          : "रास्ता",
        "raasta"         : "रास्ता",
        "sachai"         : "सच्चाई",
        "sachhai"        : "सच्चाई",
        "bhagya"         : "भाग्य",
        "kismat"         : "किस्मत",
        "takdir"         : "तक़दीर",

        # v3: Missing informal/abbreviated Hinglish
        "kese"           : "कैसे",
        "badiya"         : "बढ़िया",
        "kch"            : "कुछ",
        "kuch"           : "कुछ",
        "jigyasa"        : "जिज्ञासा",
        "jigyasu"        : "जिज्ञासु",
        "dhoka"          : "धोखा",
        "dhokha"         : "धोखा",
        "tark"           : "तर्क",
        "vitark"         : "वितर्क",
        "charcha"        : "चर्चा",
        "paristhi"       : "परिस्थिति",
        "paristhiti"     : "परिस्थिति",
        "dikkat"         : "दिक्कत",
        "mushkil"        : "मुश्किल",
        "halaat"         : "हालात",
        "samasya"        : "समस्या",
        "wasna"          : "वासना",
        "vasna"          : "वासना",
        "kaam"           : "काम",
        "raah"           : "राह",
        "sury"           : "सूर्य",
        "surya"          : "सूर्य",
        "dev"            : "देव",
        "devi"           : "देवी",
        "devta"          : "देवता",
        "grah"           : "ग्रह",
        "kartvya"        : "कर्तव्य",
        "kartavya"       : "कर्तव्य",
        "palan"          : "पालन",
        "bhitar"         : "भीतर",
        "andar"          : "अंदर",
        "bahar"          : "बाहर",
        "vaibhav"        : "वैभव",
        "garibi"         : "गरीबी",
        "gareebi"        : "गरीबी",
        "najar"          : "नज़र",
        "andaj"          : "अंदाज़",

        # v3: Action / purpose / veer words
        "chahta"         : "चाहता",
        "chahti"         : "चाहती",
        "chahte"         : "चाहते",
        "chahta hoon"    : "चाहता हूँ",
        "karna"          : "करना",
        "karna chahta"   : "करना चाहता",
        "banna"          : "बनना",
        "paana"          : "पाना",
        "achieve"        : "achieve",
        "kuch karna"     : "कुछ करना",
        "kuch banna"     : "कुछ बनना",
        "aage badhna"    : "आगे बढ़ना",
        "badalna"        : "बदलना",
        "jeetna"         : "जीतना",
        "sapna"          : "सपना",
        "lakshya"        : "लक्ष्य",
        "himmat hai"     : "हिम्मत है",
        "hausla hai"     : "हौसला है",
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
        "sadhguru"       : "सद्गुरु",
        "jaggi"          : "जग्गी",

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

        # v3: Grammar words (follow-up/clarification detection)
        "ye"             : "यह",
        "ki"             : "कि",
        "ka"             : "का",
        "ke"             : "के",
        "ko"             : "को",
        "ho"             : "हो",
        "rahi"           : "रही",
        "raha"           : "रहा",
        "se"             : "से",
        "jese"           : "जैसे",
        "jaise"          : "जैसे",
        "nhi"            : "नहीं",
        "ak"             : "एक",
        "ek"             : "एक",
        "kab"            : "कब",
        "kahan"          : "कहाँ",
        "phir"           : "फिर",
        "jab"            : "जब",
        "tab"            : "तब",
        "abhi"           : "अभी",
        "kyo"            : "क्यों",

        # v3: Concept words (common Hinglish)
        "dimag"          : "दिमाग",
        "dimaag"         : "दिमाग",
        "yaad"           : "याद",
        "yaadein"        : "यादें",
        "bhool"          : "भूल",
        "dard"           : "दर्द",
        "gussa"          : "गुस्सा",
        "akela"          : "अकेला",
        "neend"          : "नींद",
        "paisa"          : "पैसा",
        "jeet"           : "जीत",
        "haar"           : "हार",
        "lene"           : "लेने",
        "dene"           : "देने",
        "baat"           : "बात",
        "chij"           : "चीज़",
        "chijo"          : "चीज़ों",
        "cheez"          : "चीज़",
        "rakh"           : "रख",
        "rakhta"         : "रखता",
        "pata"           : "पता",
        "log"            : "लोग",
        "kisse"          : "किससे",

        # v3: Follow-up / conversational Hinglish
        "bataye"         : "बताये",
        "batao"          : "बताओ",
        "bataye"         : "बताये",
        "batana"         : "बताना",
        "sudhar"         : "सुधार",
        "sudhaar"        : "सुधार",
        "samjh"          : "समझ",
        "samjhe"         : "समझे",
        "samjho"         : "समझो",
        "samjhna"        : "समझना",
        "tarah"          : "तरह",
        "tarike"         : "तरीके",
        "tarika"         : "तरीका",
        "iske"           : "इसके",
        "uske"           : "उसके",
        "bare"           : "बारे",
        "baare"          : "बारे",
        "jaye"           : "जाये",
        "kiye"           : "किये",
        "kare"           : "करे",
        "karein"         : "करें",
        "hota"           : "होता",
        "hoti"           : "होती",
        "hote"           : "होते",
        "sakta"          : "सकता",
        "sakti"          : "सकती",
        "sakte"          : "सकते",
        "woh"            : "वो",
        "wah"            : "वह",
        "yaar"           : "यार",
        "bhai"           : "भाई",
        "toh"            : "तो",
        "lekin"          : "लेकिन",
        "magar"          : "मगर",
        "par"            : "पर",
        "liye"           : "लिए",
        "dusra"          : "दूसरा",
        "dusre"          : "दूसरे",
        "pehle"          : "पहले",
        "baad"           : "बाद",
        "saath"          : "साथ",
        "beech"          : "बीच",
        "bich"           : "बीच",
        "sambandh"       : "संबंध",
        "vikas"          : "विकास",
        "vikasit"        : "विकसित",
        "bhavishya"      : "भविष्य",
        "machine"        : "मशीन",
        "masheen"        : "मशीन",
        "robot"          : "रोबोट",
        "technology"     : "तकनीक",
        "takneek"        : "तकनीक",
        "computer"       : "कंप्यूटर",
        "kasht"          : "कष्ट",
        "kashtdayak"     : "कष्टदायक",
        "kastdayak"      : "कष्टदायक",
        "peeda"          : "पीड़ा",
        "pida"           : "पीड़ा",
        "manav"          : "मानव",
        "painful"        : "दर्दनाक",
        "depressed"      : "डिप्रेस",
        "depression"     : "डिप्रेशन",
        "emotionally"    : "भावनात्मक",
        "emotional"      : "भावनात्मक",
        "support"        : "सहारा",
        "sahara"         : "सहारा",
        "madad"          : "मदद",
        "dost"           : "दोस्त",
        "friend"         : "दोस्त",
        "opposite"       : "उलट",
        "ulat"           : "उलट",
        "vyavhar"        : "व्यवहार",
        "behave"         : "व्यवहार",
        "feel"           : "फील",
        "mehsoos"        : "महसूस",
        "mehsus"         : "महसूस",

        # v3: Missing personal/conversational
        "mujhe"          : "मुझे",
        "mene"           : "मेने",
        "maine"          : "मैंने",
        "hoon"           : "हूँ",
        "hun"            : "हूँ",
        "hone"           : "होने",
        "aage"           : "आगे",
        "thik"           : "ठीक",

        # v3: Determination / resolution
        "nischay"        : "निश्चय",
        "nishchay"       : "निश्चय",
        "taiyar"         : "तैयार",
        "reday"          : "तैयार",

        # v3: Grammar connectors
        "parntu"         : "परंतु",
        "parantu"        : "परंतु",
        "kintu"          : "किंतु",
        "krke"           : "करके",
        "karke"          : "करके",
        "badta"          : "बढ़ता",
        "badhta"         : "बढ़ता",
        "ispr"           : "इसपर",
        "ispe"           : "इसपे",

        # v3: Example / moral vocabulary
        "udahran"        : "उदाहरण",
        "udaharan"       : "उदाहरण",
        "samjha"         : "समझा",
        "galat"          : "गलत",
        "sahi"           : "सही",

        # v4: Missing Hinglish spelling variants (from trace analysis)
        "weekness"       : "कमज़ोरी",
        "weakness"       : "कमज़ोरी",
        "pariwar"        : "परिवार",
        "parivaar"       : "परिवार",
        "parivar"        : "परिवार",
        "jimmedari"      : "ज़िम्मेदारी",
        "jimmedariyon"   : "ज़िम्मेदारियों",
        "zimmadari"      : "ज़िम्मेदारी",
        "zimmedari"      : "ज़िम्मेदारी",
        "wartman"        : "वर्तमान",
        "vartman"        : "वर्तमान",
        "vartmaan"       : "वर्तमान",
        "bhavisya"       : "भविष्य",
        "muskil"         : "मुश्किल",
        "vicharo"        : "विचारों",
        "shant"          : "शांत",
        "tivra"          : "तीव्र",
        "jyada"          : "ज़्यादा",
        "sayad"          : "शायद",
        "insan"          : "इंसान",
        "sabse"          : "सबसे",
        "badi"           : "बड़ी",
        "payega"         : "पायेगा",
        "padega"         : "पड़ेगा",
        "sochna"         : "सोचना",
        "bareme"         : "बारेमें",

        # v4: Respect / desire / obsession
        "izzat"          : "इज़्ज़त",
        "samman"         : "सम्मान",
        "ichha"          : "इच्छा",
        "lalach"         : "लालच",
        "lobh"           : "लोभ",
        "trishna"        : "तृष्णा",

        # v4: Relationship words
        "bhai"           : "भाई",
        "behan"          : "बहन",
        "behen"          : "बहन",
        "pita"           : "पिता",
        "pitaji"         : "पिताजी",
        "baap"           : "बाप",
        "mata"           : "माता",
        "mataji"         : "माताजी",
        "maa"            : "माँ",
        "patni"          : "पत्नी",
        "pati"           : "पति",
        "beta"           : "बेटा",
        "beti"           : "बेटी",
        "bachcha"        : "बच्चा",
        "bachche"        : "बच्चे",
        "biwi"           : "बीवी",
        "rishtedaar"     : "रिश्तेदार",

        # v4: More common misspellings + missing words
        "duskh"          : "दुख",
        "khushiya"       : "खुशियाँ",
        "khushiyan"      : "खुशियाँ",
        "moun"           : "मौन",
        "maun"           : "मौन",
        "diffrence"      : "difference",
        "farak"          : "फ़र्क",
        "farq"           : "फ़र्क",
        "antar"          : "अंतर",
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

# Curated Hinglish-only words — NOT standard English.
# Used to detect romanized Hindi without false positives from English words
# like "feel", "friend", "machine" that exist in hinglish_map.
_HINGLISH_MARKERS = {
    # Pronouns / grammar
    "kya", "hai", "hain", "aur", "mera", "meri", "tera", "teri",
    "humara", "tumhara", "nahi", "nhi", "haan", "bahut", "tum",
    "hum", "yeh", "woh", "wo", "kaise", "kese", "kyun", "kyo",
    "kyoki", "batao", "samjhao", "bolo", "abhi", "phir", "jab",
    "tab", "toh", "lekin", "magar", "parntu", "kintu",
    # Common verbs / helpers
    "karna", "karta", "karti", "chahta", "chahti", "sakta",
    "sakti", "hota", "hoti", "raha", "rahi", "padega", "hoga",
    "karein", "kare", "jaye", "kiye", "bataye", "samjhe",
    # Concept words (clearly not English)
    "insaan", "insan", "zindagi", "jindagi", "pyar", "pyaar",
    "dukh", "sukh", "dharma", "karma", "satya", "atma", "aatma",
    "mann", "buddhi", "gyan", "shakti", "shanti", "mukti",
    "safalta", "dar", "himmat", "vishwas", "chetna", "parmatma",
    "ishwar", "bhagwan", "accha", "bura", "theek", "thik",
    "samjh", "tarika", "matlab", "kuch", "dimag", "dimaag",
    "yaad", "dard", "gussa", "akela", "neend", "paisa", "jeet",
    "haar", "soch", "vichar", "ehsaas", "hausla", "sachai",
    "sansar", "duniya", "kismat", "bhagya", "jigyasa", "dhoka",
    "mushkil", "muskil", "dikkat", "samasya", "mujhe", "maine",
    "hoon", "hun", "aage", "pehle", "baad", "saath", "rishta",
    "kamjori", "kamzori", "pariwar", "jimmedari", "wartman",
    "vicharo", "shant", "tivra", "jyada", "sayad", "farak",
    "moun", "maun", "duskh", "khushiya",
    # Relationship words (clearly not English)
    "bhai", "behan", "behen", "pita", "pitaji", "baap",
    "mata", "mataji", "maa", "patni", "pati", "biwi",
    "beta", "beti", "bachcha", "bachche", "rishtedaar",
    # Respect / desire
    "izzat", "samman", "ichha", "lalach", "lobh", "trishna",
    # Breath / struggle
    "saans", "swas", "swansh", "prana", "praana",
    "sukoon", "sukun", "ladai", "ladaai", "sangharsh",
}


def detect_language(text: str) -> str:
    """
    Detect if question is Hindi/Hinglish or English.

    Process:
    1. Check for explicit Hindi request keywords
    2. Check original text for Devanagari characters (> 2 → hindi)
    3. Check for Hinglish-only marker words (>= 2 → hindi)
    4. Otherwise → english

    NOTE: Does NOT use translate_hinglish() — that caused false positives
    because common English words (feel, friend, machine) were in hinglish_map.

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

    # Step 1: Check ORIGINAL text for Devanagari characters
    hindi_chars = set(
        'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'
        'ङञड़ढ़क्षत्रज्ञश्रफ़ज़'
    )
    devanagari_count = sum(1 for c in text if c in hindi_chars)
    if devanagari_count > 2:
        return 'hindi'

    # Step 2: Check for Hinglish-only words (romanized Hindi, NOT English)
    words = {w.lower().strip('?!.,;:।') for w in text.split()}
    hinglish_count = len(words & _HINGLISH_MARKERS)
    if hinglish_count >= 2:
        return 'hindi'

    return 'english'


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