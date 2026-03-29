# ============================================================
# core/concept_analyzer.py
# v3: Navarasa detection added
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
    # v3: Navarasa
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
    "breath": "life", "breathing": "life",
    "prana": "consciousness", "praana": "consciousness",
    "swas": "life", "saans": "life", "swansh": "life",
    "श्वास": "life", "स्वास": "life", "साँस": "life", "सांस": "life",
    "प्राण": "consciousness",
    "life": "life", "zindagi": "life", "jivan": "life",
    "death": "death", "maut": "death", "mrityu": "death",
    "mortality": "death", "afterlife": "death",
    "birth": "life", "existence": "existence",
    "ज़िंदगी": "life", "जीवन": "life", "मौत": "death", "मृत्यु": "death",
    "freedom": "freedom", "free will": "freedom",
    "choice": "freedom", "liberation": "freedom",
    "moksha": "liberation", "mukti": "liberation",
    "azadi": "freedom", "azaad": "freedom",
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
    "suffering": "suffering", "pain": "suffering", "painful": "suffering",
    "dukh": "suffering", "sorrow": "suffering",
    "kasht": "suffering", "kashtdayak": "suffering", "kastdayak": "suffering",
    "peeda": "suffering", "pida": "suffering", "taklif": "suffering",
    "peace": "peace", "shanti": "peace", "shaant": "peace", "शांत": "peace",
    "sukoon": "peace", "sukun": "peace",
    "सुकून": "peace", "चैन": "peace",
    "ladai": "courage", "ladaai": "courage", "sangharsh": "courage",
    "लड़ाई": "courage", "संघर्ष": "courage",
    "loss": "suffering", "lose": "suffering",
    "choot": "suffering", "chhoot": "suffering", "छूट": "suffering",
    "खुशी": "happiness", "सुख": "happiness", "दुख": "suffering",
    "शांति": "peace", "दर्द": "suffering",
    "कष्ट": "suffering", "कष्टदायक": "suffering", "कस्टदायक": "suffering",
    "पीड़ा": "suffering", "तकलीफ": "suffering", "तकलीफ़": "suffering",
    "मानव": "self", "जीवन": "life", "जीना": "life",
    "god": "god", "ishwar": "god", "bhagwan": "god",
    "divine": "divine", "faith": "faith",
    "religion": "religion", "prayer": "prayer",
    "spirituality": "spirituality",
    "ईश्वर": "god", "भगवान": "god", "श्रद्धा": "faith",
    # v3: Spiritual / Vedantic vocabulary
    "om": "divine", "ॐ": "divine", "aum": "divine",
    "mantra": "meditation", "मंत्र": "meditation",
    "gayatri": "divine", "गायत्री": "divine",
    "chanting": "meditation", "chant": "meditation",
    "उचारन": "meditation", "उच्चारण": "meditation", "जाप": "meditation",
    "srishti": "existence", "सृष्टि": "existence", "creation": "existence",
    "urja": "divine", "ऊर्जा": "divine", "energy": "divine",
    "sattvic": "dharma", "satvik": "dharma", "sattvik": "dharma",
    "सात्विक": "dharma", "सात्विकता": "dharma",
    "shakahari": "dharma", "शाकाहारी": "dharma", "vegetarian": "dharma",
    "shuddh": "dharma", "शुद्ध": "dharma", "pure": "dharma", "purity": "dharma",
    "aahar": "dharma", "आहार": "dharma",
    "puja": "faith", "पूजा": "faith", "pooja": "faith",
    "bhakti": "faith", "भक्ति": "faith", "devotion": "faith",
    "tap": "meditation", "tapasya": "meditation", "तपस्या": "meditation",
    "sadhna": "meditation", "साधना": "meditation",
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
    "jeet": "success", "jeetne": "success", "जीत": "success",
    "haar": "failure", "हार": "failure",
    "rona": "suffering", "hasna": "happiness", "हँसना": "happiness",
    "akela": "existence", "अकेला": "existence",
    "zid": "ego", "ज़िद": "ego",
    "lene": "karma", "dene": "karma", "लेने": "karma", "देने": "karma",
    # "rakh"/"rakhta" removed — too ambiguous (means "keep", not "remember")
    "attached": "attachment", "detach": "attachment", "detached": "attachment",
    "lost": "existence", "lonely": "existence", "alone": "existence",
    "empty": "existence", "emptiness": "existence", "hollow": "existence",
    "overthinking": "mind", "overthink": "mind",
    "wasting": "purpose", "waste": "purpose", "pointless": "purpose",
    "confused": "knowledge", "confusion": "knowledge",
    "stuck": "existence", "trapped": "existence",
    "anxious": "suffering", "anxiety": "suffering", "stressed": "suffering",
    "bekaar": "existence", "bekar": "existence",
    "money": "success", "wealth": "success",
    # v3: Hinglish curiosity / debate / difficulty / feelings
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
    "फील": "consciousness", "महसूस": "consciousness",
    "baat": "mind", "bate": "mind", "baatein": "mind",
    "badalna": "change", "badal": "change",
    "karna": "karma", "krna": "karma", "krta": "karma",
    "implement": "karma", "implementation": "karma",
    "jeena": "life", "jeete": "life", "jee raha": "life",
    # v3: Inner/outer reality, poverty/wealth, ignoring
    "bhitar": "consciousness", "andar": "consciousness",
    "bahar": "existence", "vaibhav": "consciousness",
    "garibi": "suffering", "gareebi": "suffering",
    "najar andaj": "awareness", "nazar andaz": "awareness",
    "भीतर": "consciousness", "अंदर": "consciousness",
    "बाहर": "existence", "वैभव": "consciousness",
    "गरीबी": "suffering", "नज़र अंदाज़": "awareness",
    # v3: Hinglish action/purpose words
    "achieve": "purpose", "achieving": "purpose",
    "chahta": "purpose", "chahti": "purpose", "chahte": "purpose",
    "karna hai": "purpose", "karna chahta": "purpose",
    "banna hai": "purpose", "banna chahta": "purpose",
    "kuch karna": "purpose", "kuch banna": "purpose",
    "kuch paana": "purpose", "paana chahta": "purpose",
    "sapna": "purpose", "irada": "purpose", "lakshya": "purpose",
    "jeetna": "courage", "badalna chahta": "purpose",
    "aage badhna": "purpose", "kuch kar dikhana": "purpose",
    # v3: Technology / future / human-machine / relationship / improvement
    "machine": "consciousness", "machines": "consciousness",
    "robot": "consciousness", "robots": "consciousness",
    "ai": "consciousness", "artificial intelligence": "consciousness",
    "computer": "consciousness", "computers": "consciousness",
    "technology": "consciousness", "tech": "consciousness",
    "मशीन": "consciousness", "मशीनों": "consciousness",
    "रोबोट": "consciousness", "तकनीक": "consciousness",
    "कंप्यूटर": "consciousness",
    "future": "existence", "bhavishya": "existence",
    "भविष्य": "existence",
    "sambandh": "love", "संबंध": "love",
    "vikas": "purpose", "vikasit": "purpose",
    "विकास": "purpose", "विकसित": "purpose",
    "sudhar": "purpose", "sudhaar": "purpose",
    "सुधार": "purpose",
    "tarika": "knowledge", "tarike": "knowledge",
    "तरीका": "knowledge", "तरीके": "knowledge",
    "samjh": "knowledge", "samjhna": "knowledge",
    "समझ": "knowledge", "समझना": "knowledge",
    "rasta": "purpose", "raasta": "purpose",
    "रास्ता": "purpose",
    "इंसानों": "self",
    "simulation": "consciousness", "virtual": "consciousness",
    "progress": "purpose", "evolution": "existence",
    "develop": "purpose", "development": "purpose",
    "connect": "love", "connection": "love",
    "bond": "love", "bonding": "love",
    "coexist": "existence", "coexistence": "existence",
    # v3: Emotional support / help / depression words
    "depressed": "suffering", "depression": "suffering",
    "mental health": "mind", "mental": "mind",
    "emotionally": "compassion", "emotional": "compassion",
    "support": "compassion", "help me": "compassion",
    "sahara": "compassion", "madad": "compassion",
    "सहारा": "compassion", "मदद": "compassion",
    "भावनात्मक": "compassion", "डिप्रेशन": "suffering",
    "डिप्रेस": "suffering",
    "opposite": "morality", "opposit": "morality",
    "उलट": "morality", "विपरीत": "morality",
    "behave": "self", "behavior": "self", "behaviour": "self",
    "व्यवहार": "self",
    "dost": "friendship", "friend": "friendship", "friends": "friendship",
    "friendship": "friendship", "doston": "friendship",
    "दोस्त": "friendship", "दोस्ती": "friendship", "मित्र": "friendship",
    "दोस्तों": "friendship", "मित्रता": "friendship",
    # v3: Moral/change/determination vocabulary
    "बुरा": "morality", "galat": "morality", "गलत": "morality",
    "बदलना": "change", "बदल": "change",
    "तैयार": "courage", "taiyar": "courage",
    "निश्चय": "courage", "nischay": "courage",
    # v4: Missing Hinglish vocab (trace analysis fixes)
    "weakness": "fear", "weekness": "fear",
    "pariwar": "family", "parivaar": "family", "parivar": "family",
    "परिवार": "family", "family": "family",
    "jimmedari": "duty", "jimmedariyon": "duty", "zimmadari": "duty", "zimmedari": "duty",
    "ज़िम्मेदारी": "duty", "ज़िम्मेदारियों": "duty", "responsibility": "duty",
    "wartman": "mindfulness", "vartman": "mindfulness", "vartmaan": "mindfulness",
    "वर्तमान": "mindfulness", "present moment": "mindfulness",
    "mindful": "mindfulness",
    "vicharo": "mind", "विचारों": "mind",
    "shant": "peace", "शांत": "peace",
    "tivra": "mind", "तीव्र": "mind",
    "intensity": "mind", "intense": "mind",
    # v4: Silence / quietude concept
    "silence": "silence", "silent": "silence", "quiet": "silence",
    "moun": "silence", "maun": "silence", "मौन": "silence",
    "khamoshi": "silence", "खामोशी": "silence",
    # v4: Difference / comparison words
    "farak": "knowledge", "farq": "knowledge", "फ़र्क": "knowledge",
    "antar": "knowledge", "अंतर": "knowledge",
    "duskh": "suffering", "khushiya": "happiness", "khushiyan": "happiness",
    "खुशियाँ": "happiness",
    # v4: Decision / conflict / focus concepts
    "focus": "mind", "focusing": "mind", "concentrate": "mind", "concentration": "mind",
    "attention": "mind", "distracted": "mind", "distraction": "mind",
    "conflict": "suffering", "against each other": "suffering",
    "working against": "suffering", "inner conflict": "suffering",
    "harmony": "peace", "balance": "peace", "balanced": "peace",
    "decision": "morality", "right decision": "morality",
    "brain": "mind", "heart": "mind",
    # v4: Relationship words — philosophical in context of identity exploration
    "brother": "love", "sister": "love",
    "father": "duty", "mother": "compassion",
    "wife": "love", "husband": "duty",
    "parent": "duty", "parents": "duty",
    "child": "love", "children": "love",
    "son": "love", "daughter": "love",
    "role": "duty", "roles": "duty",
    # Hindi relationship words
    "bhai": "love", "भाई": "love",
    "behan": "love", "बहन": "love", "behen": "love",
    "pita": "duty", "pitaji": "duty", "पिता": "duty", "पिताजी": "duty",
    "baap": "duty", "बाप": "duty",
    "mata": "compassion", "mataji": "compassion", "माता": "compassion", "माताजी": "compassion",
    "maa": "compassion", "माँ": "compassion", "ma": "compassion",
    "patni": "love", "पत्नी": "love",
    "pati": "duty", "पति": "duty",
    "beta": "love", "बेटा": "love", "beti": "love", "बेटी": "love",
    "bachcha": "love", "bachche": "love", "बच्चा": "love", "बच्चे": "love",
    "biwi": "love", "बीवी": "love",
    "rishtedaar": "love", "रिश्तेदार": "love",
    "bhabhee": "love", "bhabhi": "love",
    # v4: Respect / honor / desire / obsession vocabulary
    "respect": "identity", "self-respect": "identity", "self-worth": "identity",
    "disrespect": "identity", "dignity": "identity",
    "honor": "identity", "honour": "identity", "reputation": "identity",
    "recognition": "identity", "status": "identity",
    "izzat": "identity", "इज़्ज़त": "identity",
    "samman": "identity", "सम्मान": "identity",
    "maan": "identity",
    "desire": "attachment", "desiring": "attachment", "craving": "attachment",
    "wanting": "attachment", "longing": "attachment", "greed": "attachment",
    "obsessed": "attachment", "obsession": "attachment", "engrossed": "attachment",
    "addicted": "attachment", "addiction": "attachment",
    "futile": "purpose", "futility": "purpose",
    "ichha": "attachment", "इच्छा": "attachment",
    "lalach": "attachment", "लालच": "attachment",
    "lobh": "attachment", "लोभ": "attachment",
    "trishna": "attachment", "तृष्णा": "attachment",
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
    "technology": ["philosophy_of_mind", "existentialism", "rationalism"],
    "friendship": ["sufi_mysticism", "stoicism", "existentialism"],
    "family": ["gita_philosophy", "vedanta", "existentialism"],
    "mindfulness": ["buddhism", "yoga", "vedanta"],
    "silence": ["buddhism", "yoga", "vedanta"],
    "identity": ["vedanta", "existentialism", "buddhism"],
    "prayer": ["sufi_mysticism", "vedanta", "yoga"],
    "religion": ["vedanta", "gita_philosophy", "sufi_mysticism"],
    "spirituality": ["vedanta", "yoga", "buddhism", "sufi_mysticism"],
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
    "turing": "Alan Turing", "alan turing": "Alan Turing",
    "charvaka": "Charvaka", "charvak": "Charvaka",
    "shiva": "Shiva", "shiv": "Shiva", "mahadev": "Shiva",
    "शिव": "Shiva", "महादेव": "Shiva", "शंकर": "Shiva",
    "vishnu": "Vishnu", "विष्णु": "Vishnu",
    "rama": "Shree Rama", "ram": "Shree Rama", "राम": "Shree Rama",
    "hanuman": "Hanuman", "हनुमान": "Hanuman",
    "durga": "Durga", "दुर्गा": "Durga", "काली": "Durga",
    "ganesh": "Ganesh", "ganesha": "Ganesh", "गणेश": "Ganesh",
}

