# Dry Reckoning - session state (setup, before Turn 1)

Playtest game 08, 2026-10-14. Session folder overrides the normal GM\sessions path.

## Rolls
SET=10 Walled desert city | ROLE=13 Colony governor | LOOP=3 Allocate workers to jobs, see output | CLOCK=11 Water table drops | TWIST=13 You may bank one action to spend later | WIN=2 Reach a location and get out | MAP=4 Star graph: hub and 6 spokes | TONE=2 Dry humor

## Composition
Governor of Qasr Ashab, a walled desert city on a failing well. Each turn the one decision is where the work gang goes (loop 3). The well yield drops 1 every 3 turns (clock 11). You may bank a turn and spend it later for a double action (twist 13). Win by completing the Gorge Road and marching the whole city out to the Green Cut (win 2). Map: hub (city, with the Well) and 6 spokes.

Signature detail: Assessor Nabil, the Emir's tax man, who turns up with a ledger and takes a tenth of the city's water.

## Rulesheet
1. Each turn, send the work gang to one place: dig the Well at home, or one of 6 spokes outside. Results are shown with their dice.
2. The city drinks Hands/3 Water per turn (rounded up). The Well adds its yield, and the yield drops by 1 every 3 turns as the table sinks.
3. Salt Pan: make Hands/3 salt, sold on the spot to the nomads at today's rate (Water per salt). The rate drifts daily; no nomads, no sale.
4. Gorge Road: pay 5 Water, roll d6: 3+ builds a waystation (Road +1); on a 1 you also lose a Hand. Nomad Camp sells a guaranteed waystation for 8 Water when they are home.
5. Well digging at home (4+: yield +1; 1: lose a Hand) and the Aqueduct (5+: yield +2) raise the Well for good. Groves and Ruins gamble for Hands or Water.
6. Bank: hold the gang instead of working. Spend the banked turn later to work two places in one turn. One bank at a time.
7. March: with Road 4/4 and Water at least 2 x Hands, say "march" and the whole city walks out to the Green Cut. That wins.
8. Lose if Water hits 0, or turn 18 ends with you still inside the walls.

## Tracked numbers
Water 20 | Hands 12 | Road 0/4
(Status also shows Well yield, salt rate and nomad presence, and bank state: world info, not player resources.)

Turn budget: 18. Turn counter: 1.

## Map (star: hub + 6 spokes)
Hub: Qasr Ashab (the Well; dig here).
1. Gorge Road (north) - waystations toward the Green Cut.
2. Salt Pan (east) - salt sold to nomads.
3. Nomad Camp (east, past the pan) - guaranteed waystation for 8 Water when home.
4. Date Groves (south) - d6 4+: +2 Hands (grove families join), else +1 Water.
5. Old Aqueduct (west) - d6 5+: Well +2 permanent. Closed once it flows.
6. Sand-Sea Ruins (northwest) - d6: 6 = +10 Water (sealed cistern), 4-5 = +4 Water, 2-3 = nothing, 1 = lose a Hand.

## Hidden facts (player has not seen)
- Well yield: single number, starts 4, drops by 1 at the start of turns 4, 7, 10, 13, 16 (floor 0). Boosts and cracks adjust the same number.
- Drink = ceil(Hands/3), applied after the action each turn. Order each turn: action rolls, then Well yield added and drink subtracted, then hidden systems.
- Nomad presence: each turn roll d6, 3+ = home next turn (unless an event overrides). Initial presence roll: die #1.
- Salt rate: starts 2; each turn d6: 1-2 down 1, 3-4 hold, 5-6 up 1, clamped 1..3. Rate keeps drifting while nomads are away.
- Event die each turn: 5-6 draws the next event card.
- Event deck (shuffled order 3 8 5 7 6 4 2 1):
  3 Caravan week: nomads home next turn and rate pegged at 3 for it.
  8 Nomads gone: nomads away for the next 2 turns (no salt sale, no camp).
  5 Well crack: Well yield -1 now.
  7 Locusts: Date Groves closed for 3 turns.
  6 Surveyor's find: a sealed cistern on the Gorge Road. Next Road build returns +3 Water; if the Road is already 4/4, the march needs 3 less Water.
  4 Assessor Nabil: takes a tenth of current Water (rounded up).
  2 Refugees from Bani Tal: admitted at the gate under the Emir's law: Hands +3, Water -2.
  1 Sandstorm: next turn all 6 spokes are closed; the gang may only dig the Well or bank. (Rules the march by its text: the march is not gang work, so it is not blocked.)
