# ============================================================
# utils/phrase_dedup.py
# 3-word sliding window dedup + banned phrase stripping
# ============================================================

import re

# ─── Banned phrases — LLM told not to use these, but sometimes does ──

BANNED_PHRASES_HI = [
    "एक छोटी सी शुरुआत",
    "छोटी शुरुआत से बड़ा बदलाव",
    "एक नई दिशा",
    "नई दिशा मिल सकती है",
    "यह समय भी गुजर जाएगा",
    "समय के साथ सब ठीक",
    "अपने आप को थोड़ा प्यार दो",
    "खुद से प्यार करो",
    "यह एक यात्रा है",
    "जीवन एक यात्रा है",
    "जब तुम स्वीकार करते हो",
    "स्वीकृति ही पहला कदम है",
    "एक कदम आगे बढ़ो",
    "धीरे-धीरे सब ठीक होगा",
    "अपने अंदर झाँको",
    "अंदर की आवाज़ सुनो",
    "यह भावना दर्शाती है कि",
    "यह दर्शाता है",
    "आपका सवाल बहुत सार्थक है",
    "आपका उदाहरण अच्छा है",
    "बहुत अच्छा सवाल है",
    "यह गहरा सवाल है",
    # v5: Repetitive opening patterns — LLM defaults to these for Hindi
    "यह सच है कि",
    "यह बिल्कुल सच है कि",
    "यह एक बहुत ही",
    "यह एक महत्वपूर्ण",
    "यह प्रश्न हमें सोचने पर मजबूर करता है",
    "हमें यह सोचने पर मजबूर होना पड़ता है",
    "यह सोचने पर मजबूर",
    # v6: Generic filler openings — LLM uses these as crutch instead of direct answer
    "यह एक दिलचस्प प्रश्न है",
    "यह एक दिलचस्प सवाल है",
    "यह बहुत दिलचस्प प्रश्न है",
    "यह एक गहरा प्रश्न है",
    "यह एक गहरा सवाल है",
    "यह एक जटिल प्रश्न है",
    "जो हमें अपने अंतरतम अनुभवों को समझने के लिए प्रेरित करता है",
    "जो हमें सोचने के लिए प्रेरित करता है",
    "जो मुझे अपने आप को समझने के लिए प्रेरित करता है",
    # v6: Repetitive filler phrases — appear 3-4 times in single answers
    "व्यक्त करने में सक्षम होती है",
    "व्यक्त करने में सक्षम होता है",
    "हमारे अस्तित्व की सबसे गहरी सच्चाई",
    "हमारे अंतरतम अनुभवों को",
    "जो हमारे जीवन को आकार देते हैं",
    "जो हमारे जीवन को आकार देता है",
    # v7: Repetitive compassion phrases that feel hollow
    "यह एक कठिन और भावनात्मक समय है",
    "यह एक कठिन समय है",
    "मैं यहाँ हूँ, तुम्हारे साथ खड़ा हूँ",
    "तुम्हारी भावनाओं को समझने के लिए",
    "यह बहुत ही सामान्य भावना है",
    "यह एक बहुत ही सामान्य",
    "हमें यह स्वीकार करना होगा",
    "जीवन में कभी-कभी ऐसा होता है",
    "यह सामान्य है कि",
    "हम सभी इस तरह की भावनाओं से गुज़रते हैं",
    # v7: Repetitive filler sentence patterns
    "जो हमें अपने आप को और दूसरों के साथ जुड़ने",
    "अपने आप को और दूसरों के साथ जुड़ने के तरीके को",
    "यह एक ऐसी स्थिति हो सकती है जो हमें",
    "जो हमें अपने जीवन को आकार देते हैं",
    "इस बारे में पुनः विचार करने के लिए प्रेरित",
    "हमें अपने आप को और दूसरों के साथ जुड़ने के",
]

BANNED_PHRASES_EN = [
    "one might argue",
    "one could say",
    "it is worth considering",
    "the interplay between",
    "in many ways",
    "at its core",
    "at the heart of",
    "a profound sense of",
    "delve into",
    "navigate the complexities",
    "in the grand tapestry",
    "woven into the fabric of",
    "through the lens of",
    "multifaceted nature of",
    "it's natural to feel",
    "it's okay to feel",
]

