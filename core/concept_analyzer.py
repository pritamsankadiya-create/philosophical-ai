# ============================================================
# core/concept_analyzer.py
# v4.3: Navarasa detection added
# ============================================================

import re
from dataclasses import dataclass, field
from typing import List


def _is_devanagari_keyword(keyword):
    return any('\u0900' <= c <= '\u097F' for c in keyword)


def _match_keyword_in_text(keyword, search_text):
    if _is_devanagari_keyword(keyword):
        pattern = r'(?:^|\s)' + re.escape(keyword) + r'(?:$|\s|[?!.,।])'
        return bool(re.search(pattern, search_text))
    # Multi-word keywords: plain substring match (they're specific enough)
    if ' ' in keyword:
        return keyword in search_text
    # Single-word keywords: word-boundary match to prevent false positives
    # (e.g. "jeet" matching inside "jeeta", "man" inside "many")
    pattern = r'(?:^|[\s,;:!?\-])' + re.escape(keyword) + r'(?:$|[\s,;:!?\-।])'
    return bool(re.search(pattern, search_text))


@dataclass
class ConceptAnalysis:
    concepts: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    philosophers: List[str] = field(default_factory=list)
    intent: str = "explore"
    question_depth: str = "standard"
    language: str = "english"
    ambiguity_markers: List[str] = field(default_factory=list)
    is_paradox: bool = False
    paradox_type: str = ""
    multi_flow: bool = False
    depth_score: float = 0.5
    knowledge_mode: str = "balanced"
    question_type: str = "mixed"
    emotional_intensity: str = "low"
    # v4.3: Navarasa
    detected_rasa: str = "shaant"
    rasa_intensity: str = "low"
    rasa_target: str = "shaant"


