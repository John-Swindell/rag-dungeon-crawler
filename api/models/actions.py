from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class NewGameRequest(BaseModel):
    character: Literal["Weasel", "Sal", "Billy", "Finn"]


class MoveRequest(BaseModel):
    direction: str


class GameResponse(BaseModel):
    session_id: str
    character: str
    message: str
    current_room: str
    inventory: list[str]
    status: str
    available_directions: list[str]
    room_item: str | None = None
