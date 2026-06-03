# 6. Replay Review Workflow

## 1. Objective

Use replay review to explain **why the current champion loses** before writing
v3 code. Keep this workflow script-first: raw replay files and generated
diagnostics stay out of git, while only durable strategy lessons are curated
into docs.

Current champion:

| Version | Public score | Smoke losses |
| --- | ---: | --- |
| `roi_reserve_v2` | `343.6` | Seeds `18`, `24`, `27` |

## 2. Access Constraint

The installed Kaggle CLI currently exposes only:

```text
list, files, download, submit, submissions, leaderboard
```

It does not expose `episodes`, `replay`, or `logs`. The Python Kaggle API in
this environment also exposes submissions but not episode/replay helpers.

Practical rule: download episode replay JSON from the Kaggle web UI, or use an
upgraded Kaggle CLI in a controlled environment if replay commands become
available. Store raw files under ignored paths:

```text
replays/roi_reserve_v2/
logs/roi_reserve_v2/
```

Current local check: no replay JSON or HTML files are available under
`replays/`, `logs/`, or `outputs/`. Until public episode replay files are
downloaded, loss diagnosis should be labeled as **benchmark-derived**, not
replay-confirmed.

## 3. Diagnostic Command

Run replay summaries with:

```bash
python3 scripts/replay_diagnostics.py replays/roi_reserve_v2/*.json --player 0 --out-dir outputs/replay_diagnostics/roi_reserve_v2
```

Generated outputs:

| Output | Use |
| --- | --- |
| `replay_summary.csv` | One row per replay with winner, final control, and weakness flags. |
| `player_summary.csv` | Per-player final production, score proxy, action count, and launched ships. |
| `replay_findings.md` | Short Markdown handoff for strategy review. |

## 4. Review Questions

For each loss, answer only decision-relevant questions:

1. Did we lose by **elimination**, **production gap**, or **ship-count gap**?
2. Did the winner control production earlier or simply survive longer?
3. Did our action count or launched ships suggest over-reserving or over-attacking?
4. Were losses concentrated around orbiting targets, sun-blocked geometry, or exposed source planets?
5. What is the smallest v3 behavior change that should prevent the pattern?

## 5. Benchmark-Derived Loss Notes

`roi_reserve_v2` improves the random smoke benchmark from **25/30** wins to
**27/30** wins, fixing v1 loss seeds `11` and `17`. The remaining losses are
seeds `18`, `24`, and `27`.

Key observed patterns:

- Seed `18` is a hard collapse: final score proxy is `40` vs `2286`, with the
  EDA baseline ending at zero player-0 planets on the same seed.
- Seed `24` is another hard loss: final score proxy is `0` vs `2188`, despite
  a low-neutral-ship map where high-production orbiting planets look attractive.
- Seed `27` is close by score proxy, `883` vs `947`, but still reaches the
  turn limit and suggests poor endgame control rather than a runtime problem.
- Loss seeds average more **orbiting planets** than win seeds, and v2 has no
  incoming-fleet defense, no opponent arrival modeling, and no reinforcement
  behavior.

Most likely v3 direction: add **defense-aware launch gating** and
**incoming-threat estimation** before changing target calibration. The current
agent can reserve ships on sources, but it does not know whether a source is
already threatened or whether a target will be contested before arrival.

## 6. Notebook Rule

Do not create a replay notebook just to inspect a few files. Use scripts and
docs first.

Create a new notebook only when one of these is true:

- the replay analysis needs non-trivial visualization;
- the replay parser becomes a substantial workflow;
- the analysis directly produces a new agent candidate;
- there is enough code to justify a clean, reproducible Kaggle run.

Otherwise, update:

- `docs/05_next_steps.md` for strategy decisions;
- `docs/04_agent_version_log.md` for candidate outcomes;
- `scripts/replay_diagnostics.py` for reusable replay parsing improvements.
