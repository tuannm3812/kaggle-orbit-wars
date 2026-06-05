# 7. Public Replay Findings

## 1. Scope

Reviewed downloaded public replay JSON for `tuannm3823` and `tuannm3812` submissions on
2026-06-04. Raw replay files are stored under ignored local paths:

- `replays/roi_reserve_v2/`
- `replays/roi_reserve_v3/`
- `replays/roi_reserve_v4/`
- `replays/roi_reserve_v5/`

Generated analysis tables are stored under ignored local path
`outputs/replay_outcome_analysis/`. The reusable analyzer is tracked at
`scripts/replay_outcome_analysis.py`.

The installed Kaggle CLI still does not expose `episodes` or `replay` commands.
Submission ids were read from the Kaggle API submission objects, then replays
were fetched through Kaggle's authenticated episode endpoints:

```bash
GET /api/i/competitions.EpisodeService/ListEpisodes?submissionId=<SUBMISSION_ID>
GET /api/v1/competitions/episodes/<EPISODE_ID>/replay
```

## 2. Current Score Context

| Agent | Submission id | Public score | Reviewed public replays | Wins | Losses |
| --- | ---: | ---: | ---: | ---: | ---: |
| `roi_reserve_v2` | `53322680` | `438.3` then `411.9` for the later v2 notebook submission | 22 | 8 | 14 |
| `roi_reserve_v3` | `53344107` | `509.9` | 33 | 13 | 20 |
| `roi_reserve_v4` | `53349976` | `471.9` | 19 | 9 | 10 |
| `roi_reserve_v5` | `53353907` | `415.4` | 38 | 11 | 27 |

Important scoring note: the starting score is `600.0`, but public score behaves
like an Elo-style rating. The meaningful signal is score movement after public
games plus replay evidence.

## 3. What Wins Look Like

Wins usually come from **early survival into a production lead**. The agent does
not win through one precise attack; it wins when neutral capture is fast enough,
the home planet keeps enough reserve to avoid immediate collapse, and
**planet production** compounds until the opponent is eliminated.

Aggregate patterns:

| Agent | Win replay count | Median first capture | Median final production gap | Median final ship gap |
| --- | ---: | ---: | ---: | ---: |
| `roi_reserve_v2` | 8 | `19` | `57.50x` | `3691.50x` |
| `roi_reserve_v3` | 13 | `13` | `80.00x` | `3280.00x` |
| `roi_reserve_v4` | 9 | `17` | `68.00x` | `3807.00x` |

Representative wins:

| Agent | Episode | Players | First capture | Final production gap | Final ship gap | Replay tags |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `roi_reserve_v3` | `78675610` | 2 | 8 | `92.00x` | `5079.00x` | `fast_opening`, `production_lead`, `ship_lead` |
| `roi_reserve_v3` | `78669936` | 4 | 9 | `96.00x` | `10094.00x` | `fast_opening`, `production_lead`, `ship_lead` |
| `roi_reserve_v4` | `78694666` | 2 | 11 | `92.00x` | `6087.00x` | `fast_opening`, `production_lead`, `ship_lead` |

## 4. What Losses Look Like

Losses are **strategy failures**, not packaging or runtime failures. Current
v3/v4 losses mostly end in elimination. Before elimination, the replay curves
show the same pattern: early capture may happen, but the agent fails to protect
or compound that control into the midgame.

Aggregate loss patterns:

| Agent | Loss replay count | Median first capture | Median final production gap | Median final ship gap | Loss far-action share | Loss enemy-target share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `roi_reserve_v2` | 14 | `37` | `0.00x` | `0.00x` | `38.7%` | `40.5%` |
| `roi_reserve_v3` | 20 | `17` | `0.00x` | `0.00x` | `40.7%` | `46.2%` |
| `roi_reserve_v4` | 10 | `12` | `0.00x` | `0.00x` | `25.6%` | `19.1%` |

The v4 losses are especially useful: even with lower far-action and enemy-target
shares than v3, v4 still gets eliminated. That means the next fix should not be
another small target-weight calibration. We need better **combat valuation** and
**defense timing**.

Representative losses:

| Agent | Episode | Players | First action | First capture | Peak planets | Final planets | Main tags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `roi_reserve_v3` | `78671881` | 4 | 2 | None | 1 | 0 | `far_opening_target`, `slow_or_no_first_capture`, `multiplayer_pressure` |
| `roi_reserve_v3` | `78672450` | 2 | 4 | 17 | 14 | 0 | `lost_midgame_control`, `enemy_target_heavy` |
| `roi_reserve_v3` | `78674966` | 4 | 3 | 11 | 16 | 0 | `lost_midgame_control`, `enemy_target_heavy`, `multiplayer_pressure` |
| `roi_reserve_v4` | `78690953` | 2 | 8 | 10 | 16 | 0 | `lost_midgame_control` |
| `roi_reserve_v4` | `78694282` | 2 | 7 | 12 | 14 | 0 | `lost_midgame_control` |

## 5. Replay Diagnosis

The main weakness has shifted over versions:

1. `roi_reserve_v2` had an **opening-tempo problem**. Fixed reserves delayed
   first launch or first capture, especially from low-production homes.
2. `roi_reserve_v3` improved opening tempo, but losses still show high
   **far-action** and **enemy-target** shares. It often overreaches after a
   small base is established.
3. `roi_reserve_v4` reduced some target-selection symptoms, but did not solve
   **midgame control collapse**. Several v4 losses capture early and reach 14 to
   16 peak planets, then end at zero planets.

The current failure mode is not simply "expand faster." It is:

- launch decisions do not estimate whether the source planet remains safe;
- target decisions do not estimate enemy arrivals or target owner at impact;
- reinforcement is too weak or too late for high-production owned planets;
- four-player matches punish local ROI because third-party pressure changes the
  value of exposed planets.

## 6. Strategy Decision

Keep `roi_reserve_v3` as the active baseline. Its current public score is higher
than v4, and v4's replay evidence does not justify promotion.

The `roi_reserve_v5` challenger now tests this direction with a real model
change around **combat survival**, but current public evidence does not support
promotion: score moved down to `415.4`, with eleven downloaded wins and twenty-seven downloaded losses.

1. Add source safety checks before launch. A source should not spend ships if
   incoming enemy fleets or nearby enemy production can flip it.
2. Estimate target state at arrival. Increase capture cost for enemy-owned or
   contested planets based on expected production and visible fleet arrivals.
3. Add midgame defense mode. Reinforce high-production owned planets under
   threat and stop spending from threatened sources.
4. Prefer defensible clusters in four-player games. A lower-ROI nearby planet is
   better than a far or exposed planet if it keeps the production base compact.
5. Keep opening improvements from v3, but do not create another notebook only
   for calibration. Future notebooks are justified only when agent behavior
   changes around combat valuation, defense, or replay parsing.
6. Borrow the Producer-style regroup pattern, but keep it bounded: only move
   surplus ships, only into nearby pressure hotspots, and only after source
   safety has been checked.
7. Treat the notebook review workflow as a checklist: opening shape, midgame
   safety, pressure redistribution, and target valuation. Ignore the rest.

Judge future variants by public score and new replays, not by the 30/30 random
smoke result alone. v5 reduced some far/enemy targeting symptoms, but its losses
still show **production gaps**, weak peak economy, and frequent elimination, so
the next fix needs to restore opening production growth while preserving source
safety.
