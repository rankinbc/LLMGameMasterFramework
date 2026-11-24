# Greywater Wing - summary

## Game

**Title:** Greywater Wing

**Premise:** You captain a mercenary helicopter wing over Greywater, a sprawling city whose six districts swap places overnight. A Board nobody runs marks every week of your life as a W or an L. Gear comes from weekly lots where the Hollow Wing, a rival whose helicopters have no cockpit lights, circles one lot and bids high. Three hardpoints, never more. Finish the 16-week season above .500 or hit the Long Night, the two-gear job the Board posts for week 16.

**Rolls and what they became:**
- FORM=16 Market: gear items are held positions whose market values drift with the news; lots are priced at market.
- SET=14 Helicopter wing over a sprawling city: Greywater, six districts in a line.
- ROLE=12 Mercenary captain: wing captain flying paid jobs.
- LOOP=15 Bid against rivals for scarce lots: two lots a week, one circled by the Hollow Wing (outbid at listed +6, 5 in 6), one uncontested.
- CLOCK=20 Ratings drop each week you fail to deliver: from week 4, a week with no delivery is an L on the Board.
- TWIST=5 Only carry three things ever: three gear slots; a full rack blocks all buying.
- WIN=16 Finish above .500 or win the final: W > L after week 16, or hit the Long Night.
- MAP=9 Line of 6 nodes that shifts each turn: two neighboring districts swap every night; distance adds to need.
- TONE=7 Weird and uncanny: cold fires, marching crowds, unnamed patients, humming crates, a city that keeps your gear.

**Rulesheet (verbatim):**
1. Each week do one thing: fly a job, buy a lot, or refit. Weeks 1-3 are preseason; from week 4 a week with no delivery is an L on the Board.
2. Fly: d6 against the need shown. Matching gear -3, each refit (20 cash, max 2) -1, +1 per 2 districts from the Yards. Hit: W and the pay. Miss: L, and on a roll of 1 the city keeps the gear you used.
3. Gear: 3 slots, never more, 1 cash a week each. Lots sell at market value, which moves with the news.
4. Two lots a week. The Hollow Wing circles one and bids high: outbidding it costs listed +6 and still loses on a tie (1 in 6). The other lot is yours at listed.
5. Each night two neighboring districts swap places. Jobs stay in their districts, so distances change. Jobs last two weeks.
6. Week 9 on, the Low Fog: jobs need +1 and pay +5. With 3 gear you may fly both jobs in one week for 6 cash.
7. After two missed sorties in a row: Press the Tower, 8 cash for need -2 on this week's sortie.
8. Week 16 is the Long Night, a job that wants two gear types. Win: record above .500 after week 16, or hit the Long Night. Lose: cash below 0.

**Fingerprint:** action ids `fly`, `lot`, `refit`, `tower`, `double`, `finale` (fly and lot carry an index suffix, e.g. `fly:0`, `lot:1`). Tracked numbers: cash, record (W-L), gear (list of up to 3 types with rules). Refits (0-2) is a displayed modifier.

## Engine

**Tuning rounds** (300 games each policy):

| Run | Policy | win_rate | turn_avg | early_end | Flags | What changed before next run |
|---|---|---|---|---|---|---|
| 1 | random | 0.08 | 8.4 | 0.63 | SHORT GAMES | Start cash 20 to 30, upkeep 2 to 1 per gear (bankruptcies everywhere) |
| 1 | heuristic | 0.49 | 13.9 | 0.23 | SHORT GAMES | same |
| 2 | random | 0.27 | 14.6 | 0.22 | SHORT GAMES | Options require 3 weeks of crew pay in reserve before offering any purchase |
| 2 | heuristic | 0.67 | 16.1 | 0.04 | none | same |
| 3 | random | 0.40 | 16.7 | 0.01 | TOO EASY | Base need 4 to 5, Long Night base 6 to 7 |
| 3 | heuristic | 0.72 | 16.5 | 0.00 | none | same |
| 4 | random | 0.17 | 16.5 | 0.03 | none | Path analysis: 89 of 124 heuristic wins came from the Long Night roll, avg season 6-10. Design hole. Added preseason (weeks 1-3 no idle L), Long Night base 7 to 8 |
| 4 | heuristic | 0.41 | 16.3 | 0.04 | none | same |
| 5 | random | 0.18 | 16.6 | 0.03 | none | Record path now 67 vs 37 Long Night but avg season 6.2-8.8; matching gear bonus -2 to -3 |
| 5 | heuristic | 0.35 | 16.4 | 0.04 | none | same |
| 6 | random | 0.27 | 16.7 | 0.02 | none | final |
| 6 | heuristic | 0.55 | 16.8 | 0.00 | none | final |

**Final selftest:** random win 0.27, crashes 0, early_wins_before_half 0, early_end_rate 0.02, turn_avg 16.7. Heuristic win 0.55, crashes 0, early_wins_before_half 0, early_end_rate 0.00, turn_avg 16.8. Heuristic win paths: 136 record, 30 Long Night; losses 128 season, 6 grounded. Average season 8.2-7.8. All six action ids used by the heuristic (fly 2873, lot 852, double 428, refit 373, finale 160, tower 84 over 300 games).

**Crashes during play:** none. Sixteen steps, one status call, one options call, all clean.

