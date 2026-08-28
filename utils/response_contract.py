# ============================================================
# utils/response_contract.py
# Declarative response contract system — ONE place for all
# post-processing rules. Adding a new contract = adding a config entry.
# ============================================================

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.concept_analyzer import PHILOSOPHER_KEYWORDS
from utils.phrase_dedup import strip_banned_phrases, dedup_phrases


# ─── Contract definitions ────────────────────────────────

@dataclass
class ResponseContract:
    name: str
    max_sentences: int
    max_tokens: Optional[int] = None   # None = use _calculate_max_tokens()
    strip_advice: bool = False
    strip_philosophy: bool = False
    strip_names: bool = False


# The three initial contracts
CONTRACTS = {
    "crisis": ResponseContract(
        name="crisis",
        max_sentences=3,
        max_tokens=120,
        strip_advice=True,
        strip_philosophy=True,
        strip_names=True,
    ),
    "emotional_high": ResponseContract(
        name="emotional_high",
        max_sentences=5,
        strip_advice=False,
        strip_philosophy=False,
        strip_names=True,
    ),
    "default": ResponseContract(
        name="default",
        max_sentences=8,
        strip_advice=False,
        strip_philosophy=False,
        strip_names=False,
    ),
}

# ─── Karuna safety fallbacks ─────────────────────────────

_KARUNA_FALLBACK = {
    "hindi": "तुम्हारा दर्द सुन रहा हूँ। तुम अकेले नहीं हो।",
    "english": "I hear you. You're not alone in this.",
}

# ─── Advice patterns (crisis only) ───────────────────────

_ADVICE_PATTERNS = [
    # Hindi
    r"कोशिश करो",
    r"यह जरूरी है कि",
    r"एक कदम",
    r"आपको चाहिए कि",
    r"ध्यान रखो कि",
    r"याद रखो कि",
    r"try to",
    # English
    r"you should try",
    r"you should consider",
    r"you need to",
    r"you must",
    r"try to find",
    r"make sure you",
    r"consider doing",
]

# ─── Wisdom words (for philosophy stripping) ─────────────

_WISDOM_WORDS = [
    "impermanent", "impermanence", "dharma", "karma", "atman", "moksha",
    "samsara", "nirvana", "sunyata", "prakriti", "brahman", "maya",
    "consciousness", "liberation", "suffering", "attachment", "detachment",
    "ego", "illusion", "wisdom", "truth", "soul", "awareness",
    "meditation", "stillness", "equanimity", "compassion", "virtue",
    "existential", "metaphysical", "transcend", "eternal", "mortal",
    "self-knowledge", "witness", "observe",
    # Hindi
    "क्षणिक", "धर्म", "आत्मा", "अनित्य", "संसार", "अमर", "नित्य",
    "कर्म", "मोक्ष", "ब्रह्म", "प्रकृति", "माया", "चेतना", "ज्ञान",
    "सत्य", "शांति", "मुक्ति", "अहंकार", "विचार", "बोध", "साक्षी",
    "वैराग्य", "संस्कार", "गुण", "सत्व", "तमस", "रजस", "योग",
    "ध्यान", "प्राण", "तत्व", "दर्शन", "विवेक", "अनुभव", "स्वभाव",
    "करुणा", "अनासक्ति", "शाश्वत", "आनंद", "समर्पण", "क्षमा",
]


# ─── Contract selection ──────────────────────────────────

def select_contract(analysis, prajna_hint: str, is_identity: bool) -> ResponseContract:
    """
    Select the appropriate response contract based on analysis + prajna.
    1. Crisis: "THIS IS NOT PHILOSOPHY" + high/medium emotion + emotional type
    2. Emotional high: emotional + high intensity
    3. Default: everything else
    """
    emotional_intensity = getattr(analysis, 'emotional_intensity', 'low')
    question_type = getattr(analysis, 'question_type', 'mixed')

    # Crisis contract — Prajna's crisis signal is the strongest detector.
    # When Prajna says "THIS IS NOT PHILOSOPHY", trust it unconditionally.
    # EI and question_type classifiers often miss edge cases like "ghrina nazar aati hai".
    if "THIS IS NOT PHILOSOPHY" in prajna_hint:
        return CONTRACTS["crisis"]

    # Emotional high contract — high intensity regardless of question_type
    # (user can be in high distress even with question_type="mixed")
    if emotional_intensity == "high":
        return CONTRACTS["emotional_high"]

    # Medium emotion + emotional type also gets emotional_high
    if emotional_intensity == "medium" and question_type == "emotional":
        return CONTRACTS["emotional_high"]

    # Default
    return CONTRACTS["default"]


