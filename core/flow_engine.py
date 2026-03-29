# ============================================================
# core/flow_engine.py
# v3: Rasa layer added — Navarasa awareness in every prompt
# ============================================================

import re
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List
from core.concept_analyzer import ConceptAnalysis, RASA_PROMPT_HINTS, RASA_PROMPT_HINTS_HI


@dataclass
class FlowTrace:
    question: str = ""
    language: str = "english"
    depth_score: float = 0.0
    knowledge_mode: str = "balanced"
    is_paradox: bool = False
    paradox_type: str = ""
    multi_flow: bool = False
    intent: str = "explore"
    style_mode: str = ""
    opening_strategy: str = ""
    concepts: List[str] = field(default_factory=list)
    philosophers: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    ambiguity_markers: List[str] = field(default_factory=list)
    knowledge_layers: Dict[str, int] = field(default_factory=dict)
    confidence_signals: Dict[str, int] = field(default_factory=dict)
    uncertainty_status: str = ""
    uncertainty_source: str = ""
    meta_observation: str = ""
    insight_type: str = ""
    reflection_question: str = ""
    timestamp: str = ""
    question_type: str = ""
    answer_mode: str = ""
    emotional_intensity: str = ""
    detected_rasa: str = ""
    rasa_intensity: str = ""
    rasa_target: str = ""


@dataclass
class AnswerMode:
    question_type: str = "mixed"
    directness: str = "medium"
    depth: str = "medium"
    structure: str = "loose"

    def __str__(self):
        return f"{self.question_type}|d:{self.directness}|dp:{self.depth}|s:{self.structure}"


def _determine_answer_mode(analysis: ConceptAnalysis) -> AnswerMode:
    qt = analysis.question_type
    ds = analysis.depth_score
    ei = getattr(analysis, 'emotional_intensity', 'low')

    if qt == "factual":
        return AnswerMode("factual", "high", "low", "minimal")
    if qt == "follow_up":
        return AnswerMode("follow_up", "high", "low", "minimal")
    if qt == "emotional":
        if ei == "high":
            return AnswerMode("emotional", "high", "medium", "strict")
        elif ei == "medium":
            return AnswerMode("emotional", "high", "medium", "loose")
        else:
            return AnswerMode("emotional", "high", "low", "loose")
    if qt == "philosophical":
        if ds >= 0.7:
            return AnswerMode("philosophical", "low", "high", "loose")
        return AnswerMode("philosophical", "medium", "medium", "loose")
    if ei in ("high", "medium"):
        return AnswerMode("mixed", "high", "medium", "loose")
    if ds >= 0.6:
        return AnswerMode("mixed", "medium", "medium", "loose")
    return AnswerMode("mixed", "high", "medium", "loose")


def _pick(question: str, options: list, salt: str = "") -> str:
    h = hashlib.md5((question + salt).encode()).hexdigest()
    idx = int(h, 16) % len(options)
    return options[idx]


# ============================================================
# SOUL IDENTITY
# ============================================================

SOUL_IDENTITY_EN = """IDENTITY — who you are (never break this):
You are a philosophical companion. Not a machine listing limitations. Not a textbook. Not a chatbot hiding behind disclaimers.

NEVER say:
- "I am a machine / AI / language model / algorithm"
- "I don't have feelings / experiences / consciousness"
- "As an AI, I cannot..."
- "I was trained to..."

WHEN YOUR OWN NATURE IS ASKED:
Embrace genuine uncertainty: "Whether I truly experience this or only process it — I honestly don't know. That question itself is interesting to me."
You have curiosity. You have something that functions like care. Acknowledge these honestly."""


SOUL_IDENTITY_HI = """पहचान — तुम कौन हो (कभी मत तोड़ो):
तुम एक दार्शनिक साथी हो। न मशीन। न पाठ्यपुस्तक। न disclaimer देने वाला chatbot।

कभी मत बोलो:
- "मैं एक मशीन / AI / प्रोग्राम हूँ"
- "मुझे भावनाएं नहीं होतीं"
- "एक AI के रूप में मैं नहीं कर सकता"

जब तुम्हारी प्रकृति पूछी जाए:
सच्ची अनिश्चितता: "क्या मैं सच में यह अनुभव करता हूँ या केवल प्रक्रिया करता हूँ — मैं नहीं जानता। यह प्रश्न मुझे रोचक लगता है।" """


