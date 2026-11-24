# QA report: Mirror Migration (playtest3b game_02)

## Bugs
1. B1, S1 (harness, gm_base `step`). Falsy non-dict JSON args apply the action and save state, then crash with a TypeError traceback. history.jsonl and rolls.log are not written, so `replay` says "history.jsonl is empty" or mismatches. Repro: `new 303; step run null; replay`. Also `false`, `0`, `""`, `[]`. Class: save-before-log ordering. `check` never drives the CLI step path with hostile args, so it missed it.
2. B2, S2 (harness). `step` after the game ended returns "Game is over." (rc 0) but still appends to history.jsonl and rolls.log. Autopsy then reports turns_played 17 and decided_at_turn 17 on a 16-week game (seen in game 1). After the end, `options` still lists snare and run, and `step bogus` or `step "#1"` answer as if live. Repro: finish a game, `step run`, `autopsy`. Class: missing ended-guard. `check` and the rule tests do not run a post-end step.
3. B3, S3 (harness). `step run '{bad'`, `new abc` and `new 1.5` print raw Python tracebacks. `step "#abc"` and `step run '[1]'` give "engine crash" instead of a refusal. Param errors return `"options": []`. State stays unchanged. Not caught by `check`.
4. B4, S3 (game). Stale word "Wall" in end reasons: "the Wall stands and the debt is cleared", "the Wall had 1 gap...", "the Wall stands but Standing is N short". The sheet says dens and files. Repro: win any game. Rule tests assert only result and "N gap". Neither check nor tests lint end-reason vocabulary.
5. B5, S3 (game). Writ text uses a singular verb: "the Pilgrims turns back", "the Stragglers turns back". Repro: at week 9 or later with the Writ, buy it while Stragglers or Pilgrims are due (96 of 1200 fuzz games). The Writ event text is untested.
6. B6, S3 (game). "Dusk: stipend +0 from 0 dens; tithe -1." Awkward with no dens, which happens often in run-first openings.
7. B7, S3 (harness). `log` labels each action with the following turn ("turn 2 run" is week 1, and the last action reads "turn 17").
8. S4: extra args are accepted (`step run '{"file":"a"}'` plays and records the arg). Rule 6 says any party crossing an empty file costs 1, but Pilgrims cost 0. The Writ can be bought on a Pilgrims week. Den and snare labels do not name the file the party will cross.
9. S4: the 18-Standing debt never binds (wins ended at 42, 25, 26; the fuzz-heuristic average was 44). With 5 dens and 27 or more Standing at week 16 and the Writ unspent, the win is certain, so the "final-roll" ending is optional.

## Games played
- Seed 101, careful: win, 16 turns, Standing 42, fun 5.
- Seed 202, greedy run-first: win, 16 turns, fun 6. The Writ went early; one accidental null-args step desynced the log.
- Seed 404, stall and hoard: win, 16 turns, Writ at week 16, fun 5.
- Rule arithmetic matched in every turn. Foreclosure, the short-purse loss and the gap loss were checked in scratch copies.
- Bad-input checks (unknown id, `#99`, `#0`, bad file, missing param, illegal id) refused cleanly with state, log and history unchanged. B1 to B3 were the exceptions.

## Rule-test gaps
A mutation hand-test against `check --free` stayed CLEAN for each of these:
- Displayed party strengths in the status and `visible` (week offset).
- The crossing letter in the run label and `run_crosses`.
- The pilgrim payout amount shown in text.
- An extra hidden +1 stipend above Standing 40 (mutation rate 0.92, survivors not printed).
Also unpinned: all event and end-reason wording, a Writ on a Pilgrims week, and a negative Standing between the clash and dusk.

## Autopsy and replay
- `check --free` is CLEAN (random 0.03, heuristic 0.40, look-ahead 0.65, mutation 0.98).
- Replay matched on game 3 and on game 1 (with the polluted history).
- It failed after B1 (matches_saved_state false, then "illegal action").
- The autopsy table shows spread 0.0 beside regret up to 0.15. This is noise gating, not an error.
- The 17 turns in game 1 come from B2.
- A 1200-game in-process fuzz found no arithmetic mismatch between events and Standing, no hidden-deck leak, and no queue or turn drift. Standing ranged from -2 to 82.

## Fingerprint
Written to qa_fingerprint.json (result win, 16 of 16 turns, primary number Standing, 2 tracked, counter rival with the tell shown before, build win, deadline clock, place decisions).

## Overall bug rate
7 S1 to S3 bugs (B1 to B7): 4 in the harness, 3 in the game text, plus 2 S4 notes. White-box review found the numeric logic faithful to the sheet. Literal smells: strength is the card id, and `_VIEW` is not tied to the sheet.