# ─── Sentence splitting ──────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """Split on Hindi/English sentence boundaries."""
    parts = re.split(r'(?<=[।.!?])\s+', text.strip())
    return [s.strip() for s in parts if s.strip()]


# ─── Contract enforcement ────────────────────────────────

def enforce_contract(
    text: str,
    contract: ResponseContract,
    language: str,
    asked_philosophers: List[str],
    post_stream: bool = False,
) -> Tuple[str, Dict]:
    """
    Apply all contract rules to text. Returns (cleaned_text, violations_dict).

    When post_stream=True, also runs paragraph dedup + sentence dedup
    (moved from pipeline streaming code).
    """
    if not text:
        return text, {}

    # Structured violations — consistent types for trace filtering
    violations = {
        "advice_stripped": 0,
        "philosophy_stripped": 0,
        "names_stripped": [],
        "sentences_truncated": 0,
        "banned_phrases_stripped": False,
        "dedup_triggered": False,
        "safety_floor_used": False,
    }

    # ── Step 1 (streaming only): paragraph + sentence dedup ──
    if post_stream:
        text, para_dedup, sent_dedup = _post_stream_dedup(text)
        if para_dedup:
            violations["paragraph_dedup"] = True
        if sent_dedup:
            violations["sentence_dedup"] = True

    # ── Step 2: Banned phrase strip (cheap, fast — do first) ──
    before_len = len(text)
    text = strip_banned_phrases(text)
    if len(text) < before_len:
        violations["banned_phrases_stripped"] = True

    # ── Step 3: Advice stripping (before truncation — strip junk first) ──
    sentences = _split_sentences(text)
    if contract.strip_advice:
        filtered = []
        for s in sentences:
            if _is_advice_sentence(s):
                violations["advice_stripped"] += 1
            else:
                filtered.append(s)
        sentences = filtered

    # ── Step 4: Philosophy stripping (before truncation) ──
    if contract.strip_philosophy:
        filtered = []
        for s in sentences:
            if _is_philosophy_sentence(s):
                violations["philosophy_stripped"] += 1
            else:
                filtered.append(s)
        sentences = filtered

    # ── Step 5: Name-drop removal (before truncation) ──
    if contract.strip_names:
        text_joined = ' '.join(sentences)
        text_joined, names_removed = _strip_name_drops(text_joined, asked_philosophers)
        violations["names_stripped"] = names_removed
        sentences = _split_sentences(text_joined) if text_joined else []

    # ── Step 6: Sentence truncation (now truncates CLEANED text) ──
    if len(sentences) > contract.max_sentences:
        violations["sentences_truncated"] = len(sentences) - contract.max_sentences
        print(f"✂️ Contract '{contract.name}': {len(sentences)} → {contract.max_sentences} sentences")
        sentences = sentences[:contract.max_sentences]

    # Rejoin after sentence-level operations
    text = ' '.join(sentences)

    # ── Step 7: 3-gram dedup ──
    before_len = len(text)
    text = dedup_phrases(text)
    if len(text) < before_len:
        violations["dedup_triggered"] = True

    # ── Step 8: Sentence completion guard ──
    text = _ensure_sentence_completion(text)

    # ── Step 9: Safety floor — karuna fallback ──
    remaining = _split_sentences(text)
    if not remaining or all(not s.strip() for s in remaining):
        lang_key = "hindi" if language == "hindi" else "english"
        text = _KARUNA_FALLBACK[lang_key]
        violations["safety_floor_used"] = True
        print(f"🛟 Contract '{contract.name}': all sentences stripped → karuna fallback")

    # Final cleanup — orphan punctuation from stripping steps
    text = re.sub(r'\s+।', '।', text)
    text = re.sub(r'।\s*।', '।', text)
    text = re.sub(r'\.\s*\.', '.', text)
    text = re.sub(r'  +', ' ', text)

    return text.strip(), violations


