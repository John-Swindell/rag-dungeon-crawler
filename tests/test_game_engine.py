from api.game import engine


def test_new_game_starts_in_cell():
    state = engine.new_game()
    assert state.current_room == "Cell"
    assert state.inventory == []
    assert state.status == "playing"


def test_valid_move():
    state = engine.new_game()
    state, msg = engine.move(state, "east")
    assert state.current_room == "Mess hall"
    assert "Mess hall" in msg


def test_invalid_move():
    state = engine.new_game()
    state, msg = engine.move(state, "north")
    assert state.current_room == "Cell"
    assert "cannot" in msg.lower()


def test_pickup_item():
    state = engine.new_game()
    state, _ = engine.move(state, "east")  # -> Mess hall (has gas tank)
    state, msg = engine.pickup(state)
    assert "gas tank" in msg
    assert "gas tank" in state.inventory
    assert state.rooms["Mess hall"].item is None


def test_pickup_empty_room():
    state = engine.new_game()
    # Cell has no item
    state, msg = engine.pickup(state)
    assert "nothing" in msg.lower()


def test_lose_condition():
    state = engine.new_game()
    # Rush to boss room: Cell -> Mess hall -> Generator room -> Warden's office
    state, _ = engine.move(state, "east")
    state, _ = engine.move(state, "east")
    state, msg = engine.move(state, "north")
    assert state.status == "lost"
    assert state.current_room == "Warden Roys office"


def test_win_condition():
    state = engine.new_game()

    # Collect all 6 items by visiting every room
    state, _ = engine.move(state, "east")       # -> Mess hall
    state, _ = engine.pickup(state)              # gas tank

    state, _ = engine.move(state, "south")       # -> Showers
    state, _ = engine.pickup(state)              # tarp

    state, _ = engine.move(state, "east")        # -> Janitors closet
    state, _ = engine.pickup(state)              # rope

    state, _ = engine.move(state, "west")        # -> Showers
    state, _ = engine.move(state, "north")       # -> Mess hall
    state, _ = engine.move(state, "north")       # -> Security office
    state, _ = engine.pickup(state)              # computer

    state, _ = engine.move(state, "east")        # -> Temperature control room
    state, _ = engine.pickup(state)              # valves

    state, _ = engine.move(state, "west")        # -> Security office
    state, _ = engine.move(state, "south")       # -> Mess hall
    state, _ = engine.move(state, "east")        # -> Generator room
    state, _ = engine.pickup(state)              # engine

    assert len(state.inventory) == 6

    state, msg = engine.move(state, "north")     # -> Warden Roys office
    assert state.status == "won"
    assert "escaped" in msg.lower()
