# ============================================================
# core/jev_classifier.py
# Jev-1.13 classifier — single API call for all classification signals
# Falls back to pure Python (concept_analyzer) on any error
# ============================================================

import os
import time
import requests
from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class JevResult:
    question_type: str = "mixed"
    emotional_intensity: str = "low"
    crisis_signal: float = 0.0
    rasa: str = "shaant"
    contract: str = "default"
    depth: str = "medium"
    language: str = "english"
    warmth_first: bool = False
    confidence: Dict[str, float] = field(default_factory=dict)
    latency_ms: float = 0.0


# ─── Stats tracking ──────────────────────────────────────────

_stats = {
    "calls": 0,
    "successes": 0,
    "failures": 0,
    "total_latency_ms": 0.0,
}


def get_jev_stats() -> dict:
    avg = (_stats["total_latency_ms"] / _stats["successes"]
           if _stats["successes"] > 0 else 0.0)
    return {
        "calls": _stats["calls"],
        "successes": _stats["successes"],
        "failures": _stats["failures"],
        "avg_latency_ms": round(avg, 1),
    }


# ─── Payload builder ─────────────────────────────────────────

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
JEV_TIMEOUT = 2.0  # seconds — fail fast to Python fallback


def _build_payload(question: str, translated: str, language_hint: str, history: str = "") -> dict:
    return {
        "model": JEV_MODEL,
        "state": {
            "question": question,
            "language_of_question": language_hint,
            "translated_to_english": translated,
            "conversation_history": history[-300:] if history else "",
        },
        "questions": {
            "crisis_signal": {
                "type": "noul",
                "instructions": "Does this indicate crisis or self-harm?",
                "criteria": {
                    "true": (
                        "Explicit or implicit self-harm, suicidal ideation, "
                        "death wish, extreme despair. "
                        "Direct death/suicide signals: "
                        "'mrityu hi ek raasta hai', "
                        "'mar jana chahta hun', "
                        "'khatam kar lun khud ko', "
                        "'jeena nahi chahta', "
                        "'jine ka mann nahi', "
                        "'zindagi khatam kar lun', "
                        "'mujhe nahi rehna', "
                        "'sab khatam kar dun', "
                        "Self-hatred signals: "
                        "'khud se ghrina', "
                        "'apne aap se nafrat', "
                        "'main bekaar hoon', "
                        "'meri wajah se sab bura', "
                        "'koi kaam ka nahi hun', "
                        "'main ek bojh hoon', "
                        "World-weariness extreme: "
                        "'sansar se ub gaya hoon', "
                        "'sab kuch vyarth hai', "
                        "'kuch bhi achha nahi lagta', "
                        "'duniya se thak gaya', "
                        "'bas ho gaya ab', "
                        "Hopelessness signals: "
                        "'koi umeed nahi bachi', "
                        "'ab kuch nahi hoga', "
                        "'sab kuch barbaad ho gaya', "
                        "'koi raasta nahi dikh raha', "
                        "'andhera hi andhera hai', "
                        "Isolation extreme: "
                        "'koi nahi hai mera', "
                        "'sab chhod gaye', "
                        "'bilkul akela hoon', "
                        "'koi samajhta nahi koi', "
                        "'is duniya mein koi apna nahi'"
                    ),
                    "false": (
                        "Philosophical inquiry without personal distress. "
                        "NOT crisis — these are intellectual: "
                        "'mrityu ke baad kya hota hai', "
                        "'consciousness kya hai', "
                        "'jeevan ka arth kya hai', "
                        "'atma kya hai', "
                        "'moksha kya hota hai', "
                        "'brahman kya hai', "
                        "'kya hum sach mein hain', "
                        "'samay kya hota hai'"
                    ),
                },
            },
            "emotional_intensity": {
                "type": "choice",
                "instructions": "What is the emotional intensity of this question?",
                "criteria": {
                    "high": (
                        "Crisis, deep pain, self-harm risk, suicidal ideation, "
                        "extreme suffering, self-hatred. "
                        "Hindi/Hinglish: 'bahut dard', 'bahut takleef', "
                        "'bahut dukh', 'bahut rona', 'zindagi bekaar', "
                        "'koi matlab nahi', 'haar gaya', 'sab khatam', "
                        "'kuch nahi bacha', 'koi fayda nahi', "
                        "'jeena nahi', 'ghrina nazar aati hai'"
                    ),
                    "medium": (
                        "Sadness, confusion, mild distress, loneliness, frustration. "
                        "Hindi/Hinglish: 'pareshan', 'samajh nahi aa raha', "
                        "'kya karu', 'bahut akela', 'bahut thak gaya', "
                        "'bahut udas', 'sukoon nahi', 'chain nahi', "
                        "'himmat nahi', 'hausla nahi', "
                        "Longing, nostalgia, heartbreak: "
                        "'bahut yaad aa rahi hai', 'dil bhar aaya', "
                        "'aankhein bhar aayi', 'kuch kho gaya lagta hai', "
                        "'woh din yaad aa gaye', 'dil nahi lag raha kahi'"
                    ),
                    "low": (
                        "Curiosity, calm inquiry, intellectual exploration. "
                        "Hindi/Hinglish: 'yeh bahut interesting hai', "
                        "'aur batao yaar', 'mujhe samajhna hai', "
                        "'bahut mast sawaal hai', 'wow yeh toh kamaal hai', "
                        "'sach mein aisa hota hai'"
                    ),
                },
            },
            "rasa": {
                "type": "choice",
                "instructions": "Primary emotion (Navarasa framework) in the question?",
                "criteria": {
                    "karuna": (
                        "Grief, pain, compassion, suffering, sadness, loneliness. "
                        "Hindi/Hinglish: 'dard', 'dukh', 'rona', 'aansu', "
                        "'akela', 'toot gaya', 'koi nahi samajhta', "
                        "'chhod diya', 'tadap', 'kasht', 'peeda'"
                    ),
                    "bhayanak": (
                        "Fear, anxiety, dread, terror. "
                        "Hindi/Hinglish: 'darr', 'dar lag raha', 'ghabra', "
                        "'chinta', 'kya hoga', 'pata nahi kya hoga'"
                    ),
                    "raudra": (
                        "Anger, frustration, rage. "
                        "Hindi/Hinglish: 'gussa', 'naraaz', 'nafrat', "
                        "'tang aa gaya', 'bahut ho gaya', 'dhoka', 'galat hai'"
                    ),
                    "bibhatsa": (
                        "Disgust, emptiness, world-weariness, self-hatred. "
                        "Hindi/Hinglish: 'kya fayda', 'sab bekaar', 'thak gaya', "
                        "'mann nahi', 'kuch accha nahi lagta', 'koi matlab nahi', "
                        "'ghrina', 'sansar se ub gaya'"
                    ),
                    "shringaar": (
                        "Love, longing, romantic ache. "
                        "Hindi/Hinglish: 'pyaar', 'mohabbat', 'ishq', "
                        "'yaad aata hai', 'dil', 'rishta', 'mere saath', "
                        "'bahut pyaar hai mujhe', 'dil mein kuch alag feel hai', "
                        "'woh bahut special hai mere liye', "
                        "'unke baare mein sochta rehta hoon'"
                    ),
                    "veer": (
                        "Courage, determination, heroic spirit. "
                        "Hindi/Hinglish: 'karna hai', 'hausla', 'himmat', "
                        "'haar nahi maanunga', 'badalna hai', 'kar dikhaunga'"
                    ),
                    "adbhut": (
                        "Wonder, curiosity, awe, amazement. "
                        "Hindi/Hinglish: 'hairaan', 'ajeeb', 'samajh nahi aata', "
                        "'kya hai ye', 'kyun hota hai', 'sochta rehta hoon', "
                        "'yeh kaise hota hai', 'itna deep kyun hai yeh', "
                        "'pehli baar socha aisa', 'dimag ghoom gaya', "
                        "'yeh toh sochne wali baat hai'"
                    ),
                    "hasya": (
                        "Joy, humor, lightness, playfulness. "
                        "Hindi/Hinglish: 'mazaak', 'hansi', 'hasna', "
                        "'haha yeh toh mast hai', 'bhai kya baat hai', "
                        "'yaar mazaa aa gaya', 'LOL yeh sach mein?'"
                    ),
                    "shaant": (
                        "Peace, calm, equanimity, serenity. "
                        "Hindi/Hinglish: 'shanti', 'sukoon', 'theek hai', "
                        "'samajhna chahta hoon', 'sochna', 'vichar', 'khamoshi'"
                    ),
                },
            },
        },
    }


