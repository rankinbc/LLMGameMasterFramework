# Hired Knives - playtest summary

## Game

**Title:** Hired Knives

**Premise:** You captain a freelance kitchen brigade on a street of seven restaurant kitchens. The critic Ines Volk eats one dinner a night, choosing the loudest kitchen she has not tried, with one hidden habit her column hints at. Rooney's rival brigade, the Copper Pans, holds kitchens too and wants the same thing: to be the crew in her kitchen on Friday, when she returns to the place that impressed her most. Every piece of news on the street (the Buzz board, where she ate, what Rooney did) reaches you one service late. Win by holding her Friday kitchen, passing the service, and walking the crew out paid.

**Rolls and what they became:**
- FORM=6 Pursuit: Volk moves by a hidden rule (loudest unvisited kitchen plus one secret habit) and you steer her by raising Buzz where you stand.
- SET=24 Restaurant kitchen on a Friday night: the whole week builds to Friday dinner, which decides the game.
- ROLE=12 Mercenary captain: a kitchen brigade for hire that takes over kitchens by the night.
- LOOP=18 Capture and hold nodes: seven kitchens; take from the house, raid from Rooney, reinforce with a third cook.
- CLOCK=6 Rival racing to the same prize: Rooney expands, pushes Buzz, and raids starred kitchens Thursday and Friday lunch.
- TWIST=37 Information one turn late: the Buzz board you see is one service stale; Volk's and Rooney's moves arrive next service; a take or raid on a kitchen whose holder changed bounces.
- WIN=2 Reach a location and get out: be in her Friday kitchen, then pay the crew 2 per cook to walk out (or stiff them on a 5+).
- MAP=11 Weekly calendar grid 7x3: 7 days x 3 services = 21 turns; the week is the board.
- TONE=2 Dry humor: "She wrote four hundred words about your fish."

**Rulesheet (verbatim):**
1. High Street has 7 kitchens in a row. You hold a kitchen with 2 cooks; a 3rd cook makes it hard to raid and easier to cook in. Rooney's Copper Pans hold kitchens too.
2. 21 services, Saturday lunch to Friday late. One action per service. Each kitchen you hold pays 4 a service, each cook costs 1; if you cannot pay, a cook walks.
3. Volk the critic eats dinner at the loudest kitchen (highest Buzz) she has not tried yet. Ties are her secret, and she has one habit her column hints at.
4. If she eats in your kitchen: d6, need 4+ (3+ with 3 cooks). Success: a star (a 6 is two) and +6 cash. Fail: Buzz -2.
5. News is one service late: the Buzz board, where Volk ate, and Rooney's moves. Your own kitchen's rolls, and raids on you, you see at once. Taking or raiding a kitchen whose holder changed since the board was printed wastes the service.
6. Actions: Take a house kitchen (8 cash, 2 spare cooks), Raid one of Rooney's (2 spare cooks, d6 need 5+, 4+ with 3 spare; a failed raid loses a cook), Push Buzz +2 (4 cash), Reinforce (3rd cook), Hire a cook (6 cash).
7. Friday dinner Volk returns to the kitchen with the most stars (tie: loudest). Hold it and pass the service: 3+ if you earned its star, else 4+. Then walk out paying 2 per cook.
8. Lose if Rooney feeds her Friday or she eats elsewhere. Two failed rolls in a row open Comp the Room. From Wednesday Rooney pushes harder, raids your starred kitchens on Thursday and Friday lunch, and her habit is for sale (6).

**Fingerprint:** action ids = take, raid, push, reinforce, hire, hold, comp, leak, walkout, stiff. Tracked numbers = Cash; Cooks (spare of total); Kitchens held (list with cooks and stars per kitchen).

## Engine

**Tuning rounds** (300 games each policy):

