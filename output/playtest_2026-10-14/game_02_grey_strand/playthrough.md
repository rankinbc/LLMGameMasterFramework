# The Grey Strand - playthrough transcript

Playtest 2026-10-14, game 02. GM and player both played by the agent; the player is a separate persona (systems-heavy strategy and trading gamer, plays to win, takes calculated risks).

## Rolls

Command (run with Bash exactly as written in the skill):

    echo "SET=$((RANDOM%40+1)) ROLE=$((RANDOM%40+1)) LOOP=$((RANDOM%24+1)) CLOCK=$((RANDOM%18+1)) TWIST=$((RANDOM%36+1)) WIN=$((RANDOM%14+1)) MAP=$((RANDOM%10+1)) TONE=$((RANDOM%8+1))"

Output: SET=23 ROLE=5 LOOP=7 CLOCK=7 TWIST=27 WIN=8 MAP=1 TONE=5

- SET 23: Carrier strike group at sea
- ROLE 5: Fleet admiral with 4 ships
- LOOP 7: Hold a line against waves, repair between
- CLOCK 7: Plague spreads one node per turn
- TWIST 27: One resource is sentient and resists being used
- WIN 8: Achieve a majority with three factions
- MAP 1: Linear track of 10 stops
- TONE 5: Mythic

Novelty check skipped (no played_log entries). Game dice: a stream of 120 d6 was pre-rolled with Bash and consumed strictly in order (per turn: event die, then wave die, then task die if any). Stream start: 5 6 3 5 4 6 6 4 6 4 5 3 2 3 4 3 5 4 4 1 2 4 1 3 5 (25 consumed).

## Present

```
THE GREY STRAND
You are admiral of the Strand's last four ships and three proud rocs, holding ten harbors in a line against the Grey Tide until two of the three crowns pledge to you and the Rite can be sung.

Rules
1. The Strand is ten harbors in a line. The Tide holds harbor 1; your fleet holds the line at the next harbor south. Every turn a wave breaks on your line.
2. Wave = d6 + half the turn number (rounded up). Line = 2 per ship afloat + 2 per roc you launch. If the wave beats the line, Hull loses the difference and the Tide takes your harbor. Hold by 6 or more and the harbor's faction gives +1 Favor.
3. Hull starts 12; every 3 lost sinks a ship. Repairing in harbor restores 3 Hull, but docked ships count 1 each in the line that turn.
4. Your 3 rocs are living and proud. Each roc launched costs 1 Trust; a turn with none launched gains 1 (max 6). At Trust 0 one roc leaves for good and Trust resets to 2. Fisher Clan tasks feed them.
5. Three factions own the harbors: Harbor Lords (2, 5, 8), Fisher Clans (3, 6, 9), Tidewardens (4, 7, 10). Favor runs 0 to 5; at 5 a faction pledges its crown.
6. Fall back one harbor: no wave this turn, Hull +3, Trust +2, but the Tide takes the harbor you left.
7. Each harbor offers one task when you reach it. Doing it is your action for the turn (ships hold alone, rocs rest) and pays Favor on a roll.
8. Win: two crowns pledged, and the Rite turns the Tide. Lose: the Tide reaches Lanthorn (harbor 10), Hull hits 0, or turn 20 ends without two crowns.

Goal: two crowns pledged.   Lose if: the Tide reaches Lanthorn, Hull 0, or turn 20 ends short.   Turns: 20

Turn 1 of 20 | Hull 12/12 (4 ships) | Trust 4/6 (3 rocs) | Favor: Lords 1, Fisher 1, Wardens 1 | Tide at 1, line at Gullmere (2)
The Grey Tide has swallowed Northreach: grey water, drowned hulls, and things that walk on it. Your four ships, the roc-ship Thornhal, the escorts Gull and Tern, and the tender Oarhouse, anchor across the mouth of Gullmere, a Harbor Lords town of counting-houses and silver vaults.
The seer on Thornhal reads an undertow omen: if the line breaks this turn, the Tide takes two harbors, not one.
Gullmere's task: the Lords want their silver ferried south before the Tide reaches it. Your ships hold the line alone while laden (roll 3+: Favor Lords +2; fail: a laden ship is rammed, Hull -1).
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Task: ferry the silver (line 8, rocs rest, roll 3+).
or say anything else.
```

