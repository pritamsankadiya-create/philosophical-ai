# ============================================================
# core/prajna_layer.py
# v4 "Pragya": The Prajna Layer — detecting what is NOT said
#
# Prajna (प्रज्ञा) = deep knowing that goes beyond surface information
# This layer detects:
# 1. Pattern of absence — what topics the user circles but never directly asks
# 2. Pronoun avoidance — asking 3rd person when they mean 1st person
# 3. Emotional displacement — asking philosophical when they're in pain
# 4. Escalation/de-escalation patterns across session
# 5. The gap between stated question and real need
#
# Inspired by: "The blind man who correctly identified every color"
# — knowledge that comes not from data, but from pattern of absence
# ============================================================

import re
from collections import Counter


# Concepts that often hide real personal pain when asked impersonally
_DISPLACEMENT_CONCEPTS = {
    "suffering": "Someone asking impersonally about suffering often means 'I am suffering'",
    "death": "Questions about death are often about fear of one's own mortality",
    "freedom": "Questions about freedom often mean 'I feel trapped'",
    "meaning": "Questions about meaning often mean 'I feel my life lacks meaning'",
    "love": "Questions about love often mean longing for connection",
    "existence": "Questions about existence can mask existential crisis",
    "purpose": "Questions about purpose often mean 'I don't know what I'm doing with my life'",
    "loneliness": "Questions about loneliness often mean 'I am lonely right now'",
    "self_hatred": "Someone expressing self-hatred is not asking philosophy — they need immediate warmth and presence",
    "world_weariness": "Exhaustion with the world often masks deep loneliness or unresolved pain — meet it with karuna",
    "self_love": "Inability to love oneself is one of the deepest wounds — respond with gentleness, not advice",
}

# Personal pronoun patterns — their absence is meaningful
_PERSONAL_PATTERNS_EN = re.compile(
    r'\b(i|me|my|myself|i\'m|i\'ve|i\'d|i\'ll)\b', re.IGNORECASE
)
_PERSONAL_PATTERNS_HI = re.compile(
    r'\b(main|mera|meri|mujhe|mai|apna|apne|मैं|मेरा|मेरी|मुझे)\b', re.IGNORECASE
)


def _has_personal_pronoun(question: str) -> bool:
    return bool(_PERSONAL_PATTERNS_EN.search(question)) or \
           bool(_PERSONAL_PATTERNS_HI.search(question))


