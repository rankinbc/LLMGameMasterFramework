# Cold Burn - playthrough transcript

Playtest game 04, 2026-10-14. GM and player both simulated; player persona is a systems-minded strategy and trading gamer who plays to win.

## Rolls

Command run exactly as written in the skill:

```
echo "SET=$((RANDOM%40+1)) ROLE=$((RANDOM%40+1)) LOOP=$((RANDOM%24+1)) CLOCK=$((RANDOM%18+1)) TWIST=$((RANDOM%36+1)) WIN=$((RANDOM%14+1)) MAP=$((RANDOM%10+1)) TONE=$((RANDOM%8+1))"
SET=27 ROLE=5 LOOP=13 CLOCK=18 TWIST=11 WIN=7 MAP=2 TONE=4
```

- SET 27: Trench front, static war
- ROLE 5: Fleet admiral with 4 ships
- LOOP 13: Ration a shrinking supply across needs
- CLOCK 18: Each turn costs a fixed upkeep
- TWIST 11: Damage is permanent; nothing repairs
- WIN 7: Deliver a cargo intact
- MAP 2: Hex ring of 8 around a center
- TONE 4: Hard sci-fi

Novelty check skipped (no played_log yet). Library empty.

Hidden setup rolls (not shown to the player): `printf "G\nG\nG\nM\nD\nK\nC\n" | shuf` over sectors 2 to 8 gave `D C M G G G K` (2 debris, 3 clear, 4 mines, 5 gun, 6 gun, 7 gun, 8 cache). A d6 stream was pre-rolled and consumed in order: `2 2 1 3 2 5 6 4 4 1 ...`

## Present

```
COLD BURN
Two years of static orbital war over Thessaly-4 have left eight fortified sectors ringing the dying ground base Hollow; you have four ships, one sealed deuterium core, and an orbit that eats reaction mass just to stay up.

Rules
1. Four ships on a ring of 8 orbital sectors around Hollow, the base at the center. You start in sector 1. A sector's contents are unknown until a ship enters it; Pike also sees both neighboring sectors.
2. One shared tank of reaction mass (RM). Upkeep of 1 RM per surviving ship is paid at the start of every turn. RM 0 means the fleet deorbits and you lose. Scuttle a ship any time to end its upkeep.
3. Each ship does one thing per turn. Move one sector costs 2 RM (Vesper 1). Evade costs 1 RM and makes guns need 6+ on that ship this turn. Hold costs nothing.
4. Each enemy gun fires once per turn at the largest ship in its own or a neighboring sector (Castellan > Vesper > Mule > Pike): roll 4+ hits for 2 hull. A gun that fires is revealed.
5. A ship that holds may shoot one revealed gun in its own or a neighboring sector: Castellan hits 4+, Vesper 5+, Pike 6+. A hit kills that gun.
6. Descent: from sector 5 only, 6 RM, takes 3 turns. During descent Mule cannot evade or abort, and guns in sectors 4, 5, 6 fire at Mule first, each turn.
7. Nothing repairs, on either side. A ship at 0 hull is gone. Mule carries the core; Mule gone, core gone.
8. Win: Mule lands (third descent turn done). Lose: Mule destroyed, RM 0, or turn 16 ends.

Goal: land Mule at Hollow.   Lose if: Mule destroyed, RM hits 0, or turn 16 ends.   Turns: 16

Turn 1 of 16 | RM 76 (upkeep 4) | Hull C10 V6 M4 P3 | Pos C1 V1 M1 P1
Sector 1 is your anchorage, the one safe berth on the ring. Hollow is directly under sector 5 on the far side: clockwise is 2-3-4-5, the other way 8-7-6-5. The tank held 80; this turn's upkeep is already paid. Nav flags a perigee pass on turn 9: upkeep doubles from then on. Sectors 2 through 8 are unknown.
C is Castellan (cruiser), V Vesper (fast destroyer), M Mule (freighter with the core), P Pike (scout corvette).
1. Whole fleet to sector 2 (7 RM).
2. Pike alone to sector 2 (2 RM); it will see 1 and 3.
3. Castellan and Pike to sector 2 (4 RM); Castellan draws any fire.
4. Pike to 2 and Vesper to 8 (3 RM); probe both ways round.
or say anything else.
```

## Turns

**Player:** 4. Information first, and Vesper is cheap to move. I'll take the risk on the scouts.

Pike slides into sector 2: a debris field, old hull plating and slag. Guns need 6+ to hit anything parked in it. From there Pike reads sector 3 as clear, nothing but vacuum.
Vesper drops into sector 8 and finds the derelict tanker Yoke, holed but with 12 RM still in her bladders. Vesper siphons it: RM 73 to 85.
Then a railgun flash from sector 7: it fires at Vesper. roll 2 (need 4+) miss. Gun revealed in sector 7.

