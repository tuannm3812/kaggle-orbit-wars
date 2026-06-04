# Kaggle Orbit Wars

![Orbit Wars competition header](docs/assets/orbit_wars_header.png)

Notebook-first workspace for [Kaggle Orbit Wars](https://www.kaggle.com/competitions/orbit-wars), a **2D RTS agent competition** about capturing **moving planets** and **comets** while avoiding the **central sun**.

## Current State

- **Official starter files** downloaded with the Kaggle CLI.
- Latest submitted challenger is **`roi_reserve_v4`**, submitted from notebook
  output as `submission.tar.gz`.
- **Live Kaggle CLI metadata** on 2026-06-03 shows deadline `2026-06-23 23:59:00`, reward `50,000 Usd`, and user entry status `True`.
- Latest observed public score for `roi_reserve_v4` is `529.3` after dropping
  from the `600.0` starting score. Treat score movement and replays as the
  signal, not the initial score.
- Public replay findings are documented in `docs/07_public_replay_findings.md`.
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
  06_replay_review_workflow.md
  07_public_replay_findings.md
  README.md
notebooks/
  01_orbit_wars_eda.ipynb
  02_agent_submission.ipynb
  archive/
    02_roi_reserve_agent_v1.ipynb
    03_roi_reserve_agent_v2.ipynb
kaggle/
  eda/
    kernel-metadata.json
    01_orbit_wars_eda.ipynb
  submission/
    kernel-metadata.json
    02_agent_submission.ipynb
    main.py
  archive/
    roi_reserve_v1/
    roi_reserve_v2/
agents/
  roi_reserve_v1/
    main.py
  roi_reserve_v2/
    main.py
  roi_reserve_v3/
    main.py
  roi_reserve_v4/
    main.py
tests/
  test_roi_reserve_agent.py
  test_roi_reserve_agent_v2.py
  test_roi_reserve_agent_v3.py
  test_roi_reserve_agent_v4.py
  test_submission_notebook.py
  test_replay_diagnostics.py
scripts/
  replay_diagnostics.py
data/
  raw/
  processed/
outputs/
replays/
logs/
```

## Current Workflow

1. Review `docs/01_competition_instructions.md`.
2. Push and run the EDA notebook on Kaggle when the baseline needs refreshing:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels push -p kaggle/eda
```

3. Push and run the current agent notebook on Kaggle:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle kernels push -p kaggle/submission
```

4. Submit the generated notebook output after the Kaggle smoke benchmark passes:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submit orbit-wars -k tuannm3823/orbit-wars-agent-submission -f submission.tar.gz -v <kernel_version> -m "<agent_version>: <short change summary>"
```
