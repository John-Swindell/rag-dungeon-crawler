from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional

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

    room_name: Optional[str] = None

    # Helper method
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


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
    map_seed: int
    map_size: list[int] = Field(default_factory=lambda: [800, 800])
    visited_rooms: list[str] = Field(default_factory=list)
    warden_room: str = "Wardens Office"
    warden_active: bool = False
    warden_path: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    narrative_context: str = ""
    turn_count: int = 0
    status: Literal["playing", "won", "lost"] = "playing"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

