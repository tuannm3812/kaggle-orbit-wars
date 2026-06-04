"""Tempo-aware ROI agent v6 with bounded regroup pressure."""

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
REGROUP_LOOKAHEAD_TURNS = 8
REGROUP_PRESSURE_THRESHOLD = 6.0
REGROUP_MAX_SHIPS_FRAC = 0.5
REGROUP_MAX_SHIPS_ABS = 14


def get_obs_value(obs: Any, name: str, default: Any) -> Any:
    if isinstance(obs, dict):
        return obs.get(name, default)
    return getattr(obs, name, default)


def parse_planets(rows: Iterable[Iterable[Any]]) -> list:
    return [Planet(*row) for row in rows]


def parse_fleets(rows: Iterable[Iterable[Any]]) -> list:
    return [Fleet(*row) for row in rows]


def distance(source: Any, target: Any) -> float:
    return math.hypot(float(target.x) - float(source.x), float(target.y) - float(source.y))


def launch_angle(source: Any, target: Any) -> float:
    return float(math.atan2(float(target.y) - float(source.y), float(target.x) - float(source.x)))


def fleet_speed(ships: int, max_speed: float = MAX_FLEET_SPEED) -> float:
    ships = max(int(ships), 1)
    return 1.0 + (max_speed - 1.0) * (math.log(ships) / math.log(1000.0)) ** 1.5


def total_production(planets: Iterable[Any]) -> int:
    return int(sum(int(planet.production) for planet in planets))


def source_reserve(planet: Any, owned_count: int = 1) -> int:
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


def fleet_eta_to_planet(fleet: Any, planet: Any, horizon_turns: int = REGROUP_LOOKAHEAD_TURNS) -> Optional[int]:
    speed = fleet_speed(int(fleet.ships))
    dir_x = math.cos(float(fleet.angle))
    dir_y = math.sin(float(fleet.angle))
    dx = float(planet.x) - float(fleet.x)
    dy = float(planet.y) - float(fleet.y)
    projection = dx * dir_x + dy * dir_y
    if projection < 0:
        return None
    perpendicular_sq = dx * dx + dy * dy - projection * projection
    radius = float(planet.radius) + PLANET_THREAT_MARGIN
    if perpendicular_sq > radius * radius:
        return None
    hit_distance = max(0.0, projection - math.sqrt(max(0.0, radius * radius - perpendicular_sq)))
    eta = int(math.ceil(hit_distance / speed))
    if eta < 1 or eta > horizon_turns:
        return None
    return eta


def threatened_planet_ids(player: int, planets: list, fleets: list) -> set:
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
    orbital_radius = math.hypot(float(planet.x) - BOARD_CENTER[0], float(planet.y) - BOARD_CENTER[1])
    return orbital_radius + float(planet.radius) < 50.0


def rotate_point(x: float, y: float, radians: float) -> tuple[float, float]:
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
    needed = int(target.ships) + 1
    available = int(source.ships) - source_reserve(source, owned_count)
    if available < needed:
        return None
    return int(needed)


def target_score(source: Any, target: Any, ships: int) -> float:
    travel_time = distance(source, target) / fleet_speed(ships)
    capture_cost = max(float(ships), 1.0)
    production_value = float(target.production) * 30.0
    enemy_bonus = 20.0 if int(target.owner) >= 0 else 0.0
    return (production_value + enemy_bonus) / (capture_cost + travel_time)


def early_travel_cap(owned_count: int, production_owned: int) -> float:
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


