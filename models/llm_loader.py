# ============================================================
# models/llm_loader.py
# Groq API — multi-tier fallback chain
#
# Chain: qwen3.8 → gpt-oss-120b → gpt-oss-20b
#   Main:  1K RPD, 2M TPD   (best Hindi, clean output)
#   Tier2: 1K RPD, 200K TPD (strong Hindi, no think tags)
#   Tier3: 1K RPD, 200K TPD (decent, fast reflection)
#   Total: 3K RPD, 2.4M TPD
#
# Future backup: Cerebras API (LLaMA 3.3 70B, 1M tok/day)
# ============================================================

import os
import re
from datetime import datetime, timezone
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Model chain ──────────────────────────────────────────
MODEL_MAIN  = "qwen/qwen3.8-27b"       # Tier 1: best quality + 2M TPD
MODEL_MID   = "openai/gpt-oss-120b"    # Tier 2: strong Hindi, 200K TPD
MODEL_FAST  = "openai/gpt-oss-20b"     # Tier 3: fast/reflection, 200K TPD

FALLBACK_CHAIN = [MODEL_MID, MODEL_FAST]

# Anti-repetition penalties
FREQUENCY_PENALTY = 0.4
PRESENCE_PENALTY = 0.25

# ── Fallback monitoring ──────────────────────────────────

_model_stats = {
    "main": 0,
    "fallback": 0,
    "errors": 0,
    "last_used": MODEL_MAIN,
    "last_fallback_time": None,
    "last_fallback_reason": None,
    "fallback_log": [],
    "both_failed": 0,
    "per_model": {
        MODEL_MAIN: {"calls": 0, "errors": 0},
        MODEL_MID:  {"calls": 0, "errors": 0},
        MODEL_FAST: {"calls": 0, "errors": 0},
    },
}

_last_call_info = {
    "model_used": MODEL_MAIN,
    "was_fallback": False,
    "fallback_reason": "",
}

_MAX_FALLBACK_LOG = 20


def _log_fallback(reason: str, model_tried: str, error_msg: str = ""):
    """Record a fallback event with timestamp."""
    now = datetime.now(timezone.utc).isoformat()
    _model_stats["fallback"] += 1
    _model_stats["last_fallback_time"] = now
    _model_stats["last_fallback_reason"] = reason
    _model_stats["fallback_log"].append({
        "time": now,
        "reason": reason,
        "model_tried": model_tried,
        "error": error_msg[:200],
    })
    if len(_model_stats["fallback_log"]) > _MAX_FALLBACK_LOG:
        _model_stats["fallback_log"].pop(0)
    print(f"⚠️ {model_tried} rate limited → trying next in chain")


def _set_call_info(model: str, was_fallback: bool, reason: str = ""):
    _last_call_info["model_used"] = model
    _last_call_info["was_fallback"] = was_fallback
    _last_call_info["fallback_reason"] = reason


def _record_call(model: str):
    _model_stats["last_used"] = model
    if model == MODEL_MAIN:
        _model_stats["main"] += 1
    else:
        _model_stats["fallback"] += 1
    if model in _model_stats["per_model"]:
        _model_stats["per_model"][model]["calls"] += 1


def _record_error(model: str):
    _model_stats["errors"] += 1
    if model in _model_stats["per_model"]:
        _model_stats["per_model"][model]["errors"] += 1


def get_last_call_info() -> dict:
    return dict(_last_call_info)


def get_model_stats() -> dict:
    total = _model_stats["main"] + _model_stats["fallback"]
    fallback_pct = (_model_stats["fallback"] / total * 100) if total > 0 else 0.0
    return {
        "current_model": _model_stats["last_used"],
        "primary_model": MODEL_MAIN,
        "fallback_chain": FALLBACK_CHAIN,
        "main_calls": _model_stats["main"],
        "fallback_calls": _model_stats["fallback"],
        "fallback_percentage": round(fallback_pct, 1),
        "total_calls": total,
        "errors": _model_stats["errors"],
        "all_failed": _model_stats["both_failed"],
        "per_model": _model_stats["per_model"],
        "last_fallback_time": _model_stats["last_fallback_time"],
        "last_fallback_reason": _model_stats["last_fallback_reason"],
        "recent_fallbacks": _model_stats["fallback_log"][-5:],
    }


# ── Message building ─────────────────────────────────────

def _build_messages(prompt: str) -> list:
    separator = "\n===QUESTION===\n"
    if separator in prompt:
        system_part, user_part = prompt.split(separator, 1)
        return [
            {"role": "system", "content": system_part.strip()},
            {"role": "user", "content": user_part.strip()},
        ]
    return [{"role": "user", "content": prompt}]


# ── Response safety ──────────────────────────────────────

def _safe_content(response) -> str:
    content = response.choices[0].message.content
    if content is None:
        return ""
    return _strip_reasoning_artifacts(content.strip())


def _strip_reasoning_artifacts(text: str) -> str:
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'</?think>', '', text)
    text = re.sub(r'<\|(start|end|channel|message|return|call)\|>', '', text)
    return text.strip()


