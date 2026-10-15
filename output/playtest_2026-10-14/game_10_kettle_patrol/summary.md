# Kettle Patrol - playtest summary

Playtest game 10, 2026-10-14. Folder: `output/playtest_2026-10-14/game_10_kettle_patrol/`

## Game

**Title:** Kettle Patrol

**Premise:** Storm season on the Shelf. The Kettle is a small, tea-stained patrol submarine whose weapons are tamed sea beasts kept in a wet-hold: Bruno the mako, Sparks the eel, and whatever else the player can buy. Something armored and wrong, the Grey Hull, is chewing the buoy line and the fishing fleet. Three factions share a six-sector patrol line that the current reshuffles every turn; each has a home sector, a job board, and a shop. The player earns Favor by doing jobs, spends it on beasts, bait, or intel, and tries to find and sink the Grey Hull before the storm makes rolls impossible or the hull gives out. Nothing ever repairs.

**Rolls and what they became:**

| Roll | Table result | In the game |
|---|---|---|
| SET=26 | Submarine patrol zone | The Shelf: a 6-sector patrol line, player commands the sub Kettle |
| ROLE=30 | Beast tamer | Weapons are tamed beasts with Bite values; shops sell more beasts |
| LOOP=12 | Trade favors with factions, spend reputation | Three factions (Fishers, Tidewalkers, Navy), one job per turn at their home sector for Favor, Favor spent in their shop |
| CLOCK=4 | Storm season, worsening odds | Storm = (turn-1)/5, subtracted from every roll; moving in storm risks Hull |
| TWIST=11 | Damage is permanent; nothing repairs | Hull and Bite only go down; no repair exists anywhere in the game |
| WIN=4 | Destroy a named enemy | The Grey Hull: Guard 9, Hull 3, Teeth 2, moves on its own |
| MAP=9 | A line of 6 nodes that shifts each turn | Each turn one adjacent pair of sectors swaps (d5); everything in a sector moves with it |
| TONE=8 | Cozy with teeth | Tea, biscuits, named beasts, a crew; the beasts and the Grey Hull bite |

**Signature detail (invented):** the hydrophone. Every turn it reports whether the Grey Hull is west, here, or east, but once Storm reaches 2 it goes deaf on any turn after the player moved, so chasing blind versus listening becomes a real tradeoff.

**Rulesheet (verbatim):**

1. You captain the Kettle, a patrol sub with a wet-hold of tamed beasts. Each turn: move one sector along the 6-sector line, or act where you are.
2. The current swaps two neighboring sectors every turn (shown in the line). Your hydrophone says whether the Grey Hull is west, here, or east; at Storm 2+ it only works if you did not move last turn.
3. Factions: Fishers (Kelp Shelf), Tidewalkers (Narrows), Navy (Buoy Line). Do the job on offer at their home sector for Favor with them. Spend Favor there to buy beasts, bait, or intel.
4. Fight: roll d6 + Bite of the beasts you send, minus Storm, vs the target's Guard. Hit: target loses 1 Hull. Miss: each beast sent loses 1 Bite and your Hull loses the target's Teeth.
5. Damage is permanent. Bite and Hull never recover. A beast at Bite 0 is gone. Hull 0 = sunk.
6. Storm = (turn minus 1) divided by 5, rounded down. Moving in a storm: roll d6; if the roll is at or under Storm, Hull -1.
7. Grey Hull: Guard 9, Hull 3, Teeth 2. It moves on its own. If it ends a turn in your sector and you did not attack it, it rolls d6 + Storm; 4+ rams you for 2 Hull.
8. Start: Hull 10, Bruno the mako (Bite 3), Sparks the eel (Bite 2), no Favor.

Goal: sink the Grey Hull. Lose if Hull hits 0 or turn 18 ends. Turns: 18.

## Playthrough

The player opened by taking the Fishers' net-diving job and failed the very first roll, losing a Hull point for nothing. The trawler tow on turn 2 paid a Favor but the Grey Hull slid under both boats mid-tow, and when the player declined a 50/50 swing with an unupgraded pack and ran east to the Tidewalkers, the Grey Hull followed and rammed (Hull 7). Cornered, the player attacked with the full pack, rolled exactly the 9 needed, and collected a +2 urgent bonus from the Tidewalkers, which plus a free-win eel duel bought Teacup the kraken calf on turn 6 for Bite 10, making every attack an automatic hit until Storm 3. The rest of the game was a chase: the Grey Hull wandered to the west end of the line, the current slid sectors between them twice, and the player paid two storm rolls (Hull 6, then 5) and passed the target in the dark on turn 11. Staying put on the Kelp Shelf to clear sharks restored the hydrophone and revealed the Grey Hull next door; the player closed on turn 13, ate a ram (Hull 3), and landed the second hit on turn 14. With three turns left and Storm 3 coming, the player did the arithmetic out loud, closed into the Trench, was rammed again to Hull 1, and sank the Grey Hull on turn 16 with a 3 on the die against a 2+ requirement.

**Result:** WIN on turn 16 of 18. Final numbers: Hull 1, Favor F2 T0 N0, Pack Bruno 3 / Sparks 2 / Teacup 5 (Bite 10), Storm 3. Grey Hull Hull 0.

## Rules fit

