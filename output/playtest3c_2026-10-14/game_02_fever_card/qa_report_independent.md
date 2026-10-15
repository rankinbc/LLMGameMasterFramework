# Independent QA: Fever Card (game_02)

Tester did not read qa_report.md or generator_report.md. Phase 1 (black box), Phase 2 (white box), Phase 3 (check, autopsy, replay) all done. The game folder was reset at the end with `python engine.py new 610753` (the original seed, so state.json is the same fresh turn-1 state the generator left; history.jsonl is gone, as `new` always does).

## Verdict

No S1 and no S2 found. The engine matched an independent re-implementation of the rulesheet over about 5,000 games (random play, heuristic play, and heuristic with 10 and 25 percent random moves; losses, wins, Stoke, Lance, all four freezes): board, bricks, germs, Slots, Bloom, bookings, option legality, Stoke gate, status line, turn counter and end result agreed on every night. Bad input is refused cleanly everywhere I tried. The findings are cosmetic text, sheet omissions and design smells.

## Bugs

1. QA-1, S3, game. A game-ending dusk keeps narrating the next night. advance() always finishes the whole dusk and only then check_end runs, so a lost game still prints "Night 8: you may now Lance a pass.", "Night 7: the fever peaks. ...", "Old Gold masses at pass N." or "Old Gold finds no room to mass." (in all 1,904 dusk-ending losses of 3,000 simulated games the last event is that Bloom line; 1,094 also carry the Lance bulletin). The contract offers `self.finish(...)` for fatal events inside advance; the game does not use it. Repro: `new 505`; `step sweep '{"pass":1}'`, 2, 3, 4; then `step hold` x3: the pass 4 freeze loss on night 7 is followed by "Night 8: you may now Lance a pass." and "Old Gold masses at pass 2."
2. QA-2, S3, game. Two fatal things in one dusk: the loss reason is picked by check_end order (freeze before sepsis), not by what happened first. About 122 of 6,000 simulated games lost to "winter closed pass N" with germs already at 11 or more from the landing earlier in the same dusk. Sepsis also overshoots (reason says 12 or 13 germs, about 150 games) because a 4 to 6 germ landing can cross 11 in one go; the sheet only says "reach 11". Repro: seed 8 with the actions sweep 3, wall 4, hold, hold, wall 3, hold, hold ends "winter closed pass 4 at 3 bricks of 4" with 11 germs on the board.
3. QA-3, S3, game (sheet omission). Stoke stops being offered once no unfrozen pass is left that can still freeze (after night 11, or earlier if every freezing pass has frozen). The sheet says only "Once, from night 9". Not stated either: pass 4 can never be Lanced (it freezes after night 7, Lance opens night 8).
4. QA-4, S3, game. Stoke opens on night 9 with no bulletin, while Lance's opening is announced ("Night 8: you may now Lance a pass."). notes.md calls both "published bulletin". The Stoke option just appears.
5. QA-5, S3, game. "Hold" always says "The bookings stand." even when there are no bookings (night 1). Hold is also not named on the sheet (only "one move").
6. QA-6, S4, game (sheet). Rule 5's "and nothing lands" reads as if it applied at once. What the code does: Bloom is fixed at the end of a dusk; if it is "none", the next dusk lands nothing even if a Lance has just opened room (seen in seed 303, nights 11 and 12: a free dead dusk). It follows the sheet but is easy to misread.
7. QA-7, S4, game (sheet and dead code). A frozen pass is always a full pass of 4 bricks (freezing short is an immediate loss), so the sheet sentences "keeps its contents, runs nothing, takes no germs; its bays leave your Slots" can never be seen in play. Also unreachable in play: base landing plus Stoke before night 7, and the stoked variant of the "fever peaks" bulletin (Stoke opens on night 9, the peak bulletin fires on night 6). rule_tests reach them only through hand-built states.
8. QA-8, S4, game. The last third is mostly forced. Once pass 2 to 4 are done, only pass 1 is left and the sensible move is the same each night (lance, hold, hold, lance). With a Wall crew already booked and no germs in pass 1, the only other option is Sweep, which replaces the Wall crew; Hold is the only sensible move (game 459 night 13, game 101 night 16). Autopsy flags "FLAT FINISH" and "NO HARD CHOICE in the last third" in both of my autopsied games. The opening (Wall pass 4 by night 2 or 3, Sweep drain in pass 1) is also close to forced.
9. QA-9, S4, game. Literals outside CONSTANTS: BOUNDS 0 to 16 (PASSES times BAYS), BOUNDS bloom (-1, 3), REACH germs 10 (is SEPSIS minus 1) and built 16 (is the goal). They break if PASSES, BAYS or SEPSIS is retuned.
10. QA-10, S3, game (test hygiene). rule_tests r6 asserts `not any("opens the Lance" in e ...)`; that wording is from an earlier draft and is never produced, so the assertion is vacuous (the next line, `"lance_open" not in self._hits`, does the real work).
11. QA-11, S3, harness (gm_analysis.autopsy). Swing attribution ignores sign. Seed 101, turn 5: the pick was the best option (regret 0), potential fell 0.62 to 0.17 purely from the surge roll (luck_effect -0.45), yet `cause` reads "your choice" because choice_effect is measured against the mean of all options (+0.53, inflated because most options are duds) and the code compares only absolute values (gm_analysis.py lines 246 to 249).
12. QA-12, S4, harness (gm_base). `{"pass": 2.0}` is accepted as pass 2 (2.5 is refused). `step "# 1"` is accepted as option 1. `new -5` and `new 5` give the same game (Python seed behaviour). All harmless.

