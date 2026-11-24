# The Grey Strand - session state

Rewritten every turn during play. This copy is the state at game end (win, turn 12 of 20).
Session: playtest 2026-10-14, game 02.

## Rolls

SET=23 Carrier strike group at sea | ROLE=5 Fleet admiral with 4 ships | LOOP=7 Hold a line against waves, repair between | CLOCK=7 Plague spreads one node per turn | TWIST=27 One resource is sentient and resists being used | WIN=8 Achieve a majority with three factions | MAP=1 Linear track of 10 stops | TONE=5 Mythic

Blend: the carrier group became a roc-ship and three escorts; the plague became the Grey Tide walking down a line of ten harbors; the sentient resource is the rocs (Trust); the three factions are the crown-holders of the Strand. Signature detail: Skarra, the eldest roc, who bargains through the ship's seer.

## Rulesheet

1. The Strand is ten harbors in a line. The Tide holds harbor 1; your fleet holds the line at the next harbor south. Every turn a wave breaks on your line.
2. Wave = d6 + half the turn number (rounded up). Line = 2 per ship afloat + 2 per roc you launch. If the wave beats the line, Hull loses the difference and the Tide takes your harbor. Hold by 6 or more and the harbor's faction gives +1 Favor.
3. Hull starts 12; every 3 lost sinks a ship. Repairing in harbor restores 3 Hull, but docked ships count 1 each in the line that turn.
4. Your 3 rocs are living and proud. Each roc launched costs 1 Trust; a turn with none launched gains 1 (max 6). At Trust 0 one roc leaves for good and Trust resets to 2. Fisher Clan tasks feed them.
5. Three factions own the harbors: Harbor Lords (2, 5, 8), Fisher Clans (3, 6, 9), Tidewardens (4, 7, 10). Favor runs 0 to 5; at 5 a faction pledges its crown.
6. Fall back one harbor: no wave this turn, Hull +3, Trust +2, but the Tide takes the harbor you left.
7. Each harbor offers one task when you reach it. Doing it is your action for the turn (ships hold alone, rocs rest) and pays Favor on a roll.
8. Win: two crowns pledged, and the Rite turns the Tide. Lose: the Tide reaches Lanthorn (harbor 10), Hull hits 0, or turn 20 ends without two crowns.

GM rulings made during play: a wave equal to the line holds (only a greater wave breaks it). A task resolves even if the line breaks that turn. The refugee escort pays only if the line holds. Ships afloat = ceil(Hull / 3).

## Tracked numbers (final)

- Hull 11/12 (4 ships: Thornhal the roc-ship, Gull, Tern, Oarhouse the tender)
- Trust 6/6 (3 rocs: Skarra, Hask, Little Wren)
- Favor: Lords 5 (pledged turn 4), Fisher 5 (pledged turn 12), Wardens 1

Turn: 12 of 20 (game over, win)

## Map

| # | Harbor | Faction | Status at end | Task (hidden until reached) |
|---|---|---|---|---|
| 1 | Northreach | - | Tide | none |
| 2 | Gullmere | Lords | Tide (fell turn 5, fallback) | Ferry the silver: ships alone, roll 3+: Lords +2; fail Hull -1. DONE (success) |
| 3 | Netcombe | Fisher | Tide (fell turn 8, fallback) | Tow the net-boats: ships alone, roll 4+: Fisher +2, Trust +2; fail Fisher +1, Trust +1. DONE (success) |
| 4 | Saltspire | Wardens | Tide (fell turn 9, fallback) | Fly the Warden's bell: Trust -1 no rest, ships alone, roll 3+: Wardens +2; fail nothing. SKIPPED |
| 5 | Coinwater | Lords | Tide (fell turn 10, fallback) | Guard the counting-house barges: ships alone, roll 4+: Lords +2; fail Hull -2, Lords +1. SKIPPED (Lords already pledged) |
| 6 | Hookhaven | Fisher | Tide (fell turn 12, breach) | The last great catch: ships alone, roll 5+: Fisher +2 else +1; Trust +2 either way. DONE (success) |
| 7 | Candlehold | Wardens | fleet's last position | Light the drowned beacons: Trust -1, roll 4+: Wardens +2; fail +1. Not reached |
| 8 | Lordsgate | Lords | free | Hold the sea-gate: Hull -2, no roll, Lords +2. Not reached |
| 9 | Lastnet | Fisher | free | Sing the drowning song: roll 4+: Fisher +2 else +1; Trust +2 either way. Not reached |
| 10 | Lanthorn | Wardens | free | none; Tide reaching here is the loss |

## Hidden systems

Sea event: each turn roll d6 at the start; on 5-6 roll d6 again:
1 Surge (wave +3) | 2 Skarra's demand (launching costs 1 extra Trust) | 3 Hulk (Hull +1 if the line holds) | 4 Refugee boats (extra option: ships hold alone, +1 Favor with this harbor's faction if the line holds) | 5 Calm (wave -2) | 6 Undertow (if the line breaks, the Tide takes two harbors)

Dice were pre-rolled as a stream of 120 d6 and consumed strictly in order (event die, wave die, task die). Consumed: 25.

## Log

- T1 Gullmere. Event: Undertow (harmless, wave could not reach 8). Task ferry silver: wave 4 vs 8 held; task roll 5 success. Lords 3. Trust 5.
- T2 Launch one roc. Wave 7 vs 10 held by 3, no Favor. Trust 4.
- T3 Event: refugee boats. Escort, ships alone: wave 8 vs 8 held on the tie. Lords 4. Trust 5.
- T4 Launch all. Wave 7 vs 14 held by 7. Lords 5, crown pledged. Trust 2.
- T5 Fall back to Netcombe. Tide 2. Trust 4.
- T6 Task tow net-boats: wave 6 vs 8 held; roll 4 success. Fisher 3. Trust 6 (cap).
- T7 Launch all. Wave 9 vs 14 held by 5, one short of Favor. Trust 3.
- T8 Fall back to Saltspire. Tide 3. Trust 5.
- T9 (status asked) Fall back to Coinwater. Tide 4. Trust 6.
- T10 Fall back to Hookhaven. Tide 5. Trust 6.
- T11 Launch all. Wave 10 vs 14 held by 4, no Favor. Trust 3.
- T12 Task great catch: wave 9 vs 8 breaks by 1, Hull 11, Tide takes Hookhaven (Tide 6). Task roll 5 success, Fisher 5, crown pledged. WIN.
