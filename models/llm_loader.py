# ============================================================
# models/llm_loader.py
# Groq API — fast cloud inference
# ============================================================

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL_MAIN = "llama-3.3-70b-versatile"
MODEL_FAST = "llama-3.1-8b-instant"

# Anti-repetition penalties.
# frequency_penalty penalizes tokens proportional to how often they appeared.
# presence_penalty penalizes any token that appeared at all (even once).
# Together they break Hindi repetition loops where LLaMA repeats entire sentences.
FREQUENCY_PENALTY = 0.5
PRESENCE_PENALTY = 0.3

# Fallback tracking
_model_stats = {"main": 0, "fallback": 0, "last_used": MODEL_MAIN}

def get_model_stats() -> dict:
    return {
        "current_model": _model_stats["last_used"],
        "main_calls": _model_stats["main"],
        "fallback_calls": _model_stats["fallback"],
    }


def _build_messages(prompt: str) -> list:
    """
    Split prompt into system + user messages if separator is present.
    Prompts containing '\\n===QUESTION===\\n' are split into:
      - system: everything before the separator (instructions)
      - user: everything after (the actual question)
    This makes LLMs follow length/repetition rules much more strictly.
    """
    separator = "\n===QUESTION===\n"
    if separator in prompt:
        system_part, user_part = prompt.split(separator, 1)
        return [
            {"role": "system", "content": system_part.strip()},
            {"role": "user", "content": user_part.strip()},
        ]
    return [{"role": "user", "content": prompt}]


def generate_response(prompt: str, max_tokens: int = 800) -> str:
    """Normal response — returns complete answer, falls back on rate limit"""
    messages = _build_messages(prompt)
    try:
        response = client.chat.completions.create(
            model=MODEL_MAIN,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
        )
        _model_stats["main"] += 1
        _model_stats["last_used"] = MODEL_MAIN
        return response.choices[0].message.content.strip()
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            print(f"⚠️ Rate limit hit — falling back to {MODEL_FAST}")
            try:
                response = client.chat.completions.create(
                    model=MODEL_FAST,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=FREQUENCY_PENALTY,
                    presence_penalty=PRESENCE_PENALTY,
                )
                _model_stats["fallback"] += 1
                _model_stats["last_used"] = MODEL_FAST
                return response.choices[0].message.content.strip()
            except Exception as e2:
                return f"Error: {str(e2)}"
        return f"Error: {str(e)}"


def generate_stream(prompt: str, max_tokens: int = 800):
    """
    Streaming response — word by word for all languages!
    Buffers tokens and yields at word boundaries (space, punctuation).
    Fallback: yields if buffer exceeds 8 chars with no boundary.
    """
    messages = _build_messages(prompt)
    model = MODEL_MAIN
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
            stream=True,
        )
        _model_stats["main"] += 1
        _model_stats["last_used"] = MODEL_MAIN
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            print(f"⚠️ Rate limit hit — falling back to {MODEL_FAST}")
            model = MODEL_FAST
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=FREQUENCY_PENALTY,
                presence_penalty=PRESENCE_PENALTY,
                stream=True,
            )
            _model_stats["fallback"] += 1
            _model_stats["last_used"] = MODEL_FAST
        else:
            yield f"Error: {str(e)}"
            return

    try:
        buffer = ""
        full_text = ""
        boundary_chars = {' ', '\n', '\u0964', '?', '!', ',', '.', ':', ';', '\u2014', '-'}

        for chunk in stream:
            token = chunk.choices[0].delta.content or ""

            if token:
                buffer += token

                # Yield at word boundary OR if buffer is long enough
                if any(c in buffer for c in boundary_chars) or len(buffer) >= 8:
                    yield buffer
                    full_text += buffer
                    buffer = ""

                    # In-stream repetition guard: check every ~300 chars
                    if len(full_text) > 300 and len(full_text) % 50 < 10:
                        if _stream_has_repetition(full_text):
                            print("🔁 Stream repetition detected — stopping early")
                            break

        # Flush remaining buffer
        if buffer:
            yield buffer

    except Exception as e:
        yield f"Error: {str(e)}"


def _stream_has_repetition(text: str) -> bool:
    """
    Detect if streaming text has fallen into a repetition loop.
    Splits into sentences and checks if 30%+ of sentence pairs share 3+ content words.
    Works for both Hindi (Devanagari) and English.
    """
    import re
    sentences = [s.strip() for s in re.split(r'[.।\n?!]', text) if len(s.strip()) > 15]
    if len(sentences) < 4:
        return False

    # Generous stop words — Hindi has many function words that inflate overlap
    stop_words = {
        # English
        'the', 'a', 'an', 'is', 'it', 'in', 'of', 'to', 'and', 'that',
        'this', 'we', 'you', 'not', 'but', 'for', 'are', 'was', 'has',
        'have', 'with', 'from', 'our', 'your', 'can', 'be', 'do', 'as',
        'or', 'at', 'by', 'on', 'if', 'its', 'so', 'me', 'my', 'they',
        # Hindi function words
        'है', 'हैं', 'के', 'का', 'की', 'और', 'को', 'में', 'से', 'यह',
        'हम', 'हमें', 'हमारे', 'हमारी', 'एक', 'पर', 'कि', 'भी', 'तो',
        'जो', 'वो', 'वह', 'ने', 'या', 'इस', 'उस', 'जब', 'तब',
        'करता', 'करती', 'करते', 'करने', 'करनी', 'होता', 'होती',
        'लिए', 'बारे', 'अपने', 'अपनी', 'अपना',
    }

    word_sets = []
    for s in sentences:
        words = {w.strip('.,!?।,') for w in s.split()
                 if w.strip('.,!?।,') not in stop_words and len(w.strip('.,!?।,')) > 2}
        word_sets.append(words)

    repeat_count = 0
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            if word_sets[i] and word_sets[j] and len(word_sets[i] & word_sets[j]) >= 3:
                repeat_count += 1

    total_pairs = len(word_sets) * (len(word_sets) - 1) / 2
    return total_pairs > 0 and (repeat_count / total_pairs) > 0.3


def generate_fast(prompt: str) -> str:
    """Fast version for reflection — fewer tokens, smaller model"""
    try:
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
