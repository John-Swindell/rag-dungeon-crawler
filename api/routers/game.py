from fastapi import APIRouter, HTTPException

from api.game import engine
from api.game.narrative import update_narrative_context
from api.models.actions import GameResponse, MapRoom, MoveRequest, NewGameRequest
from api.state import manager

router = APIRouter(prefix="/game", tags=["game"])


def _to_response(state, message: str) -> GameResponse:
    room = state.rooms[state.current_room]
    return GameResponse(
        session_id=state.session_id,
        character=state.character,
        message=message,
        current_room=state.current_room,
        inventory=state.inventory,
        status=state.status,
        available_directions=list(room.connections.keys()),
        room_item=room.item,
        map_seed=state.map_seed,
        map_size=state.map_size,
        map_rooms=[
            MapRoom(
                name=map_room.name,
                position=map_room.room_info.position,
                size=map_room.room_info.size,
                connections=map_room.connections,
                item=map_room.item,
            )
            for map_room in state.rooms.values()
        ],
        visited_rooms=state.visited_rooms,
        warden_room=state.warden_room,
        warden_active=state.warden_active,
        warden_path=state.warden_path,
        hints=state.hints,
        narrative_context=state.narrative_context,
    )


@router.post("/new", response_model=GameResponse)
async def new_game(payload: NewGameRequest):
    """Start a new game."""
    state = engine.new_game(payload.character)
    message = (
        f"{payload.character} wakes up in a cold cell on Alcatraz. "
        f"Collect all 8 parts of the Icarus, avoid Brutus, and reach the Roof."
    )
    state = await update_narrative_context(state, "new_game", message)
    await manager.save(state)
    return _to_response(state, message)


@router.get("/{session_id}", response_model=GameResponse)
async def get_game(session_id: str):
    """Get current game state."""
    state = await manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _to_response(state, f"You are in {state.current_room}.")


@router.post("/{session_id}/move", response_model=GameResponse)
async def move_player(session_id: str, payload: MoveRequest):
    """Move the player."""
    state = await manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    state, message = engine.move(state, payload.direction)
    state = await update_narrative_context(state, "move", message)
    await manager.save(state)
    return _to_response(state, message)


@router.post("/{session_id}/pickup", response_model=GameResponse)
async def pickup_item(session_id: str):
    """Pick up an item."""
    state = await manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    state, message = engine.pickup(state)
    state = await update_narrative_context(state, "pickup", message)
    await manager.save(state)
    return _to_response(state, message)
