from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class NewGameRequest(BaseModel):
    character: Literal["Weasel", "Sal", "Billy", "Finn"]


class MoveRequest(BaseModel):
    direction: str


class MapRoom(BaseModel):
    name: str
    position: list[int]
    size: list[int]
    connections: dict[str, str]
    item: str | None = None


class GameResponse(BaseModel):
    session_id: str
    character: str
    message: str
    current_room: str
    inventory: list[str]
    status: str
    available_directions: list[str]
    room_item: str | None = None
    map_seed: int
    map_size: list[int]
    map_rooms: list[MapRoom]
    visited_rooms: list[str]
    warden_room: str
    warden_active: bool
    warden_path: list[str]
    hints: list[str]
    narrative_context: str
