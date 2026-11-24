# Plan: cleanup and test hardening for /play

Goal: a generated game almost never has a bug the player can hit. Standard: round 2 found an engine or sheet bug in 10 of 10 games. Target for round 3: 0.2 or fewer bugs per game found in play, and zero crashes.

## Bug classes seen, and what catches each

| Bug seen in round 2 | Catcher | Status |
|---------------------|---------|--------|
| Option list capped or filtered, hiding a sheet action (6 of 10) | `ACTIONS` coverage; `GATES` (action missing when affordable, or offered when not) | ACTIONS done, GATES new |
| Sheet number differs from code (10 of 10) | `RULES` template from `CONSTANTS`; `rule_tests` per rule line | RULES done, rule_tests new |
| Rival value clamped so a promised late race never happens | `REACH` (value must be reached in some game), `BOUNDS` (never leaves its range) | new |
| Rule that never fires (liar-proof, Seance, Agnes) | `TAGS` coverage | done |
| Stale or unformatted event string ("None", "{x}") | text lint on every event, label and status line | new |
| Dead or dominated action (10 of 10) | `ablate` warning | done |
| State that breaks after save and reload (sets, tuples, int keys) | JSON round trip on every step of every selftest game | new |
| Hidden state leaking to the player | `visible` check, hidden key scan | new |
| Engine uses its own random, so replay differs | determinism check (same seed twice) | new |
| Crash at a boundary value (0 items, empty list) | fuzz at observed min and max of every numeric key | new |
| Status line changing shape | label stability check | new |
| Bug found mid-play | `integrity` list in every turn JSON; GM stops and fixes | new |

## Layers

1. **Runtime integrity.** Every `step` checks BOUNDS, text lints and JSON safety and returns an `integrity` list. The GM must stop on a non-empty list.
2. **Universal checks in `check`.** Everything in the table that needs no per-game code.
3. **Executable spec.** The engine writes `rule_tests()`: one test per rule line, calling `apply` and `advance` directly on a built state. `check` fails when a rule line has no test or a test fails.
4. **Regression suite for the harness.** `tests/` holds unit tests for `gm_base` and `sameness`, plus mutants of the example engine, each with one injected bug. Every mutant must be flagged by `check`. If a future change to `gm_base` stops catching a bug class, the suite goes red.
5. **Process.** `trace` prints one full game for the GM to read for contradictions. `check` must be CLEAN before presenting. Round 3 measures bugs per game.

## Cleanup

- Delete `tools/temp_merge_fingerprints.py` (one-time backfill, done).
- Remove `__pycache__` folders and stray `tune.count`, `history.jsonl` and `state.json` files in non-session folders.
- Keep `data/fingerprint_backfill_2026-10-14/raw_round*.jsonl` as the source of the backfill. Fingerprints live in `fingerprints.jsonl`.
- Add the CURRENCY field to the played_log format; leave the 20 old lines as they are.
- Update `CLAUDE.md` with the `tools/` folder, `traits.json`, `fingerprints.jsonl`, `variation_backlog.md` and the new commands.
- Update `SKILL.md`: Step 3 reads `sameness.py brief`; Step 5 requires BOUNDS, REACH, GATES and rule_tests; Step 6 verdict gating; Step 7 reads `trace` and `profile`; Ending writes the fingerprint and runs the sameness report, then the autopsy.

## Order of work

1. Plan file (this).
2. Harden `gm_base`: round trip, lints, determinism, BOUNDS, REACH, GATES, rule_tests harness, fuzz, trace, integrity.
3. Bring `example_lantern_chain` up to the full contract.
4. Build `tests/` with mutants and unit tests. Run until green.
5. Update `SKILL.md` and `CLAUDE.md`. Cleanup.
6. Re-verify against the old round-2 engines for crashes.

## Status (2026-10-14, end of phase 1)

