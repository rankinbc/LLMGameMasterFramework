# Fog Lots - playtest summary (game 05)

## Game

**Title:** Fog Lots

**Premise:** You are the mayor of Gullhaven, a fog-bound island whose only link to the mainland is a municipal airstrip. Every week the fishing co-op puts one lot under sealed bid against Councillor Vane, chair of the hostile council: a fuel tanker, a lease on one of the airport's six districts, or (once, at week 8) the mainland Mail Contract. Districts you lease fly on their own and mature after three weeks, each flight burning fuel and paying cash. Bess, the runway, is alive and resents work: four or more flights a week and she may heave. Vane's clerk leaks her bid mode each week but is wrong one week in six. Fuel runs the clock (lights burn 1 a week; fuel 0 is loss). At week 16 the council's auditor lands and wants cash 90+ and 4+ districts leased.

**Rolls and what they became:**

| Roll | Value | Became |
|---|---|---|
| FORM | 4 Blind auction | Sealed bid each week (8/14/22) against Vane; ties to Vane; losing bid costs nothing |
| SET | 38 Airport control tower | Gullhaven municipal airstrip; the tower keeps the lights reserve |
| ROLE | 26 Mayor with a hostile council | Councillor Vane is the rival bidder; council levy 4 a week; impeachment at cash below 0 |
| LOOP | 36 Plant or tend one plot; rest grows alone | Leased districts fly and mature on their own; tend_plot matures one now; tend_bess calms the runway |
| CLOCK | 1 Fuel runs out | Lights burn 1 a week; flights burn 1 each; fuel 0 is loss; tower keeps 5 back |
| TWIST | 27 Sentient resource resists use | Bess the runway: max 5 flights a week, heaves on 1-2 at 4+ flights unless tended |
| WIN | 17 Balance budget, reviewer satisfied | Auditor at week 16: cash 90+ and 4+ districts |
| MAP | 8 Single location, 6 districts | Terminal, Apron, Hangar, Fuel Farm, Cargo Shed, Tower Cafe |
| TONE | 8 Cozy with teeth | Thermos and wire brush for Bess; ties go to the chair |

**Rulesheet (verbatim):**
1. Each week one lot goes to sealed bid against Councillor Vane: bid 8, 14 or 22 cash, or pass and tend instead. Higher bid wins and pays; ties go to Vane. A losing bid costs nothing.
2. Lots are tankers (+8 fuel) or leases on one of the airport's 6 districts. A leased district flies 1 flight a week, 2 once it matures after 3 weeks (or tend it to mature now).
3. Each flight burns 1 fuel and pays 8 cash; the runway lights burn 1 fuel a week regardless and the tower keeps 5 fuel back for them; fog weeks (rolled, shown) ground all flights. Fuel 0: the airport goes dark, you lose.
4. Bess the runway is alive and resents work: she takes at most 5 flights a week, and on 4 or more she heaves on a roll of 1-2 (closed next week, -10 cash). Tend her (10 cash) and she tolerates anything for 3 weeks.
5. Council levy 4 cash a week. Cash below 0 is impeachment: you lose.
6. Vane's clerk talks: each week you hear whether her next bid will be HIGH (11-21) or LOW (6-11). The clerk is right 5 weeks in 6.
7. Lose two auctions in a row and the fishing co-op sells you an emergency drum: 3 fuel for 12 cash.
8. Week 8: tankers shrink to 5 fuel, Vane's high bids reach 24, and the Mail Contract lot appears once (+1 flight a week paying 12). Week 16 the auditor comes: win with cash 90+ and 4+ districts leased.

**Fingerprint:**
- Action ids: `bid_low`, `bid_mid`, `bid_high`, `tend_bess`, `tend_plot`, `drum` (plus `wait` as an emergency fallback when nothing is affordable; never surfaced in play)
- Tracked numbers: `cash`, `fuel`, `districts` (list of leased districts with level/age rules)
- Signature detail: Bess the runway (thermos and wire brush) and Vane's leaky clerk.
- Rival policy: Vane bids HIGH (2d6+9; 2d6+12 after week 8) with p 0.35, 0.75 on a tanker when your fuel is 4 or under, 0.6 on the mail, +0.15 after week 8; otherwise LOW (d6+5). Ties go to her. The clerk reports her mode truthfully 5 times in 6.

