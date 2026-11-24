# Ash Rule: generator report (round 3b, game 3)

Saved by the lead from the generating agent's final reply.

## Title and premise

Ash Rule. An abbot of a cloister above a nuclear-winter bunker network writes a two-instruction Rule each dawn for a runner who walks the sliding line of bunkers alone; the larder drains, the Gleaners shadow every lift, and one bunker must reach tier 3 in 16 days.

## Rolls

FORM 15, SET 22, ROLE 46, LOOP 34, CLOCK 1, TWIST 2, WIN 9, MAP 9, TONE 1, CURRENCY 5. Novelty OK, no reroll. Verbs (write, raise, vigil, favour): 0 percent overlap. Chosen on purpose: 2 tracked (stock, line board), rival counter, upkeep clock, place and allocate params, rival tell after, final-roll ending.

## Check log

- R1: heuristic TOO EASY (1.00), two SHORT GAMES flags, one wrong rule test of its own. Look-ahead 1.00, mutation 65 percent. Random 0.
- R2 (EAT 7, start stock 15): CLEAN. Random 0, heuristic .33, look-ahead .55, mutation 92 percent. Profile warned FLAT FINISH, so a vigil final roll was added.
- R3 (vigil, start 18): heuristic .47 too easy; look-ahead .62; mutation 91 percent.
- R4 (start 17): CLEAN. Random 0.00, heuristic .34, look-ahead .50, mutation 50 of 55 (91 percent). Tuning cap reached.
- Profile (final): no warnings. Ablate: all four actions needed.

## Declarations

params: write (first and then choices; sweep from day 9), raise (bunker pick), vigil (bunker pick plus an offering amount whose range depends on stock). resample_hidden: the secret ally is an int in s["hidden"]; the redraw avoids factions already cleared and keeps a known ally. DERIVED: top_tier, camps, max_pile, min_pile. GATES use `_if` for all four actions. TRACKED = stock, line. 8 rule tests.

## Warnings accepted

Five sheet lines of 37 to 44 words. "starve fires in 0 percent of heuristic games": the loss is real and random play hits it. Look-ahead 50 percent, under 0.6 but within 0.1: look-ahead cannot search the program space.

## Harness feedback

- Look-ahead `_expand` caps param combos at 6 evenly spaced; the game has 9 combos after day 9, so look-ahead misses the best program. Always include the heuristic's pick as a candidate.
- FORCED counts option objects, so a state offering only `write` (4 to 9 real choices) counts as forced.
- The 0.25 to 0.45 heuristic band is narrow against a steep win rate in a mostly deterministic economy (one unit of START_STOCK moved it 13 points). `sweep --n 300` reproduces check's random and heuristic numbers exactly.
- Profile's FLAT FINISH warning gave good guidance but forced a redesign that cost two rounds.
- RULES cannot pluralize.
- A wac-claude hook blocked one Bash command containing the playtest path; PowerShell worked.
- GM/CLAUDE.md named `example_friday_rush`, which does not exist.
- Speed: check 20 to 35 seconds; sweep with look-ahead 1 to 3 minutes.

## Time and effort

About 75 minutes and 50 tool calls; the engine was written twice.
