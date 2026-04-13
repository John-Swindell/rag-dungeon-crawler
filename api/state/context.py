from __future__ import annotations

from api.db import get_db
from api.models.game_state import GameState


async def save_context(state: GameState, event: str, message: str) -> None:
    """Store a game event snapshot for RAG retrieval."""
    db = get_db()
    if db is None:
        return

    doc = {
        "session_id": state.session_id,
        "character": state.character,
        "room": state.current_room,
        "event": event,
        "message": message,
        "inventory": state.inventory,
        "inventory_count": len(state.inventory),
        "status": state.status,
        "timestamp": state.updated_at.isoformat(),
    }
    await db.context.insert_one(doc)


async def get_context(session_id: str, limit: int = 10) -> list[dict]:
    """Retrieve recent context for a session."""
    db = get_db()
    if db is None:
        return []

    cursor = db.context.find(
        {"session_id": session_id},
        {"_id": 0},
    ).sort("timestamp", -1).limit(limit)

    return await cursor.to_list(length=limit)