def _is_rate_limit(e: Exception) -> bool:
    error_str = str(e).lower()
    exc_type = type(e).__name__.lower()
    if "ratelimit" in exc_type or "rate_limit" in exc_type:
        return True
    if any(phrase in error_str for phrase in ["rate_limit", "rate limit", "429", "too many requests"]):
        return True
    if hasattr(e, 'status_code') and e.status_code == 429:
        return True
    return False


# ── Core: try model with chain fallback ──────────────────

def _call_with_chain(messages: list, max_tokens: int, stream: bool = False):
    """
    Try MODEL_MAIN first, then walk through FALLBACK_CHAIN.
    Returns (response_or_stream, model_used) or raises if all fail.
    """
    models_to_try = [MODEL_MAIN] + FALLBACK_CHAIN
    last_error = None

    for i, model in enumerate(models_to_try):
        try:
            result = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=FREQUENCY_PENALTY,
                presence_penalty=PRESENCE_PENALTY,
                stream=stream,
            )
            _record_call(model)
            is_fallback = (i > 0)
            reason = f"tier{i}_rate_limit" if is_fallback else ""
            _set_call_info(model, is_fallback, reason)
            return result, model

        except Exception as e:
            last_error = e
            if _is_rate_limit(e):
                _log_fallback(f"tier{i+1}_rate_limit", model, str(e))
                continue  # try next in chain
            else:
                # Non-rate-limit error — don't try other models
                _record_error(model)
                _set_call_info("none", i > 0, f"error: {str(e)[:80]}")
                raise

    # All models rate limited
    _model_stats["both_failed"] += 1
    _record_error("all")
    _set_call_info("none", True, "all_rate_limited")
    raise AllModelsRateLimited(str(last_error))


class AllModelsRateLimited(Exception):
    pass


RATE_LIMIT_MSG = "🙏 सभी मॉडल अभी व्यस्त हैं। कृपया कुछ मिनट बाद पूछें। / All models are busy. Please try again shortly."


# ── Generation functions ─────────────────────────────────

def generate_response(prompt: str, max_tokens: int = 800) -> str:
    """Normal response with multi-tier fallback."""
    messages = _build_messages(prompt)
    try:
        response, model = _call_with_chain(messages, max_tokens, stream=False)
        return _safe_content(response)
    except AllModelsRateLimited:
        return RATE_LIMIT_MSG
    except Exception as e:
        if "rate_limit" in str(e).lower():
            # Fallback to smaller model
            response = client.chat.completions.create(
                model=MODEL_FALLBACK,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        return f"Error: {str(e)}"


def generate_stream(prompt: str, max_tokens: int = 800):
    """Streaming response with multi-tier fallback and reasoning tag filter."""
    messages = _build_messages(prompt)
    try:
        stream, model = _call_with_chain(messages, max_tokens, stream=True)
    except AllModelsRateLimited:
        yield RATE_LIMIT_MSG
        return
    except Exception as e:
        yield f"Error: {str(e)}"
        return

    try:
        buffer = ""
        full_text = ""
        in_think_block = False
        boundary_chars = {' ', '\n', '\u0964', '?', '!', ',', '.', ':', ';', '\u2014', '-'}

        for chunk in stream:
            token = chunk.choices[0].delta.content or ""

            if token:
                # Filter leaked reasoning tags (safety for gpt-oss fallback)
                if '<think>' in token:
                    in_think_block = True
                    token = token.split('<think>')[0]
                if in_think_block:
                    if '</think>' in token:
                        in_think_block = False
                        token = token.split('</think>')[-1]
                    else:
                        continue

                token = re.sub(r'<\|(start|end|channel|message|return|call)\|>', '', token)
                if not token:
                    continue

                buffer += token

                if any(c in buffer for c in boundary_chars) or len(buffer) >= 8:
                    yield buffer
                    full_text += buffer
                    buffer = ""

                    if len(full_text) > 300 and len(full_text) % 50 < 10:
                        if _stream_has_repetition(full_text):
                            print("🔁 Stream repetition detected — stopping early")
                            break

        if buffer:
            yield buffer

    except Exception as e:
        if "rate_limit" in str(e).lower():
            # Fallback to smaller model for streaming
            stream = client.chat.completions.create(
                model=MODEL_FALLBACK,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                stream=True,
            )
            buffer = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    buffer += token
                    if any(c in buffer for c in boundary_chars) or len(buffer) >= 8:
                        yield buffer
                        buffer = ""
            if buffer:
                yield buffer
        else:
            yield f"Error: {str(e)}"


def _stream_has_repetition(text: str) -> bool:
    sentences = [s.strip() for s in re.split(r'[.।\n?!]', text) if len(s.strip()) > 15]
    if len(sentences) < 4:
        return False

    stop_words = {
        'the', 'a', 'an', 'is', 'it', 'in', 'of', 'to', 'and', 'that',
        'this', 'we', 'you', 'not', 'but', 'for', 'are', 'was', 'has',
        'have', 'with', 'from', 'our', 'your', 'can', 'be', 'do', 'as',
        'or', 'at', 'by', 'on', 'if', 'its', 'so', 'me', 'my', 'they',
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
    """Fast version for reflection — uses tier 3 model."""
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
        return _safe_content(response)
    except Exception as e:
        return f"Error: {str(e)}"
