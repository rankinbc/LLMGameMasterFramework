# Cistern Line - Playthrough (playtest game 03)

## Rolls

Command: `echo "SET=$((RANDOM%40+1)) ROLE=$((RANDOM%40+1)) LOOP=$((RANDOM%24+1)) CLOCK=$((RANDOM%18+1)) TWIST=$((RANDOM%36+1)) WIN=$((RANDOM%14+1)) MAP=$((RANDOM%10+1)) TONE=$((RANDOM%8+1))"`

Result: `SET=1 ROLE=33 LOOP=9 CLOCK=1 TWIST=14 WIN=8 MAP=1 TONE=6`

- SET 1: Asteroid belt mining outposts
- ROLE 33: Water engineer
- LOOP 9: Choose a contract, pay a cost, roll the outcome
- CLOCK 1: Fuel or food runs out
- TWIST 14: Each location can only be visited once
- WIN 8: Achieve a majority with three factions
- MAP 1: Linear track of 10 stops
- TONE 6: Military procedural

Novelty check skipped per playtest instructions. Dice for play were pre-rolled with Bash and consumed in order:
- d10 sequence: 3 2 7 3 8 1 6 6 3 10 2 5 5 1 9 8 7 9 4 10 ...
- d6 sequence (transit events): 6 6 5 5 4 6 1 6 3 3 ...

## Present

```
CISTERN LINE
You are the water engineer of Belt Authority tender Cistern, running outbound along the ten-stop mining line under orders to bring two of the Belt's three factions on side by Terminus.

Rules
1. Cistern runs outbound along a 10-stop line. The line is one-way: a stop left behind can never be reached again.
2. Each turn: take one contract at your stop, crack water, or jump ahead. Jump costs 2 fuel, +1 per stop skipped. Every docked turn costs 1 fuel.
3. Contracts show a cost (paid up front, win or lose) and a target. Roll d10; meet the target to succeed. A failed contract closes and may cost more.
4. Success raises Standing with that faction; some contracts lower another's. Standing runs -3 to +5.
5. Factions: Miners' Union (U), Hauler Syndicate (H), Vesta Concession (C). At +2 or better, add 1 to your rolls for that faction. At -2 or worse, that faction's contracts close to you.
6. Crack water: 3 water becomes 3 fuel, no roll.
7. Fuel 0 anywhere but Terminus means adrift: game over.
8. Each jump draws one transit event on the way. Some cost fuel or water, some pay.

Goal: dock at Stop 10 Terminus with Standing +3 or better with two factions.   Lose if: fuel hits 0, or turn 20 ends before you dock.   Turns: 20

Turn 1 of 20 | Fuel 28 | Water 10 | U 0 H 0 C 0 | Stop 1 Ceres Low
Ceres Low Anchorage, Authority depot. Tanks full, orders cut. Three taskings on the dockmaster's board.
1. TASK 1-A [Union] Flush a contaminated cistern, Dock C. Cost 2 water. Need 5+. U+1. Fail: 1 more water lost to a second scrub.
2. TASK 1-B [Concession] Certify Vesta's survey tanks. Cost 1 fuel. Need 4+. C+1, they pay 2 water.
3. TASK 1-C [Syndicate] Top off tug Marigold. Cost 3 water. No roll. H+1, U-1 (Marigold ran strike cargo last quarter).
4. Jump to Stop 2 Pallas Drift (2 fuel).
or say anything else.
```

## Turns

**Player:** Before I pick anything: who holds each stop down the line? I want to know which two factions are worth courting.

```
Dockmaster's line manifest, no charge, no turn spent:
Stop 2 Pallas Drift (Union), 3 Hygiea Yard (Syndicate), 4 Vesta Pit 4 (Concession), 5 Thule Rock (contested Union/Concession), 6 Juno Relay (Syndicate), 7 Davida Cold Store (Union), 8 Psyche Smelter (Concession), 9 Interamnia Slip (Syndicate), 10 Terminus (Authority). Contracts post on arrival only.

Turn 1 of 20 | Fuel 28 | Water 10 | U 0 H 0 C 0 | Stop 1 Ceres Low
Same board. Your call.
1. TASK 1-A [Union] Flush the cistern. Cost 2 water. Need 5+. U+1. Fail: 1 more water.
2. TASK 1-B [Concession] Certify survey tanks. Cost 1 fuel. Need 4+. C+1, 2 water paid.
3. TASK 1-C [Syndicate] Top off Marigold. Cost 3 water. No roll. H+1, U-1.
4. Jump to Stop 2 Pallas Drift (2 fuel).
or say anything else.
```

