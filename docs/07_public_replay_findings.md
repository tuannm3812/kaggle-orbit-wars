# 7. Public Replay Findings

## 1. Scope

Reviewed `roi_reserve_v2` public episodes for submission `53322680` on
2026-06-03. Raw replay JSON files are stored under ignored local path
`replays/roi_reserve_v2/`. Generated analysis tables are stored under ignored
local path `outputs/replay_diagnostics/roi_reserve_v2_public/`.

The installed Kaggle CLI still does not expose the official `episodes` and
`replay` commands. Replays were fetched through Kaggle's authenticated internal
episode service after discovering the submission id from the submission table.

Latest observed public score during this review: `446.5`.

## 2. Episodes Reviewed

| Episode | Result | Players | Turns | Final planets | Final production | Final score proxy | Opponent score proxy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `78602185` | Loss | 2 | 477 | 0 | 0 | 0 | 5021 |
| `78602430` | Loss | 2 | 500 | 17 | 28 | 1269 | 18372 |
| `78602790` | Loss | 2 | 174 | 0 | 0 | 0 | 7997 |
| `78603520` | Loss | 2 | 500 | 17 | 37 | 1629 | 9163 |
| `78603878` | Loss | 2 | 173 | 0 | 0 | 0 | 8026 |
| `78604250` | Loss | 2 | 262 | 0 | 0 | 0 | 2638 |
| `78604644` | Loss | 2 | 218 | 0 | 0 | 0 | 4923 |
| `78605030` | Loss | 2 | 167 | 0 | 0 | 0 | 3746 |
| `78605418` | Loss | 4 | 500 | 0 | 0 | 0 | 9828 |
| `78605651` | Loss | 4 | 428 | 0 | 0 | 0 | 4050 |
| `78607946` | Win | 2 | 428 | 28 | 72 | 3556 | 0 |

## 3. Main Finding

The public losses are **strategy failures**, not format or runtime failures.
Most losses end in elimination, and the two non-elimination losses still have
large **ship-count deficits** despite owning a comparable number of planets.

Across the 10 reviewed losses:

| Metric | Average |
| --- | ---: |
| Final planets | `3.4` |
| Final production | `6.5` |
| Final score proxy | `289.8` |
| Opponent score proxy | `7376.4` |
| Peak planets | `7.8` |
| Peak production | `18.4` |
| First turn trailing production | `35.8` |
| First turn below half opponent score | `60.3` |

This means the agent usually falls behind before the midgame. Later behavior is
mostly trying to recover from an already-lost economic position.

## 4. Opening Weakness

Every game starts with a home planet at `10` ships, while v2's early
`source_reserve` is at least `20`. That means v2 has no affordable launch at
turn `0` in the reviewed losses.

First action timing in losses:

| Episode | Home production | First action | First capture | Peak planets | Peak production |
| --- | ---: | ---: | ---: | ---: | ---: |
| `78602185` | 1 | 20 | 76 | 5 | 12 |
| `78602430` | 5 | 5 | 13 | 20 | 31 |
| `78602790` | 1 | 19 | 24 | 5 | 15 |
| `78603878` | 4 | 8 | 42 | 5 | 15 |
| `78604644` | 1 | 28 | 114 | 3 | 10 |
| `78605418` | 3 | 8 | 105 | 5 | 13 |
| `78605651` | 1 | 18 | None | 1 | 1 |

The reserve is too conservative for low-production homes and still not
defensive enough later, because it does not react to **incoming fleets**.

## 5. Targeting Weakness

The policy often prefers cheap, far targets over nearby expensive targets. That
is understandable from the current ROI formula, but in public matches it creates
slow captures and gives opponents time to build production.

Loss action aggregate:

| Metric | Value |
| --- | ---: |
| Median target distance | `46.7` |
| Far target share, distance > 30 | `70.5%` |
| Orbiting target share | `61.4%` |
| Enemy-owned target share | `44.5%` |
| Median travel time | `31.3` turns |
| Median ships sent | `8` |

Example first moves:

| Episode | First action | Chosen target | Target production | Distance | Travel turns | Nearby alternative |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `78602430` | 5 | neutral | 5 | 52.4 | 26.7 | nearest neutral at 10.8 distance |
| `78603878` | 8 | neutral | 5 | 27.1 | 11.7 | nearest target at 12.8 distance |
| `78605418` | 8 | neutral | 1 | 23.3 | 12.3 | nearest target at 11.7 distance |
| `78605651` | 18 | enemy-owned | 1 | 53.8 | 30.8 | nearest neutral at 9.5 distance |

The policy needs a stronger **tempo model**: a target with high theoretical ROI
is bad if it arrives after the opponent has already taken the nearby economy.

## 6. Defense Weakness

v2 reserves a fixed number of ships but does not evaluate whether a planet is
actually under threat. In replay losses we see two different failures:

- **Slow starts**: low-production homes wait too long before the first capture.
- **Over-launching later**: high-action losses launch many ships while the
  opponent ends with a massive score advantage.

The current agent also sends attacks toward enemy-owned planets without
estimating **enemy reinforcement**, **enemy arrivals**, or whether the target
will still be worth the travel time.

## 7. Strategy Decision

The next candidate should be a real model change, not a calibration-only
notebook. Build `roi_reserve_v3` around:

1. **Opening tempo reserve**
   Lower the early reserve when the home planet has low production or when a
   nearby low-cost neutral can be captured quickly.

2. **Travel-time cap**
   Penalize or skip targets whose capture travel time is too high, especially
   before we own a stable production base.

3. **Local expansion first**
   In the first phase, prefer nearby neutral captures that increase production
   quickly, even if their raw production/ship ROI is lower.

4. **Incoming-threat defense**
   Estimate which owned planets are threatened by enemy fleets and stop using
   those planets as sources until the threat is covered.

5. **Contested target cost**
   Increase required ships or skip targets when enemy fleets or enemy-owned
   planets can contest the arrival window.

6. **Reinforcement**
   Send spare ships from safe low-value planets to high-production owned planets
   that are likely to be attacked.

Do not create a new notebook for more replay calibration. A v3 notebook is
justified only when the agent behavior changes around these mechanics.
