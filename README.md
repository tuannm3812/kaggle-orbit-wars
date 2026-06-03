# Kaggle Orbit Wars

![Orbit Wars competition header](docs/assets/orbit_wars_header.png)

Notebook-first workspace for [Kaggle Orbit Wars](https://www.kaggle.com/competitions/orbit-wars), a **2D RTS agent competition** about capturing **moving planets** and **comets** while avoiding the **central sun**.

## Current State

- **Official starter files** downloaded with the Kaggle CLI.
- **No account submissions** yet.
- **Live Kaggle CLI metadata** on 2026-06-03 shows deadline `2026-06-23 23:59:00`, reward `50,000 Usd`, and user entry status `True`.
- Local PyPI `kaggle-environments==1.18.0` does not include `orbit_wars`, so **simulation EDA** should run on Kaggle.

## Repository Layout

```text
docs/
  assets/
    orbit_wars_header.png
  00_coding_standards.md
  01_competition_instructions.md
  02_eda_plan.md
  03_eda_insights.md
  04_agent_version_log.md
  05_next_steps.md
  README.md
notebooks/
  01_orbit_wars_eda.ipynb
kaggle/
  eda/
    kernel-metadata.json
    01_orbit_wars_eda.ipynb
data/
  raw/
  processed/
outputs/
replays/
logs/
```

## First Workflow

1. Review `docs/01_competition_instructions.md`.
2. Push and run the EDA notebook on Kaggle:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels push -p kaggle/eda
```

3. Check run status:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels status tuannm3812/orbit-wars-eda-baseline
```

4. Download outputs after the run completes:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels output tuannm3812/orbit-wars-eda-baseline -p outputs/kaggle_eda
```
