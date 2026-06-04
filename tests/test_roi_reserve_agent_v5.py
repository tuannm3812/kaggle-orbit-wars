import importlib.util
import math
from pathlib import Path


AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "roi_reserve_v5" / "main.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("roi_reserve_v5", AGENT_PATH)
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


def test_source_does_not_launch_if_combined_arrivals_flip_after_spend():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 45, 1],
            [1, -1, 18.0, 10.0, 1.0, 25, 3],
        ],
        fleets=[
            [100, 1, 0.0, 10.0, 0.0, 9, 12],
            [101, 1, 0.0, 10.4, 0.0, 9, 12],
        ],
    )

    moves = module.agent(obs)

    assert moves == []


def test_contested_enemy_target_loses_to_safe_neutral_capture():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 95, 4],
            [1, -1, 18.0, 10.0, 1.0, 9, 2],
            [2, 1, 24.0, 10.0, 1.0, 9, 5],
            [3, 1, 26.0, 10.0, 1.0, 70, 5],
        ],
    )

    moves = module.agent(obs)

    assert moves
    source_id, angle, ships = moves[0]
    assert source_id == 0
    assert math.isclose(angle, 0.0)
    assert ships == 10
