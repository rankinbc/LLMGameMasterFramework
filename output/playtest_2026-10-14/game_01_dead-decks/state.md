# Dead Decks - session state (final)

Playtest game 01, 2026-10-14. Written to the playtest output folder instead of GM\sessions per playtest override.

## Rolls

SET=4 (Derelict generation ship) ROLE=28 (Hero with a grudge and a small army) LOOP=1 (Buy low, sell high across moving prices) CLOCK=18 (Each turn costs a fixed upkeep) TWIST=7 (Night turns double all risk and all reward) WIN=2 (Reach a location and get out) MAP=7 (Three islands and the sea between) TONE=6 (Military procedural)

Signature detail: Quartermaster Dessa Vosk, the mutineer who holds the lifeboat bay; her Core price rises 20 every Dark cycle.

## Rulesheet

1. Three hulls: Fore (farms), Mid (armory), Aft (engineering, Vosk's lifeboat bay). Crossing between any two takes a turn through the dead decks.
2. One action per turn: Trade (sell any cargo here, then buy one good), Cross, Scavenge, Recruit (Mid only, 1 trooper for 30 chits), or Launch (Aft only).
3. Each trooper carries 1 crate and eats 3 chits at end of turn. Short on chits: 1 trooper deserts per 3 chits short.
4. Goods: Ammo, Air, Seed, Med. Each hull has its own prices, shown only while you are there; they drift every turn.
5. Cross: roll d6, ambush on 1-2. Fight: d6 + troopers/4 (round down), need 5+. Win: loot d6 x 10 chits. Lose: d3 troopers die with their crates.
6. Scavenge: roll d6. On 1 a trooper dies; otherwise gain that many crates of a random good (needs free hands).
7. Dark cycle on turns 3, 6, 9, 12, 15, 18: ambush on 1-4, scavenge kills on 1-2, and loot, scavenge yields, and price drifts all double.
8. Launch (Aft): buy the Core at the listed price (rises 20 each Dark cycle), then roll d6 + troopers/3 (round down), need 7+. Fail: lose d3 troopers, keep the Core.

Goal: Launch the lifeboat from Aft. Lose if: troopers hit 0 or turn 20 ends. Turns: 20.

## Tracked numbers (final, after turn 11)

- Chits: 542
- Troopers: 15
- Cargo: 13/15 (13 Air)
- Location: Aft. Core: 300 (paid). Turn: 11 of 20. Result: WIN.

## Map

Triangle: Fore, Mid, Aft. Any hull reaches any other in one crossing.

## Hidden facts

Base prices (buy and sell at the same price):

| Hull | Ammo | Air | Seed | Med |
|------|------|-----|------|-----|
| Fore | 30 | 24 | 8 | 20 |
| Mid | 12 | 28 | 18 | 14 |
| Aft | 26 | 10 | 24 | 32 |

Prices at end of turn 10:

| Hull | Ammo | Air | Seed | Med |
|------|------|-----|------|-----|
| Fore | 22 | 23 | 7 | 18 |
| Mid | 15 | 36 | 8 | 12 |
| Aft | 27 | 11 | 33 | 28 |

Drift: each turn, each hull shifts one good (d4: 1 Ammo, 2 Air, 3 Seed, 4 Med) by a signed d4; doubled on Dark turns; floor 4. Pre-rolled drift table used:
T1 F4-3 M2+4 A2-2 | T2 F3+1 M4-1 A3+1 | T3 F1+1 M3-3 A1+1 | T4 F2-4 M2+2 A1-1 | T5 F3-2 M4+2 A2+3 | T6 F1-2 M2+1 A3+4 | T7 F1+2 M1+3 A4-4 | T8 F4+1 M4-3 A4+1 | T9 F1-4 M3-1 A4+1 | T10 F2+3 M3-2 A4-3

Event check: d6 each turn, event on 6. Event deck (d6): 1 Hull breach (Air +12 at current hull), 2 Deserters (2 troopers for 20 each, this turn only), 3 Vosk patrol (next crossing ambush range +1), 4 Glut (most-held good -6 everywhere), 5 Vosk raid (Core +30), 6 Lights fail (next turn Dark). Pre-rolled triggers T1-T11: 1 2 3 4 1 3 2 2 5 6 5. Event fired end of T10: card 2 (Deserters).

Core price: 240, +20 at each Dark cycle (260 at T3, 280 at T6, 300 at T9).

Dice streams (consumed in order): d6: 1 6 2 1 2 6 2 6 6 3 2 1 5.

## Log

- T1 Fore: bought 12 Seed at 8 (96). Chits 68.
- T2 Cross Fore->Aft: roll 1 ambush, fight 6+3=9 win, loot 2 = 20. Chits 52.
- T3 Aft (Dark, Core 260): sold 12 Seed at 25 (300), bought 12 Air at 8 (96). Chits 220.
- T4 Cross Aft->Mid: roll 1 ambush, fight 2+3=5 win, loot 6 = 60. Chits 244. Player declined the quick-launch gamble.
- T5 Mid: sold 12 Air at 34 (408), bought 12 Ammo at 12 (144). Chits 472.
- T6 Mid (Dark, Core 280): player asked for 3 recruits; one per turn. Recruited 1 (30). Troopers 13. Chits 403.
- T7 Cross Mid->Fore: roll 2 ambush, fight 6+3=9 win, loot 6 = 60. Chits 424.
- T8 Fore: sold 12 Ammo at 30 (360), bought 13 Seed at 7 (91). Chits 654.
- T9 Fore (Dark, Core 300): status requested. Cross Fore->Aft: roll 3 ambush, fight 2+3=5 win, loot 1 x2 = 20. Chits 635.
- T10 Aft: sold 13 Seed at 33 (429), bought 13 Air at 11 (143) as a hedge. Chits 882. Event: deserters.
- T11 Aft: hired 2 deserters (40), troopers 15. Bought Core (300). Launch roll 5+5=10, need 7+. WIN. Chits 542.
