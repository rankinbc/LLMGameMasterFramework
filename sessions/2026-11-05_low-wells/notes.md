# Low Wells

Rolls: FORM=3 (tactical skirmish: units on a small grid, fog, counters) SET=17 (mercenary company in a civil war) ROLE=55 (detective) LOOP=2 (pick a destination, pay a cost, resolve what is there) CLOCK=11 (water table drops) TWIST=15 (the enemy learns your last choice and counters it) WIN=2 (reach a location and get out) MAP=7 (three islands and the sea between) TONE=6 (military procedural) CURRENCY=7 (slots) TRACKED=2.

Novelty: roll layer OK, no reroll. Brief: TONE not 12 (rolled 6), opening not free-choice (chosen: scout), midpoint not unlock (chosen: new-threat, Brae's wells fail mid-game).

How the rolls became the game:
- FORM and MAP: a 3 by 3 grid of sites, three islands west to east, three sites each (North, Middle, South). Sites are fogged until questioned or visited. The company is the one unit.
- LOOP: each day pick a destination (march on this island, sail to the next), pay the cost, resolve what is there (boats, a village, militia).
- TWIST: Colonel Vass reads your last move and is ready for it: repeat a kind of move and you pay.
- ROLE: the detective became the rival. Vass was a provost before the war; he reads a company's tracks like a ledger.
- CLOCK: drought. The wells fail island by island, west first.
- WIN: reach Saltmarch harbor and board the Merrow before she sails.
- CURRENCY (slots): seats in the boats. Every man needs a seat to cross; men without one are left on the beach.
- TRACKED=2: Men and Seats.

Signature detail: Colonel Vass, the provost turned hunter, who always answers the move you just made.

## Sense card

1. Job: Each day I, captain of a mercenary company stranded on three islands after our side lost the war, move the company one stop toward Saltmarch harbor, picking up boats and recruits on the way, so that enough men get aboard the hired ship before she sails.
2. Numbers:
   - Men: soldiers and the islanders who sign on. Raised by a village joining (refugees who want off the islands). Lowered by fights, thirst, and men left on a beach without a boat seat.
   - Seats: places in the boats the company has taken. Raised by taking fishing boats and a beaten militia post's boats. Lowered by Vass's gunboat sinking boats.
3. Actions:
   - March to another site on this island: a day's walk. Costs nothing unless Vass's riders are waiting (he is ready when you marched yesterday).
   - Sail to a site on the next island east: the company rows across in its boats; every man needs a seat. Fact: islands are crossed by boat.
   - Question the fishermen: they know every cove; tells me what is at each site here and on the next island. Costs the day.
   - Lie low: stay hidden in camp for the day.
   - Lie low: hide the company in the hills for a day; Vass loses the trail.
   - Sign on dockhands (once, at the harbor): men from the harbor town take the contract. Costs the day.
   - Boarding is not a move: the company boards the moment it stands at the harbor at full strength.
4. Trades: none. Nothing is bought or sold.
5. Out loud: "Your mercenary company lost the war and is stuck on three islands. Walk and row east to the harbor where a hired ship will take you off. You need a boat seat for every man to cross, villagers will join you if you can carry them, and the colonel hunting you is always ready for whatever you did yesterday. The wells are drying up behind you." Reads fine.

Midpoint plan: Brae's wells fail from the middle of the game (new threat); no unlock. Late lever: dockhands signed on once at the harbor (Men +4). Ending shape: cliff (the Merrow sails at dusk of the last day; boarding needs the goal). Opening shape: scout. Rival tell: before (Vass's readiness is on the status line).

Rival policy (one line): Vass is ready tomorrow for the kind of move (march, sail, camp) you made today; walking into it costs men (march, camp) or seats (sail).

## Design changes during tuning

- Map grew from 3 to 4 sites an island (3 boats, 4 villages, 3 militia shuffled over the 10 unknown sites): with 3 sites the wells pushed everyone to the harbor by day 8 and the budget never mattered.
- The Merrow's arrival window was cut (it made a waiting room at the end). She waits at the harbor; the contract asks for 29 men.
- The Brae signal fire (Seats +6) became the late lever at the harbor: the Merrow's longboats row back once for up to 6 men you left on the beaches. Leaving men behind is now a deferred cost, and the last turns have a real use (profile: turns 8 to 10 consequential; before the change turns 11 to 14 had zero spread).
- Boats found on Saltmarch say "no use on the last island" (no crossing remains).

