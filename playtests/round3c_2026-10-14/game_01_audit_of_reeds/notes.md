# Audit of Reeds

Premise: The Bureau of Sleep is auditing a dreamer's river delta, and you, its siege engineer, must chart all seven reaches before the Ferryman's barge carries the dream's last secret out to sea and wakes the dreamer.

## Rolls

FORM=10 (Heist) SET=58 (A dream that is being audited) ROLE=14 (Siege engineer) LOOP=11 (Train one thing, deploy it) CLOCK=16 (The target is getting away) TWIST=2 (One faction is secretly on your side) WIN=11 (Map the whole board) MAP=6 (Branching river delta) TONE=5 (Mythic) CURRENCY=11 (Evidence, called Soundings) TRACKED=3 (Soundings, Drill, Charted board)

## Rulesheet (python engine.py rules)

1. Chart all 7 reaches within 18 turns or the dream wakes. Reach 1 is the Source; forks 2 (East) and 3 (West) carry mouths 4 and 5, and 6 and 7. A fork and its mouths form a branch.
2. Sound any reach to learn its guard (a base of 4 to 7) and gain Soundings +2 (only +1 from turn 10), or +1 if you know the guard already. You start with Soundings 4 and Drill 0.
3. Train the sappers for 2 soundings: Drill rises one level, up to Drill 3. Each reach you chart, by any means, pays Soundings +1.
4. Deploy the sappers at an uncharted reach, pushing up to 3 soundings. Roll d6 plus Drill plus push: meeting its guard charts it. Win or lose, the push is spent and the guard learned; a failure costs 1 Drill.
5. The Ferryman's barge starts at reach 1. At dusk every 6 turns it drops to the less charted branch, then the less charted mouth under its fork (ties go low). An uncharted reach it holds has guard +3.
6. Three houses hold the reaches: Heron, Eel and Moth. One is secretly your friend: its reaches have guard -1 and pay +1 when sounded. You learn which when you act at its reaches, or rule out the other two.
7. From turn 10 the dream stirs: guards +1. Once, breach a branch with 2 or more uncharted reaches for 2 soundings: one pushed roll against their highest guard, all shown, charts them all (failure costs Drill and the breach).
8. From turn 13, once, spend 5 soundings on the Bureau's writ to chart any one reach with no roll.

Goal: chart all 7 reaches.   Lose if: turn 18 ends with a reach uncharted (the barge slips out to sea and the dream wakes).   Turns: 18

## Signature detail

The secret friendly house: one of Heron, Eel and Moth wants the audit to pass, and its keepers slip you a note (an extra sounding and a weaker guard) the first time you act on one of its reaches. The other houses give you nothing, and ruling out two houses names the third.

## Midpoint plan

Plan phase (turns 1 to 9): sound reaches for soundings and guards, train the sappers, take the easy reaches. Turn 10 the dream stirs: every guard +1, a first sounding pays less, and the once-only breach of a branch unlocks (one roll charts a fork and its mouths). Turn 13 the Bureau's writ arrives: the late lever, 5 soundings for one sure chart, meant for the warded mouth the barge settles on after turn 12.

## Rival policy

The Ferryman's barge starts at reach 1 and drops one reach at dusk after turns 6 and 12, into the branch (then the mouth) you have charted less (lower number on a tie); an uncharted reach it holds has guard +3, and its next drop is announced every dusk (tell shown after it lands, schedule shown every turn).

## Notes for the reviewer

Hidden: every reach's base guard (4 to 7) and which house is the friend. Which house holds three reaches is drawn per seed. Args are 1-based reach numbers (fork 2 is the East fork, fork 3 the West fork), as in the labels. Known after contact: a reach's guard (sound, deploy, breach, writ), the friend (first act on its reaches, or by elimination). Ending shape: cliff (the dream wakes at the end of turn 18). Opening shape: scout. Rival tell: after (plus a standing drop schedule).
