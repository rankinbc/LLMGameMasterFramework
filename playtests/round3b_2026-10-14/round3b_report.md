# Round 3b: five generated games, each attacked by an independent QA agent

Date: 2026-10-14. Method: five agents each followed the `/play` skill (harness v2: universal checks, rule tests, params, mutation pass) to generate a game and left it at turn 1 without playing it. Five other agents, who had not written the games, then played each one at least three times with different strategies, sent hostile input, compared every rule line with the code, and checked the engine's own `check`. Generator reports are `generator_report.md` in each game folder; QA reports are `qa_report.md`.

## Results

| # | Game | Generation | QA bugs S1 to S3 | Of which harness | Of which game | Arithmetic mismatches found by an independent oracle |
|---|------|-----------|------------------|------------------|---------------|------------------------------------------------------|
| 1 | Styx Arcade | 150 min, 100 tool calls, 2 counted rounds | 7 | 4 | 3 | 0 (2,400 fuzz games) |
| 2 | Mirror Migration | 70 min, 60 calls, 4 rounds | 7 | 4 | 3 | 0 (1,200 fuzz games) |
| 3 | Ash Rule | 75 min, 50 calls, 4 rounds | 9 | 3 | 6 | 0 (6 games and 30 fuzz games) |
| 4 | Dust Licence | 70 to 80 min, 55 calls, 4 rounds | 6 | 3 | 3 | 0 (2,800 games, 16,222 bids) |
| 5 | Rim Card | 150 min, 75 calls, 4 rounds | 7 | 4 | 3 | 0 (800 fuzz games) |
| | Total | | 36 | 18 | 18 | 0 |

Severity: no S1 that corrupted a saved state in a normal move; S2 about one per game; the rest S3. The engine's own `check` said CLEAN, or flagged one accepted band miss, on all five games, and caught none of the 36 bugs.

What this says. The numbers are right: four independent oracles built from the sheets alone agreed with every engine on every step. What was wrong was around the numbers: how the command line handled the end of a game and hostile input (half of all bugs), and wording, sheet omissions and display conventions (the other half).

## Bugs by class

Harness (all 18 now have a regression test or mutant):

| Class | Games hit | Fixed by |
|-------|-----------|----------|
| `step` after the end appends phantom rows to history and the roll log; autopsy then counts an extra turn | 5 of 5 | refused with a clean error before any write |
| `options` after the end still lists actions | 4 of 5 | empty after the end |
| Malformed JSON, `new abc`, `#abc`, a JSON array or string as args: traceback or "engine crash" | 5 of 5 | clean errors, no traceback |
| Unknown args accepted and stored (`"zzz": 1`, an undeclared `bribe`) | 4 of 5 | strict arg names |
| Falsy JSON args (`null`, `false`, `0`) applied the move, then crashed before writing the log | 2 of 5 | validated first; the log, history and state are written together, state last |
| `true` accepted as 1, `1.0` crashed `==`-based code, `1.5` accepted for a whole-number param | 3 of 5 | bools rejected, whole numbers coerced to ints, fractions refused |
| `advance` sees the next turn number, so "from day 9" fired on day 8 | 3 of 5 | one meaning of `_turn` for apply, advance and check_end; the budget is scored in `final_check` |
| The roll log named the turn after the one played | 1 of 5 | fixed |

Game (wording and sheet): a stale word left from an earlier draft ("the Wall stands" in a game of dens), a wrong verb ("the Pilgrims turns back"), an event that does not narrate the number it changes (a bribe, a Hub replaced), labels counting from 0 where the sheet counts from 1 (3 games), a rule on the sheet that disagrees with the code in a way the test then encodes (rate "drifts each dusk" but holds 47 percent of dusks; "bar drops 2" while the climb is 2), behavior the sheet never states (a sit-out erases the last bid), and a repeated phrase in a label.

Design smells noted by QA, not bugs: offered actions that can never matter (a Belt after night 18), a hidden starting value that decides the game (Rim Card's heuristic wins 20, 53 and 67 percent by raid period), a loop that cannot win, a debt that never binds, ledgers offered when useless.

## Injection test

One QA agent injected 11 one-line bugs into scratch copies and ran `check --free`: 5 were caught (a bribe not charged, a `>` for `>=`, the rate never holding, a void keeping Proof, a resample off by one) and 6 were missed and reported CLEAN: a label saying "aisle 0", "you can afford N+1", an accuse label saying Proof +1, a status line showing Suspects +1, a hidden name leaked into an event, and into `visible()`. All six are text or display. The mutation pass skipped helper methods and everything inside f-strings, so no test was ever required to pin a label or an event.

## Harness v3, made from this round

All in `engine/` and `tests/`, 34 mutants and 68 unit tests, all green:

- Command line: end guard, clean errors, strict args, bool and float handling, write order, roll-log label.
- Contract: one turn semantics (`apply`, `advance`, `check_end` all see the turn being played); `final_check` for the budget; `finish()` for a fatal event; `{KEY|noun}` pluralizing in the sheet.
- Checks: the mutation pass now covers every class method and module-level helper and the numbers inside f-strings, and always lists survivors; a vocabulary lint for capitalized words in events that the sheet and options never use; hidden strings appearing in events; balance by hidden starting value; literal numbers in the logic; `texts` lists every wording once for a human to read.
- Rule-test helpers: `t.label`, `t.status`, scripted `drift`, deep-copied overrides.
- Process: a tuning round counts only when logic or numbers change; at the cap a band miss within 0.1 is a warning; look-ahead breaks ties toward the heuristic, always considers the heuristic's pick, and uses 8 rollouts on 100 games; the early-win flag ignores one lucky random win.
- Skill: Step 7 now has "read every wording" and an independent review (`tools/qa_prompt.md`) that must run before a new game is presented; rule tests must assert event and end-reason wording and labels; the sheet must state what the tests pin.
- Reference engine: 96 percent of its code mutations are caught, no warnings.

## Sameness effect (28 games)

Pairwise similarity fell from 36 to 28 percent; `rival_tell`, `ending_shape` and `decision_unit` are no longer stuck. New stuck traits: `tracked_count` is now 2 in 70 percent of recent games (the brief said "not 3" and every agent picked 2; it should be a roll, 1 to 3), `opening_shape` is `build` in 70 percent, `setting_family` is scifi in 3 straight games although SET varies (the SET table is scifi-heavy), and 80 percent of games are won by the independent players' careful line.

## Cost

Generation took 70 to 150 minutes per game and 50 to 100 tool calls. The independent QA took 20 to 35 minutes and about 70 tool calls. Together that is roughly two hours per game before the new review step, which will add about 30 minutes. This is the price of the quality bar; a scaffold and the faster `check` (under a minute now) are the levers left.

## Next

A validation round under v3: three games, generated with the independent review step, then attacked by a fresh QA agent. Success is zero harness bugs and no more than one wording bug per game.