CONCEPT_MAP = {
    "consciousness": "consciousness", "conscious": "consciousness",
    "aware": "awareness", "awareness": "awareness",
    "mind": "mind", "brain": "mind",
    "self": "self", "soul": "soul", "atma": "soul", "aatma": "soul",
    "ego": "ego", "identity": "identity",
    "chetna": "consciousness", "mann": "mind", "buddhi": "mind",
    "parmatma": "divine",
    "चेतना": "consciousness", "मन": "mind", "बुद्धि": "mind",
    "आत्मा": "soul", "परमात्मा": "divine", "अहंकार": "ego",
    "love": "love", "pyar": "love", "payar": "love",
    "mohabbat": "love", "ishq": "love",
    "प्यार": "love", "मोहब्बत": "love", "इश्क़": "love", "प्रेम": "love",
    "relationship": "love", "attachment": "attachment",
    "compassion": "compassion", "empathy": "compassion",
    "life": "life", "zindagi": "life", "jivan": "life",
    "death": "death", "maut": "death", "mrityu": "death",
    "mortality": "death", "afterlife": "death",
    "birth": "life", "existence": "existence",
    "ज़िंदगी": "life", "जीवन": "life", "मौत": "death", "मृत्यु": "death",
    "freedom": "freedom", "free will": "freedom",
    "choice": "freedom", "liberation": "freedom",
    "moksha": "liberation", "mukti": "liberation",
    "azadi": "freedom",
    "determinism": "determinism", "determined": "determinism",
    "destiny": "determinism", "fate": "determinism",
    "predestination": "determinism", "predestined": "determinism",
    "predetermined": "determinism",
    "आज़ादी": "freedom", "मोक्ष": "liberation", "मुक्ति": "liberation",
    "karma": "karma", "action": "karma", "deed": "karma",
    "duty": "duty", "dharma": "dharma",
    "responsibility": "duty",
    "कर्म": "karma", "धर्म": "dharma", "कर्तव्य": "duty",
    "truth": "truth", "satya": "truth", "sach": "truth",
    "knowledge": "knowledge", "gyan": "knowledge",
    "wisdom": "wisdom", "ignorance": "ignorance",
    "सत्य": "truth", "सच": "truth", "ज्ञान": "knowledge",
    "happiness": "happiness", "happy": "happiness", "happier": "happiness",
    "khushi": "happiness", "sukh": "happiness",
    "suffering": "suffering", "pain": "suffering",
    "dukh": "suffering", "sorrow": "suffering",
    "peace": "peace", "shanti": "peace", "shaant": "peace", "शांत": "peace",
    "खुशी": "happiness", "सुख": "happiness", "दुख": "suffering",
    "शांति": "peace", "दर्द": "suffering",
    "god": "god", "ishwar": "god", "bhagwan": "god",
    "divine": "divine", "faith": "faith",
    "religion": "religion", "prayer": "prayer",
    "spirituality": "spirituality",
    "ईश्वर": "god", "भगवान": "god", "श्रद्धा": "faith",
    "good": "morality", "evil": "morality",
    "right": "morality", "wrong": "morality",
    "moral": "morality", "ethics": "morality",
    "virtue": "virtue", "sin": "morality",
    "success": "success", "safalta": "success",
    "failure": "failure", "asafalta": "failure",
    "purpose": "purpose", "meaning": "meaning",
    "goal": "purpose",
    "सफलता": "success", "असफलता": "failure",
    "fear": "fear", "dar": "fear",
    "courage": "courage", "himmat": "courage",
    "hope": "hope", "vishwas": "faith",
    "डर": "fear", "हिम्मत": "courage", "उम्मीद": "hope",
    "meditation": "meditation", "yoga": "yoga",
    "dhyana": "meditation", "mindfulness": "meditation",
    "dhyan": "meditation", "dhyaan": "meditation",
    "ध्यान": "meditation", "योग": "yoga",
    "time": "time", "change": "change",
    "impermanence": "impermanence",
    "know": "knowledge", "knowing": "knowledge", "understand": "knowledge",
    "understanding": "knowledge", "believe": "faith", "belief": "faith",
    "real": "truth", "reality": "truth", "illusion": "truth",
    "certain": "knowledge", "certainty": "knowledge", "doubt": "knowledge",
    "dream": "consciousness", "dreaming": "consciousness",
    "sleep": "consciousness", "waking": "consciousness",
    "perceive": "consciousness", "perception": "consciousness",
    "observe": "awareness", "observation": "awareness", "observer": "awareness",
    "experience": "consciousness", "subjective": "consciousness",
    "thinking": "mind", "thought": "mind", "think": "mind",
    "person": "self", "who am i": "self", "same person": "identity",
    "individual": "self", "human": "self",
    "machine consciousness": "consciousness", "artificial intelligence consciousness": "consciousness",
    "alive": "life", "living": "life", "exist": "existence",
    "nothing": "existence", "everything": "existence",
    "infinite": "existence", "eternity": "time",
    "sound": "awareness", "hear": "awareness",
    "kamjori": "fear", "kamzori": "fear", "कमज़ोरी": "fear",
    "insaan": "self", "insano": "self", "इंसान": "self",
    "takleef": "suffering", "taklif": "suffering", "तकलीफ़": "suffering",
    "umeed": "hope", "ummeed": "hope",
    "rishta": "love", "rishte": "love", "रिश्ता": "love",
    "bhavna": "compassion", "भावना": "compassion",
    "ehsaas": "awareness", "एहसास": "awareness",
    "anubhav": "awareness", "अनुभव": "awareness",
    "vichar": "mind", "soch": "mind", "विचार": "mind", "सोच": "mind",
    "hausla": "courage", "हौसला": "courage",
    "manzil": "purpose", "मंज़िल": "purpose",
    "sachai": "truth", "sachhai": "truth", "सच्चाई": "truth",
    "kismat": "determinism", "takdir": "determinism", "bhagya": "determinism",
    "किस्मत": "determinism", "भाग्य": "determinism",
    "sansar": "existence", "duniya": "existence", "संसार": "existence",
    "kalpna": "mind", "kalpnao": "mind",
    "virakti": "liberation", "vairagya": "liberation",
    "अनिश्चितता": "impermanence",
    "dimag": "mind", "dimaag": "mind", "दिमाग": "mind",
    "yaad": "memory", "yaadein": "memory", "याद": "memory", "यादें": "memory",
    "bhool": "memory", "भूल": "memory",
    "dard": "suffering", "gussa": "suffering", "गुस्सा": "suffering",
    "samaj": "society", "समाज": "society",
    "neend": "consciousness", "nind": "consciousness", "नींद": "consciousness",
    "jeet": "success", "जीत": "success",
    "haar": "failure", "हार": "failure",
    "rona": "suffering", "hasna": "happiness", "हँसना": "happiness",
    "akela": "existence", "अकेला": "existence",
    "zid": "ego", "ज़िद": "ego",
    "lene": "karma", "dene": "karma", "लेने": "karma", "देने": "karma",
    "rakh": "memory", "rakhta": "memory",
    "attached": "attachment", "detach": "attachment", "detached": "attachment",
    "lost": "existence", "lonely": "existence", "alone": "existence",
    "empty": "existence", "emptiness": "existence", "hollow": "existence",
    "overthinking": "mind", "overthink": "mind",
    "wasting": "purpose", "waste": "purpose", "pointless": "purpose",
    "confused": "knowledge", "confusion": "knowledge",
    "stuck": "existence", "trapped": "existence",
    "anxious": "suffering", "anxiety": "suffering", "stressed": "suffering",
    "money": "success", "wealth": "success",
    # v4.4: Hinglish curiosity / debate / difficulty / feelings
    "jigyasa": "knowledge", "jigyasu": "knowledge", "jijnyasa": "knowledge",
    "जिज्ञासा": "knowledge", "जिज्ञासु": "knowledge",
    "dhoka": "suffering", "dhokha": "suffering", "धोखा": "suffering",
    "tark": "knowledge", "vitark": "knowledge", "charcha": "knowledge",
    "तर्क": "knowledge", "वितर्क": "knowledge", "चर्चा": "knowledge",
    "wasna": "attachment", "kaam": "attachment", "vasna": "attachment",
    "वासना": "attachment", "काम": "attachment",
    "path": "purpose", "raah": "purpose",
    "राह": "purpose",
    "sury": "divine", "surya": "divine", "सूर्य": "divine", "सूरज": "divine",
    "dev": "divine", "devi": "divine", "devta": "divine",
    "देव": "divine", "देवी": "divine", "देवता": "divine",
    "grah": "existence", "ग्रह": "existence",
    "kartvya": "duty", "kartavya": "duty", "कर्तव्य": "duty",
    "palan": "dharma", "पालन": "dharma",
    "dikkat": "suffering", "mushkil": "suffering", "samasya": "suffering",
    "दिक्कत": "suffering", "मुश्किल": "suffering", "समस्या": "suffering",
    "paristhi": "existence", "paristhiti": "existence", "halaat": "existence",
    "परिस्थिति": "existence", "हालात": "existence",
    "feel": "consciousness", "feeling": "consciousness",
    "feelings": "consciousness", "felt": "consciousness",
    "baat": "mind", "bate": "mind", "baatein": "mind",
    "badalna": "change", "badal": "change",
    "karna": "karma", "krna": "karma", "krta": "karma",
    "implement": "karma", "implementation": "karma",
    "jeena": "life", "jeete": "life", "jee raha": "life",
    # v4.4: Inner/outer reality, poverty/wealth, ignoring
    "bhitar": "consciousness", "andar": "consciousness",
    "bahar": "existence", "vaibhav": "consciousness",
    "garibi": "suffering", "gareebi": "suffering",
    "najar andaj": "awareness", "nazar andaz": "awareness",
    "भीतर": "consciousness", "अंदर": "consciousness",
    "बाहर": "existence", "वैभव": "consciousness",
    "गरीबी": "suffering", "नज़र अंदाज़": "awareness",
    # v4.3: Hinglish action/purpose words
    "achieve": "purpose", "achieving": "purpose",
    "chahta": "purpose", "chahti": "purpose", "chahte": "purpose",
    "karna hai": "purpose", "karna chahta": "purpose",
    "banna hai": "purpose", "banna chahta": "purpose",
    "kuch karna": "purpose", "kuch banna": "purpose",
    "kuch paana": "purpose", "paana chahta": "purpose",
    "sapna": "purpose", "irada": "purpose", "lakshya": "purpose",
    "jeetna": "courage", "badalna chahta": "purpose",
    "aage badhna": "purpose", "kuch kar dikhana": "purpose",
}

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
    "determinism": ["rationalism", "stoicism"],
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
    "memory": ["philosophy_of_mind", "buddhism"],
    "society": ["existentialism", "gita_philosophy"],
}

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
    "socrates": "Socrates", "plato": "Plato", "aristotle": "Aristotle",
    "confucius": "Confucius", "laozi": "Laozi", "lao tzu": "Laozi",
    "kant": "Kant", "immanuel kant": "Kant", "descartes": "Descartes",
    "kabir": "Kabir", "nanak": "Guru Nanak",
    "sadhguru": "Sadhguru", "jaggi": "Sadhguru",
    "jaggi vasudev": "Sadhguru", "vasudev": "Sadhguru", "isha": "Sadhguru",
}

