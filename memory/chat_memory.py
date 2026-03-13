# ============================================================
# 📁 memory/chat_memory.py
# 🎯 Purpose: Remember conversation history
# 🧠 Like a human memory — remembers what was said before!
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ChatMemory:
    """
    Stores conversation history so AI remembers
    previous questions and answers!

    Think of it like a notepad where every
    question and answer is written down 📝
    """

    def __init__(self, max_history: int = 5):
        """
        max_history = how many past messages to remember
        Default 5 = remembers last 5 conversations
        More history = slower but smarter
        """
        self.history = []          # stores all messages
        self.max_history = max_history

    def add_message(self, role: str, content: str):
        """
        Add a message to memory.

        Args:
            role    : "user" or "ai"
            content : the actual message text
        """
        self.history.append({
            "role": role,
            "content": content
        })

        # Keep only last N conversations
        # (so memory doesn't get too large and slow!)
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def get_history_as_text(self) -> str:
        """
        Convert memory to readable text for the AI prompt.

        Example output:
            User: What is love?
            AI: Love is a decision to commit...
            User: Tell me more
        """
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
        """Clear all memory — fresh start!"""
        self.history = []
        print("🧹 Memory cleared!")

    def is_empty(self) -> bool:
        """Check if memory is empty"""
        return len(self.history) == 0