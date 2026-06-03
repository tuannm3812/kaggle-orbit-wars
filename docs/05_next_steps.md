# 5. Next Steps

## 1. Immediate Goal

Build v3 from `roi_reserve_v2` episode evidence. The current champion has
latest observed public score `423.1` and adds **target ROI**, **source reserves**, **sun path
rejection**, **orbit-aware aiming**, and **target reservation**.

## 2. Current Evidence

The first **Kaggle-hosted EDA run** completed **30 seeds** against `random`:

| Metric | Value |
| --- | ---: |
| Wins | `23` |
| Losses | `7` |
| Win rate | `76.7%` |
| Mean planet count | `28.40` |
| Mean orbiting planets | `11.07` |
| Mean player 0 score proxy | `2090.30` |

Losses were more common on maps with more **orbiting planets** and lower mean
production. Several losses were **catastrophic**, with player 0 ending at zero
planets.

`roi_reserve_v1` Kaggle smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `25` |
| Losses | `5` |
| Win rate | `83.3%` |
| Run errors | `0` |

`roi_reserve_v2` Kaggle smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `27` |
| Losses | `3` |
| Win rate | `90.0%` |
| Run errors | `0` |

Remaining v2 smoke losses are seeds `18`, `24`, and `27`. The current Kaggle
CLI/API cannot fetch public episode replays from this environment, and no replay
files are local yet, so the immediate strategy should use these benchmark losses
as the evidence base while we wait for downloaded public replays.

The loss profile points to **strategic weakness**, not action-format or runtime
failure:

- v2 wins 27/30 against `random`, but the public score remains far below strong
  leaderboard agents, so the random smoke benchmark is useful for regressions
  but not sufficient for strength.
- Remaining loss seeds are heavy on **orbiting geometry** and include hard
  collapses where the agent is eliminated or nearly eliminated.
- The v2 policy captures attractive targets, but it does not model **incoming
  enemy fleets**, **contested arrivals**, **reinforcement**, or source planets
  that should stop launching because they are under threat.

## 3. Next Work Items

1. **Episode monitoring**
   Inspect `roi_reserve_v2` episodes after they are available. Use
   `docs/06_replay_review_workflow.md` and keep raw replay files under
   `replays/`.

2. **Replay diagnostics**
   Inspect submitted-game wins and losses, plus v2 smoke-test loss seeds `18`,
   `24`, and `27`. Start with `scripts/replay_diagnostics.py`, not a new
   notebook.

3. **Defense and incoming fleets**
   Add incoming-threat checks before launching from exposed planets. This should
   be the next model change before further target-score calibration.

4. **Contested target cost**
   Estimate whether enemy ships can arrive before or near our capture time, then
   increase required ships or skip the target.

5. **Reinforcement**
   Move spare ships from safe low-value planets toward threatened high-production
   owned planets.

6. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

7. **Kaggle smoke run**
   Run the same 30 seeds against `random` and compare against `roi_reserve_v2`.

## 4. Evaluation Checklist

Before submitting the next candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded and compared with `roi_reserve_v2`;
- version log is updated;
- known loss seeds are inspected.

## 5. Submission Rule

Submit through the **notebook output** path, not a local `main.py` upload:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submit orbit-wars -k tuannm3823/<kernel-slug> -f submission.tar.gz -v <version> -m "<message>"
```

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from `roi_reserve_v2`.