| run | policy | win_rate | turn_avg | flags | what changed before this run |
|---|---|---|---|---|---|
| 1 | random | 0.06 | 21.0 | none | first draft; a selftest crash (SystemExit when a stale-board take hit a kitchen Rooney had just grabbed) was turned into a bounce that wastes the service |
| 1 | heuristic | 0.11 | 21.0 | TOO HARD | |
| 2 | random | 0.10 | 21.0 | none | takings 3 to 4 per kitchen; Rooney push +1 (+2 from Wed) instead of +2; mid-week raids Thursday only; Rooney's Friday push aimed at his star kitchen (he was pushing an unvisited one); take/raid defaults exclude kitchens you hold live; stale raid on a house kitchen bounces; heuristic reserves the exit bonus |
| 2 | heuristic | 0.19 | 21.0 | TOO HARD | |
| 3 | random | 0.15 | 21.0 | none | Rooney's service check 5+ (was 4+); start cash 24 (was 20) |
| 3 | heuristic | 0.22 | 21.0 | TOO HARD | |
| 4 | random | 0.13 | 21.0 | none | Rooney's raiders come from his quietest kitchen, which reverts to the house; hire 6 (was 8); heuristic reinforces starred kitchens Wed to Thu and pushes on Friday dinner for the tiebreak |
| 4 | heuristic | 0.27 | 21.0 | TOO HARD | |
| 5 | random | 0.13 | 21.0 | none | heuristic hires ahead on Wed/Thu when the predicted Friday kitchen is not its own (no measurable effect) |
| 5 | heuristic | 0.27 | 21.0 | TOO HARD | |
| 6 | random | 0.16 | 21.0 | none | Rooney never earns two stars (he was raving on a 6 at the same rate as the player despite worse odds); Rooney stands at the pass on Friday dinner instead of pushing, so the player's dinner push is the last word on a Buzz tie |
| 6 | heuristic | 0.37 | 21.0 | none | |
| 7 | random | 0.16 | 21.0 | none | pre-flight: removed an unstated +1 Buzz on every Volk visit and two vestigial state keys |
| 7 | heuristic | 0.36 | 21.0 | none | |

Diagnostics that drove the tuning: in run 1, Rooney held the Friday kitchen in 219 of 300 heuristic games and the heuristic idled ("hold") 2431 times because cash averaged 8 at Friday lunch. By run 5 the stars were even (147 vs 135) but 63 Fridays were lost on the Buzz tiebreak and 111 to Rooney's own star kitchens, which led to run 6's changes.

**Final selftest:** random 300: win_rate 0.16, crashes 0, turn_avg 21.0, early_wins 0, early_end_rate 0.0, flags none. Heuristic 300: win_rate 0.36, crashes 0, turn_avg 21.0, early_wins 0, early_end_rate 0.0, flags none. All six targets met.

**Crashes or mismatches found during play:** no crashes. Three engine behaviours worth a fix:
- The option cap (max 5 shown) dropped "hire" on turn 14 when six actions were legal. The rulesheet says you can hire; the engine refused it that turn. The GM would have had to refuse a "hire" request as illegal.
- "Hold the line" is only offered when fewer than three other options exist, so on turns 18 to 20, when the right play was to bank cash for the exit bonus, the player was forced to spend 4 to 6 a turn. The sheet does not say every service costs an action's price.
- Minor: Rooney's lagged push news ("Rooney pushed kitchen 2") printed after kitchen 2 was marked visited, which reads oddly though it is correct under the lag rule.

**Free-text refusal:** on turn 9 the player asked to "send a runner down the street" for tonight's news. There is no scout action; the GM refused in one line, re-showed the three options, and did not advance. The player then hired. Free text with a kitchen argument ("reinforce kitchen 6, not 7"; "take kitchen 5, not 4") mapped cleanly onto the action id with {"k": n} args, overriding the engine's default target.

## Playthrough

Saturday I took kitchen 6, the loudest room, and Volk walked in that night and rolled a natural 6: two stars on the first dinner. Rooney spread across kitchens 1, 2 and 3 and pumped kitchen 3 to 7 Buzz, but her column warned "nothing sours a room like sudden applause," and Sunday she skipped him for kitchen 5, where the house staff rolled a 1; I had just bought kitchen 5 on a stale board, 8 cash for a room she was done with. I learned to push kitchen 7 at dinner, before her decision, so the jump would not count against me under her habit, and Tuesday she ate at 7 with three cooks on the line: one star. Rooney fed her twice at kitchens 3 and 2 and rolled a 4 and a 1 against a 5+, so by Wednesday he had three kitchens and no stars. I took kitchen 4, pushed it exactly once a day, reinforced it, and Thursday she rolled another 6 there: two more stars. Rooney came through the fire door of kitchen 6 on Thursday (roll 5, needed 6) and kitchen 4 on Friday lunch (roll 4, needed 6) and missed both. Friday dinner she walked into kitchen 4, three cooks, my own star, need 2+, and the die came up 1.

