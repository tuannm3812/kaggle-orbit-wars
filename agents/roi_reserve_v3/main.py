"""Tempo-aware, defensive, orbit-aware, and sun-safe Orbit Wars agent v3."""

import math
from collections import namedtuple
from typing import Any, Iterable, Optional

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Fleet, Planet
except Exception:
    Planet = namedtuple("Planet", "id owner x y radius ships production")
    Fleet = namedtuple("Fleet", "id owner x y angle from_planet_id ships")


BOARD_CENTER = (50.0, 50.0)
SUN_RADIUS = 10.0
SUN_SAFETY_MARGIN = 0.25
MAX_FLEET_SPEED = 6.0
EARLY_OWNED_COUNT = 3
THREAT_HORIZON_TURNS = 30
PLANET_THREAT_MARGIN = 0.75


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


def parse_fleets(rows: Iterable[Iterable[Any]]) -> list:
    """Convert raw fleet rows to Orbit Wars fleet tuples.

    Args:
        rows: Iterable of `[id, owner, x, y, angle, from_planet_id, ships]`.

    Returns:
        Parsed fleet records with attribute access.
    """
    return [Fleet(*row) for row in rows]


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


def total_production(planets: Iterable[Any]) -> int:
    """Return total production controlled by a planet collection."""
    return int(sum(int(planet.production) for planet in planets))


def source_reserve(planet: Any, owned_count: int = 1) -> int:
    """Calculate ships to keep on a source planet before launching.

    Args:
        planet: Source planet record.
        owned_count: Number of planets currently owned by the agent.

    Returns:
        Minimum ships to preserve on the source.
    """
    production = float(planet.production)
    base = int(max(5, production * 3))
    if owned_count <= 1:
        if production <= 1:
            return 4
        if production <= 3:
            return max(base, 8)
        return max(base, 12)
    if owned_count == 2:
        return max(base, 10)
    return base


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


def fleet_intersects_planet(fleet: Any, planet: Any, horizon_turns: int = THREAT_HORIZON_TURNS) -> bool:
    """Return whether a fleet's near-term trajectory intersects a planet."""
    speed = fleet_speed(int(fleet.ships))
    start_x = float(fleet.x)
    start_y = float(fleet.y)
    end_x = start_x + math.cos(float(fleet.angle)) * speed * horizon_turns
    end_y = start_y + math.sin(float(fleet.angle)) * speed * horizon_turns
    clearance = point_segment_distance(
        float(planet.x),
        float(planet.y),
        start_x,
        start_y,
        end_x,
        end_y,
    )
    return clearance <= float(planet.radius) + PLANET_THREAT_MARGIN


def threatened_planet_ids(player: int, planets: list, fleets: list) -> set:
    """Identify owned planets whose launch budget should be frozen for defense."""
    owned_planets = [planet for planet in planets if int(planet.owner) == player]
    threats = set()
    for fleet in fleets:
        if int(fleet.owner) == player:
            continue
        for planet in owned_planets:
            if int(fleet.ships) < source_reserve(planet, len(owned_planets)):
                continue
            if fleet_intersects_planet(fleet, planet):
                threats.add(int(planet.id))
    return threats


def is_orbiting_planet(planet: Any) -> bool:
    """Return whether a planet is inside the orbiting-radius threshold."""
    orbital_radius = math.hypot(float(planet.x) - BOARD_CENTER[0], float(planet.y) - BOARD_CENTER[1])
    return orbital_radius + float(planet.radius) < 50.0


def rotate_point(x: float, y: float, radians: float) -> tuple[float, float]:
    """Rotate a point around the Orbit Wars board center.

    Args:
        x: Current x coordinate.
        y: Current y coordinate.
        radians: Rotation angle.

    Returns:
        Rotated `(x, y)` coordinate.
    """
    center_x, center_y = BOARD_CENTER
    rel_x = x - center_x
    rel_y = y - center_y
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    return (
        center_x + rel_x * cos_a - rel_y * sin_a,
        center_y + rel_x * sin_a + rel_y * cos_a,
    )