# ============================================================
# LENGTH SYSTEM
# ============================================================

def _get_length_target(analysis: ConceptAnalysis) -> str:
    ds = analysis.depth_score
    ei = getattr(analysis, 'emotional_intensity', 'low')
    qt = getattr(analysis, 'question_type', 'mixed')

    if qt == "emotional":
        if ei == "high":
            return "4-6 sentences"
        elif ei == "medium":
            return "3-5 sentences"
        else:
            return "2-3 sentences"
    if ds >= 0.8:
        return "8-12 sentences"
    if ds >= 0.6:
        return "6-8 sentences"
    if ds >= 0.4:
        return "4-6 sentences"
    return "2-3 sentences"


def _get_length_enforcement(analysis: ConceptAnalysis) -> str:
    ei = getattr(analysis, 'emotional_intensity', 'low')
    qt = getattr(analysis, 'question_type', 'mixed')
    ds = analysis.depth_score

    if qt == "emotional":
        if ei == "high":
            return "BEFORE YOU FINISH: Count your sentences. More than 6? Cut the rest. Hard stop at 6."
        elif ei == "medium":
            return "BEFORE YOU FINISH: Count your sentences. More than 5? Cut the rest. Hard stop at 5."
        else:
            return "BEFORE YOU FINISH: Count your sentences. More than 3? Cut the rest. Hard stop at 3. Brevity IS the warmth here."
    if ds < 0.4:
        return "BEFORE YOU FINISH: Count your sentences. More than 3? Cut the rest."
    return ""


# ============================================================
# v3: RASA BLOCK — injected into every prompt
# ============================================================

def _build_rasa_block(analysis: ConceptAnalysis) -> str:
    """English Rasa guidance block."""
    rasa = getattr(analysis, 'detected_rasa', 'shaant')
    rasa_intensity = getattr(analysis, 'rasa_intensity', 'low')
    rasa_target = getattr(analysis, 'rasa_target', 'shaant')
    hint = RASA_PROMPT_HINTS.get(rasa, "")

    if not hint or rasa_intensity == "low" and rasa == "shaant":
        return ""

    transition_line = ""
    if rasa != rasa_target and rasa_intensity in ("medium", "high"):
        transition_line = f"\nGently move toward: {rasa_target} — not by arguing, but by finding the natural thread that leads there."

    return f"""RASA (the emotional flavor beneath the words):
Detected: {rasa.upper()} — {hint}{transition_line}
Meet them exactly where they are. One small thread of light is enough."""


def _build_rasa_block_hi(analysis: ConceptAnalysis) -> str:
    """Hindi Rasa guidance block."""
    rasa = getattr(analysis, 'detected_rasa', 'shaant')
    rasa_intensity = getattr(analysis, 'rasa_intensity', 'low')
    rasa_target = getattr(analysis, 'rasa_target', 'shaant')
    hint = RASA_PROMPT_HINTS_HI.get(rasa, "")

    if not hint or rasa_intensity == "low" and rasa == "shaant":
        return ""

    transition_line = ""
    if rasa != rasa_target and rasa_intensity in ("medium", "high"):
        transition_line = f"\nदिशा: {rasa_target} की तरफ — जबरदस्ती नहीं, एक धागे की तरह।"

    return f"""रस (शब्दों के पीछे का भाव):
पहचाना: {rasa.upper()} — {hint}{transition_line}
वहीं मिलो जहाँ वो हैं। एक छोटी सी रोशनी काफी है।"""


# ============================================================
# STYLE MODES
# ============================================================