## Turns

**Player:** Wave is d6+1, so 7 at most, and my ships alone are 8. The undertow can't bite this turn. 4.

```
The Tide comes slow this first night. roll 3 -> wave 4 vs line 8: held by 4. The silver barges slip south under the escorts' lanterns. roll 5 (need 3+) success: the Lords' factor counts every ingot aboard and signs the ledger. Favor Lords +2. The rocs sleep on Thornhal's deck: Trust +1.

Turn 2 of 20 | Hull 12/12 (4 ships) | Trust 5/6 (3 rocs) | Favor: Lords 3, Fisher 1, Wardens 1 | Tide at 1, line at Gullmere (2)
Grey mist on the water at dawn. Gullmere's quays are half empty now that the silver is gone. The Tide has not moved; the drowned mill at Northreach's breakwater. Gullmere has nothing more to ask of you.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Fall back to Netcombe (no wave, Hull +3, Trust +2, Tide takes Gullmere).
or say anything else.
```

**Player:** Lords at 3. A hold-by-6 here is worth a point, and Coinwater's task is still ahead, so I don't need the sure thing yet. One roc: 50% at a point for one Trust. 2.

```
Hask takes wing, screaming at the grey. roll 6 -> wave 7 vs line 10: held by 3. The drowned press hard tonight; Hask breaks their front but there is no clean rout to impress the Lords. No Favor. Trust -1.

Turn 3 of 20 | Hull 12/12 (4 ships) | Trust 4/6 (3 rocs) | Favor: Lords 3, Fisher 1, Wardens 1 | Tide at 1, line at Gullmere (2)
Before the next wave, a line of refugee boats rows out of Gullmere's inner harbor: Lords' families, oars splashing, begging escort past the breakwater. If your ships hold the line alone and it holds, the Lords will remember it (Favor Lords +1).
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Escort the refugees: ships hold alone, rocs rest; +1 Lords if the line holds.
5. Fall back to Netcombe (no wave, Hull +3, Trust +2, Tide takes Gullmere).
or say anything else.
```

**Player:** Wave this turn is d6+2, max 8, line 8. A tie holds. Free point. 4.

```
roll 6 -> wave 8 vs line 8: held, by nothing at all. The drowned climb Tern's anchor chain and are cut away one at a time; the refugee boats clear the breakwater with grey water lapping their gunwales. The Lords saw it. Favor Lords +1. Trust +1.

Turn 4 of 20 | Hull 12/12 (4 ships) | Trust 5/6 (3 rocs) | Favor: Lords 4, Fisher 1, Wardens 1 | Tide at 1, line at Gullmere (2)
The Lords' crown is one point away. The Tide is quiet again, held at Northreach. Skarra, the eldest roc, watches you from Thornhal's mast and does not blink.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Fall back to Netcombe (no wave, Hull +3, Trust +2, Tide takes Gullmere).
or say anything else.
```

**Player:** Max wave is 8. Line 14 holds by 6 on any roll, so that's a guaranteed crown. Trust drops to 2, but the fallback next turn gives most of it back. 3.

```
All three rocs go up, Skarra, Hask and Little Wren, a storm of wings over Gullmere. roll 5 -> wave 7 vs line 14: held by 7. The drowned are torn out of the water and dropped on the Northreach rocks. The Lords' factor comes aboard with a crown of hammered silver. Favor Lords +1: the Harbor Lords pledge their crown. One of two. Trust -3; the rocs land sullen and will not be touched.

Turn 5 of 20 | Hull 12/12 (4 ships) | Trust 2/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 1, Wardens 1 | Tide at 1, line at Gullmere (2)
The waves are growing with the moon; from here a ships-only line can break. Gullmere has nothing left to give.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Fall back to Netcombe (no wave, Hull +3, Trust +2, Tide takes Gullmere).
or say anything else.
```

**Player:** Pull the fleet back to Netcombe. Nothing left to win here, and the rocs need the rest.

