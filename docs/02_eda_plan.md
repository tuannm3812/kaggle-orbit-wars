# 2. EDA Plan

## Goal

Use EDA only to answer questions that affect agent design. For Orbit Wars, the
important evidence is **runtime availability**, **starter baseline quality**,
**map-seed profile**, and **failure patterns**.

## Notebook 01: Baseline Evidence

Path: `notebooks/01_orbit_wars_eda.ipynb`

Kaggle path: `kaggle/eda/01_orbit_wars_eda.ipynb`

Key questions:

1. Does the **Kaggle runtime** expose `orbit_wars` through `kaggle_environments.make`?
2. Can the starter run a clean 30-seed benchmark against `random`?
3. How much orbiting and high-production terrain appears in the seed set?
4. Which starter weaknesses should the first agent target?

Expected outputs:

| Output | Meaning |
| --- | --- |
| `eda_environment_info.json` | Runtime, config, and import status. |
| `eda_seed_summary.csv` | One row per simulated seed. |
| `eda_planets_by_seed.csv` | Planet-level initial map profile. |
| `eda_readme_findings.md` | Short Markdown summary for strategy handoff. |

## Kaggle CLI Workflow

Push and run the EDA notebook:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels push -p kaggle/eda
```

Check status:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels status tuannm3823/orbit-wars-eda-baseline
```

Download outputs:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels output tuannm3823/orbit-wars-eda-baseline -p outputs/kaggle_eda_tuannm3823
```

## Strategy Handoff

- The first agent should not copy nearest-target behavior.
- Add **target ROI** before expanding aggression.
- Add **source reserves** before sending larger fleets.
- Add **orbit-aware aiming** for moving high-production planets.
- Add **sun-path rejection** before attack tuning.
