# Hail Term - playtest summary (game 06)

## Game

**Title:** Hail Term

**Premise:** You are headmaster of the Valley Weather School. Storms queue up over six farming districts and the students go out to one of them a turn; every storm left waiting may deepen a layer (richer to clear, harder to roll), and at layer 4 it bursts over the fields. The board is a day behind: a storm's shown layer is yesterday's and new arrivals show "?", so the students find out the truth on the road. Pell's cloud-seeding wagon announces which storm he will poach next. The bank takes 60 cash as turn 14 opens; the farmers' approval must be 70 or better after turn 20.

**Rolls and what they became:** `FORM=17 SET=60 ROLE=27 LOOP=21 CLOCK=3 TWIST=37 WIN=18 MAP=8 TONE=2`
- FORM 17 Triage: a queue of storms, a 3-slot board, waiting costs (approval drain for stale storms, overflow at -3, Pell).
- SET 60 Weather system over a farming valley: the storms are the cases; six named districts.
- ROLE 27 Headmaster: the Valley Weather School; "tuition day" as the no-send money action; old Agnes the retired headmistress as the loss-streak lever.
- LOOP 21 Dig deeper, each layer riskier and richer: storms deepen layer 1 to 3 while they wait (pay 8/14/22, need 3+/4+/5+), layer 4 bursts.
- CLOCK 3 Debt due on turn N: the bank takes 60 as turn 14 opens; short means closed.
- TWIST 37 Information arrives one turn late: shown layers are yesterday's, new storms show "?"; the semaphore line (midpoint unlock) removes the lag.
- WIN 18 Reach an approval number: 70+ after turn 20.
- MAP 8 One location with 6 districts: Mill Row, Orchard End, Hop Flats, Sheepfold, Fen Bottom, Upper Terraces (flavor only).
- TONE 2 Dry humor: Pell says good morning by parking facing your storm; Agnes does not do invoices.

**Rulesheet (verbatim from the engine docstring):**
1. Each turn do one thing: send the students to one storm, hold a tuition day (+12 cash), or buy gear. Wages cost 3 a turn.
2. Storms queue over six districts. A storm that has waited 2+ turns costs 1 approval a turn. The board holds 3; a fourth pushes the oldest out for -3 approval.
3. A storm has a layer 1 to 3. Sending rolls d6, need layer+2. Success pays 8/14/22 cash and +5/+7/+10 approval. Fail: -2 approval, storm stays.
4. Each turn a waiting storm may deepen one layer (1 in 3; 1 in 2 from turn 10): richer, harder. Layer 4 bursts: -6 approval, storm gone.
5. Reports are a day old: a storm's shown layer is last turn's, and new storms show "?". Students on site learn the true layer.
6. Pell's cloud-seeding wagon names the longest-waiting storm that has sat a day; next turn he takes it if it is still there (-2 approval, no pay).
7. Gear ladder: kites 20, barometer 20 (+1 to every roll each), then from turn 10 the semaphore line 35 (reports same day). From turn 10 storms come faster.
8. The bank takes 60 cash as turn 14 opens. Cash below 0 or approval 0 closes the school. After two failed sends old Agnes clears the longest-waiting storm for 12. Win: approval 70+ after turn 20.

**Fingerprint:** actions = `send` (with a case arg), `tuition`, `gear`, `agnes`. Tracked numbers = cash, approval, the storm board (a list of up to 3 storms with layer/age rules). Status line: `Cash | Approval | Board n/3 | Roll +x`.

## Engine

Selftest = 300 games each policy. Targets: random win < 0.35, heuristic 0.3 to 0.7, early wins 0, early_end < 0.15, heuristic turn_avg >= 15.

