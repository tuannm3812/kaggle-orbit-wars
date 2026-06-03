# 5. Next Steps

## 1. Immediate Goal

Build the first **non-starter agent** that improves on nearest-planet behavior by
adding **target ROI**, **source reserves**, **orbit-aware aiming**, and **sun path rejection**.

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

## 3. Next Work Items

1. **Replay diagnostics notebook**
   Create `02_loss_replay_diagnostics.ipynb` to inspect seeds `0`, `3`, `9`,
   `11`, and `24`.

2. **Geometry helpers**
   Implement and test **distance**, **angle**, **fleet speed**, **arrival estimate**, and
   **segment-to-sun collision checks**.

3. **Target ROI baseline**
   Replace nearest-target selection with **production-aware ROI**:

   ```text
   roi = production_gain / max(capture_cost + travel_time_penalty, 1)
   ```

4. **Source reserve**
   Keep a **reserve** on each owned planet before launching. Start simple:

   ```text
   reserve = max(5, production * 3)
   ```

5. **Orbit-aware targeting**
   Predict **orbiting planet position** at estimated arrival time before computing
   launch angle.

6. **Kaggle smoke run**
   Run **30 seeds on Kaggle** against `random` and compare against the starter EDA
   baseline.

## 4. Evaluation Checklist

Before submitting a candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded;
- version log is updated;
- known loss seeds are inspected.

## 5. Submission Rule

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from the previous candidate.
