# Round 3c: three games generated under harness v3, each reviewed by its author's reviewer and then by a fresh QA agent

Date: 2026-10-14 to 15. Method: three agents followed the updated `/play` skill (harness v3: strict command line, one turn semantics, mutation over helpers and f-string text, vocabulary lint, `texts`, TRACKED roll, mandatory independent review). Each ran the review step with a subagent (one of them twice) and fixed what it found. Then a fresh QA agent that had seen none of that played each game at least three times, sent about 50 to 90 hostile inputs, compared every rule line with the code, and ran an independent rule model against the engine. Generator reports are `generator_report.md`; QA reports are `qa_report_independent.md` (game 1 and 2) and `qa_report.md` (game 3).

## Results

| # | Game | Generation | Author-side reviews | Mutation score at the end | Independent QA, S1 to S3 | Of which game | Of which harness |
|---|------|-----------|---------------------|---------------------------|--------------------------|---------------|------------------|
| 1 | Audit of Reeds | about 3.5 h, 4 rounds | 2: one S2 and about 15 S3 fixed | 160 of 160 | 4 (0 S1, 0 S2) | 3 | 1 |
| 2 | Fever Card | about 85 min, 4 rounds | 1: no S2, about 8 S3 fixed | 100% | 7 (0 S1, 0 S2) | 6 | 1 |
| 3 | Sluice Street Audit | about 110 min, 3 rounds | 1: one S2 and about 10 S3 fixed | 134 of 134 | 5 (0 S1, 0 S2) | 3 | 2 |
| | Total | | | | 16 | 12 | 4 |

An independent rule model matched every engine on every step in every game (about 6,500 simulated games across games 2 and 3, and the QA's own games for game 1). No arithmetic bug has been found by any independent oracle in any of the eight games attacked in rounds 3b and 3c.

## Round 3b against round 3c

| | Round 3b (harness v2, no review step) | Round 3c (harness v3, with review) |
|---|---|---|
| S1 or S2 found by independent QA | about 8 in 5 games (1.6 a game) | 0 in 3 games |
| S3 found by independent QA | about 28 in 5 games | 16 in 3 games (5.3 a game) |
| Of which in the harness | 18 of 36 (3.6 a game) | 4 of 16 (1.3 a game), all cosmetic |
| Of which in the game | 18 of 36 (3.6 a game) | 12 of 16 (4.0 a game) |
| What `check` caught | 0 of 36 | 0 of 16 (the author-side reviews caught about 35 more before the QA saw the games) |

The command line and the hostile-input class is gone. What is left in the harness are cosmetic error texts, now fixed. The game-level S3 count did not fall: a first review removes about ten wording and sheet bugs, and a fresh reviewer still finds three to six. The author-side checks and the reviews are good at wrong numbers and bad at wording, ordering and what the sheet leaves unsaid.

## What the independent QA found in the games after two layers of review

- Wording and order: events narrated before their cause ("the keepers give you nothing" before the sound that caused it); a game-ending dusk that still announces the next night (this was in 1,904 of 3,000 simulated losses in Fever Card; a check for it now exists); two fatal events at one dusk blamed by check order, not by what happened first; "The bookings stand" printed when nothing is booked; a tell on the last dusk.
- Sheet against code: behaviors the code has that the sheet never states (Stoke vanishes after a night, a known guard moves with the stir and the barge, a pass that can never be Lanced); a status line with four fields against a TRACKED of three; a pay line that lets the player infer the ground the sheet calls hidden.
- Labels and options: a rolled option with no odds in its label, a hopeless option offered, labels that under-report.
- Tests: a rule-test assertion on a wording the game no longer emits.
- Design smells (S4): a flat finish or a dead tail in two of three games (`profile` had said so only mildly), levers that `ablate` calls unproven, a free income loop.

## Harness changes made from this round

Both the generators' feedback and the QA reports led to these (all with tests; 87 tests, all green):

- A game that ends at dusk may not narrate tomorrow (lint, reference fix, mutant); `self.finish()` for a fatal event.
- The autopsy's swing cause no longer blames the player when the best move was followed by a bad roll.
- Dev commands, unknown commands, a missing or damaged state file, `NaN`, `#N` with conflicting JSON, and a trailing argument all give clean refusals; every refusal inside `step` says the state is unchanged; `replay --apply` rebuilds a damaged state.
- `{KEY|noun}` is accepted on the sheet; BOUNDS, REACH and GATES may name constants and derived values; possessives are not unknown words; `texts` keeps signs; `need 0+` prints as `need 1+`; whole-number floats are normalised.
- A better heuristic or new tests is not a new tuning round.
- Rule-test helpers: `t.in_order`, `t.label`, `t.status`, scripted `drift`, `t.offered` that validates named params.
- Skill: events that look ahead come after every fatal check; rolled options show their odds; option and fact consistency; assert the order of events; repeat the independent review with a fresh reviewer until a round finds no S1 or S2 and at most two S3 (three rounds at most).

I introduced a regression while editing the harness during this round (a gate lookup that ignored `_turn`, live for a few minutes). The Fever Card generator worked around it. Harness edits now wait until no agent is running.

## Where the quality bar stands

- Gameplay-affecting bugs (S1 and S2): none found by independent QA in the three v3 games; none arithmetic in eight games. The rules the player reads and the numbers the engine uses agree.
- Wording and sheet bugs (S3): about four per game after review. These are real but cosmetic: a line out of order, a sheet that leaves a behavior unsaid, a label without odds.
- The process cost is high: 85 minutes to 3.5 hours per game, mostly review and tuning, plus 20 to 25 minutes per independent QA.

Options not taken, and why: a scaffold (the time goes to design and tuning, not boilerplate, and a template pulls every game toward one skeleton); a hard flag on `profile` warnings (the dead tail and flat finish remain advice, because gating them would tune games toward one tension shape).

## Next

The rest of the roadmap needs a go-ahead and is untouched: the LEARN axis, Threads (recurring cast, loose ends, foreshadowing, prophecy), the MECH axis, a rendered board. A reasonable next measurement is a fourth validation round after a month of real play, comparing bugs that players report with what this process finds.
