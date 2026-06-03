# 2. EDA Plan

## Goal

Orbit Wars has no tabular train/test dataset. **EDA** means **environment exploration**, **map-seed profiling**, starter-agent behavior analysis, replay/log analysis, and leaderboard tracking.

## Notebook 01: Rules And Environment EDA

Path: `notebooks/01_orbit_wars_eda.ipynb`

Kaggle path: `kaggle/eda/01_orbit_wars_eda.ipynb`

Main questions:

1. Does the **Kaggle runtime** expose `orbit_wars` through `kaggle_environments.make`?
2. What configuration does the runtime report?
3. Across seeds, how many planets spawn and what is the production/garrison distribution?
4. How many planets are static versus orbiting?
5. How often does the starter agent beat random?
6. What map features correlate with starter wins and losses?

Expected outputs:

| Output | Meaning |
| --- | --- |
| `eda_environment_info.json` | Runtime, config, and import status. |
| `eda_seed_summary.csv` | One row per simulated seed. |
| `eda_planets_by_seed.csv` | Planet-level initial map profile. |
| `eda_readme_findings.md` | Human-readable summary for docs. |

## Kaggle CLI Workflow

Push and run the EDA notebook:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels push -p kaggle/eda
```

Check status:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels status tuannm3812/orbit-wars-eda-baseline
```

Download outputs:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels output tuannm3812/orbit-wars-eda-baseline -p outputs/kaggle_eda
```

## How Insights Feed Strategy

- If **high-production static planets** are usually near home, prioritize static expansion first.
- If **orbiting planets** are frequently high production, add future-position targeting early.
- If starter losses come from **over-draining the home planet**, add reserve thresholds.
- If starter losses come from **slow captures**, send larger fleets for speed, not only exact capture cost.
- If **sun-blocked routes** are common, implement segment-to-circle collision checks before attack tuning.
