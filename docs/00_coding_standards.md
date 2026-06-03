# 0. Coding Standards

## 1. Repository Scope

This repository is intentionally **notebook-first**. Kaggle notebooks are the
**executable source of truth** for environment EDA, strategy experiments, local
simulation on Kaggle, and submission packaging. `docs/` captures competition
rules, EDA findings, replay lessons, version decisions, and current strategy.

Keep the root small:

- `notebooks/` for project-owned notebooks.
- `kaggle/` for Kaggle CLI push directories with kernel metadata.
- `docs/` for standards, official-rule notes, EDA insights, strategy notes,
  version logs, and small supporting assets.
- `README.md` for the high-level project overview and current workflow.

Do not use the repo as a **data dump**. Raw competition downloads, Kaggle output
folders, replay dumps, logs, and generated submissions should stay outside git
unless a small curated artifact directly supports written analysis.

## 2. Directory Conventions

Use these directories:

| Path | Purpose | Commit policy |
| --- | --- | --- |
| `docs/` | Human-readable project docs and small curated assets. | Commit. |
| `docs/assets/` | Official header image and small explanatory figures. | Commit only small, relevant assets. |
| `notebooks/` | Clean source notebooks for review. | Commit with outputs cleared unless output is intentionally curated. |
| `kaggle/<lane>/` | Kaggle CLI runnable kernel folders. | Commit metadata and clean notebook source. |
| `outputs/` | Downloaded Kaggle kernel outputs. | Ignore by default. Summarize into docs instead. |
| `data/raw/` | Official competition downloads. | Ignore. |
| `replays/` | Downloaded replay JSON or rendered replay evidence. | Ignore unless curated into docs. |
| `logs/` | Kaggle episode logs. | Ignore unless a small log excerpt is required as evidence. |

## 3. Notebook Naming

Use numbered, stable notebook names that describe the workflow:

1. `01_orbit_wars_eda.ipynb`
2. `02_agent_submission.ipynb`
3. `03_replay_review.ipynb`

Reserve new numbers for promoted project-owned workflows. For small
parameter-only variants, prefer configuration cells and a version log entry over
creating many near-duplicate notebooks.

Replay review should start with scripts and docs, not notebooks. Add a new
notebook only when replay work needs substantial visualization, a reusable
analysis workflow, or a major agent-code change.

Keep notebooks focused on reusable workflows:

- `01_orbit_wars_eda.ipynb` is the reusable environment and baseline analysis
  workflow;
- `02_agent_submission.ipynb` is the single active Kaggle submission workflow;
- `03_replay_review.ipynb` is optional and should exist only if script-first
  replay review needs visual analysis.

Do not create one notebook per agent version. Agent versions live under
`agents/<version>/main.py`; the active submission notebook selects a version via
`CFG["agent_version"]`. Keep version history in `docs/04_agent_version_log.md`,
not inside notebooks. Move superseded workflow notebooks to `notebooks/archive/`.

## 4. Notebook Structure

Each notebook should include:

- a clear title and short purpose statement;
- a **`CFG` block** near the top for seeds, opponent, run counts, time limits, and
  output paths;
- explicit **mode flags** such as `RUN_FAST`, `RUN_SIMULATIONS`,
  `WRITE_SUBMISSION`, and `SAVE_REPLAYS`;
- **Kaggle runtime detection** and path auto-detection;
- **Markdown insight cells** after important tables, plots, or replay summaries;
- **artifact-writing cells** for generated `main.py`, `submission.tar.gz`, replay
  summaries, and CSV diagnostics;
- **verification cells** that compile generated Python and run at least one smoke
  simulation on Kaggle.

Prefer readable, self-contained notebook code over imports from local project
modules. Kaggle should be able to run a notebook after attaching only the
competition source and any explicitly named Kaggle inputs.

When notebook code changes, clear outputs before committing unless the output is
small and intentionally kept as evidence. Kaggle is the trusted execution
record; downloaded outputs should be summarized into docs.

## 5. Kaggle Runtime Rules

Orbit Wars currently requires a **Kaggle-hosted runtime**. The local Python 3.9
environment can install `kaggle-environments==1.18.0`, but that version does
not include `orbit_wars`. The Kaggle worker used by the first EDA run exposed
`kaggle_environments==1.29.3`.

Standards:

- Run **simulation notebooks on Kaggle** until local `orbit_wars` is available.
- Keep Kaggle kernels offline-safe by default: `enable_internet` should be
  `false` unless an exploratory kernel explicitly needs it.
- Use the Kaggle CLI path already available in this environment:
  `/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle`.
- Keep `kernel-metadata.json` in each Kaggle push folder.
- After a Kaggle run, download outputs and summarize the useful evidence into
  `docs/`; do not commit bulky output folders.

## 6. Agent Contract

A submitted agent must expose:

```python
def agent(obs):
    ...
    return moves
```

Return value:

```python
[[from_planet_id, direction_angle, num_ships], ...]
```

Agent standards:

- Return `[]` for no action.
- Only launch from planets owned by `obs["player"]`.
- Never send more ships than the current source garrison.
- Cast action values to plain `int` and `float` values.
- Keep per-turn logic well below the 1 second action timeout.
- Avoid `print` spam in submitted agents; logs are useful for diagnostics but
  can become noisy and slow.
