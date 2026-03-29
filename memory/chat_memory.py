# ============================================================
# memory/chat_memory.py
# SHORT-TERM conversation memory only
# Long-term learning is handled by long_term_memory.py
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ChatMemory:
    """
    Short-term conversation memory — stores recent chat history.
    v3: Also stores conversation context (problem_type, emotional_state, topic)
    for smarter follow-up responses.

    This is safe to clear between conversations.
    Long-term concept tracking and learning lives in LongTermMemory.
    """

    def __init__(self, max_history: int = 5):
        self.history = []
        self.max_history = max_history
        # v3: Conversation context for follow-ups
        self.context = {
            "problem_type": "",       # emotional, factual, philosophical, etc.
            "emotional_state": "",    # what the user is feeling
            "emotional_intensity": "",  # low, medium, high
            "topic": "",              # last discussed topic/concepts
            "goal": "",               # what the user wants to achieve
        }

    def add_message(self, role: str, content: str):
        """Add a message to short-term history."""
        self.history.append({
            "role": role,
            "content": content
        })

        # Keep only last N conversation pairs
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def update_context(self, question_type: str = "", concepts: list = None,
                       emotional_intensity: str = "", question: str = ""):
        """v3: Update conversation context from latest analysis."""
        if question_type:
            self.context["problem_type"] = question_type
        if concepts:
            self.context["topic"] = ", ".join(concepts[:3])
        if emotional_intensity:
            self.context["emotional_intensity"] = emotional_intensity
        # Extract emotional state from question
        if question:
            lower = question.lower()
            emotional_states = {
                "lost": "feeling lost", "empty": "feeling empty",
                "stuck": "feeling stuck", "confused": "feeling confused",
                "sad": "feeling sad", "anxious": "feeling anxious",
                "lonely": "feeling lonely", "scared": "feeling scared",
                "angry": "feeling angry", "tired": "feeling tired",
                "bored": "feeling bored", "useless": "feeling useless",
                "worthless": "feeling worthless", "hopeless": "feeling hopeless",
                "attached": "struggling with attachment",
                "wasting": "feeling like wasting life",
                "failed": "dealing with failure",
            }
            for keyword, state in emotional_states.items():
                if keyword in lower:
                    self.context["emotional_state"] = state
                    break

    def get_context_summary(self) -> str:
        """v3: Get conversation context as text for follow-up prompts."""
        parts = []
        if self.context["problem_type"]:
            parts.append(f"Previous question type: {self.context['problem_type']}")
        if self.context["emotional_state"]:
            parts.append(f"User's state: {self.context['emotional_state']}")
        if self.context["emotional_intensity"]:
            parts.append(f"Intensity: {self.context['emotional_intensity']}")
        if self.context["topic"]:
            parts.append(f"Topic: {self.context['topic']}")
        return " | ".join(parts) if parts else ""

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

    def clear(self):
        """Clear conversation history only. Long-term memory is NOT touched."""
        self.history = []
        self.context = {
            "problem_type": "", "emotional_state": "",
            "emotional_intensity": "", "topic": "", "goal": "",
        }
        print("Chat history cleared! (Long-term memory preserved)")

    def is_empty(self) -> bool:
        return len(self.history) == 0