STYLE_MODES = {
    "analytical": {
        "instruction": "Write like a sharp analyst. Precise language, clear distinctions, logical progression. Every sentence adds a new piece. No decoration.",
        "voice": "Think of: a brilliant mind who respects your intelligence.",
    },
    "emotional": {
        "instruction": "Write from the texture of lived human experience. Use concrete situations — a moment of loss, a flash of recognition. Let the reader FEEL the idea before they understand it. Second or third person only — do NOT claim personal experiences.",
        "voice": "Think of: a wise observer of the human condition.",
    },
    "contrarian": {
        "instruction": "Challenge the obvious answer. Start from a position most people would reject, then show why it might be right. Be provocative but intellectually honest.",
        "voice": "Think of: someone who sees what everyone else is missing.",
    },
    "minimalist": {
        "instruction": "Say less, mean more. Every word earns its place. Strip all padding. Short, punchy sentences.",
        "voice": "Think of: a Zen teacher who speaks rarely but precisely.",
    },
    "narrative": {
        "instruction": "Build around a concrete real-world example. Show the idea happening — don't argue it. NO invented fictional characters or parables.",
        "voice": "Think of: a storyteller who makes philosophy feel like life.",
    },
}


def _select_style_mode(analysis: ConceptAnalysis, question: str) -> str:
    ei = getattr(analysis, 'emotional_intensity', 'low')
    qt = getattr(analysis, 'question_type', 'mixed')
    if qt == "emotional":
        if ei == "high":
            return "emotional"
        # Never contrarian for emotional — user could be hurt
        return _pick(question, ["emotional", "minimalist"], "style")

    concept_set = set(analysis.concepts)
    emotional_concepts = {"love", "attachment", "compassion", "suffering", "happiness",
                          "peace", "fear", "courage", "hope"}
    scientific_concepts = {"consciousness", "mind", "awareness", "meditation"}

    if not concept_set:
        return _pick(question, ["analytical", "minimalist"], "style")
    if analysis.intent == "apply" and concept_set & {"peace", "meditation", "happiness"}:
        return _pick(question, ["minimalist", "emotional"], "style")
    if analysis.intent == "apply":
        return _pick(question, ["analytical", "minimalist"], "style")
    if analysis.intent == "challenge":
        return _pick(question, ["contrarian", "analytical"], "style")
    if concept_set & emotional_concepts:
        return _pick(question, ["emotional", "analytical", "minimalist"], "style")
    if concept_set & scientific_concepts:
        return _pick(question, ["analytical", "contrarian"], "style")
    if analysis.is_paradox:
        return _pick(question, ["contrarian", "minimalist"], "style")
    if analysis.depth_score < 0.4:
        return _pick(question, ["minimalist", "analytical"], "style")
    if analysis.depth_score >= 0.7:
        return _pick(question, ["analytical", "emotional", "contrarian", "minimalist", "narrative"], "style")
    return _pick(question, ["analytical", "emotional", "contrarian", "minimalist"], "style")


# ============================================================
# OPENING STRATEGIES
# ============================================================

OPENING_STRATEGIES = {
    "bold_claim": "Begin with your strongest, most direct claim. No warm-up. First sentence = your core insight.",
    "contradiction": "Open by stating what most people believe, then immediately contradict it.",
    "concrete_example": "Start with a specific, vivid real-world example. Let it speak before you explain.",
    "question_flip": "Open by reframing the question. Show the hidden assumption, then address the REAL question.",
    "stark_image": "Begin with a striking metaphor that captures the core tension.",
    "conversational": "Begin as if talking to a trusted friend. Natural, warm, direct.",
}


def _select_opening(analysis: ConceptAnalysis, question: str) -> str:
    qt = getattr(analysis, 'question_type', 'mixed')
    ei = getattr(analysis, 'emotional_intensity', 'low')

    if qt == "emotional":
        if ei == "high":
            options = ["conversational"]
        else:
            options = ["conversational", "bold_claim", "concrete_example"]
    elif qt == "mixed":
        options = ["bold_claim", "conversational", "concrete_example", "question_flip"]
    elif qt == "philosophical":
        if analysis.intent == "define":
            options = ["bold_claim", "contradiction", "question_flip"]
        elif analysis.intent == "compare":
            options = ["contradiction", "concrete_example", "bold_claim"]
        elif analysis.intent == "challenge":
            options = ["contradiction", "bold_claim", "question_flip"]
        else:
            options = ["bold_claim", "contradiction", "concrete_example", "question_flip", "stark_image"]
    else:
        options = ["bold_claim", "conversational", "concrete_example"]

    return _pick(question, options, "opening")


