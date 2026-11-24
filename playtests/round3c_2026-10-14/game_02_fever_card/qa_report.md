# QA report: game_02_fever_card (Fever Card)

Verdict: no S1 or S2 found. Rules, thresholds, freeze nights, Bloom ties, landings, surge, Lance and Stoke all matched the sheet in play and in code. Findings are S3/S4.

## Bugs
1. B1 S3 (game): Sweep is offered on a finished pass and the booking sticks ("Pass 4: BBBB (Sweep booking)"), against rule 3 "A finished pass drops its booking". The option can never matter; rule test r2 pins it on purpose ("a finished pass may still be swept"). Repro: `new 1`; step wall 4, wall 3, sweep 1, sweep 4, wall 4; then `step sweep '{"pass":4}'`.
2. B2 S4 (game): Stoke is offered when every unfrozen pass among 2-4 is already finished (only effect: +1 germ per landing). Seen live: seed 20540 night 11. Heuristic play: 30 of 407 Stoke offers. `ablate`: win 0.88 with Stoke, 0.92 without, so Stoke looks dominated. Pass 4 can never benefit (it freezes night 7, Stoke opens night 9).
3. B3 S4 (game): from night 7 the surge die almost never matters (a pass has 4 bays; peak base 3, surge only helps into a pass with 4 free). After Stoke base is 4, so the surge can never change anything, yet the roll is still shown and consumed.
4. B4 S3 (game): a die is rolled and printed when the Bloom pass is full ("roll 4 (need 5+) no surge." then "Old Gold finds pass 2 full."), but nothing is rolled when Bloom is none. Sheet says "each landing rolls".
5. B5 S3 (game): "Winter nears pass 2: tomorrow is its last dusk" appears at the start of the very night whose dusk is the last one. Other bulletins say "Night N".
6. B6 S3 (game): `visible` is 0-based (bloom 1 = P2, -1 = none; brick/germ/orders/frozen/freeze_nights arrays) while status, board and params are 1-based. `freeze_nights` shows a slipped night for an already frozen pass (pass 4: 10 after it froze on 7).
7. B7 S3 (game): the dusk keeps narrating after the winning brick (roll, landing, "Old Gold finds pass 1 full."). Every heuristic win has trailing events.
8. B8 S3 (game): the status line has no night counter although every rule is keyed to night numbers. Sepsis can read "Germs 13/11" (seen in random play).
9. B9 S4 (game): forced-hold turns. When pass 1 holds the only working Wall crew and nothing can be lanced, the only other choice is a Sweep that replaces the crew (seed 5 nights 13 and 15). `autopsy` reports forced_turns [].
10. B10 S4 (design): one solved line wins: pass 1 as a sweep sink, pass 4 first, Lance plus Wall in pass 1 last. All three wins finished on nights 13 to 15. A full lesion (Slots 0, Bloom none) lands nothing and rolls nothing, so it is a risk-free stall (seed 5, Germs 10/11 for three nights).
11. B11 S4 (harness): extra trailing positional args to `step` are ignored and the move runs (`step hold '{}' '{}'`). `{"pass": 2.0}` and `1e0` are accepted as ints.
12. B12 S3 (harness): param refusals print `"options": []`. `step`/`status` with no state.json print "engine crash FileNotFoundError". Parallel QA agents share one scratchpad and overwrote each other's helper scripts.
13. B13 S4 (harness): `check --free` is CLEAN with a weak heuristic (32% vs look-ahead 79%). `autopsy` on a won game calls my winning turn-4 move a swing from 0.57 to 0.0.

## Sheet omissions (code does it, sheet silent)
Lance leaves the booking; Stoke never thaws a frozen pass; Stoke's +1 applies the same dusk; no Bloom means no landing and no die; a full Bloom pass still rolls; ending is checked after dusk; "11 germs fill the lesion" (16 bays).

## Hard-coded numbers
BOUNDS (16, 3), REACH (10, 16), HORDER, FREEZE_KEY and the "a brick each dusk" label are literals. Rule tests hard-code "4 of" and "2 bricks of".

## Rule-test gaps
Bloom stays stale across the player's move (Lance or Wall in the Bloom pass); no roll event when Bloom is none; sepsis above 11; Stoke after a pass froze; Stoke offered with only finished passes left; Sweep booking left on a finished pass; hold with no bookings wording; win ordering against a freeze or sepsis in the same dusk; events after the winning brick; surge cap by free bays after Stoke; landing into a pass that freezes the same dusk; the dead branches (Stoke term in the peak bulletin, pass 4 slip) are pinned only by artificial states.

## Games
seed 1 careful: win night 13; seed 5 greedy: win night 15 (replayed line then stalled: loss at budget, 12 of 16); seed 7 exploit (Stoke at 9): loss, winter closed pass 2 at 3 bricks, night 14; seed 20540 careful: win night 13; seed 2 (wall, wall): sepsis night 2; seed 8 (hold x4): sepsis night 4.

## Bad input
About 60 cases (unknown id, missing/extra/out-of-range/fractional/string/bool/null params, malformed JSON, `#0`, `#99`, `#abc`, step after the end): state.json, history.jsonl, rolls.log unchanged by hash in every refusal. Exceptions are B11.

## Phase 3
`check --free`: CLEAN, files untouched. `autopsy` and `replay` (dry and --apply) worked and matched the saved state on a loss and on a win.
