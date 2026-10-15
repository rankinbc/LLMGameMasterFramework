# Trophy Route - playtest summary (game 10)

## Game

**Title:** Trophy Route

**Premise:** You are the mayor. The hostile council has ruled that the Centennial Trophy, a two-ton glass bus from the sister city, must reach City Hall on the ordinary No. 6 in regular service, with passengers, by the end of the month. The bus line is the dungeon: five stops, each with a hidden crush crowd and a hidden rowdy crowd that storm the trophy on arrival. You post buses and inspectors at stops ahead (the traps and creatures), hold to earn cash and morale, or pull postings back, while Councillor Hatch rallies every turn at the least-guarded stop ahead and roadworks shuffle the stop order. Dispatch only reports averages. The drivers strike at morale 0.

**Rolls and what they became:**

| Roll | Value | Became |
|---|---|---|
| FORM | 19 Dungeon keeper | The line is the dungeon; crowds are the incoming parties; postings are traps and creatures; the trophy is the heart that moves. |
| SET | 55 City bus network | The No. 6 line: Depot, University, Stadium, Hospital, Market, City Hall. |
| ROLE | 26 Mayor with a hostile council | You are the mayor; the council passes austerity at turn 8; Councillor Hatch is the rival. |
| LOOP | 32 Open, hold, or close one position as news lands | Post guards (open), hold (normal service), pull guards (close); roadworks and Hatch's tell are the news. |
| CLOCK | 14 Crew morale, mutiny at zero | Drivers' morale; strike at 0. Heckles, austerity shortfalls, express and pulls drain it. |
| TWIST | 38 You only ever see averages | Dispatch reports crush and rowdy averaged over stops ahead and over the next two; a stop's true numbers are revealed only on arrival. |
| WIN | 7 Deliver a cargo intact | The trophy starts at 100 and must arrive at 70+. |
| MAP | 9 A line of 6 nodes that shifts each turn | Depot plus 5 stops; roadworks swap two stops ahead with 50 percent chance per turn. |
| TONE | 9 Workplace comedy | Dispatch office, tea fund, hi-vis inspectors, a councillor with a megaphone. |

**Rulesheet (verbatim):**

1. The Centennial Trophy (a two-ton glass bus) rides the No. 6 from the Depot through 5 stops to City Hall. Roadworks swap two stops ahead about every other turn; the order is always shown.
2. Each turn do one thing: advance one stop, post a bus (10 cash) or inspectors (8 cash) at any stop ahead, pull guards off a passed stop (+6 cash, morale -1), or hold (+8 cash, morale +2).
3. Every stop has a hidden crush crowd (up to 7) and a hidden rowdy crowd (up to 8). A bus absorbs 4 crush, inspectors absorb 4 rowdy. Two postings per stop at most.
4. On arrival the drivers roll d6 + 2 against the uncovered crowd. Short by N: trophy -5 x N, morale -1. Held: cash +8, morale +1.
5. Dispatch only ever reports averages: crush and rowdy averaged over all stops ahead, and over the next two. Some days the school run pays a 5 cash windfall.
6. Councillor Hatch rallies every turn at the stop ahead with the fewest guards (nearest on ties): rowdy +1 there. From turn 8 her rallies add 2, she heckles the drivers when she is at the next stop (morale -1), and austerity docks 3 cash a turn (morale -1 instead when the kitty is under 3).
7. Morale 0 is a strike and trophy 0 is shards: both lose. Each overload unlocks one Ride Along (morale +2, next roll +3).
8. From turn 8 you may run Express: two stops in one turn, morale -2. City Hall takes delivery from turn 12. Win: trophy 70+ delivered by turn 16.

**Fingerprint:** actions = advance, post_bus, post_insp, pull, hold, express, ride. Tracked numbers = cash, morale, trophy (the line with its postings is shown as the fourth status field; hidden per-stop crush/rowdy lives in `hidden`).

## Engine

**Tuning rounds** (300 games each policy):