# ─── Helper functions ────────────────────────────────────

def _is_advice_sentence(sentence: str) -> bool:
    """Check if a sentence contains advice patterns."""
    s_lower = sentence.lower()
    for pattern in _ADVICE_PATTERNS:
        if re.search(pattern, s_lower):
            return True
    return False


def _is_philosophy_sentence(sentence: str) -> bool:
    """Check if a sentence has >=2 wisdom words (philosophy injection)."""
    s_lower = sentence.lower()
    count = sum(1 for w in _WISDOM_WORDS if w in s_lower)
    return count >= 2


def _strip_name_drops(text: str, asked_philosophers: List[str]) -> Tuple[str, List[str]]:
    """
    Remove philosopher name-drops UNLESS the user asked about them.
    Returns (cleaned_text, list of removed names).
    """
    # Build set of names the user actually asked about (keep these)
    asked_names = set()
    for p in asked_philosophers:
        asked_names.add(p.lower())
        # Also keep partial matches (e.g. user asked "buddha" → keep "Buddha")
        for word in p.lower().split():
            asked_names.add(word)

    # All philosopher names from PHILOSOPHER_KEYWORDS values (unique)
    all_names = set(PHILOSOPHER_KEYWORDS.values())
    removed = []

    for name in all_names:
        # Skip if user asked about this philosopher
        if name.lower() in asked_names or any(w in asked_names for w in name.lower().split()):
            continue

        # Remove name mentions
        if name in text:
            text = text.replace(name, "")
            removed.append(name)

        # Also remove lowercase/case-insensitive variants for English names
        name_lower = name.lower()
        if not any('\u0900' <= c <= '\u097F' for c in name):
            text = re.sub(r'\b' + re.escape(name) + r'\b', '', text, flags=re.IGNORECASE)

    # Clean up artifacts from removal
    if removed:
        text = re.sub(r'  +', ' ', text)
        text = re.sub(r'^\s*[,।\.]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r',\s*,', ',', text)
        text = re.sub(r'\s+,', ',', text)
        # Remove orphan fragments like "ने कहा।" left after name removal
        text = re.sub(r'(?:^|\.\s*|।\s*)\s*ने\s+कह[ाी][।.]', '।', text)
        text = re.sub(r'\s+said\s*[।.]', '.', text, flags=re.IGNORECASE)

    return text, removed


def _post_stream_dedup(text: str) -> Tuple[str, bool, bool]:
    """
    Post-stream dedup: paragraph dedup + sentence dedup.
    Moved from pipeline streaming code.
    Returns (cleaned_text, paragraph_dedup_happened, sentence_dedup_happened).
    """
    para_dedup = False
    sent_dedup = False

    # Paragraph dedup
    paragraphs = text.split('\n\n')
    seen_para = set()
    clean_paras = []
    for p in paragraphs:
        key = p.strip()[:50]
        if key and key not in seen_para:
            seen_para.add(key)
            clean_paras.append(p)
        elif key:
            para_dedup = True
    text = '\n\n'.join(clean_paras)

    # Sentence dedup (first-30-char key)
    parts = re.split(r'([.।?!\n])', text)
    seen = set()
    clean = []
    for i in range(0, len(parts) - 1, 2):
        sentence = parts[i].strip()
        sep = parts[i + 1] if i + 1 < len(parts) else ''
        if not sentence:
            clean.append(sep)
            continue
        key = sentence[:40].lower()
        if key not in seen:
            seen.add(key)
            clean.append(parts[i] + sep)
        else:
            sent_dedup = True
    if len(parts) % 2 == 1 and parts[-1].strip():
        key = parts[-1].strip()[:40].lower()
        if key not in seen:
            clean.append(parts[-1])
        else:
            sent_dedup = True
    text = ''.join(clean).strip()

    return text, para_dedup, sent_dedup


def _ensure_sentence_completion(text: str) -> str:
    """Trim incomplete final sentence — keeps text ending at last sentence boundary."""
    if not text:
        return text
    if text.rstrip().endswith(('.', '।', '?', '!')):
        return text
    last_end = max(
        text.rfind('.'), text.rfind('।'),
        text.rfind('?'), text.rfind('!')
    )
    if last_end > len(text) * 0.7:
        return text[:last_end + 1]
    return text