## Games played

| Seed | Strategy | Result | Turns |
|------|----------|--------|-------|
| 101 | careful (Sweep drain, freeze order, Stoke 9) | loss, 16 nights ran out, 14 of 16 bricks (pass 1 never got a crew in time) | 16 |
| 202 | greedy (Wall everywhere, ignore germs) | loss, sepsis 11 germs | 4 |
| 303 | strong line, Stoke on 9 | loss, 13 of 16 bricks | 16 |
| 505 | exploit/stall (Sweep each pass once, then Hold) | loss, winter closed pass 4 at 0 bricks | 7 |
| 459 | heuristic line found by script, then replayed with `step` | win, night 14 of 16 | 14 |
| 459 (second run) | deviated on purpose at night 9 | loss, winter closed pass 2 at 2 bricks | 10 |

Fun: about 6 out of 10. Good puzzle in the first 8 nights (pass 4 first, drain in pass 1, when to Lance), then flat.

## Bad input (all refused, state.json, history.jsonl and rolls.log byte-identical afterwards)

Unknown id, empty id, upper-case id, missing param, pass 0, 5, 9, -1, 2.5, "x", "2", null, true, [2], NaN, Infinity, 1e20, extra arg, args on hold and stoke, `{}`, `[]`, `"x"`, `null`, malformed and trailing-comma JSON, `#0`, `#-1`, `#99`, `#abc`, `#1.5`, extra positional arg, passes frozen, finished, already holding that crew, Lance on a germ-free pass, Lance and Stoke before their night, `step` after the game ended ("the game is over", exit code 1). Corrupt state.json gives a JSON "engine crash" error, no traceback. `new abc` and `new 1.5` are refused and do not overwrite the game.

## White box, rule by rule

1 (start, Slots): init_state places 5 germs with a per-pass cap of 3 (tuning constant `_START_CAP`, not on the sheet); Slots recomputed by `_tally` after every apply and advance, no drift. 2 (bookings, order): matches. 3 (Wall, Sweep, waiting): matches. 4 (landing, die): the die is rolled only when a landing happens; no roll when the pass is full or Bloom is none (matches r3 tests, not stated on the sheet). 5 (Bloom, peak): peak uses `_turn >= PEAK_NIGHT`, correct; Bloom is computed after winter so a frozen pass is never named. 6 (freezes): `t >= night`, announced one night ahead; Stoke shifts all three. 7 (Lance, Stoke): gates match. 8 (goal, losses): win is checked before landing and winter, so nothing happens after the last brick. No set or dict order dependence found (FREEZE_KEY is iterated with sorted()).

## Rule-test gaps (behaviour not pinned by rule_tests)

- Dusk order beyond "pass 1 first": winter after landing, bulletins after winter, Bloom named last.
- Sepsis checked only at the end of the dusk (not after bookings), overshoot counts, and the freeze-versus-sepsis precedence.
- Stoke played on the night itself followed by the real advance (the tests build stoked states by hand), including Stoke on night 10 and 11 where a freeze is due that very dusk.
- Stoke plus peak plus surge capped by free bays.
- Stoke still offered when every unfrozen pass is already finished.
- Lance on the Bloom pass and the following landing; Lance while Bloom is "none".
- visible board strings ("BB.G") and `last_dusk` after a Stoke through a real step.
- Starting Bloom from init_state (only the `_bloom` helper is tested).

## Phase 3

- `check --free`: CLEAN, no flags. Warning only: look-ahead wins 79 percent against the heuristic's 32 percent. Random 0 percent, mutation 104 of 104 killed. It did not catch QA-1, QA-2, QA-3, QA-4, QA-7 (unreachable branches), QA-10. A check for "events narrated after the game ended" and one for "test strings never emitted" would catch QA-1 and QA-10.
- `autopsy` worked on a loss (seed 101), on a mid-game state and on a win (seed 459). `replay` (dry run) worked on a loss, a mid-game and a win: `ok true`, `matches_saved_state true`. `replay --apply` was not run.

## Could not verify

The LLM narration layer; `profile`, `ablate`, `sweep`, `trace` and plain `check` (it burns a tuning round) were not run; the hidden `log` command was not run during play; my oracle shares my reading of ambiguous sheet lines (die not rolled when nothing lands), so those points are confirmed only against the rule_tests and not against an outside reader.
