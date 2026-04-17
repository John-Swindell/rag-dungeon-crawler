from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Rect(BaseModel):
    position: list[int]
    size: list[int]


class Room(BaseModel):
    name: str
    connections: dict[str, str]  # direction -> room_name // for now
    item: str | None = None
    room_info: Rect

class Map(BaseModel):
    """
    Needs to contain the information about the dungeon that was generated.
    i.e., Positions, sizes, connections(?)

    Connections can be stored in the Room object, or within the Map as a whole,
    depending on how I want to structure this.

    Since the BSP graph will be a tree in the end, it does make sense for each node to know each child node.
    """
    # TODO research this

class GameState(BaseModel):
    session_id: str
    character: str
    current_room: str
    inventory: list[str] = Field(default_factory=list)
    rooms: dict[str, Room]
    status: Literal["playing", "won", "lost"] = "playing"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
