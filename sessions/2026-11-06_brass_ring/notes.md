# Brass Ring

Rolls: FORM=12 (logistics) SET=19 (clockwork city of guilds) ROLE=30 (a reef, bent: the cab guild everything washes up on)
LOOP=19 (hunt a boss by its tells) CLOCK=2 (the Tribunal sits on night 16) TWIST=45 (double-blind: you place, he strikes, dusk reveals both)
WIN=4 (expose the Gearwright) MAP=2 (ring of 8 around the Tower) TONE=3 (pulp) CURRENCY=4 (Heat) TRACKED=3 FINISH=1 (final roll) STORY=1 (lean)

Novelty: `sameness.py novelty` OK, no reroll. Brief: nothing stuck.

## Sense card

1. Job: Each night I, the cabmaster of the Brass Ring cab guild, place my two cabs around the ring of guild quarters to catch the Gearwright at his sabotage, so that I have enough Proof when the Tribunal sits on night 16 and he hangs instead of me.
2. Tracked numbers:
   - Heat: how hard the City Watch is looking at me. The Watch holds it. Raised by cabs rattling about after curfew (moving, whipping), by my cab being found at the scene of a strike, by a rumor traced back to me, by a raid gone wrong. Lowered by keeping the cabs in the yard for a night. At 10 I am arrested.
   - Proof: pieces of evidence against the Gearwright, in my strongbox. Raised by a cab seeing him in the act (1), by the Tower guards seeing him (2), by a successful raid of his lodging (3). Never spent.
   - The cabs: where Red and Black stand on the ring (a quarter 1 to 8, or the Tower). A board with rules: they catch where they stand, hear next door, move one step a night.
3. Actions:
   - "Send the Red cab to Quarter 4" (one step along the ring, or to or from the Tower; the Tower stands in the middle and every quarter has a road to it). Heat +1. Possible because the guild's cabs are the only wheels allowed out after curfew.
   - "Lie low, lanterns out." Heat -2. Dark cabs are not logged, and see no faces; a lit cab out after curfew must be going somewhere or the Watch moves it on, which is why there is no idle-and-lit night.
   - "Leak that the Tower guard stands down tomorrow night." Heat +1, roll 4+ (3+ once you know his habit: you know which taverns he drinks in). He bites and comes to the Tower the next night, where a lit cab must wait. A miss: the Watch traces the rumor, Heat +2. Once per habit: after night 9 he has forgotten the story.
   - "Raid his lodging in Quarter L." Offered whenever the evidence (every 2 Proof) includes a receipt with his address. Roll 4+ (3+ with a cab already in that quarter to carry the men). Proof +3. A miss: a brawl in a guild quarter, Heat +4. After any raid he moves house, and the next receipt comes 2 Proof later.
4. Trades: none. Nothing is bought or sold. Heat changes only as a consequence of what the cabs do.
5. Read aloud: nothing needs "it is like".
6. World card:
   - Era and kit: a clockwork city, gas lamps, horse cabs with brass fittings, mainsprings the size of a man in every guild hall, a Watch with lanterns and truncheons. No telegraph; news moves by cab and runner.
   - Quarters 1 to 8 run clockwise around the Clock Tower. Each quarter touches its two neighbors and the Tower. 8 touches 1.
   - One Heat is one entry in the Watch sergeant's book. At 10 entries he has his warrant.
   - One Proof is one thing you could put on the Tribunal's table: a mask, a brass key, a sworn cab driver, a receipt.
   - The Gearwright: a masked saboteur unwinding the guilds' mainsprings one a night. He buys grease at dusk a few doors from the job, the same number of doors each time, until night 9 when he notices the cabs and changes the count. Nobody knows his face, which is why the Tribunal is happy to hang the cabmaster whose cabs are always nearby.
   - Why you cannot simply fight him: you never see him until he is at the mainspring, and a cab driver with a whip is not a watchman. Catching him in the act is the fight.
   - Why the guilds do not tell you where he struck: each guild hides its unwound spring from the others; a stopped clock is a loss of face. You learn a strike only if your cab was there or next door.
   - Why you cannot leave the city: the Tribunal holds your guild charter as bond. Run and the guild hangs.
   - The Tower is the Watch's own ground: a catch there is witnessed by the Tower guards, so it costs no Heat and counts double. The Tower walls are blind to the ring.

## Gambits
- bait (rival): leak that the Tower is unguarded. Stakes Heat. Changes `bait` (he comes to the Tower tonight). One per game.
- raid (also the late lever): raid his lodging whenever a receipt names it (every 2 Proof). Stakes Heat 4 on a miss for Proof 3. He moves house after every raid.
Ideas log: Low Wells wanted ambush, assassinate, fortify. Bait is the ambush; the raid is the strike at him; lie low is the fortify.

