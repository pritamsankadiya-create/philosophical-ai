# ============================================================
# core/concept_analyzer.py
# Pure Python concept extraction from questions
# ============================================================

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ConceptAnalysis:
    concepts: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    philosophers: List[str] = field(default_factory=list)
    intent: str = "explore"
    question_depth: str = "standard"
    language: str = "english"


# Keywords → philosophical concepts
CONCEPT_MAP = {
    # Consciousness & Self
    "consciousness": "consciousness", "conscious": "consciousness",
    "aware": "awareness", "awareness": "awareness",
    "mind": "mind", "brain": "mind",
    "self": "self", "soul": "soul", "atma": "soul", "aatma": "soul",
    "ego": "ego", "identity": "identity",
    # Hindi equivalents
    "chetna": "consciousness", "mann": "mind", "buddhi": "mind",
    "aatma": "soul", "parmatma": "divine",

    # Love & Relationships
    "love": "love", "pyar": "love", "payar": "love",
    "mohabbat": "love", "ishq": "love",
    "relationship": "love", "attachment": "attachment",
    "compassion": "compassion", "empathy": "compassion",

    # Life & Death
    "life": "life", "zindagi": "life", "jivan": "life",
    "death": "death", "maut": "death", "mrityu": "death",
    "mortality": "death", "afterlife": "death",
    "birth": "life", "existence": "existence",

    # Freedom & Will
    "freedom": "freedom", "free will": "freedom",
    "choice": "freedom", "liberation": "freedom",
    "moksha": "liberation", "mukti": "liberation",
    "azadi": "freedom",

    # Karma & Action
    "karma": "karma", "action": "karma", "deed": "karma",
    "duty": "duty", "dharma": "dharma",
    "responsibility": "duty",

    # Knowledge & Truth
    "truth": "truth", "satya": "truth", "sach": "truth",
    "knowledge": "knowledge", "gyan": "knowledge",
    "wisdom": "wisdom", "ignorance": "ignorance",

    # Happiness & Suffering
    "happiness": "happiness", "khushi": "happiness", "sukh": "happiness",
    "suffering": "suffering", "pain": "suffering",
    "dukh": "suffering", "sorrow": "suffering",
    "peace": "peace", "shanti": "peace",

    # God & Religion
    "god": "god", "ishwar": "god", "bhagwan": "god",
    "divine": "divine", "faith": "faith",
    "religion": "religion", "prayer": "prayer",
    "spirituality": "spirituality",

    # Ethics & Morality
    "good": "morality", "evil": "morality",
    "right": "morality", "wrong": "morality",
    "moral": "morality", "ethics": "morality",
    "virtue": "virtue", "sin": "morality",

    # Success & Purpose
    "success": "success", "safalta": "success",
    "failure": "failure", "asafalta": "failure",
    "purpose": "purpose", "meaning": "meaning",
    "goal": "purpose",

    # Fear & Courage
    "fear": "fear", "dar": "fear",
    "courage": "courage", "himmat": "courage",
    "hope": "hope", "vishwas": "faith",

    # Meditation & Practice
    "meditation": "meditation", "yoga": "yoga",
    "dhyana": "meditation", "mindfulness": "meditation",

    # Time & Change
    "time": "time", "change": "change",
    "impermanence": "impermanence",
}

# Concepts → philosophical traditions/themes
THEME_MAP = {
    "soul": ["vedanta", "philosophy_of_mind"],
    "consciousness": ["vedanta", "philosophy_of_mind", "buddhism"],
    "awareness": ["buddhism", "yoga", "philosophy_of_mind"],
    "mind": ["philosophy_of_mind", "yoga", "buddhism"],
    "self": ["vedanta", "existentialism"],
    "ego": ["buddhism", "vedanta"],
    "liberation": ["vedanta", "yoga", "buddhism"],
    "karma": ["gita_philosophy", "buddhism", "vedanta"],
    "dharma": ["gita_philosophy", "vedanta"],
    "duty": ["gita_philosophy", "stoicism"],
    "love": ["sufi_mysticism", "vedanta"],
    "attachment": ["buddhism", "stoicism"],
    "compassion": ["buddhism", "sufi_mysticism"],
    "suffering": ["buddhism", "stoicism", "existentialism"],
    "happiness": ["stoicism", "buddhism", "vedanta"],
    "peace": ["buddhism", "stoicism", "yoga"],
    "truth": ["vedanta", "rationalism"],
    "knowledge": ["vedanta", "rationalism"],
    "wisdom": ["stoicism", "vedanta"],
    "morality": ["gita_philosophy", "stoicism", "rationalism"],
    "virtue": ["stoicism", "gita_philosophy"],
    "god": ["vedanta", "sufi_mysticism"],
    "divine": ["vedanta", "sufi_mysticism"],
    "faith": ["sufi_mysticism", "vedanta"],
    "freedom": ["existentialism", "stoicism"],
    "existence": ["existentialism", "vedanta"],
    "meaning": ["existentialism"],
    "purpose": ["existentialism", "gita_philosophy"],
    "death": ["stoicism", "buddhism", "vedanta"],
    "life": ["existentialism", "stoicism"],
    "meditation": ["yoga", "buddhism"],
    "yoga": ["yoga"],
    "fear": ["stoicism", "existentialism"],
    "courage": ["stoicism", "gita_philosophy"],
    "hope": ["stoicism", "existentialism"],
    "success": ["gita_philosophy", "stoicism"],
    "failure": ["stoicism", "gita_philosophy"],
    "change": ["buddhism", "stoicism"],
    "impermanence": ["buddhism"],
    "time": ["buddhism", "stoicism"],
    "ignorance": ["vedanta", "buddhism"],
}

