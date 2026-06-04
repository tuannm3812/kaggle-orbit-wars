"""Analyze Orbit Wars replay outcomes across submitted agents."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


SUBMISSIONS = {
    "roi_reserve_v2": 53322680,
    "roi_reserve_v3": 53344107,
    "roi_reserve_v4": 53349976,
    "roi_reserve_v5": 53353907,
}


@dataclass
class ActionDetail:
    """Reconstructed launch action details from one replay step."""

    step: int
    source: int
    ships: int
    target: Optional[int]
    target_owner: Optional[int]
    target_ships: Optional[float]
    target_production: Optional[float]
    distance: Optional[float]
    angular_error: Optional[float]


@dataclass
class Outcome:
    """One replay's outcome and strategic diagnostics."""

    label: str
    submission_id: int
    episode_id: int
    reward: Optional[float]
    result: str
    players: int
    player: int
    opponent_names: str
    turns: int
    home_production: float
    first_action_step: Optional[int]
    first_capture_step: Optional[int]
    peak_planets: int
    peak_production: float
    final_planets: int
    final_production: float
    final_ships: float
    opponent_final_planets: int
    opponent_final_production: float
    opponent_final_ships: float
    production_gap: float
    ship_gap: float
    action_count: int
    launched_ships: int
    far_action_share: float
    enemy_target_share: float
    first_action_target_owner: Optional[int]
    first_action_distance: Optional[float]
    first_action_target_production: Optional[float]
    first_action_target_ships: Optional[float]
    first_below_half_production_step: Optional[int]
    first_below_half_ships_step: Optional[int]
    diagnosis: str
    replay: str