Numbers at round 4 (later changed, see the cold-read log and QA log): DAYS 12, START 16 men / 12 seats, GOAL 29, wells Hollin day 4, Brae day 8. check: heuristic 29 percent, look-ahead 63, random 0, mutation 88 percent. CLEAN.

Accepted warnings:
- LEAK? on fishermen's report: intended, questioning reveals sites.
- TAG thirst fires in 4 percent of heuristic games: the wells are a wall the player plans around ("give out tomorrow" warning), not a toll paid often. Staying one dry dusk for a village (+5 against -2) is a real option.
- Profile: 17 of 24 games decided 3+ turns before the end; the last one or two turns are usually the boarding itself. Accepted at the cap.
- Ablate: lie low is unproven (-0.05). Kept on purpose as the odd element: the plain way to break Vass's read without moving.

## Opening screen (final, as presented 2026-11-06)

LOW WELLS
Your mercenary company backed the losing side of the civil war and is stranded on three drying islands, with Colonel Vass hunting you. Each day you make one move: march along your island, sail east to the next one, question the fishermen, or lie low. Reach Saltmarch harbor, on the far island, with at least 32 men before the Merrow sails at dusk of day 12.

Your numbers
- Men 16/32: the men with you now, and the 32 your new contract needs.
- Seats: places in the boats you hold; every man needs one to cross to the next island.
- At: where the company is.
- Vass: the move his men are lying in wait for today (rule 5).

Rules: the eight lines of `python engine.py rules` (GOAL 32), verbatim.

Goal: stand at Saltmarch harbor with 32 men or more.   Lose if: the Merrow sails at dusk of day 12 without you, or the company is wiped out.   Turns: 12

Turn 1 of 12 | Men 16/32 | Seats 12 | At: Hollin camp | Vass: no read on you
Map, west to east: Hollin (North, camp, East, South) | Brae (North, West, East, South) | Saltmarch (North, West, harbor, South).
Every site but your camp and the harbor is unknown. 16 men, boats for 12: a sail today leaves 4 behind for good. Vass has no read on you. Hollin's wells run dry from day 4.
1. March to another site on Hollin: North, East or South (unknown)
2. Sail to Brae: North, West, East or South (unknown; 4 men left on the beach)
3. Question the fishermen about Hollin and Brae
4. Lie low in the hills for the day (Vass loses your trail)
or say anything else.

The round-6 cold-read screen said 31 men and had the older wording of rules 3 to 6 and 8; GOAL moved to 32 and the wording was tightened after the QA rounds.

## Cold-read log

Round 1: score 7, no NONSENSE, first move "question the fishermen" (reasonable). Six lines quoted: the Vass status field, whether "taken once" covers every site, the first dusk of thirst, whether the longboats reach men two islands back and are their own move, whether stranded men leave the count, whether boarding is its own move. It also called lie low a dead option (strictly worse than questioning). Game change: lying low now hides the company: Vass cannot strike it, and he has no read the next day. Sheet: rules 2, 4, 6, 7, 8 state the points that were unclear. check --free after: clean, heuristic 24 (accepted within the cap slack), look-ahead 67.

Round 2: score 7, no NONSENSE, first move "question the fishermen". Five lines quoted, mostly about what counts as "a day in camp" (is lying low one, is the longboat trip one, can Vass strike boarding) and "from any island" on the longboats. Game change: the "camp day" category is gone. Vass answers three named moves (march, sail, questioning); the longboats work like lying low (he cannot strike them and loses your trail). Rule 2 says every other site holds one thing taken on the first visit; rule 5 says the gunboat's lost seats can strand more men. check --free: clean, heuristic 24, look-ahead 67.

Round 3: score 7, no NONSENSE, first move "question the fishermen". Six detail questions: the Vass legend against "no read on you", whether any march counts as a repeat, lost or parked stranded men, whether the harbor holds a site, the first dusk of thirst, whether boarding takes its own day. Three rounds spent, so the game was simplified: boarding is automatic the moment the company stands at the harbor 29 strong (the board action is gone, and the longboats can complete the company on the spot). The sheet says "any march, any sail, or questioning", "off your count (rule 7)", "every site but the harbor", "from that day's dusk on". check: clean, heuristic 24 (cap slack), look-ahead 68, mutation 86.

Round 4: score 7, no NONSENSE, first move "question the fishermen". Five questions; the stranded-men and longboat mechanic drew questions in every round. Simplified: men without a seat are lost for good, and the late lever became dockhands signed on once at the harbor (Men +4; Vass cannot strike it). Rule 6 names the dusks plainly, rule 4 says lying low works any number of days, rule 1 says the boats go with you. GOAL 31. check: clean, heuristic 34, look-ahead 65, mutation 88.