# Philosopher name detection
PHILOSOPHER_KEYWORDS = {
    "osho": "Osho", "rajneesh": "Osho",
    "krishna": "Shree Krishna", "gita": "Shree Krishna", "bhagavad": "Shree Krishna",
    "buddha": "Buddha", "gautam": "Buddha", "siddhartha": "Buddha",
    "chanakya": "Chanakya", "kautilya": "Chanakya",
    "vivekananda": "Swami Vivekananda", "vivekanand": "Swami Vivekananda",
    "kalam": "APJ Abdul Kalam", "abdul kalam": "APJ Abdul Kalam",
    "tagore": "Rabindranath Tagore", "rabindranath": "Rabindranath Tagore",
    "patanjali": "Patanjali",
    "shankaracharya": "Shankaracharya", "shankara": "Shankaracharya",
    "rumi": "Rumi",
    "marcus aurelius": "Marcus Aurelius", "aurelius": "Marcus Aurelius",
    "socrates": "Socrates",
    "plato": "Plato",
    "aristotle": "Aristotle",
    "confucius": "Confucius",
    "laozi": "Laozi", "lao tzu": "Laozi",
    "kant": "Kant", "immanuel kant": "Kant",
    "descartes": "Descartes",
    "kabir": "Kabir",
    "nanak": "Guru Nanak",
}

# Intent detection patterns
INTENT_PATTERNS = [
    (r"\bwhat\s+is\b", "define"),
    (r"\bdefine\b", "define"),
    (r"क्या\s+है", "define"),
    (r"\bhow\s+to\b", "apply"),
    (r"\bhow\s+can\b", "apply"),
    (r"\bhow\s+do\b", "apply"),
    (r"कैसे", "apply"),
    (r"\bvs\.?\b", "compare"),
    (r"\bversus\b", "compare"),
    (r"\bdifference\s+between\b", "compare"),
    (r"\bcompare\b", "compare"),
    (r"\bया\b.*\bया\b", "compare"),
    (r"\bwhy\s+not\b", "challenge"),
    (r"\bisn't\b", "challenge"),
    (r"\bwhy\s+should\b", "challenge"),
    (r"क्यों\s+नहीं", "challenge"),
]


def analyze_concepts(question: str, language: str = "english", translated: str = "") -> ConceptAnalysis:
    """
    Analyze a question to extract concepts, themes, philosophers, and intent.
    Pure Python — no LLM call needed.
    """
    analysis = ConceptAnalysis(language=language)

    # Use both original and translated for matching
    texts = [question.lower()]
    if translated and translated != question:
        texts.append(translated.lower())

    search_text = " ".join(texts)

    # Extract concepts
    found_concepts = set()
    for keyword, concept in CONCEPT_MAP.items():
        if keyword in search_text:
            found_concepts.add(concept)
    analysis.concepts = list(found_concepts)

    # Extract themes from concepts
    found_themes = set()
    for concept in analysis.concepts:
        if concept in THEME_MAP:
            for theme in THEME_MAP[concept]:
                found_themes.add(theme)
    analysis.themes = list(found_themes)

    # Detect mentioned philosophers
    found_philosophers = set()
    for keyword, name in PHILOSOPHER_KEYWORDS.items():
        if keyword in search_text:
            found_philosophers.add(name)
    analysis.philosophers = list(found_philosophers)

    # Detect intent
    analysis.intent = "explore"
    for pattern, intent in INTENT_PATTERNS:
        if re.search(pattern, search_text, re.IGNORECASE):
            analysis.intent = intent
            break

    # Determine question depth
    word_count = len(question.split())
    if word_count <= 4:
        analysis.question_depth = "simple"
    elif word_count >= 12 or analysis.intent == "compare":
        analysis.question_depth = "deep"
    else:
        analysis.question_depth = "standard"

    return analysis