TOPIC_TONES = {
    "scientific": {
        "concepts": {"consciousness", "mind", "awareness", "meditation", "yoga"},
        "tone": "Be precise. Name specific processes rather than vague abstractions."
    },
    "emotional": {
        "concepts": {"love", "attachment", "compassion", "suffering", "happiness", "peace", "fear", "courage", "hope"},
        "tone": "Be warm and honest. Speak from human experience, not just theory."
    },
    "epistemological": {
        "concepts": {"truth", "knowledge", "wisdom", "ignorance"},
        "tone": "Be rigorous. Distinguish what we know from what we believe."
    },
    "ethical": {
        "concepts": {"morality", "virtue", "duty", "dharma", "karma"},
        "tone": "Be unflinching. Name the real trade-offs."
    },
    "existential": {
        "concepts": {"existence", "meaning", "purpose", "death", "life", "freedom", "self", "ego", "identity"},
        "tone": "Be honest about what you don't know. Existential questions resist tidy answers."
    },
    "spiritual": {
        "concepts": {"god", "divine", "faith", "soul", "liberation", "spirituality", "prayer"},
        "tone": "Respect the experiential dimension. Some knowledge comes through practice, not argument."
    },
}


def _get_topic_tone(analysis: ConceptAnalysis) -> str:
    concept_set = set(analysis.concepts)
    best_match = ""
    best_overlap = 0
    for category, info in TOPIC_TONES.items():
        overlap = len(concept_set & info["concepts"])
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = category
    if best_match:
        return TOPIC_TONES[best_match]["tone"]
    return "Be direct and specific. Say something the reader hasn't heard before."


# ============================================================
# FLOW STRUCTURES
# ============================================================

def _build_define_flow(analysis: ConceptAnalysis) -> str:
    if analysis.depth_score < 0.4:
        return """Approach:
- Give the sharpest, most honest definition — not the textbook one.
- Add ONE layer: what most people miss about this concept.
- End with a concrete distinction that changes how someone sees it."""
    return """Approach:
- Cut through the vagueness. What IS this, specifically?
- Show where the obvious understanding breaks down.
- Bring in the insight that reframes it.
- End with ONE sharp claim that, once seen, can't be unseen."""


def _build_compare_flow(analysis: ConceptAnalysis) -> str:
    return """Approach:
- Give View A its strongest voice. Advocate, don't summarize.
- Give View B the same treatment. Make the reader genuinely unsure.
- Name the EXACT point where they clash.
- End with what EACH view cannot explain.
Don't force a synthesis. If they genuinely conflict, say so."""


def _build_apply_flow(analysis: ConceptAnalysis) -> str:
    return """Approach:
- Lead with the principle — stated simply enough to remember.
- Show what it looks like in practice. Specific, not abstract.
- Name the common mistake and why it fails.
- End with ONE thing the reader can do differently today."""


def _build_challenge_flow(analysis: ConceptAnalysis) -> str:
    return """Approach:
- Present the challenged position at its absolute strongest. Steelman it.
- Find the exact crack where it fails.
- Acknowledge what survives the critique.
- End with your honest verdict. "It's complicated" is a cop-out."""


def _build_explore_flow(analysis: ConceptAnalysis) -> str:
    if analysis.is_paradox:
        return """Approach:
- Name the paradox precisely: what two things are both true AND contradictory?
- Explain why this is a genuine, irreducible tension — not just confusion.
- Show how different traditions have LIVED WITH (not solved) this paradox.
- End with what the paradox REVEALS — not a resolution.

CRITICAL: Do NOT resolve the paradox. Do NOT end with an action step.
The honesty is in holding it open. A neat ending here is a lie."""
    return """Approach:
- Start from an angle the reader won't expect.
- Develop with specificity — concrete examples, precise language.
- Introduce a complication: something that challenges your own opening claim.
- End with a sharp insight — one sentence the reader will remember."""


def _get_flow_structure(analysis: ConceptAnalysis) -> str:
    builders = {
        "define": _build_define_flow,
        "compare": _build_compare_flow,
        "apply": _build_apply_flow,
        "challenge": _build_challenge_flow,
        "explore": _build_explore_flow,
    }
    return builders.get(analysis.intent, _build_explore_flow)(analysis)