Round 5: score 7, no NONSENSE, first move "question the fishermen". Five quotes, all wording: what "he is ready" physically means, whether lying low can repeat, "end on", where questioning works. Sheet: rule 5 names the riders' ambush and the gunboat, rule 4 says lying low is never struck and questioning works from any site, rule 6 says "each night you spend".

Round 6: score 7, no NONSENSE, first move "question the fishermen". Five edge questions (the first thirsty night, "even days running", that every march counts as one kind, whether lying low on a dry island still costs water). Fixed in rules 4 and 6.

Verdict after six rounds: never NONSENSE, every reader described the game the same way, scored 7 and chose the same sensible first move. The quote count stayed at five or six every round, on whichever edge cases the current sheet left open, so the two-quote bar was not met. Presented anyway, as a known miss. Harness finding for later: the quote criterion may need calibrating against an 8-line sheet (count only quotes that change the first decision?).

## QA log

Round 1 (4 games, seeds 101-404): S1 about 21 percent of maps could never reach the goal (a Hollin of villages and militia caps the first crossing). Fixed: the deal is redrawn until `ceiling()` (best case: every militia beaten, no Vass, no thirst, no clock) reaches the goal; the sheet says every map can be won; a rule test checks 60 seeds. S3 fixed: militia roll text ("You attack: roll 2 (need 4+) fail."), well warnings only for the island you are on, no Vass read set after the last day, Saltmarch militia say "nothing to gain on the last island", stale notes. S4 kept: a REACH on seats removed (seats never get near 0 in play; the defensive "whole company left on the beach" end stays); marches to searched sites stay (they break Vass's read); a lost game plays on to day 12 (the GM says so when it happens). Harness finding: autopsy regrets come from the heuristic's rollouts and can recommend a poor move. check after: clean, heuristic 41, look-ahead 83, mutation 87.

Round 2 (4 games): no S1. S2: "Every map can be won" was false for about 7 percent of seeds, because `ceiling()` ignores the clock, Vass and thirst. Fixed: `winnable()` runs an exact search (perfect knowledge, every militia fight won, every rule and the 12-day clock), pruned by the villages left; the deal redraws until a map passes. It matched the reviewer's solver on 300 random deals and takes about 3 ms per deal. S3 fixed: no Vass read for a sail on Saltmarch (no sail is left), "Your old camp is empty.", Brae's warning only on Brae, rule 3 says the militia leave either way. GM CLAUDE.md band corrected (look-ahead 60 to 90). Easier with every map winnable, so GOAL 32. check: clean, heuristic 45, look-ahead 73, mutation 67 (survivors are in the solver's pruning and cache).

Round 3 (5 games): S2 the questioning half of Vass's rule could never fire (question is gone the next day). Fixed: Vass now answers only a march after a march or a sail after a sail; questioning hides your trail like lying low. S3 fixed: losses never take Men below 0 and the text shows what was lost; Saltmarch militia label says "their boats no use on the last island"; resample_hidden draws only winnable maps; the sheet says "if your fights go well". S4 kept: dockhands always taken last, Brae's dry day rarely reached (the wall pushes you on), Saltmarch plays itself once known. check: clean, heuristic 45, look-ahead 72, mutation 69 (survivors in the solver's pruning). Three QA rounds spent; presented.

Final: DAYS 12, 16 men / 12 seats, GOAL 32, BOAT 6, RECRUIT 5, HANDS 4, riders -3, gunboat -4, thirst -2 from day 4 (Hollin) and day 8 (Brae). Every deal passes an exact solver (fights won).

## Played game (2026-11-06)

Win on turn 11 of 12, 33 men aboard. Path: question, march Hollin South (boats), sail Brae East (boats), march Brae North (village), march Brae West (village, ambushed Men -3), sail harbor, march Saltmarch North (village), question, march Saltmarch South (village), lie low, march harbor. Dockhands never used.

Autopsy: dilemma share 0.91; biggest swing turn 7 (the Saltmarch North village); top regret turn 5 (marching into Vass's ambush instead of questioning, cost 0.35). Ending was flat: the win was in hand by turn 8.

Player feedback: wanted a more open-ended game. Tried free-text moves the engine had none for (fortify a camp, assassinate Vass, double back west, split the company for an ambush). Questioned the setting (thirst beside the sea, why no return west, whether fishermen lie). Narration slips caught by the player: "six fishing boats" for Seats +6, and recruits with spears in a gunboat war. The West militia on Saltmarch was a pure loss and read as pointless.