Turn 2 of 16 | RM 81 (upkeep 4) | Hull C10 V6 M4 P3 | Pos C1 V8 M1 P2
Known: 2 debris, 3 clear, 7 gun, 8 drained tanker. Vesper is inside gun 7's reach and will be shot again if it stays.
1. Vesper back to 1 (1 RM); Castellan and Mule to 2 (4 RM).
2. Vesper holds at 8 and shoots gun 7 (5+), trading fire.
3. Pike to 3, Castellan to 2 (4 RM); Vesper holds.
4. Pike to 3, Castellan and Mule to 2, Vesper back to 1 (7 RM).
or say anything else.

**Player:** 4. Vesper trading 5+ against 4+ is a losing duel. Pull it back and push clockwise.

Vesper burns back to the anchorage. Castellan and Mule tuck into the debris at 2. Pike moves up to 3: clear. From 3 Pike reads sector 4: a minefield. Contact mines, tethered, dense enough that a ship pushing through rolls 4+ to take 2 hull.
No gun fires. Nothing is in reach of 1, 2, or 3.

Turn 3 of 16 | RM 70 (upkeep 4) | Hull C10 V6 M4 P3 | Pos C2 V1 M2 P3
Known: 2 debris, 3 clear, 4 mines, 7 gun. Sector 5, Hollow's descent point, is unknown.
1. Castellan to 3, Pike into 4 (4 RM); Pike eats the mine roll and sees 5.
2. Castellan to 3 (2 RM); Pike holds.
3. Castellan and Mule to 3, Vesper to 2 (5 RM); keep the group tight.
4. Vesper the other way to 8 (1 RM), then 7 next turn to shoot gun 7.
or say anything else.

**Player:** 1. Pike is a scout; a mine roll on it beats one on the Mule, and I need eyes on 5. If 5 has a gun it shoots Pike, and I'll accept that.

Castellan moves to 3. Pike noses into the minefield: roll 2 (need 4+ to detonate) clean. From 4 Pike reads sector 5: a hardened gun emplacement, railgun on a cold-gas turret, right over Hollow's crater.
It fires on Pike, the only ship in its reach: roll 1 (need 4+) miss. Gun confirmed in 5.

Turn 4 of 16 | RM 62 (upkeep 4) | Hull C10 V6 M4 P3 | Pos C3 V1 M2 P4
Known guns: 5 and 7. Sector 6 unknown. Gun 5 covers 4, 5, 6 and fires again this turn at the biggest ship inside that reach; right now that is Pike.
1. Castellan into 4 (2 RM, mine roll); it becomes the target. Pike holds and snipes at 6+.
2. Pike back to 3 (2 RM), Castellan into 4 (2 RM).
3. Castellan into 4, Pike evades (3 RM); Pike cannot shoot while evading.
4. Pike holds and shoots at 6+; Castellan stays out of it.
or say anything else.

**Player:** 1. Castellan is the sponge. Pike takes the long shot.

Castellan pushes into the minefield: roll 3 (need 4+) clean, two mines slide past the hull. Pike fires at the emplacement: roll 2 (need 6+) miss, the slug sails over the crater rim.
Gun 5 swings to the bigger target: fires at Castellan, roll 5 (need 4+) hit. Castellan 10 to 8, a two-metre gouge in the forward plating. Nothing repairs it.

Turn 5 of 16 | RM 55 (upkeep 4) | Hull C8 V6 M4 P3 | Pos C4 V1 M2 P4
Castellan and Pike both sit next to gun 5. Mule and Vesper are out of everything's reach.
1. Castellan (4+) and Pike (6+) both shoot gun 5; everyone else holds.
2. Both shoot; Mule to 3 and Vesper to 2 to stage (3 RM).
3. Castellan shoots, Pike falls back to 3 (2 RM).
4. Castellan evades (1 RM), Pike shoots alone.
or say anything else.

**Player:** 2. Stage the Mule at 3 where nothing reaches it, and shoot.

Castellan's main rail: roll 6 (need 4+) hit. The slug goes through the turret ring; the emplacement in 5 tumbles out of its mount and stops. Gun 5 dead. Pike holds fire.
Mule moves up to 3, Vesper to 2. Nothing fires. The ring is silent for the first time since sector 7.

Turn 6 of 16 | RM 48 (upkeep 4) | Hull C8 V6 M4 P3 | Pos C4 V2 M3 P4
Sector 5 is the only place Mule can descend from. Sector 6, next door to it, is still unknown. Anything in 6 reaches 5.
1. Castellan into 5 (2 RM); bait whatever covers it.
2. Pike into 5 (2 RM); it will see 4 and 6, but is the only target.
3. Castellan and Pike into 5 (4 RM); Castellan soaks, Pike looks.
4. Mule into 4 now (2 RM, mine roll) while Castellan goes to 5.
or say anything else.

**Player:** 3. Same drill. I want to know what is in 6 before the Mule touches 4.

Castellan and Pike move onto the dead emplacement in 5. Pike reads sector 6: a second gun, live, turret already tracking. It fires at Castellan: roll 4 (need 4+) hit. Castellan 8 to 6. Pike reads 4 as the known minefield; nothing else there.
Gun 7 stays quiet; nothing of yours is in 6, 7, or 8.

