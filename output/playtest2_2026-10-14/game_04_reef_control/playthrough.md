# Reef Control - playthrough

Rolls: FORM=7 SET=9 ROLE=35 LOOP=34 CLOCK=1 TWIST=39 WIN=14 MAP=3 TONE=8

Engine seed: see rolls.log (python engine.py new, no seed argument).

## Present

```
REEF CONTROL
Your airliner ditched on a ring of reef; you were deadheading in 14B, but you are the only one aboard who ever talked to an aircraft, so ten survivors look at you, while First Officer Dekker has taken three others to a far corner of the atoll.

Rules
1. Each day pick one: forage a tile, or build one thing with food (labor). Camp is C3. At dawn the camp eats 1 food per 3 souls (rounded up).
2. Forage: roll d6, need 4+ for the tile's full yield, else half. Every visit, yours or Dekker's, lowers that tile's yield by 1 (min 2).
3. The inner ring is on foot; the outer ring needs the Raft. The Wreck is somewhere on the outer ring; visiting it unlocks Storehouse and Tower.
4. Builds (food): Trap 4 (water rolls +1), Raft 6, Smokehouse 6 (all rolls +1), Storehouse 7, Palisade 7, Tower 9 (day 10+).
5. Tide table: days 5, 10, 15, 20 are king tides: reef and Wreck closed, lagoon yield doubled. Dawn of day 12 a storm takes half your food unless Storehouse.
6. Dekker's crew (3 who split off) strips one tile a day near his corner. From day 10 they raid 3 food a night unless Palisade.
7. After the dawn meal: food at 0, one soul walks to Dekker; food 20+, one of Dekker's walks to you. Fewer than 6 souls and the camp is done. Two bad forage rolls in a row: Dekker offers 8 food for one soul.
8. Tower lit at dawn on days 13 and 17: roll d6, 3+ for a 12-food airdrop. Win: 8+ souls when the ship comes after day 20.

Goal: 8 or more souls when the ship comes after day 20   Lose if: souls drop below 6   Turns: 20

Turn 1 of 20 | Food 10 | Souls 10 | Built - | Tide low (king 5)
Morning on the reef. The atoll is a ring of five by five squares with your camp at C3; you can see the eight squares around you and nothing past them.
  A  B  C  D  E
1 ?? ?? ?? ?? ??
2 ?? J5 L5 R7 ??
3 ?? J5 CC J5 ??
4 ?? L5 R6 J5 ??
5 ?? ?? ?? ?? ??
Debris keeps washing up on the north shore. Ten mouths eat 4 food at dawn; you have 10. Dekker's smoke has not shown yet.
1. Forage D2 reef (yield 7, reveals fog, need 4+)
2. Forage C4 reef (yield 6, reveals fog, need 4+)
3. Forage B2 jungle (yield 5, reveals fog, need 4+)
4. Build Trap (-4 food)
5. Build Raft (-6 food)
or say anything else.
```

## Turns

**Player:** Food 10, upkeep 4, so a Trap now leaves me at 2 after dawn, which is one bad roll from losing a soul. I'll take the reef at D2: best yield and it opens the north shore where the debris is coming from.

GM: (forage_D2)
roll 4 (need 4+) forage success. The D2 reef gave 7 food, full yield; that tile's yield is now 6.
From the reef you can see the north side: C1 lagoon 7, D1 jungle 7, E2 lagoon 7, E3 reef 8, and at E1 a second smoke: Dekker's camp. His crew worked E3 reef today (yield now 7).
Dawn meal: 4 food.

Turn 2 of 20 | Food 13 | Souls 10 | Built - | Tide low (king 5)
  A  B  C  D  E
1 ?? ?? L7 J7 DD
2 ?? J5 L5 R6 L7
3 ?? J5 CC J5 R7
4 ?? L5 R6 J5 ??
5 ?? ?? ?? ?? ??
Dekker sits in the north-east corner, two squares from your best reef. The debris still comes from the north.
1. Forage C4 reef (yield 6, reveals fog, need 4+)
2. Forage D2 reef (yield 6, need 4+)
3. Forage B2 jungle (yield 5, reveals fog, need 4+)
4. Build Trap (-4 food)
5. Build Raft (-6 food)
or say anything else.

