# 5. Next Steps

## 1. Immediate Goal

Build v3 from `roi_reserve_v2` episode evidence. The current champion has
latest observed public score `409.4` and adds **target ROI**, **source reserves**, **sun path
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

Remaining v2 smoke losses are seeds `18`, `24`, and `27`.

Public replay review is now available in `docs/07_public_replay_findings.md`.
Reviewed public losses show the same broad weakness as the smoke losses, but
with stronger evidence: v2 often falls behind in **production** by the first 40
turns, then either gets eliminated or loses by a large **ship-count gap**.

The loss profile points to **strategic weakness**, not action-format or runtime
failure:

- v2 wins 27/30 against `random`, but public replays show that the random smoke
  benchmark is useful for regressions, not sufficient for competitive strength.
- v2 starts with a fixed **20-ship reserve** while home planets begin with
  `10` ships, so low-production starts can wait too long before first capture.
- v2 frequently selects **far targets** with long travel times; in reviewed
  public losses, median target travel time is about `31` turns.
- v2 does not model **incoming enemy fleets**, **contested arrivals**,
  **reinforcement**, or source planets that should stop launching because they
  are under threat.

## 3. Next Work Items

1. **Opening tempo reserve**
   Replace the fixed early reserve with a tempo-aware reserve. Low-production
   homes need earlier captures; high-production homes can afford a stronger
   reserve.

2. **Travel-time cap**
   Penalize or skip targets whose capture travel time is too high before we own
   a stable production base.

3. **Local expansion first**
   Prefer nearby neutral captures during the opening, even when their raw
   production/ship ROI is lower.

4. **Defense and incoming fleets**
   Add incoming-threat checks before launching from exposed planets. This should
   be the next model change before further target-score calibration.

5. **Contested target cost**
   Estimate whether enemy ships can arrive before or near our capture time, then
   increase required ships or skip the target.

6. **Reinforcement**
   Move spare ships from safe low-value planets toward threatened high-production
   owned planets.

7. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

8. **Kaggle smoke run**
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
