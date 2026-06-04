"""Combat-survival, reinforcement-capable, orbit-aware, and sun-safe Orbit Wars agent v5."""

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
REINFORCE_LOOKAHEAD_TURNS = 35
REINFORCE_SAFETY_MARGIN = 2
ENEMY_PRODUCTION_MARGIN = 2
SOURCE_SURVIVAL_LOOKAHEAD_TURNS = 45
SOURCE_SURVIVAL_MARGIN = 2
CONTESTED_TARGET_WINDOW = 10.0
MULTIPLAYER_STABLE_PRODUCTION = 30
REGROUP_LOOKAHEAD_TURNS = 8
REGROUP_PRESSURE_THRESHOLD = 6.0
REGROUP_MAX_SHIPS_FRAC = 0.5
REGROUP_MAX_SHIPS_ABS = 14


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


def fleet_eta_to_planet(fleet: Any, planet: Any, horizon_turns: int = REINFORCE_LOOKAHEAD_TURNS) -> Optional[int]:
    """Estimate when a fleet trajectory first reaches a planet.

    Args:
        fleet: Fleet-like record with position, angle, and ship count.
        planet: Planet-like collision target.
        horizon_turns: Maximum ETA to consider.

    Returns:
        ETA in turns, or `None` if the fleet does not hit within the horizon.
    """
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


def incoming_reinforcement_needs(player: int, planets: list, fleets: list) -> dict:
    """Compute owned planets that need timed reinforcement to survive visible fleets."""
    needs = {}
    owned_planets = [planet for planet in planets if int(planet.owner) == player]
    for planet in owned_planets:
        enemy_arrivals = []
        for fleet in fleets:
            if int(fleet.owner) == player:
                continue
            eta = fleet_eta_to_planet(fleet, planet)
            if eta is None:
                continue
            enemy_arrivals.append((eta, int(fleet.ships)))
        if not enemy_arrivals:
            continue

        enemy_arrivals.sort()
        garrison = float(planet.ships)
        previous_turn = 0
        for eta, ships in enemy_arrivals:
            garrison += max(0, eta - previous_turn) * float(planet.production)
            garrison -= ships
            previous_turn = eta
            if garrison < 0:
                needs[int(planet.id)] = {
                    "planet": planet,
                    "ships_needed": int(math.ceil(-garrison)) + REINFORCE_SAFETY_MARGIN,
                    "needed_by_turn": eta,
                }
                break
    return needs


def enemy_players(player: int, planets: list, fleets: list) -> set:
    """Return visible non-neutral enemy owners."""
    owners = {
        int(planet.owner)
        for planet in planets
        if int(planet.owner) >= 0 and int(planet.owner) != player
    }
    owners.update(
        int(fleet.owner)
        for fleet in fleets
        if int(fleet.owner) >= 0 and int(fleet.owner) != player
    )
    return owners


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


def enemy_pressure_by_planet(
    player: int,
    my_planets: list,
    fleets: list,
    horizon_turns: float = REGROUP_LOOKAHEAD_TURNS,
) -> dict[int, float]:
    """Estimate per-planet pressure from visible enemy fleets in the next turns."""
    pressure: dict[int, float] = {int(planet.id): 0.0 for planet in my_planets}
    if not my_planets or horizon_turns <= 0:
        return pressure
    horizon = int(horizon_turns)
    for fleet in fleets:
        if int(fleet.owner) == player or int(fleet.owner) < 0:
            continue
        for planet in my_planets:
            eta = fleet_eta_to_planet(fleet, planet, horizon)
            if eta is None:
                continue
            decay = 1.0 - (float(eta) / float(horizon))
            if decay <= 0:
                continue
            pressure[int(planet.id)] += float(fleet.ships) * decay
    return pressure


def projected_owned_garrison(
    planet: Any,
    player: int,
    fleets: list,
    ships_spent: int = 0,
    horizon_turns: int = SOURCE_SURVIVAL_LOOKAHEAD_TURNS,
) -> float:
    """Project owned-planet garrison after visible fleet arrivals."""
    arrivals = []
    for fleet in fleets:
        eta = fleet_eta_to_planet(fleet, planet, horizon_turns)
        if eta is None:
            continue
        arrivals.append((eta, int(fleet.owner), int(fleet.ships)))
    arrivals.sort()

    garrison = float(planet.ships) - float(ships_spent)
    previous_turn = 0
    for eta, owner, ships in arrivals:
        garrison += max(0, eta - previous_turn) * float(planet.production)
        if owner == player:
            garrison += ships
        else:
            garrison -= ships
        previous_turn = eta
        if garrison < 0:
            return garrison
    return garrison


