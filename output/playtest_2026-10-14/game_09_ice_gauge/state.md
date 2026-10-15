# Ice Gauge - session state (final, after turn 13)

Rolls: SET=33 ROLE=39 LOOP=23 CLOCK=8 TWIST=18 WIN=4 MAP=7 TONE=6

## Rulesheet
1. One action per turn: Scout an island with the Sparrow, Take a posted job, Buy and fit one Cormorant part, or Strike. Swapping scrip and silver at the posted rate is free, any turn, whole silver only.
2. Command pays you 6 scrip at the end of every turn. Mill Island sells for silver only, Chapel Island for scrip only, Command requisitions for scrip. The rate moves every turn.
3. The Cormorant strike drone needs Airframe and Payload to fly a strike. Optics +1 and Datalink +1 to the strike roll; Datalink also shows the Marigold's position every turn.
4. Strike: roll d6 + bonuses, need 5+. A hit sinks the Marigold and wins. A miss spends the Payload; on a 1-2 the airframe cracks too.
5. The Marigold moves on a circuit of two docks and four reaches. You may only strike her in a reach; if she is docked when you launch, the strike aborts and the turn is lost.
6. Scouting an island reveals its dock and the reaches beside it. If the Sparrow finds her in a reach, roll d6: on a 1 her crew shoots it down and you can never scout or run jobs again.
7. You may strip the Sparrow's camera to fit Optics for free, but then the Sparrow is gone for good.
8. The ice gauge starts at 10 and drops some turns. At 0 the river freezes, the Marigold walks off over the ice, and you lose. Turn 18 is the hard stop.

## Tracked numbers
- Scrip: 6
- Silver: 0
- Cormorant parts: Air OK, Opt --, Link OK, Pay OK (spent on the winning strike)
Shown world numbers (not player resources): rate 1 Ag = 3.50 scrip, Ice 2.

Turn: 13 of 18. Result: WIN (Marigold sunk).

## Map
Three islands: Ferry (home, command shed), Mill (salvage yard, silver), Chapel (ward and fence, scrip).
Positions on the Marigold circuit: Chapel Dock -> South Reach -> Mill Dock -> Backwater -> North Reach -> West Reach -> Chapel Dock.
Scout coverage: Mill = Mill Dock, Backwater, North Reach. Chapel = Chapel Dock, South Reach, West Reach. Home channels = North, South, West Reach.

## Hidden facts (now revealed)
- Marigold start position: roll 4 = Backwater. In a reach she always moves to the next position at end of turn. At a dock, d6 1-3 stay, 4-6 move.
- Ice drop each turn: d6 1-3 no change, 4-5 minus 1, 6 minus 2.
- Rate drift each turn: d6 1 = -0.50, 2 = 0, 3-4 = +0.25, 5 = +0.50, 6 = +0.25 and draw an event (never triggered; no 6 came up on a rate roll).
- Job offer each turn: d6 1-2 none, 3-4 scrip job, 5-6 silver job. Pay set by GM from a small list (fire-watch 8 Ag, packet run 12 Ag risk on 1, skiff 9 Ag, ice-edge photos 10 Ag, medicine 10 scrip, census 8 scrip).
- Part prices fixed: Airframe 24 Ag, Optics 18 Ag, Datalink 20 scrip, Munitions 30 scrip.
- Signature detail: the ice gauge chalked on the shed wall, a visible clock with hidden drop odds.

## Dice log (pre-rolled d6 stream, consumed in order)
Stream: 4 6 4 4 3 5 5 6 5 2 4 5 1 3 2 6 4 2 4 5 1 2 4 2 3 1 4 6 5 1 5 3 1 5 5 6 2 4 3 6 5 4 6 5 6 3 1 6 ...
- #1 Marigold start = 4 (Backwater). #2 T1 job type = 6 (silver).
- T1 end: ice 4 (-1 -> 9), rate 4 (+0.25 -> 2.25), job 3 (scrip). Marigold -> North Reach.
- T2 end: ice 5 (-> 8), rate 5 (-> 2.75), job 6 (silver, risky packet). Marigold -> West Reach.
- T3: packet risk roll 5 safe. End: ice 2 (8), rate 4 (3.00), job 5 (silver). Marigold -> Chapel Dock.
- T4 end: dwell 1 stay; ice 3 (8); rate 2 (3.00); job 6 (silver).
- T5 end: dwell 4 move -> South Reach; ice 2 (8); rate 4 (3.25); job 5 (silver).
- T6 end: Marigold -> Mill Dock; ice 1 (8); rate 2 (3.25); job 4 (scrip).
- T7 end: dwell 2 stay; ice 3 (8); rate 1 (2.75); job 4 (scrip).
- T8 end: dwell 6 move -> Backwater; ice 5 (7); rate 1 (2.25); job 5 (silver).
- T9: strike roll 3 (+1 = 4, miss); crack roll 1 (airframe cracks). End: Marigold -> North Reach; ice 5 (6); rate 5 (2.75); job 6 (silver, risky packet).
- T10: packet risk roll 2 safe. End: Marigold -> West Reach; ice 4 (5); rate 3 (3.00); job 6 (silver).
- T11 end: Marigold -> Chapel Dock; ice 5 (4); rate 4 (3.25); job 6 (silver).
- T12 end: dwell 5 move -> South Reach; ice 6 (-2 -> 2); rate 3 (3.50); job 1 (none).
- T13: strike roll 6 (+1 = 7, hit). WIN.

## Log
T1 fire-watch +8 Ag. T2 medicine +10 scrip. T3 packet run +12 Ag (roll 5). T4 bought Airframe. T5 bought Datalink; first fix South Reach. T6 bought Munitions. T7 census +8 scrip, Marigold docked Mill. T8 medicine +10 scrip, still docked. T9 strike in Backwater: miss (3+1), airframe cracked (1). T10 status check; packet run +12 Ag (roll 2). T11 swapped 24 scrip for 8 Ag, bought Airframe. T12 bought Munitions; hard freeze, ice 2. T13 strike in South Reach: hit (6+1). Marigold sunk.
