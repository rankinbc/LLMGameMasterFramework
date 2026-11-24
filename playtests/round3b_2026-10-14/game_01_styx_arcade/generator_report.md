# Styx Arcade: generator report (round 3b, game 1)

Saved by the lead from the generating agent's final reply.

## Title and premise

Styx Arcade. In a 1980s arcade where the cabinets eat the coins of the dead, a smuggler in the Ferryman's debt must accuse the Skimmer, with Proof stamped on one regular's file, before the Owner's 12-night audit.

## Rolls

FORM 5 deduction, SET 50 arcade, ROLE 3 smuggler with a debt, LOOP 16, CLOCK 5 then rerolled once to 22 (the brief said clock_shape must leave "decay"), TWIST 18, WIN 15 name the culprit, MAP 10, TONE 5, CURRENCY 11 evidence. Novelty OK; verbs 0 percent overlap.

## Check log

Before round 1: about 25 free checks and 30 sweeps across three redesigns (early flags: heuristic wins of 100 percent, short games, early wins, an unreachable tag, crashing rule tests).
- Round 1 of 4: CLEAN. Warnings: rules 3 to 5 at 37 to 41 words; `seized` and `voided` rare; look-ahead 32 percent and worse than the heuristic. Random 0.00, heuristic 0.39, look-ahead 0.32, mutation 87 percent (60 of 69).
- Round 2 of 4, after more tests and tying the accusation to the file's regular: CLEAN, same warnings. Final: mutation 97 percent (67 of 69).
- Profile: no warnings. Ablate: ledger unproven.

## Declarations

params: bribe amount, swap (who plus count), ledger topic. resample_hidden: the Skimmer index is redrawn among regulars consistent with the reports learned. DERIVED: suspects, rate_flip. TRACKED is 2 (Hearsay, Proof); Rate and Suspects are shown but not counted.

## Warnings accepted

Sheet lines of 37 to 41 words; rare events by design; the ledger is a late lever and an odd element kept despite the ablate lead; look-ahead under band and below the heuristic although profile shows large spreads (the harness look-ahead is noisy on repeated small income and info choices: the heuristic identified the Skimmer by night 6.6, the look-ahead by 10.1).

## Harness feedback

- Look-ahead ties: with over 8 candidates the first pass uses 3 rollouts and finalists tie in list order, not toward the heuristic's pick.
- Params validation covered declared params only; an undeclared `bribe` passed, so `apply` had to clamp.
- `rng.drift` is not scripted in tests.
- The skill says about 40 words a line but the check warns above 36.
- TRACKED versus "board" is unclear (roster, rate); the brief rewards a count other than 3.
- A flag for any win before the midpoint counts lucky random wins; the "tag never fired" flag pushed the agent to drop outcome tags.
- The 4-round cap is porous: `--free` and `sweep` are unlimited.
- Timing: check 15 to 60 s; `sweep --lookahead` 3 to 10 min; look-ahead selftest with k=20 over 10 min.

## Time and effort

About 150 minutes and 100 tool calls; the engine was rewritten three times (a flat grind, then a per-suspect Proof file, then scarce witnesses).