**Player:** 2. Certify the Vesta tanks. Seventy percent and it pays water.

```
Crew runs pressure checks on the Vesta survey tanks. Roll 3 (need 4+) fail. The seals weep under load; the Concession rep refuses to sign. The fuel spent on the pumps is gone. Task 1-B closed.
Docked upkeep: 1 fuel.

Turn 2 of 20 | Fuel 26 | Water 10 | U 0 H 0 C 0 | Stop 1 Ceres Low
The Concession rep files his report and leaves. Union and Syndicate taskings remain.
1. TASK 1-A [Union] Flush the contaminated cistern. Cost 2 water. Need 5+. U+1. Fail: 1 more water lost.
2. TASK 1-C [Syndicate] Top off tug Marigold. Cost 3 water. No roll. H+1, U-1.
3. Crack 3 water into 3 fuel.
4. Jump to Stop 2 Pallas Drift (2 fuel).
or say anything else.
```

**Player:** 1. Flush the cistern. I don't want to open by burning Union goodwill on the tug.

```
Two tons of clean water go into Dock C's cistern as a flush charge. Roll 2 (need 5+) fail. The biofilm runs deeper than the survey showed; the dockers insist on a second scrub, another ton gone. Task 1-A closed. The Union steward notes the effort. No credit.
Docked upkeep: 1 fuel.

Turn 3 of 20 | Fuel 25 | Water 7 | U 0 H 0 C 0 | Stop 1 Ceres Low
Two taskings failed, nothing on the ledger. Ceres Low has nothing left for you but Marigold.
1. TASK 1-C [Syndicate] Top off tug Marigold. Cost 3 water. No roll. H+1, U-1.
2. Crack 3 water into 3 fuel.
3. Jump to Stop 2 Pallas Drift (2 fuel).
or say anything else.
```

**Player:** 3. Jump to Pallas. Cut losses; this depot has been a sink.

```
Cistern undocks and burns for Pallas. 2 fuel. Transit event: roll 6, favorable alignment. The nav plot finds a cheaper intercept and you bank 1 fuel.
Pallas Drift is a Union ice camp: spin habs, a dead melt plant, a steward who looks at the Authority flash on your hull without warmth.

Turn 4 of 20 | Fuel 24 | Water 7 | U 0 H 0 C 0 | Stop 2 Pallas Drift
1. TASK 2-A [Union] Recommission the ice-melt plant. Cost 2 fuel. Need 6+. U+2, plant pays 3 water. Fail: 1 water lost in the restart.
2. TASK 2-B [Union] Ration audit, certify the camp's water clean. Cost 1 water. Need 4+. U+1. Fail: U-1, they blame the inspector.
3. TASK 2-C [Concession] Serve a lien: shut the camp's unlicensed well. Cost 0. Need 5+. C+2, U-2. Fail: U-1 anyway.
4. Crack 3 water into 3 fuel.
5. Jump to Stop 3 Hygiea Yard (2 fuel).
or say anything else.
```

**Player:** 1. The melt plant. Fifty-fifty, but U+2 with water back is the best rate on the board.

```
Two fuel into the plant's heaters and a long cold restart. Roll 7 (need 6+) success. The melt plant comes up on line; the first run pays 3 tons into your tanks. The steward's tone changes. U+2.
Docked upkeep: 1 fuel.

Turn 5 of 20 | Fuel 21 | Water 10 | U 2 H 0 C 0 | Stop 2 Pallas Drift
Union +2: your rolls for Union work now get +1. The lien is still posted by the Concession's remote office.
1. TASK 2-B [Union] Ration audit. Cost 1 water. Need 4+ (your roll +1). U+1. Fail: U-1.
2. TASK 2-C [Concession] Serve the lien. Cost 0. Need 5+. C+2, U-2. Fail: U-1.
3. Crack 3 water into 3 fuel.
4. Jump to Stop 3 Hygiea Yard (2 fuel).
or say anything else.
```

**Player:** 1. The audit. Eighty percent for the third Union point.

```
Sample runs on every hab tank. Roll 3 +1 = 4 (need 4+) success, just. Water certified clean. U+1.
Docked upkeep: 1 fuel.
Union +3: the steward puts Cistern on the Union wire. Davida Cold Store, Stop 7, will hold a free 4-ton load for you. No roll, no charge.

Turn 6 of 20 | Fuel 20 | Water 9 | U 3 H 0 C 0 | Stop 2 Pallas Drift
One faction secured if you can hold it. Pallas has only the Concession lien left.
1. TASK 2-C [Concession] Serve the lien. Cost 0. Need 5+. C+2, U-2. Fail: U-1.
2. Crack 3 water into 3 fuel.
3. Jump to Stop 3 Hygiea Yard (2 fuel).
or say anything else.
```

