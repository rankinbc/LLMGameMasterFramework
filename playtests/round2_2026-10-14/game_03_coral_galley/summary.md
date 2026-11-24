# Game 03 - The Coral Galley - playtest summary

## Game

**Title:** The Coral Galley

**Premise:** You run the Reef, the kitchen line of a pulp-era supper club bolted to a coral shelf. Sixteen waves of Friday diners come down the spiral stair. The line only does what you last told it: it runs your three most recent orders in sequence every wave, and each wave you shout one new order that pushes the oldest out. The Syndicate that bankrolls you reads the League table of six supper clubs at wave 8 and again at the end; the burn (upkeep) grows every wave; a named rival, Rourke's Chop House, poaches your walkouts. Survive the night in the League's top three.

**Rolls and what they became:**

| Roll | Value | Became |
|---|---|---|
| FORM | 15 Programming | The three-slot order queue that runs on its own each wave; you edit one slot (the newest) per turn, so every order lingers three waves. |
| SET | 24 Restaurant kitchen, Friday night | Sixteen seatings, covers rolled per wave, upsells, a columnist, drunk trawlermen. |
| ROLE | 30 A reef | The kitchen line is "the Reef" that waves of diners break against; Line is its integrity. |
| LOOP | 7 Hold a line against waves, repair between | Unserved covers damage the Line; FIX repairs and halves damage; waves grow at 8 and 13. |
| CLOCK | 21 Runway, investors watch | Upkeep is 8 plus the wave number; the Syndicate reviews rank at wave 8 (cash or a higher burn) and keeps only the top three at the end. |
| TWIST | 13 Bank one action | BANK holds a token (the program repeats); SPEND runs the three orders twice in one wave. |
| WIN | 3 Survive the clock | Be open after wave 16 and in the top three. |
| MAP | 12 League table | Six clubs ranked by Buzz; rivals drift and climb after the review. |
| TONE | 3 Pulp adventure | Oilskins, brass gauges, storm doors, a Syndicate envelope, shanghaied dock crews. |

**Rulesheet (verbatim, as played):**

1. The Reef runs your last three orders in sequence every wave. Each wave you shout one new order; the oldest is forgotten.
2. FIRE serves 4 covers at 3 cash each. PUSH serves 3 at 5 each on a roll of 3+ (Line 12+ needs 2+, Line 5 or less needs 5+); a miss serves none and Line -1.
3. FIX costs 6 cash, Line +6 (max 24), and halves this wave's damage. Every unserved cover hits the Line for 1. Line 0 collapses the kitchen.
4. Upkeep each wave is 8 plus the wave number. If you cannot pay, the Syndicate covers it and your Buzz drops 2.
5. Serve the whole wave: Buzz +1. Leave 3+ unserved: Buzz -1 (6+: -2) and Rourke's Chop House poaches +2 Buzz. Rank is your Buzz against five rival clubs.
6. Instead of an order you may BANK (the Reef repeats itself; you hold one token). SPEND the token to run your three orders twice in one wave.
7. Wave 8: the Syndicate reviews the League. Rank 3 or better: +30 cash. Worse: upkeep +6 a wave. PLATTER unlocks: -10 cash, serves 2, Buzz +2, needs Line 8+. Every rival climbs +2 a wave after the review, Rourke +4.
8. Two failed waves in a row let you SHANGHAI a dock crew (-15 cash: every cover served, Line +2). Win: still open after wave 16 and in the League's top three.

(Post-game fix changed line 8 to "Two failed waves in a row, with no token held, let you SHANGHAI..." - see Engine. The as-played engine is kept as engine_as_played.py.)

**Fingerprint:** actions = fire, push, fix, platter, bank, spend, shanghai. Tracked numbers = cash, line, buzz (rank is derived from buzz against five rival values), plus the three-slot order queue as the one list with rules.

## Engine

**Tuning rounds** (300 games per policy unless noted):

