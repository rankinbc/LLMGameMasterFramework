# Playtest Report 2: 10 Engine-Backed Games

Date: 2026-10-14
Method: 10 parallel self-play runs of the `/play` skill after the engine rewrite. Each run rolled a game, wrote a Python engine, tuned it with `selftest`, then played it through the CLI as GM and player. Transcripts, engines and summaries are in `game_NN_<slug>/`. Round 1 is in `../round1_2026-10-14/playtest_report.md`.

Caveats. One persona played every game, and the same model played GM and player. The engine rolled every die, so luck was real, but a human would hit more rule friction. Ratings compressed to 6 and 7, so differences inside that range mean little. The counts of hard turns, surprises and bugs are the better signal.

## Scoreboard

| # | Title | FORM | Result | Turns | Hard turns | Surprises | Heuristic win | Tuning runs | Fun |
|---|-------|------|--------|-------|-----------|-----------|---------------|-------------|-----|
| 01 | Hired Knives | pursuit | Loss | 20 | 7 | 6 | 0.36 | 7 | 7 |
| 02 | Thaw Line | heist | Win | 14 of 18 | 5 | 6 | 0.49 | 16 | 7 |
| 03 | The Coral Galley | programming | Win | 16 | 5 | 7 | 0.68 (0.59 fixed) | 5 | 6 |
| 04 | Reef Control | build order | Win | 20 | 6 | 7 | 0.50 | 3 | 7 |
| 05 | Fog Lots | blind auction | Win | 16 | 7 | 6 | 0.42 | 5 | 7 |
| 06 | Hail Term | triage | Win | 20 | 8 | 7 | 0.44 | 7 | 7 |
| 07 | Hot Lead | deduction | Win | 23 of 24 | 6 | 6 | 0.65 | 12 | 7 |
| 08 | Bad Quarter | logistics | Win | 16 | 9 | 9 | 0.51 | 6 | 7 |
| 09 | Greywater Wing | season | Win | 16 | 7 | 6 | 0.55 | 6 | 7 |
| 10 | Trophy Route | dungeon keeper | Win | 14 of 16 | 5 | 6 | 0.54 | 7 | 7 |

## Round 1 against round 2

| Measure | Round 1 (prose only) | Round 2 (engines) |
|---------|---------------------|-------------------|
| Average fun | 6.1 | 6.9 |
| Wins | 7 of 10 | 9 of 10 |
| Hard turns, share of all turns | 38 percent | 37 percent |
| Surprises per game | 6.3 | 6.6 |
| Games with a passive or invisible rival | 4 | 1 |
| Games where the clock never bit | 6 | about 3 |
| Games with an engine or sheet bug found in play | not measurable | 10 |
| Games with a dead or dominated element | 9 | 10 |
| Games with a flat finish | 8 | 8 |
| Minutes per game, including play | 12 | 24 |
| Tokens per game, including play | 117k | 201k |

The engine fixed what a program can fix: no crashes, honest dice, no invented numbers, early wins gone, clocks that bite, rivals that act. It did not touch what a program does not measure. Decision density and the flat finish are unchanged.

## What made games bad

Ranked by how many of the 10 games showed it.

1. **Flat finish (8 of 10).** The outcome was settled well before the last turn and the rest was execution. Cold Burn-style countdowns appeared again: Reef Control turns 16 to 20 were "forage the best square". Hail Term turns 16 to 20 were a victory lap. Trophy Route was a guaranteed 80 or better from turn 10. Hired Knives turns 18 to 20 had nothing to spend on. The player named this in 8 summaries. Two went further: the selftest measures win rate and length, and cannot see tension.

2. **Option list bugs (6 of 10).** The skill's "3 to 5 options" rule collided with engines that cap or filter their own lists. Reef Control's build list was capped at two in dict order, so the Palisade vanished on the day it mattered and the Tower was never offered. Hired Knives dropped "hire" when six actions were legal. Coral Galley's Shanghai option hid Spend. Greywater Wing's hidden cash-reserve filter hid purchases the sheet implies. Thaw Line and Hot Lead offered 6 options on several turns. A legal action the sheet promises but the engine hides is worse than a bug in the numbers, because the player cannot even find it.

3. **Sheet and engine disagree (10 of 10).** Every game had at least one. Three were caught only by the pre-flight reread. The ones with teeth: Coral Galley's rival clamp meant no rival could pass 32, so the late League race the sheet promised never happened. Hot Lead's liar-proof rule fired nobody in two cases the sheet said it would. Bad Quarter's overhaul slipped a week the sheet called one week. Hail Term shipped a stale event string from the first draft. The rulesheet is hand-written prose beside the code, so the two drift.

