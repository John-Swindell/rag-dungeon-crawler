from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional
from dataclasses import dataclass

from pydantic import BaseModel, Field

class Rect(BaseModel):
    position: list[int]
    size: list[int]

@dataclass(slots=True)
class BSPNode:
    # Position + size
    x: int
    y: int
    width: int
    height: int

    # Nodes / children
    left: Optional['BSPNode'] = None
    right: Optional['BSPNode'] = None

class Room(BaseModel):
    name: str
    connections: dict[str, str]  # direction -> room_name
    item: str | None = None
    room_info: Rect

class GameState(BaseModel):
    session_id: str
    character: str
    current_room: str
    inventory: list[str] = Field(default_factory=list)
    rooms: dict[str, Room]
    status: Literal["playing", "won", "lost"] = "playing"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


