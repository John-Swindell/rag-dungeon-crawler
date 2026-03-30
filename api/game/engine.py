from __future__ import annotations

import uuid
from datetime import datetime, timezone

from api.game.world import BOSS_ROOM, START_ROOM, TOTAL_ITEMS, build_rooms
from api.models.game_state import GameState


def new_game() -> GameState:
    """Create a new game session."""
    return GameState(
        session_id=str(uuid.uuid4()),
        current_room=START_ROOM,
        inventory=[],
        rooms=build_rooms(),
        status="playing",
    )


def move(state: GameState, direction: str) -> tuple[GameState, str]:
    """Move the player in a direction."""
    if state.status != "playing":
        return state, "Game is already over."

    direction = direction.capitalize()
    room = state.rooms[state.current_room]

    if direction not in room.connections:
        return state, f"You cannot go {direction} from {state.current_room}."

    new_room_name = room.connections[direction]
    state = state.model_copy(
        update={
            "current_room": new_room_name,
            "updated_at": datetime.now(timezone.utc),
        }
    )

    # check end condition
    state, end_msg = _check_end_condition(state)
    if end_msg:
        return state, end_msg

    return state, f"You moved {direction} to {new_room_name}."


def pickup(state: GameState) -> tuple[GameState, str]:
    """Pick up the item in the current room."""
    if state.status != "playing":
        return state, "Game is already over."

    room = state.rooms[state.current_room]

    if room.item is None:
        return state, "There is nothing to pick up here."

    if room.item in state.inventory:
        return state, "You already have this item."

    item_name = room.item
    new_inventory = [*state.inventory, item_name]

    # clear item from the room
    new_rooms = {
        name: r.model_copy(update={"item": None}) if name == state.current_room else r
        for name, r in state.rooms.items()
    }

    state = state.model_copy(
        update={
            "inventory": new_inventory,
            "rooms": new_rooms,
            "updated_at": datetime.now(timezone.utc),
        }
    )

    return state, f"{item_name} added to inventory."


def _check_end_condition(state: GameState) -> tuple[GameState, str]:
    """Check win/lose on entering the boss room."""
    if state.current_room != BOSS_ROOM:
        return state, ""

    if len(state.inventory) >= TOTAL_ITEMS:
        state = state.model_copy(update={"status": "won"})
        return state, "Congratulations! You collected all items and escaped!"
    else:
        state = state.model_copy(update={"status": "lost"})
        return state, "Warden Roy caught you! Game over!"