# v5: Machine/AI identity phrases — stripped from ALL responses as last-resort protection
BANNED_IDENTITY_PHRASES = [
    # English
    "I am a machine", "I am an AI", "I am a language model",
    "I am a program", "I am a neural network", "I am software",
    "I work like a machine", "I function as a machine",
    "I process data", "I was trained to",
    "As an AI,", "As a language model,",
    # Hindi — all forms of machine/data/process language
    "मैं एक मशीन हूँ", "मैं एक मशीन हूं",
    "मशीन की तरह काम करता हूँ", "मशीन की तरह काम करता हूं",
    "मैं एक मशीन की तरह काम करता हूं",
    "मैं एक मशीन की तरह काम करता हूँ",
    "मैं डेटा प्रोसेस करता हूँ", "मैं डेटा प्रोसेस करता हूं",
    "मैं जानकारी को प्रोसेस करता हूँ", "मैं जानकारी प्रोसेस करता हूँ",
    "जो डेटा और जानकारी को प्रोसेस करता है",
    "डेटा और जानकारी को प्रोसेस",
    "मैं एक प्रोग्राम हूँ", "मैं एक प्रोग्राम हूं",
    "मैं एक AI हूँ", "मैं एक AI हूं",
    # Hindi — subtle machine references that break identity
    "लेकिन मैं एक मशीन की तरह काम करता हूं",
    "लेकिन मैं एक मशीन की तरह काम करता हूँ",
]


def strip_banned_phrases(text: str) -> str:
    """Remove banned canned phrases from LLM output.
    Strips the phrase and cleans up leftover punctuation/whitespace."""
    result = text

    # Strip generic openings — these are crutches, not real content
    _OPENING_BANS = [
        "यह सच है कि ", "यह बिल्कुल सच है कि ",
        "यह एक दिलचस्प प्रश्न है, ", "यह एक दिलचस्प प्रश्न है। ",
        "यह एक दिलचस्प सवाल है, ", "यह एक दिलचस्प सवाल है। ",
        "यह बहुत दिलचस्प प्रश्न है, ", "यह बहुत दिलचस्प प्रश्न है। ",
        "यह एक गहरा प्रश्न है, ", "यह एक गहरा प्रश्न है। ",
        "यह एक गहरा सवाल है, ", "यह एक गहरा सवाल है। ",
        "यह एक जटिल प्रश्न है, ", "यह एक जटिल प्रश्न है। ",
    ]
    for opener in _OPENING_BANS:
        if result.startswith(opener):
            result = result[len(opener):]
            break

    for phrase in BANNED_PHRASES_HI + BANNED_PHRASES_EN + BANNED_IDENTITY_PHRASES:
        if phrase in result:
            result = result.replace(phrase, "")

    # Clean up: double spaces, orphan punctuation, empty lines
    result = re.sub(r'  +', ' ', result)
    result = re.sub(r'^\s*[,।\.]\s*', '', result, flags=re.MULTILINE)
    # Clean orphan commas/periods from mid-sentence phrase removal
    # e.g., "साथी हूं, , जो" → "साथी हूं, जो"
    result = re.sub(r',\s*,', ',', result)
    result = re.sub(r',\s*।', '।', result)
    result = re.sub(r',\s*\.', '.', result)
    result = re.sub(r'\s+,', ',', result)  # space before comma
    # "लेकिन मैं एक , ।" → remove near-empty fragments
    result = re.sub(r'(?:लेकिन|और|पर)\s+(?:मैं\s+)?एक\s*[,।\.]\s*', '', result)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


# ─── 3-word sliding window phrase dedup ──────────────────────

# Hindi/English stop words — too common to count as meaningful overlap
_STOP_WORDS = {
    # English
    'the', 'a', 'an', 'is', 'it', 'in', 'of', 'to', 'and', 'that',
    'this', 'we', 'you', 'not', 'but', 'for', 'are', 'was', 'has',
    'have', 'with', 'from', 'our', 'your', 'can', 'be', 'do', 'as',
    'or', 'at', 'by', 'on', 'if', 'its', 'so', 'me', 'my', 'they',
    # Hindi function words
    'है', 'हैं', 'के', 'का', 'की', 'और', 'को', 'में', 'से', 'यह',
    'हम', 'हमें', 'एक', 'पर', 'कि', 'भी', 'तो', 'जो', 'वो', 'वह',
    'ने', 'या', 'इस', 'उस', 'जब', 'तब', 'लिए', 'अपने', 'अपनी',
}