**Result:** loss, "Volk went home unimpressed; no contract". **Final numbers:** Cash 28, 11 cooks, holding kitchens 4 (3 cooks, 2 stars), 5 (2 cooks), 6 (3 cooks, 2 stars), 7 (3 cooks, 1 star); Rooney 3 kitchens, 0 stars. **Turns played:** 20 of 21 (the game ended on Friday dinner's resolution; the walk-out turn was never reached).

## Decisions

Genuinely hard turns: 7 (turn 2 hire vs push before her first dinner; turn 3 which kitchen gets the third cook; turn 6 take 4, take 5, or raid 3; turn 8 pushing before the baseline reset; turn 10 push vs reinforce with one spare; turn 14 raid Rooney's kitchen 2 while she sits in it vs take kitchen 4; turn 16 hire vs a second push that would trip her habit).
Obvious turns: 13, of which turns 18 to 20 were worse than obvious: forced spending with nothing to buy.

## Emergence

6 moments:
1. Volk's hype habit knocked Rooney's loudest kitchen off her Sunday list, sending her to a 3-Buzz house kitchen, which I then bought one service later without knowing she had already eaten there (turns 6 to 7). The twist and the habit combined into a trap neither rule describes alone.
2. The baseline-reset exploit: pushing a kitchen on a dinner turn, before her decision, so the rise is folded into her new baseline (turn 8). A real systems discovery the rulesheet does not spell out.
3. Rooney's own policy fought the critic: his +2-a-service pushes from Wednesday lifted kitchen 1 by four between her dinners and excluded it from her Thursday list, which handed me kitchen 4 uncontested (turn 17).
4. Rooney held three kitchens and fed her twice and rolled 4 and 1 against a 5+, so the rival "wall" at kitchens 1 to 3 was loud and starless all week.
5. Two raids on reinforced kitchens, needing 6, came up 5 and 4; the reinforce decisions on turns 3 and 17 were each worth exactly the margin they missed by.
6. The Friday roll: need 2+, rolled 1. Not strategy, but the engine produced a surprise the GM could not soften.

## Problems

- **Forced spending late.** "Hold" is gated behind having fewer than three options, so when the right play on turns 18 to 20 was to bank cash for the 22-cash exit bonus, the only choices were push, hire, or leak. This never shows in selftest because the heuristic always has cash to burn there.
- **Option cap hides legal actions.** On turn 14 six actions were legal and the cap dropped hire. The 3-to-5 options limit is right for the player; the engine should merge rather than hide (for example take and raid into one "take" with a target argument).
- **Dead air when ahead.** Once I held both two-star kitchens on Thursday night, turns 18 to 20 had no decision; the game became two Rooney raids and one roll I watched. A player who is ahead needs something to spend on: a Friday-only purchase that moves the final roll or a cost to hold the kitchen.
- **The ending.** A dominant week lost on a 1-in-6. Fair by the sheet, and the selftest did predict it (the most common loss reason across 300 heuristic games was "Volk went home unimpressed," 131 of 300, which includes this exact case), but there is no lever on Friday for it. Comp the Room exists only after two failed rolls in a row, so a single failed Friday roll has no answer. A Friday-late "she takes a second plate for 10" or a reroll bought with the exit money would convert "unfair" into "expensive".
- **The Leak is weak.** The column prints the hint twice for free (Saturday late and Tuesday late) and the hint is plain; buying the habit for 6 only matters if you misread the hint. Selftest had the heuristic buying it 268 times in 300 games, which inflated its apparent value.
- **Repetition.** Hire was chosen 7 times in 20 turns; the midweek is hire, hire, push, reinforce. The economy worked (every hire mattered, the exit bonus loomed), but the verb variety is lower than the ten action ids suggest; raid, comp, walkout and stiff never fired in this game.
- **Not too easy.** Random 0.16 and heuristic 0.36 were honest: this game went about as well as a game can go until the last die and still lost. If anything the design leans hard: "too hard" was flagged on five of seven selftest runs and the final heuristic rate sits near the bottom of the target band.

## Fun rating

7 out of 10. The week had a real arc: reading her habit out of the column, finding the baseline-reset trick, buying a dead kitchen on stale news, sweating two raids that missed by one, and an economy tight enough that every 6-cash hire was a decision against the exit bonus. The last three turns were dead air and then a 1 on a 2+ took the contract; I want one lever for that night and I want "do nothing" on the list.

## Would replay

Yes. Two of her three habits (walker, noon) I never saw, and either changes how the chase reads; Rooney was starless on dice this time and would be a different problem with two stars; and I never tried the raid line (kicking in the door of the kitchen she is sitting in). The engine is sound enough that a second seed would be a different week, not the same one again.
