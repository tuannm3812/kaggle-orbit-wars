import importlib.util
from pathlib import Path


AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "roi_reserve_v1" / "main.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("roi_reserve_v1", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def obs_with(planets, player=0):
    return {
        "player": player,
        "planets": planets,
        "fleets": [],
        "angular_velocity": 0.03,
        "initial_planets": planets,
        "comet_planet_ids": [],
    }


def test_agent_preserves_source_reserve():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 20, 5],
            [1, -1, 12.0, 10.0, 1.0, 8, 1],
        ]
    )

    moves = module.agent(obs)

    assert moves == []


def test_agent_prefers_higher_roi_target_over_nearest_target():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 80, 5],
            [1, -1, 13.0, 10.0, 1.0, 12, 1],
            [2, -1, 24.0, 10.0, 2.0, 10, 5],
        ]
    )

    moves = module.agent(obs)

    assert moves
    assert moves[0][0] == 0
    assert moves[0][2] == 11
    assert moves[0][1] == 0.0


def test_agent_rejects_sun_crossing_launches():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 20.0, 50.0, 1.0, 90, 5],
            [1, -1, 80.0, 50.0, 2.0, 5, 5],
            [2, -1, 20.0, 70.0, 1.0, 8, 2],
        ]
    )

    moves = module.agent(obs)

    assert moves
    assert moves[0][0] == 0
    assert moves[0][1] > 0.0
    assert moves[0][2] == 9


def test_agent_returns_plain_action_values():
    module = load_agent_module()
    obs = obs_with(
        [
            [0, 0, 10.0, 10.0, 1.0, 80, 5],
            [1, -1, 20.0, 20.0, 1.0, 10, 3],
        ]
    )

    moves = module.agent(obs)

    assert isinstance(moves, list)
    assert moves
    source_id, angle, ships = moves[0]
    assert isinstance(source_id, int)
    assert isinstance(angle, float)
    assert isinstance(ships, int)
