# QA report: Sluice Street Audit (game_03_sluice_street)

Independent tester, did not write the game. Prompt: `tools\qa_prompt.md`. Engine file under test: `engine.py` (49,352 bytes, as found).
Nothing under `engine\`, `tools\`, `tests\` was edited; engine.py was not edited.

## Verdict

No S1 or S2 bug found. The engine matched the rulesheet line by line, matched an independent model of the sheet over 1,500 random games, and refused 50-plus bad inputs without touching state.json, history.jsonl or rolls.log. What remains is S3 and S4: two classes of dead options, a sheet that leaves out the ground odds, a pay line that leaks the hidden ground, label ambiguity on the status line, and a few harness CLI rough edges.

## Bugs

Where it lives is given for each one: GAME is engine.py, HARNESS is `engine\gm_*.py`.

| ID | Sev | Where | What | Repro |
|----|-----|-------|------|-------|
| B1 | S4 | GAME | Scouting lot 6 can never matter: the notes are carried off at that same dusk, before any other action can use them. Scouting on night 16 and raising on nights 14, 15 and 16 are also dead (a raise pays 3 a dusk for the nights left, so 9, 6, 3 against a cost of 10). All are offered as normal options, so the menu has traps and padding. | `new 101`, `step scout '{"lot":6}'`: events show "Lot 6 scouted" then "The creek carried off your notes on lot 6". For raise: reach night 14 with a depot and 10 Standing; `raise` is listed. |
| B2 | S4 | GAME (sheet) | The ground odds are not on the sheet. The code draws a d6: 1 Rich, 2-4 Fair, 5-6 Poor (`_RICH_UP`, `_FAIR_UP`, underscore tuning constants). A player cannot price an unscouted lot or judge how rare a Rich stake is. | `python engine.py rules` says only "Rich, Fair or Poor". |
| B3 | S3 | GAME | Rule 2 says the ground is "hidden until scouted", but the dusk pay line leaks it: total minus neighbours minus raises is exactly the ground pay under your depots (a lone depot "paid nothing" means Poor). The rule test only asserts the line does not name the ground. Voss's choice also bounds the other empty lots. Both leaks are real information, but neither goes into `known`, so it cannot be filed. | `new 5`, `step build '{"lot":3}'`: event "1 open depot paid nothing" tells you lot 3 is Poor. |
| B4 | S3 | GAME | Status line labels are ambiguous. "Snow 2" is a count of closed lots (the legend lives only in `visible.legend`); "Open 3" means open depots, not open lots. The line shows four labelled fields (Standing, Snow, Open, Street) against TRACKED = 3; "Open" is a derived fourth number. | `python engine.py status` |
| B5 | S4 | GAME | Numbers in code instead of CONSTANTS: `REACH` uses the literals 132 and 3 (should name LEVY, INSPECT, SNOW_MAX so a sweep moves them); the flood's "twice" is `slides = 1` then `slides += 1`. | read `REACH`, `advance` |
| B6 | S4 | GAME | `resample_hidden` redraws every unknown lot with no regard for what the player has inferred (pay lines, Voss's stake choice). Look-ahead and autopsy "luck" figures are therefore a little off: autopsy on seed 202 credits +0.65 swing at turn 3 to one Voss stake. Impact not measured. | `autopsy` after seed 202 |
| B7 | S3 | GAME (sheet) | Rule 3 is 42 words and rule 7 is 41; `check` warns "aim for 40". Under the 45-word cap. | `check --free` |
| B8 | S3 | HARNESS | Param errors return `"options": []`, which reads like "no legal moves" when it only means "this action needs a lot". | `step scout` (no args) |
| B9 | S3 | HARNESS | Developer commands label bad user input as "engine crash": `selftest 0` (ZeroDivisionError), `selftest abc`, `sweep LEVY=abc`, `ablate abc`, `autopsy abc` (ValueError). `selftest -1` prints `win_rate -0.0`. Unknown policy names (`selftest 5 nosuch`, `trace 5 nosuch`) and a bad seed (`trace abc`, which uses seed 7) fall back silently. Unknown command `frobnicate` prints no command list. Player-facing commands are all clean. | as listed |
| B10 | S4 | HARNESS | state.json and history.jsonl keep the hidden ground and flood night in plain text, and `log` prints them; the only guard is the narrator not reading them. history.jsonl stores the full state (including a 625-word RNG state) each step, about 8 KB a step. | `python engine.py log` |

Not bugs, noted so nobody re-reports them: `{"lot":3.0}` and `{"lot":1e0}` are accepted and normalised to ints (the param check compares by value; `true`, `"3"`, `2.5`, NaN and Infinity are all refused). `new` overwrites an unfinished game without asking. A depot on lot 1 built before night 8 is a legal trap (rule 7 states lot 1 closes on night 8).

## Games played

| Seed | Strategy | Result | Turns | Fun |
|------|----------|--------|-------|-----|
| 101 | careful: build 3, raise 4/5/3 from night 8, plough, scout then file | loss, Standing 123 vs Levy 132 | 16/16 | 6 |
| 202 | greedy: build at once, raise from 8, buy out lot 6, plough, file on 15 and 16 | win, 133 vs 132, 3 open depots | 16/16 | 7 |
| 303 | exploit: early lot 1 depot (trap), file spam, buy out a Voss stake after ploughing, rebuild after flood | loss, 28 vs 132 | 16/16 | 4 |

Also: 1,500 random games against an independent model (below), 200-seed runs of scripted loops (pure scout and file never passes 87 Standing, mean 53 to 69, 0 wins, so there is no free-value loop; "build 4 depots, raise, plough, file when 2 lots are known" wins 82 of 200, close to the heuristic's 40 percent).

No turn-counter, ending-timing, plural or "None" faults seen in any game. The last dusk's pay does count (seed 202 won on it).

## What I verified

- Black box: `rules`, `texts` (all 1,209 status wordings, 8 option wordings, 31 event wordings, 4 end wordings read), three full games, the end texts for win and "books short". The "too few open depots" end text and "lot 5 carried off" flood wording were not reached in play; they were read in code and rule tests.
- Bad input (about 50 cases, byte comparison of state.json, history.jsonl, rolls.log before and after): unknown id, `#0`, `#-1`, `#99`, `#abc`, missing param, out-of-range, fractional, string, bool, null, list, NaN, Infinity, 1e400, duplicate key, extra arg, extra positional, malformed JSON, non-object JSON, wrong case, padded id, and `step` after the game ended. All refused with exit code 1 and nothing changed.
- White box: every rule line mapped to code; thresholds are right (`>=` for LEVY, INSPECT, RAISE_FROM, BUILD and BUYOUT affordability); pay happens before the slide and before the flood washout; Voss is processed after the flood; snow for tomorrow is set after Voss and pay; plough only after the last lot closes, once; washed-out depot clears its raise flag; no dict or set ordering dependence (all lists).
- Differential model: I wrote an independent model from the rulesheet (`model_check.py`, in the scratchpad, not in the game folder) and ran 1,500 random games (half biased toward build and raise). Option sets, lot choices, Standing, known, lots, raised, snow, ground and final result matched at every step; invariants (known equals true ground, raised only on a depot, Standing at least 0, no integrity entries) held. Max Standing seen 141.