| Run | Policy | win_rate | turn_avg | early_end | Flags | What changed before the next run |
|---|---|---|---|---|---|---|
| 1 | random | 0.03 | 11.6 | 0.51 | SHORT GAMES | Game resolved too fast: one guard per stop was enough and cash never bound. Damage 10 to 5 per short point, win threshold 50 to 70, crowd heats raised, start cash 30 to 24, hold morale +1 to +2, heuristic now estimates the next stop from the dispatch averages and posts a second guard when the estimate exceeds 3. |
| 1 | heuristic | 0.39 | 10.4 | 0.97 | SHORT GAMES | (same) |
| 2 | random | 0.02 | 11.7 | 0.53 | SHORT GAMES | Trace found a trap: austerity (-3, applied after the action) pushed cash below 0 and ended the game by "council takeover" after a legal posting. Also the economy could not fund two guards per stop and morale drained from turn 1 via heckles. Austerity now costs morale instead when cash is under 3; cash-below-0 loss removed; start cash 12; fares +8 to +6; heckle only from turn 8; heuristic posts one right-type guard then a second only when estimate exceeds 3. |
| 2 | heuristic | 0.00 | 12.4 | 0.44 | TOO HARD, SHORT GAMES | (same) |
| 3 | random | 0.02 | 12.0 | 0.51 | SHORT GAMES | Trace found Hatch's rallies piling without limit (City Hall reached rowdy 17, unbeatable by any posting) and pull/hold churn under a starved economy. Caps: crush 7, rowdy 8 (two right guards always hold a stop); start cash 20; bus 10 / inspectors 8; hold +8; fares +8; pull refund 6; heuristic pulls only at morale 8+. |
| 3 | heuristic | 0.00 | 15.7 | 0.00 | TOO HARD | (same) |
| 4 | random | 0.11 | 12.9 | 0.38 | SHORT GAMES | Random's early endings were early deliveries at turns 8 to 11, not deaths. Added a fiction-fitting gate: City Hall takes delivery from turn 12 (advance and express to City Hall blocked before then). |
| 4 | heuristic | 0.57 | 15.4 | 0.00 | none | (same) |
| 5 | random | 0.13 | 14.4 | 0.03 | none | Usage count showed ride chosen in 1 of 300 heuristic games. Streak made cumulative (two overloads total); sheet wording fixed (roadworks 50 percent, windfall event added to line 5). |
| 5 | heuristic | 0.57 | 15.4 | 0.00 | none | (same) |
| 6 | random | 0.15 | 14.5 | 0.02 | none | ride still 5 of 300: in sensible play the second overload is almost always the final arrival. Ride now unlocks after each single overload. |
| 6 | heuristic | 0.57 | 15.4 | 0.00 | none | (same) |
| 7 (final) | random | 0.19 | 14.5 | 0.02 | none | - |
| 7 (final) | heuristic | 0.54 | 15.4 | 0.00 | none | - |

**Final selftest numbers:** random: wins 58/300 (0.19), crashes 0, turn_min 8, turn_avg 14.5, turn_max 17, early_wins_before_half 0, early_end_rate 0.02, flags none. Heuristic: wins 163/300 (0.54), crashes 0, turn_min 12, turn_avg 15.4, turn_max 17, early_wins_before_half 0, early_end_rate 0.00, flags none. Heuristic action usage across 300 games: advance 300, post_insp 300, post_bus 299, hold 297, pull 285, express 140, ride 69.

**Crashes during play:** none. Every step returned valid JSON; options filtered correctly (post options vanished when cash was short; advance to City Hall was withheld until turn 12; express never appeared because the only two-stop run available ended at City Hall before turn 12).

**Rulesheet/engine mismatches found during play:** none in the numbers. One presentation gap: the rulesheet does not say that a posting stays with its stop when roadworks move the stop; the Present block added that in one line, which the "new information through play" rule allows, but it belongs on line 1.

**Free-text refusal:** at turn 5 the player asked to lean on or bribe Hatch. The GM refused in one line ("no action for leaning on Hatch; the only way to move her is where you post guards"), re-showed the five options, and did not call the engine. The player then chose advance. Clean.

## Playthrough

The player opened by reading the next-two averages against the known stop types and posted inspectors at University, then advanced cleanly (roll 5, need 3+). Inspectors went to the Stadium after Hatch had rallied there twice, and the roadworks immediately swapped the Hospital ahead of the Stadium, with Hatch pivoting to the now-unguarded Hospital the same turn. A quick bit of arithmetic on the next-two rowdy total showed the Hospital's rowdy was about 1, so a bus went there, and the arrival held on a roll of 1 (+2 = 3, need 3+), the closest call of the game. The Stadium held on a 4. At turn 7 the player posted a bus at the Market knowing it would push Hatch onto City Hall for the rest of the game; she stayed there seven turns and capped City Hall at crush 7, rowdy 8. Inspectors joined the bus at the Market, it held with uncovered 1, and from turn 10 the averages were exact because only City Hall remained. Cash ran to 1 and austerity hit morale instead, so two holds (both paid out windfalls) rebuilt the kitty, the City Hall bus went up at turn 13, and the final arrival with uncovered 7 rolled a 6 (+2 = 8, need 7+) for a clean delivery.

Result: WIN, turn 14 of 16. Final numbers: Cash 16, Morale 9, Trophy 100. Turns played: 14 engine steps (plus one refused free-text request and one status call).

## Decisions