**Rulesheet/engine mismatches found in play:**
- The crew-pay reserve filter is not on the sheet. It hid the Gun pod on turn 3 (cash 21 vs 17 + 9 reserve) and the double sortie on turn 13 (cash 17 vs 6 + 12). The GM had to explain it in a line each time. Should be on the sheet or dropped.
- Minor bug: the reserve formula uses len(gear) + 1 even when the rack is full, so a full rack demands 12 cash in reserve rather than 9.
- Line 3 says "Lots sell at market value", which a player can read as "you can sell gear". There is no sell action. Wording should be "Lots are priced at market value".
- Turn 1 to 2: the news announced a marching crowd in Ninth Market but no job appeared because the board was full. News does not always produce a job; the sheet does not say that.
- Line 2's "+1 per 2 districts" is dist // 2; the option labels show the computed need so this never confused the player.

**Free-text refusal:** On turn 3 the player typed "Buy the Gun pod for 17, I want three types before the fog." The GM ran `options`, found no lot action, said so in one line with the reason (cash short of listed plus reserve), re-showed the two options and did not advance. Worked as the skill specifies.

## Playthrough

The wing used its preseason to outbid the Hollow Wing for a Litter rig, then banked two easy crate runs from its own district (the Yards moves with you, so Yards jobs are always 0 away). Week 4's outbid for a Bambi bucket hit the 1-in-6 tie and cost an L for nothing; week 6 filled the rack with an uncontested Gun pod. A refit in week 8 ahead of the fog set up the back half, but the first double sortie split 1-1 and the failing roll was a 1, so the city kept the Gun pod. A second refit in week 11 was followed by the Board posting a Long Night that wanted exactly the Gun pod the city had eaten and the bucket the tie had denied. The player bought the bucket to go 6-6, then rolled another 1 on an 83 percent patient run and lost the Litter rig, dropping to 6-7 with three weeks left. Three straight need-2 sorties followed, the last one a hot crate that spawned next door in week 16, and the wing declined the 33 percent Long Night to finish 9-7.

Result: WIN, season 9-7, above .500. Final numbers: Cash 78 | Record 9-7 | Gear Sling / Bambi bucket / - | Refits 2. Turns played: 16 of 16.

## Decisions

16 turns. Genuinely hard: 7 (turns 4, 6, 8, 9, 11, 12, 15: buy-and-take-an-L versus fly-a-coin-flip, refit timing before the fog, double versus single, bucket versus record, fire-now versus Gun-pod-for-the-Long-Night). Obvious: 9 (turns 1, 2, 3, 5, 7, 10, 13, 14, 16, all "fly the need-2 job"). The hard turns cluster in the midgame; the last four turns were forced by the record.

## Emergence

6 moments where the systems produced a surprise:
1. Turn 4: the 1-in-6 auction tie landed (Hollow Wing 19 vs 18), an L with nothing bought, from a 2-0 start.
2. Turn 9: the fog unlocked the double sortie, the first double split 1-1, and the 1 destroyed the Gun pod the same week the fog made gear matter most.
3. Turn 9 night: the Yards itself traded places with Spire, so the hangar moved and a far patient became a next-door need-2 job.
4. Turn 12: the Board's Long Night wanted precisely the two gear types the player had lost or been denied, turning the "final" into a long shot and forcing a record-path commitment.
5. Turn 13: a 1 on an 83 percent run took the Litter rig and dropped the wing under .500 with three weeks left.
6. Turn 16: the hot crate spawned one district over at need 2, so the player declined the Long Night and won on the record instead; the season's final was skipped as the correct play.

Plus one learned trick: Yards jobs are always 0 away because the hangar district moves with the line.

## Problems

- **Harsh gear loss.** The roll-of-1 rule fired on 2 of 9 matched sorties (1 in 6 expected, so unlucky but not rare). Each loss cost 15-19 cash of gear plus the L. It created the drama, but twice in one game felt punishing, and the selftest cannot see feel.
- **Thin auction.** LOOP 15 is the weakest ingredient: one bid level, 5 in 6 to win, and the tell is deterministic. The "bid against rivals" verb is really "pay a 6-cash tax and roll a 1-in-6". The selftest flagged nothing because the rival only costs cash, not wins.
- **Hidden affordability filter.** The reserve rule hides options the sheet implies exist (turn 3, turn 13). Not broken, but the sheet should say it.
- **Repetitive late game.** Once two refits land, every matched job is need 2 and the last four turns were "fly the 83". The fog's +1 is fully cancelled by two refits, so the escalation ends up flat for a built-out wing.
- **Long Night lottery.** Selftest showed heuristic games at 1-15 or 2-13 winning on a 1-in-6 Long Night roll. In this game the Long Night was correctly declined, but the rule can hand a bad season a win.
- **Sheet wording.** "Lots sell at market value" suggests selling; news that produces no job when the board is full.
- **Difficulty versus prediction.** Selftest predicted heuristic 0.55 with an average 8.2-7.8 season and most wins on the record path; the actual game was a 9-7 record win with a thoughtful player, which matches. Not too easy, not too hard. The selftest did not predict how much of the back half would be forced play.

## Fun rating

7/10, as the player. The economy-versus-record tension (every purchase is an L, so you buy from strength and fly from weakness) is exactly the CS16 eco-round feeling, and the swapping districts plus the hangar moving gave real "wait for the city to come to me" play. The auction is a tax rather than a contest, and the roll-of-1 gear loss turned two good decisions into setbacks that felt more like the dice than the system.

## Would replay

Yes. The seed changes the starting gear, the line, the news and which two types the Long Night wants, and there is an obvious strategy to test next time: refit twice in preseason and never pay the Hollow Wing. I would want the auction to have a second bid level and the roll-of-1 rule to only bite on contested-gear types, but the core loop is worth another 16 weeks.
