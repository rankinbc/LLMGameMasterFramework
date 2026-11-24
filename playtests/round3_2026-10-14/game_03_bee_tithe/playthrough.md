# The Bee Tithe: playthrough (game_03)

Opening presented to the player: title, premise, the 8-line sheet printed by `python engine.py rules`, Goal: total mood 36 at the Harvest Count after turn 16. Lose if any steading hits mood -3. Turns: 16.

Format per turn: turn | engine status line | player choice | one line of narration.

T1 | Light 8/14 | Approval 6/36 | Mood O1 B1 M1 V1 F1 H1 | Sun O1 B2 M2 V2 F1 H2@ | Gift 1 light to Hearth (+6 mood, blessing at its peak) | Hearth takes one light and glows; the front falls on Barley, the first of the tied-sunniest fields, so the front hunts the sun.
T2 | Light 7/14 | Approval 12/36 | Mood O1 B1 M1 V1 F1 H7 | Sun O2 B0 M3 V1 F2 H1@ | Gift 1 light to Orchard (+6, walk 1) | Barley sits at sun 0 and is slipping, so I stepped toward it; the front chose Mill, the sunniest, and I noted the pattern holds.
T3 | Light 5/14 | Approval 17/36 | Mood O7 B0 M1 V1 F1 H7 | Sun O1@ B1 M1 V2 F3 H2 | Gift 1 light to Barley (+6, walk 1) | Barley, the weakest field, comes back from 0 to 6; the front clips Fen, the sunniest, again.
T4 | Light 3/14 | Approval 23/36 | Mood O7 B6 M1 V1 F1 H7 | Sun O1 B2@ M2 V3 F1 H3 | Gift 1 light to Mill (+6, walk 1, last turn of the full blessing) | Mill rises to 7 and the pantry of light is nearly empty; the front cuts Vine.
T5 | Light 1/14 | Approval 29/36 | Mood O7 B6 M7 V1 F1 H7 | Sun O2 B3 M3@ V1 F1 H4 | Gather at Mill (+3 light, no walk) | The blessing has faded to +2, so I turn to the bees and fill the baskets; the front clips Vine again.
T6 | Light 4/14 | Approval 29/36 | Mood O7 B6 M7 V1 F1 H7 | Sun O1 B3 M3@ V1 F2 H2 | Gather at Mill (+3 light) | Light is not the pressure yet; I bank 3 more before the last cheap blessing turns, and the front takes Barley.
T7 | Light 7/14 | Approval 29/36 | Mood O7 B6 M7 V1 F1 H7 | Sun O2 B1 M2@ V2 F2 H3 | Gift 2 light to Vine (+6, walk 1) | Vine, the first of my two neglected fields, comes up to 7; the front keeps stripping the sunniest field and Barley is the latest victim.
T8 | Light 4/14 | Approval 35/36 | Mood O7 B6 M7 V7 F1 H7 | Sun O3 B2 M3 V2@ F2 H1 | Gift 2 light to Fen (+6, walk 1) | Every steading now sits at 6 or 7 and the sum is over the goal, but the count is not until turn 16 and the dark is coming.
T9 | Light 1/14 | Approval 41/36 | Mood O7 B6 M7 V7 F7 H7 | Sun O1 B3 M2 V2 F2@ H2 | Call a favor at Fen (mood -2, light +8) | Fen pays its favor and the baskets fill to 9; the long night begins and the front now strikes two fields, darkening Mill.
T10 | Light 9/14 | Approval 39/36 | Mood O7 B6 M7 V7 F5 H7 | Sun O2 B1 M0 V1 F2@ H3 | Gift 2 light to Fen (+3 after the ceiling) | Light is plentiful, so I top Fen back to 8; Mill goes dark and loses a point at dusk, Orchard is struck down to sun 0.
T11 | Light 7/14 | Approval 41/36 | Mood O7 B6 M6 V7 F8 H7 | Sun O0 B0 M1 V2 F3@ H1 | Gift 1 light to Orchard (+1, walk 2) | I walk toward the darkened fields so I stand where the decay is; Barley slips a point at dusk and the front cuts Fen and Vine.
T12 | Light 4/14 | Approval 41/36 | Mood O8 B5 M6 V7 F8 H7 | Sun O1@ B0 M2 V0 F1 H1 | Gift 1 light to Barley (+3, walk 1) | A cheap dark-field gift restores Barley to 8 and spares it dusk unrest; the front cuts Mill and Orchard to nothing.
T13 | Light 2/14 | Approval 43/36 | Mood O8 B8 M6 V6 F8 H7 | Sun O0 B1@ M0 V0 F2 H1 | Call a favor at Mill (mood -2, light +8, walk 1) | Light had run thin, so Mill pays its favor and the baskets refill to 9; Mill's lost mood makes room for a later gift. Orchard and Vine slip at dusk.
T14 | Light 9/14 | Approval 39/36 | Mood O7 B8 M4 V5 F8 H7 | Sun O1 B0 M1@ V1 F0 H0 | Gift 2 light to Mill (+4, no walk) | Mill climbs back to 8; Barley, Fen and Hearth each lose a point to the dark at dusk, and the Golden Hour is announced.
T15 | Light 7/14 | Approval 40/36 | Mood O7 B7 M8 V5 F7 H6 | Sun O0 B1 M0@ V2 F1 H0 | Gift 1 light to Vine (+3, Golden Hour doubling, walk 1) | Vine fills to 8 ahead of the final count. ENGINE BUG: the game ended here with "the Harvest Count found approval 40", so turn 16's action never happened (the count fired after turn 15's dusk). See the bug note below; the game was restarted with the same seed after the fix.