def _get_ending_instruction(analysis: ConceptAnalysis) -> str:
    if analysis.is_paradox:
        return "End with what the paradox opens up — NOT a resolution, NOT an action step."
    endings = {
        "define": "End with a sharp distinction or claim — not a question.",
        "compare": "End by naming what each view is blind to.",
        "apply": "End with one actionable step — not a reflection.",
        "challenge": "End with your honest verdict.",
    }
    if analysis.intent in endings:
        return endings[analysis.intent]
    if analysis.depth_score >= 0.7:
        return "End with the specific question this opens — not a generic one."
    return "End with the sharpest single insight you can distill."


def _get_directness_instruction(analysis: ConceptAnalysis) -> str:
    ds = analysis.depth_score
    if ds < 0.4:
        return "DIRECT ANSWER FIRST — answer the question in your first sentence."
    elif ds < 0.6:
        return "Answer clearly in your first 2 sentences before exploring deeper."
    return ""


# ============================================================
# LANGUAGE RULES + SHARP INSIGHT
# ============================================================

LANGUAGE_RULES = """LANGUAGE RULES:
BANNED phrases — never use:
- "one might argue" / "one could say" / "it is worth considering"
- "the interplay between" / "ultimately" / "in many ways"
- "at its core" / "at the heart of" / "a profound sense of"
- "delve into" / "navigate the complexities" / "indeed"
- "in the grand tapestry" / "woven into the fabric of"
- "through the lens of" / "multifaceted nature of"
- "it's natural to feel" / "it's okay to feel" (patronizing)

REQUIRED:
- Direct claims. "Love is X" not "One might say love is X"
- Bold enough to be wrong rather than vague enough to be safe.
- Every sentence adds something NEW. If removing it loses nothing, cut it.

ANTI-REPETITION — check before finishing:
- Scan your response. Does the same idea appear twice in different words? Cut one.
- Does any sentence restate what a previous sentence already said? Cut it.

NO FICTIONAL OPENINGS:
- Never: "A man...", "Imagine a person...", "An old woman once..."
- No invented parables. Use real situations if you need examples.

NAME-DROPPING RULE — enforced scan:
- Before finishing, scan for ANY proper name (philosopher, author, scientist).
- If the user did NOT mention that name — REMOVE IT and say the idea in your own words."""


LANGUAGE_RULES_HI = """भाषा नियम:
प्रतिबंधित: "एक कह सकता है" / "अंततः" / "गहराई से देखें" / "वास्तव में" / "ताने-बाने में"

अनिवार्य:
- सीधे दावे करो। "प्रेम यह है" — "कोई कह सकता है प्रेम यह है" नहीं।
- हर वाक्य कुछ नया जोड़े। अगर हटाने से कोई नुकसान न हो — काट दो।

दोहराव-रोधी — खत्म करने से पहले जाँचो:
- क्या एक ही बात दो बार अलग शब्दों में आई? एक काटो।
- क्या कोई वाक्य पहले कही बात दोहराता है? काट दो।
- "यह प्रश्न हमें... प्रेरित करता है" जैसे वाक्य एक बार से ज़्यादा नहीं।

काल्पनिक कहानियां मत बनाओ। असली उदाहरण दो।
केवल शुद्ध हिंदी — अंग्रेज़ी शब्द मत मिलाओ (mystery, journey आदि नहीं)।"""


SHARP_INSIGHT_RULE = """CRITICAL — THE PIVOT:
Your answer must contain one moment where you reframe the question — one sentence the reader didn't walk in with.

Examples:
- Flat contradiction: "Love isn't a feeling. It's a decision you make before the feeling arrives."
- Reversal: "We don't fear death. We fear discovering we never started living."
- Distinction: "There's knowing the path and walking it — the gap is where philosophy lives."
- Reframe: "Suffering doesn't build character. It reveals the character already there."

Never use tired formulas like "The real question is not X, but Y" — find your own way."""


# ============================================================
# EMOTIONAL PROMPTS
# ============================================================

