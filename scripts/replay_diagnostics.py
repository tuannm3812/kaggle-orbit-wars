"""Summarize Orbit Wars replay JSON files into strategy diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


DEFAULT_PLAYER = 0


@dataclass
class PlayerSnapshot:
    """Final per-player control metrics extracted from one replay."""

    player: int
    reward: Optional[float]
    status: Optional[str]
    planets: int
    production: float
    planet_ships: float
    fleet_ships: float
    action_count: int
    launched_ships: int

    @property
    def score_proxy(self) -> float:
        """Return final ships on planets plus active fleets."""
        return self.planet_ships + self.fleet_ships


@dataclass
class ReplaySummary:
    """Replay-level diagnostics used for strategy review."""

    replay: str
    steps: int
    selected_player: int
    selected_reward: Optional[float]
    selected_status: Optional[str]
    selected_score_proxy: float
    selected_planets: int
    selected_production: float
    winner: Optional[int]
    winner_score_proxy: Optional[float]
    weakness_flags: list[str]
    players: list[PlayerSnapshot]


def read_json(path: Path) -> Any:
    """Read a JSON replay file.

    Args:
        path: Replay JSON path.

    Returns:
        Parsed JSON content.
    """
    with path.open() as f:
        return json.load(f)


def get_value(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from dict-like or object-like values."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def unwrap_observation(agent_state: Any) -> Any:
    """Extract an observation from an agent state."""
    if agent_state is None:
        return {}
    observation = get_value(agent_state, "observation", None)
    return observation if observation is not None else agent_state


def unwrap_action(agent_state: Any) -> Any:
    """Extract an action from an agent state."""
    return get_value(agent_state, "action", None)


def find_steps(payload: Any) -> list:
    """Find the step list inside common Kaggle replay JSON layouts.

    Args:
        payload: Parsed replay JSON.

    Returns:
        Replay step list.

    Raises:
        ValueError: If no step list can be found.
    """
    candidates = [
        payload,
        get_value(payload, "episode", {}),
        get_value(payload, "configuration", {}),
    ]
    for candidate in candidates:
        steps = get_value(candidate, "steps", None)
        if isinstance(steps, list) and steps:
            return steps
    if isinstance(payload, list) and payload:
        return payload
    raise ValueError("Could not find replay steps")


def last_observations(steps: list) -> list[Any]:
    """Return final observations for each player."""
    for step in reversed(steps):
        if isinstance(step, list) and step:
            observations = [unwrap_observation(agent_state) for agent_state in step]
            if any(observations):
                return observations
    return []


def iter_agent_states(steps: Iterable[Any]) -> Iterable[tuple[int, Any]]:
    """Yield `(player_index, state)` pairs from every list-shaped step."""
    for step in steps:
        if not isinstance(step, list):
            continue
        for player, state in enumerate(step):
            yield player, state


def normalize_actions(action: Any) -> list[list[Any]]:
    """Normalize a Kaggle action value to a list of launch actions."""
    if action is None:
        return []
    if isinstance(action, str):
        try:
            action = json.loads(action)
        except json.JSONDecodeError:
            return []
    if not isinstance(action, list):
        return []
    if len(action) == 3 and not isinstance(action[0], list):
        return [action]
    return [move for move in action if isinstance(move, list) and len(move) == 3]


def action_metrics(steps: list) -> dict[int, tuple[int, int]]:
    """Count launch actions and launched ships for each player."""
    metrics: dict[int, list[int]] = {}
    for player, state in iter_agent_states(steps):
        moves = normalize_actions(unwrap_action(state))
        if not moves:
            continue
        metrics.setdefault(player, [0, 0])
        metrics[player][0] += len(moves)
        metrics[player][1] += sum(safe_int(move[2]) for move in moves)
    return {player: (values[0], values[1]) for player, values in metrics.items()}


def safe_float(value: Any) -> float:
    """Convert a value to float, returning 0.0 on failure."""
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    """Convert a value to int, returning 0 on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def planet_rows(observation: Any) -> list:
    """Read planet rows from an observation."""
    rows = get_value(observation, "planets", []) or []
    return rows if isinstance(rows, list) else []


def fleet_rows(observation: Any) -> list:
    """Read fleet rows from an observation."""
    rows = get_value(observation, "fleets", []) or []
    return rows if isinstance(rows, list) else []


def reward_for(agent_state: Any) -> Optional[float]:
    """Read reward from one final agent state."""
    reward = get_value(agent_state, "reward", None)
    return None if reward is None else safe_float(reward)


def status_for(agent_state: Any) -> Optional[str]:
    """Read status from one final agent state."""
    status = get_value(agent_state, "status", None)
    return None if status is None else str(status)


def player_snapshot(
    player: int,
    final_state: Any,
    action_count: int,
    launched_ships: int,
) -> PlayerSnapshot:
    """Build final control metrics for one player."""
    observation = unwrap_observation(final_state)
    planets = planet_rows(observation)
    fleets = fleet_rows(observation)
    owned_planets = [row for row in planets if len(row) > 5 and safe_int(row[1]) == player]
    owned_fleets = [row for row in fleets if len(row) > 6 and safe_int(row[1]) == player]
    return PlayerSnapshot(
        player=player,
        reward=reward_for(final_state),
        status=status_for(final_state),
        planets=len(owned_planets),
        production=sum(safe_float(row[6]) for row in owned_planets),
        planet_ships=sum(safe_float(row[5]) for row in owned_planets),
        fleet_ships=sum(safe_float(row[6]) for row in owned_fleets),
        action_count=action_count,
        launched_ships=launched_ships,
    )


