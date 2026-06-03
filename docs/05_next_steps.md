# 5. Next Steps

## 1. Immediate Goal

Build v3 from `roi_reserve_v2` episode evidence. The current champion has
public score `600.0` and adds **target ROI**, **source reserves**, **sun path
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

## 3. Next Work Items

1. **Episode monitoring**
   Inspect `roi_reserve_v2` episodes after they are available.

2. **Replay diagnostics**
   Inspect submitted-game wins and losses, plus v2 smoke-test loss seeds `18`,
   `24`, and `27`.

3. **Defense and incoming fleets**
   Add incoming-threat checks before launching from exposed planets.

4. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

5. **Kaggle smoke run**
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
