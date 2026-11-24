# Drawdown Depot: playtest 3, game 02

## Title and one-sentence description

Drawdown Depot: a smuggler in debt to a creditor who holds a lien on the Low Ward runs three night buses between the street and tunnels that drain open as the water table falls, while a bureaucratic Assessor on a hidden cycle impounds whichever layer pays most; keep the Ward's beds at 14 or more after night 16.

## Rolls

FORM=12 (logistics) SET=55 (city bus network) ROLE=3 (smuggler with a debt) LOOP=21 (dig deeper) CLOCK=11 (water table drops) TWIST=21 (wandering threat hunts the richest) WIN=14 (keep a settlement above a threshold) MAP=5 (surface and below) TONE=12 (deadpan bureaucratic) CURRENCY=7 (slots, here Ward beds). No rerolls: FORM+SET matched no prior game, FORM 12 was in 1 of the last 5, and the played_log lines carry no CURRENCY so that reroll test could not be applied.

What I changed because of `sameness.py brief` (7 items):
- MAP not 9: rolled 5, nothing to do.
- primary_bucket not cash: CURRENCY rolled slots, so Beds is the primary number and cash never appears.
- tracked_count not 3: chose 2 on purpose (Beds plus the bus board). My first sketch had a live Table number (pumping drops it faster); I dropped that so Table is a fixed countdown, 17 minus the night. This is arguable: if the lead counts Table the game has 3.
- rival_tell not before: the Assessor's order is a hidden cycle (2 richest nights, 1 haunt night, 1 home night, shuffled per seed) and the player infers it from past strikes. Rounds 1 and 2 used per-night dice for the Assessor; I replaced them with the hidden cycle in round 3, partly for this item and partly because dice made choices flat (look-ahead below heuristic).
- ending_shape not flat: gave the game a hard floor (lose below 3) plus a hard KEEP threshold at the end, aiming for photo-finish or cliff. What happened was a slow collapse, so the fingerprint says collapse.
- player_frame not operator: ROLE smuggler was bent into a fleet manager (three buses, one dial per night). Judged manager.
- decision_unit not pick-action: the main verb is assign (move a bus to a layer), and buses start on random layers so the opening is an assignment puzzle. Nine of 16 turns were assignments.

## Result and turns

LOSS on the final audit after all 16 of 16 turns: 6 beds, short of 14. Seed 360553. Beds peaked at 16 on turn 9, the wells failed at table 8 (night 9), and eight Assessor hits plus repeated stalls (five rolls of 1 at a shored Layer 2, which stalls on 1) kept the fleet short.

## Fun rating 1 to 10 with two sentences why

6 out of 10. Working out the Assessor's cycle from two strikes (night 1 home, night 2 haunt, so nights 3 and 4 had to be rich) and the stack-or-spread deflection puzzle were real thinking, and the wells-fail midpoint with a sink-or-bleed purchase was tense; but five of sixteen turns were a bare hold, stall dice swung the result more than my choices did, and from turn 15 nothing I could do changed the outcome.

## Bugs found in play (each: what, which turn, class, and whether `check` could have caught it, or "none")

Engine bugs in play: none. The `integrity` list was empty on all 17 JSON outputs (new plus 16 steps) and no engine crash or illegal action occurred.

Things that felt off, listed so they are not mistaken for "no bugs":
- `visible()` printed "impounded, 1 nights to go" (whenever a bus was held, first seen at the start of turn 3). Class: cosmetic text. `check` could not catch it (the lints do not check plurals). I used "bed(s)" and "night(s)" hedges elsewhere for the same reason.
- The ended game's JSON says `turn` 17 of 16 (final output, turn 16 step). Class: harness cosmetic. `check` does not look at it. The GM must not print "Turn 17 of 16".
- Harness bug found during development (turn n/a, found in check round 1 and verified by hand afterwards): `step shore '{"layer":3}'` when only one `shore` option is legal (layer 2) is accepted. `_match` returns the single candidate whatever the args, and `_step` merges the caller's args over the option's, so the closed Layer 3 got shored and a bed was charged. Class: harness contract bug (an illegal action runs). `check` cannot catch it, because selftests only play offered options, and `t.offered` in rule tests has the same blind spot (it returned True for an unoffered layer, which failed my own rule 7 test in round 1). In real play the GM copies args from the options so it would take a GM slip to trigger.
- On night 13 the Assessor took recess on what the cycle said was a home night. This is by design (8 percent recess), but it made one inference look wrong for a moment; no fix needed.
- The autopsy's top regret (turn 2) depends on the hidden haunt, which no player could have known (see harness feedback).

## Check log

