# Kettle Patrol - session state

Playtest game 10, 2026-10-14. Final state (file was rewritten each turn during play; this is the end-of-game version).

## Rolls
SET=26 Submarine patrol zone | ROLE=30 Beast tamer | LOOP=12 Trade favors with factions, spend reputation | CLOCK=4 Storm season, worsening odds | TWIST=11 Damage is permanent; nothing repairs | WIN=4 Destroy a named enemy | MAP=9 A line of 6 nodes that shifts each turn | TONE=8 Cozy with teeth

## Rulesheet
1. You captain the Kettle, a patrol sub with a wet-hold of tamed beasts. Each turn: move one sector along the 6-sector line, or act where you are.
2. The current swaps two neighboring sectors every turn (shown in the line). Your hydrophone says whether the Grey Hull is west, here, or east; at Storm 2+ it only works if you did not move last turn.
3. Factions: Fishers (Kelp Shelf), Tidewalkers (Narrows), Navy (Buoy Line). Do the job on offer at their home sector for Favor with them. Spend Favor there to buy beasts, bait, or intel.
4. Fight: roll d6 + Bite of the beasts you send, minus Storm, vs the target's Guard. Hit: target loses 1 Hull. Miss: each beast sent loses 1 Bite and your Hull loses the target's Teeth.
5. Damage is permanent. Bite and Hull never recover. A beast at Bite 0 is gone. Hull 0 = sunk.
6. Storm = (turn minus 1) divided by 5, rounded down. Moving in a storm: roll d6; if the roll is at or under Storm, Hull -1.
7. Grey Hull: Guard 9, Hull 3, Teeth 2. It moves on its own. If it ends a turn in your sector and you did not attack it, it rolls d6 + Storm; 4+ rams you for 2 Hull.
8. Start: Hull 10, Bruno the mako (Bite 3), Sparks the eel (Bite 2), no Favor.

Goal: sink the Grey Hull. Lose if Hull hits 0 or turn 18 ends. Turns: 18.

## Tracked numbers
- Hull: 1 (started 10)
- Favor: Fishers 2, Tidewalkers 0, Navy 0
- Pack: Bruno 3, Sparks 2, Teacup 5 (total Bite 10)

## Turn
16 of 18 - game over, WIN (Grey Hull sunk)

## Map (line, west to east, final)
Kelp Shelf (Fishers) - Gull Rock - Wreck Field - Deep Trench [Kettle] - Buoy Line (Navy) - Narrows (Tidewalkers)

Current rule: each turn roll d5, swap that neighboring pair (1 = positions 1-2 ... 5 = positions 5-6). Everything in a sector moves with it.

## Hidden facts (now revealed)
- Grey Hull start position: 3 + d3 (rolled 1) = position 4, Buoy Line.
- Grey Hull movement each turn: d6, 1-2 west, 3-4 stay, 5-6 east, cannot pass the ends. Moves after the player's action, before the line swap, then ram check.
- Grey Hull: Guard 9, Hull 3, Teeth 2. Final Hull 0.
- Shops: Fishers - Bait 1F (+2 one attack), the Twins 2F (dolphin pod, Bite 3). Tidewalkers - Rumor 1T (exact sector plus next move direction), Decoy drum 2T (Grey Hull comes to your sector next turn), Teacup 3T (kraken calf, Bite 5; on purchase d6 1-2 she bites a packmate for 1 Bite). Navy - Sonar fix 1N (exact sector), Corvette escort 2N (+3 to one fight), Depth charges 3N (one automatic hit on a target in your sector).
- Job tables (d6 at each faction sector each turn; previous job expires). Fishers: 1-2 sharks in the nets here (Guard 5, Teeth 1) +1F; 3-4 tow a trawler to the next sector east +1F on arrival; 5-6 dive for lost nets, d6 minus Storm need 3+, fail Hull -1, success +1F. Tidewalkers: 1-2 carry a crate to Wreck Field +2T on delivery (Navy -1 if you pass Buoy Line); 3-4 bite test duel vs their eel (Guard 6, Teeth 1) +1T; 5-6 look the other way +1T, Navy -1. Navy: 1-2 report the Grey Hull's position (needs a HERE reading or bought intel) +1N; 3-4 clear a drifting mine (Guard 7, Teeth 2) +1N; 5-6 recover a buoy from Wreck Field +1N on delivery.
- Urgent bonus: if the Grey Hull attacked a faction's home sector in the last 2 turns, that faction pays +2 for a hit on it in their sector (used by Tidewalkers turn 4; offered by Fishers turn 11, unused).
- Wreck Field dive (offered turns 8 and 15, never taken): d6, 5-6 find a Navy depth charge, 1-2 Hull -1.
- Dice were pre-rolled in order and consumed sequentially (see playthrough.md header).

## Log
T1 dive for nets, roll 1 fail, Hull 9. GH -> Narrows. Swap 5-6.
T2 tow trawler to Gull Rock, +1F. GH -> Gull Rock (same sector), ram roll 2 miss. Swap 4-5.
T3 ran east to Narrows. GH followed, ram roll 5, Hull 7. Swap 5-6.
T4 attacked with pack, roll 4+5=9 hit, GH Hull 2, +2T. GH fled east to Trench, swap 3-4 put it west of the Kettle.
T5 duel eel, roll 5+5=10 win, +1T (T3). GH stays. Swap 4-5.
T6 bought Teacup (Bite 5), bite roll 3 no bite. GH stays. Swap 2-3.
T7 status requested. Moved west to Wreck Field, storm roll 6 safe. GH stays. Swap 1-2.
T8 moved west to Gull Rock, storm roll 4 safe. GH stays. Swap 1-2.
T9 moved west into Trench, storm roll 3 safe. GH moved west to Kelp. Swap 2-3 slid Gull Rock between.
T10 moved west to Gull Rock, storm roll 1, Hull 6. GH stuck at west end. Swap 3-4.
T11 moved west to Kelp Shelf, storm roll 1, Hull 5. GH moved east to Gull Rock (passed in the dark). Swap 2-3.
T12 cleared sharks, roll 6+10-2=14 hit, +1F (F2). GH moved west to Wreck Field. Swap 5-6. Hydrophone: east, close.
T13 moved east into Wreck Field, storm roll 3 safe. GH stayed. Swap 2-3. Ram roll 3+2=5, Hull 3.
T14 attacked with pack, roll 3+10-2=11 hit, GH Hull 1. GH fled east to Trench. Swap 5-6.
T15 moved east into Trench, storm roll 6 safe. GH stayed. Swap 5-6. Ram roll 2+2=4, Hull 1.
T16 attacked with pack, roll 3+10-3=10 hit. Grey Hull sunk. WIN.
