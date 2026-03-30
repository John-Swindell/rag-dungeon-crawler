from api.models.game_state import Room

ROOM_DEFINITIONS: dict[str, dict] = {
    "Cell": {
        "connections": {"East": "Mess hall"},
        "item": None,
    },
    "Mess hall": {
        "connections": {
            "West": "Cell",
            "North": "Security office",
            "South": "Showers",
            "East": "Generator room",
        },
        "item": "gas tank",
    },
    "Showers": {
        "connections": {"North": "Mess hall", "East": "Janitors closet"},
        "item": "tarp",
    },
    "Janitors closet": {
        "connections": {"West": "Showers"},
        "item": "rope",
    },
    "Security office": {
        "connections": {"South": "Mess hall", "East": "Temperature control room"},
        "item": "computer",
    },
    "Temperature control room": {
        "connections": {"West": "Security office"},
        "item": "valves",
    },
    "Generator room": {
        "connections": {"West": "Mess hall", "North": "Warden Roys office"},
        "item": "engine",
    },
    "Warden Roys office": {
        "connections": {"South": "Generator room"},
        "item": None,
    },
}

TOTAL_ITEMS = 6
START_ROOM = "Cell"
BOSS_ROOM = "Warden Roys office"


def build_rooms() -> dict[str, Room]:
    """Return a fresh copy of the room graph."""
    return {
        name: Room(name=name, connections=dict(data["connections"]), item=data["item"])
        for name, data in ROOM_DEFINITIONS.items()
    }