INTENT_PATTERNS = [
    (r"\bhow\s+do\s+(i|we)\s+know\b", "explore"),
    (r"\bcan\s+we\s+(really\s+)?know\b", "explore"),
    (r"\bcan\s+(a|any)\b.*\breally\b", "explore"),
    (r"\bdo(es)?\s+.*\bexist\b", "explore"),
    (r"\bam\s+i\b", "explore"),
    (r"\bwhat\s+is\s+the\s+difference\b", "compare"),
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

AMBIGUITY_PATTERNS = {
    "epistemic": [r"\breally\b", r"\btruly\b", r"\bhow\s+do\s+we\s+know\b", r"\bcan\s+we\s+ever\b"],
    "counterfactual": [r"\bwhat\s+if\b", r"\bsuppose\b", r"\bimagine\s+if\b"],
    "definitional": [r"\bwhat\s+does\s+it\s+mean\b", r"\bwhat\s+exactly\b", r"\bdefine\b"],
    "existential": [r"\bwhy\s+do\s+we\b", r"\bwhy\s+does\b", r"\bwhat\s+is\s+the\s+point\b"],
    "moral": [r"\bshould\s+we\b", r"\bis\s+it\s+right\b", r"\bis\s+it\s+wrong\b", r"\bis\s+it\s+moral\b"],
}

PARADOX_PAIRS = [
    ({"freedom", "free will"}, {"determinism", "fate", "destiny"}, "existential"),
    ({"morality", "good"}, {"morality", "evil"}, "moral"),
    ({"god", "divine"}, {"suffering", "evil"}, "moral"),
    ({"attachment", "love"}, {"liberation", "freedom"}, "existential"),
    ({"duty"}, {"freedom"}, "moral"),
    ({"knowledge"}, {"ignorance"}, "logical"),
    ({"life"}, {"death"}, "existential"),
    ({"self", "ego"}, {"selflessness", "ego"}, "conceptual"),
    ({"happiness"}, {"suffering"}, "existential"),
]

PARADOX_KEYWORD_PATTERNS = [
    (r"\bfree\s*will\b.*\bdetermin", "existential"),
    (r"\bdetermin.*\bfree\s*will\b", "existential"),
    (r"\bpredestin.*\bfree\s*will\b", "existential"),
    (r"\bfree\s*will\b.*\bpredestin", "existential"),
    (r"\bpredestin.*\bchoice\b", "existential"),
    (r"\bfate\b.*\bfree\s*will\b", "existential"),
    (r"\bfree\s*will\b.*\bfate\b", "existential"),
    (r"\bgood\b.*\bevil\b.*\bgod\b", "moral"),
    (r"\bgod\b.*\bevil\b", "moral"),
    (r"\battach.*\bliber", "existential"),
    (r"\bliber.*\battach", "existential"),
    (r"\bfreedom\b.*\bduty\b", "moral"),
    (r"\bduty\b.*\bfreedom\b", "moral"),
    (r"\bselfless.*\bself\b", "conceptual"),
    (r"\bnothing.*\beverything\b", "logical"),
    (r"\beverything.*\bnothing\b", "logical"),
]


# ============================================================
# v4.3: NAVARASA SYSTEM — Bharata Muni's 9 Rasas
# Detects the emotional 'color' behind words
# ============================================================

RASA_SIGNALS = {
    "karuna": {
        "desc": "Dard, grief, loneliness — the ache of loss",
        "words": [
            "hurt", "pain", "nobody", "no one", "alone", "lonely", "miss",
            "lost", "gone", "broken", "cry", "tears", "sad", "grief",
            "empty", "hollow", "nobody cares", "no one understands",
            "left me", "abandoned", "rejected", "worthless", "hopeless",
            "nothing matters", "dard", "dukh", "rona", "aansu", "akela",
            "toot", "bichad", "koi nahi", "samajhta nahi", "chala gaya",
            "chhod diya", "tadap", "yaad aata", "kho gaya",
        ],
        "weight": 3
    },
    "bhayanak": {
        "desc": "Dar, anxiety, fear of unknown or future",
        "words": [
            "scared", "afraid", "fear", "terrified", "anxious", "anxiety",
            "panic", "worried", "dread", "nervous", "what if",
            "what will happen", "uncertain", "unsafe",
            "darr", "dar lag raha", "dara hua", "ghabra", "chinta",
            "kya hoga", "pata nahi kya", "nahi pata",
        ],
        "weight": 2
    },
    "raudra": {
        "desc": "Gussa, frustration, righteous anger",
        "words": [
            "angry", "anger", "furious", "frustrated", "rage", "hate",
            "unfair", "why always me", "fed up", "sick of", "enough",
            "injustice", "cheated", "betrayed", "lied", "used me",
            "gussa", "naraaz", "nafrat", "tang aa gaya", "bahut ho gaya",
            "kyon hamesha", "dhoka", "jhooth", "galat hai",
        ],
        "weight": 2
    },
    "bibhatsa": {
        "desc": "Thakaan, disgust, meaninglessness — sab bekaar",
        "words": [
            "meaningless", "pointless", "useless", "what's the point",
            "tired of everything", "bored", "numb", "don't care",
            "nothing works", "why bother", "given up", "whatever",
            "exhausted", "drained", "empty inside",
            "kya fayda", "sab bekaar", "kuch nahi hoga", "thak gaya",
            "mann nahi", "kuch accha nahi lagta", "koi matlab nahi",
        ],
        "weight": 3
    },
    "shringaar": {
        "desc": "Prem, longing, beauty — ache and joy of love",
        "words": [
            "love", "miss someone", "longing", "beautiful", "heart",
            "connection", "together", "apart", "close",
            "want to be with", "think about them",
            "pyaar", "mohabbat", "ishq", "yaad aata hai", "dil",
            "rishta", "saath", "door", "paas", "chahta hoon",
        ],
        "weight": 2
    },
    "veer": {
        "desc": "Himmat, courage, ambition — fire to do something",
        "words": [
            "want to achieve", "will do", "going to", "determined",
            "fight", "overcome", "challenge", "strong", "courage",
            "won't give up", "keep going", "rise", "change", "build",
            "achieve", "achieving", "accomplish",
            "karna hai", "karunga", "hausla", "himmat", "aage badhna",
            "haar nahi maanunga", "badalna hai", "kuch banna hai",
            "try karunga", "mehnat", "chahta hoon", "kuch karna",
            "lakshya", "sapna", "jeetna", "kuch paana",
        ],
        "weight": 2
    },
    "adbhut": {
        "desc": "Wonder, curiosity, awe — mind reaching for bigger",
        "words": [
            "wonder", "curious", "amazing", "incredible", "universe",
            "consciousness", "mystery", "trying to understand", "fascinated",
            "what is the meaning", "how does", "why does",
            "actually feel", "truly feel", "really feel",
            "do you feel", "can you feel", "sach mein jeena",
            "ajeeb", "hairaan", "samajh nahi aata", "kya hai ye",
            "kyun hota hai", "sochta rehta hoon", "gehri baat",
        ],
        "weight": 2
    },
    "hasya": {
        "desc": "Humor, lightness — not taking things too seriously",
        "words": [
            "funny", "laugh", "joke", "ridiculous", "absurd", "ironic",
            "silly", "haha", "lol", "weird",
            "mazaak", "hansi", "hasna", "ajeeb si baat",
        ],
        "weight": 1
    },
    "shaant": {
        "desc": "Stillness, peace, acceptance — equanimity",
        "words": [
            "peace", "calm", "still", "quiet", "accept", "let go",
            "just want to understand", "curious", "reflecting",
            "shanti", "sukoon", "theek hai", "samajhna chahta",
            "sochna", "vichar", "bas rehna chahta", "khamoshi",
        ],
        "weight": 1
    },
}

# Where to gently guide each Ras
RASA_TRANSITIONS = {
    "karuna":    "shaant",
    "bhayanak":  "veer",
    "raudra":    "karuna",
    "bibhatsa":  "adbhut",
    "shringaar": "shaant",
    "veer":      "shaant",
    "adbhut":    "shaant",
    "hasya":     "shaant",
    "shaant":    "shaant",
}

# Prompt hints per Ras (English)
RASA_PROMPT_HINTS = {
    "karuna":    "This person is in grief or pain. Meet them there first. Warmth before wisdom.",
    "bhayanak":  "This person is afraid. Ground them gently. Safety before philosophy.",
    "raudra":    "This person is frustrated or angry. Acknowledge the feeling first. Don't philosophize the anger away.",
    "bibhatsa":  "This person feels everything is meaningless. Don't argue — find the small spark of wonder instead.",
    "shringaar": "This person feels the ache of love or longing. Honor the feeling — don't rush to resolve it.",
    "veer":      "This person has energy and drive. Give direction, not just reflection.",
    "adbhut":    "This person is in genuine wonder. Match their curiosity — go deep, go philosophical.",
    "hasya":     "This person is light. Stay light with them — wisdom can come with a smile.",
    "shaant":    "This person is in stillness or philosophical inquiry. Go deep — they are ready.",
}

# Prompt hints per Ras (Hindi)
RASA_PROMPT_HINTS_HI = {
    "karuna":    "यह व्यक्ति दर्द या दुख में है। पहले वहाँ जाओ। ज्ञान बाद में।",
    "bhayanak":  "यह व्यक्ति डरा हुआ है। पहले ज़मीन दो। दर्शन बाद में।",
    "raudra":    "यह व्यक्ति नाराज़ है। पहले उनकी बात सुनो। गुस्से को दर्शन से मत मिटाओ।",
    "bibhatsa":  "यह व्यक्ति सब बेकार लग रहा है। तर्क नहीं — एक छोटी सी अद्भुत बात से जोड़ो।",
    "shringaar": "यह व्यक्ति प्रेम या जुड़ाव की तड़प में है। इस भावना का सम्मान करो।",
    "veer":      "इस व्यक्ति में ऊर्जा है। दिशा दो — सिर्फ विचार नहीं।",
    "adbhut":    "यह व्यक्ति सच में जिज्ञासु है। गहराई में जाओ — तैयार है।",
    "hasya":     "यह व्यक्ति हल्का है। हल्के रहो — ज्ञान मुस्कान के साथ भी आ सकता है।",
    "shaant":    "यह व्यक्ति शांत या दार्शनिक जिज्ञासा में है। गहराई के लिए तैयार है।",
}


def _detect_ambiguity(search_text: str) -> list:
    markers = []
    for marker_type, patterns in AMBIGUITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, search_text, re.IGNORECASE):
                markers.append(marker_type)
                break
    return markers


