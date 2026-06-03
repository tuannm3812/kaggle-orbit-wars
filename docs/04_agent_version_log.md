# 4. Agent Version Log

## 1. Submission State

As of 2026-06-03, account `tuannm3823` has two Orbit Wars submissions.

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submissions orbit-wars
```

Latest submissions:

| File | Kaggle timestamp | Description | Status | Public score |
| --- | --- | --- | --- | --- |
| `submission.tar.gz` | `2026-06-03 09:41:07.643000` | `roi_reserve_v2: orbit-aware aiming, target reservation, stronger reserves` | `SubmissionStatus.COMPLETE` | `423.1` |
| `main.py` | `2026-06-03 08:52:34` | `roi_reserve_v1: ROI target scoring, source reserves, sun-safe paths` | `SubmissionStatus.COMPLETE` | `337.1` |

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
| `roi_reserve_v1` | `kaggle/roi_reserve_v1/02_roi_reserve_agent.ipynb` / `agents/roi_reserve_v1/main.py` | Yes | `337.1` | Production-aware ROI target scoring, source reserve, and sun-path rejection. Kaggle smoke benchmark: 25 wins, 5 losses, 0 errors over 30 seeds vs `random`. | Superseded by v2 smoke benchmark; keep for leaderboard comparison. |
| `roi_reserve_v2` | `kaggle/roi_reserve_v2/03_roi_reserve_agent_v2.ipynb` / `agents/roi_reserve_v2/main.py` | Yes | `423.1` | Adds orbit-aware aiming, per-turn target reservation, and stronger early reserve. Kaggle smoke benchmark: 27 wins, 3 losses, 0 errors over 30 seeds vs `random`. Submitted from notebook output `submission.tar.gz`. | Current champion. Use downloaded episodes when available; use benchmark loss seeds `18`, `24`, and `27` for v3 defense work now. |

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