- Round 1: FLAGS (1): RULETEST rule 7 failed ("each layer is shored once"; my test used `t.offered`, which ignores args when one option of that id remains). Warnings: MENU 13 options, BAND look-ahead 27 percent under 60, look-ahead no better than heuristic (heuristic 36, random 0). Tuning round 1 of 4. Before it I had run `selftest` and `sweep` (not counted) to bring a first draft from heuristic 1 percent (far too hard) up to heuristic 36 percent.
- Round 2: CLEAN. Warnings: MENU 14, BAND look-ahead 22 percent, look-ahead no better than heuristic (heuristic 34). Changes since round 1: fixed the test with an exact-args helper, Assessor hunt roll 5+ to 4+, random starting layers, START_BEDS 12, DRY 5, KEEP 18. Tuning round 2 of 4.
- Round 3: CLEAN. Warnings: MENU 14, BAND look-ahead 43 percent under 60 (heuristic 36, so look-ahead now above it). Changes: Assessor dice replaced by the hidden cycle, START_BEDS 14, KEEP 14. Tuning round 3 of 4.
- Round 4: CLEAN, identical numbers and warnings to round 3 (MENU 14, BAND 43 percent). Only cosmetic edits since round 3 (one group label for all moves, rule 5 wording, forfeit text), so this round was a re-run rather than tuning, and it printed the TUNING CAP note. Tuning round 4 of 4.
- Accepted warnings: MENU (all moves share one group, so the GM shows 4 choices: move a bus, shore a layer, sink a well, hold; `check` still prints "set a group" because it counts legal options, not groups). BAND look-ahead 43 percent: the heuristic wins 36 percent, so a thoughtful player has about 7 points of headroom; I did not flatten the game to chase 60.
- Pre-flight: `trace 7` and `trace 7 random` read (found "1 nights" on the sheet, "forfeiting 0", three move groups; all fixed), `profile` (hard share 31 percent, no warnings after the round-3 redesign; before it: FLAT OPENING and LOW DENSITY), `ablate` (move, shore, sink, hold all "needed").

## Time and effort

About 45 minutes of wall clock (folder created 19:59, last file written 20:28, plus roughly 10 minutes of reading before that) and about 75 tool calls: roughly 8 reading the skill and harness, 25 on writing, sweeping and checking the engine (4 `check` rounds, about 9 `sweep`, 3 `profile`, 2 `ablate`), 16 game steps, 6 small plan-simulation scripts at turns 10 to 15, the rest on notes, autopsy, fingerprint and summary.

## Harness feedback

Too loose:
- `_match` and `t.offered` ignore args when only one option of an id exists (verified, see bugs). `step` should reject args that do not equal the option's args, and `t.offered(s, id, **args)` should compare them. This was the only flag the checker raised on my first draft and it was a test-helper trap, not a game bug.
- `check` cannot see plural or grammar problems ("1 nights"), only braces, None, doubled signs and repeated words.
- Nothing verifies that the sheet's wording matches the code's timing (idle nights after an impound); only my own rule tests did, and only because I wrote them from the sentence.

Too strict or confusing:
- The MENU warning says "set a group on each" even when every option has a group; it fires on a count of legal options. It should count groups, or say the groups were seen.
- The look-ahead band differs between SKILL.md (0.5 to 0.8) and `gm_base.py` (0.6 to 0.9). The `check` output printed "under 60%".
- The K=6 look-ahead is too noisy for menus with 10 to 14 options: in the dice version it scored below the heuristic (22 vs 34 percent). My own K=30 run scored 30 percent and K=6 scored 20 percent on 60 games against a heuristic at 34. The "look-ahead no better than heuristic" warning then reads as "choices do not matter" when it may be noise. A larger K for large menus, or paired comparison against the heuristic, would help.
- Look-ahead rollouts and the autopsy copy the whole state including `hidden`, so a hidden-information game gets a look-ahead that cheats and an autopsy that blames the player for unknowable choices (my turn-2 "regret" depended on the hidden haunt).
- Autopsy and profile "hard turn" is best minus worst option. A turn with one obvious move and one disaster counts as hard (autopsy said 14 of 16 turns hard while `profile` said 31 percent). Best versus second best, or best versus the heuristic's pick, would measure difficulty.
- `check` increments the round counter even for a non-tuning re-run; I burned round 4 on a cosmetic edit and got the TUNING CAP note with nothing left to tune. `check --free` and `--quick` exist in code but SKILL.md does not mention them, so a generator either wastes rounds or finds them by reading `gm_base.py`.
- The `played_log.md` format string in the Ending names CURRENCY, but existing lines do not carry it (and none carry MAP or ROLE), so the CURRENCY reroll test in Step 3 cannot be applied from the log.

Unclear instructions:
- "tracked numbers" is fuzzy: does a fixed countdown shown on the status line count? Does the bus board count (the skill says a list with rules counts as one)? I scored it 2, arguably 3. The brief asks for 1 or 2 on purpose, so the definition matters.
- ending_shape cannot be chosen on purpose, only judged afterwards; I aimed for photo-finish or cliff and got collapse. If it matters, the skill needs a design recipe or a post-hoc check (the autopsy only flags flat).
- The rule-test API works well (hidden__ overrides, scripted dice and chances), but the order of rng calls inside `advance` must match the dice list by hand. A note in SKILL.md about the order dice are consumed would save time.
- Step 7 says "read one whole game" but the trace shows only a heuristic and a random policy, not a player who exploits the rival's habit; a "trace with a scripted line" option would let a designer test the intended trick.

Worked well: the rule-tests-per-sheet-line requirement caught my own wording drift ("sits out N nights" versus the code), BOUNDS/REACH/GATES and the JSON round-trip never fired because I used lists and ints, the `integrity` list stayed empty all game, and `sweep` made tuning quick.

## Autopsy as shown to the player

You lost the audit with 6 beds against the 14 needed, and by turn 15 even the best move won only 8 percent of games (0.075).
The game turned on turn 2 (win chance 0.57 down to 0.35): a second bus sent to Layer 1 sat on the Assessor's hidden haunt and was impounded; moving the Layer 1 bus to Layer 2 instead would have lifted your odds from 0.25 to 0.58, though nothing on the table could have told you that yet.
The other missed move was turn 6, where holding (0.30) beat sending the third bus to Layer 2 (0.15).
Fourteen of your sixteen turns had a clearly better and worse option, and no flat stretch was flagged.
