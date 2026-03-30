from __future__ import annotations

from api.models.game_state import GameState

_sessions: dict[str, GameState] = {}


def save(state: GameState) -> None:
    _sessions[state.session_id] = state


def load(session_id: str) -> GameState | None:
    return _sessions.get(session_id)


def delete(session_id: str) -> bool:
    return _sessions.pop(session_id, None) is not None
