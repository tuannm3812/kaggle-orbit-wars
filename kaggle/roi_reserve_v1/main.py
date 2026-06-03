"""ROI, reserve, and sun-safe Orbit Wars agent v1."""

import math
from collections import namedtuple
from typing import Any, Iterable, Optional

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
except Exception:
    Planet = namedtuple("Planet", "id owner x y radius ships production")


BOARD_CENTER = (50.0, 50.0)
SUN_RADIUS = 10.0
SUN_SAFETY_MARGIN = 0.25
MAX_FLEET_SPEED = 6.0


def get_obs_value(obs: Any, name: str, default: Any) -> Any:
    """Read an observation field from either dict or object observations.

    Args:
        obs: Kaggle observation as a dict-like or object-like value.
        name: Field name to read.
        default: Value returned when the field is absent.

    Returns:
        The observation field value, or `default` when unavailable.
    """
    if isinstance(obs, dict):
        return obs.get(name, default)
    return getattr(obs, name, default)


def parse_planets(rows: Iterable[Iterable[Any]]) -> list:
    """Convert raw planet rows to Orbit Wars planet tuples.

    Args:
        rows: Iterable of `[id, owner, x, y, radius, ships, production]`.

    Returns:
        Parsed planet records with attribute access.
    """
    return [Planet(*row) for row in rows]


def distance(source: Any, target: Any) -> float:
    """Calculate Euclidean distance between two planet-like objects."""
    return math.hypot(float(target.x) - float(source.x), float(target.y) - float(source.y))


def launch_angle(source: Any, target: Any) -> float:
    """Calculate launch angle from source to target in radians."""
    return float(math.atan2(float(target.y) - float(source.y), float(target.x) - float(source.x)))


def fleet_speed(ships: int, max_speed: float = MAX_FLEET_SPEED) -> float:
    """Calculate fleet speed from ship count using the Orbit Wars curve.

    Args:
        ships: Number of ships in the fleet.
        max_speed: Environment maximum fleet speed.

    Returns:
        Fleet speed in board units per turn.
    """
    ships = max(int(ships), 1)
    return 1.0 + (max_speed - 1.0) * (math.log(ships) / math.log(1000.0)) ** 1.5


def source_reserve(planet: Any) -> int:
    """Calculate ships to keep on a source planet before launching."""
    return int(max(5, float(planet.production) * 3))


def point_segment_distance(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
) -> float:
    """Calculate the shortest distance from a point to a segment."""
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    closest_x = ax + t * dx
    closest_y = ay + t * dy
    return math.hypot(px - closest_x, py - closest_y)


def crosses_sun(source: Any, target: Any) -> bool:
    """Return whether the direct launch segment intersects the sun."""
    center_x, center_y = BOARD_CENTER
    clearance = point_segment_distance(
        center_x,
        center_y,
        float(source.x),
        float(source.y),
        float(target.x),
        float(target.y),
    )
    return clearance <= SUN_RADIUS + SUN_SAFETY_MARGIN


def ships_to_send(source: Any, target: Any) -> Optional[int]:
    """Calculate a conservative capture fleet while preserving reserve.

    Args:
        source: Owned source planet.
        target: Non-owned target planet.

    Returns:
        Ship count to send, or `None` if the source cannot afford the move.
    """
    needed = int(target.ships) + 1
    available = int(source.ships) - source_reserve(source)
    if available < needed:
        return None
    return int(needed)


def target_score(source: Any, target: Any, ships: int) -> float:
    """Score a target by production value adjusted for cost and travel time."""
    travel_time = distance(source, target) / fleet_speed(ships)
    capture_cost = max(float(ships), 1.0)
    production_value = float(target.production) * 30.0
    enemy_bonus = 20.0 if int(target.owner) >= 0 else 0.0
    return (production_value + enemy_bonus) / (capture_cost + travel_time)


def best_target(source: Any, targets: list) -> Optional[tuple]:
    """Choose the best affordable, sun-safe target for one source planet."""
    best = None
    best_score = float("-inf")
    for target in targets:
        if crosses_sun(source, target):
            continue
        ships = ships_to_send(source, target)
        if ships is None:
            continue
        score = target_score(source, target, ships)
        if score > best_score:
            best_score = score
            best = (target, ships)
    return best


def agent(obs: Any) -> list:
    """Return ROI-ranked, reserve-safe, sun-safe Orbit Wars launch actions."""
    try:
        player = int(get_obs_value(obs, "player", 0))
        raw_planets = get_obs_value(obs, "planets", [])
        planets = parse_planets(raw_planets)
        my_planets = [p for p in planets if int(p.owner) == player]
        targets = [p for p in planets if int(p.owner) != player]

        moves = []
        if not targets:
            return moves

        for source in my_planets:
            chosen = best_target(source, targets)
            if chosen is None:
                continue
            target, ships = chosen
            moves.append([int(source.id), launch_angle(source, target), int(ships)])
        return moves
    except Exception:
        return []
