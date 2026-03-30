from fastapi import APIRouter, HTTPException

from api.game import engine
from api.models.actions import GameResponse, MoveRequest
from api.state import manager

router = APIRouter(prefix="/game", tags=["game"])


def _to_response(state, message: str) -> GameResponse:
    room = state.rooms[state.current_room]
    return GameResponse(
        session_id=state.session_id,
        message=message,
        current_room=state.current_room,
        inventory=state.inventory,
        status=state.status,
        available_directions=list(room.connections.keys()),
        room_item=room.item,
    )


@router.post("/new", response_model=GameResponse)
async def new_game():
    """Start a new game."""
    state = engine.new_game()
    manager.save(state)
    return _to_response(state, "Welcome to the Prison Escape! Collect all 6 items to win.")


@router.get("/{session_id}", response_model=GameResponse)
async def get_game(session_id: str):
    """Get current game state."""
    state = manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _to_response(state, f"You are in {state.current_room}.")


@router.post("/{session_id}/move", response_model=GameResponse)
async def move_player(session_id: str, payload: MoveRequest):
    """Move the player."""
    state = manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    state, message = engine.move(state, payload.direction)
    manager.save(state)
    return _to_response(state, message)


@router.post("/{session_id}/pickup", response_model=GameResponse)
async def pickup_item(session_id: str):
    """Pick up an item."""
    state = manager.load(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    state, message = engine.pickup(state)
    manager.save(state)
    return _to_response(state, message)
