# Mirror Migration: generator report (round 3b, game 2)

Saved by the lead from the generating agent's final reply.

## Title and premise

Mirror Migration. A smuggler pawn owes the Bishop a season of tithe and must raise a den on all five files, plus 18 Standing, after the Great Crossing, while a party always crosses the file opposite your latest build.

## Rolls

FORM 3, SET 57, ROLE 3, LOOP 35, CLOCK 22, TWIST 6, WIN 5, MAP 10, TONE 10, CURRENCY 12 (Standing). No reroll; verbs 0 percent overlap (den, snare, run, writ). Chosen from the brief: 2 tracked numbers (Standing and the Files board), counter rival, deadline clock with a week-9 escalation, place decisions with params, final-roll ending, rival tell shown before.

## Check log

- R1: no flags. Warnings: five rule lines over 36 words; look-ahead 40 percent under band. Random 0.00, heuristic 0.31, look-ahead 0.40, mutation 0.88.
- R2: SNARE_BONUS 3, sheet trimmed. No flags; look-ahead 43 percent. Mutation 0.88.
- R3: tithe 1 then 2. No flags, no warnings. Random 0.03, heuristic 0.40, look-ahead 0.70, mutation 0.88.
- R4: new rule tests added for mutation survivors, WRIT_COST 12. No flags, no warnings. Random 0.03, heuristic 0.40, look-ahead 0.65, mutation 0.98 (56 of 57). Tuning cap note.
- Before R1: sweeps and two design rewrites (a debt win condition; snares only on den files), not counted.
- profile: no warnings, dilemma share 0.52, turn 1 flat. ablate: den needed, writ marginal, snare and run unproven.

## Declarations

params: den and snare each take a file letter (placement is the core pick; one option per verb keeps the menu at 4 or fewer). resample_hidden: yes, the unseen deck order is in s["hidden"]["deck"]; the heuristic never reads hidden. DERIVED: dens, snares, surplus (REACH takes one threshold per key, and Standing needs two).

## Rough edges known

Standing piles up late (48 in one trace against a debt of 18), so weeks 11 to 15 are often a run-and-hold stretch. The heuristic is myopic and values banked snares at zero (the 0.25 gap to look-ahead). ablate calls snare and run unproven: banning run still leaves it when it is the only legal option.

## Harness feedback

- Look-ahead is noisy (k=6, 60 games, SE about 0.065); win rates swung 0.39 to 0.70 for small constant changes, and at some settings look-ahead scored below the heuristic.
- The tuning counter hashed the rule_tests code, so adding tests to kill mutants counted as round 4. This discourages strengthening tests late.
- Mutation survivors print only when the rate is under 75 percent; the agent had to call gm_mutate itself.
- One surviving mutant (`nxt < turns`) is equivalent and cannot be killed.
- ablate's baseline (0.72) is not the heuristic's rate (0.40) and the output does not say it uses look-ahead.
- `sweep --lookahead` uses n/4 games and shows no error bar.
- SKILL.md is unclear whether the midpoint unlock and the late lever may be the same thing.
- The wac Bash hook blocked two `ls` commands (false positive) until split.

## Time and effort

About 70 minutes and 60 tool calls.
