# 4. Agent Version Log

## 1. Submission State

As of 2026-06-04, account `tuannm3823` has five Orbit Wars submissions.

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submissions orbit-wars
```

Latest submissions:

| File | Kaggle timestamp | Description | Status | Public score |
| --- | --- | --- | --- | --- |
| `submission.tar.gz` | `2026-06-04 05:09:23` | `roi_reserve_v4: timed reinforcement and production-aware capture cost` | `SubmissionStatus.COMPLETE` | `529.3` |
| `submission.tar.gz` | `2026-06-04 00:22:31.283000` | `roi_reserve_v3: tempo reserve, local expansion, incoming-threat hold` | `SubmissionStatus.COMPLETE` | `505.8` |
| `submission.tar.gz` | `2026-06-03 22:25:31` | `roi_reserve_v2: consolidated submission notebook, 29/30 smoke` | `SubmissionStatus.COMPLETE` | `411.9` |
| `submission.tar.gz` | `2026-06-03 09:41:07.643000` | `roi_reserve_v2: orbit-aware aiming, target reservation, stronger reserves` | `SubmissionStatus.COMPLETE` | `438.3` |
| `main.py` | `2026-06-03 08:52:34` | `roi_reserve_v1: ROI target scoring, source reserves, sun-safe paths` | `SubmissionStatus.COMPLETE` | `382.5` |

Current public leaderboard reference from the same session:

| Rank reference | Team | Score |
| --- | --- | ---: |
| Top listed team | Isaiah @ Tufa Labs | `1785.9` |

Use this as a rough **public-score orientation** only. Agent competitions move as
new episodes are played.

## 2. Version Table

| Version | Source | Submitted | Public score | Main change | Decision |
| --- | --- | --- | ---: | --- | --- |
| Starter EDA | `kaggle/eda/01_orbit_wars_eda.ipynb` | No | N/A | Official nearest-planet starter run against random for 30 seeds. | Keep as environment and baseline reference. |
| `roi_reserve_v1` | `kaggle/archive/roi_reserve_v1/02_roi_reserve_agent.ipynb` / `agents/roi_reserve_v1/main.py` | Yes | `382.5` | Production-aware ROI target scoring, source reserve, and sun-path rejection. Kaggle smoke benchmark: 25 wins, 5 losses, 0 errors over 30 seeds vs `random`. | Superseded by v2 smoke benchmark; keep for leaderboard comparison. |
| `roi_reserve_v2` | `notebooks/02_agent_submission.ipynb` / `kaggle/submission/02_agent_submission.ipynb` / `agents/roi_reserve_v2/main.py` | Yes | `438.3` | Adds orbit-aware aiming, per-turn target reservation, and stronger early reserve. Best Kaggle smoke benchmark: 29 wins, 1 loss, 0 errors over 30 seeds vs `random`. | Superseded by v3 public score; keep as rollback because smoke performance was slightly stronger against `random`. |
| `roi_reserve_v3` | `notebooks/02_agent_submission.ipynb` / `kaggle/submission/02_agent_submission.ipynb` / `agents/roi_reserve_v3/main.py` | Yes | `505.8` | Adds replay-driven opening tempo reserve, early local-neutral preference, travel-time filtering, and incoming-threat launch holds. Kaggle smoke benchmark: 28 wins, 2 losses, 0 errors over 30 seeds vs `random`. | Submitted challenger. It dropped from the `600.0` starting score after early public games, so replay review is required before promoting or extending it. |
| `roi_reserve_v4` | `notebooks/02_agent_submission.ipynb` / `kaggle/submission/02_agent_submission.ipynb` / `agents/roi_reserve_v4/main.py` | Yes | `529.3` | Adds Proto-inspired timed reinforcement and enemy-production capture cost. Kaggle smoke benchmark: 29 wins, 1 loss, 0 errors over 30 seeds vs `random`. | Current leading challenger by observed public score, but it still dropped from the `600.0` starting score. Review replays before adding more complexity. |

Important scoring note: Orbit Wars public scores behave like an Elo-style
rating. A fresh submission can appear at `600.0` before enough games are played.
Do not treat `600.0` as a performance gain by itself; score movement after wins
and losses plus replay evidence is the meaningful signal. v3 moved downward
from `600.0` to `505.8`, which means the public games exposed losses despite
the smoke benchmark passing.

## 3. Logging Rules

Every meaningful **agent candidate** should record:

- version name;
- notebook or source path;
- whether it was submitted;
- public score and timestamp when available;
- **local/Kaggle simulation result**;
- **replay lesson** from at least one win and one loss when available;
- decision: keep, revise, rollback, or archive.

## 4. Candidate Names

Use descriptive, stable names:

- `starter_nearest_v1`
- `roi_static_expansion_v1`
- `roi_reserve_v1`
- `orbit_aware_targeting_v1`
- `sun_safe_roi_v1`
- `defense_reinforce_v1`
- `comet_roi_v1`
