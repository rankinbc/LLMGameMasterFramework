# /play redesign: from budget puzzles to games that grow

Written 2026-11-06 after Brass Ring, which the player declined to save: "these games are kind of boring and similar and i feel like the original idea of this project has been drifted from." This is a plan, not a change. Nothing in the skill or the harness has been edited.

## 1. What the games have become

Evidence from `played_log.md` and `fingerprints.jsonl` (34 games):

- Every recent game has the same skeleton: one budget number the player spends and recovers (oil, Seats, Heat), one rival with a hidden rule to read (a stride, a counter, a habit), two bolted-on gambits, a die at the end. The verbs are act-then-recover: light/haul, march/sail, move/lie low.
- 17 of 34 games run exactly 16 turns; 22 are "mid" length. Nothing compounds in 16 turns.
- `decision_unit` is pick-an-action in 21 of 34. `player_frame` is operator or manager in 24 of 34.
- Nothing grows. No game has an income that rises, an upgrade that changes what the next ten turns look like, a map that fills in, or a second path to the win.
- Brass Ring passed `check` clean, seven cold reads found no nonsense, three QA rounds found no S1 or S2, and the player was bored. The review machinery measures clean and balanced; it cannot measure dull.

## 2. What the player actually asked for

From `taste_profile.md`, the lines that no recent game delivers:

- An economy that carries across rounds and snowballs (CS16, WC2, StarCraft).
- Every solution creates the next problem; optimization feeds growth feeds a new bottleneck (Cities: Skylines).
- An upgrade ladder for the player's one vessel or base; tech gates that unlock stronger options.
- Freedom with gravity: trader, fighter, builder are all valid paths; scarcity keeps you moving.
- Finite deposits that deplete and force expansion into contested ground.
- Prepare, perform, assess: a calm buildup, a sharp test, a debrief that feeds the next round.
- Player-set goals in a sandbox; the systems generate wants.
- Mastery over narrative: repeat play with better results is the point.

The profile also says simple rules. The two are not in conflict: Cities: Skylines has dozens of numbers and a child can play it, because every number is a plain thing (people, money, traffic) and the rules are the obvious consequences. The /play limits confused "few rules" with "little state".

## 3. What caused the drift

1. **Hard limits that forbid growth.** 3 tracked numbers, 5 mechanics, 8 rule lines, 12 to 25 turns, one decision a turn. A compounding economy needs an income, a stock, a sink, an upgrade and a threat: that is five tracked things before a map or a rival.
2. **Checks that reward the wrong thing.** The bands (random under 35%, heuristic 25 to 45%) and the flags push toward a tight, balanced puzzle. There is no check for "something got bigger", "there were two ways to win", or "the player's early choice changed the late game".
3. **A generator template that is a budget puzzle.** The reference engine (Lantern Chain) is oil versus wind. Every roll gets bent to fit its shape: CURRENCY becomes the budget, the rival gets a hidden rule, FINISH becomes the die.
4. **Review loops that eat the session.** Brass Ring: 7 cold reads, 3 QA rounds, roughly 80% of the effort, on a game whose design was fixed by turn 1. Polish went up; fun did not move.

## 4. The redesign: /play v4, "games that grow"

Keep: the engine owns every number; the LLM owns words; the sense card and the World card; gambits; STORY and the cast; `check` for crashes, sheet drift, coverage, gates, JSON, determinism; the mutation pass; one QA round.

Change the center of gravity:

### 4a. Mandatory growth

Every game declares `GROWTH`: one number or board that must get bigger over the game (population, fleet, territory, income per turn, a crafting tier). `check` fails a game where heuristic play does not at least double it by the two-thirds mark, or where it can be maxed before the midpoint. The win is usually a growth target or what growth unlocks, not survival of a budget.

### 4b. An economy with three parts, not a budget

