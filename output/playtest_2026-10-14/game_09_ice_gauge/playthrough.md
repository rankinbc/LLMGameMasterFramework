# Playthrough: Ice Gauge (game 09)

## Rolls

Command: `echo "SET=$((RANDOM%40+1)) ROLE=$((RANDOM%40+1)) LOOP=$((RANDOM%24+1)) CLOCK=$((RANDOM%18+1)) TWIST=$((RANDOM%36+1)) WIN=$((RANDOM%14+1)) MAP=$((RANDOM%10+1)) TONE=$((RANDOM%8+1))"`

Output: `SET=33 ROLE=39 LOOP=23 CLOCK=8 TWIST=18 WIN=4 MAP=7 TONE=6`

- SET 33: Plague-era river town
- ROLE 39: Drone fleet operator
- LOOP 23: Repair a failing machine piece by piece
- CLOCK 8: Winter closes the passes
- TWIST 18: Two currencies that trade at a shifting rate
- WIN 4: Destroy a named enemy
- MAP 7: Three islands and the sea between
- TONE 6: Military procedural

Novelty check skipped (no played_log, no library). A stream of 120 d6 was pre-rolled with Bash and consumed in order for every die in the game; hidden-system rolls are listed in state.md.

## Present

```
ICE GAUGE
A fever has shut the river town of Harrow's Crossing; you run the quarantine command's drone shed on Ferry Island, and the barge Marigold is running fever-carriers past the cordon every night.

Rules
1. One action per turn: Scout an island with the Sparrow, Take a posted job, Buy and fit one Cormorant part, or Strike. Swapping scrip and silver at the posted rate is free, any turn, whole silver only.
2. Command pays you 6 scrip at the end of every turn. Mill Island sells for silver only, Chapel Island for scrip only, Command requisitions for scrip. The rate moves every turn.
3. The Cormorant strike drone needs Airframe and Payload to fly a strike. Optics +1 and Datalink +1 to the strike roll; Datalink also shows the Marigold's position every turn.
4. Strike: roll d6 + bonuses, need 5+. A hit sinks the Marigold and wins. A miss spends the Payload; on a 1-2 the airframe cracks too.
5. The Marigold moves on a circuit of two docks and four reaches. You may only strike her in a reach; if she is docked when you launch, the strike aborts and the turn is lost.
6. Scouting an island reveals its dock and the reaches beside it. If the Sparrow finds her in a reach, roll d6: on a 1 her crew shoots it down and you can never scout or run jobs again.
7. You may strip the Sparrow's camera to fit Optics for free, but then the Sparrow is gone for good.
8. The ice gauge starts at 10 and drops some turns. At 0 the river freezes, the Marigold walks off over the ice, and you lose. Turn 18 is the hard stop.

Goal: Sink the Marigold.   Lose if: Ice gauge hits 0, or turn 18 ends.   Turns: 18

Turn 1 of 18 | Scrip 10 | Silver 8 | 1 Ag = 2.00 scrip | Ice 10 | Cormorant: Air -- Opt -- Link -- Pay -- | Marigold: unknown
Ferry Island, dawn. The Cormorant sits in the ferry shed with a cracked wing spar, no camera, no radio, no bombs. The Sparrow quadcopter is charged.
Parts board: Airframe spar 24 Ag (Mill yard). Optics camera 18 Ag (Mill yard). Datalink radio 20 scrip (Chapel fence). Munitions pair 30 scrip (Command).
Jobs board: night fire-watch over Harrow's timber yard, 8 Ag, no risk.
Ice gauge chalked on the shed wall: 10.
1. Scout Mill Island (Mill Dock, Backwater, North Reach)
2. Scout Chapel Island (Chapel Dock, South Reach, West Reach)
3. Scout the home channels (North, South, West Reach)
4. Job: fire-watch over Harrow's yard, 8 Ag
5. Buy and fit a part (name it)
or say anything else.
```

## Turns

**Player:** 4. Eight silver for a no-risk night is the best rate on the board, and I need 24 for that spar before anything else matters.

Turn 1 resolved: The Sparrow orbits the timber yard till dawn. Nothing burns. Harrow's foreman counts out 8 Ag. Command credits 6 scrip at shift change.

