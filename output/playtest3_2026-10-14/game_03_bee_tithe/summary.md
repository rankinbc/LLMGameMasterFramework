# Game 3: The Bee Tithe (pilot round 3)

Written by the lead from the playing agent's report (the agent's Write tool refused report files).

## Title and description

The Bee Tithe: a mythic trading run. The last Beekeeper of Orrin Vale carries stored sunlight between six steadings, gifting it for goodwill (mood) and calling in favors, while a storm front hunts the sunniest fields. Goal: total mood of 40 at a Harvest Count after turn 16.

## Rolls

FORM 1, SET 60, ROLE 34, LOOP 12, CLOCK 10, TWIST 24, WIN 18, MAP 8, TONE 5, CURRENCY 6 (Light). No reroll.

Changes because of `sameness brief`: no cash; the front's strike is shown after it lands and its temper is hidden; the ending is a count after the last action plus a doubling Golden Hour; the player is a negotiator. Not achieved: tracked_count 2 (honestly 3) and decision_unit (the contract is a menu).

## Result

Win, approval 43 of 40, turn 16 of 16.

## Fun rating: 6

Early blessing choice, dusk decay, favors and the Golden Hour gave real choices in turns 1 to 4, 9, 10 and 14 to 16. Turns 5 to 8 and 11 to 13 were routine gather-then-gift shuffles, the hidden front temper was readable after two strikes, and a 24 to 30 option menu is heavy for chat.

## Bugs found in play

1. **Turn-boundary off-by-one (real engine bug).** The Harvest Count fired after turn 15's dusk, so the 16th action was never offered. `integrity` was empty and `check` was clean. Cause: `check_end` runs after the action (`_turn` is this turn) and after dusk (`_turn` is the next turn), and a `_turn >= TURNS` test fired in the second phase. `check` could not catch it: no universal check compared actions taken with the budget, the rule test asserted `check_end` on a hand-built state instead of stepping from turn 15 into 16, and the trace showed `T16` then `END` with no `do:` line, which the agent read past. Side effect: the bug hid the last Golden Hour turn from every selftest, so tuning was wrong (heuristic win rate 0.33 became 0.75 once fixed).
2. Nothing else broke.
3. Felt off: gifts into a steading at the mood ceiling were offered at "+0"; "Gift 2" and "Gift 3" often showed the same gain; two sheet lines carried 3 to 4 mechanics each.

## Check log

R1: lookahead EARLY WIN (a rush won before the midpoint) and RULETEST rule 7 (test-helper trap). R2: CLEAN. R3: CLEAN. R4: CLEAN, cap note. Final random 0.00, heuristic 0.37, look-ahead 0.80. About 85 tool calls, 60 minutes, of which about 25 waiting on `check` (3 min a round), `ablate` (7 to 11 min) and `profile` (1.5 min) with a 30-option menu.

## Harness feedback

- Nothing detects a game that ends before its last action; add a `check_end`-depends-on-`_turn` test, a trace annotation, or an actions equal budget rule.
- The contract never says `check_end` runs twice a turn with different `_turn` meanings.
- `T.offered` ignores args when exactly one option has the id.
- The 8-line limit counts lines only; the sheet had 8 lines and about 14 mechanics.
- tracked_count, decision_unit and player_frame cannot be enforced.
- The heuristic band invites tuning the heuristic instead of the game; the look-ahead minus heuristic gap is the better signal.
- Autopsy continuation uses a weak endgame heuristic: a player who won by 3 was told the gift he made rated 28 percent against 100 percent for gathering.
- The MENU warning fires when every option has a group. `ablate` and `check` are slow with big menus.
- Add an `engine.py replay` command that re-runs history.jsonl after an engine fix.
- Step 7 should say "count the player's actions; they must equal the budget".

## Autopsy as shown to the player

1. The game turned on turn 9: the best win chance on offer rose from 65 percent to 95 percent across your favor call at Fen, as the long night began.
2. The best move you missed was on turn 14: gathering at Mill rates 100 percent against 28 percent for your two-light gift there.
3. 94 percent of your turns were hard choices and no stretch was flat.
