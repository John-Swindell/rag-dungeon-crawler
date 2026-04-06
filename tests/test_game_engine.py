from api.game import engine


def test_new_game_starts_in_cell():
    state = engine.new_game("Sal")
    assert state.current_room == "Cell"
    assert state.character == "Sal"
    assert state.inventory == []
    assert state.status == "playing"


def test_valid_move():
    state = engine.new_game("Weasel")
    state, msg = engine.move(state, "east")
    assert state.current_room == "Michigan Avenue"
    assert "Michigan Avenue" in msg


def test_invalid_move():
    state = engine.new_game("Billy")
    state, msg = engine.move(state, "north")
    assert state.current_room == "Cell"
    assert "cannot" in msg.lower()


def test_pickup_item():
    state = engine.new_game("Finn")
    # Cell -> Michigan Avenue -> Times Square -> Library (has control valves)
    state, _ = engine.move(state, "east")
    state, _ = engine.move(state, "north")
    state, _ = engine.move(state, "east")
    state, msg = engine.pickup(state)
    assert "control valves" in msg
    assert "control valves" in state.inventory
    assert state.rooms["Library"].item is None


def test_pickup_empty_room():
    state = engine.new_game("Weasel")
    state, msg = engine.pickup(state)
    assert "nothing" in msg.lower()


def test_lose_condition():
    state = engine.new_game("Sal")
    # Rush to boss: Cell -> Michigan Ave -> Times Square -> Citadel Tunnels -> Wardens Office
    state, _ = engine.move(state, "east")
    state, _ = engine.move(state, "north")
    state, _ = engine.move(state, "north")
    state, msg = engine.move(state, "east")
    assert state.status == "lost"
    assert state.current_room == "Wardens Office"
    assert "brutus" in msg.lower()


def test_win_condition():
    state = engine.new_game("Weasel")

    # Collect all 8 Icarus parts
    state, _ = engine.move(state, "east")       # -> Michigan Avenue
    state, _ = engine.move(state, "south")       # -> Broadway
    state, _ = engine.move(state, "east")        # -> Laundry Room
    state, _ = engine.pickup(state)              # rigging

    state, _ = engine.move(state, "west")        # -> Broadway
    state, _ = engine.move(state, "south")       # -> Cafeteria
    state, _ = engine.move(state, "east")        # -> Kitchen
    state, _ = engine.pickup(state)              # fuel tank

    state, _ = engine.move(state, "west")        # -> Cafeteria
    state, _ = engine.move(state, "south")       # -> Recreation Yard
    state, _ = engine.move(state, "east")        # -> Guard Tower
    state, _ = engine.pickup(state)              # wiring kit

    state, _ = engine.move(state, "west")        # -> Recreation Yard
    state, _ = engine.move(state, "south")       # -> Docks
    state, _ = engine.pickup(state)              # engine

    state, _ = engine.move(state, "east")        # -> Building 64
    state, _ = engine.pickup(state)              # flight gear

    state, _ = engine.move(state, "north")       # -> Gondola Station
    state, _ = engine.move(state, "north")       # -> Roof
    state, _ = engine.pickup(state)              # propeller

    state, _ = engine.move(state, "west")        # -> Spiral Staircase
    state, _ = engine.move(state, "south")       # -> Citadel Tunnels
    state, _ = engine.move(state, "south")       # -> Times Square
    state, _ = engine.move(state, "east")        # -> Library
    state, _ = engine.pickup(state)              # control valves

    state, _ = engine.move(state, "west")        # -> Times Square
    state, _ = engine.move(state, "west")        # -> Infirmary
    state, _ = engine.pickup(state)              # navigation tools

    assert len(state.inventory) == 8

    state, msg = engine.move(state, "north")     # -> Wardens Office
    assert state.status == "won"
    assert "escaped" in msg.lower()