| Run | Policy | win_rate | turn_avg | early_end | Flags | What changed before this run |
|---|---|---|---|---|---|---|
| 1 | random | 0.00 | 11.1 | 0.47 | SHORT GAMES | First draft: debt 90, approval 3/5/8, arrivals 1 + 40%, Pell names any oldest storm, waiting -1 per storm per turn, wages 4. |
| 1 | heuristic | 0.00 | 8.3 | 1.00 | TOO HARD, SHORT GAMES | (same) |
| 2 | random | 0.00 | 12.7 | 0.32 | SHORT GAMES | Debt 60; approval 4/6/9; arrivals 1 + 25% (season 1 + 60%); Pell names only storms that sat a day; heuristic reserve formula loosened. |
| 2 | heuristic | 0.00 | 13.4 | 0.30 | TOO HARD, SHORT GAMES | (same) |
| 3 | random | 0.01 | 15.3 | 0.09 | none | Waiting cost only for storms aged 2+; wages 3; heuristic rewritten (kites by turn 6, tuition only when the bank projection is short). |
| 3 | heuristic | 0.25 | 18.8 | 0.07 | TOO HARD | (same) |
| 4 | random | 0.01 | 15.5 | 0.10 | none | Second-storm chance 15% / 50%; overflow -4 to -3; heuristic keeps a 12-cash buffer before gear, projects the bank more conservatively. |
| 4 | heuristic | 0.22 | 20.1 | 0.02 | TOO HARD | (same; heuristic over-tuitioned, 3.4 tuition turns a game) |
| 5 | random | 0.03 | 15.5 | 0.10 | none | Approval 5/7/10; heuristic projects +4 cash a turn with a 2-cash margin. |
| 5 | heuristic | 0.44 | 19.6 | 0.02 | none | (same) |
| 6 | both | 0.03 / 0.44 | 15.5 / 19.6 | 0.10 / 0.02 | none | Docstring-only edits (deepening odds on line 4, "as turn 14 opens" on line 8). Confirmation run, identical numbers. |
| 7 | both | 0.03 / 0.44 | 15.5 / 19.6 | 0.10 / 0.02 | none | After play: fixed the season event string (see mismatch below). Identical numbers. |

Crashes: 0 in every run. early_wins_before_half: 0 in every run.

**Final selftest numbers:** random win 0.03, turn_avg 15.5, early_end 0.10; heuristic win 0.44, turn_avg 19.6, turn_min 8, early_end 0.02; no flags. Breakdown of 300 heuristic games at the final tuning: 132 wins, 107 ended short of 70, 33 bank closures, 18 approval-zero, 10 out of cash. Per-game approval sinks: Pell 15.9, bursts 14.9, overflow 11.2, fails 7.7, waiting 1.5. Action mix: send 4232, tuition 803, gear 534, agnes 18.

**Crashes during play:** none. All 20 steps, the `status` call and the `new` call returned clean JSON.

**Rulesheet/engine mismatch found during play:** the turn-10 event string still said "Two storms a turn from now on" from the round-1 draft, while the sheet (line 7) and the code say storms come faster (a second storm 50% of the time). Text only; fixed after the game and the selftest confirmed identical numbers. Minor cosmetic: with +2 gear a layer-1 storm prints `roll 5 (need 1+)`, which is a correct but silly check line.

**Free-text refusal:** on turn 11 the player typed "Split the students: half to Fen Bottom, half to Upper Terraces." No engine action fits; the GM said so in one line, re-showed the five options and did not advance. The player picked option 1. On turn 4 the free text "the gale, before Pell gets it" mapped cleanly to the send on case 4. The `status` request on turn 9 ran `engine.py status` and printed the same turn and options without advancing.

## Playthrough

The headmaster opened by buying kites with 30 cash and let Pell seed the Hop Flats fog, then cleared a Fen Bottom gale on a 6 to get the tin back above wages. Turn 3 was a true coin flip on a layer-3 hail for 22 and +10; it came up 2, Pell took the storm, and approval sat at 41 with 15 cash. Three stale reports in a row then paid upward: storms shown as layer 1 or 2 turned out a layer deeper on the road and paid 14 and 22, including a drought that needed exactly the 3 the students rolled. The barometer on turn 6 (down to 8 cash) made layer 1 automatic and layer 3 a 3+, and approval climbed to 75 by the start of storm season. The bank window was the hard stretch: the semaphore line was affordable but would have made the 60 impossible, a 1 on an Orchard End drought handed Pell another storm, a layer-3 frost burst the night it was left, and the player chose a guaranteed tuition day over a 94% send rather than risk closing on bank day. The bank took its 60 and left 5 cash, which turned the next two turns into cash survival; a 94% hail and then a 3+ hail for 22 restored both numbers. From turn 15 on every send succeeded, two of them on the exact number needed, a hidden layer-3 fog burst from under a question mark without ever showing a number, and the term ended at approval 115 with 88 cash.

