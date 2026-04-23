from __future__ import annotations

import heapq
import math

from api.game.world import room_center
from api.models.game_state import Room


def _heuristic(rooms: dict[str, Room], source: str, target: str) -> float:
    source_x, source_y = room_center(rooms[source])
    target_x, target_y = room_center(rooms[target])
    return math.dist((source_x, source_y), (target_x, target_y))


def a_star(rooms: dict[str, Room], start: str, goal: str) -> list[str]:
    """Find the fastest room path between two locations using A*."""
    if start not in rooms or goal not in rooms:
        return []

    frontier: list[tuple[float, str]] = [(0, start)]
    came_from: dict[str, str | None] = {start: None}
    cost_so_far: dict[str, float] = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in rooms[current].connections.values():
            new_cost = cost_so_far[current] + _heuristic(rooms, current, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + _heuristic(rooms, neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        return []

    path = [goal]
    current = goal
    while came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
