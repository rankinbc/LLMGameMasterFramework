# Fever Card: generator report (round 3c, game 2)

Saved by the lead from the generating agent's final reply. This agent had an Agent tool and ran the independent review itself. Note: the lead edited harness files while it was working (a regression in the `_turn` gate lookup, fixed within minutes); it worked around that with a DERIVED value.

## Title and premise

Fever Card. The player books Wall and Sweep crews into four capillary passes of a 4x4 lesion, the Card runs at dusk without them, and they must raise the Granuloma (4 bricks in every pass) before winter freezes the passes and the staph colony Old Gold fills the room.

## Rolls

FORM 15, SET 32, ROLE 51, LOOP 32, CLOCK 8, TWIST 39, WIN 5, MAP 14, TONE 10, CURRENCY 7 (Slots), TRACKED 3 (slots, germs, built). No reroll; verbs 20 percent overlap. Opening shape chosen on purpose: grind or clean-up, not build.

## Check log

1. R1: sheet flags and one failing rule test. Mutation 93 percent. Heuristic 45 percent, look-ahead 100 percent.
2. R2: HEIGHT 3 to 4 and a heuristic rewrite (a 3-brick game was too easy). Mutation 86 percent.
3. R3: CLEAN. Random 0, heuristic 29 percent, look-ahead 99 percent, mutation 99 percent.
4. R4 (cap): CLEAN. Random 0, heuristic 32 percent, look-ahead 79 percent, mutation 100 percent.
After the review, `check --free`: CLEAN, same rates.

## Independent review (run by the generator)

Done once; no S1 or S2, so no second review. S3 fixed: Sweep offered on a finished pass; a die rolled for a full pass; a wrong "tomorrow" in the winter warning; `visible` 0-based (now 1-based); events narrating after the winning brick; sheet omissions (Lance leaves the booking, a frozen pass keeps its contents, no Bloom means no landing, "fill the lesion" reworded). Not fixed: "Germs 13/11" overshoot (truthful, cosmetic). S4 accepted: Stoke sometimes pointless, the surge die rarely decisive from night 7, forced holds, a solved line.

## Texts review

"Card" was never defined on the sheet (option and event now say bookings); "tomorrow is its last dusk" became "night N is its last dusk"; the Lance unlock was reworded; plural variants checked; the roll no longer prints when nothing lands. Trace and profile read: decisions were front-loaded; profile still says FLAT FINISH in 12 of 24 games.

## Warnings accepted

HEURISTIC weak (look-ahead 79 percent against 32 percent): the strong line is learnable and that is the mastery lesson. Stoke is unmissed in ablate: a deliberate decoy. Rule 6 sits at 40 to 41 words.

## Harness feedback

1. `{KEY|noun}` in RULES was rejected by the sheet check. Fixed.
2. A mid-run harness change broke `_turn` gates (the lead's regression). Fixed.
3. Heuristic edits counted as tuning rounds. Fixed: the heuristic is not part of the hash.
4. Look-ahead is the heuristic plus one ply, so one missed opening idea shows as a huge gap; the BAND and HEURISTIC warnings are hard to clear in 4 rounds.
5. `step` ignored trailing positional args; param refusals printed `"options": []`; a missing state.json gave "engine crash". All fixed.
6. `trace` said "1 turns". Fixed.

## Time and effort

About 85 minutes wall clock (QA about 18 of them), 125 tool calls plus 83 for the review subagent; roughly 40 percent on tuning because difficulty came mostly from the opening and the winter deadlines never bound.