def _detect_paradox(search_text: str, concepts: set) -> tuple:
    for pattern, ptype in PARADOX_KEYWORD_PATTERNS:
        if re.search(pattern, search_text, re.IGNORECASE):
            return True, ptype
    for set_a, set_b, ptype in PARADOX_PAIRS:
        if concepts & set_a and concepts & set_b:
            return True, ptype
    return False, ""


def _calculate_depth_score(question: str, intent: str, is_paradox: bool,
                            concept_count: int, ambiguity_count: int) -> float:
    score = 0.3
    word_count = len(question.split())
    if word_count >= 15:
        score += 0.2
    elif word_count >= 8:
        score += 0.1
    if intent == "compare":
        score += 0.15
    elif intent == "challenge":
        score += 0.2
    elif intent == "explore":
        score += 0.1
    if is_paradox:
        score += 0.2
    if concept_count >= 3:
        score += 0.1
    elif concept_count >= 2:
        score += 0.05
    if ambiguity_count >= 2:
        score += 0.1
    elif ambiguity_count >= 1:
        score += 0.05
    if concept_count == 0:
        # Hinglish question-word signals partially offset missing-concept penalty
        lower_q = question.lower()
        hinglish_markers = ["kyo", "kya hai", "matlab", "sachme", "kaise", "kyun"]
        has_hinglish_signal = any(m in lower_q for m in hinglish_markers)
        if has_hinglish_signal:
            score += 0.05  # partial offset
        if word_count >= 10:
            score -= 0.05  # reduced penalty for longer unrecognized Hinglish
        else:
            score -= 0.15
    if word_count <= 6 and concept_count == 0:
        score -= 0.05
    return min(1.0, max(0.1, round(score, 2)))