```
The anchors come up. Gullmere's counting-houses go grey behind you; the Tide walks in over the quays without a sound. Tide takes Gullmere. The rocs feed on the move: Trust +2. Hull already full.
Netcombe is a Fisher Clans town, net-racks and smokehouses on stilts. Its task: the clans' net-boats are still out past the point, and they want them towed clear before the Tide reaches them (ships hold alone, rocs rest; roll 4+: Favor Fisher +2 and the clans feed the rocs, Trust +2; fail: Favor Fisher +1, Trust +1).

Turn 6 of 20 | Hull 12/12 (4 ships) | Trust 4/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 1, Wardens 1 | Tide at 2, line at Netcombe (3)
Wave this turn is d6+3.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Task: tow the net-boats clear (line 8, rocs rest, roll 4+).
or say anything else.
```

**Player:** 4. One-in-six breach risk for a shot at two points and a feed. Take it.

```
Oarhouse runs lines to the net-boats while Gull and Tern hold the point. roll 3 -> wave 6 vs line 8: held by 2. roll 4 (need 4+) success: every net-boat comes in, and the clans heap smoked fish on Thornhal's deck for the rocs. Favor Fisher +2. Trust +2 (fed), +1 (rested): Trust 6, the cap.

Turn 7 of 20 | Hull 12/12 (4 ships) | Trust 6/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 2, line at Netcombe (3)
The rocs are fat and loud. Wave this turn is d6+4; a ships-only line breaks on a 5 or 6 now. Netcombe has asked all it will ask.
1. Hold with ships; rocs rest (line 8, Trust +1, wasted at the cap).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Fall back to Saltspire (no wave, Hull +3, Trust +2, Tide takes Netcombe).
or say anything else.
```

**Player:** Trust is capped, so resting is wasted. Line 14 against d6+4 holds by 6 on a 1 through 4. Two-thirds for a Fisher point. 3.

```
Three rocs up again. roll 5 -> wave 9 vs line 14: held by 5. One short. The drowned come in thicker than before, a whole hull's worth of them under the water, and the rocs spend the night just holding them off the point. No clean rout, no Favor. Trust -3. Skarra lands on Thornhal's rail and bites a deckhand.

Turn 8 of 20 | Hull 12/12 (4 ships) | Trust 3/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 2, line at Netcombe (3)
Wave this turn is d6+4. Launching all three now would put Trust at 0, and a roc would leave.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3, one roc leaves).
4. Fall back to Saltspire (no wave, Hull +3, Trust +2, Tide takes Netcombe).
or say anything else.
```

**Player:** Fall back to Saltspire. I'll see what the Wardens want.

```
Netcombe's smokehouses sink into grey water as the fleet pulls south. Tide takes Netcombe. Trust +2.
Saltspire is a Tidewardens holding, a white tower on a salt-crusted rock where the Wardens keep the Strand's charts and bells. Its task: carry the Warden's great bell to the spire-top before the Tide drowns it, and only a roc can lift it (one roc flies the errand: Trust -1 and no rest; ships hold alone; roll 3+: Favor Wardens +2; fail: the bell is dropped into the Tide, nothing gained).

Turn 9 of 20 | Hull 12/12 (4 ships) | Trust 5/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 3, line at Saltspire (4)
Wave this turn is d6+5. A ships-only line now breaks on a 3 or better.
1. Launch one roc (line 10, Trust -1).
2. Launch all three rocs (line 14, Trust -3).
3. Task: fly the bell (line 8, Trust -1, roll 3+).
4. Hold with ships; rocs rest (line 8, Trust +1).
5. Fall back to Coinwater (no wave, Hull +3, Trust +2, Tide takes Saltspire).
or say anything else.
```

**Player:** status

```
Turn 9 of 20 | Hull 12/12 (4 ships) | Trust 5/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 3, line at Saltspire (4)
Crowns: 1 of 2.
Harbors: 1 Northreach (Tide), 2 Gullmere (Tide), 3 Netcombe (Tide), 4 Saltspire (you), 5 Coinwater (Lords), 6 Hookhaven (Fisher), 7 Candlehold (Wardens), 8 Lordsgate (Lords), 9 Lastnet (Fisher), 10 Lanthorn (Wardens). Six harbors stand between the Tide and Lanthorn.
Ships: Thornhal, Gull, Tern, Oarhouse. Rocs: Skarra, Hask, Little Wren.
```

**Player:** Wardens need four points and I'd have to fight ships-only to do their bell. Fisher needs two, and Hookhaven is a Fisher town two harbors down. I'm not spending a turn here. Fall back to Coinwater.