## Design
- Rival tell: shown before the player acts (tonight's grease quarter in the status line). The habit (doors from the grease) is hidden, learned by hearing or seeing one strike, re-hidden on night 9.
- Midpoint escalation: night 9, the habit changes (and the leak can be tried again). Unlock: the lodging, every 2 Proof. Late lever: the raid, which repeats.
- Finish: final roll at the Tribunal, d6 + Proof against 11. Proof is the purchase. Proof 10 is certain; Proof 4 or less is not even heard.
- Rival policy: target = grease quarter + hidden offset in {-2,-1,+1,+2}, redrawn to a different value at the dusk before night 9. Baited: the Tower instead.
- Odd element: the guilds hide their losses, so a strike with no cab nearby is a snap in the dark.

## Opening screen (as presented)

BRASS RING
You are the cabmaster of the Brass Ring cab guild in a clockwork city, where eight guild quarters circle the Clock Tower and your two cabs are the only wheels allowed out after curfew. A masked saboteur, the Gearwright, unwinds one guild's mainspring every night, and the Tribunal that sits after night 16 means to hang you for it, since your cabs are always nearby; you cannot leave, because the Tribunal holds your guild charter as bond. Each night you move one cab, douse both lanterns to cool the Watch, or spend the night on a leak or a raid; a lit cab standing where he strikes catches him in the act. A catch is worth 1 Proof, the Tower trap 2, a raid 3; a cabmaster who brings 7 or more to the Tribunal has even odds, and 10 is certain.

Your numbers
- Heat: how hard the City Watch is looking at you. Cabs rattling about after curfew raise it; a night with the lanterns out lowers it. At 10 you are arrested.
- Proof: the evidence against the Gearwright in your strongbox. It is added to the Tribunal's roll.
- Cabs: where Red and Black stand, a quarter 1 to 8 or the Tower in the middle. A cab catches him where it stands and hears a strike in the quarter next door.
- Gearwright: where the Watch saw him buy grease this evening, and what you know of his habit.

Rules
1. Eight quarters, 1 to 8 clockwise, ring the Tower. Your cabs are Red and Black. Each night move one cab one step: to a neighbor quarter, or to or from the Tower.
2. The Gearwright unwinds one quarter a night. At dusk the Watch reports where he bought grease; he strikes 1 to 2 quarters from there, always the same count and direction (his habit) until night 9, when it changes.
3. A lit cab in the struck quarter catches him: Proof +1, but the Watch finds it there: Heat +2. A cab next door hears the spring snap and learns where he struck. A Tower cab sees only the Tower.
4. A move costs Heat +1. Lie low, lanterns out, cabs where they stand: Heat -2 (never below 0), but they catch nothing that night, though they still hear. Start at Heat 3; at 10 you are arrested and lose.
5. Leak that the Tower guard stands down tomorrow (Heat +1): roll 4+, or 3+ once you know his habit, and tomorrow night he strikes the Tower, not the ring. A miss is traced to you: Heat +2.
6. The leak can be tried once before night 9 and once after, never on night 16. Caught at the Tower by a lit cab there, with the Tower guard as witness: Proof +2 and no Heat.
7. At Proof 2, and 2 Proof after each raid, his address turns up and a raid is offered: roll 4+, or 3+ with a cab in that quarter, for Proof +3; a miss costs Heat +4. He moves house.
8. After night 16 the Tribunal sits. Roll a d6 and add your Proof: 11 or more exposes the Gearwright and you win. Less, and you are convicted in his place.

Goal: when the Tribunal sits after night 16, your Proof plus one roll of a d6 reaches 11.   Lose if: Heat reaches 10, or that roll falls short.   Turns: 16

Turn 1 of 16 | Heat 3 | Proof 0 | Cabs: Red Tower, Black Tower | Gearwright: grease at Q3, habit unknown
The curfew bell has gone. Both cabs stand in the Tower yard, lanterns lit, horses steaming. The Watch's dusk report says the Gearwright bought his grease in Quarter 3, so tonight he strikes Quarter 1, 2, 4 or 5; which one is his habit, and you do not know it yet. A cab parked in Quarter 4 catches him if he comes to 4 and hears him if he comes to 5; a cab in Quarter 2 does the same for 2 and 1. A Tower cab sees only the Tower, but can reach any quarter in one move. You learn his habit by seeing or hearing one strike. Pick a number; a move that needs a destination asks for it next.
1. Send the Red cab out from the Tower to a quarter, 1 to 8 (Heat +1)
2. Send the Black cab out from the Tower to a quarter, 1 to 8 (Heat +1)
3. Lie low with the lanterns out (Heat -2, no catch tonight)
4. Leak that the Tower guard stands down tomorrow night (Heat +1; roll 4+ and he strikes the Tower tomorrow; miss: Heat +2)
or say anything else.

## Tuning record

- Round 1: heuristic 0.80 (too easy). Found: parked cabs caught for free while lying low; bait (same night, cab at Tower) was offered in 17% of states.
- Fix: lie low puts the lanterns out (no catch that night, hearing still works); bait now lures him to the Tower the next night, legal from anywhere, once per habit (reset on night 9).
- Round 2: TRIBUNAL_NEED 9 to 11; look-ahead had crashed (heuristic indexed an empty list when both cabs sat on the target). Fixed.
- Round 3: heuristic 0.47, profile healthy (dilemma share 0.55, no flat stretch, finish consequential), ablate: every action needed or marginal.
- Round 4: HEAT_START 2 to 3. CLEAN. random 0.01, heuristic 0.43, look-ahead 0.48, mutation 95%.

- Cold reads 1 to 3 (scores 7, 7, 6, no NONSENSE, but 4 to 5 unclear lines each): the turn-1 hint miscounted, "doors" read as jargon, "whip" confused two readers, rule 3 "Tower cabs see nothing" clashed with rule 6, an "unguarded" Tower had guards, and the raid was once-only. Design simplified after round 3: the whip (dash) is cut (ablate had it marginal), the bait is now "the Tower guard stands down", and the raid repeats: every 2 Proof a receipt names his current lodging, and after any raid he moves house. Rounds 5 and 6 (design changes, not number tuning): CLEAN, raid offered in 30% of states, heuristic 0.44 to 0.50, look-ahead 0.44 to 0.45, mutation 92%.
- The raid gambit's odds purchase is positional: a cab in his quarter makes it 3+, which gives the cabs a second routing goal between catches.

- Cold reads 4 and 5 (7 and 7, no NONSENSE): remaining nits were my own premise sentence about idle lit cabs (cut), the Tower-catch wording, the raid rule's density, and twice "why does a cab at the Tower make a rumor more believable". The leak's odds purchase is now knowledge, not position: 4+, or 3+ once you know his habit (you know which taverns he drinks in). QA round 1 fixed: a leak pending across night 9 could be re-leaked (BR-1), the sheet now states the Heat floor and the no-leak-on-night-16 rule (BR-3), ruled-out doors stop accumulating once the habit is known (BR-6); tests added for each and for the Tribunal past the mark and the arrest-before-receipt order. After these: CLEAN, heuristic 0.44, look-ahead 0.35, mutation 93%, bait offered 46%, raid 33%.

- Cold reads 6 and 7 (6 and 7, no NONSENSE, heading 1 right both times, first move Red to Quarter 4 both times): the quoted lines are now questions the sheet answers ("do dark cabs hear", "is the raid my action for the night", "7 Proof is even odds, I checked"). Seven readers never marked NONSENSE and always understood the job; none got under three quoted lines. The sheet sits at eight lines of 31 to 40 words with two gambits, a habit change and a final roll; the only cut left is a gambit, which hard limit 11 forbids. Presented with the dense sheet named as the rough edge.

- QA round 2 (no S1 or S2, five S3): silence now names the habits it rules out and concludes the habit when one is left; rule 7 states when addresses turn up (at Proof 2, and 2 Proof after each raid); no grease quarter is drawn for a Tower night; no habit lesson on the last night; the premise names leak and raid nights. Tests added: deduction from silence, a dark cab hearing next door, a non-empty ruled-out list cleared by a catch, the tell on a Tower night, the Tower move list, the habit set computed from MAX_DOORS.

Accepted warnings:
- BAND: look-ahead under the heuristic (0.35 vs 0.44 at 100 games, standard error 0.05): the heuristic is strong, the search is coarse with up to 18 move candidates and 8 rollouts each, and a final d6 caps what search can add.
- BAND: look-ahead 0.48, under 0.60. The final roll is the design (FINISH 1): a d6 against Proof caps what search can add, and the heuristic is strong (gap 5 points). Not a flat game: profile shows 64% of turns consequential.
- TAG tower_missed 0% in heuristic games: the heuristic never leaves the Tower empty on a baited night; a careless player can. Fine for a twist.

## Pre-flight
- Traces read: seed 7 heuristic, seed 7 random (arrested night 5 after a traced rumor at Heat 7: the sharp consequence is on the sheet, rule 5), seed 5 scripted (flank, bait miss, hear, catch). Move counts match the budget; dusk endings are real events (arrest, Tribunal).
- texts read: 34 status shapes (one format, four fields), 13 option wordings, 42 events, 3 endings. Plurals correct ("1 door", "2 doors"), no stale words.
- Odds buyable: bait 4+ or 3+ once his habit is known; raid 4+ or 3+ with a cab in the lodging quarter; Tribunal d6 plus Proof.
- Decision test: turn 1 (flank which side, or bait), turn 8 (spend Heat on a last catch before the habit resets, or lie low), turn 14 (raid at 4+ with Heat room, or one more catch).
- Odd element kept: the guilds hide their losses, so a strike with no cab near is a snap in the dark and the silence itself rules out doors.
