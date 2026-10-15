# Thaw Line: playtest summary (game 02)

## Game

**Title:** Thaw Line

**Premise:** You manage Kelvin Station, an Arctic research base that pays its bills as a hotel for visiting scientists. The crew that froze here in 1971 still haunt the modules, and only you can see them; they know exactly which part of the shelf goes under when, and they will tell you, two slots at a time, until the ice starts moving. Boreas Holdings wants the Specimen (a worm thawed from Core 7) proven SEQUENCED, ALIVE and STABLE and flown out. Turns 1-9 are the plan: bolt modules onto a 12-slot line with a hand of three, keep everything within two slots of a Generator, bank intel. Turn 10 the shelf calves and the execute phase begins: one slot drowns per turn in a hidden order, the plan meets reality, and you run trials with whatever is still powered until the plane comes.

**Rolls and what they became:**

| Roll | Table result | In the game |
|---|---|---|
| FORM=10 | Heist: plan then execute | Turns 1-9 plan with limited intel; turn 10 calving starts the execute phase |
| SET=10 | Arctic research station | Kelvin Station on a calving shelf |
| ROLE=39 | Hotel manager who sees ghosts | Bunks are guest rooms paid in diesel; the 1971 crew are the intel source |
| LOOP=31 | Place one tile; adjacency scores | Hand of 3 modules, next empty slot; a Generator powers everything within two slots |
| CLOCK=12 | Map floods tile by tile | One slot drowns at the end of each of turns 10-17 in a hidden order |
| TWIST=24 | Huge advantage that decays | 52 fuel at start, burned every night, refilled only by powered Bunks |
| WIN=19 | Specimen with all three traits | SEQ, ALIVE, STABLE trials, then call the plane |
| MAP=10 | No map; deck of encounters | Nightly event deck: storm, charter, supply drop, ghost sighting, quiet |
| TONE=2 | Dry humor | The ghosts play cards; you do the brochure copy |

**Rulesheet (verbatim from the engine docstring):**
1. The station is a line of 12 slots; slots 1-3 hold a Freezer, a Bunk and a Generator. Each turn place one of your 3 drawn modules in the next empty slot, or do one other thing (hunkering down redraws the hand and saves 1 fuel).
2. A module is powered if a Generator stands within two slots of it, water or not. Each turn burns 2 fuel plus 1 per Generator; each powered Bunk pays 3 back. Fuel starts at 52 and only guests refill it.
3. Trials (3 fuel, need a powered Lab) prove one trait each: roll d6, need 5 minus powered Labs (min 3). SEQUENCED any time; ALIVE and STABLE only after the thaw on turn 10.
4. After turn 9 the shelf calves: one slot drowns at the end of each of turns 10 to 17 in a hidden order, and the ice groans under the next one a turn early. Before the calving, ask the ghosts (2 fuel) to learn when the two lowest unrevealed slots drown.
5. The Specimen lives in your Freezers: with no powered Freezer standing you cannot run trials or board the plane.
6. Swap (2 fuel): trade the groaning module with its ridge-side neighbour (sea-side if there is none) before the sea takes the slot.
7. Two failed trials in a row open a Seance (2 fuel): your next trial needs only 2+.
8. Win: three traits, then Call the plane (2 fuel): roll d6, need 4 minus powered Radios (min 2). Lose: fuel 0, nothing standing, or the end of turn 18 (the plane lands then anyway: win only with 3 traits and a powered Freezer).

**Fingerprint:**
- Action ids: `place_G, place_L, place_F, place_B, place_R, trial_seq, trial_alive, trial_stable, ask, swap, seance, call, hold`
- Tracked numbers: Fuel; the Line (12 slots of modules with power and flood rules, one list); Traits 0-3.

## Engine

**Tuning rounds** (300 games per policy unless marked sweep = 200 per cell):

