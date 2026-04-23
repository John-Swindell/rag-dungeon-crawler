from __future__ import annotations

from pymongo.errors import PyMongoError

from api.config import settings
from api.db import disable_db, get_db
from api.models.game_state import GameState


async def save_context(
    state: GameState,
    event: str,
    message: str,
    text: str,
    embedding: list[float] | None = None,
) -> None:
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
        "text": text,
        "inventory": state.inventory,
        "inventory_count": len(state.inventory),
        "status": state.status,
        "player_position": state.current_room,
        "warden_position": state.warden_room,
        "warden_active": state.warden_active,
        "timestamp": state.updated_at.isoformat(),
    }
    if embedding is not None:
        doc["embedding"] = embedding
    try:
        await db.context.insert_one(doc)
    except PyMongoError:
        disable_db()


async def get_context(
    session_id: str,
    limit: int = 10,
    query_embedding: list[float] | None = None,
) -> list[dict]:
    """Retrieve recent context for a session."""
    db = get_db()
    if db is None:
        return []

    if settings.enable_vector_search and query_embedding is not None:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": settings.mongo_vector_index,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(limit * 8, 24),
                    "limit": limit,
                    "filter": {"session_id": {"$eq": session_id}},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "embedding": 0,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        try:
            cursor = db.context.aggregate(pipeline)
            return await cursor.to_list(length=limit)
        except PyMongoError:
            pass

    cursor = db.context.find(
        {"session_id": session_id},
        {"_id": 0, "embedding": 0},
    ).sort("timestamp", -1).limit(limit)

    try:
        return await cursor.to_list(length=limit)
    except PyMongoError:
        disable_db()
        return []
