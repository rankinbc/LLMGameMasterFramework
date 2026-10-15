# Dry Reckoning - playtest summary (game 08)

## Game

**Title:** Dry Reckoning

**Premise:** You govern Qasr Ashab, a walled desert city on a well whose table drops every three days. Each day you send the one work gang to one place: dig the well at home, or go out to one of six spokes (Gorge Road, Salt Pan, Nomad Camp, Date Groves, Old Aqueduct, Sand-Sea Ruins). Salt sells to nomads for water at a drifting rate, the road to the Green Cut needs four waystations, and the march out needs a cistern holding two Water per Hand. You may bank a day and spend it later for a double move. Dry-humored flavor: a surveyor who wants things noted, a nomad headman who is the market, and Assessor Nabil, the Emir's tax man.

**Rolls:** `SET=10 ROLE=13 LOOP=3 CLOCK=11 TWIST=13 WIN=2 MAP=4 TONE=2`

- SET 10 Walled desert city -> Qasr Ashab, the hub.
- ROLE 13 Colony governor -> the governor, deciding where the gang goes.
- LOOP 3 Allocate workers to jobs, see output -> one gang, one destination per turn, output scaled by Hands and a shown d6.
- CLOCK 11 Water table drops -> Well yield falls by 1 every 3 turns; lose at Water 0.
- TWIST 13 Bank one action -> hold the gang, spend the banked turn later for two jobs in one turn.
- WIN 2 Reach a location and get out -> complete the Gorge Road and march the whole city to the Green Cut.
- MAP 4 Star graph, hub and 6 spokes -> city plus six named spokes.
- TONE 2 Dry humor -> the surveyor, the headman, Assessor Nabil.
- Signature detail: Assessor Nabil, who takes the Emir's tenth of the cistern.

**Rulesheet (verbatim):**

```
1. Each turn, send the work gang to one place: dig the Well at home, or one of 6 spokes outside. Results are shown with their dice.
2. The city drinks Hands/3 Water per turn (rounded up). The Well adds its yield, and the yield drops by 1 every 3 turns as the table sinks.
3. Salt Pan: make Hands/3 salt, sold on the spot to the nomads at today's rate (Water per salt). The rate drifts daily; no nomads, no sale.
4. Gorge Road: pay 5 Water, roll d6: 3+ builds a waystation (Road +1); on a 1 you also lose a Hand. Nomad Camp sells a guaranteed waystation for 8 Water when they are home.
5. Well digging at home (4+: yield +1; 1: lose a Hand) and the Aqueduct (5+: yield +2) raise the Well for good. Groves and Ruins gamble for Hands or Water.
6. Bank: hold the gang instead of working. Spend the banked turn later to work two places in one turn. One bank at a time.
7. March: with Road 4/4 and Water at least 2 x Hands, say "march" and the whole city walks out to the Green Cut. That wins.
8. Lose if Water hits 0, or turn 18 ends with you still inside the walls.
```

## Playthrough

The player opened with the aqueduct gamble and hit it (roll 6), taking the Well from +4 to +6 and buying a long cushion. A caravan event pushed the salt rate to 3 the next turn, and the player sold for +12, swelling the cistern to 34; the caravan then left and took the nomads with it. With no buyers, the player built road for four turns straight (one miss, three hits), banking once at rate 1 and spending the bank on a dig-plus-build turn, finishing Road 4/4 on turn 8 with Water 11 against a march threshold of 24. The midgame was a salt grind at rate 1 (the rate never rose above 1 from turn 5 to turn 16) while the well cracked, dropped, and was partly re-dug (+1 on turn 10). A surveyor event cut the threshold to 21, and by turn 13 the player sat at 20, one short, when the nomads left again. A ruins roll missed, Assessor Nabil took 2 skins, and then on turn 15 three refugee families were admitted at the gate: Hands 15, threshold 27, Water 16, with the Well at +1 and no buyers. The player went all in on the ruins twice and rolled 6 then 6 (+10 each), reaching 28 at dawn on turn 18, and marched out through a sandstorm. Result: win on turn 18 of 18, final Water 28, Hands 15, Road 4/4, Well +1. Turns played: 18 (plus one `status` and one question that did not consume a turn).

## Rules fit