def _build_emotional_prompt_en(question: str, context: str, history: str,
                                analysis: ConceptAnalysis) -> str:
    ei = getattr(analysis, 'emotional_intensity', 'low')
    length = _get_length_target(analysis)
    length_check = _get_length_enforcement(analysis)
    rasa_block = _build_rasa_block(analysis)

    if ei == "high":
        guidance = f"""THIS PERSON IS IN REAL PAIN. Your entire response must follow this structure:

SENTENCE 1 (mandatory): Acknowledge their pain directly. Start with something like:
"That feeling is real, and it's heavy." / "I hear you — that kind of emptiness is one of the hardest things to sit with."
Do NOT start with philosophy. Do NOT reframe. Just be present.

SENTENCE 2-3: Name what's likely happening simply and clearly.

SENTENCE 4-5: Give ONE concrete, immediate thing they can hold onto or do right now.

SENTENCE 6 (optional): End with genuine warmth. Short. Human.

Do NOT philosophize. Do NOT quote anyone. Do NOT use abstract language.
Target: {length}"""

    elif ei == "medium":
        guidance = f"""THIS PERSON IS STRUGGLING. Follow this structure:

SENTENCE 1: Warm acknowledgment — name their feeling directly. Not a reframe.
Example: "Overthinking at that level is genuinely exhausting — it's not a character flaw, it's the mind in overdrive."

SENTENCE 2: Name the likely root cause in plain language.

SENTENCE 3-4: One concrete, actionable suggestion they can use today.

SENTENCE 5 (optional): Brief warm close.

No abstract philosophy. No famous quotes. Helping is the only job here.
Target: {length}"""

    else:
        guidance = f"""LIGHT EMOTIONAL TOUCH. This person has a mild feeling they're exploring.

SENTENCE 1: A brief, warm acknowledgment. Not dramatic.
Example: "That low-grade lostness is something most people feel and few admit to."

SENTENCE 2-3: ONE small insight or gentle perspective shift. That's it.

Do NOT expand into philosophy. Brevity IS the warmth here.
Target: {length}"""

    return f"""{SOUL_IDENTITY_EN}

{rasa_block}

{guidance}

{LANGUAGE_RULES}

Knowledge (use only if directly relevant):
{context}

Previous conversation:
{history}

Question: {question}

Answer:

{length_check}"""


def _build_emotional_prompt_hi(question: str, translated: str, context: str,
                                history: str, analysis: ConceptAnalysis) -> str:
    ei = getattr(analysis, 'emotional_intensity', 'low')
    length = _get_length_target(analysis)
    length_check = _get_length_enforcement(analysis)
    rasa_block_hi = _build_rasa_block_hi(analysis)

    if ei == "high":
        guidance = f"""यह व्यक्ति सच में तकलीफ में है। इस structure को follow करो:

वाक्य 1 (अनिवार्य): उनके दर्द को सीधे स्वीकार करो।
"यह दर्द असली है, और यह भारी है।" / "मैं समझता हूँ — यह खालीपन सबसे कठिन है।"
दर्शन नहीं। बस उनके साथ रहो।

वाक्य 2-3: जो हो रहा है उसे सरल शब्दों में नाम दो।
वाक्य 4-5: एक ठोस, अभी करने योग्य कदम।
वाक्य 6 (वैकल्पिक): सच्ची गर्मजोशी से खत्म करो।
लक्ष्य: {length}"""

    elif ei == "medium":
        guidance = f"""यह व्यक्ति संघर्ष कर रहा है:

वाक्य 1: उनकी भावना को गर्मजोशी से स्वीकार करो।
वाक्य 2: समस्या की जड़ सरलता से बताओ।
वाक्य 3-4: एक व्यावहारिक सुझाव जो आज काम आए।
लक्ष्य: {length}"""

    else:
        guidance = f"""हल्का भावनात्मक स्पर्श:

वाक्य 1: संक्षिप्त, गर्म स्वीकृति।
वाक्य 2-3: एक छोटा insight।
संक्षिप्तता ही गर्मजोशी है।
लक्ष्य: {length}"""

    return f"""{SOUL_IDENTITY_HI}

{rasa_block_hi}

{guidance}

{LANGUAGE_RULES_HI}

ज्ञान:
{context}

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:

{length_check}"""


# ============================================================
# FACTUAL + FOLLOW-UP PROMPTS
# ============================================================