Every game declares `ECONOMY`: an income (what comes in each turn and from where), a stock (what is held), and sinks (what it is spent on, at least one of which raises income). The default rival is visible and economic (a competitor's tally, a market that moves, a rival expanding on the same map), not a hidden rule. Hidden rules are a TWIST, not the spine.

### 4c. A ladder

Every game declares `LADDER`: three tiers the player climbs (hut, hall, keep; sloop, brig, frigate; apprentice, journeyman, master), each unlocking at least one new action and one new problem. Tier 2 should land around the first third, tier 3 around the last third. `check` verifies both tiers are reached in heuristic play and that each tier adds an action to the menu.

### 4d. Two paths

Every game declares `PATHS`: at least two action families that can carry a win (trade or raid; build or expand; breed or buy). `check` fails when fewer than 30% of look-ahead wins use the second family, or when ablating either family drops the win rate to near zero (one path is not a game with paths).

### 4e. Longer arcs, bigger boards

Turns: 24 to 40. Tracked state: a board the player can ask to see (`python engine.py board`), up to 8 plain numbers, each a thing in the world. The status line stays at 4 fields: the growth number, the money or stock, the threat, the turn. The rulesheet stays at 8 lines: it teaches the loop and the ladder, not every number. New information arrives through play, as now.

### 4f. New roll tables

Replace FORM and LOOP as the spine with:

- ENGINE (what the economy is): extraction with depleting deposits; trade across a price map; production chain (raw to goods); territory and tribute; contracts and reputation; herd or crop that breeds.
- GROWTH (what gets bigger): headcount, fleet, land, income, tier, map revealed.
- PRESSURE (what pushes back): a rival expanding on the same map; a market that moves against you; a threat that scales with your size; deposits that run out; a deadline with a bill.
- PATHS (the two families): build/expand, trade/haul, fight/raid, scout/claim, research/craft, hire/recruit.

Keep SET, ROLE, TONE, CLOCK, TWIST, MAP, STORY, FINISH. Drop CURRENCY (ECONOMY replaces it) and TRACKED (the board replaces it). FINISH stays rolled.

### 4g. Checks that measure fun, not just balance

Add to `check`: growth curve (4a), ladder reach (4c), path diversity (4d), and a "ripple" score from `ablate` (at least four actions whose removal costs 10 points or more). Keep the difficulty bands but widen the heuristic band to 25 to 55%: a longer game with more paths should be winnable by a sensible player more often than a tight puzzle.

Add to the sameness detector a `skeleton` trait: budget-recover, grow-and-defend, race, build-order, trade-loop, hunt. Flag three in a row.

### 4h. Review budget

One cold read, one QA round, both after the design is settled. If the cold read finds no NONSENSE and the QA round finds no S1 or S2, present. Fix S3s in the game as they come up. Cap review at a quarter of the session's effort.

## 5. Proof sketch: one game in the new shape

Rolls: ENGINE extraction, GROWTH fleet, PRESSURE rival on the same map, PATHS haul and raid, SET asteroid belt, 32 turns, STORY cast.

You run a two-ship salvage outfit in a belt of eight rocks. Each rock has an ore grade that depletes as it is mined. Income: tons of ore per turn per ship on a rock. Sink: ore sells at the station for credits; credits buy a third ship (tier 2, around turn 10), then a refinery (tier 3, around turn 22) that triples the price of what you haul. Rival: the Kessler outfit mines the same belt, claims rocks you leave, and its fleet grows on the sheet every five turns. Paths: haul (grind grade, sell, build) or raid (jump a Kessler barge, roll against its escort, take the cargo and the heat). Pressure: the richest rocks run out first; by turn 20 both fleets are fighting over the last three. Win: own the refinery and 60% of the belt's remaining grade when the survey closes on turn 32. Lose: fleet at zero, or Kessler holds the refinery rock. Cast: four named crew, one per ship plus the station fixer, who die when a ship is lost.

Rulesheet in 8 lines, status in 4 fields (Fleet, Credits, Belt share, Turn), board on request with the eight rock grades and both fleets. Every turn the player does one thing: move a ship, sell, build, raid, or scout a rock. Nothing is hidden except the rival's next target, which it announces a turn ahead. The game is about where to be when the rocks run out.

## 6. Work plan

1. Skill: rewrite the hard limits (section 4e), the roll tables (4f), the generation procedure (ECONOMY, GROWTH, LADDER, PATHS before any code), the review budget (4h). Keep the sense card, World card, gambits, story.
2. Harness: add `GROWTH`, `ECONOMY`, `LADDER`, `PATHS` to the Game contract in `engine/gm_base.py`; add the growth-curve, ladder-reach, path-diversity and ripple checks to `engine/gm_checks.py`; add `board` to the CLI; widen the heuristic band. Mutants first in `tests/test_mutants.py`, then the checks.
3. Sameness: add the `skeleton` trait and a GROWTH roll to `traits.json`; teach `tools/sameness.py` to flag the skeleton streak.
4. Reference engine: replace `engine/example_lantern_chain` with the belt game from section 5 as the new shape to copy.
5. Play one. Judge it by the taste profile, not by `check`.

Estimated size: skill 2 to 3 hours of editing, harness and tests about a day, example engine half a day.

## 7. Decisions for the player

- Turn budget 24 to 40: long enough to compound, or too long for a chat session? A 32-turn game is about 90 minutes of play.
- A board on request (up to 8 numbers) versus keeping everything on one status line.
- Keep the hidden-rule rival as a TWIST option, or retire it for a while.
- The belt game as the first test, or a different ENGINE (trade across a price map; a production chain).

## 8. Done (2026-11-07)

Decisions taken as recommended: 24 to 40 turns, a board on request, the hidden-rule rival kept only as a TWIST (48), the belt game first.

- Harness: `GROWTH`, `ECONOMY`, `LADDER`, `PATHS` on the Game contract; `growth_problems`, `ladder_problems`, `paths_problems`, `economy_problems`, `declaration_problems` in `gm_checks.py`; per-game recording of growth, tier and picks in `gm_base._play`; `board` command and `Game.board`; heuristic band 0.25 to 0.55; TRACKED limit 4; TURNS warning outside 24 to 40. Tests: `tests/test_v4.py` (25 unit tests), a belt mutant suite in `tests/test_mutants.py` (growth capped, ladder top unreachable, dead raid path).
- Sameness: `skeleton` and `growth_kind` traits, ENGINE, GROWTH, PRESSURE and PATHS roll axes, `novelty` reads the v4 axes and warns SKELETON on three alike; the last three games backfilled as budget-recover.
- Skill: rewritten (v4), repo copy updated.
- Reference engine: `engine/example_belt/engine.py` (Belt Claim, 32 turns): CLEAN, random 0.00, heuristic about 0.43, look-ahead 0.58, mutation 80%, both gambits touch the rival.
- Not done: the ripple score in `check` (ablate stays advisory); the old example engine stays for the regression suite.