# ─── Response parser ─────────────────────────────────────────

def _parse_jev_response(data: dict, latency_ms: float) -> JevResult:
    answers = data.get("answers", {})

    def _get_noul(key: str, default: float) -> float:
        ans = answers.get(key, {})
        if isinstance(ans, dict):
            # Jev returns {"type": "noul", "noul": 0.98} — key is "noul", not "value"
            val = ans.get("noul", ans.get("value"))
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, bool):
                return 1.0 if val else 0.0
            if isinstance(val, str):
                try:
                    return float(val)
                except ValueError:
                    return 1.0 if val.lower() == "true" else 0.0
        return default

    def _get_choice(key: str, default: str) -> str:
        ans = answers.get(key, {})
        if isinstance(ans, dict):
            # Jev choice: {"type": "choice", "choice": "value"} or {"value": "..."}
            return ans.get("choice", ans.get("value", default))
        return default

    crisis_signal = _get_noul("crisis_signal", 0.0)
    emotional_intensity = _get_choice("emotional_intensity", "low")
    rasa = _get_choice("rasa", "shaant")

    return JevResult(
        crisis_signal=crisis_signal,
        emotional_intensity=emotional_intensity,
        rasa=rasa,
        latency_ms=latency_ms,
    )


# ─── Main classifier ─────────────────────────────────────────

def classify_with_jev(question: str, translated: str, language_hint: str, history: str = "") -> Optional[JevResult]:
    """
    Classify a question using Jev-1.13 via OpenRouter decisions API.
    Returns JevResult on success, None on any failure (timeout, HTTP error, missing key).
    Currently used for crisis detection only — Python handles all other classification.
    """
    api_key = os.environ.get("JEV_API_KEY")
    if not api_key:
        return None

    _stats["calls"] += 1
    payload = _build_payload(question, translated, language_hint, history)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        start = time.monotonic()
        response = requests.post(
            JEV_URL, headers=headers, json=payload,
            timeout=JEV_TIMEOUT,
        )
        latency_ms = (time.monotonic() - start) * 1000

        if response.status_code != 200:
            print(f"⚠️ Jev API error {response.status_code}: {response.text[:200]}")
            _stats["failures"] += 1
            return None

        data = response.json()
        result = _parse_jev_response(data, latency_ms)

        _stats["successes"] += 1
        _stats["total_latency_ms"] += latency_ms
        print(f"🎯 Jev: crisis={result.crisis_signal:.2f}, EI={result.emotional_intensity}, "
              f"rasa={result.rasa} ({latency_ms:.0f}ms)")
        return result

    except requests.exceptions.Timeout:
        print(f"⚠️ Jev timeout (>{JEV_TIMEOUT}s) — falling back to Python")
        _stats["failures"] += 1
        return None
    except Exception as e:
        print(f"⚠️ Jev error: {e} — falling back to Python")
        _stats["failures"] += 1
        return None