| Run | Policy | win_rate | turn_avg | Flags | What changed before this run |
|---|---|---|---|---|---|
| 1 | random / heuristic | 0.00 / 0.02 | 18.5 / 18.3 | TOO HARD | Baseline: 10 slots, fuel 48, power = unbroken run holding a Generator, need 7-Labs, trial 4 fuel, 8 drownings |
| 2 | random / heuristic | 0.00 / 0.02 | 18.6 / 18.5 | TOO HARD | 12 slots (the flood had gutted 10 by turn 14) |
| 3 | random / heuristic | 0.00 / 0.01 | 19.0 / 19.0 | TOO HARD | Fuel 60; Hunker redraws the hand; deck 3G/4R; income-aware heuristic |
| 4 | random / heuristic | 0.00 / 0.01 | 19.0 / 18.8 | TOO HARD | Power rule changed to "Generator within two slots" (the run rule blacked out whole wings per drowning) |
| 5 | random / heuristic | 0.00 / 0.02 | 19.0 / 18.6 | TOO HARD | Need 6-Labs; heuristic checks Generator range |
| 6 | heuristic | 0.03 | 18.5 | TOO HARD | Heuristic rewrite: SEQ in plan phase, mulligan, smarter swap |
| 7 | sweep | 0.12-0.24 / rand 0.01 | 18.0-18.2 | TOO HARD | Start layout F B G (Generator at slot 3 covers 1-5); deck as a constant; swept drownings 6-8 x Generators 4-5 |
| 8 | sweep | 0.14-0.24 / rand 0.01-0.04 | 18.0-18.3 | TOO HARD | Trait loss replaced by the Freezer gate; ghosts plan-phase only; heuristic caps Generators at 3 and fishes for a Radio |
| 9 | sweep | 0.21-0.28 / rand 0.00-0.04 | 17.6-17.7 | TOO HARD | Radio no longer gates the plane call (only improves odds) |
| 10 | random / heuristic | 0.02 / 0.33 | 19.0 / 17.7 | none | Trial 3 fuel; powered Bunk pays 3; call need 4-Radios; phase-2 heuristic may place into empty slots |
| 11 | random / heuristic | 0.02 / 0.28 | 19.0 / 17.5 | TOO HARD | Mulligan guard relaxed; fuel 50 (too tight: 59 fuel deaths) |
| 12 | random / heuristic | 0.01 / 0.29 | 19.0 / 17.8 | TOO HARD | Fuel 56; 4 Freezers in the deck |
| 13 | random / heuristic | 0.01 / 0.26 | 19.0 / 17.5 | TOO HARD, early_end 0.03 | Calving moved to turn 9 (shorter plan phase made weaker lines); reverted |
| 14 | sweep | base 6: 0.32-0.35; base 5: 0.51-0.57 | 16.5-17.7 | none at base 5 | Trial base made a constant; swept drownings 6-8 x base 6/5 x fuel 56/60 |
| 15 | sweep | 0.49-0.53 / rand 0.03 | 16.4-16.7 | none | Base 5; swept floor 2/3 x fuel 52/56 |
| 16 (final) | random / heuristic | 0.03 / 0.49 | 18.9 / 16.6 | none | Base 5, floor 3, fuel 52, 8 drownings |

**Final selftest numbers:** random: 300 games, wins 9, win_rate 0.03, crashes 0, turn_min 15, turn_avg 18.9, early_wins_before_half 0, early_end_rate 0.0, flags none. Heuristic: 300 games, wins 146, win_rate 0.49, crashes 0, turn_min 12, turn_avg 16.6 (0.92 of the 18-turn budget), early_wins_before_half 0, early_end_rate 0.0, flags none.

**Crashes / mismatches found during play:**
- No crashes, no illegal-action errors.
- The engine offered 6 numbered options on turns 3 and 11 (two placements, two trials, swap, hunker), over the skill's limit of 5. The option list is not pruned by phase.
- Rulesheet line 3 originally implied a trial at 0 Labs (need 5+); the engine requires a powered Lab. Fixed on the sheet in pre-flight before play.
- Minor sequencing not on the sheet: when a Generator drowns, that night's burn is computed after the drowning (burn 3, not 4, on turn 11). Consistent with the rule text but not stated.
- The Swap offered on turn 14 (Lab for Freezer) was legal but pointless; the engine does not filter swaps for usefulness.

**Free-text refusal:** on turn 5 the player asked to drag the Generator from slot 3 to slot 6. No action matched (`options` returned only place_F, place_B, ask, hold). The GM answered in one line ("nothing moves a module before the calving; Swap only works on a groaning slot"), re-showed the options and did not advance. Worked as designed. Two other free-text moves mapped cleanly ("Get on the radio and call the Twin Otter" to `call`; "hunker down and redraw" to `hold`).

## Playthrough

