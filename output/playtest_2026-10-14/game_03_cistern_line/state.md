# Cistern Line - session state

Status: ENDED (WIN, turn 18 of 20). This file was rewritten every turn during play; this is the final version.

## Rolls
SET=1 (asteroid belt mining outposts) ROLE=33 (water engineer) LOOP=9 (choose a contract, pay a cost, roll the outcome) CLOCK=1 (fuel runs out) TWIST=14 (each location visited once) WIN=8 (majority of three factions) MAP=1 (linear track of 10 stops) TONE=6 (military procedural)

Signature detail: the cracker (3 water -> 3 fuel, no roll) plus Union/Syndicate haulers that pay in the other resource, so water and fuel are one pool with a conversion cost.

## Rulesheet
1. Cistern runs outbound along a 10-stop line. The line is one-way: a stop left behind can never be reached again.
2. Each turn: take one contract at your stop, crack water, or jump ahead. Jump costs 2 fuel, +1 per stop skipped. Every docked turn costs 1 fuel.
3. Contracts show a cost (paid up front, win or lose) and a target. Roll d10; meet the target to succeed. A failed contract closes and may cost more.
4. Success raises Standing with that faction; some contracts lower another's. Standing runs -3 to +5.
5. Factions: Miners' Union (U), Hauler Syndicate (H), Vesta Concession (C). At +2 or better, add 1 to your rolls for that faction. At -2 or worse, that faction's contracts close to you.
6. Crack water: 3 water becomes 3 fuel, no roll.
7. Fuel 0 anywhere but Terminus means adrift: game over.
8. Each jump draws one transit event on the way. Some cost fuel or water, some pay.

Goal: dock at Stop 10 Terminus with Standing +3 or better with two factions. Lose: fuel 0, or turn 20 ends before docking. Turns: 20.

## Tracked numbers (final)
Fuel 1 | Water 2 | Standing U +5, H +4, C -1

Turn counter: 18 of 20 (game ended on docking)

## Map (linear, one-way)
1 Ceres Low (Authority) - visited, left T3
2 Pallas Drift (Union) - visited, left T6
3 Hygiea Yard (Syndicate) - visited, left T9
4 Vesta Pit 4 (Concession) - skipped
5 Thule Rock (contested U/C) - visited, left T12
6 Juno Relay (Syndicate) - visited, left T14
7 Davida Cold Store (Union) - visited, left T17
8 Psyche Smelter (Concession) - skipped
9 Interamnia Slip (Syndicate) - visited, left T18
10 Terminus (Authority) - docked T18

## Hidden facts (as designed before turn 1)

Contract board per stop (cost / target / success / fail):
- 1-A [U] flush cistern: 2 water / 5+ / U+1 / -1 water more
- 1-B [C] certify survey tanks: 1 fuel / 4+ / C+1, +2 water / nothing more
- 1-C [H] top off tug Marigold: 3 water / no roll / H+1, U-1
- 2-A [U] recommission melt plant: 2 fuel / 6+ / U+2, +3 water / -1 water
- 2-B [U] ration audit: 1 water / 4+ / U+1 / U-1
- 2-C [C] serve lien on well: 0 / 5+ / C+2, U-2 / U-1
- 3-A [H] refit scrubbers: 2 water / 5+ / H+1, +3 fuel / nothing more
- 3-B [H] water run to Dunlin: 3 water 1 fuel / 4+ / H+2, +2 fuel / -1 fuel
- 3-C [U] quiet lift to dockers: 2 water / no roll / U+1, H-1
- 4-A [C] brine separation: 1 fuel / 5+ / C+1, +4 water / -2 water
- 4-B [C] reservoir pressure test: 2 water / 7+ / C+2, +2 fuel / C-1
- 4-C [H] smuggle untaxed water: 0 / 6+ / H+2, C-1 / C-2
- 5-A [U] certify claim for Union: 1 water / 5+ / U+2, C-1 / C-1
- 5-B [C] certify claim for Concession: 1 water / 5+ / C+2, U-1 / U-1 (withdrawn once 5-A or 5-B resolves)
- 5-C [H] sell 4 water to stockpile: 4 water / no roll / H+1, +3 fuel
- 6-A [H] barter: 3 water / no roll / +4 fuel, H+1
- 6-B [H] repair coolant loop: 1 water 1 fuel / 6+ / H+2 / -1 fuel
- 6-C [C] relay data audit: 1 fuel / 4+ / C+1, H-1
- 7-A [U] thaw intake: 2 fuel / 5+ / U+2, +5 water / -1 fuel
- 7-B [U] free load: only if U >= +3; 0 / no roll / +4 water
- 7-C [H] broker ice: 0 / 5+ / H+1, U-1
- 8-A [C] smelter cooling supply: 4 water / no roll / C+2, +2 fuel
- 8-B [C] coolant leak: 1 water / 7+ / C+2, +3 fuel / C-1, -1 fuel
- 8-C [U] water to strikers' hab: 2 water / 5+ / U+2, C-2 / U+1, C-2
- 9-A [H] clean manifest: 2 water / 4+ / H+1, +2 fuel
- 9-B [H] tow-assist barge: 2 fuel / 6+ / H+2 / -1 fuel
- 9-C [U] carry stranded crew: 3 water / no roll / U+1

Transit event deck (d6 per jump): 1-2 clean; 3 micropuncture -1 water; 4 debris dodge -1 fuel (past Thule: Rock Hound toll, 2 water or else 2 fuel); 5 Syndicate hauler with dry tanks hails, answer next turn with 2 water (or equivalent) for H+1, ignore for H-1; 6 favorable alignment +1 fuel.

Faction thresholds: +2 gives +1 on rolls (in rulesheet); +3 Union unlocks 7-B; -2 closes that faction's board.

## Log
T1 1-B roll 3 fail. T2 1-A roll 2 fail. T3 jump Pallas, event 6 (+1 fuel). T4 2-A roll 7 success U2. T5 2-B roll 3+1 success U3, Davida load unlocked. T6 jump Hygiea, event 6. T7 3-B roll 8 success H2. T8 3-A roll 1+1 fail. (status) T9 jump Thule skipping Vesta, event 5 Kestrel hail. T10 pump Kestrel H3. T11 5-A roll 6+1 success U5 C-1. T12 jump Juno, event 5 Tern hail. T13 pump Tern 2 fuel H4. T14 jump Davida, event 4 toll -2 fuel. T15 Union load +4 water. T16 crack. T17 jump Interamnia skipping Psyche, event 6. T18 jump Terminus, event 1. WIN.