INTENT_PATTERNS = [
    (r"\bhow\s+do\s+(i|we)\s+know\b", "explore"),
    (r"\bcan\s+we\s+(really\s+)?know\b", "explore"),
    (r"\bcan\s+(a|any)\b.*\breally\b", "explore"),
    (r"\bdo(es)?\s+.*\bexist\b", "explore"),
    (r"\bam\s+i\b", "explore"),
    (r"\bwhat\s+is\s+the\s+difference\b", "compare"),
    (r"\bwhat\s+is\b", "define"),
    (r"\bwho\s+is\b", "define"),
    (r"\bdefine\b", "define"),
    (r"क्या\s+है", "define"),
    (r"\bkaun\s+(?:hai|hota|hoti)\b", "define"),
    (r"कौन\s+(?:है|होता|होती)", "define"),
    (r"\bhow\s+to\b", "apply"),
    (r"\bhow\s+can\b", "apply"),
    (r"\bhow\s+do\b", "apply"),
    (r"कैसे", "apply"),
    (r"\bvs\.?\b", "compare"),
    (r"\bversus\b", "compare"),
    (r"\bdifference\s+between\b", "compare"),
    (r"\bcompare\b", "compare"),
    (r"\bया\b.*\bया\b", "compare"),
    (r"\bya\b.*\bya\b", "compare"),
    (r"\bchahiye\s+ya\b", "compare"),
    (r"\bkaru\s+ya\b", "compare"),
    # v4: Hinglish/Hindi compare patterns (diffrence/farak/antar)
    (r"\b(?:diff(?:e)?rence|farak|farq|antar)\b", "compare"),
    (r"(?:में|me)\s+(?:क्या|kya)\s+(?:diff|farak|farq|antar|अंतर|फ़र्क)", "compare"),
    (r"(?:अंतर|फ़र्क)\s+(?:क्या|kya)\s+(?:है|hai)", "compare"),
    (r"\bor\b.*\bme\s+kya\b", "compare"),
    (r"\b(?:don't|doesn't)\s+(?:find|see)\b", "challenge"),
    (r"\b(?:don't|doesn't)\s+feel\s+(?:any|the|much|enough|like\s+it)\b", "challenge"),
    (r"\bno\s+(?:depth|substance|meaning)\b", "challenge"),
    (r"\bnot\s+good\s+enough\b", "challenge"),
    (r"\blacks\s+depth\b", "challenge"),
    (r"\b(?:shallow|superficial|generic|repetitive)\b", "challenge"),
    (r"नहीं\s+(?:लगता|दिखता|मिलता)", "challenge"),
    (r"गहराई\s+नहीं", "challenge"),
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
    ({"virtue"}, {"morality"}, "moral"),
    ({"god", "divine"}, {"suffering", "evil"}, "moral"),
    ({"attachment", "love"}, {"liberation", "freedom"}, "existential"),
    ({"duty"}, {"freedom"}, "moral"),
    ({"knowledge"}, {"ignorance"}, "logical"),
    ({"life"}, {"death"}, "existential"),
    ({"self"}, {"ego"}, "conceptual"),
    ({"happiness"}, {"suffering"}, "existential"),
    # v4: Concept-pair paradoxes for Hindi/mindfulness questions
    ({"peace"}, {"mind"}, "experiential"),
    ({"mindfulness"}, {"family", "duty"}, "existential"),
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
    # v4: Hindi/Hinglish paradox patterns — suppression paradox (X → opposite of X)
    (r"shant\s+karne\s+se.*(?:jyada|badh|tivra|tej)", "experiential"),
    (r"(?:rok|ruk|band\s+kar|control).*(?:jyada|badh|tivra|tej)", "experiential"),
    (r"शांत.*(?:तीव्र|बढ़|ज़्यादा)", "experiential"),
    (r"(?:रोक|बंद\s+कर).*(?:तीव्र|बढ़|ज़्यादा)", "experiential"),
    (r"\b(?:suppress|silence|stop|control)\w*\s+(?:thought|mind).*\b(?:stronger|more|intense|louder|worse)\b", "experiential"),
    (r"\b(?:trying|try)\s+(?:to\s+)?(?:not|stop|silence|suppress)\b.*\b(?:more|stronger|worse|intense)\b", "experiential"),
]