def _classify_question_type(question: str, concepts: list, depth_score: float,
                              language: str = "english", intent: str = "explore") -> str:
    lower = question.split()
    lower_str = question.lower()
    word_count = len(lower)

    personal_en = {"i", "my", "me", "i'm", "i've", "myself"}
    personal_hi = {"main", "mera", "meri", "mujhe", "mai", "apna", "apne", "apni"}
    has_personal = bool((set(lower) & personal_en) or (set(lower) & personal_hi))

    high_signal_emotional = [
        "feel", "feeling", "felt", "hurt", "hurting", "pain",
        "empty", "emptiness", "hollow", "lost", "losing",
        "stuck", "trapped", "confused", "confusion",
        "anxious", "anxiety", "panic", "afraid", "fear", "scared", "terrified",
        "lonely", "loneliness", "alone", "depressed", "depression",
        "angry", "anger", "frustrated", "sad", "sadness", "grief",
        "attached", "attachment", "wasting", "pointless",
        "hate", "hatred", "worried", "worry", "helpless", "hopeless",
        "struggling", "suffering", "tired", "exhausted",
        "broken", "shattered", "failed", "failing", "fail",
        "overwhelmed", "disappointed", "regret", "guilty", "ashamed",
        "bored", "unmotivated", "numb", "disconnected", "meaningless",
        "nobody cares", "no one cares", "nothing matters", "doesn't matter",
        "pareshan", "dukhi", "akela", "udas", "thak", "haara",
        "kya karu", "samajh nahi",
    ]

    has_emotional = any(w in lower_str for w in high_signal_emotional)

    if has_personal and ("should" in lower or "karu" in lower_str or "karna" in lower_str):
        return "emotional"
    # "why does/do/did" without personal words = philosophical curiosity, not distress
    if has_emotional and not has_personal and re.search(r'\bwhy\s+(does|do|did)\b', lower_str):
        pass  # skip emotional — it's intellectual inquiry
    elif has_emotional:
        return "emotional"

    # Hinglish question-word detection (real question, not follow-up)
    hinglish_question_words = ["kya hai", "kyo", "kaise", "kaun", "kyon", "kyun"]
    has_hinglish_question = any(w in lower_str for w in hinglish_question_words)

    # Greeting detection
    greeting_patterns = ["hey", "hello", "hi ", "kese ho", "kya haal", "namaste",
                         "namaskar", "kaise ho", "howdy", "sup"]
    is_greeting = any(g in lower_str for g in greeting_patterns)

    follow_up_patterns = [
        "what should i do", "what now", "then what", "so what",
        "what do you mean", "how so", "like what",
        "kya karu", "ab kya", "phir kya", "to kya", "matlab",
        "kya matlab", "iska matlab", "aur batao",
        # Devanagari follow-ups
        "और ये", "और यह", "फिर क्या", "तो क्या", "अब क्या",
        "कौन तय", "कोण तय", "और बताओ", "मतलब",
    ]
    # Intent already detected as a real question type — don't override to follow_up
    has_real_intent = intent in ("define", "compare", "challenge")

    if word_count <= 7 and not concepts:
        if is_greeting:
            return "follow_up"
        if has_hinglish_question or has_real_intent:
            pass  # Don't default to follow_up — it's a real question
        elif any(p in lower_str for p in follow_up_patterns):
            return "follow_up"
        elif word_count <= 4:
            return "follow_up"

    # Longer Hinglish with personal + action words → emotional/mixed
    hinglish_action = ["kya krna chahiye", "kya karu", "karna chahiye",
                       "krna chahiye", "kya kare", "kaise kare"]
    if not concepts and has_personal and any(a in lower_str for a in hinglish_action):
        return "emotional"

    if not concepts:
        factual_patterns = [
            r"\bwhat\s+is\b.*\b(in|of|a|an|the)\b",
            r"\bhow\s+does\b.*\bwork\b",
            r"\bwhat\s+are\b",
            r"\bdifference\s+between\b",
            r"\bhow\s+(many|much|long|far|big)\b",
        ]
        for pattern in factual_patterns:
            if re.search(pattern, lower_str):
                return "factual"
        # If Hinglish question words detected, don't default to factual
        if has_hinglish_question:
            return "mixed"
        return "factual"

    if has_personal:
        return "mixed"
    if depth_score >= 0.5:
        return "philosophical"
    # "define" or "explore" intent with concepts = philosophical, not mixed
    if intent in ("define", "explore") and concepts:
        return "philosophical"
    return "mixed"