Turn 7 of 16 | RM 40 (upkeep 4) | Hull C6 V6 M4 P3 | Pos C5 V2 M3 P5
Gun 6 covers 5, 6, 7, which includes the descent sector. Gun 7 covers 6, 7, 8 and cannot touch a descent. Two turns to perigee; upkeep doubles on turn 9.
1. Castellan and Pike shoot gun 6; Mule holds at 3.
2. Both shoot; Mule into 4 (2 RM, mine roll) to stage; Vesper to 3 (1 RM).
3. Both shoot; scuttle Pike after, to cut upkeep.
4. Castellan evades (1 RM), Pike shoots alone.
or say anything else.

**Player:** 2. The clock is the real enemy now. Mule takes its mine roll while the guns work.

Castellan fires at gun 6: roll 4 (need 4+) hit. The slug goes into the magazine; the emplacement in 6 vents and goes dark. Gun 6 dead. Pike holds.
Mule enters the minefield: roll 1 (need 4+) clean. Vesper moves up to 3.
No gun in reach of anything. Gun 7 is the last known one, two sectors off Mule's path.

Turn 8 of 16 | RM 33 (upkeep 4) | Hull C6 V6 M4 P3 | Pos C5 V3 M4 P5
Mule is one move from 5. Descent costs 6 RM and three turns, and from turn 9 the fleet pays 2 RM per ship per turn.
1. Mule to 5 (2 RM); keep all four ships.
2. Mule to 5; scuttle Pike.
3. Mule to 5; scuttle Pike and Vesper.
4. Hold everything; send Pike to 6 to look at 7 (2 RM).
or say anything else.

**Player:** status

Turn 8 of 16 | RM 33 (upkeep 4) | Hull C6 V6 M4 P3 | Pos C5 V3 M4 P5
Known ring: 1 anchorage, 2 debris (cover, guns need 6+), 3 clear, 4 mines (4+ for 2 hull on entry), 5 dead gun, 6 dead gun, 7 live gun, 8 drained tanker.
Descent: from 5 only, 6 RM, three turns, guns in 4, 5, 6 fire at Mule each turn. None alive there.
Upkeep from turn 9: 2 RM per surviving ship.

**Player:** Mule to 5, scuttle Pike. Four ships at 8 a turn lands me with 1 RM; three ships lands me with 7. Pike is done, and Vesper stays as a 5+ gun in case I have miscounted something.

Mule burns into 5 and settles over the crater, the dead emplacement's turret still hanging off its ring. Pike's crew transfers to Castellan by tether; Pike is vented and cut loose, drifting out of the ring. Three ships remain.
No gun fires.

Turn 9 of 16 | RM 25 (upkeep 6) | Hull C6 V6 M4 | Pos C5 V3 M5
Perigee. The station-keeping burn doubled; the tank dropped 6 this turn. Mule is in position. Every gun that could reach a descent is dead.
1. Begin descent (6 RM); Castellan and Vesper hold.
2. Begin descent; Vesper to 4 (1 RM, mine roll) to close up.
3. Begin descent; scuttle Vesper.
4. Hold one turn; Castellan to 6 (2 RM) to shoot gun 7 next turn.
or say anything else.

**Player:** 1. Descend. There is no reason to touch anything.

Mule lights its deorbit burn, 6 RM, and drops out of the ring. Descent turn 1 of 3. Guns in 4, 5, 6: none alive. Nothing fires. Castellan and Vesper hold position.
Hollow comes up on the beacon: "We see your burn. Reactor at four percent."

Turn 10 of 16 | RM 13 (upkeep 6) | Hull C6 V6 M4 | Pos C5 V3 M descending
Mule is in the entry phase and cannot act. One more upkeep to pay before touchdown: 6 RM. You have 13.
1. Hold everything.
2. Scuttle Vesper now (upkeep drops to 4).
3. Castellan to 6 (2 RM) to shoot gun 7 next turn.
or say anything else.

**Player:** 1. Hold.

Mule's heat shield takes the entry; telemetry flickers and comes back. Descent turn 2 of 3. No gun in reach. Castellan and Vesper hold.

Turn 11 of 16 | RM 7 (upkeep 6) | Hull C6 V6 M4 | Pos C5 V3 M landing
Final approach. Touchdown resolves at the end of this turn.
1. Hold everything.
2. Scuttle Vesper.
3. Castellan to 6 (2 RM).
or say anything else.

**Player:** 1. Hold. Bring it down.

Mule's landing legs hit Hollow's pad. Descent turn 3 of 3. Core delivered, untouched. Hollow's reactor crew have the deuterium in the feed line inside the hour.

RESULT: WIN on turn 11 of 16.
Final: RM 7 | Hull Castellan 6, Vesper 6, Mule 4 | Pike scuttled | Guns killed: 5, 6. Gun 7 never engaged.
Verdict: scouting with Pike before the Mule moved, and two 4+ rails that landed on the first and second shots, meant the Mule never took a hit; the tank, not the guns, ended up as the real opponent.

(played_log append skipped per playtest override.)

Save this one to the library? Give it a name, or say no.

**Player:** no
