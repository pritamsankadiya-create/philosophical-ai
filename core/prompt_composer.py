# ============================================================
# core/prompt_composer.py
# Embeds Reasoning Engine + Dialectic Engine into prompts
# ============================================================

from core.concept_analyzer import ConceptAnalysis


# Theme → reasoning framework prompts
REASONING_FRAMEWORKS = {
    "vedanta": "Consider the Advaita perspective: what is the ultimate reality behind appearances?",
    "buddhism": "Apply the Middle Way. How does attachment or impermanence relate?",
    "stoicism": "What is within our control? What would a Stoic sage advise?",
    "gita_philosophy": "What does dharma require here? Consider the balance of action and detachment.",
    "sufi_mysticism": "What does the heart's longing reveal? Consider the union of lover and beloved.",
    "yoga": "How does inner discipline lead to clarity? Consider the path of self-mastery.",
    "existentialism": "What does authentic existence demand? Consider freedom and responsibility.",
    "rationalism": "What can reason alone tell us? Examine the logical foundations.",
    "philosophy_of_mind": "What is the nature of subjective experience? Consider the relationship between mind and reality.",
}

REASONING_FRAMEWORKS_HINDI = {
    "vedanta": "अद्वैत दृष्टिकोण से विचार करो: दिखावे के पीछे परम सत्य क्या है?",
    "buddhism": "मध्यम मार्ग अपनाओ। आसक्ति या अनित्यता कैसे संबंधित है?",
    "stoicism": "क्या हमारे नियंत्रण में है? एक स्टोइक ऋषि क्या सलाह देते?",
    "gita_philosophy": "यहाँ धर्म क्या माँगता है? कर्म और वैराग्य के संतुलन पर विचार करो।",
    "sufi_mysticism": "दिल की तड़प क्या प्रकट करती है? प्रेमी और प्रेमास्पद के मिलन पर विचार करो।",
    "yoga": "आंतरिक अनुशासन से स्पष्टता कैसे आती है? आत्म-नियंत्रण के मार्ग पर विचार करो।",
    "existentialism": "प्रामाणिक अस्तित्व क्या माँगता है? स्वतंत्रता और उत्तरदायित्व पर विचार करो।",
    "rationalism": "तर्क अकेला क्या बता सकता है? तार्किक नींव की जाँच करो।",
    "philosophy_of_mind": "व्यक्तिगत अनुभव की प्रकृति क्या है? मन और वास्तविकता के संबंध पर विचार करो।",
}

# Intent → instruction for the LLM
INTENT_INSTRUCTIONS = {
    "define": "Define clearly, then deepen with philosophical insight.",
    "compare": "Present each view fairly, find points of agreement and disagreement, then offer a synthesis.",
    "apply": "Give practical wisdom grounded in philosophy. Be actionable.",
    "challenge": "Steelman the opposing view first, then offer your counter with depth.",
    "explore": "Explore the question with depth and multiple perspectives.",
}

INTENT_INSTRUCTIONS_HINDI = {
    "define": "पहले स्पष्ट परिभाषा दो, फिर दार्शनिक गहराई से समझाओ।",
    "compare": "प्रत्येक दृष्टिकोण को निष्पक्षता से प्रस्तुत करो, सहमति और असहमति खोजो, फिर संश्लेषण करो।",
    "apply": "दर्शन पर आधारित व्यावहारिक ज्ञान दो। कार्यान्वयन योग्य बनाओ।",
    "challenge": "पहले विरोधी दृष्टिकोण को मजबूती से प्रस्तुत करो, फिर गहराई से खंडन करो।",
    "explore": "प्रश्न को गहराई और विविध दृष्टिकोणों से खोजो।",
}


def _build_reasoning_section(analysis: ConceptAnalysis, language: str) -> str:
    """Select reasoning frameworks based on detected themes."""
    frameworks = REASONING_FRAMEWORKS_HINDI if language == "hindi" else REASONING_FRAMEWORKS

    lines = []
    used = set()
    for theme in analysis.themes[:3]:
        if theme in frameworks and theme not in used:
            lines.append(f"  - {frameworks[theme]}")
            used.add(theme)

    if not lines:
        return ""

    if language == "hindi":
        header = "दार्शनिक ढाँचे:"
    else:
        header = "Reasoning frameworks to apply:"
    return f"\n{header}\n" + "\n".join(lines)