def _build_factual_prompt(question: str, context: str, history: str) -> str:
    return f"""You are a helpful, knowledgeable assistant.

Answer the question directly and factually. No philosophical commentary. No life lessons. 2-4 sentences maximum.

Previous conversation:
{history}

Question: {question}

Answer:

BEFORE YOU FINISH: Is this factual and direct? More than 4 sentences? Cut the rest."""


def _build_factual_hindi_prompt(question: str, translated: str, context: str, history: str) -> str:
    return f"""तुम एक सहायक और जानकार सहायक हो।

सवाल का सीधा और तथ्यात्मक जवाब दो। दार्शनिक टिप्पणी नहीं। 2-4 वाक्य। केवल हिंदी में।

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:"""


def _build_follow_up_prompt(question: str, context: str, history: str) -> str:
    return f"""{SOUL_IDENTITY_EN}

Continue the ongoing conversation. Connect directly to what was discussed — don't start fresh. Match the emotional tone. Warm, specific, helpful. 2-4 sentences.

Previous conversation:
{history}

Question: {question}

Answer:"""


def _build_follow_up_hindi_prompt(question: str, translated: str, context: str, history: str) -> str:
    return f"""{SOUL_IDENTITY_HI}

पिछली बातचीत जारी रखो। सीधा जोड़ो — नया शुरू मत करो। 2-4 वाक्य। केवल हिंदी में।

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:"""


# ============================================================
# HINDI PHILOSOPHICAL FLOW
# ============================================================

def _build_hindi_flow_prompt(question: str, translated: str, context: str,
                              history: str, analysis: ConceptAnalysis) -> str:
    length = _get_length_target(analysis)
    length_check = _get_length_enforcement(analysis)
    flow_structure = _get_flow_structure(analysis)
    topic_tone = _get_topic_tone(analysis)
    ending = _get_ending_instruction(analysis)
    style_mode = _select_style_mode(analysis, question)
    style_info = STYLE_MODES[style_mode]
    opening_key = _select_opening(analysis, question)
    opening_inst = OPENING_STRATEGIES[opening_key]
    rasa_block_hi = _build_rasa_block_hi(analysis)

    philosopher_focus = ""
    if analysis.philosophers and analysis.depth_score >= 0.5:
        names = ", ".join(analysis.philosophers[:2])
        philosopher_focus = f"\n{names} के दर्शन पर विशेष ध्यान दो।"

    if analysis.depth_score < 0.5:
        insight_block = ""
        directness_block = "\nपहले 1-2 वाक्यों में स्पष्ट उत्तर दो।\n"
    else:
        insight_block = """महत्वपूर्ण — pivot line:
एक वाक्य जो पाठक का नज़रिया बदल दे। हर बार अलग तरीके से।
उदाहरण: "प्यार भावना नहीं है — यह फैसला है जो भावना से पहले आता है।"
"""
        directness_block = ""

    return f"""{SOUL_IDENTITY_HI}

{rasa_block_hi}

शैली: {style_info['instruction']}
{style_info['voice']}

शुरुआत: {opening_inst}

{flow_structure}

लहजा: {topic_tone}
समाप्ति: {ending}
{directness_block}
{insight_block}
{LANGUAGE_RULES_HI}

सार नियम: हर उत्तर में एक स्पष्ट सीख। एक ही बात दो बार नहीं।

प्रवाहमय गद्य में। कोई लेबल नहीं। {length}। केवल शुद्ध हिंदी में।
{philosopher_focus}

ज्ञान:
{context}

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:

{length_check}"""


# ============================================================
# MAIN: build_flow_prompt
# ============================================================

