# Playtest Report: 10 Generated Games

Date: 2026-10-14
Method: 10 parallel self-play runs of the `/play` skill. Each run rolled a fresh game, then one agent played both GM and player to the end. Per-game transcripts and summaries are in `game_NN_<slug>/`. Ratings are the player persona's, 1 to 10.

Caveat: self-play. The GM and player share a brain, so rule ambiguities were resolved generously and the player never misread a rule. A human would hit more friction. Treat ratings as an upper bound on clarity and a fair read on design.

## Scoreboard

| # | Title | Setting / Role / Loop | Result | Turns | Hard choices | Surprises | Fun |
|---|-------|----------------------|--------|-------|--------------|-----------|-----|
| 01 | Dead Decks | Derelict ship / warlord / trade | Win | 11 of 20 | 3 of 11 | 6 | 6 |
| 02 | The Grey Strand | Carrier group / admiral / hold the line | Win | 12 of 20 | 6 of 12 | 5 | 6 |
| 03 | Cistern Line | Asteroid belt / water engineer / contracts | Win | 18 of 20 | 7 of 18 | 7 | 7 |
| 04 | Cold Burn | Trench front / admiral / ration supply | Win | 11 of 16 | 5 of 11 | 4 | 7 |
| 05 | Black Lanterns | Pirate isles / lighthouse keeper / dig deeper | Loss | 10 of 16 | 6 of 10 | 5 | 5 |
| 06 | Feral Ring | Monster hinterland / beast tamer / chase | Loss | 15 of 16 | 6 of 15 | 9 | 6 |
| 07 | Trench Herd | Deep-sea platform / beast tamer / destinations | Loss | 16 of 16 | 4 of 16 | 6 | 4 |
| 08 | Dry Reckoning | Desert city / governor / allocate workers | Win | 18 of 18 | 7 of 18 | 8 | 7 |
| 09 | Ice Gauge | Plague river town / drone operator / repair | Win | 13 of 18 | 5 of 13 | 6 | 7 |
| 10 | Kettle Patrol | Submarine zone / beast tamer / faction favors | Win | 16 of 18 | 4 of 16 | 7 | 6 |

