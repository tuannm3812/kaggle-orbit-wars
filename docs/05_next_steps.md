# 5. Next Steps

## 1. Immediate Goal

Review `roi_reserve_v3` score movement and public replays before changing the
model again. The latest submitted challenger started at public score `600.0`,
then moved down to `547.5` after early public games. That confirms the starting
score is not proof of improvement. v3 adds
**opening tempo reserve**, **local-neutral opening preference**, **travel-time
filtering**, and **incoming-threat launch holds** on top of v2's **target ROI**,
**source reserves**, **sun path rejection**, **orbit-aware aiming**, and
**target reservation**.

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

Scoring caution: a fresh Orbit Wars submission can show `600.0` before it has
played enough public matches. Treat that as a starting rating. v3's first score
movement was downward to `547.5`, so promotion requires replay evidence that the
drop is recoverable or narrower than v2's failure modes.

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

## 4. Next Work Items

1. **Replay review for v3**
   Compare public wins and losses against the v2 replay failure modes: opening
   timing, long-travel targets, defense holds, and elimination pattern.

2. **Score movement check**
   Continue checking the submission table after public games. v3 has already
   dropped from `600.0` to `547.5`; inspect losses before making another model
   change.

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

## 5. Evaluation Checklist

Before submitting the next candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded and compared with `roi_reserve_v2`;
- version log is updated;
- known loss seeds are inspected.

## 6. Submission Rule

Submit through the **notebook output** path, not a local `main.py` upload:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submit orbit-wars -k tuannm3823/<kernel-slug> -f submission.tar.gz -v <version> -m "<message>"
```

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from `roi_reserve_v2`.