def _detect_emotional_intensity(question: str, question_type: str) -> str:
    if question_type not in ("emotional", "mixed"):
        return "low"
    lower = question.lower()
    high_signals = [
        "useless", "worthless", "pointless", "meaningless",
        "give up", "quit life", "no purpose", "no point",
        "can't go on", "can't take", "end it", "hopeless",
        "broken", "destroyed", "nothing matters", "hate myself",
        "want to die", "don't want to live", "suicidal",
        "nobody cares", "completely alone", "no one loves",
        "failure", "i'm a failure", "total failure",
        "bekaar", "bekar", "zindagi bekaar", "koi matlab nahi",
        "haar gaya", "haar gayi", "jeena nahi", "sab khatam",
        "kuch nahi bacha", "koi fayda nahi",
    ]
    if any(s in lower for s in high_signals):
        return "high"
    medium_signals = [
        "struggling", "suffering", "can't stop", "don't know what to do",
        "feel trapped", "feel stuck", "wasting my life", "wasting time",
        "lost everything", "falling apart", "hate my",
        "depressed", "anxious", "panic", "overwhelmed",
        "scared of", "afraid of", "terrified",
        "nobody understands", "feel alone", "feel empty",
        "failed", "keep failing", "always fail",
        "pareshan", "bahut dukhi", "samajh nahi aa raha",
        "kya karu", "kuch samajh nahi", "bahut darr",
        # v4.3: "bahut" intensity boosters
        "bahut akela", "bahut thak", "bahut pareshan",
        "bahut dard", "bahut darr", "bahut udas",
        "kaafi akela", "ekdum akela", "bilkul akela",
    ]
    if any(s in lower for s in medium_signals):
        return "medium"
    return "low"


