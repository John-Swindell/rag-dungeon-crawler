from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Room(BaseModel):
    name: str
    connections: dict[str, str]  # direction -> room_name
    item: str | None = None


class GameState(BaseModel):
    session_id: str
    current_room: str
    inventory: list[str] = Field(default_factory=list)
    rooms: dict[str, Room]
    status: Literal["playing", "won", "lost"] = "playing"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
