# 5. Next Steps

## 1. Immediate Goal

Review `roi_reserve_v5` losses before changing the model again. v5 is submitted
on account `tuannm3812` and has dropped to `415.4` after more public games,
while `roi_reserve_v3` remains the best mature baseline on `tuannm3823`.

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

`roi_reserve_v5` Kaggle-hosted smoke benchmark:

| Metric | Value |
| --- | ---: |
| Wins | `30` |
| Losses | `0` |
| Win rate | `100.0%` |
| Run errors | `0` |

Scoring caution: a fresh Orbit Wars submission can show `600.0` before it has
played enough public matches. Treat that as a starting rating. v4 moved down to
`471.9`, so its reinforcement/production-cost changes should be treated as a
failed challenger until replays explain the failure. v5 has also underperformed
v3 after moving down to `415.4`; its 30/30 random smoke result did not translate
to public strength.

Public replay review is now available in `docs/07_public_replay_findings.md`.
Reviewed public losses show the same broad weakness as the smoke losses, but
with stronger evidence: submitted agents often fall behind in **production** or
lose control in the **midgame**, then either get eliminated or lose by a large
**ship-count gap**.

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

## 5. Completed v5 Work Items

1. **Source safety after launch**
   v5 projects visible incoming fleets after proposed ship spend and skips
   launches that would leave the source unsafe.

2. **Contested target pressure**
   v5 increases enemy-target capture cost using nearby visible enemy production
   and spare ships that can contest the arrival window.

3. **Multiplayer restraint**
   v5 avoids enemy-owned targets in unstable four-player openings until our
   production base is more stable.

4. **Pressure-based regroup**
   v5 now adds a limited regroup pass inspired by `slawekbiel/the-producer-agent`:
   move only surplus ships, prefer nearby pressure hotspots, and keep the source
   reserve intact.

## 6. Next Work Items

1. **Replay expansion for v5**
   v5 currently has 38 downloaded public replays: 11 wins and 27 losses. Keep v3
   as the baseline while using v5 losses to design the next candidate.

2. **Replay review for v5**
   Compare new wins and losses against v3/v4 failure modes: midgame control
   collapse, over-defense, source safety, and contested enemy attacks. Current
   v5 losses show **production gaps**, frequent elimination, and weak peak
   economy: median loss peak is only 5 planets and 8 production.

3. **Comet policy**
   Ignore or capture comets based on remaining lifetime and travel cost.

4. **RL-inspired feature audit**
   The public PPO tutorial frames each owned planet as a source decision with
   self, candidate, and global features. The Producer agent adds a second
   checklist: per-planet pressure and a small regroup step. Use both as an audit
   checklist for v5 heuristics, not as a reason to add training code before replay
   evidence supports it.

## 7. Evaluation Checklist

Before submitting the next candidate:

- generated agent compiles;
- Kaggle simulation runs without errors;
- action format is always list-of-lists;
- source planets are not overdrawn;
- sun-crossing launches are rejected;
- at least 30-seed random benchmark is recorded and compared with `roi_reserve_v2`;
- version log is updated;
- known loss seeds are inspected.

## 8. Submission Rule

Submit through the **notebook output** path, not a local `main.py` upload:

```bash
/Users/tuanm.nguyen/Library/Python/3.9/bin/kaggle competitions submit orbit-wars -f outputs/<kaggle-output>/submission.tar.gz -m "<message>"
```

Do not submit a speculative rewrite until it has passed the **Kaggle smoke run**
and has a clear **expected behavior difference** from `roi_reserve_v2`.

## 9. Agent Setup

Keep the agent ladder small:

1. **Baseline**
   `roi_reserve_v3` stays the reference point because it is still the best
   mature public score at `509.9`.

2. **Archive**
   `roi_reserve_v5` stays as the combat-survival archive. Its public score is
   `415.4`, and the replay set shows that the extra safety logic was too costly
   when it was pushed too far.

3. **Next candidate**
   Build `roi_reserve_v6` from the v3 opening shape, then add only one new
   improvement at a time:
   - bounded regroup for surplus ships in pressure hotspots;
   - a milder source-safety gate than v5;
   - no extra notebook unless the model shape changes materially.

4. **Ablations**
   If `roi_reserve_v6` moves in the wrong direction, split it into two
   single-change variants instead of tuning everything together:
   - `v6_source_safety`
   - `v6_regroup`

This setup makes score movement easier to read: if a variant drops, the replay
delta tells us whether the issue is over-defense, over-regrouping, or the
opening itself.
