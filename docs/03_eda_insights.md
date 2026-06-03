# 3. EDA Insights

## 1. Run Context

The first EDA notebook was pushed and run on Kaggle as:

```text
https://www.kaggle.com/code/tuannm3812/orbit-wars-eda-baseline
```

Run status: **complete**.

Kaggle runtime:

| Item | Value |
| --- | --- |
| Python | `3.12.13` |
| Platform | Linux Kaggle worker |
| `kaggle_environments` | `1.29.3` |
| `orbit_wars` available | `True` |
| Seeds requested | `30` |
| Seeds completed | `30` |
| Run errors | `0` |

Local note: the current local PyPI package available for Python 3.9 is `kaggle-environments==1.18.0`, which does not include `orbit_wars`. Use **Kaggle for simulation** until a newer local package is available for this machine.

## 2. Starter Agent Baseline

The notebook ran the **official nearest-planet starter-style agent** against `random` for **30 seeds**.

| Metric | Value |
| --- | ---: |
| Wins | `23` |
| Losses | `7` |
| Win rate | `76.7%` |
| Mean planet count | `28.40` |
| Mean orbiting planets | `11.07` |
| Mean initial ships per planet | `27.30` |
| Mean production per planet | `2.67` |
| Mean player 0 score proxy | `2090.30` |

The baseline is good enough to validate **environment access** and **submission plumbing**, but not strategically strong. It sends exact capture amounts to the nearest non-owned planet without preserving **reserves**, checking **sun collision**, predicting **orbit movement**, or reacting to **incoming fleets**.

## 3. Win Versus Loss Pattern

Average seed features:

| Feature | Losses | Wins |
| --- | ---: | ---: |
| Episode steps | `304.86` | `218.22` |
| Planet count | `30.86` | `27.65` |
| Orbiting planets | `13.71` | `10.26` |
| Static planets | `17.14` | `17.39` |
| Mean initial ships | `26.84` | `27.44` |
| Mean production | `2.30` | `2.78` |
| Player 0 score proxy | `10.14` | `2723.39` |
| Player 0 final planets | `0.43` | `27.00` |
| Player 0 final production | `0.43` | `72.57` |

Interpretation:

- The starter struggles more on maps with many **orbiting planets**.
- Loss maps have lower average **production**, so exact nearest captures can waste tempo on low-value planets.
- Losses are usually **catastrophic**: player 0 often ends with zero planets rather than narrowly losing on final score.
- Static planet count is similar in wins and losses, so the difference is not just map size. **Orbit density** and **target quality** matter more.

Loss seeds to inspect first:

| Seed | Steps | Planets | Orbiting | Mean production | Final score proxy | Final planets |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0` | `500` | `32` | `16` | `1.63` | `27` | `1` |
| `3` | `127` | `36` | `12` | `2.78` | `0` | `0` |
| `9` | `435` | `28` | `16` | `2.71` | `0` | `0` |
| `11` | `500` | `32` | `16` | `1.75` | `44` | `2` |
| `12` | `231` | `28` | `12` | `2.57` | `0` | `0` |
| `22` | `204` | `24` | `8` | `2.67` | `0` | `0` |
| `24` | `137` | `36` | `16` | `2.00` | `0` | `0` |

## 4. Map Distribution

Across 852 initial planets from 30 seeds:

| Production | Count |
| ---: | ---: |
| `1` | `272` |
| `2` | `172` |
| `3` | `144` |
| `4` | `156` |
| `5` | `108` |

All initial planets in the planet profile output are neutral because the notebook used `initial_planets` when available. The next EDA pass should also record the first live `planets` observation so **home planets** and **player assignments** are explicit.

## 5. Strategy Implications

The next agent should not be a small tweak to nearest-target logic. The first real baseline should add four **strategy guards** before it becomes a champion candidate:

1. **Target value model**
   Prefer high-production and strategically central targets over nearest targets. Low-production maps punish greedy nearest expansion.

2. **Orbit-aware aiming**
   For orbiting targets, aim at predicted future position near fleet arrival time. The loss pattern makes this a high-priority improvement.

3. **Source reserve model**
   Avoid draining owned planets to exact zero-risk thresholds. Catastrophic losses suggest the starter leaves planets exposed or mistimes captures.

4. **Sun path check**
   Reject launches whose path segment crosses the sun. Continuous collision makes this mandatory before attack tuning.

## 6. Next EDA Pass

The next notebook should produce richer behavior diagnostics:

- first live owner distribution from `obs["planets"]`;
- per-turn planet ownership timeline;
- per-turn production controlled by each player;
- fleet launch counts and ship totals;
- estimated fleet arrivals and failed captures;
- sun-crossing risk for candidate planet pairs;
- replay JSON for selected loss seeds.

Recommended immediate target: inspect seeds `0`, `3`, `9`, `11`, and `24`, then design the first non-starter heuristic around **target ROI**, **orbit prediction**, and **source reserves**.