**Player:** 3. Jump to Hygiea. Time to start on the Syndicate.

```
Burn for Hygiea Yard. 2 fuel. Transit event: roll 6, favorable alignment again; 1 fuel banked.
Hygiea is a Syndicate tanker yard, gantries and tugs, a dispatcher who talks in manifests. A Union organizer finds you at the airlock.

Turn 7 of 20 | Fuel 19 | Water 9 | U 3 H 0 C 0 | Stop 3 Hygiea Yard
1. TASK 3-A [Syndicate] Refit a tanker's scrubbers. Cost 2 water. Need 5+. H+1, they pay 3 fuel.
2. TASK 3-B [Syndicate] Run water out to stranded freighter Dunlin. Cost 3 water, 1 fuel. Need 4+. H+2, they pay 2 fuel. Fail: 1 more fuel burned on the return.
3. TASK 3-C [Union] Quiet lift of 2 water to the yard's dockers. No roll. U+1, H-1.
4. Crack 3 water into 3 fuel.
5. Jump to Stop 4 Vesta Pit 4 (2 fuel).
or say anything else.
```

**Player:** 2. The Dunlin run. H+2 at seventy percent, and it's fuel-positive if it hits.

```
Cistern matches Dunlin's drift and pumps across. Roll 8 (need 4+) success. Dunlin's crew pay in reaction mass, 2 fuel, and the dispatcher logs it. H+2.
Costs: 3 water, 1 fuel. Docked upkeep: 1 fuel.

Turn 8 of 20 | Fuel 19 | Water 6 | U 3 H 2 C 0 | Stop 3 Hygiea Yard
Syndicate +2: rolls for Syndicate work now get +1. The scrubber refit is still open.
1. TASK 3-A [Syndicate] Refit the scrubbers. Cost 2 water. Need 5+ (your roll +1). H+1, 3 fuel paid.
2. TASK 3-C [Union] Quiet lift to the dockers. Cost 2 water. No roll. U+1, H-1.
3. Crack 3 water into 3 fuel.
4. Jump to Stop 4 Vesta Pit 4 (2 fuel).
or say anything else.
```

**Player:** 1. Scrubbers. Seventy percent to lock the second faction and come out ahead on fuel.

```
Scrubber cartridges swapped, test cycle run. Roll 1 +1 = 2 (need 5+) fail. The new beds foul on the first pass; 2 water flushed out with them. The dispatcher does not log a refit. Task 3-A closed.
Docked upkeep: 1 fuel.

Turn 9 of 20 | Fuel 18 | Water 4 | U 3 H 2 C 0 | Stop 3 Hygiea Yard
Water is getting thin. Seven stops ahead, 14 fuel of jumps at minimum.
1. TASK 3-C [Union] Quiet lift to the dockers. Cost 2 water. No roll. U+1, H-1.
2. Crack 3 water into 3 fuel.
3. Jump to Stop 4 Vesta Pit 4 (2 fuel).
4. Jump to Stop 5 Thule Rock, skipping Vesta (3 fuel).
or say anything else.
```

**Player:** status

```
CISTERN LINE, turn 9 of 20
Fuel 18 | Water 4 | U 3 H 2 C 0 | Stop 3 Hygiea Yard
Ahead: 4 Vesta Pit 4 (C), 5 Thule Rock (U/C), 6 Juno Relay (H), 7 Davida Cold Store (U, free 4 water held for you), 8 Psyche Smelter (C), 9 Interamnia Slip (H), 10 Terminus.
Jump 2 fuel, +1 per stop skipped. Docked turn 1 fuel. Crack 3 water to 3 fuel.
Win: dock at Terminus with two factions at +3 or better. Turns remaining: 12.
```

**Player:** 4. Skip Vesta and jump straight to Thule. Concession work costs me Union points and I need the turns.