- Rulesheet: 8 lines, though lines 4 and 5 are dense (two mechanics each). Within the cap, but at the limit.
- Tracked numbers: 3 (Water, Hands, Road). The status line also shows Well yield, salt rate, nomad presence and bank state. These are world/clock information rather than player-managed resources, but the status line reads as six fields and a strict reading might call Well yield a fourth number.
- One decision per turn: held every turn. Spending the bank produced two actions in one turn, as the twist intends.
- Status line: same format every turn. Turn length: all under 180 words after a trim; the first two turns came out at 190 and 196 on the first pass and had to be cut, so the cap is tight when a turn carries both a resolution and a new price/event line.
- Dice shown every time in the `roll N (need X+) result` form.
- Nothing had to be invented mid-game. Two rulings were pinned in state.md before play and both came up: (1) no short-water march, Rule 7 is literal; (2) the Sandstorm card closes the spokes but does not block the march, because the march is not gang work. The second one would have been contentious if ruled live, since the sandstorm hit on the exact turn the player had to march. (3) The Surveyor's find card needed its "if Road is already 4/4" clause, which was written before play; without it the card would have been dead.
- Unclear to the player: the Aqueduct closing after success was not on the rulesheet; it only showed up as the option vanishing. Groves and Ruins odds were revealed in the option text, which worked.

## Decisions

Of 18 turns:

- Genuinely hard: 7 (T1 aqueduct vs salt; T2 sell vs build at rate 3; T6 bank vs road vs salt at rate 1; T7 how to spend the bank; T9 salt vs dig vs ruins after the road closed; T13 safe 20 vs ruins; T14 ruins vs bank with the buyers gone).
- Obvious or forced: 11 (T3, T4, T5 road with fat water and no buyers; T8 finish the road; T10 dig with nothing else open; T11, T12, T15 salt grind; T16, T17 ruins as the only line; T18 march).

The back third was the problem: once the refugees landed, the only move was the ruins, and the player knew it.

## Emergence

Moments where the systems produced something not scripted:

1. T1 to T2: aqueduct success followed immediately by the caravan event, so the best salt price of the game landed on the one turn the player had slack to take it, then the caravan pulled the nomads away and shut off salt for two turns right after selling.
2. T4: the nomads returned with the rate at 1 after two hidden down-drifts, so the "sell high" window closed for the rest of the game; rate 1 persisted from turn 5 through turn 16.
3. T5: the well crack landed the turn before the scheduled table drop, turning a +1 surplus into a -1 deficit in two days and prompting the bank.
4. T9 to T10: locusts closed the groves and the nomads left in the same night, leaving dig-or-gamble as the only options.
5. T11: the surveyor's cistern lowered the march threshold by 3 at exactly the point the player was counting turns to 24.
6. T13 to T14: sitting at 20 against 21, the nomads left; the ruins missed; the Assessor took the Emir's tenth. Three systems stacked against one missing point of water.
7. T15: refugees raised Hands to 15 and the threshold to 27 in one stroke, with the Well at +1 and the nomads gone. A systems-driven near-loss from a "good" event.
8. T16 to T17: two sixes on the ruins turned the near-loss into a win on the last turn, and the sandstorm card arrived on the last night.

Count: 8.

## Problems

- Salt rate stuck at 1 for 12 turns. The drift (1/3 up, 1/3 down, 1/3 hold, clamped 1 to 3) spends too long on the floor; with rate 1 the salt pan is a flat +4 and the "sell high" game disappears. A biased drift or a rate that reverts toward 2 would help.
- The back half collapsed into a grind: salt, salt, salt. Turns 11 to 15 were arithmetic, not decisions. The road finished at turn 8 and nothing new opened after that; the game needed a second-stage goal or a spoke that unlocks after Road 4/4.
- The refugees card is a near-unwinnable swing late. Raising the threshold by 6 while removing nothing else, with 3 turns left, left the player one option. It is thematically right for a governor, but it should either come with a choice (turn them away at a reputation or Hands cost) or raise salt output enough to pay for itself.
- The win came from a 1-in-36 double six. Honest, but the player would say the skill decisions were over by turn 10 and the result was luck. A loss would have felt unfair; a win felt lucky.
- Groves and Nomad Camp were never used. Groves (+2 Hands) is actively bad under the 2 x Hands march threshold; Nomad Camp at 8 Water was dominated by road rolls at 5 Water and 2/3 odds. Both spokes need repricing.
- The bank twist was used once, for a dig-plus-build turn. Useful, but with the rate pinned at 1 the "wait for a high price" use never materialized.
- Hands never decreased. No road 1s, no ruins 1s, no well 1s were rolled, so the Hand-loss risk never bit.

## Fun rating

**7 / 10.** The opening six turns were exactly the kind of planning I like: a permanent-upgrade gamble, a price spike to sell into, a build phase with visible odds, and a bank to time. The last eight turns were a salt treadmill followed by a refugee swing that left me rolling dice I did not choose to depend on, and the win owed more to two sixes than to anything I did after turn 10.

## Would replay

Yes, once more, with changes. The core (well decay versus road cost versus salt income, with a bank) is a sound little economy and 18 turns is the right length; I want to see a game where the rate actually moves and the road finishing opens something instead of closing the decision space. If the rate stays at 1 again and the back half is the same grind, no third play.