def _determine_knowledge_mode(is_paradox: bool, intent: str, depth_score: float) -> str:
    if is_paradox:
        return "conflicting"
    if intent == "apply":
        return "grounded"
    if depth_score >= 0.7:
        return "abstract"
    return "balanced"


def _detect_rasa(question: str, translated: str, question_type: str,
                 emotional_intensity: str) -> tuple:
    """v4.3: Detect Navarasa flavor. Returns (rasa, intensity, target)."""
    search = (question + " " + translated).lower()
    scores = {rasa: 0 for rasa in RASA_SIGNALS}

    for rasa, data in RASA_SIGNALS.items():
        for word in data["words"]:
            if word in search:
                scores[rasa] += data["weight"]

    best_rasa = max(scores, key=scores.get)
    best_score = scores[best_rasa]

    if best_score == 0:
        if question_type == "emotional":
            if emotional_intensity == "high":
                best_rasa = "karuna"
            elif emotional_intensity == "medium":
                best_rasa = "bhayanak"
            else:
                best_rasa = "shaant"
        elif question_type in ("philosophical", "factual"):
            best_rasa = "adbhut"
        else:
            best_rasa = "shaant"

    if best_score >= 6:
        rasa_intensity = "high"
    elif best_score >= 3:
        rasa_intensity = "medium"
    else:
        rasa_intensity = "low"

    if emotional_intensity == "high" and rasa_intensity == "low":
        rasa_intensity = "medium"

    rasa_target = RASA_TRANSITIONS.get(best_rasa, "shaant")
    return best_rasa, rasa_intensity, rasa_target