def source_survives_launch(
    source: Any,
    player: int,
    fleets: list,
    ships: int,
    owned_count: int,
) -> bool:
    """Return whether a source remains safe after spending launch ships."""
    projected = projected_owned_garrison(source, player, fleets, ships)
    reserve_floor = source_reserve(source, owned_count) + SOURCE_SURVIVAL_MARGIN
    return projected >= reserve_floor


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


def enemy_support_pressure(
    player: int,
    target: Any,
    planets: list,
    travel_turns: float,
) -> int:
    """Estimate visible enemy support that can contest a target near arrival."""
    if int(target.owner) < 0:
        return 0

    pressure = 0.0
    for planet in planets:
        if int(planet.owner) < 0 or int(planet.owner) == player or int(planet.id) == int(target.id):
            continue
        support_eta = distance(planet, target) / fleet_speed(max(int(planet.ships), 1))
        if support_eta > travel_turns + CONTESTED_TARGET_WINDOW:
            continue
        pressure += float(planet.production) * max(1.0, travel_turns - support_eta + CONTESTED_TARGET_WINDOW)
        pressure += max(0.0, float(planet.ships) - source_reserve(planet, 4)) * 0.35
    return int(math.ceil(pressure))


def build_regroup_moves(
    player: int,
    my_planets: list,
    planets: list,
    fleets: list,
    angular_velocity: float,
    used_source_ids: set,
    threatened_ids: set,
) -> list:
    """Move idle ships from safe surplus sources into pressure hotspots.

    This is a low-cost producer-inspired regroup pass. It is intentionally limited
    to single-step redistributions, so it can only correct early midgame pressure
    imbalances, not perform deep logistic planning.
    """
    if len(my_planets) < 2:
        return []

    pressure = enemy_pressure_by_planet(
        player,
        my_planets=my_planets,
        fleets=fleets,
        horizon_turns=REGROUP_LOOKAHEAD_TURNS,
    )
    pressure_targets = sorted(
        [(planet_id, value) for planet_id, value in pressure.items() if value >= REGROUP_PRESSURE_THRESHOLD],
        key=lambda item: item[1],
        reverse=True,
    )
    if not pressure_targets:
        return []

    planet_lookup = {int(planet.id): planet for planet in my_planets}
    movable_planets = [
        planet
        for planet in my_planets
        if int(planet.id) not in used_source_ids
        and int(planet.id) not in threatened_ids
    ]
    if not movable_planets:
        return []

    owned_count = len(my_planets)
    mutable_ships = {int(planet.id): int(planet.ships) for planet in my_planets}
    moves: list = []

    for target_id, total_pressure in pressure_targets:
        target = planet_lookup.get(target_id)
        if target is None:
            continue
        target_reserve = source_reserve(target, owned_count)
        current_surplus = max(0, mutable_ships[target_id] - target_reserve)
        needed = max(0, int(math.ceil(total_pressure * 0.6)) - current_surplus)
        if needed <= 0:
            continue

        donors = sorted(
            [
                planet
                for planet in movable_planets
                if int(planet.id) not in {target_id}
                and mutable_ships[int(planet.id)] > source_reserve(planet, owned_count)
            ],
            key=lambda donor: distance(donor, target),
        )
        for donor in donors:
            if needed <= 0:
                break
            donor_id = int(donor.id)
            donor_ships = mutable_ships.get(donor_id, int(donor.ships))
            donor_reserve = source_reserve(donor, owned_count)
            donor_excess = max(0, donor_ships - donor_reserve)
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
            if not source_survives_launch(donor, player, fleets, transfer, owned_count):
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

    return moves


def capture_ships_needed(source: Any, target: Any, seed_ships: int, player: int, planets: list) -> int:
    """Estimate capture cost at fleet arrival time."""
    needed = int(target.ships) + 1
    if int(target.owner) < 0:
        return needed

    ships = max(needed, int(seed_ships))
    for _ in range(3):
        travel_turns = distance(source, target) / fleet_speed(ships)
        support = enemy_support_pressure(player, target, planets, travel_turns)
        next_needed = (
            int(math.ceil(int(target.ships) + travel_turns * float(target.production)))
            + support
            + ENEMY_PRODUCTION_MARGIN
        )
        if next_needed == ships:
            break
        ships = max(needed, next_needed)
    return int(ships)


def ships_to_send(source: Any, target: Any, owned_count: int, player: int, planets: list, fleets: list) -> Optional[int]:
    """Calculate a conservative capture fleet while preserving reserve.

    Args:
        source: Owned source planet.
        target: Non-owned target planet.

    Returns:
        Ship count to send, or `None` if the source cannot afford the move.
    """
    needed = capture_ships_needed(source, target, int(target.ships) + 1, player, planets)
    available = int(source.ships) - source_reserve(source, owned_count)
    if available < needed:
        return None
    if not source_survives_launch(source, player, fleets, needed, owned_count):
        return None
    return int(needed)


