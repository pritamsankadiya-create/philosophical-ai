# ============================================================
# 📁 models/llm_loader.py
# ⚡ Streaming + Normal response with Hindi fix!
# ============================================================

import requests
import json


def generate_response(prompt: str, max_tokens: int = 300) -> str:
    """Normal response — returns complete answer"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model"  : "mistral",
        "prompt" : prompt,
        "stream" : False,
        "options": {
            "temperature"   : 0.7,
            "num_predict"   : max_tokens,
            "top_k"         : 20,
            "top_p"         : 0.9,
            "repeat_penalty": 1.1,
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=180)
        return response.json()["response"].strip()
    except requests.exceptions.Timeout:
        return "⏱️ Timeout. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def generate_stream(prompt: str, max_tokens: int = 300):
    """
    ⚡ Streaming response — word by word for all languages!
    Buffers tokens and yields at word boundaries (space, punctuation).
    Fallback: yields if buffer exceeds 8 chars with no boundary,
    so streaming never gets stuck.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model"  : "mistral",
        "prompt" : prompt,
        "stream" : True,
        "options": {
            "temperature"   : 0.7,
            "num_predict"   : max_tokens,
            "top_k"         : 20,
            "top_p"         : 0.9,
            "repeat_penalty": 1.1,
        }
    }

    try:
        # timeout=(connect, read) — 10s to connect, 300s for first token
        response = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=(10, 300)
        )

        buffer = ""
        boundary_chars = {' ', '\n', '।', '?', '!', ',', '.', ':', ';', '—', '-'}

        for line in response.iter_lines():
            if line:
                data  = json.loads(line)
                token = data.get("response", "")
                done  = data.get("done", False)

                if token:
                    buffer += token

                    # Yield at word boundary OR if buffer is long enough
                    # (fallback prevents getting stuck)
                    if any(c in buffer for c in boundary_chars) or len(buffer) >= 8:
                        yield buffer
                        buffer = ""

                if done:
                    if buffer:
                        yield buffer
                    break

    except Exception as e:
        yield f"❌ Error: {str(e)}"


def generate_fast(prompt: str) -> str:
    """Fast version for reflection — fewer tokens"""
    return generate_response(prompt, max_tokens=150)


def load_embeddings(model_name: str = "nomic-embed-text"):
    """Load embeddings for vector search"""
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(model=model_name)