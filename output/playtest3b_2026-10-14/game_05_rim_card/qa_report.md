# QA report: Rim Card

## Bugs
Numbers are clean: 800 fuzzed games (16,000 steps) matched a rule-derived oracle (rating, cash, bar, raid target, ring, status, option gates, gain_if_booked): 0 mismatches.
1. S1, harness. `new 909; step hustle null` advances night 1 to 2, then a TypeError traceback fires before history.jsonl or rolls.log get a line; `replay` later halts. Class: arg validation, save before log. check and rule tests never drive CLI step, so no.
2. S2, harness. `step` after the end exits 0 and appends bogus lines to history.jsonl and rolls.log; `autopsy` then reports turns_played 21 (sheet: 20). `options` still lists 7 actions on an ended game. Class: no _ended guard; check could assert options(ended)==[].
3. S3. Malformed JSON (`step book '{bad'`) and `new abc` print tracebacks; state unchanged.
4. S3. `outpost:true` books outpost 1; `step "#1" '{"kind":"belt","outpost":3}'` books a Belt, not #1; junk args are stored in history.
5. S3, sheet. Rule 6 says the bar "drops 2", but from night 13 the dusk climb is 2, so the cut nets 0 and the bar never falls (seed 101 night 17, 52 to 52). Wording; check cannot see it.
6. S3, sheet. Rule 8 never says a main event uses the night's one action; rules 1 and 8 read as two bookings. r8 never steps a main.
7. S3. Replacing a Hub event is silent, unlike "bumped" at outposts; Rating 63 to 55 unexplained (seed 202 night 14).
8. S4. Belt after night 18, Tag after 19, anything on night 20 cannot go live, yet is offered with positive gain_if_booked.
9. S4. Status line has no night counter; glyph key (lowercase = travelling) is on no sheet.
10. S4 balance. Heuristic wins 20, 53, 67 percent by hidden raid period 3, 4, 5 (n=600). Brute-force max Rating is 65, yet 25 percent of games end with bar 66 or more (0 wins). Rating 57.6 sd 8.4 vs bar 61.5 sd 5.4: dice decide.
11. S4. Cash is dead late (15 to 40 unused); 9 percent of turns have one option.
12. S4. Literals: die size 6 in rng.check; hub["since"] never read; BOUNDS far looser than reachable.

## Games played
- 101 careful: win 62 v 56, 20 turns, 6/10.
- 202 greedy: loss 63 v 74, 20, 4/10.
- 303 hoard: loss 27 v 72, 20, 2/10.
- 404 counter-program nightly from 13: loss 38 v 62, 20, 3/10. Not dominant: 6 percent wins in sim vs 43 heuristic.
- 505 careful: loss 63 v 64, 20, 5/10.
- 606 careful: loss 63 v 64, 20, 5/10.
Counters matched budget. Bad ids, args, ranges, `#99`, `#0`, missing params all refused with state.json byte-identical.

## Rule-test gaps
Mutation survivors (47/55 killed): Hub travel countdown, die size, starting since. Unpinned: Hub going live over time; a favourite Hub with no matching outposts scores +2; main uses the night; raid on night 20; visible, status, gain and option order (extra mutants on helpers: 38/57); resample_hidden.

## Autopsy and replay
Clean game 606: replay ok (20, matches saved state); autopsy 23 s, plausible. After bug 1 or 2, replay halts and autopsy counts 21 turns. `check --free` CLEAN in 64 s (heuristic 0.43, lookahead 0.63); it could not catch 1 to 4 or 8 to 10.

## Fingerprint
In qa_fingerprint.json.

## Overall bug rate
7 (S1 to S3): 4 harness, 3 sheet or text. Unverified: look-ahead strength; fun ratings are subjective.