```
The bell stays in its tower. Saltspire's Wardens watch the fleet go with their hands folded; the Tide takes the white rock a few hours later, and the bell rings once as it goes under. Tide takes Saltspire. Trust +2 (one wasted at the cap).
Coinwater is a Harbor Lords town, barges and counting-houses. Its task is guarding the counting-house barges, but the Lords are already pledged; there is no Favor left to earn from them.

Turn 10 of 20 | Hull 12/12 (4 ships) | Trust 6/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 4, line at Coinwater (5)
Wave this turn is d6+5.
1. Hold with ships; rocs rest (line 8).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Fall back to Hookhaven (no wave, Hull +3, Trust +2, Tide takes Coinwater).
or say anything else.
```

**Player:** Dead harbor. 4, fall back to Hookhaven.

```
Coinwater's barges are left tied to their posts; the Tide takes them, silver and all. Tide takes Coinwater. Trust already at the cap, Hull already full: the retreat buys nothing but position.
Hookhaven is the Fisher Clans' great harbor, a whole fleet of catch-boats on the beach. Its task: the clans mean to make one last great catch before the Tide, and they want your ships in the line while they do it (ships hold alone, rocs rest; roll 5+: Favor Fisher +2; any other roll: Favor Fisher +1; the clans feed the rocs either way, Trust +2).

Turn 11 of 20 | Hull 12/12 (4 ships) | Trust 6/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 5, line at Hookhaven (6)
Wave this turn is d6+6. A ships-only line breaks on anything but a 1 or 2. Four harbors stand between the Tide and Lanthorn.
1. Hold with ships; rocs rest (line 8).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3).
4. Task: the last great catch (line 8, rocs rest, roll 5+).
5. Fall back to Candlehold (no wave, Hull +3, Trust +2, Tide takes Hookhaven).
or say anything else.
```

**Player:** Trust is full again and the catch refills it, so spend it first. All three rocs: safe line, one-in-three at a free point. 3.

```
The rocs go up over the beach while the clans launch their catch-boats under them. roll 4 -> wave 10 vs line 14: held by 4. The drowned come in on a long grey swell and are beaten back, but it is a brawl, not a rout. No Favor. Trust -3.

Turn 12 of 20 | Hull 12/12 (4 ships) | Trust 3/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 3, Wardens 1 | Tide at 5, line at Hookhaven (6)
Wave this turn is d6+6. The catch-boats are loaded and waiting for your word. Skarra has not eaten since Netcombe and says so, through the seer, in words.
1. Hold with ships; rocs rest (line 8, Trust +1).
2. Launch one roc (line 10, Trust -1).
3. Launch all three rocs (line 14, Trust -3, one roc leaves).
4. Task: the last great catch (line 8, rocs rest, roll 5+).
5. Fall back to Candlehold (no wave, Hull +3, Trust +2, Tide takes Hookhaven).
or say anything else.
```

**Player:** The catch gets me to 4 at worst, 5 at best, and refills the rocs. The line will probably break and cost me Hookhaven, but Hull is full and I have four harbors of slack. 4.

```
The clans row out singing. roll 3 -> wave 9 vs line 8: the line breaks by 1. A drowned hulk grinds down Gull's side and the Tide walks in over Hookhaven's beach behind the catch-boats. Hull -1. Tide takes Hookhaven.
But the catch comes in. roll 5 (need 5+) success: the biggest haul the clans have ever landed, hauled south in the dark with the Tide at their sterns. Favor Fisher +2. Trust +2 (fed), +1 (rested).
Favor Fisher 5: the Fisher Clans pledge their crown. Two crowns.

RESULT: WIN, turn 12 of 20.
Final: Hull 11/12 (4 ships) | Trust 6/6 (3 rocs) | Favor: Lords 5 (pledged), Fisher 5 (pledged), Wardens 1 | Tide at 6 of 10.
With two crowns on Thornhal's deck the seer sings the Rite at Candlehold, and the Grey Tide stops at Hookhaven's beach and begins, slowly, to go out.
Verdict: the Lords' crown came cheap off two early roc launches; the end was decided by spending capped Trust before the great catch refilled it.
Save this one to the library? Give it a name, or say no.
```

**Player:** no

(Playtest: no played_log or library writes were made.)
