# ============================================================
# models/llm_loader.py
# Groq API — fast cloud inference
# ============================================================

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL_MAIN = "llama-3.3-70b-versatile"
MODEL_FAST = "llama-3.1-8b-instant"


def generate_response(prompt: str, max_tokens: int = 300) -> str:
    """Normal response — returns complete answer"""
    try:
        response = client.chat.completions.create(
            model=MODEL_MAIN,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def generate_stream(prompt: str, max_tokens: int = 300):
    """
    Streaming response — word by word for all languages!
    Buffers tokens and yields at word boundaries (space, punctuation).
    Fallback: yields if buffer exceeds 8 chars with no boundary.
    """
    try:
        stream = client.chat.completions.create(
            model=MODEL_MAIN,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            stream=True,
        )

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
            max_tokens=150,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