def _detect_displacement(question: str, concepts: list) -> str:
    """
    Detect if user is asking philosophically about something they're experiencing personally.
    Returns a hint string if displacement is detected, else "".
    """
    # v7: CRISIS DIRECT CHECK — highest priority, runs before everything else
    CRISIS_SIGNALS_DIRECT = [
        # Self-hatred
        "ghrina nazar", "apne aap se ghrina", "khud se ghrina",
        "apne aap se nafrat", "khud se nafrat",
        "घृणा आती है", "खुद से घृणा", "अपने आप से घृणा",
        # World-weariness / exhaustion — BOTH Romanized AND Devanagari
        "sansar se ub", "duniya se ub", "ub chuka hoon",
        "ub gaya hoon", "is duniya se thak",
        "संसार से ऊब", "ऊब चुका", "ऊब गया", "ऊब", "दुनिया से ऊब",
        # Self-exclusion from love
        "sivay khud ke", "khud se pyaar nahi",
        "apne aap se pyaar nahi",
        "सिवाय खुद के", "खुद से प्यार नहीं",
        # Relationship disillusionment + isolation
        "rishte jhute", "koi apna nahi", "koi mera nahi",
        "is sansar mein koi nahi",
        "रिश्ते झूठे", "कोई अपना नहीं",
    ]

    lower_q = question.lower()
    for signal in CRISIS_SIGNALS_DIRECT:
        if signal in lower_q:
            return (
                "[Prajna: This person is expressing self-hatred, world-weariness, "
                "or deep isolation. THIS IS NOT PHILOSOPHY. "
                "Respond with karuna FIRST — warmth, presence, acknowledgment. "
                "NO wisdom injection. NO reframing. NO philosophy. "
                "Just be there with them. One gentle sentence that says: I hear you.]"
            )

    # ... existing code continues unchanged below
    has_personal = _has_personal_pronoun(question)
    if has_personal:
        return ""  # They're asking directly — no displacement

    lower_q = question.lower()
    word_count = len(question.split())

    # Short impersonal questions about heavy topics = likely displacement
    if word_count <= 12:
        for concept in concepts:
            if concept in _DISPLACEMENT_CONCEPTS:
                hint = _DISPLACEMENT_CONCEPTS[concept]
                return f"[Prajna: {hint} — respond with extra warmth even if question seems philosophical]"

    # Detect question patterns that mask personal experience
    displacement_patterns = [
        (r'\bwhy\s+do\s+people\b', "user may mean 'why do I'"),
        (r'\bwhy\s+does\s+one\b', "user may be asking about themselves"),
        (r'\bhow\s+do\s+people\s+(deal|handle|cope)\b', "user may need coping support"),
        (r'\bwhat\s+should\s+(one|a\s+person)\s+do\b', "user may need personal guidance"),
        (r'\binsaan\s+(kyun|kyu|kaise)\b', "user may be asking about themselves"),
        (r'\binsan\s+(kyun|kyu)\b', "user may be asking about themselves"),
    ]

    for pattern, hint in displacement_patterns:
        if re.search(pattern, lower_q):
            return f"[Prajna: {hint} — the question is likely personal, respond accordingly]"

    return ""


def _detect_circling(question_history: list, current_concepts: list) -> str:
    """
    Detect if user keeps returning to same concepts without resolution.
    Returns a hint if circling detected.
    """
    if len(question_history) < 4:
        return ""

    # Count concept frequency in recent history
    recent_concepts = []
    for entry in question_history[-8:]:
        recent_concepts.extend(entry.get("concepts", []))

    if not recent_concepts:
        return ""

    concept_freq = Counter(recent_concepts)
    top_repeated = [c for c, count in concept_freq.most_common(3) if count >= 3]

    if not top_repeated:
        return ""

    # They keep returning — but current question shares same territory
    overlap = [c for c in current_concepts if c in top_repeated]
    if overlap:
        concept_str = ", ".join(overlap[:2])
        return f"[Prajna: User has returned to '{concept_str}' multiple times — this territory has unresolved weight for them. Go deeper than before, offer a different angle.]"

    return ""


def _detect_rasa_stuck(rasa_journey: list, current_rasa: str) -> str:
    """
    Detect if user is emotionally stuck in the same rasa across many questions.
    v5: Lowered threshold from 6→4, added adbhut (wonder monotony).
    """
    if len(rasa_journey) < 4:
        return ""

    recent = rasa_journey[-6:]

    # v7: Alternating distress pattern — karuna + bibhatsa oscillating
    # Person swings between grief and emptiness — both need karuna response
    # Only fires when 2+ different distress rasas present (true alternation)
    if len(recent) >= 6:
        distress_rasas = {"karuna", "bibhatsa", "bhayanak"}
        distress_in_recent = [r for r in recent if r in distress_rasas]
        distress_count = len(distress_in_recent)
        distinct_distress = len(set(distress_in_recent))
        if distress_count >= 5 and distinct_distress >= 2:
            return (
                "[Prajna: This person is oscillating between grief and emptiness "
                "across many turns — karuna and bibhatsa alternating. "
                "They are in sustained distress. "
                "DO NOT offer new philosophy. DO NOT reframe. "
                "Simply be present. Ask: are you okay right now?]"
            )

    dominant_count = recent.count(current_rasa)

    if dominant_count >= 4 and current_rasa in ("karuna", "bibhatsa", "bhayanak", "adbhut"):
        rasa_messages = {
            "karuna": (
                "[Prajna: This person has been in pain across many turns. "
                "The grief is persistent and real. "
                "DO NOT philosophize. DO NOT reframe. "
                "Acknowledge the depth of their pain first — "
                "ONE sentence of genuine warmth before anything else. "
                "Then, and only then, a small opening toward light.]"
            ),
            "bibhatsa": (
                "[Prajna: This person has felt meaningless and empty across many turns. "
                "DO NOT argue with the emptiness. DO NOT offer hope too fast. "
                "Find ONE specific, concrete thing that still has texture in their world — "
                "even a tiny one. That specificity is the only bridge out of bibhatsa.]"
            ),
            "bhayanak": "[Prajna: This person has been afraid across many questions. The anxiety is chronic. Ground them first, philosophy second.]",
            "adbhut": "[Prajna: This person has been in wonder/curiosity for many turns — but the response tone is becoming monotonous. Break the pattern: offer a provocative counter-question, a personal challenge, or shift from 'wonder at the universe' to 'what does this mean for YOU'. Surprise them.]",
        }
        return rasa_messages.get(current_rasa, "")

    return ""


