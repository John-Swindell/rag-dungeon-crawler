from __future__ import annotations

from pydantic import BaseModel


class MoveRequest(BaseModel):
    direction: str


class GameResponse(BaseModel):
    session_id: str
    message: str
    current_room: str
    inventory: list[str]
    status: str
    available_directions: list[str]
    room_item: str | None = None