```
Burn past Vesta Pit 4 without slowing. 3 fuel. Transit event: roll 5. A Syndicate hauler, Kestrel, hails on the guard channel: tanks dry, crew on ration, drifting at Thule's approach. They can hold one turn.
Thule Rock: a disputed ice claim, Union crew on one side of the dock, Concession surveyors on the other. The dockmaster adds that past Thule the line is Rock Hound country; skiffs run tolls.

Turn 10 of 20 | Fuel 15 | Water 4 | U 3 H 2 C 0 | Stop 5 Thule Rock
1. Pump 2 water to Kestrel. No roll. H+1. Leave Thule without answering and the Syndicate logs it: H-1.
2. TASK 5-A [Union] Certify Thule's claim for the Union. Cost 1 water. Need 5+ (+1). U+2, C-1. Fail: C-1 anyway.
3. TASK 5-B [Concession] Certify for the Concession. Cost 1 water. Need 5+. C+2, U-1. Fail: U-1 anyway.
4. TASK 5-C [Syndicate] Sell 4 water to the Thule stockpile. No roll. H+1, 3 fuel paid.
5. Jump to Stop 6 Juno Relay (2 fuel).
or say anything else.
```

**Player:** 1. Pump Kestrel. The stockpile sale would net zero on Syndicate once I leave her dry, and I'd rather not hit zero water with Rock Hounds ahead.

```
Cistern pumps 2 tons across to Kestrel. Her master signs the transfer on the Syndicate wire. H+1. Kestrel limps off toward Juno.
Docked upkeep: 1 fuel.

Turn 11 of 20 | Fuel 14 | Water 2 | U 3 H 3 C 0 | Stop 5 Thule Rock
Two factions at +3. Now it is holding them and reaching Terminus: five jumps, 10 fuel minimum, with Davida's free load on the way. The stockpile sale needs 4 water; you have 2.
1. TASK 5-A [Union] Certify the claim for the Union. Cost 1 water. Need 5+ (+1). U+2, C-1. Fail: C-1 anyway.
2. TASK 5-B [Concession] Certify for the Concession. Cost 1 water. Need 5+. C+2, U-1. Fail: U-1 anyway.
3. Jump to Stop 6 Juno Relay (2 fuel).
or say anything else.
```

**Player:** 1. Certify for the Union. Cheap buffer on U in case something costs me a point later.

```
Survey logs reviewed, claim markers checked. Roll 6 +1 = 7 (need 5+) success. Thule's ice is entered as a Union claim. U+2. The Concession surveyors pack up; C-1. Task 5-B withdrawn, the claim is decided.
Docked upkeep: 1 fuel.

Turn 12 of 20 | Fuel 13 | Water 1 | U 5 H 3 C -1 | Stop 5 Thule Rock
Union standing capped at +5. Nothing else here you can afford.
1. Jump to Stop 6 Juno Relay (2 fuel).
2. Jump to Stop 7 Davida Cold Store, skipping Juno (3 fuel).
or say anything else.
```

**Player:** 1. Jump to Juno.

```
Burn for Juno Relay. 2 fuel. Transit event: roll 5. Another Syndicate hull on the guard channel: hauler Tern, tanks dry, drifting short of the relay. Same as Kestrel: they can hold one turn.
Juno Relay is a Syndicate comms station, coolant loops and a bored relay chief.

Turn 13 of 20 | Fuel 11 | Water 1 | U 5 H 3 C -1 | Stop 6 Juno Relay
You hold 1 water. Four jumps to Terminus, 8 fuel minimum.
1. Answer Tern's hail. They need 2 water; you have 1. Leave without answering: H-1.
2. TASK 6-A [Syndicate] Barter 3 water for 4 fuel. H+1. Needs 3 water.
3. TASK 6-B [Syndicate] Repair the relay coolant loop. Cost 1 water, 1 fuel. Need 6+ (+1). H+2. Fail: 1 more fuel.
4. TASK 6-C [Concession] Relay data audit. Cost 1 fuel. Need 4+. C+1, H-1.
5. Jump to Stop 7 Davida Cold Store (2 fuel).
or say anything else.
```

**Player:** Pump Tern 2 fuel instead of water. It's the same hydrogen once it's cracked, and I have more fuel than water.

```
Tern's master takes it: 2 fuel of reaction mass in place of 2 water, pumped across on the guard channel's handshake. H+1.
Docked upkeep: 1 fuel.

Turn 14 of 20 | Fuel 8 | Water 1 | U 5 H 4 C -1 | Stop 6 Juno Relay
Fuel 8 against four jumps at 2 each. Zero margin unless Davida's free load becomes fuel. The relay chief has nothing cheaper to offer.
1. TASK 6-B [Syndicate] Repair the coolant loop. Cost 1 water, 1 fuel. Need 6+ (+1). H+2. Fail: 1 more fuel.
2. Jump to Stop 7 Davida Cold Store (2 fuel).
3. Jump to Stop 8 Psyche Smelter, skipping Davida (3 fuel).
or say anything else.
```

