# Mirror Migration

Premise: a nature documentary on a chessboard. You are a smuggler pawn who owes the Bishop a season of tithe, and the only way to clear the debt is to raise a den on every one of five files before the Great Crossing, with a party of wild pieces that always crosses the file opposite whatever you last built.

## Rolls
FORM=3 (tactical skirmish) SET=57 (a chessboard where the pieces have an economy) ROLE=3 (smuggler with a debt) LOOP=35 (place one trap or creature; a party comes through) CLOCK=22 (a season of fixed length) TWIST=6 (the rival mirrors your move) WIN=5 (build a specific final structure) MAP=10 (no map; a deck of encounters) TONE=10 (nature documentary) CURRENCY=12 (Standing)

Novelty check: no reroll needed. Verbs check: 0 percent overlap (den, snare, run, writ).
Brief asked for: tracked_count not 3 (this game: 2), rival not hunter (counter), clock not decay (deadline plus escalation), decision unit not route/pick-action (place, with params).

## Rulesheet (python engine.py rules)
1. 5 files, lettered from a, face the road. Each week do one thing: raise a den on an empty file (3 Standing), lay one snare on a den's file (1), or run contraband.
2. A run rolls a d6 for 4+ (3+ with 3 or more dens) and pays +5 Standing; a miss pays +1. You start with 10 Standing.
3. Each week a party crosses the file opposite your latest build (a with e, b with d, c with c). If you run, it repeats last week's file; before week 1 that file is random.
4. This week's party and next week's are shown with a strength, drawn from a deck. Pilgrims are harmless and pay +3 Standing if the file they cross holds a den.
5. A den on the crossed file holds on a d6 roll of 4 plus strength minus defense, from 2+ to 6+. Defense: 2, +1 per neighbouring den, +3 for a snare. A hold pays +1.
6. A snare is used up when its den rolls to hold. A party that crosses an empty file, or breaks a den, costs 1 Standing, and a broken den is gone.
7. At dusk each den pays +1 Standing and the Bishop takes 1. Below 0 Standing he forecloses and you lose. From week 9 the tithe is 2 and every party but Pilgrims gains +1 strength.
8. Once from week 9, a 12-Standing Writ turns that week's party back. Week 16 is the Great Crossing (strength 5); after its dusk, win with a den on every file and 18 Standing.

Goal: a den on all 5 files and 18 Standing after the Great Crossing's dusk.   Lose if: Standing below 0, or a gap or a short purse at the end.   Turns: 16

## Signature detail
The mirror road: the party crosses the file opposite your latest build (a with e, b with d, c with c), so every build exposes a different file than the one you touched. One Pilgrims card per season is harmless and pays dens: steer it onto a den by building opposite it (the deck shows two weeks ahead). Strength 0, never springs a snare.

## Midpoint plan
Week 9: tithe rises 1 to 2, every party but Pilgrims gains +1 strength, and the Writ goes on sale (12 Standing, once, turns a week's party back; also the late lever that buys certainty at the Great Crossing).

## Rival policy (one line)
The party (counter type, mirrors your move) crosses the file opposite your latest build, or repeats last week's file if you run or buy the Writ; its strength comes from a shuffled deck (two cards shown ahead, the rest unseen), tell shown before you act; the Great Crossing (strength 5) is week 16.

## Shape choices
tracked numbers: 2 (Standing, the Files board). ending shape: final-roll (the last build picks the file that takes the Crossing; snares and neighbours buy the odds, or pay for the Writ). hidden facts: the unseen deck order only (resample_hidden reshuffles it).