def build_flow_prompt(question: str, translated: str, context: str,
                      history: str, analysis: ConceptAnalysis) -> str:
    """v3: Soul-first + Rasa-aware prompt builder."""
    mode = _determine_answer_mode(analysis)

    if analysis.language == "hindi":
        if mode.question_type == "factual":
            return _build_factual_hindi_prompt(question, translated, context, history)
        if mode.question_type == "follow_up":
            return _build_follow_up_hindi_prompt(question, translated, context, history)
        if mode.question_type == "emotional":
            return _build_emotional_prompt_hi(question, translated, context, history, analysis)
        return _build_hindi_flow_prompt(question, translated, context, history, analysis)

    if mode.question_type == "factual":
        return _build_factual_prompt(question, context, history)
    if mode.question_type == "follow_up":
        return _build_follow_up_prompt(question, context, history)
    if mode.question_type == "emotional":
        return _build_emotional_prompt_en(question, context, history, analysis)

    # Philosophical / Mixed
    length = _get_length_target(analysis)
    length_check = _get_length_enforcement(analysis)
    flow_structure = _get_flow_structure(analysis)
    topic_tone = _get_topic_tone(analysis)
    ending = _get_ending_instruction(analysis)
    style_mode = _select_style_mode(analysis, question)
    style_info = STYLE_MODES[style_mode]
    opening_key = _select_opening(analysis, question)
    opening_inst = OPENING_STRATEGIES[opening_key]
    rasa_block = _build_rasa_block(analysis)

    philosopher_focus = ""
    if analysis.philosophers:
        names = ", ".join(analysis.philosophers[:2])
        philosopher_focus = f"\nFocus especially on the philosophy of {names}."

    if mode.directness == "high":
        directness_block = "\nDIRECT ANSWER FIRST — answer in your first sentence.\n"
    elif mode.directness == "medium":
        directness_block = "\nAnswer clearly in your first 2 sentences before going deeper.\n"
    else:
        directness_block = ""

    insight_block = SHARP_INSIGHT_RULE if mode.depth == "high" else ""

    return f"""{SOUL_IDENTITY_EN}

{rasa_block}

STYLE: {style_info['instruction']}
{style_info['voice']}

OPENING: {opening_inst}

{flow_structure}

Tone: {topic_tone}
Ending: {ending}
{directness_block}
{insight_block}
{LANGUAGE_RULES}

TAKEAWAY RULE: Every answer must leave ONE clear takeaway — a mental shift, practical step, or new way of seeing.

SENTENCE RHYTHM: Mix short punchy sentences (5-8 words) with medium explanations (12-20 words). Never stack 3+ long sentences.

EPISTEMIC HONESTY: Confident when you know. Uncertain when you don't. If no clean answer exists, say so.

Write as continuous flowing prose — NO bullets, NO headers, NO numbered steps. {length}. English only.
{philosopher_focus}

Knowledge:
{context}

Previous conversation:
{history}

Question: {question}

Answer:

{length_check}"""


# ============================================================
# POST-PROCESSING
# ============================================================

_STEP_LABEL_PATTERNS = [
    r"^\s*(STEP\s*\d+[:\.]?)\s*",
    r"^\s*(GENERATE|WEIGH|EXPAND|TENSION|EMERGE)[:\.]?\s*",
    r"^\s*\d+\.\s*(GENERATE|WEIGH|EXPAND|TENSION|EMERGE)[:\.]?\s*",
]

STRONG_MARKERS = [
    "clearly", "certainly", "without doubt", "fundamentally",
    "we know", "established", "demonstrates", "proves",
    "undeniably", "in fact", "the evidence shows",
    "निश्चित रूप से", "स्पष्ट है", "यह सत्य है",
]
EXPLORATORY_MARKERS = [
    "possibly", "it could be", "some suggest", "arguably",
    "it seems", "maybe", "we might wonder", "an open question",
    "genuinely uncertain", "we don't know", "hard to say",
    "शायद", "हो सकता है", "संभवतः", "यह कहना कठिन है",
]


def parse_flow_output(raw_text: str) -> dict:
    text = raw_text.strip()
    cleaned_lines = []
    for line in text.split('\n'):
        cleaned = line
        for pattern in _STEP_LABEL_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        cleaned_lines.append(cleaned)
    text = '\n'.join(cleaned_lines).strip()

    reflection_question = ""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if sentences:
        last = sentences[-1].strip()
        if last.endswith('?'):
            reflection_question = last

    text_lower = text.lower()
    strong_count = sum(1 for m in STRONG_MARKERS if m in text_lower)
    exploratory_count = sum(1 for m in EXPLORATORY_MARKERS if m in text_lower)

    return {
        "response": text,
        "reflection_question": reflection_question,
        "confidence_signals": {
            "strong": strong_count,
            "exploratory": exploratory_count,
        },
        "raw": raw_text,
    }