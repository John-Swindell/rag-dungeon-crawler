def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_new_game_returns_session(client):
    response = client.post("/game/new")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["current_room"] == "Cell"
    assert data["status"] == "playing"


def test_get_game(client, session_id):
    response = client.get(f"/game/{session_id}")
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id


def test_move_via_api(client, session_id):
    response = client.post(f"/game/{session_id}/move", json={"direction": "east"})
    assert response.status_code == 200
    assert response.json()["current_room"] == "Mess hall"


def test_pickup_via_api(client, session_id):
    # Move to a room with an item first
    client.post(f"/game/{session_id}/move", json={"direction": "east"})
    response = client.post(f"/game/{session_id}/pickup")
    assert response.status_code == 200
    assert "gas tank" in response.json()["inventory"]


def test_session_not_found(client):
    response = client.get("/game/nonexistent-id")
    assert response.status_code == 404
