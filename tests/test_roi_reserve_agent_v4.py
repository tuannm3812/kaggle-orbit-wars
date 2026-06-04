import importlib.util
import math
from pathlib import Path


AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "roi_reserve_v4" / "main.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("roi_reserve_v4", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def obs_with(planets, fleets=None, player=0, angular_velocity=0.0):
    return {
        "player": player,
        "planets": planets,
        "fleets": fleets or [],
        "angular_velocity": angular_velocity,
        "initial_planets": planets,
        "comet_planet_ids": [],
    }


def test_agent_reinforces_before_incoming_enemy_capture():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 12, 2],
            [1, 0, 14.0, 10.0, 1.0, 80, 5],
            [2, -1, 30.0, 30.0, 1.0, 5, 1],
        ],
        fleets=[
            [100, 1, 0.0, 10.0, 0.0, 9, 30],
        ],
    )

    moves = module.agent(obs)

    assert moves
    source_id, angle, ships = moves[0]
    assert source_id == 1
    assert math.isclose(angle, math.pi, abs_tol=1e-9)
    assert ships >= 2


def test_enemy_capture_budget_includes_expected_production_before_arrival():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 100, 5],
            [1, 1, 35.0, 10.0, 1.0, 10, 5],
        ],
    )

    moves = module.agent(obs)

    assert moves
    source_id, angle, ships = moves[0]
    assert source_id == 0
    assert math.isclose(angle, 0.0)
    assert ships > 11
