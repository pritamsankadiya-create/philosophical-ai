# ============================================================
# models/llm_loader.py
# Groq API — fast cloud inference
# ============================================================

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL_MAIN = "llama-3.3-70b-versatile"
MODEL_FAST = "llama-3.1-8b-instant"

# Fallback tracking
_model_stats = {"main": 0, "fallback": 0, "last_used": MODEL_MAIN}

def get_model_stats() -> dict:
    return {
        "current_model": _model_stats["last_used"],
        "main_calls": _model_stats["main"],
        "fallback_calls": _model_stats["fallback"],
    }


def generate_response(prompt: str, max_tokens: int = 800) -> str:
    """Normal response — returns complete answer, falls back on rate limit"""
    try:
        response = client.chat.completions.create(
            model=MODEL_MAIN,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
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
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
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
    model = MODEL_MAIN
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
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
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                stream=True,
            )
            _model_stats["fallback"] += 1
            _model_stats["last_used"] = MODEL_FAST
        else:
            yield f"Error: {str(e)}"
            return

    try:
        buffer = ""
        boundary_chars = {' ', '\n', '\u0964', '?', '!', ',', '.', ':', ';', '\u2014', '-'}

        for chunk in stream:
            token = chunk.choices[0].delta.content or ""

            if token:
                buffer += token

                # Yield at word boundary OR if buffer is long enough
                if any(c in buffer for c in boundary_chars) or len(buffer) >= 8:
                    yield buffer
                    buffer = ""

        # Flush remaining buffer
        if buffer:
            yield buffer

    except Exception as e:
        yield f"Error: {str(e)}"


def generate_fast(prompt: str) -> str:
    """Fast version for reflection — fewer tokens, smaller model"""
    try:
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