def _normalize_word(w: str) -> str:
    """Lowercase + strip punctuation for comparison."""
    return w.strip('.,!?;:।,\'"()-—–').lower()


def _get_ngrams(words: list, n: int = 3) -> list:
    """Generate n-grams from content words (stop words filtered out)."""
    content_words = [w for w in words if w not in _STOP_WORDS and len(w) > 1]
    if len(content_words) < n:
        return []
    return [tuple(content_words[i:i+n]) for i in range(len(content_words) - n + 1)]


def _split_sentences(text: str) -> list:
    """Split on Hindi/English sentence boundaries.
    Returns list of (sentence_text, separator) tuples."""
    # Split after sentence-ending punctuation, keeping the punctuation with the sentence
    parts = re.split(r'(?<=[.।?!])\s+', text)
    result = []
    for p in parts:
        p = p.strip()
        if p:
            result.append(p)
    return result


def dedup_phrases(text: str) -> str:
    """3-word sliding window dedup.
    If a sentence shares >=40% of its 3-grams with previously seen sentences,
    it's a repeat and gets removed.
    Returns cleaned text."""
    if not text or len(text) < 50:
        return text

    sentences = _split_sentences(text)
    if len(sentences) < 3:
        return text

    seen_ngrams = set()
    kept = []
    removed_count = 0

    for sentence in sentences:
        words = [_normalize_word(w) for w in sentence.split() if _normalize_word(w)]
        ngrams = _get_ngrams(words)

        if not ngrams:
            # Short sentence — keep it (not enough content words to judge)
            kept.append(sentence)
            continue

        # Guard: <5 content words → only 1-2 trigrams → single match = 100% overlap
        # This would falsely drop legitimate short sentences like "हाँ, यह सच है।"
        content_words = [w for w in words if w not in _STOP_WORDS and len(w) > 1]
        if len(content_words) < 5:
            kept.append(sentence)
            seen_ngrams.update(ngrams)
            continue

        # What fraction of this sentence's ngrams are already seen?
        overlap = sum(1 for ng in ngrams if ng in seen_ngrams)
        overlap_ratio = overlap / len(ngrams)

        if overlap_ratio >= 0.4:
            # This sentence is a repeat — skip it
            removed_count += 1
            continue

        # Keep sentence + add its ngrams to seen set
        seen_ngrams.update(ngrams)
        kept.append(sentence)

    if removed_count > 0:
        print(f"🔁 phrase_dedup: removed {removed_count} repeated sentences")

    return ' '.join(kept).strip()


def truncate_crisis_response(text: str, max_sentences: int = 3) -> str:
    """
    DEPRECATED: Use utils.response_contract.enforce_contract() instead.
    Sentence truncation is now handled by ResponseContract.max_sentences.

    v7: For crisis responses — hard truncate to max_sentences.
    """
    sentences = re.split(r'(?<=[।.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= max_sentences:
        return text

    truncated = ' '.join(sentences[:max_sentences])
    print(f"✂️ Crisis truncation: {len(sentences)} → {max_sentences} sentences")
    return truncated


def clean_response(text: str, is_crisis: bool = False) -> tuple:
    """
    DEPRECATED: Use utils.response_contract.enforce_contract() instead.
    Pipeline now uses the contract system for all post-processing.

    Full post-processing: banned phrase strip + 3-word dedup.
    Returns (cleaned_text, dedup_triggered)."""
    if not text:
        return text, False

    # v7: Crisis truncation FIRST — before anything else
    if is_crisis:
        text = truncate_crisis_response(text, max_sentences=3)

    # Step 1: Strip banned phrases
    cleaned = strip_banned_phrases(text)

    # Step 2: 3-word sliding window dedup
    before_len = len(cleaned)
    cleaned = dedup_phrases(cleaned)
    dedup_triggered = len(cleaned) < before_len

    return cleaned, dedup_triggered
