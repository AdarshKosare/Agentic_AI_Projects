import json
import os
from datetime import datetime
from config import settings


MEMORY_FILE = "conversation_memory.json"


def _load_memory() -> list[dict]:
    """Load all past sessions from disk."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(sessions: list[dict]) -> None:
    """Save all sessions to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)


def save_session(topic: str, report: str) -> None:
    """
    Save a completed research session to memory.
    Called at the end of every agent run.
    """
    sessions = _load_memory()
    sessions.append({
        "topic": topic,
        "report": report,
        "timestamp": datetime.now().isoformat(),
    })
    _save_memory(sessions)


def get_context_for_query(query: str, max_sessions: int = 3) -> str:
    """
    Return past sessions relevant to the current query.
    Injected into the agent's context window before each run.
    """
    sessions = _load_memory()

    if not sessions:
        return ""

    # Most recent sessions first
    recent = sessions[-max_sessions:]

    context_parts = ["Previous research sessions:"]
    for s in recent:
        context_parts.append(
            f"\n[{s['timestamp'][:10]}] Topic: {s['topic']}\n"
            f"Summary: {s['report'][:300]}..."
        )

    return "\n".join(context_parts)


def get_all_topics() -> list[str]:
    """Return list of all researched topics."""
    sessions = _load_memory()
    return [s["topic"] for s in sessions]


def clear_memory() -> None:
    """Clear all saved sessions."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)