# ============================================================
# v3: NAVARASA SYSTEM — Bharata Muni's 9 Rasas
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
            "kasht", "kashtdayak", "kastdayak", "peeda", "pida",
            "कष्ट", "कष्टदायक", "कस्टदायक", "पीड़ा", "painful",
            "depressed", "depression", "emotionally", "emotional support",
            "need help", "need support", "sahara", "madad",
            "डिप्रेशन", "डिप्रेस", "भावनात्मक", "सहारा", "मदद",
            "bad person", "galat kaam", "गलत काम", "बुरा इंसान",
            "guilt", "guilty", "shame", "ashamed", "regret",
            "kya karu", "क्या करू", "क्या करूँ",
            # v4: Self-criticism / self-directed distress
            "upset with myself", "upset with me", "hate myself",
            "angry at myself", "disappointed in myself", "frustrated with myself",
            "feel bad about myself", "blame myself", "my fault",
            "upset", "let down", "let myself down",
            # v4.4: Negated peace / post-victory emptiness (Q7 fix)
            "sukoon nahi", "sukun nahi", "chain nahi",
            "peace remains elusive", "something left behind",
            "even after victory", "jeet ke baad bhi",
            "phir bhi khali", "still empty", "no peace",
            "kuch choot gaya", "kuch chhoot gaya",
            "सुकून नहीं", "चैन नहीं", "कुछ छूट गया",
            "जीत के बाद भी", "लड़ाई के बाद भी",
            "phir bhi sukoon nahi", "after winning still",
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
            "डर", "घबरा", "चिंता", "भय", "आशंका", "क्या होगा",
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
            "गुस्सा", "नाराज़", "नफ़रत", "धोखा", "झूठ", "क्रोध", "अन्याय",
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
            "kya fayda", "sab bekaar", "bekaar", "bekar",
            "kuch nahi hoga", "thak gaya",
            "mann nahi", "kuch accha nahi lagta", "koi matlab nahi",
            "achieve nahi", "nahi kar pa", "nahi ho pa",
            "क्या फ़ायदा", "सब बेकार", "बेकार", "थक गया", "मन नहीं", "कोई मतलब नहीं",
        ],
        "weight": 3
    },
    "shringaar": {
        "desc": "Prem, longing, beauty — ache and joy of love",
        "words": [
            "love", "miss someone", "longing", "beautiful",
            "my heart", "broken heart", "heart aches",
            "connection", "together", "apart", "close",
            "want to be with", "think about them",
            "pyaar", "mohabbat", "ishq", "yaad aata hai", "dil",
            "rishta", "mere saath", "tere saath", "door", "mere paas", "tere paas", "chahta hoon",
            "प्यार", "मोहब्बत", "इश्क़", "दिल", "रिश्ता", "मेरे साथ", "तेरे साथ", "दूर",
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
            "lakshya", "sapna", "jeetna", "jeetne", "kuch paana",
            "kar dikhana", "kar dikhaunga", "kar dikha",
            "haar maan", "haar nahi",
            "ready", "taiyar", "तैयार", "nischay", "निश्चय",
            "decide", "decided", "move on", "move forward",
            "बदलना चाहता", "आगे बढ़", "बढ़ता",
            "चाहता हूँ", "बदलना", "जीतना", "जीतने",
            "कर दिखाना", "कर दिखाऊंगा",
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
            "भविष्य", "विकसित", "संबंध", "मशीन", "तकनीक",
            "sambandh", "bhavishya", "vikasit", "machine",
            "sudhar", "sudhaar", "tarika", "samjhna",
        ],
        "weight": 2
    },
    "hasya": {
        "desc": "Humor, lightness — not taking things too seriously",
        "words": [
            "funny", "laugh", "joke", "ridiculous", "absurd", "ironic",
            "silly", "haha", "lol", "weird",
            "mazaak", "hansi", "hasna", "ajeeb si baat",
            "मज़ाक", "मजाक", "हँसी", "हँसना", "हा हा", "हास्य",
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
            "शांति", "सुकून", "खामोशी", "विचार",
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


CASUAL_SIGNALS = [
    "joking", "kidding", "just joking", "just kidding",
    "mazaak", "mazak", "मज़ाक", "मजाक",
    "what's up", "whats up", "just asking", "aise hi", "aise he",
    "timepass", "time pass", "bas aise hi",
    "how are you", "kaise ho", "kya haal", "kya chal raha",
]


def _classify_question_type(question: str, concepts: list, depth_score: float,
                              language: str = "english", intent: str = "explore",
                              philosophers: list = None) -> str:
    # Normalize em-dash/en-dash to spaces so "this—so" splits into ["this", "so"]
    q_normalized = question.replace('—', ' ').replace('–', ' ')
    lower = q_normalized.split()
    lower_str = question.lower()
    word_count = len(lower)
    lower_set = {w.lower().strip('?!.,;:।') for w in lower}

    personal_en = {"i", "my", "me", "i'm", "i've", "myself"}
    personal_hi = {"main", "mera", "meri", "mujhe", "mai", "apna", "apne", "apni"}
    personal_hi_deva = {"मेरा", "मेरी", "मुझे", "मैं", "मेने", "मैंने", "अपना", "अपने", "अपनी", "हमारा", "हमारी", "हूँ", "हूं"}
    has_personal = bool(
        (lower_set & personal_en)
        or (lower_set & personal_hi)
        or any(w in question for w in personal_hi_deva)
    )

    # Conversational / casual detection — before emotional to avoid misclassification
    has_casual = any(s in lower_str for s in CASUAL_SIGNALS)
    if has_casual and word_count <= 12:
        # Only classify as conversational if not emotional
        emotional_check = [
            "feel", "feeling", "hurt", "pain", "empty", "lost",
            "stuck", "anxious", "afraid", "scared", "lonely", "depressed",
            "dukhi", "akela", "udas", "pareshan", "दुखी", "अकेला",
        ]
        if not any(e in lower_str for e in emotional_check):
            return "conversational"

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
        "bored", "unmotivated", "numb", "disconnected", "meaningless", "upset",
        "nobody cares", "no one cares", "nothing matters", "doesn't matter",
        "matlab nahi", "matlab hi nahi", "koi matlab nahi",
        "pareshan", "dukhi", "akela", "udas", "thak", "haara", "gussa",
        "kya karu", "samajh nahi",
        "kasht", "kashtdayak", "kastdayak", "peeda", "pida",
        "कष्ट", "कष्टदायक", "कस्टदायक", "पीड़ा",
        "depressed", "depression", "emotionally",
        "emotional support", "need help", "need support",
        "डिप्रेशन", "डिप्रेस", "भावनात्मक", "सहारा",
        "madad chahiye", "मदद चाहिए",
        # Hindi Devanagari emotional signals
        "दुखी", "अकेला", "उदास", "थक", "हारा",
        "परेशान", "तकलीफ़", "मुश्किल",
        "डर", "चिंता", "गुस्सा", "नाराज़",
        "टूट", "बिछड़", "तड़प",
        # v3: Guilt / self-blame / negativity signals
        "बुरा इंसान", "गलत काम", "बुरा", "गलत",
        "क्या करू", "क्या करूँ",
        "नेगटिव", "नकारात्मक",
        # Hinglish despair / futility signals
        "bekaar", "bekar", "sab bekaar", "kya fayda",
        "kuch nahi hoga", "nahi kar pa", "nahi ho pa",
        "बेकार", "सब बेकार",
        # v4.4: Negated peace / post-victory emptiness
        "sukoon nahi", "chain nahi", "kuch choot gaya",
        "सुकून नहीं", "चैन नहीं", "कुछ छूट गया",
        "peace remains elusive", "something left behind",
    ]

    has_emotional = any(w in lower_str for w in high_signal_emotional)

    # AI-directed questions ("do you feel", "aapko feel hota hai") are philosophical,
    # not emotional — the user is exploring AI consciousness, not expressing distress
    ai_directed_en = {"you", "your", "you're", "yourself"}
    ai_directed_hi = {"aapko", "tumko", "tumhe", "aap", "tum", "tumhare", "aapke"}
    ai_directed_deva = {"आपको", "तुमको", "तुम्हे", "तुम्हारे", "आपके"}
    is_ai_directed = bool(
        (lower_set & ai_directed_en)
        or (lower_set & ai_directed_hi)
        or any(w in question for w in ai_directed_deva)
    )
    ai_nature_words = ["feel", "feeling", "conscious", "alive", "experience",
                       "feel hota", "mehsoos", "mehsus", "anubhav",
                       "महसूस", "अनुभव", "फील"]
    is_ai_nature_question = is_ai_directed and any(w in lower_str for w in ai_nature_words)

    if has_personal and ("should" in lower or "karu" in lower_str or "karna" in lower_str
                         or "करू" in question or "करूँ" in question):
        if not is_ai_nature_question:
            return "emotional"
    # Impersonal questions with emotional words = philosophical inquiry, not distress
    if has_emotional and not has_personal:
        intellectual_patterns = [
            r'\bwhy\s+(does|do|did)\b',
            r'\b(can|do|does|could|would|should)\b.*\b(feel|feeling|feelings)\b',
        ]
        if any(re.search(p, lower_str) for p in intellectual_patterns):
            pass  # skip emotional — it's intellectual inquiry
        else:
            return "emotional"
    elif has_emotional:
        # AI-nature questions override emotional classification
        if is_ai_nature_question:
            pass  # philosophical inquiry about AI consciousness
        else:
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
        "about this", "about it", "about that",
        "in this area", "in this regard", "regarding this",
        "on this topic", "on this", "explain this",
        "explain something", "tell me more", "more about",
        "elaborate on", "go deeper", "in this context",
        "this further", "this better", "improvements",
        "kya karu", "ab kya", "phir kya", "to kya",
        "kya matlab", "iska matlab", "uska matlab", "aur batao",
        "iske bare", "iske baare", "is baare",
        # Devanagari follow-ups
        "और ये", "और यह", "फिर क्या", "तो क्या", "अब क्या",
        "कौन तय", "कोण तय", "और बताओ", "क्या मतलब", "इसका मतलब",
        "इसके बारे", "इस बारे", "और बताये",
        # v3: Conversational continuations
        "not letting", "isn't letting", "won't let",
        "move forward", "move on",
    ]
    # Context-reference words — strong follow-up signal when no concepts found
    context_ref_words = {"this", "it", "that", "these", "those"}
    context_ref_hinglish = {"ye", "yeh", "isko", "isme", "ispe", "ispr", "iska"}
    lower_clean = {w.lower().strip('?!.,;:।') for w in question.split()}
    has_context_ref = bool(lower_clean & context_ref_words) or bool(lower_clean & context_ref_hinglish)

    # Acknowledgment patterns — user affirming/closing, not asking
    acknowledgment_words = {"okay", "ok", "alright", "thik", "theek", "accha", "haan", "chalo"}
    is_acknowledgment = bool(lower_clean & acknowledgment_words) or "ठीक" in question

    # Intent already detected as a real question type — don't override to follow_up
    # But only when concepts exist; no-concept + challenge intent = likely conversational
    has_real_intent = intent in ("define", "compare", "challenge") and bool(concepts)

    if not concepts and not has_real_intent:
        if word_count <= 10 and any(p in lower_str for p in follow_up_patterns):
            return "follow_up"
        if word_count <= 5 and is_greeting:
            return "follow_up"
        if word_count <= 10 and is_acknowledgment:
            return "follow_up"
        if word_count <= 18 and has_context_ref:
            return "follow_up"
        # Daily-life Hinglish questions → factual, not follow_up
        daily_life_hinglish = ["khana", "khaya", "khaye", "piya", "soya",
                               "aaj", "kal", "parso", "abhi"]
        if any(d in lower_str for d in daily_life_hinglish):
            return "factual"
        if word_count <= 7:
            if has_hinglish_question:
                pass  # Don't default to follow_up — it's a real question
            elif word_count <= 4:
                return "follow_up"

    # Short conversational follow-ups — even if concepts exist
    # (e.g. "Me ready hun parntu ye mujhe aage nhi..." — has courage but is follow_up)
    if concepts and not has_real_intent and word_count <= 12 and not has_hinglish_question:
        if is_acknowledgment:
            return "follow_up"
        if has_context_ref and len(concepts) <= 1:
            return "follow_up"

    # Longer Hinglish with personal + action words → emotional/mixed
    hinglish_action = ["kya krna chahiye", "kya karu", "karna chahiye",
                       "krna chahiye", "kya kare", "kaise kare"]
    if not concepts and has_personal and any(a in lower_str for a in hinglish_action):
        return "emotional"

    # Hindi emotional support requests (मदद चाहिए, सहारा, भावनात्मक)
    hindi_emotional_signals = [
        "मदद चाहिए", "सहारा", "भावनात्मक", "डिप्रेशन", "डिप्रेस",
        "madad", "sahara", "emotional support", "emotionally",
    ]
    if has_personal and any(s in lower_str or s in question for s in hindi_emotional_signals):
        return "emotional"

    if not concepts and philosophers:
        return "philosophical"

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
        # Hindi/Devanagari questions — check for meta/system questions first
        has_devanagari = any('\u0900' <= c <= '\u097F' for c in question)
        if has_devanagari:
            meta_signals = [
                "जानकारी", "साझा", "डेटा", "प्राइवेसी", "सुरक्षा",
                "information", "data", "privacy", "expose", "share",
                "उपयोगकर्ता", "user", "users",
            ]
            if any(s in lower_str or s in question for s in meta_signals):
                return "factual"
            # Personal daily-life questions — not philosophical
            daily_life_signals = [
                "खाना", "खाया", "खाये", "पिया", "सोया", "उठा",
                "पहना", "गया", "आया", "किया", "देखा",
                "आज", "कल", "परसों", "अभी",
                "khaya", "khana", "piya", "soya",
            ]
            if any(s in lower_str or s in question for s in daily_life_signals):
                return "factual"
            return "philosophical"
        # Hinglish with common conversational words → mixed, not factual
        hinglish_conv = ["toh", "kare", "kaise", "batao", "bataye",
                         "samjh", "tarah", "tarike", "sudhar", "rasta",
                         "hota", "sakta", "chahiye", "jaye", "kiye"]
        if any(w in lower_str for w in hinglish_conv):
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