## Rule-test gaps (what the rule_tests do not pin down)

- Die thresholds: tests use dice 1, 4 and 6 only; the boundary values 2 and 5 and the interior value 3 are not pinned (mutation testing still killed all 134 mutants).
- Buying out a Voss stake on a closed lot is not tested; plough on a lot that holds a Voss stake, then buyout, is not tested (seed 303 does it; the code is right).
- Order of several dusk events (notes lost, stake, tell, snow) is pinned only for flood before stake.
- A build on the last night raising the open-depot count for the audit is not tested (the last-night test uses scout).
- `visible()` is checked only for the absence of `hidden`; the pay-line information leak (B3) is not tested.
- `resample_hidden` and the heuristic have no tests.

Should `check` have caught my findings? B5 yes in principle (a literal equal to a CONSTANT value in REACH or code). B1 would need a "dominated option" check (an option whose effect is destroyed before use). B3 and B4 are judgement calls that no mechanical check covers.

## Phase 3

- `check --free`: CLEAN, 0 flags. Warnings: rules 3 and 7 over 40 words, `closed_depot` tag fires in 3 percent of heuristic games. Random 0.0, heuristic 0.4, look-ahead 0.72, mutation 134 of 134. About 24 seconds. Game files unchanged by it (md5 compared).
- `autopsy`: worked on all three finished games. Seed 303 flagged FLAT FINISH (decided turn 4) and NO HARD CHOICE in the last third, which matches how I played it; top regret was the turn 3 lot 1 build.
- `replay`: dry run and `--apply` (on a scratch copy) both matched the saved state; apply left the three files byte-identical.
- `ablate`: scout is "marginal" (win 0.48 without it against about 0.66 with it); build, file, raise and plough are needed. `profile`: no warnings.

## Could not verify

- Floods on nights 9 and 15 were not seen in live play (live floods fell on nights 13 and 14); they are covered by the model check and rule tests.
- Whether B6 changes autopsy conclusions in practice.
- I did not read `generator_report.md`, to keep the review independent.
- I worked in a scratchpad shared with other testers; early helper files used generic names (`st.py`, `bad.py`, `copy1`, `copy2`) and I removed and recreated `copy1` and `copy2` there.