| Run | Policy | win_rate | turn_avg | early_end | flags | What changed before this run |
|---|---|---|---|---|---|---|
| 1 | random | 0.03 | 10.4 | 0.60 | SHORT GAMES | First draft: cash 40, Line 10, waves 6/8/10 +d6, FIRE 3, PUSH 7, FIX 8 for +3, upkeep 12 (18 after bad review), runway loss on cash below 0, win = not bottom two. |
| 1 | heuristic | 0.30 | 13.3 | 0.32 | SHORT GAMES | |
| 2 | random | 0.02 | 9.1 | 0.74 | SHORT GAMES | Diagnosis: 203 of 300 heuristic games died of Line collapse with 140 cash on hand (odds not buyable). Pay cut (FIRE 2, PUSH 5, PLATTER 10), FIX 10 for +4, heuristic fixes earlier and spends the token when Line is low. |
| 2 | heuristic | 0.42 | 13.9 | 0.28 | SHORT GAMES | |
| 3 | random | 0.13 | 11.0 | 0.55 | SHORT GAMES | Engine rewritten around tuning constants. Cash 50, Line 12, waves 5/7/9, heuristic buys Line with cash when Line is low. |
| 3 | heuristic | 0.79 | 16.2 | 0.05 | none | |
| sweep A | both, 200 games x 48 combos | - | - | - | - | WIN_RANK knob added. Best random early_end found: 0.27. Conclusion: the two targets (random survives to 12, heuristic loses a third) pull against each other; cash was never the constraint and the League was not a race. |
| sweep B | both, 200 x 32 | - | - | - | - | Rival upward drift and Rourke climb knobs added; Line 16/20, FIX +5/+6. Random early_end still 0.28+. The heuristic was ending rank 1 nearly always. |
| 4 | random | 0.08 | 13.5 | 0.32 | SHORT GAMES | Structural: Line 20, FIX 8 for +6, waves 5/8/12, cash 60, win = top 3, rivals drift up (0.4/0.25) and Rourke +1 a wave after review, Syndicate covers cash shortfall before the review (Buzz -1). PUSH thresholds and heuristic rescaled to Line 20. |
| 4 | heuristic | 0.84 | 16.9 | 0.00 | none | |
| sweep C | both, 200 x 64 | - | - | - | - | PLATTER made a cash-to-Buzz converter (-10 cash, +2 Buzz); all rivals climb after the review. Runway death removed in favour of Buzz -2 on any shortfall (random was dying of cash at 8-11 regardless of Line size). Still 0.18-0.34 random early end. |
| sweep D | both, 200 x 48 | - | - | - | - | Upkeep made 8 plus wave number (+6 after bad review); FIRE 3, FIX 6 for +6; heuristic adds a second PLATTER when rich. Several combos clear all targets; picked waves 4/7/12, Line 24, rival drift 0.5/0.25, rival climb +2, Rourke +2 extra. |
| 5 | random | 0.01 | 14.9 | 0.09 | none | Constants locked, rulesheet synced to the engine. Final pre-play selftest. |
| 5 | heuristic | 0.68 | 16.8 | 0.00 | none | |
| post-game | random | 0.01 | 14.8 | 0.09 | none | Fixes for the two mismatches found in play (rival drift clamp raised from 30 to 99; SHANGHAI only offered when no token is held). |
| post-game | heuristic | 0.59 | 16.8 | 0.00 | none | |

**Final selftest numbers (as played, run 5):** random win 0.01, crashes 0, turn_avg 14.9, early_end_rate 0.09, early wins 0; heuristic win 0.68, crashes 0, turn_min 13, turn_avg 16.8 (budget 16), early_end_rate 0.00, flags none. Post-fix heuristic 0.59.

**Crashes during play:** none. Every `step` returned valid JSON; `status` worked; the illegal-action guard was never tripped because the GM only sent ids from the options list.

**Rulesheet/engine mismatches found during play:**

1. **Rival drift clamp (bug).** `rng.drift(value, 3, 30, ...)` clamps every rival to 30 before the post-review climb is added, so no rival can exceed 32 (Rourke 34). Rule 7's "every rival climbs +2 a wave, Rourke +4" is therefore false from about wave 13 on; Rourke sat at 34 for the last four waves while the sheet promised +4 a wave. Discovered at turn 14 when Rourke failed to move after a wave in which he was owed +6. Fixed post-game (clamp raised to 99); heuristic win rate moved from 0.68 to 0.59.
2. **SHANGHAI hides SPEND.** The options builder uses an if/elif chain so that after two failed waves the shanghai option replaces whichever of bank/spend would have shown, including SPEND while a token is held. Rule 6 says you may spend the token; rule 8 does not say shanghai suppresses it. Hit at turn 14. Fixed post-game by offering shanghai only when no token is held, and the sheet now says so (keeps the option count at five).
3. **PLATTER with no diners still pays Buzz.** Turns 9 and 10: "PLATTER: -10 cash, served 0, Buzz +2." The sheet says "serves 2, Buzz +2" and does not say it needs anyone to serve. Not a contradiction, but it makes a double-run PLATTER on a small wave a pure Buzz purchase. Left as is, narrated as a showpiece going to the bar.
4. Minor: the end-of-game loss text said "cuts the bottom two" after the win was changed to top three; caught in pre-flight before play and fixed.

**Free-text refusal:** tested twice. Turn 3, "Can I hire a second cook to widen the line?" The GM answered in one line that there is no hiring, only orders, the token, or a shanghaied crew, re-showed the four options, and did not run `step`. Turn 14, "Spend the token" when the engine's options did not include `spend`: the GM declined in one line, flagged it as a sheet mismatch, and re-showed the five options. Both times the game did not advance. The `status` command at turn 4 printed the status line and the League without advancing.

## Playthrough