def predicted_target(source: Any, target: Any, ships: int, angular_velocity: float) -> Any:
    """Predict a moving target position near fleet arrival time.

    Args:
        source: Source planet.
        target: Target planet at the current observation.
        ships: Ships planned for launch.
        angular_velocity: Environment angular velocity in radians per turn.

    Returns:
        Target-like record with future x/y coordinates when prediction applies.
    """
    if not angular_velocity or not is_orbiting_planet(target):
        return target
    arrival_turns = distance(source, target) / fleet_speed(ships)
    future_x, future_y = rotate_point(float(target.x), float(target.y), angular_velocity * arrival_turns)
    return Planet(
        int(target.id),
        int(target.owner),
        future_x,
        future_y,
        float(target.radius),
        int(target.ships),
        int(target.production),
    )


def ships_to_send(source: Any, target: Any, owned_count: int = 1) -> Optional[int]:
    """Calculate a conservative capture fleet while preserving reserve.

    Args:
        source: Owned source planet.
        target: Non-owned target planet.

    Returns:
        Ship count to send, or `None` if the source cannot afford the move.
    """
    needed = int(target.ships) + 1
    available = int(source.ships) - source_reserve(source, owned_count)
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


def early_travel_cap(owned_count: int, production_owned: int) -> float:
    """Return the maximum preferred travel time before the economy is stable."""
    if owned_count <= 1:
        return 18.0
    if owned_count <= EARLY_OWNED_COUNT or production_owned < 15:
        return 24.0
    return 36.0


def best_target(
    source: Any,
    targets: list,
    reserved_target_ids: set,
    owned_count: int,
    angular_velocity: float,
    production_owned: int,
) -> Optional[tuple]:
    """Choose the best affordable, sun-safe target for one source planet."""
    candidates = []
    for target in targets:
        if int(target.id) in reserved_target_ids:
            continue
        if crosses_sun(source, target):
            continue
        ships = ships_to_send(source, target, owned_count)
        if ships is None:
            continue
        aim_target = predicted_target(source, target, ships, angular_velocity)
        if crosses_sun(source, aim_target):
            continue
        travel_time = distance(source, target) / fleet_speed(ships)
        candidates.append((target, aim_target, ships, travel_time, target_score(source, target, ships)))
    if not candidates:
        return None

    if owned_count <= EARLY_OWNED_COUNT or production_owned < 15:
        cap = early_travel_cap(owned_count, production_owned)
        local_neutrals = [
            candidate
            for candidate in candidates
            if int(candidate[0].owner) < 0 and candidate[3] <= cap
        ]
        if local_neutrals:
            candidates = local_neutrals
        else:
            capped = [candidate for candidate in candidates if candidate[3] <= cap * 1.35]
            if capped:
                candidates = capped

    best = max(candidates, key=lambda item: (item[4], -item[3], int(item[0].production)))
    target, aim_target, ships, _, _ = best
    return target, aim_target, ships


def agent(obs: Any) -> list:
    """Return ROI-ranked, reserve-safe, sun-safe Orbit Wars launch actions."""
    try:
        player = int(get_obs_value(obs, "player", 0))
        raw_planets = get_obs_value(obs, "planets", [])
        raw_fleets = get_obs_value(obs, "fleets", [])
        angular_velocity = float(get_obs_value(obs, "angular_velocity", 0.0) or 0.0)
        planets = parse_planets(raw_planets)
        fleets = parse_fleets(raw_fleets)
        my_planets = [p for p in planets if int(p.owner) == player]
        targets = [p for p in planets if int(p.owner) != player]

        moves = []
        if not targets:
            return moves

        reserved_target_ids = set()
        threatened_ids = threatened_planet_ids(player, planets, fleets)
        production_owned = total_production(my_planets)
        ordered_sources = sorted(my_planets, key=lambda p: (int(p.ships), int(p.production)), reverse=True)
        for source in ordered_sources:
            if int(source.id) in threatened_ids:
                continue
            chosen = best_target(
                source,
                targets,
                reserved_target_ids,
                len(my_planets),
                angular_velocity,
                production_owned,
            )
            if chosen is None:
                continue
            target, aim_target, ships = chosen
            reserved_target_ids.add(int(target.id))
            moves.append([int(source.id), launch_angle(source, aim_target), int(ships)])
        return moves
    except Exception:
        return []
