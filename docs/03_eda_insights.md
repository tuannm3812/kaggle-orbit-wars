# 3. EDA Insights

## 1. Decision Summary

The EDA phase has enough evidence to start agent development.

- **Kaggle runtime works:** `orbit_wars` is available on Kaggle with `kaggle_environments==1.29.3`.
- **Local runtime is not enough:** local Python 3.9 has `kaggle-environments==1.18.0`, which does not include `orbit_wars`.
- **Starter is only a control policy:** it wins against `random`, but its losses expose clear strategy gaps.
- **Next work:** build the first ROI/reserve/orbit-aware agent on account `tuannm3823`.

Latest Kaggle EDA lane:

```text
https://www.kaggle.com/code/tuannm3823/orbit-wars-eda-baseline
```

## 2. Runtime Gate

| Item | Value |
| --- | --- |
| Python | `3.12.13` |
| Platform | Linux Kaggle worker |
| `kaggle_environments` | `1.29.3` |
| `orbit_wars` available | `True` |
| Seeds requested | `30` |
| Seeds completed | `30` |
| Run errors | `0` |

Use **Kaggle for simulation evidence** until the local package includes Orbit
Wars. Local notebook runs remain useful only for syntax and artifact checks.

## 3. Starter Baseline

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

This is enough as a control set. It is not enough as an agent strategy because
it has no **target value model**, **source reserve**, **orbit prediction**,
**sun-path check**, or **incoming fleet response**.

## 4. Loss Pattern

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

Key insight:

- Losses are usually **catastrophic**, not close score losses.
- Failed maps have more **orbiting planets** and lower average **production**.
- Static planet count is similar between wins and losses, so map size alone is not the problem.
- The first agent should improve **target quality**, **arrival timing**, and **source safety**.

Loss seeds to keep as regression checks:

| Seed | Steps | Planets | Orbiting | Mean production | Final score proxy | Final planets |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0` | `500` | `32` | `16` | `1.63` | `27` | `1` |
| `3` | `127` | `36` | `12` | `2.78` | `0` | `0` |
| `9` | `435` | `28` | `16` | `2.71` | `0` | `0` |
| `11` | `500` | `32` | `16` | `1.75` | `44` | `2` |
| `12` | `231` | `28` | `12` | `2.57` | `0` | `0` |
| `22` | `204` | `24` | `8` | `2.67` | `0` | `0` |
| `24` | `137` | `36` | `16` | `2.00` | `0` | `0` |

## 5. Map Profile

Across 852 initial planets from 30 seeds:

| Production | Count |
| ---: | ---: |
| `1` | `272` |
| `2` | `172` |
| `3` | `144` |
| `4` | `156` |
| `5` | `108` |

Production is mixed enough that nearest-target expansion will often choose
low-value planets. The first agent should score targets by **production gain**
and **travel/capture cost**, not distance alone.

## 6. Agent Build Priorities

Build the first non-starter agent around four guards:

1. **Target value model**
   Prefer high-production and strategically central targets over nearest targets. Low-production maps punish greedy nearest expansion.

2. **Orbit-aware aiming**
   For orbiting targets, aim at predicted future position near fleet arrival time. The loss pattern makes this a high-priority improvement.

3. **Source reserve model**
   Avoid draining owned planets to exact zero-risk thresholds. Catastrophic losses suggest the starter leaves planets exposed or mistimes captures.

4. **Sun path check**
   Reject launches whose path segment crosses the sun. Continuous collision makes this mandatory before attack tuning.

Do not add another broad EDA notebook before building an agent. Use seeds `0`,
`3`, `9`, `11`, and `24` as targeted diagnostics after the first candidate
exists.
