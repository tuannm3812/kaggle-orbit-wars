# 4. Agent Version Log

## 1. Submission State

As of 2026-06-03, the **Kaggle CLI** reports **no submissions** for this account in
Orbit Wars.

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submissions orbit-wars
```

Current public leaderboard reference from the same session:

| Rank reference | Team | Score |
| --- | --- | ---: |
| Top listed team | Isaiah @ Tufa Labs | `1750.5` |

Use this as a rough **public-score orientation** only. Agent competitions move as
new episodes are played.

## 2. Version Table

| Version | Source | Submitted | Public score | Main change | Decision |
| --- | --- | --- | ---: | --- | --- |
| Starter EDA | `kaggle/eda/01_orbit_wars_eda.ipynb` | No | N/A | Official nearest-planet starter run against random for 30 seeds. | Keep as environment and baseline reference. |

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
