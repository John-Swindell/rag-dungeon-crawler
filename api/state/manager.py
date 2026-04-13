from __future__ import annotations

from api.db import get_db
from api.models.game_state import GameState

_sessions: dict[str, GameState] = {}


async def save(state: GameState) -> None:
    db = get_db()
    if db is not None:
        await db.sessions.replace_one(
            {"session_id": state.session_id},
            state.model_dump(mode="json"),
            upsert=True,
        )
    else:
        _sessions[state.session_id] = state


async def load(session_id: str) -> GameState | None:
    db = get_db()
    if db is not None:
        doc = await db.sessions.find_one({"session_id": session_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return GameState.model_validate(doc)
    return _sessions.get(session_id)


async def delete(session_id: str) -> bool:
    db = get_db()
    if db is not None:
        result = await db.sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    return _sessions.pop(session_id, None) is not None