def _detect_absence_pattern(question_history: list, current_concepts: list) -> str:
    """
    The core of Prajna — what topics have they NEVER asked about?
    Sometimes what's missing reveals more than what's present.
    """
    if len(question_history) < 8:
        return ""

    # Collect all concepts ever asked about
    all_concepts = set()
    all_rasas = []
    all_intents = []
    for entry in question_history:
        all_concepts.update(entry.get("concepts", []))
        if entry.get("rasa"):
            all_rasas.append(entry["rasa"])
        if entry.get("intent"):
            all_intents.append(entry["intent"])

    # Pattern: Always asks 3rd person (explore), never personal (apply)
    intent_freq = Counter(all_intents)
    explore_count = intent_freq.get("explore", 0) + intent_freq.get("define", 0)
    apply_count = intent_freq.get("apply", 0)

    if explore_count >= 8 and apply_count == 0:
        return "[Prajna: This person consistently explores ideas intellectually but never asks how to apply them. They may be seeking understanding to avoid action. Gently offer one practical bridge.]"

    # Pattern: Deep philosophical questions but always in pain (karuna dominant)
    rasa_freq = Counter(all_rasas)
    karuna_pct = rasa_freq.get("karuna", 0) / max(len(all_rasas), 1)
    if karuna_pct >= 0.6 and "self" in all_concepts and "freedom" not in all_concepts:
        return "[Prajna: User explores self and suffering deeply but never asks about freedom or choice. They may feel trapped. Offer the possibility of agency gently.]"

    return ""


def get_prajna_insight(
    question: str,
    concepts: list,
    question_history: list,
    rasa_journey: list,
    current_rasa: str,
    language: str = "english"
) -> str:
    """
    v4: Main Prajna function — returns a subtle hint for the prompt.
    Combines all pattern detection into one actionable insight.

    Returns "" if no meaningful pattern detected.
    Returns a bracketed hint string if a pattern is found.
    """
    insights = []

    # 1. Displacement detection (asking philosophical when really personal)
    displacement = _detect_displacement(question, concepts)
    if displacement:
        insights.append(displacement)

    # 2. Circling detection (returning to same topics unresolved)
    circling = _detect_circling(question_history, concepts)
    if circling:
        insights.append(circling)

    # 3. Rasa stuck detection (emotionally stuck)
    rasa_stuck = _detect_rasa_stuck(rasa_journey, current_rasa)
    if rasa_stuck:
        insights.append(rasa_stuck)

    # 4. Absence pattern (what they never ask = what they need)
    absence = _detect_absence_pattern(question_history, concepts)
    if absence:
        insights.append(absence)

    if not insights:
        return ""

    # Return most important insight (first detected = highest priority)
    primary = insights[0]
    print(f"🔮 Prajna insight detected: {primary[:60]}...")
    return primary