## Engine

**Tuning rounds (300 games each policy):**

| Run | Policy | win_rate | turn_avg | early_end | Flags | What changed before this run |
|---|---|---|---|---|---|---|
| 1 | random | 0.00 | 6.4 | 0.96 | SHORT GAMES | First draft: fuel 8, tankers 6/4, no lights reserve, levy 5 |
| 1 | heuristic | 0.00 | 6.4 | 1.00 | TOO HARD, SHORT GAMES | (same) |
| 2 | random | 0.00 | 11.4 | 0.53 | SHORT GAMES | Fuel start 12, tankers 8/5, lights reserve 2, fuel-first heuristic rewrite |
| 2 | heuristic | 0.04 | 14.7 | 0.16 | TOO HARD, SHORT GAMES | (same) |
| 3 | random | 0.00 | 12.7 | 0.39 | SHORT GAMES | Reserve 3; heuristic bids high when fuel is urgent regardless of tell, values leases until 4 districts, stops tending Bess at low fuel |
| 3 | heuristic | 0.22 | 16.6 | 0.02 | TOO HARD | (same) |
| 4 | random | 0.01 | 15.0 | 0.15 | none | Levy 5 to 4, reserve 5, fuel start 14, heuristic thresholds keyed to usable fuel (fuel minus reserve) |
| 4 | heuristic | 0.34 | 16.9 | 0.00 | none | (same) |
| 5 | random | 0.02 | 15.2 | 0.13 | none | Fuel start 15; heuristic stops buying fuel it cannot burn before the audit |
| 5 | heuristic | 0.42 | 17.0 | 0.00 | none | (same) |
| 5b | heuristic | 0.42 | 17.0 | 0.00 | none | Rulesheet line 4 wording only (added the 5-flight cap the engine already enforced) |

Diagnosis across rounds: round 1 died because auto-flights flew fuel down to the last unit and the lights killed every game by turn 6; the lights reserve plus bigger tankers fixed the clock, after which the remaining heuristic losses were audit cash (avg 76, then 90, then 97 against the 90 target) rather than fuel.

**Final selftest numbers:**
- random: 7/300 wins (0.02), crashes 0, turn_min 4, turn_avg 15.2, turn_max 17, early_wins_before_half 0, early_end_rate 0.13, flags none
- heuristic: 127/300 wins (0.42), crashes 0, turn_min 14, turn_avg 17.0, turn_max 17, early_wins_before_half 0, early_end_rate 0.00, flags none
- Heuristic end reasons: 168 auditor unsatisfied (cash short in most), 127 wins, 3 impeached, 2 dark lights

**Crashes or rulesheet/engine mismatches found in play:** no crashes, no illegal-action errors. Pre-flight caught one sheet gap (the engine caps Bess at 5 flights a week; the sheet did not say so) and the sheet was fixed before presenting. Two soft mismatches noticed during play that did not affect the result: (1) the Mail Contract is implemented as "+4 cash whenever at least one flight flies" rather than a distinct 12-cash flight, so under fuel throttling the mail bonus pays even when fewer flights than potential fly; (2) the "Only X of Y flights could be fuelled" line reports potential 7 to 9 although Bess caps at 5, which is accurate but reads oddly.

**Free-text refusal:** on turn 5 the player asked to ground the Terminal flights to save fuel and bid 14. The GM refused in one line (no action grounds your own flights; the tower holds the reserve itself), re-showed the five options and did not call the engine. The player then chose bid 14 and the turn advanced normally.

## Playthrough