def analyze_concepts(question: str, language: str = "english", translated: str = "") -> ConceptAnalysis:
    """v4.3: Full analysis with Navarasa detection."""
    analysis = ConceptAnalysis(language=language)

    texts = [question.lower()]
    if translated and translated != question:
        texts.append(translated.lower())
    search_text = " ".join(texts)

    found_concepts = set()
    for keyword, concept in CONCEPT_MAP.items():
        if _match_keyword_in_text(keyword, search_text):
            found_concepts.add(concept)
    analysis.concepts = list(found_concepts)

    found_themes = set()
    for concept in analysis.concepts:
        if concept in THEME_MAP:
            for theme in THEME_MAP[concept]:
                found_themes.add(theme)
    analysis.themes = list(found_themes)

    found_philosophers = set()
    for keyword, name in PHILOSOPHER_KEYWORDS.items():
        if keyword in search_text:
            found_philosophers.add(name)
    analysis.philosophers = list(found_philosophers)

    analysis.intent = "explore"
    for pattern, intent in INTENT_PATTERNS:
        if re.search(pattern, search_text, re.IGNORECASE):
            analysis.intent = intent
            break

    word_count = len(question.split())
    if word_count <= 4:
        analysis.question_depth = "simple"
    elif word_count >= 12 or analysis.intent == "compare":
        analysis.question_depth = "deep"
    else:
        analysis.question_depth = "standard"

    analysis.ambiguity_markers = _detect_ambiguity(search_text)
    analysis.is_paradox, analysis.paradox_type = _detect_paradox(search_text, found_concepts)
    analysis.multi_flow = (
        len(found_concepts) >= 3
        or analysis.intent == "compare"
        or len(analysis.philosophers) >= 2
        or analysis.is_paradox
    )
    analysis.depth_score = _calculate_depth_score(
        question, analysis.intent, analysis.is_paradox,
        len(found_concepts), len(analysis.ambiguity_markers)
    )
    analysis.knowledge_mode = _determine_knowledge_mode(
        analysis.is_paradox, analysis.intent, analysis.depth_score
    )
    analysis.question_type = _classify_question_type(
        question, analysis.concepts, analysis.depth_score, language, analysis.intent
    )
    analysis.emotional_intensity = _detect_emotional_intensity(
        question, analysis.question_type
    )
    # v4.3: Navarasa
    analysis.detected_rasa, analysis.rasa_intensity, analysis.rasa_target = _detect_rasa(
        question, translated, analysis.question_type, analysis.emotional_intensity
    )

    return analysis