Done: plan, harness hardening (gm_checks.py: JSON round trip, text lint, status shape, hidden leak, BOUNDS, REACH, GATES, fuzz, determinism, rule tests, integrity, trace), the reference engine brought to the full contract, tests/ with 21 mutants plus 25 unit tests all green, SKILL.md and CLAUDE.md updated, cleanup. Old round-2 engines re-audited: the new checks found a duplicate-id crash in Hot Lead and a boundary IndexError in Trophy Route that the earlier harness could not see.

In flight: pilot round 3, three freshly generated games under the new instructions, to measure bugs found in play after `check` is clean. Harness files are frozen until the pilot finishes so its results are not confounded.

## Phase 2 (after the pilot)

1. Fold the pilot's harness feedback into gm_checks and the skill; add a mutant for any bug class the pilot finds that `check` missed.
2. Parametric actions, the biggest sameness finding (decision_unit is pick-an-action in 90 percent of games whatever FORM rolls). An option may carry `params`, for example `{"amount": {"min": 0, "max": 40}}` or `{"target": ["a", "b"]}`. The player supplies the value; the runtime validates it against the range; the heuristic returns a value; random play and look-ahead sample min, quarter points, max and the heuristic's value. This lets bids, allocations, placements and routes exist as real decisions. Needs: `_match` and `_norm` handling, `_validate_opts` checks, sampling in the three policies, a mutant for an out-of-range value accepted, a rule-test helper, and one new example action in the reference engine.
3. Roll axes from the variation backlog: TRACKED (1 to 3), TELL (before, after, hidden), FINISH (final-roll, photo-finish, collapse, cliff). Each needs a skill paragraph saying how the generator must honor it and a `profile` or `autopsy` check that verifies it.
4. Round 3 proper: 10 games, bugs per game as the headline number (target 0.2 or fewer), plus the sameness report on the 30 games.

## Status (end of round 3b)

Pilot round 3 (3 games) and round 3b (5 games, each attacked by an independent QA agent) are done. Independent QA found 36 S1 to S3 bugs in 5 games: 18 in the harness (the command line at the end of a game, hostile input, arg types, turn semantics) and 18 in the games (wording, sheet omissions, 0-based display). No independent oracle found an arithmetic mismatch in any game. The engine's own `check` caught none of the 36.

Built in response (harness v3, 34 mutants and 68 unit tests, all green): the end guard and clean errors on every command, strict args, one turn semantics plus `final_check` and `finish`, mutation over helpers and f-string expressions, a vocabulary lint, hidden text in events, balance by hidden starting value, `texts`, wording-pinning rule-test helpers, a TRACKED roll, and a mandatory independent review before a game is presented (`tools/qa_prompt.md`). Details: `playtests/round3b_2026-10-14/round3b_report.md`.

In flight: round 3c, three games generated under v3 with the independent review, then a fresh QA agent on each. Target: zero harness bugs, at most one wording bug per game.

Left over: a scaffold that starts every game from a known-good skeleton (generation still takes 70 to 150 minutes), parametric-action coverage for the old engines, the LEARN, Threads, MECH and render features the user has not yet said to build.

## Status (end of round 3c)

Round 3c (three games under harness v3 with the independent review step, then a fresh QA agent on each): 0 S1 or S2, 16 S3 (12 in the games, 4 cosmetic in the harness, all since fixed). Independent rule models matched every engine on every step in all eight games attacked across rounds 3b and 3c. Round 3b had about 1.6 S1 or S2 per game. Details: `playtests/round3c_2026-10-14/round3c_report.md`.

Built since round 3b: dusk narration lint and `finish()`, a safer autopsy swing cause, clean refusals for every bad command and a damaged state file, `replay --apply` rebuilds state, `{KEY|noun}` on the sheet, constant and derived names in BOUNDS, REACH and GATES, `t.in_order`, a rule for odds in labels, a repeat-the-review rule. 87 tests, all green.

Not done, by decision: a scaffold; gating on `profile` warnings. Not done, awaiting the user: LEARN, Threads, MECH, render.