def _detect_emotional_intensity(question: str, question_type: str, intent: str = "explore") -> str:
    is_emotional_type = question_type in ("emotional", "mixed") or intent == "challenge"
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
        return "high" if is_emotional_type else "medium"
    medium_signals = [
        "struggling", "suffering", "can't stop", "don't know what to do",
        "feel trapped", "feel stuck", "wasting my life", "wasting time",
        "lost everything", "falling apart", "hate my",
        "depressed", "anxious", "panic", "overwhelmed",
        "scared of", "afraid of", "terrified",
        "nobody understands", "feel alone", "feel empty",
        "failed", "keep failing", "always fail",
        # v4: Self-criticism medium signals
        "upset with myself", "upset with me", "feel bad about myself",
        "disappointed in myself", "frustrated with myself", "angry at myself",
        "blame myself", "my fault", "let myself down",
        "pareshan", "bahut dukhi", "samajh nahi aa raha",
        "kya karu", "kuch samajh nahi", "bahut darr",
        # v3: "bahut" intensity boosters
        "bahut akela", "bahut thak", "bahut pareshan",
        "bahut dard", "bahut darr", "bahut udas",
        "kaafi akela", "ekdum akela", "bilkul akela",
        # v3: Guilt / self-blame / negativity medium signals
        "what should i do", "what do i do",
        "bad person", "wrong things", "done wrong",
        "negative mindset", "negative thinking", "preventing me",
        "बुरा इंसान", "गलत काम",
        "क्या करू", "क्या करूँ",
        "नकारात्मक", "नेगटिव",
        "आगे नहीं", "aage nahi", "aage nhi",
        # v4.4: Post-victory emptiness / negated peace signals
        "sukoon nahi", "sukun nahi", "chain nahi",
        "peace remains elusive", "something left behind",
        "even after victory", "jeet ke baad bhi",
        "kuch choot gaya", "kuch chhoot gaya",
        "सुकून नहीं", "चैन नहीं", "कुछ छूट गया",
        "जीत के बाद भी",
        # Challenge / critique frustration signals
        "no depth", "no substance", "no meaning",
        "shallow", "superficial", "generic", "repetitive",
        "not good enough", "lacks depth", "don't find",
        "doesn't make sense", "doesn't help", "not helpful",
        "disappointed", "expected more", "expected better",
        "गहराई नहीं", "नहीं लगता", "नहीं दिखता", "नहीं मिलता",
        "कोई गहराई नहीं", "बेकार जवाब",
    ]
    if any(s in lower for s in medium_signals):
        return "medium" if is_emotional_type else "low"
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
    """v3: Detect Navarasa flavor. Returns (rasa, intensity, target)."""
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
        elif question_type == "conversational":
            best_rasa = "hasya"
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


