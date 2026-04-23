from api.game import engine
from api.game.pathfinding import a_star
from api.game.world import ITEMS, ROOF_ROOM, START_ROOM, WARDEN_ROOM


def _direction_to(state, source: str, target: str) -> str:
    for direction, destination in state.rooms[source].connections.items():
        if destination == target:
            return direction
    raise AssertionError(f"No direct exit from {source} to {target}")


def _move_along_path(state, path: list[str]):
    message = ""
    for source, target in zip(path, path[1:], strict=False):
        direction = _direction_to(state, source, target)
        state, message = engine.move(state, direction)
    return state, message


def test_new_game_starts_in_cell():
    state = engine.new_game("Sal", map_seed=101)
    assert state.current_room == START_ROOM
    assert state.character == "Sal"
    assert state.inventory == []
    assert state.status == "playing"
    assert state.map_seed == 101
    assert state.visited_rooms == [START_ROOM]


def test_valid_move():
    state = engine.new_game("Weasel", map_seed=102)
    direction, destination = next(iter(state.rooms[state.current_room].connections.items()))

    state, msg = engine.move(state, direction)

    assert state.current_room == destination
    assert destination in msg


def test_invalid_move():
    state = engine.new_game("Billy", map_seed=103)
    state, msg = engine.move(state, "upstairs")
    assert state.current_room == START_ROOM
    assert "cannot" in msg.lower()


def test_pickup_item():
    state = engine.new_game("Finn", map_seed=104)
    item_room = next(room.name for room in state.rooms.values() if room.item is not None)
    path = a_star(state.rooms, state.current_room, item_room)

    state, _ = _move_along_path(state, path)
    state, msg = engine.pickup(state)

    assert "added to inventory" in msg
    assert len(state.inventory) == 1
    assert state.rooms[item_room].item is None


def test_pickup_empty_room():
    state = engine.new_game("Weasel", map_seed=105)
    state, msg = engine.pickup(state)
    assert "nothing" in msg.lower()


def test_entering_warden_room_loses():
    state = engine.new_game("Sal", map_seed=106)
    path = a_star(state.rooms, state.current_room, WARDEN_ROOM)

    state, msg = _move_along_path(state, path)

    assert state.status == "lost"
    assert state.current_room == WARDEN_ROOM
    assert "brutus" in msg.lower()


def test_warden_activates_after_fifth_item():
    state = engine.new_game("Weasel", map_seed=107)
    item_room = next(room.name for room in state.rooms.values() if room.item is not None)
    state = state.model_copy(
        update={
            "current_room": item_room,
            "inventory": [f"test-part-{index}" for index in range(engine.WARDEN_RELEASE_ITEM_COUNT - 1)],
        }
    )

    state, _ = engine.pickup(state)

    assert state.warden_active is True
    assert state.warden_room != WARDEN_ROOM
    assert any("Brutus" in hint for hint in state.hints)


def test_win_condition_requires_roof_and_all_items():
    state = engine.new_game("Weasel", map_seed=108)
    roof_neighbor = next(iter(state.rooms[ROOF_ROOM].connections.values()))
    direction_to_roof = _direction_to(state, roof_neighbor, ROOF_ROOM)
    state = state.model_copy(
        update={
            "current_room": roof_neighbor,
            "inventory": ITEMS,
            "visited_rooms": [START_ROOM, roof_neighbor],
        }
    )

    state, msg = engine.move(state, direction_to_roof)

    assert state.status == "won"
    assert "roof" in msg.lower()
