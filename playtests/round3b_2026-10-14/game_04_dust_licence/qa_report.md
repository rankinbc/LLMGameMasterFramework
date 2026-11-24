## Bugs
Engine arithmetic is clean: an independent oracle (2,800 games, 16,222 bids) found zero disagreements with the sheet. The bugs are harness and text.

1. B1, S2, harness. `step` after the end is not a no-op: exit 0, "Game is over.", but ghost rows are appended to history.jsonl and rolls.log. Repro: finish a game, `step sit`, `wc -l history.jsonl`; `autopsy` says turns_played 17. Class: post-terminal mutation. check: no (in-process fuzz; needs a CLI file-hash test).
2. B2, S3, harness. After the end `options` still lists bid and sit.
3. B3, S3, harness. Malformed JSON (`step bid '{bad'`), `new abc`, or no state.json print a raw traceback; `'[3]'` or `'3'` args give "engine crash AttributeError". State unchanged. check: no.
4. B4, S4, harness. Unknown args are accepted (`step bid '{"amount":3,"foo":1}'` played; `step sit '{"amount":3}'`); `{"table":false}` passes as table 0. This bit my own bad-input run in game 1.
5. B5, S3, engine. Audit `table` choices are raw 0-based indices ([0,1,5,6,7], Cage 8) but text says Table 1 to 8. Rule tests: no.
6. B6, S3, engine. Label "(take 1, yours, yours already, no convoy needed)" repeats itself. Text lint: no.
7. B7, S3, engine. Rule 6 says "your last bid plus 1 (3 if none)", but a sit or audit turn erases it (seed 3: bid 6, sit, bid; Vey bid 3, not 7). Test r3 pins it; the sheet does not say it.
8. B8, S4. Sitting out on a table you hold lets Vey roll to steal it; the label says only "Vey wins it for 1". An all-in bid, or audit at exactly 4 Standing, can bankrupt you unwarned.
9. B9, S4. The turn 16 Cage is nearly a formula: miser bids 4 to 5, shadow 3 after a feint, so about 6 Standing swings 6 table points. Sitting on lots Vey holds is free +2.
10. B10, S4. No turn counter or Y/V legend on the status line; `log` prints the hidden habit ("choice='miser'").

## Games played
- Seed 101, careful (miser): loss 3 to 8, turn 16, 6/10. My stray-key test (B4) bid 3 on the Cage.
- Seed 202, greedy then hoard (gambler): loss 3 to 7, turn 16, 5/10. My bad-input amount 12 was legal.
- Seed 305, stall (gambler): loss 0 to 10, turn 16, 2/10. Stalling cannot win.
- Seed 101, replay of game 1 (events matched), Cage bid 8: win 6 to 5, turn 16, 7/10.
- Seed 7, shadow, scratch copy, feint and hoard: win 6 to 4, turn 16, 5/10.
23 bad-input forms refused with files byte-identical, except the cases above. Exactly 16 actions per game.

## Rule-test gaps
Surviving mutants: Vey winning a sat-out lot skips the convoy roll; audit cannot target a Vey-held Cage; Y/V swapped in the ring line; table names 0-based in labels and events; tie and "renewed" text deleted; sit price wrong for a rich Vey (30 and up); docket unshuffled; Cage touching only tables 1 to 7. check's mutation covers 5 methods (64 of 65); widened to helpers, 116 of 119.

## Autopsy and replay
Both worked on every finished game; numbers agree. Polluted history gives 17 turns (B1). Regrets are noisy (picked_rate 0.0 on turns I won). check --free: FLAGS (heuristic 0.47 over 0.45; random 0.04, look-ahead 0.80, mutation 0.98; tune cap used). It caught none of B1 to B10.

## Fingerprint
Written to qa_fingerprint.json.

## Overall bug rate
6 S1 to S3 bugs (1 S2, 5 S3), plus 4 S4. Not verified: human fun, ablate, sweep.