def read_json(path: Path) -> Any:
    """Read a JSON file."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def safe_float(value: Any) -> float:
    """Convert a scalar to float, returning zero for missing values."""
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    """Convert a scalar to int, returning zero for missing values."""
    try:
        if value is None:
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_actions(action: Any) -> list[list[Any]]:
    """Normalize a Kaggle action value to launch-action rows."""
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


def observation_at(step_state: Any) -> dict[str, Any]:
    """Return an observation dict from a replay player state."""
    if not isinstance(step_state, dict):
        return {}
    observation = step_state.get("observation")
    return observation if isinstance(observation, dict) else {}


def action_at(step_state: Any) -> list[list[Any]]:
    """Return normalized actions from a replay player state."""
    if not isinstance(step_state, dict):
        return []
    return normalize_actions(step_state.get("action"))


def planet_rows(observation: dict[str, Any]) -> list[list[Any]]:
    """Return planet rows from an observation."""
    rows = observation.get("planets", [])
    return rows if isinstance(rows, list) else []


def fleet_rows(observation: dict[str, Any]) -> list[list[Any]]:
    """Return fleet rows from an observation."""
    rows = observation.get("fleets", [])
    return rows if isinstance(rows, list) else []


def replay_steps(payload: dict[str, Any]) -> list[list[Any]]:
    """Return replay steps from a Kaggle replay payload."""
    steps = payload.get("steps", [])
    return steps if isinstance(steps, list) else []


def owner_metrics(observation: dict[str, Any], owner: int) -> tuple[int, float, float]:
    """Return planet count, production, and ships controlled by an owner."""
    planets = [
        row
        for row in planet_rows(observation)
        if len(row) >= 7 and safe_int(row[1]) == owner
    ]
    fleets = [
        row
        for row in fleet_rows(observation)
        if len(row) >= 7 and safe_int(row[1]) == owner
    ]
    production = sum(safe_float(row[6]) for row in planets)
    planet_ships = sum(safe_float(row[5]) for row in planets)
    fleet_ships = sum(safe_float(row[6]) for row in fleets)
    return len(planets), production, planet_ships + fleet_ships


def owned_players(observation: dict[str, Any]) -> list[int]:
    """Return non-neutral owners visible in the observation."""
    owners = {
        safe_int(row[1])
        for row in planet_rows(observation)
        if len(row) >= 2 and safe_int(row[1]) >= 0
    }
    owners.update(
        safe_int(row[1])
        for row in fleet_rows(observation)
        if len(row) >= 2 and safe_int(row[1]) >= 0
    )
    return sorted(owners)


def angular_delta(lhs: float, rhs: float) -> float:
    """Return absolute angular difference in radians."""
    diff = (lhs - rhs + math.pi) % (2 * math.pi) - math.pi
    return abs(diff)


def find_target(
    planets: list[list[Any]],
    source_id: int,
    angle: float,
    max_error: float = 0.65,
) -> tuple[Optional[list[Any]], Optional[float], Optional[float]]:
    """Estimate the intended target from source, angle, and current positions."""
    source = next((row for row in planets if len(row) >= 4 and safe_int(row[0]) == source_id), None)
    if source is None:
        return None, None, None
    sx, sy = safe_float(source[2]), safe_float(source[3])
    best: tuple[float, float, list[Any], float] | None = None
    for target in planets:
        if len(target) < 7 or safe_int(target[0]) == source_id:
            continue
        dx = safe_float(target[2]) - sx
        dy = safe_float(target[3]) - sy
        distance = math.hypot(dx, dy)
        bearing = math.atan2(dy, dx)
        error = angular_delta(angle, bearing)
        score = error * 80.0 + distance
        if best is None or score < best[0]:
            best = (score, distance, target, error)
    if best is None or best[3] > max_error:
        return None, None, None
    return best[2], best[1], best[3]


def player_from_metadata(episode: dict[str, Any], submission_id: int) -> Optional[int]:
    """Infer our player index from episode metadata."""
    for position, agent in enumerate(episode.get("agents", [])):
        if agent.get("submissionId") == submission_id:
            return safe_int(agent.get("index", position))
    return None


def reward_from_metadata(episode: dict[str, Any], submission_id: int) -> Optional[float]:
    """Read our reward from episode metadata."""
    for agent in episode.get("agents", []):
        if agent.get("submissionId") == submission_id:
            return safe_float(agent.get("reward"))
    return None


def episode_lookup(path: Path, submission_id: int) -> dict[int, dict[str, Any]]:
    """Load episode metadata keyed by episode id."""
    payload = read_json(path)
    episodes = payload.get("episodes", [])
    return {safe_int(episode.get("id")): episode for episode in episodes}


def infer_episode_id(path: Path, payload: dict[str, Any]) -> int:
    """Infer an episode id from replay metadata or filename."""
    info = payload.get("info", {})
    episode_id = safe_int(info.get("EpisodeId"))
    if episode_id:
        return episode_id
    stem_parts = path.stem.split("_")
    for part in stem_parts:
        if part.isdigit():
            return int(part)
    return 0


def opponent_names(payload: dict[str, Any], player: int) -> str:
    """Return readable opponent names from replay info."""
    names = payload.get("info", {}).get("TeamNames") or []
    if not isinstance(names, list):
        return ""
    return "|".join(str(name) for index, name in enumerate(names) if index != player)


def action_details(steps: list[list[Any]], player: int) -> list[ActionDetail]:
    """Reconstruct coarse target diagnostics for all launch actions."""
    details: list[ActionDetail] = []
    for step_index, step in enumerate(steps):
        if not isinstance(step, list) or player >= len(step):
            continue
        actions = action_at(step[player])
        if not actions:
            continue
        observation = observation_at(step[player])
        planets = planet_rows(observation)
        for move in actions:
            source = safe_int(move[0])
            angle = safe_float(move[1])
            ships = safe_int(move[2])
            target, distance, error = find_target(planets, source, angle)
            details.append(
                ActionDetail(
                    step=step_index,
                    source=source,
                    ships=ships,
                    target=safe_int(target[0]) if target else None,
                    target_owner=safe_int(target[1]) if target else None,
                    target_ships=safe_float(target[5]) if target else None,
                    target_production=safe_float(target[6]) if target else None,
                    distance=distance,
                    angular_error=error,
                )
            )
    return details


def diagnose(outcome: Outcome) -> list[str]:
    """Assign compact strategy tags to an outcome."""
    tags = []
    if outcome.result == "win":
        if outcome.first_capture_step is not None and outcome.first_capture_step <= 35:
            tags.append("fast_opening")
        if outcome.production_gap >= 1.0:
            tags.append("production_lead")
        if outcome.ship_gap >= 1.0:
            tags.append("ship_lead")
        if outcome.final_planets == 0:
            tags.append("reward_win_but_eliminated")
        return tags or ["survived_better"]

    if outcome.final_planets == 0:
        tags.append("eliminated")
    if outcome.first_action_step is None:
        tags.append("no_launches")
    elif outcome.first_action_step > 12:
        tags.append("slow_first_launch")
    if outcome.first_capture_step is None or outcome.first_capture_step > 45:
        tags.append("slow_or_no_first_capture")
    if outcome.first_action_distance is not None and outcome.first_action_distance > 30:
        tags.append("far_opening_target")
    if outcome.production_gap < 0.5:
        tags.append("production_gap")
    if outcome.ship_gap < 0.5:
        tags.append("ship_gap")
    if outcome.peak_planets >= max(4, outcome.final_planets + 4):
        tags.append("lost_midgame_control")
    if outcome.enemy_target_share > 0.4:
        tags.append("enemy_target_heavy")
    if outcome.players > 2:
        tags.append("multiplayer_pressure")
    return tags or ["marginal_loss"]


def summarize_replay(
    label: str,
    submission_id: int,
    replay_path: Path,
    metadata: dict[int, dict[str, Any]],
) -> Outcome:
    """Build one replay outcome summary."""
    payload = read_json(replay_path)
    steps = replay_steps(payload)
    episode_id = infer_episode_id(replay_path, payload)
    episode = metadata.get(episode_id, {})
    player = player_from_metadata(episode, submission_id)
    if player is None:
        player = safe_int(replay_path.stem.split("_player")[-1].split("_")[0])
    reward = reward_from_metadata(episode, submission_id)
    if reward is None and payload.get("rewards") and player < len(payload["rewards"]):
        reward = safe_float(payload["rewards"][player])

    player_series = []
    opponent_series = []
    initial_planets = 0
    initial_production = 0.0
    for step in steps:
        if not isinstance(step, list) or player >= len(step):
            continue
        observation = observation_at(step[player])
        if not observation:
            continue
        players = [owner for owner in owned_players(observation) if owner != player]
        own = owner_metrics(observation, player)
        opponent_metrics = [owner_metrics(observation, owner) for owner in players]
        opponent = max(opponent_metrics, key=lambda values: values[2], default=(0, 0.0, 0.0))
        player_series.append(own)
        opponent_series.append(opponent)
        if len(player_series) == 1:
            initial_planets = own[0]
            initial_production = own[1]

    details = action_details(steps, player)
    first_action = details[0] if details else None
    first_capture_step = None
    first_below_half_production_step = None
    first_below_half_ships_step = None
    for index, (own, opponent) in enumerate(zip(player_series, opponent_series)):
        if first_capture_step is None and own[0] > initial_planets:
            first_capture_step = index
        if (
            first_below_half_production_step is None
            and opponent[1] > 0
            and own[1] < opponent[1] * 0.5
        ):
            first_below_half_production_step = index
        if (
            first_below_half_ships_step is None
            and opponent[2] > 0
            and own[2] < opponent[2] * 0.5
        ):
            first_below_half_ships_step = index

    final = player_series[-1] if player_series else (0, 0.0, 0.0)
    opponent_final = opponent_series[-1] if opponent_series else (0, 0.0, 0.0)
    peak_planets = max((values[0] for values in player_series), default=0)
    peak_production = max((values[1] for values in player_series), default=0.0)
    launched_ships = sum(detail.ships for detail in details)
    reconstructed_targets = [detail for detail in details if detail.target is not None]
    far_actions = [detail for detail in reconstructed_targets if (detail.distance or 0.0) > 30.0]
    enemy_targets = [detail for detail in reconstructed_targets if detail.target_owner not in (-1, player)]
    result = "win" if reward is not None and reward > 0 else "loss"
    outcome = Outcome(
        label=label,
        submission_id=submission_id,
        episode_id=episode_id,
        reward=reward,
        result=result,
        players=len(payload.get("rewards", [])),
        player=player,
        opponent_names=opponent_names(payload, player),
        turns=len(steps),
        home_production=initial_production,
        first_action_step=first_action.step if first_action else None,
        first_capture_step=first_capture_step,
        peak_planets=peak_planets,
        peak_production=peak_production,
        final_planets=final[0],
        final_production=final[1],
        final_ships=final[2],
        opponent_final_planets=opponent_final[0],
        opponent_final_production=opponent_final[1],
        opponent_final_ships=opponent_final[2],
        production_gap=final[1] / opponent_final[1] if opponent_final[1] else final[1],
        ship_gap=final[2] / opponent_final[2] if opponent_final[2] else final[2],
        action_count=len(details),
        launched_ships=launched_ships,
        far_action_share=len(far_actions) / len(reconstructed_targets) if reconstructed_targets else 0.0,
        enemy_target_share=len(enemy_targets) / len(reconstructed_targets) if reconstructed_targets else 0.0,
        first_action_target_owner=first_action.target_owner if first_action else None,
        first_action_distance=first_action.distance if first_action else None,
        first_action_target_production=first_action.target_production if first_action else None,
        first_action_target_ships=first_action.target_ships if first_action else None,
        first_below_half_production_step=first_below_half_production_step,
        first_below_half_ships_step=first_below_half_ships_step,
        diagnosis="",
        replay=str(replay_path),
    )
    outcome.diagnosis = "|".join(diagnose(outcome))
    return outcome


def mean(values: Iterable[Optional[float]]) -> float:
    """Return the arithmetic mean of present values."""
    present = [safe_float(value) for value in values if value is not None]
    return sum(present) / len(present) if present else 0.0


def median(values: Iterable[Optional[float]]) -> float:
    """Return the median of present values."""
    present = sorted(safe_float(value) for value in values if value is not None)
    if not present:
        return 0.0
    middle = len(present) // 2
    if len(present) % 2:
        return present[middle]
    return (present[middle - 1] + present[middle]) / 2.0


def to_row(outcome: Outcome) -> dict[str, Any]:
    """Convert an outcome to a CSV row."""
    return {
        field: getattr(outcome, field)
        for field in Outcome.__dataclass_fields__
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write rows to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["empty"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def line_for_value(value: Optional[float], digits: int = 1) -> str:
    """Format an optional number for Markdown."""
    if value is None:
        return "`None`"
    return f"`{value:.{digits}f}`"


def write_markdown(path: Path, outcomes: list[Outcome]) -> None:
    """Write a concise replay strategy report."""
    lines = [
        "# Replay Outcome Analysis",
        "",
        "Raw replay files stay in ignored local folders under `replays/`. This report",
        "summarizes the current public replay evidence for submitted agents.",
        "",
        "## Score Context",
        "",
        "| Agent | Public score | Reviewed replays | Wins | Losses |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    scores = {
        "roi_reserve_v2": "438.3/411.9",
        "roi_reserve_v3": "509.9",
        "roi_reserve_v4": "471.9",
        "roi_reserve_v5": "518.4",
    }
    for label in sorted({outcome.label for outcome in outcomes}):
        subset = [outcome for outcome in outcomes if outcome.label == label]
        wins = sum(outcome.result == "win" for outcome in subset)
        losses = len(subset) - wins
        lines.append(f"| `{label}` | `{scores.get(label, '')}` | {len(subset)} | {wins} | {losses} |")

    lines.extend(["", "## Aggregate Outcome Patterns", ""])
    for label in sorted({outcome.label for outcome in outcomes}):
        subset = [outcome for outcome in outcomes if outcome.label == label]
        losses = [outcome for outcome in subset if outcome.result == "loss"]
        wins = [outcome for outcome in subset if outcome.result == "win"]
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Win rate in downloaded public replays: `{len(wins)}/{len(subset)}`.",
                f"- Median first capture: wins {line_for_value(median(o.first_capture_step for o in wins), 0)}, losses {line_for_value(median(o.first_capture_step for o in losses), 0)}.",
                f"- Median final production gap: wins `{median(o.production_gap for o in wins):.2f}x`, losses `{median(o.production_gap for o in losses):.2f}x`.",
                f"- Median final ship gap: wins `{median(o.ship_gap for o in wins):.2f}x`, losses `{median(o.ship_gap for o in losses):.2f}x`.",
                f"- Loss far-action share: `{mean(o.far_action_share for o in losses) * 100:.1f}%`.",
                f"- Loss enemy-target share: `{mean(o.enemy_target_share for o in losses) * 100:.1f}%`.",
                "",
            ]
        )

    lines.extend(
        [
            "## Why We Win",
            "",
            "Wins usually come from **early survival into a production lead**. The replay",
            "pattern is not a single decisive attack; it is faster neutral capture, enough",
            "reserve to avoid immediate elimination, then compounding **planet production**.",
            "",
            "| Agent | Episode | Opponents | First capture | Final production gap | Final ship gap | Tags |",
            "| --- | ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    top_wins = sorted(
        [outcome for outcome in outcomes if outcome.result == "win"],
        key=lambda outcome: (outcome.production_gap, outcome.ship_gap),
        reverse=True,
    )[:12]
    for outcome in top_wins:
        capture = "" if outcome.first_capture_step is None else outcome.first_capture_step
        lines.append(
            f"| `{outcome.label}` | `{outcome.episode_id}` | {outcome.opponent_names} | {capture} | "
            f"`{outcome.production_gap:.2f}x` | `{outcome.ship_gap:.2f}x` | `{outcome.diagnosis}` |"
        )

    lines.extend(
        [
            "",
            "## Why We Lose",
            "",
            "Losses mostly show **economic collapse before endgame tactics matter**. The",
            "common failure is falling behind in production or ships by the midgame, then",
            "losing control even after many launches. Multiplayer episodes are especially",
            "harsh because a local-only policy does not model cross-player pressure.",
            "",
            "| Agent | Episode | Opponents | First action | First capture | Peak planets | Final planets | Production gap | Ship gap | Tags |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    representative_losses = sorted(
        [outcome for outcome in outcomes if outcome.result == "loss"],
        key=lambda outcome: (outcome.final_planets, outcome.production_gap, outcome.ship_gap),
    )[:18]
    for outcome in representative_losses:
        first_action = "" if outcome.first_action_step is None else outcome.first_action_step
        first_capture = "" if outcome.first_capture_step is None else outcome.first_capture_step
        lines.append(
            f"| `{outcome.label}` | `{outcome.episode_id}` | {outcome.opponent_names} | "
            f"{first_action} | {first_capture} | {outcome.peak_planets} | {outcome.final_planets} | "
            f"`{outcome.production_gap:.2f}x` | `{outcome.ship_gap:.2f}x` | `{outcome.diagnosis}` |"
        )

    lines.extend(
        [
            "",
            "## Strategy Implications",
            "",
            "1. Keep `roi_reserve_v3` as the active baseline; v4's current public replay set",
            "   does not justify promotion because its score is lower and losses still show",
            "   production and ship gaps.",
            "2. The next model change should improve **combat valuation**, not only opening",
            "   calibration. We need to estimate enemy arrivals, target ownership at impact,",
            "   and whether a source planet remains safe after launching.",
            "3. Add an explicit **midgame defense mode**: reinforce high-production owned",
            "   planets under threat, stop launching from threatened sources, and avoid",
            "   sending small attacks into enemy production unless the arrival window is",
            "   favorable.",
            "4. Treat **far neutral captures** as conditional. They are acceptable only when",
            "   nearby production is already secured or the target's production/ship payoff",
            "   survives travel-time discounting.",
            "5. For four-player matches, reduce exposed expansion and prefer defensible",
            "   clusters; the replay losses show local ROI alone does not handle third-party",
            "   pressure.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def collect_outcomes(replay_root: Path) -> list[Outcome]:
    """Collect outcomes for all configured submissions present on disk."""
    outcomes = []
    for label, submission_id in SUBMISSIONS.items():
        directory = replay_root / label
        metadata_path = directory / f"episodes_{submission_id}.json"
        if not metadata_path.exists():
            metadata_path = directory / f"episodes_{submission_id}_latest.json"
        if not metadata_path.exists():
            continue
        metadata = episode_lookup(metadata_path, submission_id)
        for replay_path in sorted(directory.glob("episode_*.json")):
            outcomes.append(summarize_replay(label, submission_id, replay_path, metadata))
    return outcomes


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-root", type=Path, default=Path("replays"))
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/replay_outcome_analysis"))
    return parser.parse_args()


def main() -> None:
    """Run replay outcome analysis."""
    args = parse_args()
    outcomes = collect_outcomes(args.replay_root)
    rows = [to_row(outcome) for outcome in outcomes]
    write_csv(args.out_dir / "replay_outcomes.csv", rows)
    write_markdown(args.out_dir / "replay_outcome_analysis.md", outcomes)
    print(f"wrote: {args.out_dir / 'replay_outcomes.csv'}")
    print(f"wrote: {args.out_dir / 'replay_outcome_analysis.md'}")


if __name__ == "__main__":
    main()