Seed 213891. The player opened by paying the ghosts, who said the starting Freezer goes at the end of turn 15 and the Bunk never goes, then built two Labs inside the starting Generator's reach and banked SEQ on turn 4 with a roll of 5. With no Generator in hand and slot 6 dark, the player tried to move the Generator (refused), then hunkered to redraw; the same night a free ghost sighting revealed the slot-3 Generator drowns at the end of turn 11, which meant the Freezer in slot 1 could never be re-powered. The redraw brought a Generator, placed in slot 6; a Lab went into 7, and the Freezer that arrived on turn 8 went into slot 8 as the ridge-side insurance. The last plan turn bought the final ghost answer (slot 4 outlasts, slot 5 goes turn 12). The calving's first two drownings landed on empty pads. ALIVE failed on a 2 then passed on a 4; on turn 11 the player declined to swap the drowning Generator for the long-lived Lab, accepting the loss of all Bunk income. STABLE passed on a 4 on turn 12 for three traits. With no Radio ever drawn, the plane call was a flat 4+: a 2 turned the pilot back in a whiteout, then a 4 landed the Twin Otter on turn 14.

**Result:** WIN on turn 14 of 18. **Final numbers:** Fuel 26 | Traits 3/3 SEQ/ALIVE/STABLE | Line f b ~ L ~ G L! F . ~ . ~ | Labs on 2. **Turns played:** 14 engine turns (plus one status check and one refused free-text move).

## Decisions

14 decision turns. Genuinely hard: 5 (turn 1 ask vs build; turn 4 trial vs build dark vs redraw; turn 5 redraw vs ask vs build dark; turn 9 last ghost answer vs Generator in slot 9; turn 11 swap the Generator and keep income vs keep the Lab that outlasts the plane). Obvious: 9 (turns 2, 3, 6, 7, 8, 10, 12, 13, 14; from turn 12 on the only sensible move was trial or call).

## Emergence

6 moments where the systems produced something not scripted:
1. The free ghost sighting on turn 5 put a date on the starting Generator, and the power-radius rule turned that into "the slot-1 Freezer is dead after turn 11 no matter what": a whole build plan fell out of one event card.
2. The hunker redraw fetched the Generator the same night that sighting landed; a mulligan turn became the pivotal turn.
3. The hidden crack order spent its first two drownings (slots 10 and 12) on pads the player never built, because 9 plan turns cannot fill 12 slots; the flood wasted a quarter of its bite.
4. The turn-11 swap offer was a real trade produced by three rules interacting (intel on slot 4, the groan on slot 3, the Generator radius): keep the Generator and the Bunk's 3 a night, or keep the Lab the ghosts said outlasts the plane.
5. The trial floor of 3 made the third Lab retroactively irrelevant; the player noticed and used it to justify trialing instead of swapping.
6. Losing the slot-3 Generator cut the nightly burn from 4 to 3, a small coherent upside to a loss.

## Problems

- **Flat finish.** Once three traits were banked (turn 12) the rest was rolling a 4+ with nothing else worth doing. The Radio is the intended odds-buy and was never drawn, so the preflight "no flat coin flip" rule was honored only on paper. Two of the last three turns had no real decision.
- **Empty-slot drownings.** The crack order covers all 12 slots but the plan phase can fill at most 9. Drownings on empty pads are free, which blunts the clock. The order should only cover built slots, or the line should be 10 with a 9-turn plan.
- **Option count.** 6 options on two turns, over the limit.
- **Thin hotel.** Only the starting Bunk was ever built; income was 3 a night then 0. The hotel half of the ROLE roll barely registered, and fuel never got close to 0 (ended at 26). The decaying-advantage twist was felt in the plan phase (two early storms) but not in the execute phase.
- **Unused levers.** Seance never triggered (no two failed trials in a row); Radio never appeared; Swap was offered three times and never taken. Dead elements in this run, not necessarily in the design.
- **Easier than predicted.** The selftest heuristic wins 0.49; the player won with four turns to spare on average dice (two failed rolls, four passes). Credit goes to intel use (two asks plus a lucky sighting) and the two empty-slot drownings. One run is not a sample, but the design leans easy for a player who buys the ghost intel early.
- **Status line field.** "Labs on" is dead information once traits are banked; the field could switch to the next drowning.
- Not broken, not unfair, not repetitive in the plan phase; repetitive in the last three turns.

## Fun rating

7/10, as the player. The turn-5 reveal that the Generator had a date on it, and the turn-11 choice between the Generator's income and a Lab that would outlast the plane, were exactly the kind of systems-colliding decisions I want; I was doing arithmetic on fuel, reach and drowning dates every turn of the plan phase. The ending was three coin flips in a row with nothing to spend on them, and the hotel side never became a system.

## Would replay

Yes. The hidden crack order, the hand order and the event deck make a second seed a different build problem, and I want to try the other line (Bunk-heavy economy, Radio for a 3+ call, third Generator at slot 9). I would want two fixes first: cracks only under built slots, and a second odds-buy for the plane call that does not depend on drawing one card.