4. **Dead or dominated elements (10 of 10).** Trophy Route's Pull was strictly worse than Hold, and the pre-flight check passed it because the heuristic was coded to use it. Hail Term's semaphore unlocked when the bank wanted the cash and was pointless after. Bad Quarter's twist, a misplaced container, was unreachable. Thaw Line never saw Seance or Radio. Hired Knives never fired Raid, Comp, Walkout or Stiff. Reef Control's Storehouse sat offered and useless for 8 turns. Usage counts do not detect value. An action that is used 285 times in 300 games can still be strictly worse than its neighbor.

5. **Soft openings, caused by the selftest target (2 of 10).** Coral Galley's summary says it plainly: the target that random play must survive to turn 12 fights the target that sensible play loses a third of the time. Every sharpening of the opening pushed random play over the early-end line, so the opening stayed soft. Waves 1 to 7 played themselves. Hot Lead's opening was nine days of the same pay, bluff or lean choice.

6. **Dice decided the ending (3 of 10).** Hired Knives lost a dominant week on a 1 on a 2+ with no Friday lever. Bad Quarter's final needed a 5-in-6. Greywater Wing's roll-of-1 gear loss hit twice. Down from 5 of 10 in round 1.

7. **Late levers that never fire (5 of 10).** Agnes, Seance and Comp the Regulars all trigger only after two failures in a row, which a good player avoids. They exist on paper and are never felt. The one loss in the round had no lever for a single failed decisive roll.

## What made games fun

1. **Visible arithmetic with a tight margin (10 of 10).** Same as round 1. Every best turn was a sum the player could do from the status line and a margin of one or two.

2. **A rival with a readable habit that the player can use (7 of 10).** This is the clearest gain since round 1. Dekker's crew visibly migrating across the reef. Vane squeezing at the lowest-fuel moment. Carver's biggest-job habit used as a tool, by leaving him the job that lands in a week he already owns. Rooney's own pushes fighting the critic. Kessler left to scoop a node so the player's leads migrate upward. Players did not just beat these rivals. They steered them. Pre-flight rule 6 caused this.

3. **Known future, uncertain present (6 of 10).** Reef Control's tide table made the player plan three days ahead. Bad Quarter's ledger slots gave every dispatch a landing week. Hail Term's bank day. Thaw Line's ghost sightings that put a date on the Generator. Greywater's hangar moving with the line. A schedule the player can read plus dice the player cannot gave the best planning turns.

4. **Exploits the player finds (7 of 10).** Baseline-reset in Hired Knives. Lead migration in Hot Lead. Hold a building, not a shed, before the storm in Reef Control. Night Run as tempo in Bad Quarter. Swap instead of job in Ice Gauge, last round. These are the lines the player remembers. The game only has to leave room and not announce it.

5. **Two systems colliding (10 of 10, 66 instances).** Unchanged from round 1. Examples: roadworks swapping the stop the rival had just targeted, the reef's one bad roll cascading into two lost souls because the night cost 7 and no square paid 8.

6. **Hard trades with a named price (6 of 10).** "Take the 100 percent and lose 5 approval." "Keep the Generator's income or the Lab that outlasts the plane." The player rated these turns highest.

7. **A diagnosis from the engine's own numbers (3 of 10).** Reef Control's food landing on exactly 20 pulled a defector. The selftest's loss reasons told Hired Knives' player what the dominant failure was. This supports the autopsy idea.

## Did the pre-flight rules work

| Rule | Result |
|------|--------|
| 1 Paper-run the economy | Worked. Selftest enforces it. Early wins and early ends gone. |
| 2 Midpoint escalation | Worked in most games. |
| 3 Midpoint unlock | Mixed. Semaphore unaffordable, Express never seen, Radio never drawn. |
| 4 No dead elements | Failed 10 of 10. Judgment only, and usage counts mislead. |
| 5 Odds buyable | Mostly worked. Thin spots: Radio, Fog Lots tend actions. |
| 6 Rival acts with a tell | Worked. The best result of the round. |
| 7 Loss-streak lever | Mixed. Present, rarely felt. |
| 8 Sharp consequences on the sheet | Mixed. Hidden reserve filter and build ordering were not on the sheet. |
| 9 Turn floor | Worked. |
| 10 Decision test at N/2 and N-2 | Failed 8 of 10. Judgment only. |

