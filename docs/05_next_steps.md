# 5. Next Steps

## 1. Immediate Goal

Review `roi_reserve_v4` score movement and public replays before changing the
model again. The latest submitted challenger moved from the `600.0` starting
score to `529.3`, currently above v3's `505.8` but still not a confirmed
strategic win without replay review. v4 adds
**timed reinforcement** and **enemy-production capture cost** on top of v3's
**opening tempo reserve**, **local-neutral opening preference**, **travel-time
filtering**, and **incoming-threat launch holds**.

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

`roi_reserve_v2` best Kaggle smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `29` |
| Losses | `1` |
| Win rate | `96.7%` |
| Run errors | `0` |

`roi_reserve_v3` Kaggle smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `28` |
| Losses | `2` |
| Win rate | `93.3%` |
| Run errors | `0` |

Remaining v3 smoke losses are seeds `0` and `19`.

`roi_reserve_v4` Kaggle smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `29` |
| Losses | `1` |
| Win rate | `96.7%` |
| Run errors | `0` |

Remaining v4 smoke loss is seed `0`.

Scoring caution: a fresh Orbit Wars submission can show `600.0` before it has
played enough public matches. Treat that as a starting rating. v4 has moved
down to `529.3`, so promotion requires replay evidence that its losses are
narrower or more fixable than v3's.

Public replay review is now available in `docs/07_public_replay_findings.md`.
Reviewed public losses show the same broad weakness as the smoke losses, but
with stronger evidence: v2 often falls behind in **production** by the first 40
turns, then either gets eliminated or loses by a large **ship-count gap**.

The loss profile points to **strategic weakness**, not action-format or runtime
failure:

- v2 wins up to 29/30 against `random`, but public replays show that the random smoke
  benchmark is useful for regressions, not sufficient for competitive strength.
- v2 starts with a fixed **20-ship reserve** while home planets begin with
  `10` ships, so low-production starts can wait too long before first capture.
- v2 frequently selects **far targets** with long travel times; in reviewed
  public losses, median target travel time is about `31` turns.
- v2 does not model **incoming enemy fleets**, **contested arrivals**,
  **reinforcement**, or source planets that should stop launching because they
  are under threat.

## 3. Completed v3 Work Items

1. **Opening tempo reserve**
   v3 replaces the fixed early reserve with a tempo-aware reserve.

2. **Travel-time cap**
   v3 filters long-travel candidates before the economy is stable.

3. **Local expansion first**
   v3 prefers nearby neutral captures during the opening.

4. **Defense and incoming fleets**
   v3 holds launches from owned planets with clear incoming enemy fleet threats.

## 4. Completed v4 Work Items

1. **Timed reinforcement**
   v4 uses visible incoming enemy fleet ETA to send reinforcements before an
   owned planet is forecast to fall.

2. **Enemy-production capture cost**
   v4 increases required ships for enemy-owned targets based on expected
   production before our fleet arrives.

3. **OW-Proto lesson**
   The `djenkivanov/orbit-wars-agent-ow-proto-passed-1-000` notebook validates
   that reinforcement timing and production-aware attack cost are high-value
   mechanics. v4 ports those ideas narrowly without copying the full public
   agent.

## 5. Next Work Items

1. **Score movement check for v4**
   Continue checking the submission table after public games. v4 currently sits
   at `529.3` after dropping from `600.0`.

2. **Replay review for v4**
   Compare public wins and losses against v3 and v2 failure modes: opening
   timing, reinforcement success, over-defense, and enemy-production attacks.

3. **Contested target cost**
   Estimate whether enemy ships can arrive before or near our capture time, then
   increase required ships or skip the target.

4. **Reinforcement**
   Move spare ships from safe low-value planets toward threatened high-production
   owned planets.

5. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

6. **RL-inspired feature audit**
   The public PPO tutorial frames each owned planet as a source decision with
   self, candidate, and global features. Use that structure as an audit checklist
   for v4 heuristics, not as a reason to add training code before replay evidence
   supports it.

## 6. Evaluation Checklist

Before submitting the next candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded and compared with `roi_reserve_v2`;
- version log is updated;
- known loss seeds are inspected.

## 7. Submission Rule

Submit through the **notebook output** path, not a local `main.py` upload:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submit orbit-wars -k tuannm3823/<kernel-slug> -f submission.tar.gz -v <version> -m "<message>"
```

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from `roi_reserve_v2`.
