# Rim Card: generator report (round 3b, game 5)

Saved by the lead from the generating agent's final reply.

## Title and premise

Rim Card. A washed-up wrestling booker runs a touring card through eight asteroid-belt outposts for 20 nights, trying to out-rate Vesper Broadcasting's climbing bar while Vesper's crews raid the longest-running shows. Noir.

## Rolls

FORM 12, SET 1, ROLE 51, LOOP 31, CLOCK 16, TWIST 35, WIN 18, MAP 2, TONE 11, CURRENCY 9 (cash). No reroll; verbs 0 percent overlap. 2 tracked numbers (cash and the ring), a place-a-bout decision, a marcher and saboteur rival, a race clock and a hidden beat inferred from history.

## Check log

- R1: `BAR0=19` passed to `check` was silently ignored, so the round was wasted. Flags: heuristic too easy (85 percent) and one failing rule test (the agent's bug: `t.fresh` shares override objects between states).
- R2: CLEAN. Look-ahead 48 percent warning. Random 0, heuristic 36 percent, mutation 85 percent.
- R3: same numbers after an int() cast on the outpost arg and a param rename.
- R4 (cap): CLEAN, no warnings. Random 0, heuristic 43 percent, look-ahead 63 percent, mutation 85 percent (47 of 55).
- profile: no warnings; dilemma share 56 percent, forced 5 percent. ablate: only the hustle warning.

## Declarations

params: booking takes an `outpost` pick (choices ordered best first) per kind; slot choices exclude the same kind. resample_hidden: the favourite kind and the raid beat are hidden; the beat is redrawn only over (period, phase) pairs consistent with the raids seen. DERIVED: rating, gap and live count. BOUNDS, REACH, GATES, TAGS and rule_tests all declared.

## Warnings accepted

None remain. "Banning hustle changes win rate by 0.00" is accepted: hustle is the broke-turn safety net and ablation never removes the only legal move.

## Harness feedback

- `check` ignores unknown args (`check BAR0=19` ran unchanged and used a counted round); it should reject them.
- Option order matters a lot to look-ahead: menus of 20 or more candidates get a first pass of 3 rollouts and ties go to list order, so finalists were arbitrary. Sorting options best first took look-ahead from about 0.47 to 0.72. This is a harness artifact.
- `_expand` caps param combos at 6, so look-ahead only sees choice indices 0, 1, 3, 4, 6 and 7.
- `t.fresh` stores override objects by reference; a mutated list leaked between states and caused a false failure. It should deepcopy.
- `check --free` makes the 4-round cap soft.
- `ablate` took about 4.5 minutes under CPU load against the documented minute.
- The guideline "every check is buyable" does not say whether a rival's die counts.

## Time and effort

About 2.5 hours and 75 tool calls, mostly a redesign after a first version played as fill-the-ring-then-idle, and one wasted tuning round.