- Ruling fixed before play: no short-water march. Rule 7 is literal.
- d6 stream (consumed in order, pointer starts at 1):
  4 6 3 6 5 6 5 5 2 3 1 2 6 4 1 2 4 3 4 5 5 2 3 2 5 3 3 2 4 6 4 4 1 3 6 5 4 3 2 3 3 6 4 1 4 1 4 1 2 5 4 5 2 2 6 6 2 5 3 6 6 6 6 6 1 6 4 4 3 2 3 5 5 5 1 6 1 3 1 1 3 5 3 1 6 2 4 3 3 5 6 1 4 5 3 1 2 1 5 1 3 3 3 1 1 3 5 5 3 1 5 5 2 2 2 1 4 6 6 3 3 5 2 1 6 5 4 1 5 4 6 6 4 1 5 4 2 4 5 1

## Log
- Setup. Initial presence die #1 = 4: nomads home for Turn 1. Pointer at 2.

---

# Final state (after Turn 18)

Water 28 | Hands 15 | Road 4/4 | Well +1 | Salt rate 3 (nomads home) | Bank: none
Turn counter: 18 of 18. RESULT: WIN (marched turn 18). March threshold at the end: 27 (2 x 15 - 3 surveyor).
Aqueduct: repaired turn 1 (closed). Groves: locusts turns 10-12. Event deck fully drawn (8 of 8). Dice pointer ended at 64.

## Turn log
- T1 aqueduct: roll 6 success, Well 4->6 from T2. W 20. Hidden: home / rate up 3 / event: Caravan week.
- T2 salt 4x3=+12. W 34. Hidden: home / rate up (clamp 3) / event: Nomads gone 2 turns (T3-T4).
- T3 road: roll 2 fail. W 31. Hidden: - / rate down 2 / none. Well drops to 5 at T4.
- T4 road: roll 6 success, Road 1. W 27. Hidden: home T5 / rate down 1 / none.
- T5 road: roll 4 success, Road 2. W 23. Hidden: home / hold 1 / event: Well crack, Well 5->4.
- T6 bank. W 23. Hidden: home / down (clamp 1) / none. Well drops to 3 at T7.
- T7 spend bank: dig roll 2 fail; road roll 5 success, Road 3. W 17. Hidden: home / hold / none.
- T8 status (no turn). Road: roll 4 success, Road 4/4. W 11. Hidden: home / hold / none.
- T9 question (no turn). Salt +4. W 14. Hidden: away T10 / hold / event: Locusts (groves closed T10-T12). Well drops to 2 at T10.
- T10 dig: roll 5 success, Well 2->3 from T11. W 12. Hidden: home / hold / none.
- T11 salt +4. W 15. Hidden: home / hold / event: Surveyor's find, march needs -3 (21).
- T12 salt +4. W 18. Hidden: home / down (clamp 1) / none. Well drops to 2 at T13.
- T13 salt +4. W 20. Hidden: away T14 / hold / none.
- T14 ruins: roll 2 nothing. W 18. Hidden: home / hold / event: Assessor takes 2. W 16.
- T15 salt +4. W 18. Hidden: away T16 / down (clamp 1) / event: Refugees, Hands 15, W 16, threshold 27. Well drops to 1 at T16.
- T16 ruins: roll 6, +10. W 22. Hidden: away T17 / up 2 / none.
- T17 ruins: roll 6, +10. W 28. Hidden: home / up 3 / event: Sandstorm (spokes closed T18).
- T18 march. WIN.
