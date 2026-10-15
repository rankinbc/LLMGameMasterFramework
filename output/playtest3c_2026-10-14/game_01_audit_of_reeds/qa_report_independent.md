# Independent QA: Audit of Reeds

Tester: independent agent. Scratch work in the shared scratchpad folder qa_reeds. Game files touched: only state.json, history.jsonl and rolls.log (produced by `new` and `step`; the generator's original turn-1 state and roll log were overwritten by my first `new`). engine.py, notes.md, gm_*.py untouched. I did not read qa_report.md or generator_report.md, and I did not run `log`.

Disclosure: I saw hidden data twice by accident (the head of state.json when I arrived, and a `cat` of history.jsonl during game 2). Game 2 (seed 202) is therefore not a clean black-box game; the other four are.

## Bugs

Nothing in S1 or S2. I found no number that disagrees with its rule, no early or late ending, no wrong turn counter, no negative or runaway number, and no hidden-information leak in the turn JSON.

1. S3, game. The breach label carries no roll hint, unlike deploy ("roll 5+", "no roll can win"). A breach that cannot succeed is offered as a normal option and burns the once-only breach. Repro: `new 303`, then steps deploy 2/3, sound 4, sound 3, sound 6, deploy 6/3, deploy 3/3, deploy 4/3, sound 1, sound 5, deploy 5/3; on turn 11 (Drill 0, Soundings 4) `step breach '{"fork":2,"push":2}'` gives "roll 3 (need 7+) fail". The label also says "highest guard unknown" when the maximum is already pinned (a known 8 is the largest any guard can be after the stir).
2. S4, game. Deploy options labelled "no roll can win" stay on the menu (seed 101, turn 16: Drill 1, Soundings 0, reach 4 guard 8). Choosing one is a certain failure that also costs Drill. The label is honest, the option is a trap.
3. S3, game. Event order: "The X keepers give you nothing" and "That leaves House Y" print before the "You sound reach N" / "The sappers go in" line they follow from. Repro seed 101: sound 2 then sound 3.
4. S3, game (sheet). A learned guard is not fixed: it is shown as it stands now, so it moves with the stir and the barge's ward. Seed 101 reach 3: 6 (turn 3), 9 (barge arrives), 10 (stir), 7 (barge leaves). The sheet states each effect but not that a known guard follows them; "guard 3" also appears for a friend's reach although the sheet says base 4 to 7.
5. S4, game. Death spiral and flat finish. A failed deploy pays nothing and costs Drill; at Soundings 0 and Drill 0 around turn 14 the game cannot be won but runs 3 to 4 more turns. `autopsy` flagged NO HARD CHOICE in the last third (games 1 and 5) and FLAT FINISH (game 5); notes.md promises a cliff ending. `check` said CLEAN and `profile` had no warnings, so neither catches it.
6. S4, game. Weak or free levers. `ablate`: train and breach change the win rate by 0.00. My 400-game runs: no train 0.41 vs heuristic 0.42; no breach 0.50 vs 0.42 (the engine's own heuristic breaches badly); no writ 0.34; no train, breach or writ 0.17. The barge only adds +3 to one reach and can always be waited out. Sounding a friend's reach (+2) or any known reach (+1) is a free income loop; with known guards, stalling and spending the writ on turn 18 wins (game 2).
7. S3, harness. A truncated or corrupt state.json gives "a value on the command line could not be read" (it was not the command line). Repro: `head -c 100 state.json > state.tmp`, copy over, `status`.
8. S4, harness. state.json and history.jsonl hold the hidden guards, the friend and the full RNG state in plain text (history.jsonl is 145 KB after 18 turns, about 8 KB per turn). One stray `cat` of the game folder leaks everything.
9. S4, harness. Lenient parsing: `{"reach":2.0}`, `"push":1e0`, `-0.0`, `step "# 1"` (with a space) and `step "#14" '{"fork":2,"push":2}'` (fork repeats the option's own arg) are all accepted. The 2.0 case is pinned on purpose in rule test r2. Error payloads are inconsistent: param and arg errors carry `"state_unchanged": true`; malformed JSON, usage and `#N` errors do not (state was unchanged in every case).
10. S4, harness, unverified. `autopsy` top_regrets can report noise as regret (seed 101 turn 1: sounding Eel reach 4 instead of reach 2 shown as cost 0.20 though they are near-symmetric). I did not measure the noise.

## Bad input

About 90 refusals tried across live and ended games (unknown id, wrong or extra args, out-of-range, fractional, string, bool, null, list, NaN, Infinity, 20-digit push, push over soundings, missing push, malformed JSON, `#0`, `#-1`, `#99`, `#abc`, step after the end, breach/writ/train when not offered, deploy at a charted reach, wrong-case ids). Every refusal left state.json, history.jsonl and rolls.log byte-identical (hash compared before and after). The only accepted oddities are in bug 9.

## Games played

| Seed | Strategy | Result | Turns | Fun |
|---|---|---|---|---|
| 101 | careful: sound, train to 3, deploy | loss 5/7 | 18 | 6 |
| 202 | stall and hoard, writ on turn 18 (hidden data seen) | win on turn 18 | 18 | 4 |
| 303 | greedy: push 3 from turn 1, no training | loss 4/7 | 18 | 5 |
| 404 | mixed: deploy at the barge's reach turn 1, bank on the friend, breach the East | loss 6/7 | 18 | 6 |
| 505 | careful: train to 3 first, then deploy | loss 4/7 | 18 | 5 |

Win-on-the-last-turn works (writ on turn 18, game 2). Ties, level mouths, the barge's two drops, the stir on turn 10, the writ on turn 13, elimination of the friend and both plurals of "reach uncharted" all behaved as the sheet says. Fun is low-to-middling: the first three turns are sound, sound, train for everyone, and four of five games were decided by single d6 failures with no recovery.

## White box

Each of the 8 rule lines maps to code with no off-by-one: stir `_turn >= STIR_TURN` (and the dusk announcement on turn 9), writ `>= WRIT_TURN`, breach gate, barge `t % PACE == 0`, ties go low, ward only on uncharted reaches, friend ease and bonus, push capped by soundings. No dict or set order matters. Numbers written into the code rather than CONSTANTS: the delta shape (PARENT, HOUSES, SIDES, "Three houses" and the fork numbers in the sheet) and the heuristic's tuning literals (0.75, 0.6, 0.65, +3, +1); none is player-visible. Branches that never run: none found.

## Rule-test gaps

- Event order is never pinned (tests use `has`, not order), so bug 3 survives.
- No test for a breach label's odds wording (there is none) or for hopeless breaches.
- Friend plus stir together on a fresh sounding label (only each alone).
- The `ward` tag fires on deploy only; sound, breach and writ at the barge's reach do not set it, unpinned.
- No test that a known guard follows the stir and the barge between turns (only fixed states).
- No test for unwinnable states or last-third choice.
- Deploy, breach and writ at a friend's reach pay no extra: only implied.

## Autopsy and replay

Worked on seed 101 (loss) and seed 505 (loss): `autopsy` gave swing turn, regrets and flags; `replay` returned ok, 18 turns replayed, matches_saved_state true. `check --free`: CLEAN, random win 0.01, heuristic 0.43, lookahead 0.68, mutation 160 of 160 killed. 600 random games and 400 heuristic games: no crashes.

Should `check` have caught my findings? Bug 1 and 2 (label honesty for breach) could be a label-versus-odds check; bugs 5 and 6 are visible in autopsy and ablate only; 3, 4, 7 to 10 are outside what `check` looks at.

## Could not verify

Autopsy accuracy, `sweep`, fairness of Python's RNG, and whether the lookahead policy plays well. Win rates in my sims use the engine's own heuristic, so they bound but do not prove balance.
