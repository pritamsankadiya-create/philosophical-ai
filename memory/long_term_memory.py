# ============================================================
# memory/long_term_memory.py
# v3: ACTIVE memory — not just collected, but used.
#     Returns depth boost and context hints for returning users.
# ============================================================

import os
import json
from collections import Counter
from datetime import datetime

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MEMORY_PATH = os.path.join(_BASE_DIR, "memory", "long_term.json")

# How many times a concept must appear before depth boost kicks in
DEPTH_BOOST_THRESHOLD = 3
DEPTH_BOOST_AMOUNT = 0.15   # add to depth_score when user is a "regular" on a topic
MAX_DEPTH_BOOST = 0.25


class LongTermMemory:
    """
    v3: Active persistent memory.
    Now RETURNS signals that the pipeline actually uses to adapt responses:
    - depth_boost: increase depth_score for familiar concepts
    - context_hint: pass known user patterns into the prompt
    """

    def __init__(self, path: str = None):
        self.path = path or DEFAULT_MEMORY_PATH
        self.concept_counts = Counter()
        self.theme_counts = Counter()
        self.philosopher_counts = Counter()
        self.intent_counts = Counter()
        self.paradox_log = []
        self.insight_patterns = []
        self.session_count = 0
        self.total_questions = 0
        self.first_active = None
        self.last_active = None
        self.concept_connections = {}
        self._load()

    # ─── Persistence ────────────────────────────────────────────

    def _load(self):
        if not os.path.exists(self.path):
            print("Long-term memory: Starting fresh")
            self.first_active = datetime.now().isoformat()
            self._save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.concept_counts = Counter(data.get("concept_counts", {}))
            self.theme_counts = Counter(data.get("theme_counts", {}))
            self.philosopher_counts = Counter(data.get("philosopher_counts", {}))
            self.intent_counts = Counter(data.get("intent_counts", {}))
            self.paradox_log = data.get("paradox_log", [])
            self.insight_patterns = data.get("insight_patterns", [])
            self.session_count = data.get("session_count", 0)
            self.total_questions = data.get("total_questions", 0)
            self.first_active = data.get("first_active")
            self.last_active = data.get("last_active")
            self.concept_connections = data.get("concept_connections", {})

            print(f"Long-term memory loaded: {self.total_questions} questions, "
                  f"{len(self.concept_counts)} concepts tracked")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Long-term memory: corrupt file, starting fresh ({e})")
            self.first_active = datetime.now().isoformat()
            self._save()

    def _save(self):
        self.last_active = datetime.now().isoformat()
        data = {
            "concept_counts": dict(self.concept_counts),
            "theme_counts": dict(self.theme_counts),
            "philosopher_counts": dict(self.philosopher_counts),
            "intent_counts": dict(self.intent_counts),
            "paradox_log": self.paradox_log[-200:],
            "insight_patterns": self.insight_patterns[-200:],
            "session_count": self.session_count,
            "total_questions": self.total_questions,
            "first_active": self.first_active,
            "last_active": self.last_active,
            "concept_connections": self.concept_connections,
        }
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ─── v3: Active memory — returns signals for pipeline ───────

    def get_depth_boost(self, concepts: list) -> float:
        """
        v3: Return a depth boost if the user has explored these concepts before.
        Used in pipeline to increase depth_score for returning explorers.
        """
        if not concepts:
            return 0.0

        boost = 0.0
        for concept in concepts:
            count = self.concept_counts.get(concept, 0)
            if count >= DEPTH_BOOST_THRESHOLD:
                # Logarithmic scaling: more visits = more boost, but diminishing returns
                concept_boost = min(DEPTH_BOOST_AMOUNT * (count / DEPTH_BOOST_THRESHOLD), DEPTH_BOOST_AMOUNT)
                boost += concept_boost

        return min(boost, MAX_DEPTH_BOOST)

    def get_context_hint(self, concepts: list, language: str = "english") -> str:
        """
        v3: Return a context hint for the prompt when user has history.
        Tells the LLM: "this user has explored X before, go deeper by default."
        """
        if not concepts or self.total_questions < 3:
            return ""

        familiar = [c for c in concepts if self.concept_counts.get(c, 0) >= DEPTH_BOOST_THRESHOLD]
        if not familiar:
            return ""

        top_themes = [t for t, _ in self.theme_counts.most_common(3)]

        if language == "hindi":
            if familiar:
                familiar_str = ", ".join(familiar[:3])
                return f"[यह उपयोगकर्ता पहले {familiar_str} पर गहराई से सोच चुका है — सामान्य परिचय मत दो, सीधे गहराई में जाओ।]"
        else:
            if familiar:
                familiar_str = ", ".join(familiar[:3])
                hint = f"[This person has explored {familiar_str} before — skip the basics, go deeper immediately.]"
                if top_themes:
                    themes_str = ", ".join(top_themes[:2])
                    hint += f" [Their dominant philosophical interests: {themes_str}.]"
                return hint

        return ""

    def get_returning_user_note(self, language: str = "english") -> str:
        """Return a note if this is a returning user with significant history."""
        if self.total_questions < 5:
            return ""
        if language == "hindi":
            return f"[यह उपयोगकर्ता {self.total_questions} प्रश्न पूछ चुका है — परिचय की ज़रूरत नहीं, सीधे depth में जाओ।]"
        return f"[Returning explorer — {self.total_questions} questions asked. No need for basics.]"

    # ─── Learning from each question ───────────────────────────

    def learn_from_question(self, analysis, trace=None):
        self.total_questions += 1

        if hasattr(analysis, "concepts"):
            for c in analysis.concepts:
                self.concept_counts[c] += 1
            if len(analysis.concepts) >= 2:
                self._track_connections(analysis.concepts)

        if hasattr(analysis, "themes"):
            for t in analysis.themes:
                self.theme_counts[t] += 1

        if hasattr(analysis, "philosophers"):
            for p in analysis.philosophers:
                self.philosopher_counts[p] += 1

        if hasattr(analysis, "intent"):
            self.intent_counts[analysis.intent] += 1

        if hasattr(analysis, "is_paradox") and analysis.is_paradox:
            self.paradox_log.append({
                "concepts": getattr(analysis, "concepts", []),
                "type": getattr(analysis, "paradox_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            })

        if trace and hasattr(trace, "insight_type"):
            self.insight_patterns.append({
                "concepts": getattr(analysis, "concepts", []),
                "insight_type": trace.insight_type,
                "uncertainty": getattr(trace, "uncertainty_status", "unknown"),
                "depth": getattr(analysis, "depth_score", 0),
                "timestamp": datetime.now().isoformat()
            })

        self._save()

    def _track_connections(self, concepts: list):
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                key = tuple(sorted([c1, c2]))
                key_str = f"{key[0]}+{key[1]}"
                self.concept_connections[key_str] = \
                    self.concept_connections.get(key_str, 0) + 1

    def increment_session(self):
        self.session_count += 1
        self._save()

    # ─── Querying ───────────────────────────────────────────────

    def get_dominant_concepts(self, top_n: int = 10) -> list:
        return self.concept_counts.most_common(top_n)

    def get_dominant_themes(self, top_n: int = 5) -> list:
        return self.theme_counts.most_common(top_n)

    def get_strongest_connections(self, top_n: int = 10) -> list:
        return sorted(self.concept_connections.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_concept_context(self, concept: str) -> dict:
        connections = {k: v for k, v in self.concept_connections.items() if concept in k}
        related_paradoxes = [p for p in self.paradox_log if concept in p.get("concepts", [])]
        return {
            "frequency": self.concept_counts.get(concept, 0),
            "connections": connections,
            "paradoxes": related_paradoxes[-5:],
        }

    def get_summary(self) -> dict:
        days_active = 0
        if self.first_active:
            try:
                first = datetime.fromisoformat(self.first_active)
                days_active = (datetime.now() - first).days
            except (ValueError, TypeError):
                pass

        return {
            "days_active": days_active,
            "total_sessions": self.session_count,
            "total_questions": self.total_questions,
            "first_active": self.first_active,
            "last_active": self.last_active,
            "top_concepts": self.get_dominant_concepts(10),
            "top_themes": self.get_dominant_themes(5),
            "top_connections": self.get_strongest_connections(10),
            "top_philosophers": self.philosopher_counts.most_common(5),
            "intent_distribution": dict(self.intent_counts),
            "paradoxes_encountered": len(self.paradox_log),
            "insight_patterns_stored": len(self.insight_patterns),
        }

    def reset(self):
        self.concept_counts = Counter()
        self.theme_counts = Counter()
        self.philosopher_counts = Counter()
        self.intent_counts = Counter()
        self.paradox_log = []
        self.insight_patterns = []
        self.session_count = 0
        self.total_questions = 0
        self.first_active = datetime.now().isoformat()
        self.last_active = None
        self.concept_connections = {}
        self._save()
        print("Long-term memory RESET — all learning erased")