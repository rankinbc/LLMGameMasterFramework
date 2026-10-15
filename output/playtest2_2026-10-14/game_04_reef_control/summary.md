# Reef Control - playtest summary (game 04)

## Game

**Title:** Reef Control

**Premise:** Your airliner ditched on a five-by-five ring of reef. You were deadheading in 14B, but you are the only one aboard who ever talked to an aircraft, so ten survivors look at you while First Officer Dekker has taken three others to a far corner. Each day you send the camp to forage one square or spend food as labor on one structure; the camp eats at dawn, Dekker's crew strips the squares near his corner, and people walk between the two fires depending on who has food. The tide table, the storm, the planes and the ship are all published on day 1. Keep eight souls fed until the ship comes after day 20.

**Rolls and what they became:**

| Roll | Value | Became |
|---|---|---|
| FORM | 7 build order | Six structures gated on each other: Raft opens the outer ring, the Wreck (outer ring) unlocks Storehouse and Tower, Tower (day 10+) turns the planes into airdrops |
| SET | 9 shipwreck atoll | 5x5 atoll of jungle, lagoon and reef squares around a central camp |
| ROLE | 35 air traffic controller | A deadheading controller the survivors defer to; the "Tower" build and the plane schedule carry the role |
| LOOP | 34 visit one district, spend money or time, poll the result | Each turn is one forage visit (roll, yield, depletion, fog reveal) or one build paid in food |
| CLOCK | 1 food runs out | Dawn meal of 1 food per 3 souls; food at 0 loses a soul to Dekker; raids from day 10 |
| TWIST | 39 rules change on a published schedule | Tide table: king tides on 5/10/15/20 close reef and Wreck and double lagoons; storm at dawn 12; raids and Tower from 10; planes 13 and 17; ship after 20 |
| WIN | 14 keep a settlement above a threshold | 8 or more souls when the ship comes; fewer than 6 at any time ends the camp |
| MAP | 3 5x5 grid, fog | Inner ring visible at start, outer ring revealed by visiting adjacent squares and by Dekker's tells |
| TONE | 8 cozy with teeth | Pretzels and seat-webbing fish traps, but a soul walks away every time the tins hit zero |

**Rulesheet (verbatim from the engine docstring):**

1. Each day pick one: forage a tile, or build one thing with food (labor). Camp is C3. At dawn the camp eats 1 food per 3 souls (rounded up).
2. Forage: roll d6, need 4+ for the tile's full yield, else half. Every visit, yours or Dekker's, lowers that tile's yield by 1 (min 2).
3. The inner ring is on foot; the outer ring needs the Raft. The Wreck is somewhere on the outer ring; visiting it unlocks Storehouse and Tower.
4. Builds (food): Trap 4 (water rolls +1), Raft 6, Smokehouse 6 (all rolls +1), Storehouse 7, Palisade 7, Tower 9 (day 10+).
5. Tide table: days 5, 10, 15, 20 are king tides: reef and Wreck closed, lagoon yield doubled. Dawn of day 12 a storm takes half your food unless Storehouse.
6. Dekker's crew (3 who split off) strips one tile a day near his corner. From day 10 they raid 3 food a night unless Palisade.
7. After the dawn meal: food at 0, one soul walks to Dekker; food 20+, one of Dekker's walks to you. Fewer than 6 souls and the camp is done. Two bad forage rolls in a row: Dekker offers 8 food for one soul.
8. Tower lit at dawn on days 13 and 17: roll d6, 3+ for a 12-food airdrop. Win: 8+ souls when the ship comes after day 20.

**Fingerprint:** actions = forage_<tile> (one id per offered tile, e.g. forage_D2), build_trap, build_raft, build_smoke, build_store, build_wall, build_tower, bargain. Tracked numbers = food, souls, built (list of structures). Signature detail: Dekker's splinter camp, whose daily tell names and reveals the square he stripped, and the two-way migration rule (food 0 loses a soul, food 20+ wins one back).

## Engine

**Tuning rounds:**