The night opened softly: four seatings of 5 to 10 covers against a line that plates 11 or 12, and the Tribune's columnist happened to visit twice in that window (waves 2 and 5), each time on a wave small enough to hold outright, banking 8 Buzz that no rival could match. By the Syndicate's review at wave 8 the Galley was rank 1 with 187 cash and nothing to spend it on, so the player put the new Reef Platter into the program and started converting cash into Buzz at 10 a wave, accepting walkouts on the biggest seatings. The token became the rhythm of the second half: bank on light or normal waves, spend on rushes, each double run plating 18 and buying 5 Buzz. The sea-wolves wave at 12 forced the one real course correction: the player abandoned the bank/spend alternation to shout FIX, so that every later double run also repaired 12 Line, and that program (FIRE>PLATTER>FIX) carried the line through the 13-to-18-cover late crowd. Two failed waves in a row at 13 opened the shanghai option, which turned out stronger than the token it replaced: 10 covers served for tips, +3 Buzz, +8 Line. Rourke peaked at 34 and stuck there (the clamp bug), the Lantern, Ballroom and Pier Nine bunched at 32, and the Galley finished at 46.

**Result:** win, rank 1 of 6. **Final numbers:** Cash 22, Line 21, Buzz 46, orders PLATTER>FIX>PLATTER. **Turns played:** 16 of 16.

## Decisions

Genuinely hard turns: 5 (turn 5: risk the critic on one PUSH roll or burn the token; turn 8: cut capacity for PLATTER or keep plating; turn 11: spend now or save for wave 13; turn 12: FIX into the sea-wolves versus banking for the token; turn 14: shanghai after the token was blocked). Medium turns: 2 (turn 1 PUSH versus BANK, turn 2 BANK versus FIRE before the critic). Obvious turns: 9 (turns 3, 4, 6, 7, 9, 10, 13, 15, 16, where one option was clearly correct). The hard turns were all in waves 5 to 14; the opening and the last two waves played themselves.

## Emergence

Seven moments where the systems produced something unplanned:

1. Turn 2: the PUSH rolled a 1 (fail, Line -1) on the columnist's wave, but the wave rolled exactly 8 covers so the two FIREs held it anyway; a miss that cost nothing.
2. Turn 8: the first big seating rolled a 6 (13 covers) on the exact wave the player cut capacity to 9 for the Platter; four walked out and Rourke jumped 15 to 22 in one wave from poach plus climb plus drift.
3. Turn 9: the token was spent on a rush that rolled a 1 (11 covers); the second pass served 2, and the second PLATTER served nobody and still paid +2 Buzz.
4. Turn 12: FIX pushed the Line to 25, the cap trimmed it to 24, then the halved sea-wolves damage took 7; the cap silently ate one point of the repair.
5. Turn 13: Rourke's Buzz did not move after a wave he was owed +6 for, which exposed the drift clamp; the rulesheet's late-game race existed only on paper.
6. Turn 14: two failed waves swapped the token for the dock crew; the forced option was better than the plan (+3 Buzz, +8 Line versus +4 Buzz, +12 Line but 6 walkouts).
7. The cash arc: 193 at wave 12 drained to 22 at the close through rising upkeep (19 to 24) and platters; the runway ran out on the last wave almost to the coin, with the shortfall penalty never triggering.

## Problems

- **Broken:** the rival clamp bug (rivals cannot pass 32, Rourke 34) means the late-game League race the sheet promises does not happen; the player led from turn 3 and was never threatened. Fixed post-game. The shanghai/spend option conflict blocked a legal rule-6 action once. Fixed post-game.
- **Boring:** waves 1 to 7 (4 plus a d6 covers against capacity 11 or 12) carry no threat; the only early decision is where to put the single PUSH slot and when to bank. Seven turns of autopilot out of sixteen is too many. The selftest's early_end target under 0.15 for random play drove this softness directly: every attempt at a sharper opening sent random play's early deaths over the line.
- **Repetitive:** the second half fell into bank/spend alternation; once FIX was in the program the double-run was always correct. The sliding queue was interesting mainly at the moments of changing it (turns 8 and 12).
- **Unfair:** none observed; every roll was shown and every loss of Buzz or Line was arithmetic the player could do in advance. The PLATTER-with-no-diners quirk is in the player's favour.
- **Too easy / too hard:** too easy as played. Winning margin was 12 Buzz at rank 1 with 21 Line to spare. Two columnist visits on small early waves were worth 8 Buzz of luck. The selftest predicted a 0.68 heuristic win rate (0.59 with the clamp fixed); the play fell in the winning majority and did not feel like a 60/40 game. The selftest said nothing about the opening being empty because its metrics are about game length and win rate, not about whether early turns carry decisions.
- **Cash sink arrives late:** with FIRE at 3 and PUSH at 5 the first half banks 150 to 190 cash with nothing to buy until PLATTER unlocks at wave 8. The runway clock only bites from about wave 13.

## Fun rating

**6 / 10.** The order-queue lag and the bank/spend rhythm are a genuinely fresh way to run a kitchen, and waves 8 to 15 were a real puzzle with every number on the table: capacity against cover ranges, Buzz against a climbing pack, Line against doubled damage. But the first seven waves played themselves and the League never actually breathed down my neck, so the win felt administered rather than earned.

## Would replay

Yes, once, with the clamp fixed and the opening sharpened (waves 5 plus a d6 from the start, or a critic that only visits after wave 6). I want to try a PUSH-heavy cash opening into a double-PLATTER endgame and see whether the rank race at the fixed climb rates is as close as the 0.59 suggests. Without the opening fix I would not play it a third time.