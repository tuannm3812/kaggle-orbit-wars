import importlib.util
import math
from pathlib import Path


AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "roi_reserve_v3" / "main.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("roi_reserve_v3", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def obs_with(planets, fleets=None, player=0, angular_velocity=0.03):
    return {
        "player": player,
        "planets": planets,
        "fleets": fleets or [],
        "angular_velocity": angular_velocity,
        "initial_planets": planets,
        "comet_planet_ids": [],
    }


def test_low_production_home_expands_before_twenty_ship_reserve():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 18, 1],
            [1, -1, 20.0, 10.0, 1.0, 8, 1],
        ]
    )

    moves = module.agent(obs)

    assert moves == [[0, 0.0, 9]]


def test_opening_prefers_near_neutral_over_far_high_roi_target():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 55, 2],
            [1, -1, 18.0, 10.0, 1.0, 4, 1],
            [2, -1, 62.0, 10.0, 2.0, 5, 5],
        ],
        angular_velocity=0.0,
    )

    moves = module.agent(obs)

    assert moves
    source_id, angle, ships = moves[0]
    assert source_id == 0
    assert math.isclose(angle, 0.0)
    assert ships == 5


def test_threatened_planet_does_not_launch():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 60, 5],
            [1, -1, 18.0, 10.0, 1.0, 4, 1],
        ],
        fleets=[
            [100, 1, 0.0, 10.0, 0.0, 9, 35],
        ],
        angular_velocity=0.0,
    )

    moves = module.agent(obs)

    assert moves == []
