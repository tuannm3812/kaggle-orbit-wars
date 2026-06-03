# 5. Next Steps

## 1. Immediate Goal

Monitor `roi_reserve_v1` after submission, then build v2 from replay evidence.
The first submitted agent already adds **target ROI**, **source reserves**, and
**sun path rejection**.

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

## 3. Next Work Items

1. **Submission monitoring**
   Wait for `roi_reserve_v1` public score and episodes.

2. **Replay diagnostics**
   Inspect submitted-game wins and losses, plus smoke-test loss seeds from
   `roi_reserve_v1`.

3. **Orbit-aware targeting v2**
   Predict moving planet position before launch-angle calculation.

4. **Defense and incoming fleets**
   Add basic incoming-threat checks before launching from exposed planets.

5. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

6. **Kaggle smoke run**
   Run the same 30 seeds against `random` and compare against `roi_reserve_v1`.

## 4. Evaluation Checklist

Before submitting the next candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded and compared with `roi_reserve_v1`;
- version log is updated;
- known loss seeds are inspected.

## 5. Submission Rule

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from `roi_reserve_v1`.