def build_reinforcement_moves(
    player: int,
    my_planets: list,
    planets: list,
    fleets: list,
    angular_velocity: float,
) -> tuple[list, set]:
    """Create high-priority reinforcement moves for planets forecast to fall."""
    needs = incoming_reinforcement_needs(player, planets, fleets)
    if not needs:
        return [], set()

    moves = []
    used_sources = set()
    ordered_needs = sorted(needs.values(), key=lambda item: (item["needed_by_turn"], -int(item["planet"].production)))
    for need in ordered_needs:
        target = need["planet"]
        due_turn = int(need["needed_by_turn"])
        ships_needed = max(1, int(need["ships_needed"]))
        best = None
        for source in my_planets:
            if int(source.id) == int(target.id) or int(source.id) in used_sources:
                continue
            available = int(source.ships) - source_reserve(source, len(my_planets))
            if available < ships_needed:
                continue
            send = min(available, ships_needed)
            if not source_survives_launch(source, player, fleets, send, len(my_planets)):
                continue
            aim_target = predicted_target(source, target, send, angular_velocity)
            if crosses_sun(source, aim_target):
                continue
            travel_turns = distance(source, aim_target) / fleet_speed(send)
            if travel_turns > due_turn:
                continue
            candidate = (travel_turns, -int(source.production), source, aim_target, send)
            if best is None or candidate < best:
                best = candidate
        if best is None:
            continue
        _, _, source, aim_target, send = best
        used_sources.add(int(source.id))
        moves.append([int(source.id), launch_angle(source, aim_target), int(send)])
    return moves, used_sources


def target_score(
    source: Any,
    target: Any,
    ships: int,
    player: int,
    planets: list,
    active_enemy_count: int,
    production_owned: int,
) -> float:
    """Score a target by production value adjusted for cost and travel time."""
    travel_time = distance(source, target) / fleet_speed(ships)
    capture_cost = max(float(ships), 1.0)
    production_value = float(target.production) * 30.0
    enemy_bonus = 16.0 if int(target.owner) >= 0 else 0.0
    support = enemy_support_pressure(player, target, planets, travel_time)
    multiplayer_penalty = 0.0
    if active_enemy_count > 1 and production_owned < MULTIPLAYER_STABLE_PRODUCTION:
        multiplayer_penalty = 18.0 if int(target.owner) >= 0 else 4.0
    return (production_value + enemy_bonus) / (capture_cost + support + travel_time + multiplayer_penalty)


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
    player: int,
    planets: list,
    fleets: list,
    active_enemy_count: int,
) -> Optional[tuple]:
    """Choose the best affordable, sun-safe target for one source planet."""
    candidates = []
    for target in targets:
        if int(target.id) in reserved_target_ids:
            continue
        if active_enemy_count > 1 and production_owned < MULTIPLAYER_STABLE_PRODUCTION and int(target.owner) >= 0:
            continue
        if crosses_sun(source, target):
            continue
        ships = ships_to_send(source, target, owned_count, player, planets, fleets)
        if ships is None:
            continue
        aim_target = predicted_target(source, target, ships, angular_velocity)
        if crosses_sun(source, aim_target):
            continue
        travel_time = distance(source, target) / fleet_speed(ships)
        score = target_score(source, target, ships, player, planets, active_enemy_count, production_owned)
        cluster_distance = min(
            (
                distance(target, planet)
                for planet in planets
                if int(planet.owner) == player and int(planet.id) != int(source.id)
            ),
            default=distance(source, target),
        )
        candidates.append((target, aim_target, ships, travel_time, score, cluster_distance))
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

    best = max(candidates, key=lambda item: (item[4], -item[3], -item[5], int(item[0].production)))
    target, aim_target, ships, _, _, _ = best
    return target, aim_target, ships


def agent(obs: Any) -> list:
    """Return reinforcement-first, ROI-ranked, reserve-safe Orbit Wars launch actions."""
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
        active_enemy_count = len(enemy_players(player, planets, fleets))
        reinforcement_moves, reinforcement_sources = build_reinforcement_moves(
            player,
            my_planets,
            planets,
            fleets,
            angular_velocity,
        )
        moves.extend(reinforcement_moves)
        ordered_sources = sorted(my_planets, key=lambda p: (int(p.ships), int(p.production)), reverse=True)
        used_source_ids = set(reinforcement_sources)
        for source in ordered_sources:
            if int(source.id) in used_source_ids:
                continue
            if int(source.id) in threatened_ids:
                continue
            chosen = best_target(
                source,
                targets,
                reserved_target_ids,
                len(my_planets),
                angular_velocity,
                production_owned,
                player,
                planets,
                fleets,
                active_enemy_count,
            )
            if chosen is None:
                continue
            target, aim_target, ships = chosen
            reserved_target_ids.add(int(target.id))
            moves.append([int(source.id), launch_angle(source, aim_target), int(ships)])
            used_source_ids.add(int(source.id))

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