Genuinely hard turns: 5 (turn 1: which guard type at University with 20 cash, or hold first; turn 3: post at Stadium versus advance into Hatch's double rally; turn 4: respond to the roadworks swap with a bus, advance unguarded, or wait; turn 7: guard the Market knowing it sends Hatch to City Hall, versus guarding City Hall first to keep her heckling at a stop already covered; turn 10: inspectors at City Hall at cash 9 and eat the austerity morale hit, or hold first).

Obvious turns: 9 (turns 2, 5, 6, 8, 9, 11, 12, 13, 14). From turn 10 on, with B+I at City Hall guaranteeing at least 80 on arrival, every remaining turn was a known sequence of hold, post, advance.

## Emergence

1. Turn 3 to 4: one turn after posting inspectors at the Stadium, roadworks swapped the Hospital in front of it, and Hatch pivoted the same turn to the newly next, unguarded Hospital. Map shift and rival policy combined to punish the posting's timing.
2. Turn 4: the averages were decodable. Next-two rowdy 3.0 across Hospital and Stadium, with the Stadium known to be 5 or more, pinned the Hospital's rowdy at about 1, which made the bus (not inspectors) the right call. The twist produced a real deduction.
3. Turn 5: Hospital arrival held on roll 1 (+2 = 3, need 3+), zero margin.
4. Turns 7 to 13: steering Hatch. Guarding the Market sent her to City Hall, where she stayed seven straight turns, turned the finale into a maxed-out boss, and heckled the drivers every turn from the Market onward. The player caused the boss with their own placement, then planned against the cap.
5. Turn 10: with one stop left, "averages only" collapsed into exact numbers (crush 7.0 / rowdy 8.0), so the twist handed over the final answer.
6. Turn 10 to 11: austerity found the kitty at 1 and took morale instead, the fallback rule firing exactly where the trace had found the old bankruptcy trap.

Count: 6 surprise moments, 4 of them from systems interacting (map shift x rival, averages x stop types, placement x rival policy, austerity x cash floor) and 2 from dice.

## Problems

- **Pull is strictly dominated by hold.** Pull gives +6 cash and -1 morale; hold gives +8 cash and +2 morale. The player said so at turn 11 and never pulled. The selftest usage count (pull in 285/300 heuristic games) hid this because the heuristic was coded to pull; the pre-flight dead-element check passed on usage, not on value. Fix: refund the full posting price (10 or 8) and make the morale cost the real trade, or make pull free of a turn (combine it with a post).
- **The finale is a solved lock-in.** With the caps at crush 7 / rowdy 8 and two postings covering 8, uncovered is at most 7, the worst roll costs 20, and a trophy still at 100 lands at 80 or better. Once cash for two City Hall postings was secured (turn 10), the last five turns had no risk. The caps were added to make odds buyable, but they also make a full-health finale unlosable. Fix: win threshold 80, or let City Hall's crowd exceed the cap through Hatch's final rallies, or let the crowd grow while the trophy waits at the Market.
- **Express never appeared.** With only Market and City Hall ahead from turn 7, express was gated by the turn-12 City Hall rule, so the midpoint unlock was invisible this game. The selftest shows it used in 140/300 heuristic games, so it is not dead, but a fast opening makes it moot.
- **Morale was never under threat** (minimum 6). The CLOCK roll (crew morale) was soft for a competent player: hold's +2 outruns Hatch's -1 heckle. For a struggling player it bites (random strikes in 35/300 games). Making the heckle -2 from turn 12, or making each posting cost 1 morale (drivers resent reassignment), would make the clock felt by good players too.
- **GM process issue:** turns 11 and 12, and 13 and 14, were run as pre-committed pairs. The turn-12 windfall (+5) made a bus affordable a turn earlier than the GM had assumed; the player's hold at 12 was defensible (cash buffer against austerity) but was not freshly decided after seeing the windfall. Not an engine problem, a harness discipline problem.
- **Four windfalls in 14 turns** (turns 2, 4, 12, 13) at 20 percent odds is lucky, not broken. It made the back half easier than par.
- **Compared with the selftest:** the selftest predicted a 54 percent heuristic win with games ending around turn 15; the actual game won at turn 14 with zero overloads, better than par, consistent with the heuristic's main loss mode (a damaged final arrival) being removable by a B+I finale with a full-health trophy. The selftest did not predict the dominated pull action or the lock-in, because those are value judgments, not statistics.
- Not boring in the first half; repetitive in the second (hold, post, advance with known numbers). Not unfair at any point: every number that hurt was announced one turn ahead.

## Fun rating

7 out of 10. The first seven turns were exactly my kind of game: reading two averages against known stop types, watching the roadworks and Hatch's megaphone push back on my postings, and the roll of 1 that held by nothing. The back half was arithmetic I had already done, and once I saw City Hall was a guaranteed 80 or better the last five turns were just waiting for cash.

## Would replay

Yes, once or twice. I want to try the opposite line: guard City Hall first to keep Hatch heckling at a stop I have already covered, and see whether an express run through the middle is worth the morale. But I would want the pull refund fixed and the finale given some risk before a third play.