**Player:** Trap. Most of what I can see is water, and a 3+ instead of a 4+ on every reef and lagoon for the rest of the game is the cheapest odds I'll ever buy. Food 13 minus 4 minus the dawn meal still leaves 5.

GM: (build_trap)
Built Trap for 4 food. Two of the cabin crew wove it from seat webbing and a cargo net.
Dekker's crew worked C1 lagoon (yield now 6). Dawn meal: 4 food.

Turn 3 of 20 | Food 5 | Souls 10 | Built Trap | Tide low (king 5)
  A  B  C  D  E
1 ?? ?? L6 J7 DD
2 ?? J5 L5 R6 L7
3 ?? J5 CC J5 R7
4 ?? L5 R6 J5 ??
5 ?? ?? ?? ?? ??
Five food in the tins and ten mouths at dawn. Nothing is affordable to build today. Water tiles now need a 3+.
1. Forage C4 reef (yield 6, reveals fog, need 3+)
2. Forage D2 reef (yield 6, need 3+)
3. Forage B4 lagoon (yield 5, reveals fog, need 3+)
or say anything else.

**Player:** Take the crew to B2 and work the jungle. I want eyes on the north-west corner before I commit to a raft.

GM: There is no action for B2 today; the board offers only C4, D2 and B4. Pick one of those, or say something else.
1. Forage C4 reef (yield 6, reveals fog, need 3+)
2. Forage D2 reef (yield 6, need 3+)
3. Forage B4 lagoon (yield 5, reveals fog, need 3+)
or say anything else.

**Player:** Fine. C4 reef then: 6 at a 3+ and it opens the south.

GM: (forage_C4)
roll 4 (need 3+) forage success. C4 reef gave 6 food, full yield; tile yield now 5.
From the south reef you see B5 jungle 6, C5 lagoon 7, D5 jungle 7. Dekker's crew worked D1 jungle (yield now 6). Dawn meal: 4 food.

Turn 4 of 20 | Food 7 | Souls 10 | Built Trap | Tide low (king 5)
  A  B  C  D  E
1 ?? ?? L6 J6 DD
2 ?? J5 L5 R6 L7
3 ?? J5 CC J5 R7
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
The north row is lagoon, jungle, Dekker. If the debris is honest, the Wreck is at A1 or B1. Tomorrow is the first king tide.
1. Forage D2 reef (yield 6, need 3+)
2. Forage B4 lagoon (yield 5, reveals fog, need 3+)
3. Forage C2 lagoon (yield 5, reveals fog, need 3+)
4. Build Raft (-6 food)
5. Build Smokehouse (-6 food)
or say anything else.

**Player:** Tomorrow is a king tide: reefs close, lagoons double. So today I take the reef at D2 while it's open, and tomorrow C2 lagoon is worth 10 and shows me B1, which is the only north square left that can be the wreck. Raft has to wait; 7 minus 6 minus 4 is a soul walking to Dekker.

GM: (forage_D2)
roll 3 (need 3+) forage success. D2 reef gave 6 food, full yield; tile yield now 5. The Trap earned its keep on that roll.
Dekker's crew worked E2 lagoon (yield now 6). Dawn meal: 4 food.
King tide today: reef and Wreck closed, lagoon yields doubled.

Turn 5 of 20 | Food 9 | Souls 10 | Built Trap | Tide KING
  A  B  C  D  E
1 ?? ?? L6 J6 DD
2 ?? J5 L5 R5 L6
3 ?? J5 CC J5 R7
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
The water is up over the reef flats and the lagoons are boiling with fish pushed in by the tide.
1. Forage B4 lagoon (yield 10 king tide x2, reveals fog, need 3+)
2. Forage C2 lagoon (yield 10 king tide x2, reveals fog, need 3+)
3. Forage B2 jungle (yield 5, reveals fog, need 4+)
4. Build Raft (-6 food)
5. Build Smokehouse (-6 food)
or say anything else.

