# QA report: Styx Arcade (playtest3b game_01)

Tester: independent QA agent, 2026-10-14. Engine, notes and tools were not edited. The generator's in-progress state.json (seed 735424) was overwritten by my `new` calls; a copy is in the QA scratchpad. The state left in this folder is a finished, clean win on seed 101.

## Bugs (S1 to S3 are counted, S4 are smells)

1. B1, S3, game. The ledger is narrated as a witness. Repro: `new 202`, reach night 8+, `step ledger '{"topic":"coat"}'` prints "You pay 3 Hearsay for a page of the ledger." then "The witness says the Skimmer wears the crimson coat." Class: stale or reused text. check and rule test r8 cannot see it (r8 pins only the word "ash"); one assertion that ledger events do not say "witness" would.
2. B2, S3, game. The bribe is never narrated. Repro: `new 101`, `step run '{"aisle":1,"bribe":2}'`: Hearsay goes 2 to 6 while the event says "haul +6"; a caught bribe vanishes with only "no haul". Class: event versus number reconciliation. check cannot see it; the rule tests pin the Hearsay arithmetic but no event wording.
3. B3, S3, game/sheet. Rule 4 says the rate "drifts a step each dusk". The code holds the rate 1/3 of the time mid-band and 2/3 at 6 or 9; over 18,000 fuzz dusks the rate did not move on 47 percent. The starting rate 7 and the hold are not on the sheet. Repro: `new 404`, Rate shows 6 on nights 2, 3, 4 and 5. Class: sheet versus code. Rule test r4 pins the hold, so the test encodes the mismatch; the sheet check counts words only.
4. B4, S3, harness (game also lacks int()). Arg identity compares with `==`. `step run '{"aisle":1.0,"bribe":1}'` gives "engine crash: TypeError list indices"; `{"aisle":true,...}` is accepted as aisle 2 and stored as True in history. State unchanged. Class: arg type validation. check never fuzzes arg types.
5. B5, S3, harness. Unknown extra args are accepted and written to history.jsonl: `step run '{"aisle":0,"bribe":0,"zzz":1}'`; also an undeclared `bribe` with an empty purse; duplicate JSON keys, last wins. The game's apply clamps, so numbers stay right. The generator had already reported this.
6. B6, S2, harness. `step` after the game has ended, with an id that is still listed, prints "Game is over.", exits 0, and appends a phantom row to history.jsonl and a line to rolls.log (state.json unchanged). Autopsy then reports turns_played 13 and a turn-13 table row. `options` lists actions in an ended game while `status` lists none. Repro: finish any game, `step ledger '{"topic":"coat"}'` or `step "#1" '{"bribe":0}'`, diff the files. Class: the ended guard runs after the option match. check does not drive the CLI past the end.
7. B7, S3, harness. Malformed JSON (`'{bad'`), `new abc`, `new 1.5` and any command with no state.json give raw Python tracebacks. Non-object JSON (`[1,2]`, `5`) and `#abc` or `#` are reported as "engine crash" (AttributeError, ValueError) though nothing broke. State files stay unchanged in all of them.

S4 smells (not counted): (a) the ledger is offered when it cannot help (one suspect left, or coat when both candidates wear saffron), and witness aisles on an already-known topic carry no marker; `ablate` already called the ledger unproven. (b) Bribe is never worth its cost: EV of a run is (6-h+b)(h+2)/6 - b with slope (h-4)/6, so it is a pure variance dial. The safe loop (+2 a night) reaches at most 22 Hearsay by night 11 against 24 needed, so only gamblers win, and early bad luck ends the game by night 4 (autopsy FLAT FINISH on games 2 and 4). (c) TRACKED says 2 but the status line shows four numbers; `aisle` args are 0-based while labels say aisle 1; the 1980s arcade barely appears in the text. (d) `hidden_leaks` is blind here because the culprit is stored as an int index.

## Games played (all four to the end, 12 nights each)

| Seed | Strategy | Result | Fun |
|---|---|---|---|
| 101 | careful: info first, buy 1 Proof at 7, then 3 at 6 on night 11, accuse night 12 | win (exactly 18 Hearsay for 18). My first run lost: a bad-input test on night 12 was a legal run and ate the last night. I replayed the same moves and accused. | 7 |
| 202 | greedy: stamp early, high hazard | loss, 3 catches, hearsay 0 by night 3, decided by turn 4 | 3 |
| 303 | max-EV runs, then probed Magpie and ledger | loss, culprit known night 9, 9 Hearsay short | 4 |
| 404 | exploit: extra args, safe loop, bad inputs | loss, 6 catches in 11 runs | 3 |

Bad-input battery (about 60 cases, checked by file hash): refused cleanly with files unchanged for unknown id, wrong or out-of-range aisle, out-of-range, fractional, string, null, bool, NaN and Infinity bribe, missing params, `#0`, `#99`, `#-1`, unlisted action, wrong `who`, bad `proof`. Failures are B4 to B7 only.

## Oracle and fuzz

I wrote an independent oracle (need = hazard - bribe + 1, haul, bribe cost, Walker, void, Magpie thresholds 3 then 2 from night 6, rate range and step, known facts, case, countdown text, turn counter) and ran it over my 4 games plus 2,400 in-process games (173 accusations, all correct). Zero mismatches. Dealing statistics match the sheet (witness 51 percent and 50 percent, hazards uniform, d6 uniform, topics and positions uniform).

## Phase 2: sheet versus code

All 8 rules match the code. Dead guards: `max(1, hazard-bribe+1)`, `max(1, rate)`, `took = min(LIFT, proof)`, the `_cands() or list(...)` fallback in resample_hidden, and `_step`'s "out of turns" branch (check_end covers it). Literals: the rate die `rng.d(3)` and its branches, booth "two topics" and "fourth", and one constant HAZ_MAX serving both plain cards and the booth. No set or dict order dependence. check_end uses `_turn > turns` as the contract allows. BOUNDS are loose (proof to 20, hearsay to 200).

## Rule-test gaps

Not pinned: any event wording beyond a few substrings (B1, B2); numbers inside option labels and the status line (only "Hearsay 2" is pinned); `visible()`; `resample_hidden`; option order (the `#N` numbering); the Magpie announcement numbers; the audit text; the sheet's claims about the rate. Tests also pin unstated behavior (start rate, hold).

Injection experiment (single-line bugs in scratch copies, `check --free`). Caught: bribe not charged, Magpie `>` for `>=`, rate never holds, void keeps Proof, resample off-by-one (only through the look-ahead crash). Missed (CLEAN): label "aisle 0", exchange label "you can afford N+1", accuse label Proof +1, status "Suspects" +1, culprit name leaked into an event, culprit name leaked into visible(). Mutation pass: 69 mutants, 67 killed; the 2 survivors are equivalent (`_deal(1,...)`, `max(1,rate)`). It skips helper methods and f-string text; with helpers included I got 79 of 83, the extra survivors being resample_hidden.

## Phase 3

`check --free`: CLEAN, 0 flags, 7 accepted warnings (rule words 37 to 41; seized and voided in 0 percent of heuristic games; look-ahead 32 percent, below heuristic 39 percent). None of B1 to B7 was caught. `replay`: exact (matches_saved_state true, `--apply` idempotent, hashes unchanged). `autopsy`: worked; swing, choice and luck effects, decided_at_turn and regrets reconcile by hand. Autopsy issues: the B6 phantom turn; best and worst unrounded in the table while other fields are rounded.

## Overall bug rate

7 bugs of S1 to S3 (S1 none, S2 one, S3 six): game 3 (B1 to B3), harness 4 (B4 to B7).
