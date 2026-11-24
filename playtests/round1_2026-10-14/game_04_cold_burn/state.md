# Cold Burn - session state

Playtest game 04, 2026-10-14. Final state after the game ended (file was rewritten every turn during play; this is the last version).

## Rolls
SET=27 (Trench front, static war) ROLE=5 (Fleet admiral with 4 ships) LOOP=13 (Ration a shrinking supply across needs) CLOCK=18 (Each turn costs a fixed upkeep) TWIST=11 (Damage is permanent; nothing repairs) WIN=7 (Deliver a cargo intact) MAP=2 (Hex ring of 8 around a center) TONE=4 (Hard sci-fi)

Hidden layout roll: `printf "G\nG\nG\nM\nD\nK\nC\n" | shuf` over sectors 2..8 gave `D C M G G G K`.
Pre-rolled d6 stream (consumed in order): 2 2 1 3 2 5 6 4 4 1 5 1 4 2 3 2 4 6 4 2 ...

## Rulesheet
1. Four ships on a ring of 8 orbital sectors around Hollow, the base at the center. You start in sector 1. A sector's contents are unknown until a ship enters it; Pike also sees both neighboring sectors.
2. One shared tank of reaction mass (RM). Upkeep of 1 RM per surviving ship is paid at the start of every turn. RM 0 means the fleet deorbits and you lose. Scuttle a ship any time to end its upkeep.
3. Each ship does one thing per turn. Move one sector costs 2 RM (Vesper 1). Evade costs 1 RM and makes guns need 6+ on that ship this turn. Hold costs nothing.
4. Each enemy gun fires once per turn at the largest ship in its own or a neighboring sector (Castellan > Vesper > Mule > Pike): roll 4+ hits for 2 hull. A gun that fires is revealed.
5. A ship that holds may shoot one revealed gun in its own or a neighboring sector: Castellan hits 4+, Vesper 5+, Pike 6+. A hit kills that gun.
6. Descent: from sector 5 only, 6 RM, takes 3 turns. During descent Mule cannot evade or abort, and guns in sectors 4, 5, 6 fire at Mule first, each turn.
7. Nothing repairs, on either side. A ship at 0 hull is gone. Mule carries the core; Mule gone, core gone.
8. Win: Mule lands (third descent turn done). Lose: Mule destroyed, RM 0, or turn 16 ends.

## Tracked numbers
- RM (reaction mass): start 80. Final 7.
- Hull list: Castellan 10, Vesper 6, Mule 4, Pike 3 at start. Final: Castellan 6, Vesper 6, Mule 4 (landed), Pike scuttled turn 8.

Signature detail: perigee pass on turn 9, upkeep doubles to 2 RM per ship from then on.

## Turn counter
Game over: WIN on turn 11 of 16.

## Map (ring of 8, Hollow at center under sector 5)
| Sector | Content | Revealed |
|---|---|---|
| 1 | Anchorage (start, safe) | start |
| 2 | Debris field (guns need 6+ on ships here) | T1 |
| 3 | Clear | T1 (Pike sight) |
| 4 | Minefield (entering ship rolls 4+ = 2 hull) | T2 (Pike sight) |
| 5 | Gun emplacement, KILLED T5 | T3 |
| 6 | Gun emplacement, KILLED T7 | T6 (Pike sight) |
| 7 | Gun emplacement, LIVE | T1 (fired at Vesper) |
| 8 | Derelict tanker Yoke, 12 RM, DRAINED T1 | T1 |

Ship positions at end: Castellan 5, Vesper 3, Mule landed at Hollow.

## Hidden facts (all now revealed)
Gun 7 was never engaged. No other hidden content.

## Log
- T1: Pike to 2 (debris), Vesper to 8 (Yoke, +12 RM). Gun 7 fires at Vesper, roll 2, miss. RM 85.
- T2: Pike to 3 (clear, sees mines in 4). Castellan and Mule to 2. Vesper back to 1. Quiet.
- T3: Castellan to 3. Pike into 4, mine roll 2 clean, sees gun in 5. Gun 5 fires at Pike, roll 1, miss.
- T4: Castellan into 4, mine roll 3 clean. Pike shoots gun 5, roll 2 miss. Gun 5 hits Castellan (roll 5), C 10 to 8.
- T5: Castellan shoots gun 5, roll 6, KILL. Mule to 3, Vesper to 2.
- T6: Castellan and Pike to 5. Pike sees gun in 6. Gun 6 hits Castellan (roll 4), C 8 to 6.
- T7: Castellan shoots gun 6, roll 4, KILL. Mule into 4, mine roll 1 clean. Vesper to 3.
- T8: Player checked status. Mule to 5. Pike scuttled.
- T9: Perigee, upkeep 6. Descent begins (6 RM). RM 19.
- T10: Descent 2 of 3. RM 13.
- T11: Descent 3 of 3. Mule lands. WIN. RM 7.