Turn 2 of 18 | Scrip 16 | Silver 16 | 1 Ag = 2.25 scrip | Ice 9 | Cormorant: Air -- Opt -- Link -- Pay -- | Marigold: unknown
The rate ticked up overnight; silver buys more scrip than yesterday. The ice gauge lost a point.
Jobs board: medicine drop to the Chapel ward, 10 scrip, no risk.
Parts board unchanged.
1. Scout Mill Island
2. Scout Chapel Island
3. Scout the home channels
4. Job: medicine drop, 10 scrip
5. Buy and fit a part
or say anything else.

**Player:** 4. Still bootstrapping. I'll start scouting once I have something that can fly.

Turn 2 resolved: The Sparrow lowers a sealed crate onto the chapel roof. A nurse signs for it. 10 scrip, plus Command's 6.

Turn 3 of 18 | Scrip 32 | Silver 16 | 1 Ag = 2.75 scrip | Ice 8 | Cormorant: Air -- Opt -- Link -- Pay -- | Marigold: unknown
Silver jumped again. At this rate your 32 scrip is worth 11 Ag.
Jobs board: Harrow wants a sealed packet carried across the North Reach to the far bank, 12 Ag. His men say someone has been shooting at gulls out there. Risk: roll d6, on a 1 the Sparrow is lost.
1. Scout Mill Island
2. Scout Chapel Island
3. Scout the home channels
4. Job: packet run, 12 Ag, risk on a 1
5. Buy and fit a part
or say anything else.

**Player:** Twelve silver is 33 scrip at today's rate and it gets me to 28 Ag, airframe next turn with change. Five in six. Taking it. 4.

Turn 3 resolved: roll 5 (need 2+) success. The Sparrow crosses the North Reach low and fast; a shot cracks somewhere behind it but nothing hits. Harrow pays 12 Ag. Command adds 6 scrip.

Turn 4 of 18 | Scrip 38 | Silver 28 | 1 Ag = 3.00 scrip | Ice 8 | Cormorant: Air -- Opt -- Link -- Pay -- | Marigold: unknown
Silver is at 3.00 and climbing; the Mill parts are getting dearer in scrip terms by the day. The ice held.
Jobs board: spot Harrow's stolen skiff from the air, 9 Ag, no risk.
1. Scout Mill Island
2. Scout Chapel Island
3. Scout the home channels
4. Job: find the skiff, 9 Ag
5. Buy and fit a part
or say anything else.

**Player:** 5, the airframe spar. Lock in the silver price before the rate runs further.

Turn 4 resolved: A Mill yard cart brings the spar over on the morning ferry. Fitting it takes the whole day. 24 Ag paid. Command adds 6 scrip.

Turn 5 of 18 | Scrip 44 | Silver 4 | 1 Ag = 3.00 scrip | Ice 8 | Cormorant: Air OK Opt -- Link -- Pay -- | Marigold: unknown
The Cormorant can fly now; it just cannot see or hit anything. Rate flat.
Jobs board: night fire-watch over Harrow's yard, 8 Ag, no risk.
1. Scout Mill Island
2. Scout Chapel Island
3. Scout the home channels
4. Job: fire-watch, 8 Ag
5. Buy and fit a part (Datalink 20 scrip, Munitions 30 scrip, Optics 18 Ag)
or say anything else.

**Player:** 5, the Datalink. I have zero fixes on her and no idea what her circuit looks like. Twenty scrip for a permanent position feed beats burning turns on the Sparrow, and I'm still two turns from munitions anyway.

Turn 5 resolved: The Chapel fence hands over a radio module wrapped in a blanket. By evening the Cormorant's relay is pulling the Marigold's barge-band chatter. 20 scrip paid. Command adds 6.

Turn 6 of 18 | Scrip 30 | Silver 4 | 1 Ag = 3.25 scrip | Ice 8 | Cormorant: Air OK Opt -- Link OK Pay -- | Marigold: South Reach
First fix: she is in the South Reach between Chapel and Mill, moving. Silver up again.
Jobs board: photograph the far-shore ice edge for Harrow, 10 Ag, no risk.
1. Scout the home channels
2. Job: ice-edge photos, 10 Ag
3. Buy and fit Munitions, 30 scrip
4. Strip the Sparrow camera to fit Optics (free, Sparrow gone)
or say anything else.