- Rulesheet: 8 lines, no more. Each line is dense (line 7 carries three facts) but it read as one sheet.
- Tracked numbers: Hull, Favor, Pack. Favor is really three sub-counts (F/T/N) and Pack is a list of three beasts with Bite values, so the status line shows seven digits. This is within the letter of the cap (a list counts as one) but it is the upper edge of it. A one-number Favor pool would have been simpler and would have lost the per-faction flavor the taste profile asks for.
- One decision per turn: held every turn. Buying a beast and moving were never offered in the same action.
- Status line: same format every turn, with the whole line of sectors and the player's sector in brackets. It was long (about 20 words) but it carried the map, so no separate map block was needed.
- Turn length: all turns under 180 words after one trim; the turn 5 output (hit narration plus the Tidewalker shop listing) first came out at 191 and had to be cut to about 170. Shop listings are where the budget goes.
- Rules invented mid-game, each explained in one line when it mattered: the urgent bonus (+2 Favor for a hit in a faction's water after the Grey Hull attacked them); the wreck-diving salvage roll at Wreck Field; the Grey Hull cannot move past the ends of the line; a job expires when the next one is rolled; Teacup's on-purchase bite roll. None of these broke the sheet and none required memorizing.
- Unclear: whether moving into the Grey Hull's sector counts as "did not attack" for the ram check. The GM ruled yes (you only attack on a turn you start in its sector), which is consistent but makes every approach cost a 2-Hull ram on 4+ (5/6 at Storm 2). The player understood it by turn 9 and planned around it, but it should be stated in rule 7.
- Also unclear until shown: the order of hidden resolution (Grey Hull moves, then the line swaps, then ram check). The GM kept it fixed and it never contradicted itself, but the player had to infer it.

## Decisions

16 turns played (plus one `status` query that did not advance the turn).

- Genuinely hard: 4 (turn 3 attack-or-flee with a weak pack; turn 6 Teacup versus Rumor+Decoy; turn 13 close now or hold; turn 15 close at Hull 3 with a real death chance).
- Moderate: 3 (turn 4 swing versus keep running; turn 11 move blind versus wait for the hydrophone; turn 12 sharks-and-listen versus chase).
- Obvious: 9 (turns 1, 2, 5, 7, 8, 9, 10, 14, 16: free favor, "move west", or "attack, it is here and you auto-hit").

The obvious turns were mostly the chase in the middle (turns 7 to 10), where the only sensible move was "one sector west" four times in a row.

## Emergence

Moments where the systems produced something the GM did not script:

1. Turn 2: the Grey Hull's random move put it under the trawler the player was towing; the ram roll missed, so it became a HERE reading with a 50/50 decision attached.
2. Turn 3: the player ran east and the Grey Hull's movement roll followed; it rammed in the Tidewalkers' harbor, which triggered the Tidewalkers' urgent bounty and turned a bad turn into the cheapest +2 Favor in the game.
3. Turn 4: the Grey Hull fled east after being hit, then the current swapped the Narrows and the Trench, so the hydrophone said "west" one turn after the player watched it go east.
4. Turn 9: the player entered the Trench to engage, the Grey Hull stepped west, and the swap slid Gull Rock in between them, converting a one-sector gap into two.
5. Turn 11: the player ran toward the Fishers' flares, the Grey Hull moved east, and they passed in the dark; the GM could narrate it because the Fishers had been attacked and would say so.
6. Turn 13: the current swapped the sector both boats were in, carrying them together, which read as the Grey Hull deliberately staying to fight.
7. Turn 16: the ending was decided by a 2+ roll with the player at Hull 1, entirely produced by the accumulated storm and ram rolls rather than any designed set-piece.

Count: 7. At least one in every 4-turn window.

## Problems

- The favor-trading loop (the rolled LOOP) ended up secondary. The player did four jobs, bought one thing, and never visited the Navy at all. The decisive purchase was made by turn 6; after that Favor had nothing worth buying because the pack already auto-hit. More Bite past 10 is worthless, so the Twins and Bait were dead options for the last ten turns. The shop needs something that matters late: contact (Decoy drum, Sonar fix) was the real bottleneck but was at the far end of the line.
- Contact is a coin flip. The Grey Hull moves 1-2 west / 3-4 stay / 5-6 east, and the line swap adds a second random displacement. Four consecutive turns (7 to 10) were "move one west" with no decision. A hunt loop needs tells; here the only tell was the hydrophone, and it was deaf exactly when the player was chasing.
- Approach is always punished. Entering the target's sector hands it a free ram on 4+ (5/6 at Storm 2). Combined with storm move damage, the Kettle lost 9 of 10 Hull and only 1 of it to a failed action roll. The player never missed a swing and still finished at Hull 1. The ram rule should give the player a reaction roll or only trigger when the Grey Hull is the one who moved in.
- Too swingy at the end. The turn 15 decision was good tension but the win was one unlucky storm roll from a loss that would have been nobody's fault. Fair-but-unforgiving is the taste; this was closer to fair-but-random.
- The Navy was never relevant. A faction that never gets visited in a 16-turn game is a sign the line is too long for one-sector moves, or the Navy's goods are not attractive enough to walk to.
- Turn 1's failed roll (Hull -1, no Favor) was a flat start: a 1-in-3 chance of pure loss on the first action.
- Too hard? Not quite: the win came with a margin of one Hull and two turns, which is about right for a 16-turn game, but the margin was dice rather than skill after turn 6.

## Fun rating

**6 / 10.** The player persona would say: the Teacup purchase and the turn 15 math were exactly the kind of system-reading I like, and the shifting line with the hydrophone produced real surprises. But the trading side I showed up for was over by turn 6, and then I spent eight turns walking west and getting rammed for the crime of arriving, which is not a system I can get better at.

## Would replay

Yes, with reservations. There is a learnable lesson (contact is the scarce resource, not Bite; buy the Decoy drum or Navy sonar early and let it come to you), and the taste profile prizes exactly that kind of "I know what to do differently" replay. But the GM should fix the free ram on approach and give Favor something to buy in the late game before this goes in the library.