Totals: 7 wins, 3 losses. 140 turns played. 53 hard choices (38 percent of turns). 63 emergent moments (6.3 per game, above the skill's one-per-4-turns floor).

**Average fun: 6.1 / 10.** Range 4 to 7. No game scored 8 or above. No game was broken. Every game was recognizably different from the others; the novelty goal is met. The ceiling is the problem, not the floor.

## Overall rating

**6 / 10 as a generator.** Openings are consistently good; every summary praises turns 1 to 6. The mid-to-late game collapses in 9 of 10 runs into one of three failure shapes: the economy outruns the clock and the rest is execution, a mechanic goes dead and the option list shrinks to one, or the dice take over because nothing the player buys changes the odds. The fixes are design rules the GM can check before presenting; they are listed at the end.

## What made games bad

Ranked by how many of the 10 games showed it.

1. **Dead mechanics (9 of 10).** A tracked number, rule line, option, faction, or shop item that never engaged. Scavenge and Med in Dead Decks. Hull and repair in Grey Strand. The Concession faction in Cistern Line. The shop and silver in Black Lanterns. Serum in Feral Ring. Herd in Trench Herd. Groves and Nomad Camp in Dry Reckoning. Scouting and Optics in Ice Gauge. The Navy in Kettle Patrol. With only 8 rule lines and 3 numbers, one dead element is 12 to 33 percent of the game wasted, and it shows.

2. **Back half with no decisions (8 of 10).** Hard choices clustered in the first 6 to 10 turns, then the game became a solved line. Dead Decks turns 5 to 10 were the same trade loop. Cold Burn's last three turns were watching a counter. Dry Reckoning turns 11 to 15 were salt, salt, salt. Kettle Patrol turns 7 to 10 were "move one west" four times. Nothing new opened after the midpoint in any game.

3. **The clock had no teeth until late or never (6 of 10).** Dead Decks won with 542 unspent. Grey Strand lost 1 Hull all game. Cold Burn's 80 RM was loose until a turn-8 doubling. Ice Gauge's gauge sat at 8 for five turns. When the lose condition is never in sight, risk has no cost and every option collapses to the greedy one.

4. **Dice decided, choices did not (5 of 10).** Feral Ring: every action a flat 4+ with no way to improve it. Trench Herd: the whole win hung on a 28 percent roll attemptable four times. Dry Reckoning: won on back-to-back sixes after decisions ended at turn 10. Kettle Patrol: lost 9 of 10 Hull to rams and storms, not to any missed action. Black Lanterns: three bad d6s with no recovery lever. The player persona's line from Trench Herd: "I like being squeezed by a system; I do not like being told the whole game is one die."

5. **Passive or invisible rival (4 of 10).** Vosk in Dead Decks only raised a price. Kessler's Serum and route were hidden, so the lesson arrived in hindsight. Ice Gauge jobs never reacted to the target. A named rival who does not visibly act is a ledger line, not an opponent.

6. **Economy that does not close (3 of 10).** Black Lanterns: the player proved by arithmetic on turn 1 that oil could not last. Trench Herd: 40 percent of turns were forced recharges. The opposite failure, Dead Decks, netted +100 a turn against a +7 clock. Nobody paper-checked income against upkeep over N turns before presenting.

7. **No loss-streak compensation (3 of 10).** The taste profile asks for it explicitly. Black Lanterns, Trench Herd, and Ice Gauge punished a bad streak with nothing to climb back on.

8. **Dense rulesheet and status line (6 of 10).** All ten fit 8 lines, but most used compound lines doing double duty, and status lines carried 5 to 7 numbers once world state (prices, gauge, rival holdings) was included. Within the letter of the cap, at the edge of its spirit.

9. **Rulings invented mid-game (7 of 10).** Usually 2 to 5 per game. None contradicted the sheet, but several were the single most important consequence of the game. In Black Lanterns the Rock is only reachable through an islet you cannot return to, and that was not on the sheet. A human player would have been blindsided.

## What made games fun

Ranked by how often the summaries cited it as the high point.

1. **Visible arithmetic with a tight margin (10 of 10).** Every game's best turns were ones where the player computed a threshold, a price, or a fuel line and the margin was small. Cistern Line's water-to-fuel conversion, Grey Strand's breach threshold, Cold Burn's RM against upkeep, Ice Gauge's exchange rate. The taste profile's "visible numbers" is the single strongest predictor of a good turn.

2. **Finding your own line (6 of 10).** The highest-praised moments were exploits the game did not hand over: skip-jump pricing in Cistern Line, spend-before-refill in Grey Strand, swap-instead-of-job in Ice Gauge, the Teacup purchase in Kettle Patrol, the Air hedge in Dead Decks. Players want to feel clever, and the game only has to leave room.

3. **Two systems colliding (10 of 10, 63 instances).** The memorable surprises were never events alone. They were an event landing on a system state: the refugee escort arriving when the wave could not reach the line, the hail wanting the same water as the stockpile sale, the current swap carrying both submarines into the same sector, the refugees raising the march threshold the turn after the nomads left. The event deck fires; the system turns it into a story.

4. **A clock that finally bites at the right moment (4 of 10).** Cold Burn's perigee doubling, Ice Gauge's ice dropping 1, 1, 1, 1, 2 in the last five turns, Feral Ring's integrity drain tied to the feral count. When the clock arrived it produced the single tightest decision of each game. The problem was that it arrived late or not at all in the others.

5. **Hidden layout as the puzzle (4 of 10).** Cold Burn's gun placement, Kettle Patrol's hydrophone, Black Lanterns' rival target order, Cistern Line's faction map. Fog of war with a cheap scouting action gave information real value.

6. **A rival that visibly reacts (3 of 10).** Morrow skipping an islet the player claimed. Kessler following the player around the ring. The sub fleeing after a hit. When the opponent's behavior was readable and changed in response to the player, the summaries called it the best beat.

7. **Permanent consequences (3 of 10).** Castellan's hull as the price of information. Dead Decks' lost cargo at launch. Black Lanterns' FOUL channels. The "damage is permanent" twist was the one that most reliably produced tension.

8. **A learnable lesson for the replay (9 of 10 said would replay).** Every yes cited a specific thing to do differently. Mastery over narrative, as the profile says. This is the generator's biggest strength: the games are small enough that one play teaches a strategy.

9. **The opening six turns (10 of 10).** Unknown map, tight bankroll, first gamble. Every summary rates the opening well. The generator already knows how to start a game.

## Recommended changes to the skill

Add a pre-flight check the GM runs before Step 6 (Present). Each item is a one-line rule.

1. **Paper-run the economy.** Project income minus upkeep over the full turn budget. Win must be reachable around turn 0.7N with average dice and unreachable before turn 0.5N. If the clock cannot bite by midpoint, tighten it.
2. **Clock escalates at midpoint.** Upkeep doubles, the threat moves faster, or a new drain appears at turn N/2. Announce it on the rulesheet.
3. **Midpoint unlock.** Something new opens at turn N/2: a spoke, a second-stage goal, a shop tier, a revealed objective. The option list must not shrink after the opening.
4. **No dead elements.** Every tracked number needs a source and a sink that both matter in the last third. Every rule line must be reachable in a normal game. Every faction must be worth touching. Cut anything that fails.
5. **Odds are buyable.** No flat coin-flip actions. Every roll must have at least one purchase, position, or preparation that moves the target number.
6. **Rival acts every turn with a tell.** The named opponent moves, spends, or claims each turn, and the player sees one line about what they did or where they are heading.
7. **Loss-streak lever.** After two consecutive failed rolls, something cheap becomes available: a hazard bonus, a free scout, a discounted retry.
8. **Status line: 4 fields max.** Tracked numbers plus the clock. World prices go in the situation text, not the header.
9. **State the sharp consequence.** If a rule combination creates a trap (a place you cannot return from, an approach that always costs Hull), it goes on the rulesheet in plain words.
10. **Turn floor enforced.** If the paper run says the game can end before turn 12, lengthen the win condition.

## Library candidates

None scored 8. Best skeletons worth saving after one tuning pass, in order: Cistern Line, Cold Burn, Ice Gauge, Dry Reckoning. Each summary lists the specific numbers to change.