Result: win, approval 115 after turn 20. Final status: Cash 88 | Approval 115 | Board 3/3 | Roll +2. Turns played: 20 of 20. Rolls: 17 sends, 15 successes, 2 fails (turn 3 and turn 10); 2 gear buys; 1 tuition day; Agnes never triggered (no two consecutive fails).

## Decisions

Genuinely hard turns: 8 (turns 1, 3, 6, 10, 12, 13, 14, 15). Each had two options a careful player could defend: kites vs a sure fee at 30 cash; a 4+ coin flip for the best payout; barometer timing against wages; semaphore vs the bank; a layer-3 gamble against a safe fog on the bank approach; a 6% death chance vs a certain tuition day; a 94% send vs Pell's target at 5 cash; a 3+ hail vs two unknowns.

Obvious turns: 12 (turns 2, 4, 5, 7, 8, 9, 11, 16, 17, 18, 19, 20). Most were "send to the shown layer 1 or 2 that Pell is pointed at." Turns 16 to 20 were a victory lap: with +2 and approval over 85 the only question was which storm paid most.

## Emergence

Moments where the systems produced a surprise: 7.
1. Turn 5: the "layer 1" Fen Bottom flood was a layer 2 on arrival and paid 14 instead of 8 (the lag works in your favor as often as against).
2. Turn 7: the Mill Row drought had deepened to layer 3 and the students rolled exactly the 3 they needed for 22 and +10.
3. Turn 10: the semaphore line unlocked in the same window as the bank's 60, so the midpoint unlock was unaffordable precisely when it was useful.
4. Turn 12: the layer-3 frost left behind for the safe play burst that night (-6), which is the exact trade the sheet warned about, happening.
5. Turn 13-14: paying the bank with a tuition day left 5 cash, so the wages clock (3 a night) briefly became the real loss condition even though approval was comfortable.
6. Turn 18: the Hop Flats fog arrived as "?", was secretly a layer 3, deepened and burst without ever showing a number on the board.
7. Turn 18-19: the board emptied and Pell's wagon "sat idle outside the inn" twice; the rival switched off because the player had out-triaged him.

## Problems

- **Too easy in the back half.** Once the barometer landed (turn 6) and the bank was paid, nothing threatened the win; approval ran from 73 to 115 in six turns. The selftest's 0.44 heuristic win rate hides a bimodal distribution: wins land at 100+ and losses in the teens, so the variance is almost entirely early-game and bank-day. The player beat the heuristic by buying both gear items by turn 6 and never over-tuitioning; the heuristic's 33 bank closures and 10 cash deaths are mostly its own caution.
- **The semaphore line is a dead element in practice.** It unlocks on turn 10 and costs 35 while the bank wants 60 on turn 14, so it is unaffordable when it matters and pointless after turn 16. The heuristic buys it in 44 of 300 games. It should unlock earlier, cost less, or the bank should come later.
- **Agnes never appeared.** Needs two consecutive fails; with +2 gear that is rare. Fine as a safety net, but in this run the loss-streak lever was invisible.
- **Repetition.** Twelve of twenty turns were "send to Pell's target." The triage question is real only when a layer 3 sits next to Pell's target or when cash is near zero.
- **Not unfair.** Both fails were honest rolls at stated odds; the one burst that cost something was a known trade. The waiting cost (-1 for storms aged 2+) almost never fired (1.5 per game in selftest) and could be cut from the sheet without anyone noticing.
- **Selftest vs play:** the selftest predicted a 44% win and a 20-turn game; the play was a 20-turn win with no early danger beyond the turn-3 fail. The selftest did not predict how flat turns 16 to 20 would feel, because turn_avg and win_rate cannot see tension.

## Fun rating

7 out of 10. The first ten turns were a tight little economy where the kites-or-fee and barometer-or-wages questions and the day-old reports kept me doing arithmetic every turn, and the bank-day tuition call was the kind of "take the 100% and lose 5 approval" decision I play these for. The last five turns were a formality, and the one unlock I was curious about was never a sane buy.

## Would replay

Yes, once, with a different opening: skip the kites on turn 1, send instead, and see whether the bank window gets genuinely dangerous without the +2 by turn 6. I would also want the semaphore moved so the late game has a real purchase to weigh, otherwise a second replay would feel like the same ten good turns followed by the same ten obvious ones.