**Player:** 3. Munitions. Exactly 30 in hand. I want to see where she goes from a reach before I commit a strike.

Turn 6 resolved: Command signs over two guided munitions and a stern note about rules of engagement. 30 scrip paid, 6 credited.

Turn 7 of 18 | Scrip 6 | Silver 4 | 1 Ag = 3.25 scrip | Ice 8 | Cormorant: Air OK Opt -- Link OK Pay OK | Marigold: Mill Dock (docked)
She moved out of the South Reach and tied up at Mill Dock overnight. Striking a docked barge aborts under ROE. The ice has sat at 8 for four turns.
Jobs board: fever census over Chapel Island, 8 scrip, no risk.
1. Job: census, 8 scrip
2. Strip the Sparrow camera to fit Optics (free, Sparrow gone)
3. Scout the home channels
4. Strike (aborts, she is docked)
or say anything else.

**Player:** 1. No point stripping the Sparrow while the jobs are the only income I have. I'll bank scrip and wait for her to cast off.

Turn 7 resolved: The Sparrow counts cots and chimney smoke over Chapel Island. 8 scrip, plus 6 from Command.

Turn 8 of 18 | Scrip 20 | Silver 4 | 1 Ag = 2.75 scrip | Ice 8 | Cormorant: Air OK Opt -- Link OK Pay OK | Marigold: Mill Dock (docked)
Still at Mill Dock; her crew is loading something under tarps. Silver slipped to 2.75.
Jobs board: medicine drop to the Chapel ward, 10 scrip, no risk.
1. Job: medicine drop, 10 scrip
2. Strip the Sparrow camera to fit Optics
3. Scout the home channels
4. Strike (aborts, she is docked)
or say anything else.

**Player:** 1. Two turns docked. She's loading for a run, so she should be in open water next turn.

Turn 8 resolved: Crate on the chapel roof, signature, 10 scrip. Command adds 6. Toward midnight the relay picks up her engine.

Turn 9 of 18 | Scrip 36 | Silver 4 | 1 Ag = 2.25 scrip | Ice 7 | Cormorant: Air OK Opt -- Link OK Pay OK | Marigold: Backwater
She is in the Backwater, a dead-end reach behind Mill Island. Open water. Strike roll would be d6 +1 (Link), need 5+. Silver fell again to 2.25; 32 scrip would buy 14 Ag right now.
Jobs board: night fire-watch, 8 Ag, no risk.
1. Strike now (50 percent)
2. Swap scrip for silver and buy Optics (18 Ag), strike next turn if she is still in a reach
3. Job: fire-watch, 8 Ag
4. Scout the home channels
or say anything else.

**Player:** This is the real decision. Optics gets me to 67 percent but she might be docked next turn and I'd have four scrip left if it goes wrong. A sure target in a reach at 50 is worth more than a maybe at 67. Launch the Cormorant. Put her on the bottom of the Backwater.

Turn 9 resolved: The Cormorant lifts off the ferry ramp and runs the Backwater at treetop height. Strike: roll 3 +1 Link = 4 (need 5+) miss. Both munitions throw up mud a boat-length short. She returns fire on the way out. Airframe check: roll 1 (cracks on 1-2) the spar splits on landing. Payload spent, Airframe cracked. Command adds 6 scrip.

Turn 10 of 18 | Scrip 42 | Silver 4 | 1 Ag = 2.75 scrip | Ice 6 | Cormorant: Air -- Opt -- Link OK Pay -- | Marigold: North Reach
She slipped out of the Backwater into the North Reach. Ice down to 6. Silver back up to 2.75.
Jobs board: Harrow's sealed packet across the North Reach again, 12 Ag, risk on a 1. She is out there.
1. Job: packet run, 12 Ag, risk on a 1
2. Buy Airframe (24 Ag, you have 4)
3. Buy Munitions (30 scrip)
4. Scout the home channels
or say anything else.