**Player:** C2 lagoon, doubled to 10, and it reveals B1.

GM: (forage_C2)
roll 3 (need 3+) forage success. C2 lagoon gave 10 food, full yield; tile yield now 4.
From the lagoon you see B1: reef 7. Dekker's crew worked E3 reef (yield now 6). Dawn meal: 4 food.

Turn 6 of 20 | Food 15 | Souls 10 | Built Trap | Tide low (king 10)
  A  B  C  D  E
1 ?? R7 L6 J6 DD
2 ?? J5 L4 R5 L6
3 ?? J5 CC J5 R6
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
Fifteen food, the best larder yet. The north row is reef, lagoon, jungle, Dekker; only A1 is still fog, and the debris still comes from the north.
1. Forage B4 lagoon (yield 5, reveals fog, need 3+)
2. Forage C4 reef (yield 5, need 3+)
3. Forage D2 reef (yield 5, need 3+)
4. Build Raft (-6 food)
5. Build Smokehouse (-6 food)
or say anything else.

**Player:** B1 is reef, so the Wreck is A1, the only north square left. Raft now: 15 minus 6 minus 4 leaves 5, and I need the Wreck before the day-12 storm to build the Storehouse.

GM: (build_raft)
Built Raft for 6 food: two evacuation slides lashed over a spar from the wing. The outer ring is open to you.
Dekker's crew worked C1 lagoon (yield now 5). Dawn meal: 4 food.

Turn 7 of 20 | Food 5 | Souls 10 | Built Trap,Raft | Tide low (king 10)
  A  B  C  D  E
1 ?? R7 L5 J6 DD
2 ?? J5 L4 R5 L6
3 ?? J5 CC J5 R6
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
The raft floats. Five food left and nothing to build with it. The outer ring is richer than the inner, and Dekker keeps shaving the north.
1. Forage B1 reef (yield 7, reveals fog, need 3+)
2. Forage C5 lagoon (yield 7, need 3+)
3. Forage D5 jungle (yield 7, reveals fog, need 4+)
or say anything else.

**Player:** B1 reef. Seven food at a 3+ and it uncovers A1.

GM: (forage_B1)
roll 5 (need 3+) forage success. B1 reef gave 7 food, full yield; tile yield now 6.
From the north reef you can finally see the corner: A1 is the Wreck, yield 8, the tail section sitting in the shallows, and A2 is a lagoon 6. Dekker's crew worked D1 jungle (yield now 5). Dawn meal: 4 food.

Turn 8 of 20 | Food 8 | Souls 10 | Built Trap,Raft | Tide low (king 10)
  A  B  C  D  E
