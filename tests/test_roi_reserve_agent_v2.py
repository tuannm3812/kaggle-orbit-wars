import importlib.util
import math
from pathlib import Path


AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "roi_reserve_v2" / "main.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("roi_reserve_v2", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def obs_with(planets, player=0, angular_velocity=0.03):
    return {
        "player": player,
        "planets": planets,
        "fleets": [],
        "angular_velocity": angular_velocity,
        "initial_planets": planets,
        "comet_planet_ids": [],
    }


def test_agent_does_not_duplicate_targets_in_one_turn():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 90, 5],
            [1, 0, 10.0, 20.0, 1.0, 90, 5],
            [2, -1, 25.0, 15.0, 2.0, 10, 5],
            [3, -1, 26.0, 18.0, 2.0, 10, 4],
        ]
    )

    moves = module.agent(obs)

    assert len(moves) == 2
    angles = {round(move[1], 3) for move in moves}
    assert len(angles) == 2


def test_agent_aims_ahead_for_orbiting_target():
    module = load_agent_module()
    source = module.Planet(0, 0, 50.0, 10.0, 1.0, 120, 5)
    target = module.Planet(1, -1, 65.0, 50.0, 1.0, 10, 5)
    ships = 11

    current_angle = module.launch_angle(source, target)
    predicted_target = module.predicted_target(source, target, ships, 0.05)
    predicted_angle = module.launch_angle(source, predicted_target)

    assert predicted_target.x < target.x
    assert predicted_target.y > target.y
    assert not math.isclose(predicted_angle, current_angle)


def test_agent_uses_stronger_reserve_when_owned_count_is_low():
    module = load_agent_module()
    planet = module.Planet(0, 0, 10.0, 10.0, 1.0, 30, 5)

    early_reserve = module.source_reserve(planet, owned_count=1)
    normal_reserve = module.source_reserve(planet, owned_count=4)

    assert early_reserve > normal_reserve
    assert early_reserve == 20


def test_agent_rejects_sun_crossing_launches():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 20.0, 50.0, 1.0, 100, 5],
            [1, -1, 80.0, 50.0, 2.0, 5, 5],
            [2, -1, 20.0, 70.0, 1.0, 8, 2],
        ]
    )

    moves = module.agent(obs)

    assert moves
    assert moves[0][0] == 0
    assert moves[0][1] > 0.0
    assert moves[0][2] == 9
