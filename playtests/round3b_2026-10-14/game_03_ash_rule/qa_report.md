# QA report: Ash Rule (game_03_ash_rule)

Method: 6 full games by CLI (3 hand-played, 3 scripted policies), plus 30 mixed-policy fuzz games. An independent oracle built only from the rulesheet and visible JSON checked stock, piles, camps, status line and turn counter after every step: zero numeric mismatches in about 36 games. Vigil, fractional params and sweep-at-end-of-line were tested on a scratch copy (START_STOCK 60). engine.py was not edited.

## Bugs

1. S2. Vigil `offering` accepts non-integers. Scratch copy: `new 9`, raise one bunker twice, `step vigil '{"bunker":"<it>","offering":1.5}'` gives "Stock 25.5" and "need 2.5+". Class: param spec lacks `"step": 1` and the harness does not treat integer min/max as integer. check/rule tests should catch: r5 and the fuzz only try integers.
2. S2. Step after the game ended appends a phantom row to history.jsonl and rolls.log (state.json unchanged). Repro: finish a game, `step write '{"first":"take","then":"take"}'`, `step "#1"`; history 13 to 15 rows. Autopsy then shows turns_played 17 on a 16-day game (game 1) or forced_turns [9,13,13]. Class: harness (`_step` returns early but the CLI still logs). check does not drive the CLI past the end.
3. S2. Second Gleaner camp lands at dusk of day 8, not day 9. Sheet: "1 a dusk, 2 from day 9". advance() runs after _turn is incremented, so `>= MID` fires one dusk early. Repro: seed 202, day 8 `write take,walk` gives two camps; "second crew arrives" prints after them. Rule test r6 pins this via `advance(turn=MID)`, so it passes.
4. S3. Malformed JSON args print a Python traceback (exit 1, state unchanged); `step "#abc"`, a JSON array or a string give "engine crash"; `new abc` traceback. Class: harness input validation.
5. S3. `options` after the end lists options (e.g. write) while the turn JSON says [].
6. S3. Starvation: after "The cloister starves." the dusk continues (camps, regrowth, slide); turn shows 13/16 for a game that ended at day 12 dusk.
7. S3. "The Gleaners find no trail to follow" when all lifts came from raised bunkers (seed 202 day 7), which contradicts the sheet ("a day with no lifts").
8. S3. Vigil text: "roll 2 (need 3+) vigil fail." (label doubled). Sheet line 5 does not say the added stock is also spent on a hit; code and r5 spend it.
9. S3. Status line has no day counter (contract example has T3/16); camp brackets have no legend.
10. S4. Unknown param keys are accepted and logged (`{"first":"take","then":"walk","extra":1}` applied a turn).
11. S4. Vigil with offering 3 needs "1+": it can never fail, so the final roll is a 15-stock purchase. Autopsy shows waiting to buy it beats rolling. r5's miss case at offering 3 feeds die value 0 (impossible).
12. S4. Camps hit the head bunker, which slides to the back before the camp matters, so `take,take` at the head is immune (seed 101 day 6: 11 stock).
13. S4. Raise is offered when it guarantees starvation (seed 202 day 12: stock 13, raise to tier 2, dead). Dead states persist for many turns (game 1 decided at day 7).
14. S4. Literal 6 for the vigil die (code, RULES "d6", test); mutation survivor at line 608.

Overall bug rate: 9 S1 to S3 (6 engine, 3 harness), 0 S1.

## Games played

| Seed | Strategy | Result | Turns | Fun |
|------|----------|--------|-------|-----|
| 101 | careful, by hand | loss, days ran out (tier 2, stock 1) | 16 | 4 |
| 202 | greedy rush | loss, starved day 12 | 12 | 3 |
| 303 | exploit, repeat take,take at head | loss, starved day 6 | 6 | 2 |
| 13 | careful, scripted | loss, vigil miss day 14 | 16 | 5 |
| 14 | careful, scripted | win by vigil, day 13 | 13 | 6 |
| 16 | careful, scripted | win by vigil, day 16 | 16 | 6 |

## Rule-test gaps

Die size (literal 6); starve tag at exactly 0 and the "dry" tag (survivors, lines 631 and 584; line 639 `amt > 0` is a dead condition); integer-ness of offering; vigil miss at offering 3; tier-1 regrow; ally bonus on sweep; event text and ordering; status line and day counter; post-end CLI behaviour. GATES are tautological (`_if` reuses `_raise_choices`). r6 encodes the day-8 camp.

## Autopsy and replay

Both worked. On clean games (seed 14): turns_played 13, replay matches saved state. Anomalies: phantom rows (bug 2); `forced` is set on a turn whose rollout spread is 1.0 (it counts option objects, not param combos); game 1 autopsy gave a swing of 0.17 to 0.65 after a poor 3-stock day, which I could not verify.

## check --free

CLEAN, 7 warnings (sheet word counts, starve tag 0 percent, look-ahead 50 percent), mutation 50 of 55. None of bugs 1 to 14 was flagged.