The mayor opened by tending the Terminal for a free second flight instead of chasing the Apron into a HIGH tell, then bought the first tanker at 14. The clerk's first lie cost the Hangar at 14 against Vane's 17, and from then on every lease was bought at 22. Three cheap tankers at LOW tells built a fuel cushion, Bess was tended on week 7 just as the Cargo Shed pushed flights to 4, and the Mail Contract was won on week 8 by a single cash (22 against Vane's 21, after the clerk said LOW). The second half turned into a fuel famine: tankers shrank to 5, the Tower Cafe and Fuel Farm leases drained cash, and three fog weeks landed in weeks 10, 12 and 14. A 22-22 tie went to Vane on week 12 with fuel at 4, leaving cash exactly 90 and three weeks of lights. Two 22 bids bought survival, and on the last two turns the arithmetic was explicit: pass with a free 8-cash bid and fly three safe flights, then bid 14 rather than 22 so that a Bess heave after four flights could not drop the audit below 90. Vane bid 11, four flights flew, Bess rolled a 4 and held.

Result: WIN, auditor satisfied. Final numbers: Cash 100 | Fuel 5 | Districts 4/6. Turns played: 16 of 16.

## Decisions

- Genuinely hard turns (two defensible picks, numbers worth working): 7 (turns 1, 4, 7, 8, 12, 15, 16).
- Obvious turns (one clearly right pick): 9 (turns 2, 3, 5, 6, 9, 10, 11, 13, 14).
- Mid-game turns 9 to 14 were mostly "bid 22 on whatever is in the envelope"; the real decisions clustered at the start and in the last three weeks.

## Emergence

Moments where the systems produced a surprise: 6.
1. Turn 3: the clerk's first lie (LOW, Vane bid 17) lost the Hangar and changed the player's posture for the rest of the game (22 on every lease).
2. Turn 8: Mail Contract won 22 to 21 after a LOW tell; one cash either way on the most valuable lot in the game.
3. Turn 12: Vane bid exactly 22 on a tanker while the player sat at fuel 4; the tie rule handed it to her and left cash on 90 with three weeks of lights. Her squeeze-when-low policy combined with the tie rule in a way the player could feel but not see.
4. Fog landed in weeks 10, 12 and 14, all inside the fuel-starved stretch, compounding the famine.
5. The lights reserve (5) plus the 5-flight cap meant four mature districts (potential 9) flew 0 to 4 a week; the leases bought for the auditor were nearly dead weight for income. Every solution created the next problem.
6. Turn 16: the Bess heave check resolving after the last week and before the audit made the bid size matter (14 leaves a 10-cash cushion, 22 does not), a rules interaction neither the sheet nor the player anticipated until the maths was done.

## Problems

- Not broken: no crashes, no illegal actions, no sheet/engine disagreements with teeth. The refusal path worked.
- Bid tiers partly collapse after the midpoint. Once the clerk had lied, every important lot was bought at 22; bid_low was used once as a free pass and bid_mid only when the margin maths demanded it. The 8 tier needs a reason to exist beyond "costs nothing to lose" (for example a rebate on a losing bid or a discount on the next lot).
- The plant-and-tend loop is thin. tend_plot was used once (turn 1), tend_bess once (turn 7); after that the lot was always worth more than a tend. The LOOP roll is recognisable but secondary to the auction.
- Late districts are mostly for the auditor's checklist, not income. The reserve of 5 was needed to keep random play alive but makes a four-district airport fly 2 to 4 flights a week. A smaller reserve with a visible "weeks of lights left" warning might serve better.
- Fog at 15 percent with no counterplay felt like variance rather than decision when it stacked with the fuel edge (three fogs in five weeks).
- Difficulty: the selftest predicted a 0.42 heuristic win rate and a last-week finish; the game ended on turn 16 with cash 100 against 90. Tight, fair, and consistent with the prediction. Not too easy, not too hard.

## Fun rating

7/10. The sealed-bid-with-a-leaky-clerk loop was tense, Vane's 22-22 tie at my lowest fuel was a proper villain moment, and the last three turns were real arithmetic that I got right. The middle stretch was mostly paying 22 for whatever showed up while my new districts sat on the apron with no fuel, and the tend actions stopped mattering after week 7.

## Would replay

Yes. The seed changes the lot order and which weeks the clerk lies, and I want to test a different plan: fewer leases early, a bigger fuel bank before week 8, and whether 14-bids on LOW tells can be trusted across a whole run once Vane's late purse is in play.
