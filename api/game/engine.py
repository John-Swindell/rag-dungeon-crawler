from __future__ import annotations

import secrets
from datetime import datetime, timezone

from api.game.pathfinding import a_star
from api.game.world import ROOF_ROOM, START_ROOM, TOTAL_ITEMS, WARDEN_ROOM, build_rooms
from api.models.game_state import GameState, Room

WARDEN_RELEASE_ITEM_COUNT = 8


def _now():
    return datetime.now(timezone.utc)


def _touch(state: GameState, **updates) -> GameState:
    return state.model_copy(update={**updates, "updated_at": _now()})


def new_game(character: str, map_seed: int | None = None) -> GameState:
    """Create a new game session with a unique procedural map."""
    seed = map_seed if map_seed is not None else secrets.randbits(32)
    rooms = build_rooms(seed)

    return GameState(
        session_id=secrets.token_urlsafe(24),
        character=character,
        current_room=START_ROOM,
        inventory=[],
        rooms=rooms,
        map_seed=seed,
        map_size=[800, 800],
        visited_rooms=[START_ROOM],
        warden_room=WARDEN_ROOM,
        status="playing",
        hints=[
            "Collect all 8 Icarus parts, then reach the Roof.",
            "Brutus starts in the Warden's Office. Do not enter it.",
        ],
    )


def move(state: GameState, direction: str) -> tuple[GameState, str]:
    """Move the player in a direction and resolve the Warden turn."""
    if state.status != "playing":
        return state, "Game is already over."

    direction = direction.capitalize()
    room = state.rooms[state.current_room]

    if direction not in room.connections:
        return _touch(state, hints=[f"No passage leads {direction} from {state.current_room}."]), (
            f"You cannot go {direction} from {state.current_room}."
        )

    new_room_name = room.connections[direction]
    visited_rooms = _append_unique(state.visited_rooms, new_room_name)
    state = _touch(
        state,
        current_room=new_room_name,
        visited_rooms=visited_rooms,
        turn_count=state.turn_count + 1,
        hints=[],
    )

    state, turn_hint = _resolve_turn(state)
    if state.status == "won":
        return state, "You assembled the Icarus and reached the Roof. Alcatraz falls away beneath you."
    if state.status == "lost":
        return state, "Brutus caught you before the Icarus could fly."

    message = f"You moved {direction} to {new_room_name}."
    if turn_hint:
        message = f"{message} {turn_hint}"
    return state, message


def pickup(state: GameState) -> tuple[GameState, str]:
    """Pick up the item in the current room and resolve the Warden turn."""
    if state.status != "playing":
        return state, "Game is already over."

    room = state.rooms[state.current_room]

    if room.item is None:
        return _touch(state, hints=["There is nothing useful here. Keep moving."]), "There is nothing to pick up here."

    if room.item in state.inventory:
        return _touch(state, hints=["You already scavenged this room."]), "You already have this item."

    item_name = room.item
    new_inventory = [*state.inventory, item_name]
    new_rooms = {
        name: _clear_item(r) if name == state.current_room else r
        for name, r in state.rooms.items()
    }

    state = _touch(
        state,
        inventory=new_inventory,
        rooms=new_rooms,
        turn_count=state.turn_count + 1,
        hints=[],
    )

    state, turn_hint = _resolve_turn(state)
    if state.status == "won":
        return state, f"{item_name} added to inventory. The Icarus is complete, and the Roof is yours."
    if state.status == "lost":
        return state, f"{item_name} added to inventory, but Brutus caught you before you could escape."

    message = f"{item_name} added to inventory."
    if turn_hint:
        message = f"{message} {turn_hint}"
    return state, message


def _clear_item(room: Room) -> Room:
    return room.model_copy(update={"item": None})


def _append_unique(values: list[str], value: str) -> list[str]:
    if value in values:
        return values
    return [*values, value]


def _resolve_turn(state: GameState) -> tuple[GameState, str]:
    """Resolve win/catch/release/chase after a successful player action."""
    hints: list[str] = []

    state = _check_escape_condition(state)
    if state.status == "won":
        return _touch(state, hints=["All parts are secured. You launch from the Roof before Brutus can reach you."]), ""

    state = _check_warden_collision(state)
    if state.status == "lost":
        return _touch(state, hints=["Brutus is in the room. The escape is over."]), ""

    if not state.warden_active and len(state.inventory) >= WARDEN_RELEASE_ITEM_COUNT:
        state = _touch(state, warden_active=True)
        hints.append("Brutus has left the Warden's Office and is now hunting you.")

    if not state.warden_active:
        missing = TOTAL_ITEMS - len(state.inventory)
        hints.append(f"Find {missing} more Icarus part{'s' if missing != 1 else ''}. Brutus is still in his office.")
        return _touch(state, hints=hints), ""

    path_to_player = a_star(state.rooms, state.warden_room, state.current_room)
    if not path_to_player:
        hints.append("The corridors confuse Brutus for now, but do not count on it.")
        return _touch(state, hints=hints, warden_path=[]), ""

    next_warden_room = path_to_player[1] if len(path_to_player) > 1 else state.current_room
    state = _touch(state, warden_room=next_warden_room)
    state = _check_warden_collision(state)

    if state.status == "lost":
        return _touch(state, hints=[*hints, "Brutus took the fastest route and caught you."]), ""

    updated_path = a_star(state.rooms, state.warden_room, state.current_room)
    distance = max(len(updated_path) - 1, 0)
    hints.append(f"Brutus moves into {state.warden_room}. He is {distance} room{'s' if distance != 1 else ''} away.")
    return _touch(state, hints=hints, warden_path=updated_path), hints[-1]


def _check_escape_condition(state: GameState) -> GameState:
    if state.current_room == ROOF_ROOM and len(state.inventory) >= TOTAL_ITEMS:
        return _touch(state, status="won")
    return state


def _check_warden_collision(state: GameState) -> GameState:
    if state.current_room == state.warden_room:
        return _touch(state, status="lost")
    return state