| Run | Policy | win_rate | turn_avg | Flags | What changed before this run |
|---|---|---|---|---|---|
| 1 | random | 0.98 | 21.0 | TOO EASY | First draft: upkeep 1 per 4 souls, inner yields 6/6/7, outer 7/7/8, Wreck 9, start food 12, builds 3/5/5/6/6/8, raid 2 |
| 1 | heuristic | 1.00 | 21.0 | none | same |
| 2 | random | 0.44 | 20.1 | TOO EASY | Upkeep 1 per 3 souls; inner yields 5/5/6, outer 6/6/7, Wreck 8; start food 10 |
| 2 | heuristic | 0.48 | 19.8 | none | same (heuristic barely beat random: built the Raft in half its games and the Palisade in 17 of 300) |
| 2b scratch harness | random / heuristic / forage-only / no-raft | 0.44 / 0.48 / 0.09 / 0.08 | - | - | No engine change; showed builds were cheap and always positive, so random won by building everything |
| 2c scratch harness | heuristic | 0.73 | - | - | Rewrote heuristic as a deadline-aware build plan (Trap, Raft by 12, Storehouse before 12, Palisade 6-14, Tower 10-16, Smokehouse) with a one-meal food buffer instead of two |
| 2d scratch sweep, 12 configs | random / heuristic | 0.17-0.44 / 0.30-0.79 | - | - | Swept raid 2 vs 3, inner yields, build costs; picked raid 3 plus higher build costs for the widest random-to-heuristic gap |
| 3 | random | 0.22 | 19.0 | none | Raid 3; builds Trap 4, Raft 6, Smokehouse 6, Storehouse 7, Palisade 7, Tower 9; rulesheet lines 4 and 6 updated |
| 3 | heuristic | 0.50 | 20.5 | none | same |

**Final selftest (300 games each):** random win_rate 0.22, crashes 0, turn_avg 19.0, early_wins_before_half 0, early_end_rate 0.0, no flags. Heuristic win_rate 0.50, crashes 0, turn_min 12, turn_avg 20.5 (budget 20), early_wins_before_half 0, early_end_rate 0.0, no flags.

**Crashes during play:** none. Twenty steps plus one status call, all clean JSON.

**Rulesheet/engine mismatches found during play:**

1. Build options are capped at two and taken in dictionary order (trap, raft, smoke, store, wall, tower). Once the Wreck is found, Smokehouse and Storehouse occupy both slots while they are affordable and unbuilt, so the Palisade vanished on day 9 (it had been offered on day 8) and the Tower was never offered at all in this game. Rulesheet line 1 says "build one thing" and line 8 describes the Tower; the engine made both conditional on an ordering the sheet does not mention. This is the one real bug. The selftest's heuristic number is partly an artifact of it, since the heuristic's plan is forced through the same ordering.
2. Forage options are capped at three (best expected yield plus a frontier square), so legal-by-rulesheet squares are not always offered. The player asked for B2 on day 3 and was refused.
3. The Storehouse stays on the board after the day-12 storm, when it does nothing; it was a dead option for the last eight turns.
4. Cosmetic: the final status line reads "Tide low" with no next king tide after day 20.

**Free-text refusal path:** tested twice. Day 3, "take the crew to B2" (a reachable square the engine did not list): the GM said in one line that there was no action for B2 and re-showed the three options without advancing; the player picked C4. Day 9, "build the Palisade" (affordable per the rulesheet, hidden by the build cap): same one-line refusal, no advance; the player banked food instead. Both refusals worked mechanically; the second refused something the rulesheet promised, which is mismatch 1 above.

## Playthrough

The player opened on the D2 reef, which paid 7 and revealed Dekker's smoke at E1 and the whole north shore, then bought the Trap on day 2 to make every water square a 3+. With the debris hint pointing north and the north row showing lagoon, jungle and Dekker, he deduced the Wreck had to be at A1 or B1, took the reef the day before the first king tide and the doubled C2 lagoon on it for 10, built the Raft on day 6, and found the Wreck at A1 on day 7 by elimination. On day 9 he asked for the Palisade and was refused because the build list only showed Smokehouse and Storehouse; he banked a lagoon instead, and on the day-10 king tide A2 paid 12, landing food on exactly 20 at dawn so one of Dekker's people walked over (Souls 11). Facing the storm he reasoned that a Storehouse saving 5 for 7 was a bad trade and that a pile would be halved either way, so he converted the food into a Smokehouse and sat at Food 2. The next roll was a 1 on a 2+: half yield, raid, meal, Food 0, a soul walked; and because the night now cost 7 and no square paid 8, a second soul walked the next dawn. That dropped the camp to 9 souls and the meal to 3, which is what stabilized it: E5 reef for 8, the day-15 king tide at E4 for 14, then four days of steady foraging while the Palisade's math quietly stopped working. He saved the lagoons for the last king tide and took A4 for 14 on day 20.