**Player:** status

```
Turn 10 of 18 | Scrip 42 | Silver 4 | 1 Ag = 2.75 scrip | Ice 6 | Cormorant: Air -- Opt -- Link OK Pay -- | Marigold: North Reach
Sparrow: ready. Parts: Airframe 24 Ag, Optics 18 Ag, Datalink fitted, Munitions 30 scrip.
Marigold seen so far: South Reach (T6), Mill Dock (T7, T8), Backwater (T9), North Reach (T10).
```

**Player:** Rebuild costs 24 Ag plus 30 scrip, call it 96 scrip at this rate, and I have 53 worth. Eight turns left, ice at 6. Jobs it is. 1, take the packet run.

Turn 10 resolved: roll 2 (need 2+) success. The Sparrow skirts the far bank; the Marigold's rifleman never gets a line on it. 12 Ag. Command adds 6 scrip.

Turn 11 of 18 | Scrip 48 | Silver 16 | 1 Ag = 3.00 scrip | Ice 5 | Cormorant: Air -- Opt -- Link OK Pay -- | Marigold: West Reach
She is in the West Reach, heading toward Chapel. Ice 5. Silver at 3.00.
Jobs board: night fire-watch, 8 Ag, no risk.
1. Job: fire-watch, 8 Ag
2. Buy Airframe (24 Ag, you have 16)
3. Buy Munitions (30 scrip)
4. Scout the home channels
or say anything else.

**Player:** The fire-watch gives 8 Ag for a turn; swapping 24 scrip gives the same 8 Ag for no turn. Swap 24 scrip for 8 silver, buy the airframe now.

Turn 11 resolved: 24 scrip at 3.00 buys 8 Ag; you hand the Mill yard 24 Ag for a new spar. The fitters work through the night. Command adds 6 scrip.

Turn 12 of 18 | Scrip 30 | Silver 0 | 1 Ag = 3.25 scrip | Ice 4 | Cormorant: Air OK Opt -- Link OK Pay -- | Marigold: Chapel Dock (docked)
She tied up at Chapel Dock. Ice 4 and the shed wall is frosting over. Exactly 30 scrip in hand.
Jobs board: ice-edge photos for Harrow, 10 Ag, no risk.
1. Buy Munitions (30 scrip)
2. Job: ice-edge photos, 10 Ag
3. Strip the Sparrow camera to fit Optics
4. Strike (aborts, she is docked)
or say anything else.

**Player:** 1. Munitions. She docks for one or two turns and then runs; I need to be loaded when she casts off.

Turn 12 resolved: Command signs over a second pair of munitions, no note this time. 30 scrip paid, 6 credited.

Turn 13 of 18 | Scrip 6 | Silver 0 | 1 Ag = 3.50 scrip | Ice 2 | Cormorant: Air OK Opt -- Link OK Pay OK | Marigold: South Reach
A hard freeze overnight: the ice gauge dropped two points to 2. Skim ice at the ferry ramp. The relay has her in the South Reach, under way. Strike roll would be d6 +1, need 5+.
1. Strike now (50 percent)
2. Strip the Sparrow camera to fit Optics, strike next turn
3. Scout the home channels
or say anything else.

**Player:** No more waiting; two more bad ice rolls and she walks. Strike.

Turn 13 resolved: The Cormorant crosses the South Reach out of the sun. Strike: roll 6 +1 Link = 7 (need 5+) hit. Both munitions go through the hold. The Marigold settles in four minutes, bow up, in mid-channel.

```
RESULT: WIN. The Marigold is sunk on turn 13 of 18.
Final: Scrip 6 | Silver 0 | 1 Ag = 3.50 scrip | Ice 2 | Cormorant: Air OK Opt -- Link OK Pay OK | Sparrow intact.
Verdict: buying the Datalink early turned every reach turn into a known window, and the turn-11 scrip-for-silver swap bought back the turn the failed first strike had cost.
Save this one to the library? Give it a name, or say no.
```

**Player:** No save for this one (playtest).

(Per playtest instructions, nothing was appended to played_log.md and nothing was written to library or sessions.)