def choose_winner(players: list[PlayerSnapshot]) -> Optional[int]:
    """Choose the likely winner from rewards, falling back to score proxy."""
    if not players:
        return None
    reward_winners = [p for p in players if p.reward is not None and p.reward > 0]
    if reward_winners:
        return max(reward_winners, key=lambda p: p.reward or 0.0).player
    return max(players, key=lambda p: p.score_proxy).player


def weakness_flags(selected: PlayerSnapshot, players: list[PlayerSnapshot]) -> list[str]:
    """Infer actionable weakness flags from final replay metrics."""
    flags = []
    winner = choose_winner(players)
    winner_snapshot = next((p for p in players if p.player == winner), None)
    if selected.reward is not None and selected.reward <= 0:
        flags.append("loss")
    if selected.planets == 0:
        flags.append("eliminated")
    if selected.production == 0:
        flags.append("no_final_production")
    if winner_snapshot and selected.production < winner_snapshot.production * 0.5:
        flags.append("production_gap")
    if winner_snapshot and selected.score_proxy < winner_snapshot.score_proxy * 0.5:
        flags.append("ship_count_gap")
    if selected.action_count == 0:
        flags.append("no_recorded_actions")
    return flags


def summarize_replay(path: Path, selected_player: int) -> ReplaySummary:
    """Summarize one replay file."""
    payload = read_json(path)
    steps = find_steps(payload)
    final_step = steps[-1] if steps and isinstance(steps[-1], list) else []
    actions = action_metrics(steps)
    players = [
        player_snapshot(
            player=player,
            final_state=state,
            action_count=actions.get(player, (0, 0))[0],
            launched_ships=actions.get(player, (0, 0))[1],
        )
        for player, state in enumerate(final_step)
    ]
    selected = next(
        (player for player in players if player.player == selected_player),
        PlayerSnapshot(selected_player, None, None, 0, 0.0, 0.0, 0.0, 0, 0),
    )
    winner = choose_winner(players)
    winner_snapshot = next((p for p in players if p.player == winner), None)
    return ReplaySummary(
        replay=str(path),
        steps=len(steps),
        selected_player=selected_player,
        selected_reward=selected.reward,
        selected_status=selected.status,
        selected_score_proxy=selected.score_proxy,
        selected_planets=selected.planets,
        selected_production=selected.production,
        winner=winner,
        winner_score_proxy=winner_snapshot.score_proxy if winner_snapshot else None,
        weakness_flags=weakness_flags(selected, players),
        players=players,
    )


def summary_rows(summaries: Iterable[ReplaySummary]) -> list[dict[str, Any]]:
    """Convert replay summaries to CSV rows."""
    rows = []
    for summary in summaries:
        rows.append(
            {
                "replay": summary.replay,
                "steps": summary.steps,
                "selected_player": summary.selected_player,
                "selected_reward": summary.selected_reward,
                "selected_status": summary.selected_status,
                "selected_score_proxy": summary.selected_score_proxy,
                "selected_planets": summary.selected_planets,
                "selected_production": summary.selected_production,
                "winner": summary.winner,
                "winner_score_proxy": summary.winner_score_proxy,
                "weakness_flags": "|".join(summary.weakness_flags),
            }
        )
    return rows


def player_rows(summaries: Iterable[ReplaySummary]) -> list[dict[str, Any]]:
    """Convert player snapshots to CSV rows."""
    rows = []
    for summary in summaries:
        for player in summary.players:
            rows.append(
                {
                    "replay": summary.replay,
                    "player": player.player,
                    "reward": player.reward,
                    "status": player.status,
                    "planets": player.planets,
                    "production": player.production,
                    "score_proxy": player.score_proxy,
                    "action_count": player.action_count,
                    "launched_ships": player.launched_ships,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write dictionaries to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["empty"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summaries: list[ReplaySummary]) -> None:
    """Write a short Markdown strategy handoff."""
    lines = ["# Replay Diagnostics", ""]
    if not summaries:
        lines.append("No replay files were parsed.")
    for summary in summaries:
        lines.extend(
            [
                f"## {Path(summary.replay).name}",
                "",
                f"- Steps: `{summary.steps}`",
                f"- Selected player: `{summary.selected_player}`",
                f"- Reward: `{summary.selected_reward}`",
                f"- Final planets: `{summary.selected_planets}`",
                f"- Final production: `{summary.selected_production:.1f}`",
                f"- Score proxy: `{summary.selected_score_proxy:.1f}`",
                f"- Winner: `{summary.winner}`",
                f"- Weakness flags: `{', '.join(summary.weakness_flags) or 'none'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Strategy Review Checklist",
            "",
            "- Prioritize losses with `production_gap`, `ship_count_gap`, or `eliminated`.",
            "- Compare action counts and launched ships against the winner.",
            "- Curate only the decision-worthy lessons into `docs/05_next_steps.md`.",
            "- Create a new notebook only when replay work requires substantial new code or visuals.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replays", nargs="+", type=Path, help="Replay JSON files to summarize.")
    parser.add_argument("--player", type=int, default=DEFAULT_PLAYER, help="Player id to analyze.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs/replay_diagnostics"),
        help="Directory for CSV and Markdown outputs.",
    )
    return parser.parse_args()


def main() -> None:
    """Run replay diagnostics from the command line."""
    args = parse_args()
    summaries = [summarize_replay(path, args.player) for path in args.replays]
    write_csv(args.out_dir / "replay_summary.csv", summary_rows(summaries))
    write_csv(args.out_dir / "player_summary.csv", player_rows(summaries))
    write_markdown(args.out_dir / "replay_findings.md", summaries)
    print(f"wrote: {args.out_dir / 'replay_summary.csv'}")
    print(f"wrote: {args.out_dir / 'player_summary.csv'}")
    print(f"wrote: {args.out_dir / 'replay_findings.md'}")


if __name__ == "__main__":
    main()
