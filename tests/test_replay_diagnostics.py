import json

from scripts.replay_diagnostics import summarize_replay


def test_summarize_replay_flags_eliminated_loss(tmp_path):
    replay = {
        "steps": [
            [
                {
                    "observation": {
                        "planets": [
                            [0, 0, 10, 10, 1, 20, 5],
                            [1, 1, 90, 90, 1, 20, 5],
                        ],
                        "fleets": [],
                    },
                    "action": [[0, 0.5, 10]],
                    "reward": 0,
                    "status": "ACTIVE",
                },
                {
                    "observation": {
                        "planets": [
                            [0, 0, 10, 10, 1, 20, 5],
                            [1, 1, 90, 90, 1, 20, 5],
                        ],
                        "fleets": [],
                    },
                    "action": [],
                    "reward": 0,
                    "status": "ACTIVE",
                },
            ],
            [
                {
                    "observation": {
                        "planets": [[1, 1, 90, 90, 1, 200, 5]],
                        "fleets": [],
                    },
                    "action": [],
                    "reward": -1,
                    "status": "DONE",
                },
                {
                    "observation": {
                        "planets": [[1, 1, 90, 90, 1, 200, 5]],
                        "fleets": [],
                    },
                    "action": [],
                    "reward": 1,
                    "status": "DONE",
                },
            ],
        ]
    }
    path = tmp_path / "loss.json"
    path.write_text(json.dumps(replay))

    summary = summarize_replay(path, selected_player=0)

    assert summary.steps == 2
    assert summary.winner == 1
    assert summary.selected_reward == -1
    assert summary.selected_planets == 0
    assert "loss" in summary.weakness_flags
    assert "eliminated" in summary.weakness_flags
    assert "production_gap" in summary.weakness_flags


def test_summarize_replay_counts_actions_and_ships(tmp_path):
    replay = {
        "steps": [
            [
                {
                    "observation": {
                        "planets": [[0, 0, 10, 10, 1, 40, 5]],
                        "fleets": [],
                    },
                    "action": [[0, 0.5, 10], [0, 0.8, 5]],
                    "reward": 0,
                    "status": "ACTIVE",
                }
            ],
            [
                {
                    "observation": {
                        "planets": [[0, 0, 10, 10, 1, 60, 5]],
                        "fleets": [[0, 0, 20, 20, 0.5, 0, 15]],
                    },
                    "action": [],
                    "reward": 1,
                    "status": "DONE",
                }
            ],
        ]
    }
    path = tmp_path / "win.json"
    path.write_text(json.dumps(replay))

    summary = summarize_replay(path, selected_player=0)
    player = summary.players[0]

    assert player.action_count == 2
    assert player.launched_ships == 15
    assert player.score_proxy == 75
    assert summary.weakness_flags == []
