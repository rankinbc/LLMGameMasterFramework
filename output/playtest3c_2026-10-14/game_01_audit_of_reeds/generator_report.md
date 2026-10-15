# Audit of Reeds: generator report (round 3c, game 1)

Saved by the lead from the generating agent's final reply. This agent had an Agent tool and ran the independent review twice.

## Title and premise

Audit of Reeds. The Bureau of Sleep is auditing a dreamer's river delta, and the player, its siege engineer, must chart all seven reaches before the Ferryman's barge carries the dream out to sea and wakes it.

## Rolls

FORM 10 (heist), SET 58, ROLE 14, LOOP 11, CLOCK 16, TWIST 2, WIN 11 (map the whole board), MAP 6 (branching delta), TONE 5, CURRENCY 11 (Evidence, called Soundings), TRACKED 3 (Soundings, Drill, Charted board). Novelty OK, verbs 20 percent overlap with Mirror Migration.

## Check log

- Round 1: CLEAN. Random 0.01, heuristic 0.43, look-ahead 0.64, mutation 139 of 139.
- Round 2: CLEAN; a roll helper clamps "need 0+" to 1+.
- Round 3 (after review 1): CLEAN, look-ahead 0.68, mutation 157 of 160, then 160 of 160 after pinning the survivors with scripted-dice tests.
- Round 4 (after review 2): CLEAN, tuning cap reached.
- Final `check --free`: no flags, no warnings. Before round 1 it tuned with `sweep` and `selftest` only.

## Independent review (run by the generator, twice)

- Review 1: no S1. One S2: the sheet said the breach rolls against "it and its mouths" but the code used only uncharted reaches (the sheet was fixed). S3, all fixed: sheet omissions (elimination, branch and fork terms, breach minimum), a sound label that under-reported the first friend contact, 0-based args (now 1-based), a fixed 3/2/2 house split (now drawn per seed), confusing wording.
- Review 2: no S1 or S2. S3 fixed: a stale tell on the last dusk, a +3 ward kept on a charted reach, a misleading label, sheet gaps for the barge and the breach, a `not_friends` inconsistency, a hard-coded breach "2" (now BREACH_MIN).
- Left as S4 or harness: a friend-reach sounding farm (+2 a turn, bounded by turns); the barge can be parked on a charted reach by charting both mouths.

## Texts review

`texts` showed "need 0+" in roll events (clamped), an awkward "no roll wins unpushed" label (replaced), possessives in events (removed), "charted alike" barge tie wording, "fresh soundings" wording, a stale final-dusk tell. The last full read found no stale words or bad plurals.

## Warnings accepted

None from `check`. `ablate` marks train and breach unproven and writ marginal, read as look-ahead noise; all three kept. Heuristic win rate 0.43 near the 0.45 ceiling. profile clean: 69 percent of turns consequential, no flat stretch.

## Harness feedback

1. `{KEY|noun}` was flagged "not on the rulesheet". Fixed.
2. The VOCAB check false-positived on possessives. Fixed.
3. `RNG.check` printed "need 0+". Fixed (clamped to 1+).
4. `t.offered` and `t.label` returned False silently when a param is missing. Fixed.
5. `step` with `{"reach":1.0}` matched the option but was not normalised, and NaN reported "engine crash". Fixed.
6. `step "#N" '<json>'` let the JSON override the picked option. Fixed.
7. The harness files were edited by the lead while this agent's reviewer worked (00:18, 00:20, 00:25).
8. Layout numerals in RULES ("2 (East)") are unavoidable.

## Time and effort

About 3.5 hours of wall clock, much of it waiting on two reviews of about 25 minutes with heavy CPU contention; 150 of its own tool calls plus 2 subagents (about 190 calls). Engine plus tests is about 1,000 lines.