1 W8 R6 L5 J5 DD
2 L6 J5 L4 R5 L6
3 ?? J5 CC J5 R6
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
The galley carts are still in that tail. Two days until the next king tide closes the Wreck; four until the storm.
1. Forage A1 wreck (yield 8, need 3+)
2. Forage C5 lagoon (yield 7, need 3+)
3. Forage A2 lagoon (yield 6, reveals fog, need 3+)
4. Build Smokehouse (-6 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** A1, the Wreck. Eight food at a 3+ and it unlocks the Storehouse, and the king tide on day 10 would close it anyway.

GM: (forage_A1)
roll 5 (need 3+) forage success. A1 wreck gave 8 food, full yield: galley carts, two cases of water, a bin of pretzels. Tile yield now 7.
The Wreck is yours to strip: Storehouse and Tower can now be built. Dekker's crew worked E2 lagoon (yield now 5). Dawn meal: 4 food.

Turn 9 of 20 | Food 12 | Souls 10 | Built Trap,Raft | Tide low (king 10)
  A  B  C  D  E
1 W7 R6 L5 J5 DD
2 L6 J5 L4 R5 L5
3 ?? J5 CC J5 R6
4 ?? L5 R5 J5 ??
5 ?? J6 L7 J7 ??
Tomorrow is the second king tide, and tomorrow night Dekker starts raiding. The storm is three dawns away.
1. Forage A1 wreck (yield 7, need 3+)
2. Forage C5 lagoon (yield 7, need 3+)
3. Forage A2 lagoon (yield 6, reveals fog, need 3+)
4. Build Smokehouse (-6 food)
5. Build Storehouse (-7 food)
or say anything else.

**Player:** Raids start tomorrow night at 3 a night, ten nights, 30 food. The Palisade is the best buy on the island. Build the Palisade.

GM: There is no action for the Palisade today; the board offers Smokehouse or Storehouse as builds. Pick an option or say something else.
1. Forage A1 wreck (yield 7, need 3+)
2. Forage C5 lagoon (yield 7, need 3+)
3. Forage A2 lagoon (yield 6, reveals fog, need 3+)
4. Build Smokehouse (-6 food)
5. Build Storehouse (-7 food)
or say anything else.

**Player:** That's annoying, it was on the board yesterday. Then I bank instead: C5 lagoon for 7, and tomorrow's king tide doubles whichever lagoon I hit. If I'm at 20 at dawn one of Dekker's people walks over.

GM: (forage_C5)
roll 4 (need 3+) forage success. C5 lagoon gave 7 food, full yield; tile yield now 6.
Dekker's crew worked E3 reef (yield now 5). Dawn meal: 4 food.
Day 10: Dekker's raids start tonight. The Tower can be built now. King tide today: reef and Wreck closed, lagoon yields doubled.

Turn 10 of 20 | Food 15 | Souls 10 | Built Trap,Raft | Tide KING
  A  B  C  D  E
1 W7 R6 L5 J5 DD
2 L6 J5 L4 R5 L5
3 ?? J5 CC J5 R5
4 ?? L5 R5 J5 ??
5 ?? J6 L6 J7 ??
Halfway. The tide is up, the reef is under, and the lagoons are full again. Tonight Dekker's people come for the tins.
1. Forage A2 lagoon (yield 12 king tide x2, reveals fog, need 3+)
2. Forage C5 lagoon (yield 12 king tide x2, need 3+)
3. Forage B4 lagoon (yield 10 king tide x2, reveals fog, need 3+)
4. Build Smokehouse (-6 food)
5. Build Storehouse (-7 food)
or say anything else.

**Player:** A2 lagoon at 12 and it reveals A3. 15 plus 12 is 27, minus 3 for the raid, minus 4 at dawn is exactly 20. That's a recruit if the roll holds.

GM: (forage_A2)
roll 3 (need 3+) forage success. A2 lagoon gave 12 food, full yield; tile yield now 5. Past it, A3 is jungle 6.
Dekker's crew worked C1 lagoon (yield now 4). Dekker's raiders took 3 food in the night. Dawn meal: 4 food.
Food 20+. One of Dekker's people walked over to your fire. Souls +1.

Turn 11 of 20 | Food 20 | Souls 11 | Built Trap,Raft | Tide low (king 15)
  A  B  C  D  E
1 W7 R6 L4 J5 DD
2 L5 J5 L4 R5 L5
3 J6 J5 CC J5 R5
4 ?? L5 R5 J5 ??
5 ?? J6 L6 J7 ??
A purser from Dekker's fire came over at first light with her own blanket. Eleven souls still eat 4. The storm hits at tomorrow's dawn; so do the raiders, tonight.
1. Forage A1 wreck (yield 7, need 3+)
2. Forage B1 reef (yield 6, need 3+)
3. Forage D5 jungle (yield 7, reveals fog, need 4+)
4. Build Smokehouse (-6 food)
5. Build Storehouse (-7 food)
or say anything else.

**Player:** status

GM: (python engine.py status, no advance)
Turn 11 of 20 | Food 20 | Souls 11 | Built Trap,Raft | Tide low (king 15)
Upkeep 4 a dawn. Schedule: king tides 5/10/15/20; raids and Tower from 10; storm dawn 12; planes 13 and 17; ship after 20. Map as above. Same five options.

**Player:** The storm takes half at dawn whatever I do. Storehouse for 7 saves me about 5, that's a bad trade. Forage leaves me with a pile the storm eats. Smokehouse leaves me at 2 but with a permanent +1 on every roll, and I'd rather hold a building than a pile. Build the Smokehouse.

GM: (build_smoke)
Built Smokehouse for 6 food: a smoking rack over the fire pit, lined with aluminum from the wing.
Dekker's crew worked D1 jungle (yield now 4). Dekker's raiders took 3 food in the night. Dawn of day 12: the storm hit and swept away 5 food. Dawn meal: 4 food.

Turn 12 of 20 | Food 2 | Souls 11 | Built Trap,Raft,Smokehouse | Tide low (king 15)
  A  B  C  D  E
1 W7 R6 L4 J4 DD
2 L5 J5 L4 R5 L5
3 J6 J5 CC J5 R5
4 ?? L5 R5 J5 ??
5 ?? J6 L6 J7 ??
The storm blew through before dawn and took the tins that were not under the rack. Two food, eleven souls, and the first plane passes tomorrow with nothing on the ground to light.
1. Forage A1 wreck (yield 7, need 2+)
2. Forage D5 jungle (yield 7, reveals fog, need 3+)
3. Forage B1 reef (yield 6, need 2+)
or say anything else.

**Player:** A1 wreck, 7 at a 2+. Only a 1 hurts me.

GM: (forage_A1)
roll 1 (need 2+) forage fail. A1 wreck gave 3 food, half yield: the tide had shifted the tail and the galley was underwater. Tile yield now 6.
Dekker's crew worked D2 reef (yield now 4). Dekker's raiders took 3 food in the night. A plane passed high over the atoll. Nothing on the ground to see. Dawn meal: 4 food.
Food at 0. One soul walked to Dekker. Souls -1.

Turn 13 of 20 | Food 0 | Souls 10 | Built Trap,Raft,Smokehouse | Tide low (king 15)
  A  B  C  D  E
1 W6 R6 L4 J4 DD
2 L5 J5 L4 R4 L5
3 J6 J5 CC J5 R5
4 ?? L5 R5 J5 ??
5 ?? J6 L6 J7 ??
The contrail went straight over the camp while a man from row 30 walked up the beach to the other fire. Empty tins, ten souls, and the night costs 7.
1. Forage D5 jungle (yield 7, reveals fog, need 3+)
2. Forage A1 wreck (yield 6, need 2+)
3. Forage B1 reef (yield 6, need 2+)
or say anything else.

**Player:** The night costs 7 and nothing on the board pays more than 7. I'm losing another soul tomorrow whatever I pick; at 9 souls the meal drops to 3 and the bleeding stops. D5 jungle: 7 at a 3+ with the rack, and it shows me the south-east corner.

GM: (forage_D5)
roll 6 (need 3+) forage success. D5 jungle gave 7 food, full yield; tile yield now 6. Beyond it, E4 is a lagoon 7 and E5 a reef 8, the richest water on the atoll.
Dekker's crew worked D3 jungle (yield now 4), on your side of the island now. Dekker's raiders took 3 food in the night. Dawn meal: 4 food.
Food at 0. One soul walked to Dekker. Souls -1.

Turn 14 of 20 | Food 0 | Souls 9 | Built Trap,Raft,Smokehouse | Tide low (king 15)
  A  B  C  D  E
1 W6 R6 L4 J4 DD
2 L5 J5 L4 R4 L5
3 J6 J5 CC J4 R5
4 ?? L5 R5 J5 L7
5 ?? J6 L6 J6 R8
Nine souls eat 3 now. The night costs 6. Dekker's crew is working D3, within sight of your fire.
1. Forage E5 reef (yield 8, need 2+)
2. Forage E4 lagoon (yield 7, need 2+)
3. Forage A3 jungle (yield 6, reveals fog, need 3+)
or say anything else.

**Player:** E5 reef, 8 at a 2+. That leaves 2 after the night, and tomorrow is a king tide with E4 lagoon doubled to 14.

GM: (forage_E5)
roll 5 (need 2+) forage success. E5 reef gave 8 food, full yield; tile yield now 7.
Dekker's crew worked E2 lagoon (yield now 4). Dekker's raiders took 3 food in the night. Dawn meal: 3 food.
King tide today: reef and Wreck closed, lagoon yields doubled.

Turn 15 of 20 | Food 2 | Souls 9 | Built Trap,Raft,Smokehouse | Tide KING
  A  B  C  D  E
1 W6 R6 L4 J4 DD
2 L5 J5 L4 R4 L4
3 J6 J5 CC J4 R5
4 ?? L5 R5 J5 L7
5 ?? J6 L6 J6 R7
Third king tide. The reef is under and the east lagoon at E4 is the fullest water you have seen.
1. Forage E4 lagoon (yield 14 king tide x2, need 2+)
2. Forage C5 lagoon (yield 12 king tide x2, need 2+)
3. Forage B4 lagoon (yield 10 king tide x2, reveals fog, need 2+)
or say anything else.

**Player:** E4 lagoon at 14. 2 plus 14 is 16, minus 6 for the night is 10, and that puts the Palisade back in reach.

GM: (forage_E4)
roll 4 (need 2+) forage success. E4 lagoon gave 14 food, full yield; tile yield now 6.
Dekker's crew worked E3 reef (yield now 4). Dekker's raiders took 3 food in the night. Dawn meal: 3 food.

Turn 16 of 20 | Food 10 | Souls 9 | Built Trap,Raft,Smokehouse | Tide low (king 20)
  A  B  C  D  E
1 W6 R6 L4 J4 DD
2 L5 J5 L4 R4 L4
3 J6 J5 CC J4 R4
4 ?? L5 R5 J5 L6
5 ?? J6 L6 J6 R7
Ten food, nine souls, four nights of raids left, the last plane tomorrow and a king tide on the final day. Dekker's quadrant is down to 4s.
1. Forage E5 reef (yield 7, need 2+)
2. Forage A1 wreck (yield 6, need 2+)
3. Forage A3 jungle (yield 6, reveals fog, need 3+)
4. Build Storehouse (-7 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** Palisade now costs 7 and a day's forage, call it 14, to block three raids worth 9, and it would drop me to 0 at dawn and cost a soul. The math is gone. I forage from here on: E5 reef, 7 at a 2+.

GM: (forage_E5)
roll 6 (need 2+) forage success. E5 reef gave 7 food, full yield; tile yield now 6.
Dekker's crew worked C1 lagoon (yield now 3). Dekker's raiders took 3 food in the night. A plane passed high over the atoll. Nothing on the ground to see. Dawn meal: 3 food.

Turn 17 of 20 | Food 11 | Souls 9 | Built Trap,Raft,Smokehouse | Tide low (king 20)
  A  B  C  D  E
1 W6 R6 L3 J4 DD
2 L5 J5 L4 R4 L4
3 J6 J5 CC J4 R4
4 ?? L5 R5 J5 L6
5 ?? J6 L6 J6 R6
The second plane went over without slowing. Three nights left; the ship comes after day 20.
1. Forage A1 wreck (yield 6, need 2+)
2. Forage B1 reef (yield 6, need 2+)
3. Forage A3 jungle (yield 6, reveals fog, need 3+)
4. Build Storehouse (-7 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** A1 wreck, 6 at a 2+. Steady state: 11 in, 6 out a night.

GM: (forage_A1)
roll 2 (need 2+) forage success. A1 wreck gave 6 food, full yield; tile yield now 5. The Smokehouse turned a 2 into a full haul.
Dekker's crew worked C2 lagoon (yield now 3). Dekker's raiders took 3 food in the night. Dawn meal: 3 food.

Turn 18 of 20 | Food 11 | Souls 9 | Built Trap,Raft,Smokehouse | Tide low (king 20)
  A  B  C  D  E
1 W5 R6 L3 J4 DD
2 L5 J5 L3 R4 L4
3 J6 J5 CC J4 R4
4 ?? L5 R5 J5 L6
5 ?? J6 L6 J6 R6
Dekker's crew is working the lagoon beside your own camp now; his quadrant is stripped to 3s and 4s. Two nights left.
1. Forage B1 reef (yield 6, need 2+)
2. Forage C5 lagoon (yield 6, need 2+)
3. Forage A3 jungle (yield 6, reveals fog, need 3+)
4. Build Storehouse (-7 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** B1 reef, 6 at a 2+. Saving the lagoons for the king tide on the last day.

GM: (forage_B1)
roll 2 (need 2+) forage success. B1 reef gave 6 food, full yield; tile yield now 5.
Dekker's crew worked D1 jungle (yield now 3). Dekker's raiders took 3 food in the night. Dawn meal: 3 food.

Turn 19 of 20 | Food 11 | Souls 9 | Built Trap,Raft,Smokehouse | Tide low (king 20)
  A  B  C  D  E
1 W5 R5 L3 J3 DD
2 L5 J5 L3 R4 L4
3 J6 J5 CC J4 R4
4 ?? L5 R5 J5 L6
5 ?? J6 L6 J6 R6
One night of raids left, then the last day is a king tide, then the ship.
1. Forage C5 lagoon (yield 6, need 2+)
2. Forage E4 lagoon (yield 6, need 2+)
3. Forage A3 jungle (yield 6, reveals fog, need 3+)
4. Build Storehouse (-7 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** A3 jungle. Hitting a lagoon today knocks a point off tomorrow's doubled yield, and I'm safe either way: 11 plus anything covers the last night. I'll see the west corner while I'm at it.

GM: (forage_A3)
roll 4 (need 3+) forage success. A3 jungle gave 6 food, full yield; tile yield now 5. Past it, A4 is a lagoon 7.
Dekker's crew worked D2 reef (yield now 3). Dekker's raiders took 3 food in the night. Dawn meal: 3 food.
King tide today: reef and Wreck closed, lagoon yields doubled.

Turn 20 of 20 | Food 11 | Souls 9 | Built Trap,Raft,Smokehouse | Tide KING
  A  B  C  D  E
1 W5 R5 L3 J3 DD
2 L5 J5 L3 R3 L4
3 J5 J5 CC J4 R4
4 L7 L5 R5 J5 L6
5 ?? J6 L6 J6 R6
The last king tide. Nine souls on the beach, eleven food, and a ship due after today.
1. Forage A4 lagoon (yield 14 king tide x2, reveals fog, need 2+)
2. Forage C5 lagoon (yield 12 king tide x2, need 2+)
3. Forage E4 lagoon (yield 12 king tide x2, need 2+)
4. Build Storehouse (-7 food)
5. Build Palisade (-7 food)
or say anything else.

**Player:** A4 lagoon at 14 and the last corner of the map. Then we light whatever we have for the ship.

GM: (forage_A4)
roll 3 (need 2+) forage success. A4 lagoon gave 14 food, full yield; tile yield now 6. Past it, A5 is a reef 8, the last square on the map.
The ship's boat grounds on the C3 beach at dusk. Nine souls walk out to it with 25 food in the tins, and you talk the coxswain through the reef gap like it is a runway.

## Ending

Result: WIN. Ship came for 9 souls (needed 8).
Final numbers: Food 25 | Souls 9 | Built Trap,Raft,Smokehouse | 20 turns played.
Verdict: the two king tides on days 10 and 15 paid 12 and 14 and funded the whole second half; the one bad roll (a 1 on a 2+ at Food 2) cost two souls, and the drop to nine souls lowered the meal to 3, which is what let the camp outrun the raids without a Palisade.

Save this one to the library? Give it a name, or say no.
(Playtest run: not saved; no played_log entry written.)