CONTEXT_SENSITIVE_WORDS = {
    "confused": r"(?:you(?:'re|r| are| seem| look| sound| get(?:ting)?))\s+(?:\w+\s+)*confused",
    "confusion": r"(?:you(?:'re|r| are| seem| look| sound))\s+(?:\w+\s+)*confusion|(?:getting|causing)\s+confusion",
    "stuck": r"(?:you(?:'re|r| are| seem| look| sound| get(?:ting)?))\s+(?:\w+\s+)*stuck",
    "lost": r"(?:you(?:'re|r| are| seem| look| sound| get(?:ting)?))\s+(?:\w+\s+)*lost",
}


def analyze_concepts(question: str, language: str = "english", translated: str = "") -> ConceptAnalysis:
    """v3: Full analysis with Navarasa detection."""
    analysis = ConceptAnalysis(language=language)

    texts = [question.lower()]
    if translated and translated != question:
        texts.append(translated.lower())
    search_text = " ".join(texts)

    # Strip English idioms that cause false positives
    idiom_strip = [
        "mind you", "bear in mind", "never mind", "don't mind",
        "do you mind", "make up your mind", "change your mind",
    ]
    clean_search = search_text
    for idiom in idiom_strip:
        clean_search = clean_search.replace(idiom, "")

    found_concepts = set()
    for keyword, concept in CONCEPT_MAP.items():
        if _match_keyword_in_text(keyword, clean_search):
            if keyword in CONTEXT_SENSITIVE_WORDS:
                if re.search(CONTEXT_SENSITIVE_WORDS[keyword], clean_search, re.IGNORECASE):
                    continue
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
        question, analysis.concepts, analysis.depth_score, language, analysis.intent,
        analysis.philosophers
    )
    analysis.emotional_intensity = _detect_emotional_intensity(
        question, analysis.question_type, analysis.intent
    )
    # v3: Navarasa
    analysis.detected_rasa, analysis.rasa_intensity, analysis.rasa_target = _detect_rasa(
        question, translated, analysis.question_type, analysis.emotional_intensity
    )

    return analysis