- Prefer deterministic behavior for a given observation unless randomness is
  explicitly seeded and tested.
- Fail safely. If a helper raises or a state assumption is missing, the agent
  should return a conservative valid action or `[]`, not crash.

## 7. Strategy Code Standards

Build the agent as **small, testable helpers** inside the notebook first. Promote a
helper only when it is reused across strategy versions.

Core helper groups:

- **state parsing**: planets, fleets, ownership, comets;
- **geometry**: distance, angle, segment-circle intersection, board bounds;
- **movement prediction**: orbiting planet future position, comet future position,
  fleet arrival estimate;
- **scoring**: target ROI, source reserve, defense threat, attack opportunity;
- **action selection**: expansion, reinforcement, attack, comet capture, no-op.

Use simple functions with explicit inputs. Avoid hidden global state except for
small cached constants or controlled per-game memory. If memory is introduced,
document the reset condition and prove it does not leak across episodes.

## 8. Code Style

Follow PEP 8 for Python code:

- Use 4 spaces for indentation.
- Keep lines to 79 characters or fewer where practical; allow slightly longer
  notebook display lines when breaking them hurts readability.
- Prefer f-strings, comprehensions, and small utility functions when they make
  intent clearer.
- Add type hints for reusable helpers when the type is clear.
- Group imports in this order:
  1. Standard library
  2. Third-party libraries
  3. Local modules, if the project later adds them
- Separate import groups with a blank line.

Use **Google-style docstrings** for reusable logic:

```python
def fleet_speed(ships: int, max_speed: float = 6.0) -> float:
    """Calculate Orbit Wars fleet speed from fleet size.

    Args:
        ships: Number of ships in the fleet.
        max_speed: Environment maximum fleet speed.

    Returns:
        Fleet movement speed in board units per turn.
    """
```

Add comments only when they explain why a decision was made. Avoid comments
that restate the code.

## 9. Visualization And Image Standards

Use visual assets only when they support strategy or documentation:

- The official Kaggle header image is stored at
  `docs/assets/orbit_wars_header.png`.
- Use Kaggle environment renders or replay views as primary gameplay evidence.
- Use compact charts for map distributions, production control, fleet counts,
  and win/loss comparisons.
- Use the Viridis palette for analytical charts unless semantic colors are
  clearer.
- Keep chart titles short and analytical.
- Do not add decorative figures that do not support a decision.

For curated replay images, name files by notebook, seed, and purpose:

```text
docs/assets/seed_003_loss_final_state.png
docs/assets/seed_009_sun_blocked_route.png
```

## 10. EDA Standards

EDA for Orbit Wars is **environment and replay analysis**, not train/test table
analysis.

Every EDA pass should answer a concrete strategy question, such as:

- Which seeds expose starter-agent failure modes?
- Do losses correlate with orbiting planet count, production spread, or route
  geometry?
- Which target pairs are sun-blocked?
- How quickly does each player control production?
- How often do exact-capture fleets fail due to timing or third-party arrivals?

Write machine-readable outputs to `/kaggle/working`:

- seed-level summary CSV;
- planet-level profile CSV;
- turn-level ownership or production CSV;
- selected replay metadata JSON;
- a short markdown findings file.

Then summarize the findings into `docs/03_eda_insights.md` or a later numbered
insight doc.

## 11. Submission Standards

Before submitting:

1. Generate `main.py` or `submission.tar.gz`.
2. **Compile every generated Python file**.
3. Run a **Kaggle simulation smoke test**.
4. Confirm **action format** is valid.
5. Confirm no **local-only imports or file paths** are required.
6. Record the candidate in the version log.
7. Submit with a message that includes the version name and strategy change.

After submitting:

- check submission status;
- wait for episodes;
- download replays/logs for at least one win and one loss when available;
- run `scripts/replay_diagnostics.py` on downloaded replay JSON files;
- update the version log with score, observations, and next decision.

## 12. Documentation Style

Documentation should be written for a teammate reviewing the competition plan:

- Use numbered sections.
- Lead with objectives, constraints, and implications.
- Include exact commands, metrics, dates, and file paths where useful.
- Link notebooks and docs with relative paths.
- Keep broad narrative in `README.md`.
- Keep detailed evidence in focused numbered docs.
- Prefer tables for rules, metrics, and version comparisons.

Required docs for this project:

- `docs/README.md`: documentation index and reading order.
- `docs/00_coding_standards.md`: repo, notebook, agent, and submission rules.
- `docs/01_competition_instructions.md`: official rules and strategy frame.
- `docs/02_eda_plan.md`: current EDA questions and outputs.
- `docs/03_eda_insights.md`: first EDA findings.
- `docs/04_agent_version_log.md`: submission and strategy version history.
- `docs/05_next_steps.md`: current action plan and evaluation checklist.

## 13. Git Hygiene

Do not commit:

- raw Kaggle competition downloads;
- generated `main.py`, `submission.py`, or `submission.tar.gz`;
- Kaggle working directories;
- downloaded output folders;
- local replay/log dumps;
- Python caches or notebook checkpoints;
- ad hoc experiment outputs.

Commit lightweight artifacts only when they directly support written analysis,
such as docs, small official images, curated diagrams, and small notebook
summaries.