**Result:** WIN. Ship came for 9 souls (needed 8). Final: Food 25 | Souls 9 | Built Trap,Raft,Smokehouse. 20 of 20 turns played (engine turn counter 21 at end). Seed 308763.

## Decisions

Genuinely hard turns: 6 (day 2 Trap at Food 13 with a 4-food meal; day 4 reef today versus lagoon tomorrow; day 6 Raft timing; day 11 Smokehouse versus Storehouse versus forage before the storm; day 16 Palisade arithmetic; day 19 preserving lagoons for the final king tide). Obvious turns: 14, including the four closing turns, which were forage-the-best-square on rails once the threshold was safe. Day 9 would have been a seventh hard turn if the Palisade had been on the board.

## Emergence

Moments where the systems produced something the player did not script: 7.

1. Food landing on exactly 20 at dawn 11 after the player did the sum out loud (27 minus 3 raid minus 4 meal), which pulled a defector across.
2. The one bad roll cascading into two lost souls: a 1 on a 2+ at Food 2, then a second soul the next day because the night cost 7 and no square on the island paid 8. The player saw the second loss coming and could not stop it.
3. The lost souls acting as a stabilizer: at 9 souls the meal dropped from 4 to 3, which is what let the camp outrun the raids without ever building a Palisade. Cruel, legible, and the kind of feedback loop the taste profile asks for.
4. Dekker's crew creeping across the island: his tells moved from E3/C1/D1 in the north-east to D3, C2 and D2 beside the player's camp as his quadrant was stripped to 3s. The rival's policy became visible as a migration.
5. The Storehouse turning out to be a bad buy: the player worked out that the storm halves whatever you hold, so the answer is to hold a building, not a shed. The Smokehouse before the storm was the game's best decision.
6. The Palisade flipping from "best buy on the island" on day 9 to "the math is gone" on day 16 purely from the calendar.
7. The king tides as the economy's heartbeat: 10, 12 and 14 food on days 5, 10 and 15 funded everything, and the player began routing the days before and after around them (reef the day before, jungle the day before the last one).

## Problems

- **Broken:** the two-slot build list in dictionary order (Engine mismatch 1). It hid the Palisade on the turn it mattered most and made the Tower, the airdrops and rulesheet line 8 unreachable in this game. Fix: list every affordable build, or order builds by deadline, and cap only the forage squares.
- **Dead options:** Storehouse offered for eight turns after the storm; the three-square forage cap refused a legal square. Fix: remove Storehouse after day 12, and either show all reachable squares or let the GM map any reachable square id.
- **Repetitive:** turns 16 to 20 were forage-the-best-square with no real choice once souls were safe at 9 with four turns left. The threshold win condition stops generating tension once it is secured; a late objective (the food-20 recruit, or a final tally) would keep the last quarter alive.
- **Unused content:** Tower, Palisade and Storehouse were never built, so three of six structures and both plane events were flavor only. Partly the bug, partly the economy: after the day-12 squeeze there was never a 9-food surplus.
- **Luck versus the selftest:** 14 of 15 forage rolls succeeded; at the mix of 2+ and 3+ targets about 2.5 failures were expected. The one failure cost two souls, which suggests a typical run loses three or four and lands at 7 or 8 souls, matching the selftest's 0.50. The selftest predicted a coin flip; the actual run was a comfortable win on good dice with one sharp scare, which is consistent with that prediction.
- **Not a problem:** nothing was unfair. Every loss was announced a turn ahead by numbers the player could read, and the one 1-in-6 that landed had been accepted out loud.

## Fun rating

7 out of 10. The first fifteen turns were a tight, readable puzzle where every number mattered and the tide table made me plan three days ahead, and the two-soul cascade after the storm was the kind of scare I want from a survival game. It loses points because the build I wanted most was hidden by the interface on the day it mattered, and because the last four turns played themselves.

## Would replay

Yes, once the build list is fixed. I want to try the Palisade-first line (seven food on day 9 blocks 30 food of raids) and a Tower before the day-13 plane, which are the two strategies this run never got to test, and the random map plus Dekker's corner would make the opening different.