def enemy_pressure_by_planet(player: int, my_planets: list, planets: list, fleets: list) -> dict[int, float]:
    pressure: dict[int, float] = {int(planet.id): 0.0 for planet in my_planets}
    if not my_planets:
        return pressure

    horizon_speed = max(1.0, MAX_FLEET_SPEED * float(REGROUP_LOOKAHEAD_TURNS))
    for fleet in fleets:
        if int(fleet.owner) < 0 or int(fleet.owner) == player:
            continue
        for planet in my_planets:
            eta = fleet_eta_to_planet(fleet, planet, REGROUP_LOOKAHEAD_TURNS)
            if eta is None:
                continue
            decay = 1.0 - (float(eta) / float(REGROUP_LOOKAHEAD_TURNS))
            if decay > 0:
                pressure[int(planet.id)] += float(fleet.ships) * decay

    for enemy_planet in planets:
        if int(enemy_planet.owner) < 0 or int(enemy_planet.owner) == player:
            continue
        for planet in my_planets:
            d = distance(enemy_planet, planet)
            decay = 1.0 - (d / horizon_speed)
            if decay <= 0:
                continue
            pressure[int(planet.id)] += float(enemy_planet.production) * 3.0 * decay
            pressure[int(planet.id)] += max(0.0, float(enemy_planet.ships) - source_reserve(enemy_planet, 4)) * 0.1 * decay
    return pressure


def build_regroup_moves(
    player: int,
    my_planets: list,
    planets: list,
    fleets: list,
    angular_velocity: float,
    used_source_ids: set,
    threatened_ids: set,
) -> list:
    if len(my_planets) < 2:
        return []

    pressure = enemy_pressure_by_planet(player, my_planets, planets, fleets)
    pressure_targets = sorted(
        [(planet_id, value) for planet_id, value in pressure.items() if value >= REGROUP_PRESSURE_THRESHOLD],
        key=lambda item: item[1],
        reverse=True,
    )
    if not pressure_targets:
        return []

    owned_count = len(my_planets)
    mutable_ships = {int(planet.id): int(planet.ships) for planet in my_planets}
    lookup = {int(planet.id): planet for planet in my_planets}
    moves = []

    for target_id, total_pressure in pressure_targets:
        target = lookup.get(target_id)
        if target is None:
            continue
        target_reserve = source_reserve(target, owned_count)
        current_surplus = max(0, mutable_ships[target_id] - target_reserve)
        needed = max(0, int(math.ceil(total_pressure * 0.5)) - current_surplus)
        if needed <= 0:
            continue

        donors = sorted(
            [
                planet
                for planet in my_planets
                if int(planet.id) not in used_source_ids
                and int(planet.id) not in threatened_ids
                and int(planet.id) != target_id
                and mutable_ships[int(planet.id)] > source_reserve(planet, owned_count) + 1
            ],
            key=lambda donor: distance(donor, target),
        )
        for donor in donors:
            if needed <= 0:
                break
            donor_id = int(donor.id)
            donor_excess = max(0, mutable_ships[donor_id] - source_reserve(donor, owned_count))
            if donor_excess <= 1:
                continue

            transfer = max(
                1,
                min(
                    int(donor_excess * REGROUP_MAX_SHIPS_FRAC),
                    needed,
                    REGROUP_MAX_SHIPS_ABS,
                ),
            )
            if transfer <= 0:
                continue

            aim_target = predicted_target(donor, target, transfer, angular_velocity)
            if crosses_sun(donor, aim_target):
                continue
            if distance(donor, target) / fleet_speed(transfer) > REGROUP_LOOKAHEAD_TURNS:
                continue

            moves.append([donor_id, launch_angle(donor, aim_target), transfer])
            mutable_ships[donor_id] -= transfer
            mutable_ships[target_id] += transfer
            needed -= transfer
            used_source_ids.add(donor_id)
            used_source_ids.add(target_id)

    return moves


def agent(obs: Any) -> list:
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
        used_source_ids = set()
        ordered_sources = sorted(my_planets, key=lambda p: (int(p.ships), int(p.production)), reverse=True)
        for source in ordered_sources:
            if int(source.id) in threatened_ids or int(source.id) in used_source_ids:
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
            used_source_ids.add(int(source.id))
            moves.append([int(source.id), launch_angle(source, aim_target), int(ships)])

        moves.extend(
            build_regroup_moves(
                player,
                my_planets=my_planets,
                planets=planets,
                fleets=fleets,
                angular_velocity=angular_velocity,
                used_source_ids=used_source_ids,
                threatened_ids=threatened_ids,
            )
        )
        return moves
    except Exception:
        return []