## Engine bug note (found at the end of turn 15)

The engine ended the game right after turn 15's dusk with "the Harvest Count found approval 40". The rulesheet says the count comes right after the player's action on turn 16, so the 16th action was skipped and `integrity` was empty. Cause: `check_end` runs twice per turn (after the action, and again after dusk when `_turn` is already the next turn), and my count test used `_turn >= TURNS` alone, so it fired at the dusk of turn 15. Fix: the count fires only when `_turn == TURNS` and a steading was visited this turn (or `_turn > TURNS`), plus a rule test that plays turn 15 into turn 16. The bug had also hidden the Golden Hour's last turn from every selftest, so the game was easier than the tuning said (heuristic win rate 0.75 after the fix); GOAL was retuned 36 to 40 and `check` round 4 was clean. The game was restarted with the same seed (151858) by replaying the 15 saved actions from history.jsonl. States were identical on replay, except that status lines now read /40 instead of /36. Turns 1 to 15 above were played under goal 36; the lines are otherwise unchanged.

## Turn 16 (after the fix)

T16 | Light 5/14 | Approval 40/40 | Mood O6 B7 M7 V8 F7 H5 | Sun O0 B0 M1 V0@ F2 H0 | Gift 1 light to Hearth (+3 after the ceiling, Golden Hour x2, walk 2) | Hearth, the lowest field, is topped to 8 with the last light; the Harvest Count reads 43 against 40.

## Ending

Result: win. The Harvest Count found approval 43 against a goal of 40, after 16 turns. Final: Light 2/14, moods O6 B7 M7 V8 F7 H8, two favors called (Fen turn 9, Mill turn 13).

Autopsy (shown to the player):
1. The game turned on turn 9: the best win chance on offer rose from 65% to 95% across your favor call at Fen, as the long night began.
2. The best move you missed was on turn 14: gathering at Mill rates 100% against 28% for your two-light gift there; turns 12 and 11 had the same shape (a favor at Mill or Vine rated 82% and 80%, against 20% and 28% for the small gifts you made).
3. 94% of your turns were hard choices and no stretch was flat.
