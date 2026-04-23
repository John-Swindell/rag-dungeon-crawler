def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_new_game_returns_session_and_map(client):
    response = client.post("/game/new", json={"character": "Sal"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["current_room"] == "Cell"
    assert data["character"] == "Sal"
    assert data["status"] == "playing"
    assert data["map_rooms"]
    assert data["map_seed"]
    assert data["hints"]


def test_get_game(client, session_id):
    response = client.get(f"/game/{session_id}")
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id


def test_move_via_api(client, session_id):
    current = client.get(f"/game/{session_id}").json()
    direction = current["available_directions"][0]
    expected_room = next(
        room["connections"][direction]
        for room in current["map_rooms"]
        if room["name"] == current["current_room"]
    )

    response = client.post(f"/game/{session_id}/move", json={"direction": direction})

    assert response.status_code == 200
    assert response.json()["current_room"] == expected_room


def test_pickup_via_api(client, session_id):
    current = client.get(f"/game/{session_id}").json()
    item_room = next(room for room in current["map_rooms"] if room["item"] is not None)
    path = _path_to(current["map_rooms"], current["current_room"], item_room["name"])

    for source, target in zip(path, path[1:], strict=False):
        direction = _direction_between(current["map_rooms"], source, target)
        current = client.post(f"/game/{session_id}/move", json={"direction": direction}).json()

    response = client.post(f"/game/{session_id}/pickup")

    assert response.status_code == 200
    assert len(response.json()["inventory"]) == 1


def test_session_not_found(client):
    response = client.get("/game/nonexistent-id")
    assert response.status_code == 404


def test_invalid_character(client):
    response = client.post("/game/new", json={"character": "Richtofen"})
    assert response.status_code == 422


def _path_to(map_rooms: list[dict], start: str, goal: str) -> list[str]:
    rooms = {room["name"]: room for room in map_rooms}
    queue = [(start, [start])]
    visited = set()

    while queue:
        current, path = queue.pop(0)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor in rooms[current]["connections"].values():
            queue.append((neighbor, [*path, neighbor]))

    raise AssertionError(f"No path from {start} to {goal}")


def _direction_between(map_rooms: list[dict], source: str, target: str) -> str:
    room = next(room for room in map_rooms if room["name"] == source)
    for direction, destination in room["connections"].items():
        if destination == target:
            return direction
    raise AssertionError(f"No direction from {source} to {target}")
