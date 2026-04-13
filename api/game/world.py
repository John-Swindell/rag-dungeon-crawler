from api.models.game_state import Room

CHARACTERS = ["Weasel", "Sal", "Billy", "Finn"]

ROOM_DEFINITIONS: dict[str, dict] = {
    "Cell": {
        "connections": {"East": "Michigan Avenue"},
        "item": None,
    },
    "Michigan Avenue": {
        "connections": {
            "West": "Cell",
            "North": "Times Square",
            "South": "Broadway",
            "East": "Showers",
        },
        "item": None,
    },
    "Broadway": {
        "connections": {
            "North": "Michigan Avenue",
            "East": "Laundry Room",
            "South": "Cafeteria",
        },
        "item": None,
    },
    "Times Square": {
        "connections": {
            "South": "Michigan Avenue",
            "East": "Library",
            "North": "Citadel Tunnels",
            "West": "Infirmary",
        },
        "item": None,
    },
    "Showers": {
        "connections": {
            "West": "Michigan Avenue",
            "South": "Laundry Room",
        },
        "item": None,
    },
    "Laundry Room": {
        "connections": {
            "West": "Broadway",
            "North": "Showers",
        },
        "item": "rigging",
    },
    "Cafeteria": {
        "connections": {
            "North": "Broadway",
            "East": "Kitchen",
            "South": "Recreation Yard",
        },
        "item": None,
    },
    "Kitchen": {
        "connections": {"West": "Cafeteria"},
        "item": "fuel tank",
    },
    "Recreation Yard": {
        "connections": {
            "North": "Cafeteria",
            "East": "Guard Tower",
            "South": "Docks",
        },
        "item": None,
    },
    "Guard Tower": {
        "connections": {"West": "Recreation Yard"},
        "item": "wiring kit",
    },
    "Docks": {
        "connections": {
            "North": "Recreation Yard",
            "East": "Building 64",
        },
        "item": "engine",
    },
    "Building 64": {
        "connections": {
            "West": "Docks",
            "North": "Gondola Station",
        },
        "item": "flight gear",
    },
    "Gondola Station": {
        "connections": {
            "South": "Building 64",
            "North": "Roof",
        },
        "item": None,
    },
    "Roof": {
        "connections": {
            "South": "Gondola Station",
            "West": "Spiral Staircase",
        },
        "item": "propeller",
    },
    "Spiral Staircase": {
        "connections": {
            "East": "Roof",
            "South": "Citadel Tunnels",
        },
        "item": None,
    },
    "Citadel Tunnels": {
        "connections": {
            "North": "Spiral Staircase",
            "South": "Times Square",
            "East": "Wardens Office",
        },
        "item": None,
    },
    "Library": {
        "connections": {"West": "Times Square"},
        "item": "control valves",
    },
    "Infirmary": {
        "connections": {
            "East": "Times Square",
            "North": "Wardens Office",
        },
        "item": "navigation tools",
    },
    "Wardens Office": {
        "connections": {
            "South": "Infirmary",
            "West": "Citadel Tunnels",
        },
        "item": None,
    },
}

TOTAL_ITEMS = 8
START_ROOM = "Cell"
BOSS_ROOM = "Wardens Office"

MAP_SIZE = (800, 1000)
GRID_SIZE = 20

class Map:
    def __init__(self):
        self.map = {}
        self.num_rooms =  len(ROOM_DEFINITIONS)
        self.min_space_dimension = 2 * GRID_SIZE



def build_rooms() -> dict[str, Room]:
    """Return a fresh copy of the room graph."""
    return {
        name: Room(name=name, connections=dict(data["connections"]), item=data["item"])
        for name, data in ROOM_DEFINITIONS.items()
    }
