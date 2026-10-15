# QA report: Audit of Reeds (game_01)

Tester: independent QA agent. Harness files (gm_base.py, gm_checks.py) were edited by someone else at 00:18, 00:20 and 00:25 during this session; findings below were re-checked against the 00:25 version (the "lantern" example in the JSON-args error and the silently ignored extra `step` token were already fixed by then and are not listed).

Note: playing needs `new`, so the original state.json / history.jsonl / rolls.log (seed 3, turn 1) were replaced. The folder now holds seed 707, in progress at turn 7. engine.py, notes.md and tune.count are untouched. `check --free`, `autopsy`, `replay`, `ablate` and `texts` were verified (md5) not to change state files.

## Bugs

1. S2, game (sheet vs code). Rule 7 says the breach rolls against "the highest guard among it and its mouths". The code (`apply`, breach branch: `g = max(self.eff(s, m) for m in rest)`) takes the max over only the UNCHARTED reaches of the branch, and the label agrees with the code. rule_tests r7 pins this ("a charted reach does not raise the roll"), so the test contradicts the sheet sentence. Repro (scratch copy, crafted state: turn 10, barge on charted reach 2, reaches 4 and 5 known at guard 5): `options` shows "Breach the East branch (reaches 4 and 5; highest guard 5)" while reach 2 shows guard 10. Fix the sheet ("among its uncharted reaches") or the code.
2. S3, game (sheet omissions; the code does these things, the sheet does not say so): (a) breach is only offered when the fork has 2 or more uncharted reaches (seed 101 turn 10: East branch with only reach 4 left, no breach option); (b) friend by elimination ("That leaves House Moth") is in notes.md but not in rule 6; (c) charted reaches can still be sounded; (d) push cannot exceed soundings in hand; (e) a breach contacts every house under the fork; (f) Heron always holds 3 reaches, Eel and Moth 2 each, so a Heron friend discounts 3 reaches (pinned by r1, not on the sheet).
3. S3, game (label vs result). First contact with the friend's house: label says "+2 soundings", event pays "+3 (1 from the Moth keepers)". Hidden-info-preserving, but it was the only label/result mismatch in about 120 fuzzed games. Repro: `python engine.py new 101`, `step sound '{"reach":1}'`.
4. S3, game (0-based args). `args` are 0-based while labels, status, events and `visible.reaches[].reach` are 1-based. `{"reach":0}` is "reach 1"; `{"fork":1}` is the East branch (reach 2), `{"fork":2}` the West (reach 3). Typing the label number is refused cleanly; typing a smaller number silently acts on the wrong reach.
5. S3, harness. `step sound '{"reach":1.0}'` (also 1e0, 0.0, and a float fork) matches the option (1.0 == 1) but is not normalised: reply is `{"error": "engine crash", "detail": "TypeError: list indices must be integers..."}`. State files are unchanged and `state_unchanged` is true, so the refusal is clean but mislabelled. A float push (`1.0`) is normalised and accepted.
6. S4, harness. `step "#N" '<json>'`: the JSON overrides the option's own args. `step "#1" '{"reach":3}'` sounds reach 4, not reach 1 (history.jsonl records the label of reach 4).
7. S4, game. Sounding a charted friend reach pays +2 per turn with no cap and no cost. Seed 303: 20 soundings by turn 8 with zero charting. Soundings become abundant; turns are the real constraint. Not exploitable to an auto-win (max soundings about 60, below the 80 bound).
8. S4, game. Status line has no turn counter (the base contract example shows T3/16); the counter is only in the JSON `turn` field.
9. S3, game (text). Sheet mixes "forks" (rules 1, 7) and "branch" (rule 5, labels, events); "mouth" is never defined on the sheet; "fresh soundings" (stir event) is not a sheet term; "+2 (+1 from turn 10)" can be misread as an extra +1. Event "need 1+" versus label "any roll wins". The stir text "fresh soundings pay 1" is awkward.
10. S4, game. Deploy is offered when no push can ever win (for example Drill 0, 2 soundings, guard 10 on the barge reach): a dominated option that only burns a turn and teaches the guard.
11. S4, game. Numbers in code, not CONSTANTS: BOUNDS (0,3) drill, (0,6) barge, (0,7); REACH {7, 3, 3, 5}; PARENT tree and `SIDES[f-1]` fixed to 7 reaches although REACHES is a constant; rule 1's tree text is a literal, not derived from PARENT; `joined()` single-name branch can never run in play.

## Games played (CLI, black box)

| Seed | Strategy | Result | Turns | Fun |
|------|----------|--------|-------|-----|
| 101 | careful, train to 3, breach, writ | win on the last action | 18 | 7 |
| 202 | greedy, big pushes, early breach | win | 12 | 5 |
| 303 | stall and hoard (sound loop), then chart | loss, 1 reach uncharted (chosen) | 18 | 3 |
| 404 | avoid-the-rival, East breach at turn 10 | win | 14 | 6 |
| 506 | random bot | loss, 5 uncharted | 18 | n/a |
| 707 | bad-input probing, partly played | in progress | 7 | n/a |

About 120 further bot games (copies of the engine in scratch folders) were checked against an independent model of rules 2 to 8 (soundings arithmetic, need = guard - Drill - push, drill loss floor, breach and writ pay, barge drop target and timing, status line, turn counter, integrity list): no violation other than item 3.

## Bad input

Refused cleanly, state files byte-identical: unknown id, missing args, `{}`, reach out of range, negative, 1.5, "1", true, null, unknown keys, push 4, -1, 1.5, "2", true, null, missing push, push above soundings, fork 0 or 3, breach and writ out of turn or unaffordable, malformed JSON, list, int, null, `#0`, `#99`, `#-1`, `#abc`, step after the game ended ("the game is over", `state_unchanged`), `new` with bad seeds. Accepted: push 1.0 (normalised), `# 1`, `#09`.

## Rule-test gaps

Not pinned: the label under-reporting the first friend contact (only the post-reveal label is tested); not_friends staying partial after the friend is found; a win by breach or writ on turn 18 (only deploy is tested); `barge_drops_after_turn` for turns 8 to 12; end-to-end ordering of action versus dusk through `step`; hidden-state redraw (`resample_hidden`) consistency; the sound payout on a charted reach (only "offered" is tested); dominated deploys; a breach label when the charted fork is warded (item 1 is pinned the other way).

## Autopsy, replay, check

`check --free`: CLEAN (random 1 percent, heuristic 43, look-ahead 64, mutation 140/140 killed). `autopsy` and `replay` worked on a win (seed 101) and a loss (seed 506); replay also detected a changed constant (matches_saved_state false) and `--apply` rewrote state in a scratch copy. Autopsy regrets use the heuristic as continuation, so it scored my guaranteed winning turn-16 line (deploy, sound, writ) as a 0.75 regret; it does not know the sound-then-writ plan. `ablate` marks train, breach and writ "unproven". `check` could not have caught items 1, 2, 4 (sheet semantics) or 3 and 5 (no label-versus-result check, no integral-float fuzz).
