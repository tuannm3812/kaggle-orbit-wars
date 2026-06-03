# 6. Replay Review Workflow

## 1. Objective

Use replay review to explain **why the current champion loses** before writing
v3 code. Keep this workflow script-first: raw replay files and generated
diagnostics stay out of git, while only durable strategy lessons are curated
into docs.

Current champion:

| Version | Public score | Smoke losses |
| --- | ---: | --- |
| `roi_reserve_v2` | `409.4` | Seeds `18`, `24`, `27` |

## 2. Official Replay Commands

The official Orbit Wars starter guide documents these Kaggle commands for
episode review after a submission has played games:

```bash
kaggle competitions submissions orbit-wars
kaggle competitions episodes <SUBMISSION_ID>
kaggle competitions episodes <SUBMISSION_ID> -v
kaggle competitions replay <EPISODE_ID> -p ./replays
kaggle competitions logs <EPISODE_ID> 0 -p ./logs
kaggle competitions logs <EPISODE_ID> 1 -p ./logs
```

Expected review flow:

1. Find the relevant **submission ID** from the submission table.
2. List episodes for that submission.
3. Select at least one **win**, one **loss**, and one close game.
4. Download replay JSON and logs for our player slot.
5. Store raw files under ignored local folders.
6. Run the local diagnostics script.
7. Curate only durable lessons into `docs/05_next_steps.md` and
   `docs/04_agent_version_log.md`.

## 3. Current Access Constraint

The installed Kaggle CLI currently exposes only:

```text
list, files, download, submit, submissions, leaderboard
```

It does not expose `episodes`, `replay`, or `logs`. The Python Kaggle API in
this environment also exposes submissions but not episode/replay helpers. A
local package-source scan also found no references to `episodes`, `replay`,
`logs`, or `pages`.

Practical rule: download episode replay JSON from the Kaggle web UI, or use an
environment where the official replay commands are available. Store raw files
under ignored paths:

```text
replays/roi_reserve_v2/
logs/roi_reserve_v2/
```

Current local status: public replay JSON for `roi_reserve_v2` submission
`53322680` has been downloaded under ignored path `replays/roi_reserve_v2/`.
Replay-derived findings are curated in `docs/07_public_replay_findings.md`.
Keep raw replay files and generated diagnostics out of git.

## 4. Diagnostic Command

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

## 5. Review Questions

For each loss, answer only decision-relevant questions:

1. Did we lose by **elimination**, **production gap**, or **ship-count gap**?
2. Did the winner control production earlier or simply survive longer?
3. Did our action count or launched ships suggest over-reserving or over-attacking?
4. Were losses concentrated around orbiting targets, sun-blocked geometry, or exposed source planets?
5. Did we lose ships to **comet expiration**, failed comet timing, or comet
   over-commitment?
6. Were high-production owned planets left under-defended while low-value
   planets launched attacks?
7. What is the smallest v3 behavior change that should prevent the pattern?

## 6. Replay Review Checklist

For every downloaded episode, capture these fields in the generated findings or
the version log:

| Field | Why it matters |
| --- | --- |
| Submission id and episode id | Makes the replay traceable. |
| Player slot | Logs are player-slot-specific. |
| Result and final score proxy | Separates close losses from collapses. |
| Final planets and production | Shows whether the loss is economic. |
| Action count and launched ships | Flags over-reserving or over-attacking. |
| Sun/path failures | Directly tests trajectory logic. |
| Incoming enemy pressure | Tests whether defense gating is needed. |
| Comet ownership and expiry | Tests whether comet policy helps or hurts. |

## 7. Benchmark-Derived Loss Notes

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

## 8. Notebook Rule

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
