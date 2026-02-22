"""
Session management for multi-turn conversation memory.
Manages chat history, context window, and session metadata.
"""

from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Message:
    role: str          # "user" or "model"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    token_count: Optional[int] = None


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: list[Message] = field(default_factory=list)
    total_tokens_used: int = 0


def create_session() -> Session:
    """Initialize a new conversation session."""
    return Session()


def add_message(session: Session, role: str, content: str, tokens: int = 0) -> None:
    """Append a message to the session history."""
    session.messages.append(Message(role=role, content=content))
    session.total_tokens_used += tokens


def get_history_for_api(session: Session, max_turns: int = 20) -> list[dict]:
    """
    Convert session messages to Gemini API format.
    Returns the last `max_turns` exchanges (user+model pairs).
    """
    messages = session.messages[-(max_turns * 2):]
    return [{"role": msg.role, "parts": [{"text": msg.content}]} for msg in messages]


def get_message_count(session: Session) -> int:
    return len(session.messages)


def clear_session(session: Session) -> None:
    """Reset conversation history while preserving session metadata."""
    session.messages.clear()
    session.total_tokens_used = 0