The pattern is clean. Checks that became numbers in selftest worked. Checks left to the GM's judgment failed. Two of the worst failures are rules the skill already states.

## Repackaging

- **Action sets are distinct.** No two games share more than two action ids. The overlaps are generic verbs: push in three games, hold in three, send in two. The fingerprint check would pass every pair.
- **FORM is distinct.** 10 different forms from 20.
- **SET repeated once.** Hired Knives and The Coral Galley both rolled the restaurant kitchen, and both contain a critic and a review. The reference engine, Friday Rush, is also a kitchen with a critic. Copying its shape leaked its content. Suggest the example moves to a neutral setting, or the skill says to change nouns as well as structure.
- **The skeleton is similar.** Cash is a tracked number in 7 of 10 games, usually beside a score and a rival under a clock. The verbs differ and the economy does not. This is the subtle form of repackaging. A currency roll would address it.

## Cost

A game took about 24 minutes and 200k tokens including a full playthrough, against 12 minutes and 117k tokens without engines. Tuning is the bulk: about 7 runs on average and 16 for Thaw Line. Several agents hand-rolled parameter sweeps because the runtime has none. A real `/play` would make the player wait roughly 10 to 15 minutes before turn 1 at this rate.

The heuristic also undersells a thoughtful player. Final heuristic win rates averaged 0.51, and the persona won 9 of 10. Under that rate, 9 or more wins in 10 has about a 1 percent chance. The selftest bands should be set so a thoughtful player wins about 60 percent, which means a heuristic band near 0.25 to 0.45.

## Recommended changes

Make the failed checks mechanical.

1. **`ablate`.** Ban each action id in turn, rerun selftest, and report the win-rate change. Flag any action whose absence changes the rate by less than 3 points. This catches dominated Pull, dead semaphore, unused Storehouse. It replaces the judgment check.
2. **Coverage counters.** The engine calls a one-line `hit(tag)` for every twist, event, unlock and lever. Selftest flags tags hit in under 5 percent of heuristic games. This catches the unreachable container, Seance, Agnes and Express.
3. **`profile`.** Rollouts from sampled turns of 30 heuristic games. For each turn report the win probability and the spread between the best and worst legal option. Flag a stretch of 3 or more turns with spread under 3 points, and any game decided for 3 or more turns before the end. This measures the flat finish and decision density directly, and it is the same machinery as the autopsy feature.
4. **Options without caps.** The engine's `options` returns every legal action, with same-verb actions merged through a target argument. The GM groups for display. Selftest asserts that every action the sheet names appears in some turn's options. Remove the engine-side cap.
5. **Sheet from constants.** The engine holds a `CONSTANTS` dict and the rulesheet is a template over it, printed by `python engine.py rules`. No number can drift between code and text. Reserve filters and ordering rules must be written into a rule line.
6. **`sweep KEY a,b,c`.** One command to try a constant at several values and print both win rates. Cap tuning at 4 rounds. This should cut generation time roughly in half.
7. **Selftest targets.** Drop the random early-end target. Keep random win rate under 0.35. Heuristic band 0.25 to 0.45. Add a look-ahead policy with a band of 0.5 to 0.8.
8. **Finale lever.** One purchase available only in the last third that changes the final roll, so one failed decisive roll has an answer. Replace "two failures in a row" levers.
9. **Finish when decided.** If `profile` shows the result is settled, the game may end early with the margin shown, rather than playing out a victory lap.
10. **CURRENCY roll.** A d12 for what the primary tracked number is. Cash is one of twelve results. Others: time, trust, attention, heat, stock, light, slots, energy.
11. **Rewrite the example engine** in a setting that is not a kitchen.

## Library candidates

Nothing scored above 7, so none is ready as is. Best skeletons with the fix each needs:

- **Bad Quarter.** Highest decision density of the round at 9 hard turns in 16, and 9 surprises. Fix the yard-slip mismatch and add a cheap order to sweep a dock so the twist is reachable.
- **Hot Lead.** The only deduction game and a clearly different shape. Fix the slow opening and give the late game a counterweight to lead migration.
- **Hired Knives.** The best arc and a real lesson to carry. Add a Friday lever, always offer Hold, and stop the option cap hiding Hire.
- **Reef Control.** The tide table gives the best planning turns. Remove the build-list cap, drop the Storehouse after the storm, and add a late objective.
