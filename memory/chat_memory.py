# ============================================================
# memory/chat_memory.py
# Conversation memory with conversation theme tracking
# ============================================================

import os
import sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ChatMemory:
    """
    Stores conversation history and tracks conversation themes.

    Theme tracking: counts concept frequency across turns.
    If user keeps asking about "consciousness" → it becomes a
    dominant theme, influencing future responses.
    """

    def __init__(self, max_history: int = 5):
        self.history = []
        self.max_history = max_history
        self.concept_counts = Counter()  # lifetime concept frequency
        self.turn_concepts = []          # concepts per turn (for recency)

    def add_message(self, role: str, content: str, concepts: list = None):
        """
        Add a message to memory with optional concept metadata.
        """
        self.history.append({
            "role": role,
            "content": content
        })

        # Track concepts for user messages
        if role == "user" and concepts:
            self.turn_concepts.append(concepts)
            for c in concepts:
                self.concept_counts[c] += 1

            # Keep turn tracker in sync with history size
            if len(self.turn_concepts) > self.max_history:
                self.turn_concepts = self.turn_concepts[-self.max_history:]

        # Keep only last N conversations
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def get_history_as_text(self) -> str:
        if not self.history:
            return "No previous conversation."

        text = "Previous Conversation:\n"
        for message in self.history:
            if message["role"] == "user":
                text += f"User: {message['content']}\n"
            else:
                text += f"AI: {message['content']}\n"

        return text

    def get_recent_concepts(self, n: int = 3) -> list:
        """Get unique concepts from the last n turns."""
        recent = self.turn_concepts[-n:]
        seen = set()
        result = []
        for concepts in recent:
            for c in concepts:
                if c not in seen:
                    seen.add(c)
                    result.append(c)
        return result

    def get_dominant_themes(self, min_count: int = 2, top_n: int = 3) -> list:
        """
        Get conversation themes — concepts the user keeps returning to.

        Example: user asked about consciousness 3 times, mind 2 times
        → returns ["consciousness", "mind"]

        Only returns concepts mentioned min_count or more times.
        """
        themes = [
            (concept, count)
            for concept, count in self.concept_counts.most_common(top_n)
            if count >= min_count
        ]
        return [concept for concept, count in themes]

    def get_theme_summary(self) -> dict:
        """Debug: full view of conversation themes."""
        return {
            "dominant_themes": self.get_dominant_themes(),
            "recent_concepts": self.get_recent_concepts(),
            "all_concept_counts": dict(self.concept_counts.most_common(10)),
            "total_turns": len(self.turn_concepts),
        }

    def clear(self):
        self.history = []
        self.turn_concepts = []
        self.concept_counts.clear()
        print("Memory cleared!")

    def is_empty(self) -> bool:
        return len(self.history) == 0