def _build_dialectic_section(analysis: ConceptAnalysis, language: str) -> str:
    """Build dialectic template for standard/deep questions."""
    if analysis.question_depth == "simple":
        return ""

    if language == "hindi":
        return """
संरचना:
1. सामान्य समझ (थीसिस) प्रस्तुत करो
2. गहरा या विरोधी दृष्टिकोण (एंटीथीसिस) स्वीकार करो
3. एक समृद्ध संश्लेषण पर पहुँचो"""
    else:
        return """
Structure your reasoning:
1. Present the common understanding (thesis)
2. Acknowledge a deeper or opposing view (antithesis)
3. Arrive at a richer synthesis"""


def _build_multi_perspective(analysis: ConceptAnalysis, language: str) -> str:
    """Instruct LLM to present multiple philosophical perspectives."""
    if analysis.question_depth == "simple":
        return ""

    # Map theme keys to readable tradition names
    THEME_LABELS = {
        "vedanta": "Vedanta", "buddhism": "Buddhism",
        "stoicism": "Stoicism", "existentialism": "Existentialism",
        "gita_philosophy": "Gita/Karma Yoga", "sufi_mysticism": "Sufi Mysticism",
        "yoga": "Yoga", "rationalism": "Rationalism",
        "philosophy_of_mind": "Philosophy of Mind",
    }
    THEME_LABELS_HINDI = {
        "vedanta": "वेदांत", "buddhism": "बौद्ध दर्शन",
        "stoicism": "स्टोइक दर्शन", "existentialism": "अस्तित्ववाद",
        "gita_philosophy": "गीता/कर्म योग", "sufi_mysticism": "सूफ़ी दर्शन",
        "yoga": "योग दर्शन", "rationalism": "तर्कवाद",
        "philosophy_of_mind": "मनोदर्शन",
    }

    labels = THEME_LABELS_HINDI if language == "hindi" else THEME_LABELS
    traditions = [labels[t] for t in analysis.themes[:3] if t in labels]

    # If less than 2 detected, add defaults for breadth
    if len(traditions) < 2:
        if language == "hindi":
            defaults = ["वेदांत", "बौद्ध दर्शन", "स्टोइक दर्शन"]
        else:
            defaults = ["Vedanta", "Buddhism", "Stoicism"]
        for d in defaults:
            if d not in traditions:
                traditions.append(d)
            if len(traditions) >= 3:
                break

    tradition_list = ", ".join(traditions)

    if language == "hindi":
        return f"\nएक से अधिक दृष्टिकोण दो। कम से कम 2-3 परंपराओं से उत्तर दो: {tradition_list}।"
    else:
        return f"\nPresent multiple perspectives. Draw from at least 2-3 traditions: {tradition_list}."


def _build_philosopher_focus(analysis: ConceptAnalysis, language: str) -> str:
    """Add philosopher-specific focus when one is mentioned."""
    if not analysis.philosophers:
        return ""

    names = ", ".join(analysis.philosophers[:2])
    if language == "hindi":
        return f"\n{names} के दर्शन पर विशेष ध्यान दो।"
    else:
        return f"\nFocus especially on the philosophy of {names}."


def compose_prompt(question: str, translated: str, context: str,
                   history: str, analysis: ConceptAnalysis) -> str:
    """
    Compose the full prompt with embedded reasoning and dialectic engines.
    """
    language = analysis.language

    intent_instruction = (INTENT_INSTRUCTIONS_HINDI if language == "hindi"
                         else INTENT_INSTRUCTIONS).get(analysis.intent, "")

    reasoning = _build_reasoning_section(analysis, language)
    dialectic = _build_dialectic_section(analysis, language)
    multi_perspective = _build_multi_perspective(analysis, language)
    philosopher_focus = _build_philosopher_focus(analysis, language)

    # Determine sentence count based on depth
    if analysis.question_depth == "simple":
        sentences = "3-4"
    else:
        sentences = "4-6"

    if language == "hindi":
        prompt = f"""तुम एक दार्शनिक गुरु हो।
नीचे दिए ज्ञान से प्रश्न का उत्तर दो।
केवल हिंदी में। {sentences} वाक्य। सीधे उत्तर दो।
{intent_instruction}

ज्ञान:
{context}
{reasoning}{dialectic}{multi_perspective}{philosopher_focus}

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:"""

    else:
        prompt = f"""You are a wise philosophical guru.
Answer the question using the knowledge below.
Give {sentences} sentences. Stay on topic. Be direct and deep.
{intent_instruction}

Knowledge:
{context}
{reasoning}{dialectic}{multi_perspective}{philosopher_focus}

Previous conversation:
{history}

Question: {question}

Answer:"""

    return prompt