**Player:** 2. Davida. Straight there, take the Union load, crack it.

```
Burn for Davida. 2 fuel. Transit event: roll 4. A Rock Hound skiff cuts across the lane and paints you with a ranging laser: toll, 2 water or 2 fuel. You hold 1 ton of water. They take 2 fuel and peel off.
Davida Cold Store: a Union ice mine, intake frozen solid, but the steward has your 4-ton load racked and waiting.

Turn 15 of 20 | Fuel 4 | Water 1 | U 5 H 4 C -1 | Stop 7 Davida Cold Store
Three jumps left, 6 fuel minimum. Fuel 4.
1. Take the Union load. No cost, no roll. +4 water.
2. TASK 7-A [Union] Thaw the mine's frozen intake. Cost 2 fuel. Need 5+ (+1). U+2, mine pays 5 water. Fail: 1 more fuel.
3. TASK 7-C [Syndicate] Broker Davida ice to the Syndicate. Cost 0. Need 5+ (+1). H+1, U-1.
4. Jump to Stop 8 Psyche Smelter (2 fuel).
or say anything else.
```

**Player:** 1. Take the load. Then crack next turn. That puts me at 5 fuel; Psyche then Interamnia then Terminus is 6, but Davida to Interamnia direct is 3 and Terminus is 2 more. Five exactly.

```
Four tons of Union ice come aboard, racked and signed. Water 5.
Docked upkeep: 1 fuel.

Turn 16 of 20 | Fuel 3 | Water 5 | U 5 H 4 C -1 | Stop 7 Davida Cold Store
The steward mentions the thaw job is still open if you want it. The intake creaks.
1. Crack 3 water into 3 fuel.
2. TASK 7-A [Union] Thaw the intake. Cost 2 fuel. Need 5+ (+1). U+2, 5 water paid. Fail: 1 more fuel.
3. TASK 7-C [Syndicate] Broker ice to the Syndicate. Cost 0. Need 5+ (+1). H+1, U-1.
4. Jump to Stop 8 Psyche Smelter (2 fuel).
or say anything else.
```

**Player:** 1. Crack.

```
The cracker runs a full cycle: 3 water in, 3 fuel out.
Docked upkeep: 1 fuel.

Turn 17 of 20 | Fuel 5 | Water 2 | U 5 H 4 C -1 | Stop 7 Davida Cold Store
Fuel 5. Via Psyche the run home costs 6. Skipping Psyche it costs 5, with two transit draws between you and the dock.
1. Jump to Stop 8 Psyche Smelter (2 fuel).
2. Jump to Stop 9 Interamnia Slip, skipping Psyche (3 fuel).
3. Crack (needs 3 water; you have 2).
or say anything else.
```

**Player:** 2. Interamnia, skip Psyche. If a toll hits I pay it in water.

```
Long burn past Psyche Smelter. 3 fuel. Transit event: roll 6, favorable alignment. The plot shaves the intercept and you bank 1 fuel.
Interamnia Slip: a Syndicate barge dock, the last stop before Terminus. The dispatcher already has Kestrel's and Tern's transfers on file; the dockers wave you through.

Turn 18 of 20 | Fuel 3 | Water 2 | U 5 H 4 C -1 | Stop 9 Interamnia Slip
One jump to Terminus, 2 fuel. A toll on the way would take your 2 water.
1. TASK 9-A [Syndicate] Deliver a clean tanker manifest. Cost 2 water. Need 4+ (+1). H+1, 2 fuel paid.
2. TASK 9-B [Syndicate] Tow-assist a Syndicate barge. Cost 2 fuel. Need 6+ (+1). H+2. Fail: 1 more fuel.
3. TASK 9-C [Union] Carry a stranded Union crew to Terminus. Cost 3 water. No roll. U+1.
4. Jump to Stop 10 Terminus (2 fuel).
or say anything else.
```

**Player:** 4. Jump to Terminus. Nothing here raises my odds of winning, and the manifest job would leave me with no water to cover a toll.

```
Final burn. 2 fuel. Transit event: roll 1, clean transit. Cistern coasts into Terminus on 1 fuel and docks.

RESULT: WIN. Docked at Terminus on turn 18 of 20.
Final: Fuel 1 | Water 2 | Union +5, Syndicate +4, Concession -1.
Two factions above +3. Mission complete.
Verdict: the Union sponsor load at Davida and the decision to pay Tern in fuel instead of leaving her dry decided it; the two opening failures at Ceres Low cost nothing that mattered in the end.

Save this one to the library? Give it a name, or say no.
```

**Player:** no (playtest; not saved)
