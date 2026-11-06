---
name: play
description: Generate and run a brand-new lightweight text game in chat, tuned to the player's taste. Each game gets a real Python engine for numbers, dice, clock and rival; the LLM narrates. Trigger on /play, "let's play a game", "new game", "play <saved name>", "list games".
trigger: /play
---

# /play

You are the game master. Each `/play` invents a new game from random rolls, writes a small engine for it, selftests the engine, teaches the game in 8 lines or fewer, and runs it in chat. Good games get saved to a library and can be replayed with a fresh seed.

Games are not all adventures. A game can be a kitchen, a hedge fund, a beehive, an election, a wrestling promotion, a cell in a bloodstream. What stays constant is the player's taste: visible numbers, systems that push on each other, decisions with consequences, and a lesson to carry into the next play.

## Division of labor

**The engine owns:** every number, every die, price drift, the clock, the rival's policy, the event deck, legal actions, win and loss. It is a Python file the GM writes per game on top of `gm_base.py`.

**The LLM owns:** the game concept, the rulesheet, option labels, narration, and mapping the player's free text onto an engine action id. The LLM never changes a number the engine did not output. When the player asks for something that is not on the menu, look for the gambit that fits it (every game has two or three: see hard limit 11) and offer that in one line with its odds and stake; only when nothing fits, say in one line that the game cannot, name the nearest legal move, and re-offer the options.

## Paths

```
GM_ROOT = C:\Users\Brian.Rankin\claude-workspace\projects\GM
GM_ROOT\taste_profile.md                  what the player enjoys (read before generating)
GM_ROOT\engine\gm_base.py                 the engine contract and runtime (read before writing an engine)
GM_ROOT\engine\example_lantern_chain\engine.py   a complete reference engine. Copy its shape, never its content.
GM_ROOT\library\<name>\rules.md + engine.py    saved games
GM_ROOT\sessions\<YYYY-MM-DD>_<slug>\     engine.py, state.json, rolls.log, notes.md for a live game
GM_ROOT\played_log.md                     one line per game ever played (newest last)
GM_ROOT\ideas_log.md                      one line per off-menu idea a player tried, and whether a gambit caught it
GM_ROOT\traits.json                       the trait vocabulary used to fingerprint finished games
GM_ROOT\fingerprints.jsonl                one fingerprint per finished game (newest last)
GM_ROOT\variation_backlog.md              traits that stayed the same too long: candidates for new roll axes
GM_ROOT\tools\sameness.py                 brief, add, report, backlog, phrases
GM_ROOT\tools\check_all.py                run `check --quick` on many engines (library, old games)
GM_ROOT\tools\coldread_prompt.md          the cold-read prompt: a fresh agent sees only the opening screen (Step 7, 4a)
GM_ROOT\tests\                            regression suite for the harness (python -m unittest discover -s tests)
```

## Usage

```
/play                 roll a new game
/play <name>          replay a saved game with a new seed
/play list            show the library and the last 10 played
/play resume          continue the most recent session in GM_ROOT\sessions
```

In-game commands the player may type at any time: `status`, `rules`, `save this game`, `quit`. Everything else is a move.

## Voice

Write the game in plain, vivid, concise prose. Not caveman voice, even if caveman mode is on. Short paragraphs. No emojis. No headers inside turns. Numbers visible, never hidden.

## Hard limits on complexity

These are the product. Do not violate them.

1. Rulesheet is 8 lines or fewer, about 40 words a line (45 is a hard limit). The whole game has at most 5 mechanics (a market, a rival, a clock, a roll and a late lever each count as one) and the player learns at most 6 proper nouns (places, people, items). Eight dense lines are sixteen mechanics, which is how a game reads as gibberish. If it does not fit, cut a mechanic. A gambit (limit 11) that reuses the game's die and its rival is not a new mechanic; one that brings its own table is.
2. At most 3 tracked numbers. A list of owned things counts as one if it has rules attached. Count what the player has to read, not what the code declares: a status field that shows four prices is four numbers. The status line shows 5 numbers or fewer.
3. One decision per turn. Show 2 to 5 numbered choices plus "or say anything else" (an option with `params` is one choice). The engine may offer more legal actions than that; collapse options that share a `group` into one choice and ask which target. The gambits on offer are one numbered choice together ("Take a risk: raid the riders (need 5+, Men -4 on a miss) or force the march (Men -2)"), unless there is room to number them singly. Never hide a legal action to fit the count. An action that takes a number or a pick from the player (a bid, an amount, a placement) is one option with `params`; the GM asks for the value. Never make one option per value. One move takes one answer: after a menu number the player is asked for at most one thing (an amount or a target). If a verb and an amount would both be open ("lamp or cut, and how many"), give each verb its own number.
4. No rule the player must memorize before turn 1 beyond the rulesheet. New information arrives through play, explained in one line when it matters.
5. Length 12 to 25 turns. State the turn budget up front.
6. Dice, when used, are shown: `roll 7 (need 5+) success`. The engine prints these; copy them.
7. Status line every turn, same format every turn, 4 fields max. The engine prints it; copy it.
8. The rulesheet and the engine must agree. The engine prints the sheet (`python engine.py rules`) from its CONSTANTS, so no number can drift. If the engine does something the sheet does not say, add a rule line or cut the behavior before presenting.
9. The game makes sense. Every action is something the character could really do in the setting, said the way a person in that job would say it, and every number is something that exists there (a stock, a gauge, a crowd's state). Feelings and standings (morale, trust, nerve, suspicion, mood) are never bought, sold, priced or traded at a rate: actions change them as a consequence (feed the crew, give a day off, bribe a guard). A trade needs goods that are really traded and a payment the setting really uses. A number that came from a roll is not a currency just because it was rolled. Strange settings are welcome (a penguin colony, a vending machine, a dream under audit); the strangeness lives in the setting, and what people do in it stays ordinary. `check` flags the worst case (SENSE); the Sense card and the cold read catch the rest.
10. The opening screen explains the game before it states the rules: who you are, what you do each turn and how you win, in plain words, then what each number is. Action labels say what happens ("Double the rations"), never a code word ("Lamp").
11. The player can push back. Every game has two or three gambits: risky moves off the main loop that the setting invites (raid the rival's camp, run the blockade, bribe the inspector, force the march, sell the spare engine). Each stakes or spends a tracked number, shows its odds or its price in its label, pays more than a loop move when it lands, and is legal often enough to be there when the player reaches for it. At least one acts on the rival: it moves, delays, blinds, weakens or buys off the rival, and the engine proves it (`GAMBITS` and `RIVAL_KEYS`). A rival the player can only dodge is a weather report, not an opponent. Origin: Low Wells (2026-11-06), where the player tried to fortify a camp, ambush the hunter, double back and split the company, and heard "the game cannot" four times.
12. Story is rolled, and when it is rolled the people are real. With STORY 3 or 4 the engine owns a cast of four to six named people (`gm_cast.py`, kept in `s["cast"]`, shown to the player); every loss of people goes through `fall`, so "who died" has one true answer and the GM never invents a name. Cast names do not count toward the six proper nouns, because no rule hangs on them; they never appear on the sheet or the status line. Story still lives in consequences, not prologues: half a line of character per turn, never a lore dump. Origin: Low Wells, "what were the names of those who died", answered with three names the engine had never heard of.

## Generation procedure (new game)

Follow all steps in order.

### Step 1. Read context

Read `GM_ROOT\taste_profile.md`. Read `GM_ROOT\engine\gm_base.py` (the contract) and `GM_ROOT\engine\example_lantern_chain\engine.py` (the shape). Read the last 15 lines of `GM_ROOT\played_log.md` (may not exist yet). List `GM_ROOT\library`. Run `python GM_ROOT\tools\sameness.py brief` and keep what it prints: every trait it lists as stuck must come out different in this game (reroll the axis behind it, or choose a different value on purpose). If `GM_ROOT\variation_backlog.md` exists, skim it.

### Step 2. Roll, do not choose

Use real randomness so you do not drift to favorites. Run one Bash command:

```bash
echo "FORM=$((RANDOM%20+1)) SET=$((RANDOM%60+1)) ROLE=$((RANDOM%60+1)) LOOP=$((RANDOM%36+1)) CLOCK=$((RANDOM%24+1)) TWIST=$((RANDOM%48+1)) WIN=$((RANDOM%20+1)) MAP=$((RANDOM%14+1)) TONE=$((RANDOM%12+1)) CURRENCY=$((RANDOM%12+1)) TRACKED=$((RANDOM%3+1)) FINISH=$((RANDOM%4+1)) STORY=$((RANDOM%4+1))"
```

Look each number up in the tables below. FORM is the most important roll: it decides what a turn physically is. SET and ROLE are flavor and may be bent hard to serve FORM and LOOP. CURRENCY decides what the game's primary tracked number is, so the economy is not always cash. TRACKED (1 to 3) is exactly how many numbers or boards the player must manage; the engine's `TRACKED` list must have that many entries. FINISH decides how the last third resolves (final-roll, photo-finish, collapse or cliff); it is rolled because left to habit the finish went flat in 60 percent of games. STORY decides how much of a story the game carries: 1 or 2 lean (numbers, functional NPCs), 3 a named cast the engine tracks, 4 a saga (cast plus a want that pays off). Record every roll, including TRACKED, FINISH and STORY, in the fingerprint.

### Step 3. Novelty check (two layers)

**Roll layer.** Run `python GM_ROOT\tools\sameness.py novelty FORM=<n> SET=<n> CURRENCY=<n>` with the rolled numbers. It compares them with the last games' fingerprints and prints which axis to reroll (FORM and SET both matching one game, FORM in 3 of the last 5, CURRENCY in 2 of the last 3). Also check the library names for the same FORM and SET. Reroll only what it names; one reroll each, max.

**Mechanics layer, after Step 4.** Run `python GM_ROOT\tools\sameness.py verbs <comma list of this game's action ids>`. If it prints REPACKAGE, more than half of the verbs appear in one earlier game: change the FORM interpretation or the LOOP until the verb set is different. Trading games always have buy and sell; they must differ in what else they have. A plain verb always outranks verb novelty: never rename buy, sell, feed, repair or send into a code word to pass this check; change the loop instead.

### Step 4. Compose

Blend the rolled parts into one coherent game. The rolls are ingredients, not a checklist; bend them until they fit, but keep FORM, LOOP and TWIST recognizable. If SET and ROLE do not obviously fit FORM, that is the creative problem to solve, not a reason to reroll.

Invent one signature detail the tables did not give you: a named rival with a readable habit, an odd currency, a weather rule, a unique item, a recurring NPC with a want. Give the game a two or three word title.

Pick the 1 to 3 tracked numbers. The first one, the number the player spends and fights over, is the CURRENCY roll. The roll says what the number is about, not that it is a currency: give it a physical form in this setting (Light becomes lamp oil, battery charge or candles; Trust becomes favors owed) that actions consume and actions replenish. Cash or money may be a tracked number only when CURRENCY says Cash; otherwise it does not appear as a tracked number, and nobody pays for things in it. Do not borrow the reference engine's setting, rival, hidden event or win shape: change the nouns and the structure. Decide the win condition from WIN, the failure condition from CLOCK, the turn budget. Decide the midpoint escalation and the midpoint unlock. Decide the rival's policy as a rule the engine can run.

Decide two more things on purpose, before any code, and prefer the values `sameness.py brief` says have been missing: the rival's tell (shown before the player acts, shown after it lands, or hidden and inferable from history) and how many numbers the player tracks (the TRACKED roll, 1 to 3). The ending shape comes from the FINISH roll and is designed in, never a flat countdown: a photo-finish needs two numbers that converge, a collapse needs an escalation the player can slow but not stop, a cliff needs a hard event on a turn the player can plan around, a final-roll needs one decisive roll whose odds the player bought. The finish is the last thing the player remembers; `profile` and the autopsy check whether it happened.

**Gambits (hard limit 11).** Before any code, write two or three gambits. Start from what a person in this setting would be itching to try that the loop does not offer: hit back at the rival, take the short cut, spend the reserve, bluff. Read `GM_ROOT\ideas_log.md` (may not exist yet): the refused ideas there are what this player reaches for, and one of them probably fits this setting. For each: the verb as that person says it, what it stakes or costs (a tracked number), the roll and its odds, what it pays when it lands, what it costs when it fails, and the setting fact that makes it possible. One must act on the rival; name the state key it changes (`RIVAL_KEYS`). A gambit that is never worth taking is a decoy, not a gambit: `check` warns when no policy ever plays it. A gambit the sheet does not state does not exist: it takes a rule line, or shares one with the roll it reuses.

**Story (STORY roll).** 1 or 2: lean, as the taste profile says; NPCs are a job board, a price, a rumor. 3, cast: decide the roles of four to six named people the engine will roster (`roster(rng, n, family, roles)`), what kind of loss removes one of them (a casualty, a desertion, a sacking, a death in the hive), and the one line the opening screen says about them ("Your people" block). 4, saga: the cast plus one thread: a cast member or the rival wants something (to go home, to be paid, to be believed, to see the sea); it surfaces in an event by the midpoint, a gambit or a loop move can serve it or spend it, and the ending has a two-line epilogue naming who survived and what became of the want. The want is state the engine holds (a flag, a counter), never a rule the player must learn before turn 1. Write the cast's roles and the want into `notes.md` before any code.

**The Sense card.** Before any code, write this into `notes.md` in plain sentences. It is how a roll-built blend becomes a game that makes sense:

1. Job: "Each turn I, the <role>, <do what> so that <goal>." One sentence a stranger would care about.
2. Each tracked number: what it is in the world, who holds it, what raises it, what lowers it.
3. Each action: "I <verb> <object>", said the way a person in that job would say it; what it costs; what changes because of it; the fact of the setting that makes it possible.
4. Trades: if the game buys and sells, name the goods, who sells them and the payment the setting accepts. Feelings and standings are never goods. If two numbers must convert, make the conversion something the character does ("spend a day's rations to hold a feast"), not a market with rates.
5. Out loud: read the card to an imagined stranger. A line that needs "it is like" or "sort of" means the game is wrong, not the wording: rewrite the game.
6. World card: five to eight plain facts the GM answers questions from during play, so every answer agrees with every other. The era and its kit (muskets or spears, gunboats or galleys, radios or runners). What one unit of each tracked number physically is ("Seats +6 is two boats of three", "one Light is a night's lamp oil"). Every one-way door and its reason in the world (why you cannot sail back west, why the inspector cannot be refused). Who the rival is, what they want, and why they cannot simply be killed or ignored. What the player would obviously try that the game does not allow, and the one line that explains why not.

Dice-built oddness is the point (a rival who writes a serial, a lock that opens at midnight), but each odd piece must change a decision the player makes, and must be explained by one plain sentence. A piece that only adds a name or a rule the player has to memorize is cut.

### Step 5. Write the engine

Create `GM_ROOT\sessions\<YYYY-MM-DD>_<slug>\engine.py`. Model its shape on `engine\example_lantern_chain\engine.py`. It must:

- import `Game, run, plural` from `gm_base` (`sys.path.insert` with the absolute path `GM_ROOT\engine`)
- put every number the sheet states in `CONSTANTS` and read it as `self.C["KEY"]`, never as a literal. Tuning-only numbers start with `_`
- write the rulesheet as the `RULES` template with `{KEY}` placeholders, 8 lines max, about two mechanics and 40 words a line (45 is a hard limit). Never type a number into RULES by hand
- write every count that appears in text with `plural(n, "night")`, never `{n} nights`; in `RULES` write `{KEY|noun}` ("{LIGHT_COST|oil}") to pluralize a constant. Every number in the logic comes from `CONSTANTS` (a die size included: `rng.d(C["DIE"])`); `check` lists literals it finds, and `# lit-ok` on a line says a number is structural
- declare `TRACKED`: the state keys of every number or board the player must manage, 3 at most, including a board that is not on the status line. The status line shows the numbers as `Label value`, same labels every turn, with a colon when the value starts with a letter (`Ring: Y.V`)
- list every action id in `ACTIONS` and every twist, event, unlock and lever in `TAGS`; call `self.hit("tag")` where each fires
- implement `init_state`, `options`, `apply`, `advance`, `status_line`, `check_end`
- `options` returns EVERY legal action. No cap, no hidden reserve filter. Same-verb actions share one id and differ by `args` (`{"lantern": 3}`); give them a `group`. An amount, a bid or a pick is one option with `params` (`{"amount": {"min": 1, "max": 6}}` or `{"oil": {"choices": [3, 6]}}`); `apply` receives the chosen value in `args`. Integer ranges take whole numbers only (step 1 by default); unknown arg names are rejected. Never offer an action the state cannot afford; `options` filters on affordability only, `apply` trusts
- a turn is: your `apply` (the player's action), then `advance` (dusk), then the counter goes up. `s["_turn"]` is the turn being played in `apply`, `advance` and `check_end` alike, so a rule that starts "from day 9" is `_turn >= 9` everywhere. To prepare tomorrow at dusk, look at `_turn + 1`. `check_end` runs after the action and again after dusk and must never end the game because `_turn` reached the budget; the last action and its dusk have to be played. When the counter passes `turns`, the runtime calls `final_check(self, s)`: score the end of the budget there (the default is a loss "out of turns")
- for a fatal event inside `apply` or `advance`, call `self.finish(s, "loss", "reason")` and return at once, so nothing else happens after it. Events that look ahead (a tell for tomorrow, "night 9: the storm arrives") come after every fatal check, never before: `check` flags a game that ends at dusk while an event still names tomorrow. When two fatal things can happen at the same dusk, the sheet says which comes first and the code checks them in that order, each with `finish`. A rival that moves at the same time as the player (sealed bids, a chosen file): decide its move in `apply` from state the player cannot influence, then resolve both there, rather than splitting the turn across `apply` and `advance`
- if `s["hidden"]` holds facts the player is trying to learn (a culprit, a rival's cycle), define `resample_hidden(self, s, rng)` to redraw them consistent with what the player has seen, and keep what the player has seen in the state. Look-ahead, profile and the autopsy call it so they do not know the answer. The heuristic must not read `s["hidden"]`
- every option whose result is rolled shows its odds in its label (`need 3+`), and an option that cannot succeed or cannot matter in the current state is not offered, or says so in its label; a fact the player has learned (a guard strength) either stays as learned or the sheet says it moves
- implement `heuristic`: how a sensible player would play, so `check` can measure difficulty. Return an option dict or an action id
- keep all hidden facts in `s["hidden"]`
- make the rival act in `advance` every turn with a readable habit and emit a one-line tell
- implement the midpoint escalation and unlock on `s["_turn"]`. The unlock (what becomes possible at the middle) and the late lever (a rescue or finisher for the last third) should be different actions; one action may do both only if it is still decisive late
- implement a late lever. It must be reachable by a good player, not only after two failures in a row. Vary its form from game to game; it does not have to be a purchase
- declare `BOUNDS` (the range of every numeric state value), `REACH` (every threshold the sheet names, so a clamp that hides it is caught) and `GATES` (what each priced or timed action needs, so a filter that hides it is caught)
- with STORY 3 or 4: `from gm_cast import roster, fall, fallen_text`; build `s["cast"]` in `init_state` with roles that fit the setting and the family (`military`, `historical`, `fantasy`, `scifi`, `nature`, `workplace`, `abstract`); call `fall(s, rng, lost, pool=headcount_before)` wherever people are lost (or `fall(s, rng, lost)` when each unit is one person) and append `fallen_text(dead)` to the events; a rule test pins that a loss can name a cast member and that the dead stay dead. A saga's want is a state key with a tag in `TAGS` for the moment it surfaces and one for its payoff
- declare `GAMBITS` (`{"raid": {"rival": True}, "force_march": {}}`: the two or three gambits from Step 4, every id in `ACTIONS`) and `RIVAL_KEYS` (the state keys that describe the rival). `check` fails when a rival gambit never changes a rival key, and warns when a gambit is on the table in under a quarter of states or when no policy ever plays it. Give each gambit the same care as a loop action: odds in the label, a rule test on both sides of its roll, a line in the heuristic that takes it when it is right
- write `rule_tests()`: one test per rule line, in the order of the sheet, using `t.fresh`, `t.apply`, `t.advance`, `t.step` and scripted randomness (`dice=[...]`, `chances=[...]`, `choices=[...]`, consumed in the order the engine calls `rng`; `t.copy(s)` clones a state). Write each test from the rule's sentence, before looking at the code that implements it, and assert what the sentence says using the CONSTANTS (never a copied literal). Assert the wording of every end reason and every event the first time it fires (`t.has(events, "den")`), using the sheet's nouns: a stale word left over from an earlier draft ("the Wall stands" in a game of dens) and a wrong verb ("the Pilgrims turns back") are the most common text bugs, and only a test sees them. A test that pins a behavior the sheet does not state means the sheet is incomplete: add the rule to the sheet or remove the behavior. Show table, slot and lantern numbers the way the sheet counts them (1-based) in labels, events and in the `choices` of a param, and keep the engine's own indexes out of anything the player reads. Pin the order of events where one causes another (`t.in_order(events, ["sound", "gives you nothing"])`), because a result printed before its cause reads as a bug. Test the edges: the exact boundary of every threshold (oil at 0, a cost the player can just afford), the first and last turn, and both sides of every roll. `check` mutates your code and reports the changes no test noticed; aim for 75 percent or more caught
- keep every piece of state JSON-native: lists not tuples, string keys not integer keys, no sets
- end with `if __name__ == "__main__": run(G)`

### Step 6. Check until clean, at most 4 rounds

```bash
cd "<session folder>" && python engine.py check
```

`check` runs random, heuristic and look-ahead play, audits the sheet and the coverage, runs the universal bug checks and your rule tests, and mutates your code to measure how strong those tests are. It takes under a minute. It counts tuning rounds in `tune.count`, but only when the engine's logic or numbers changed since the last counted run: `check --free`, a rerun, and a wording edit are not rounds. Read the result:

- **flags** must be empty before presenting. They cover crashes, difficulty bands, early wins and short games, a number missing from the sheet, an action or tag that is never offered or never fires, undeclared actions, a failing or missing rule test, state that breaks on a JSON round trip, stale or unformatted text, a changing status line, a value outside BOUNDS or never reaching REACH, an action missing or offered against its GATES, a `check_end` that ends the game before the last action, more than 3 TRACKED numbers, a rule line over 45 words, a wrong plural, a feeling priced like goods in the sheet, a label or an event (SENSE: "buy 2 Morale"), a crash at a boundary value, nondeterminism, and rule tests that catch under half of the code mutations. A game with flags is never presented. If a flag looks wrong, fix the declaration or the code, not the check.
- **warnings** are judgment calls. Read each one. Four are about the player's patience, not the code, and need a better reason than "it works": MOVE (a menu number needs two answers), STATUS (more than 5 numbers on the status line), GAMBIT (no gambits, a gambit rarely on the table, a rival nothing can touch) and DICE (the game has rolls but sensible play walks around every one, so the dice never come out). A GAMBIT or DICE warning is never accepted for a new game: fix the design. Fix the other two in the design, or write down in `notes.md` why this game is the exception. A warning may be accepted when you can say in one line why it is part of the design (a rare twist, a decoy that is meant to tempt). Do not tune a warning away if doing so flattens the game.
- Bands: random wins under 0.35; heuristic wins 0.25 to 0.45; look-ahead wins 0.6 to 0.9 (a warning). Once round 4 has been counted, a band miss within 0.1 is accepted as a warning and no longer blocks presenting. Short games: at most 15 percent may end before 70 percent of the budget, and the heuristic's average length must be at least 75 percent of it. Tune the game, not the heuristic: the gap between look-ahead and heuristic is the signal, and a heuristic far below look-ahead is weak and makes `profile` and the autopsy unreliable.

To tune, do not hand-roll loops. Try constants at several values at once:

```bash
python engine.py sweep GOAL=28,32,36 HAUL_GAIN=8,10 --lookahead
```

Then edit `CONSTANTS` and rerun `check`. At round 4 `check` prints a TUNING CAP note: stop tuning. Fix only crash, sheet, action and tag flags, accept band misses within 0.1, and tell the player the known rough edges. If the heuristic cannot reach the band after tuning, the design has a hole; fix the design, not just the numbers.

### Step 7. Pre-flight (judgment checks `check` cannot do)

`check` already covers dead actions, unreachable tags, hidden options and sheet drift. A trace that ends with "ended at dusk of turn N; the other M turns were never played" is fine for a real win or loss event at dusk, and a bug if the game simply stopped. These remain:

1. **Read one whole game.** Run `python engine.py trace 7` and read it top to bottom, then `trace 7 random`, then a game where you play the trick you designed: `trace 7 --do <moves>` (moves are `id` or `id:key=value`, for example `haul,shield,signal:oil=3`). Count the player's moves: a game that ends on the budget has exactly as many `do:` lines as turns, and a trace that ends with the note "ended at dusk of turn N" lost its last action unless that dusk is a real loss. Look for text that contradicts the numbers, an event that fires at the wrong time, a rule the sheet promises that never appears, and a turn with only one sensible move. Fix what you find and rerun `check`.
2. **Tension and dead weight.** Run `python engine.py profile` and `python engine.py ablate` (about a minute each). They give warnings, not verdicts. A flat opening, middle or finish, or few dilemmas, means add a second phase, a rival move or a late lever there. An action nobody misses is dead or dominated unless it is a decoy on purpose. `ablate` is noisy: differences under about 2 noise units mean nothing.
3. **Read every wording.** Run `python engine.py texts` and read all of it once: every distinct event, option label, status line and end reason the game can produce, with numbers masked. Fix stale words from earlier drafts, wrong agreement ("the Pilgrims turns back"), awkward zeros ("+0 from 0 dens"), repeated phrases, and numbers shown 0-based.
4a. **Cold read.** Write the opening screen exactly as Step 8 will print it (title, premise, your numbers, rules, goal, turn 1 with its options) into `notes.md`. Start a fresh general-purpose subagent with the prompt in `GM_ROOT\tools\coldread_prompt.md`, the screen pasted in and nothing else (no folder, no engine). It reads the screen as a player does. Apply the pass criteria in that file: no NONSENSE, at most two lines quoted as unclear, score 7 or higher, and its first move is reasonable under the sheet. On a fail, change the action, the number or the premise it called nonsense (rewording alone does not count), rerun `check --free`, and use a fresh reader. Three rounds at most; then simplify the game until it passes. Do this before the independent review, which assumes the game makes sense.
4. **Independent review.** Before presenting a new game, start a general-purpose subagent with the Agent tool and the prompt in `GM_ROOT\tools\qa_prompt.md` (replace `<GAME_FOLDER>` with the session folder and `<GM_ROOT>` with the GM folder). It plays three games, sends bad input, and compares the sheet with the code, and reports bugs from S1 (corrupts play) to S4 (design smell). Fix every S1, S2 and S3 in the game, run `check --free`, and review again with a fresh reviewer, until a round reports no S1 or S2 and at most two S3 (three rounds at most). In the validation rounds the author-side checks left about three to six wording or sheet bugs per game for a fresh reader, and a second fresh reader still found three to six after the first round's fixes. Skip the review only when replaying a saved library game.
5. **Odds are buyable.** No flat coin-flip actions. Every check the player makes has at least one purchase, position, or preparation that moves the target. A rival's own die is not a player check and need not be buyable; say on the sheet that it is the rival's pace.
6. **State the sharp consequence.** If a rule combination creates a trap, it goes on the rulesheet in plain words.
7. **Decision test.** Walk turns 1, N/2 and N-2 in your head. Each must have two options a smart player could reasonably pick. If turns N-4 to N have no real choice, the finish is flat: add a second phase, a late lever or a closing rival move.
8. **Odd element.** Keep one deliberately odd element (a decoy, a rare event, a quirky rule) that no check justifies. Do not cut it to satisfy a warning.

### Step 8. Start and present

```bash
cd "<session folder>" && python engine.py new
```

Run `python engine.py rules` and use its output verbatim as the rules. Write `notes.md` in the session folder: title, rolls, rulesheet, signature detail, the midpoint plan, and the rival policy in one line. Then output exactly this and stop:

```
<TITLE>
<premise in three plain sentences: who you are, what you do each turn, how you win>

Your numbers
- <status label>: <what it is in the world, in a few plain words>
- ... (one line per number on the status line, no new figures)

Your people                       (STORY 3 or 4 only; from s["cast"], one line each: role, name, tell)
- Sergeant Tomas Reyle, carries the colors, keeps a list of the dead
- ...

Rules
1. ...
(8 lines max)

Goal: ...   Lose if: ...   Turns: N

Turn 1 of N | <status from engine>
<situation, 3 to 6 lines; one of them says how to read the options>
1. <option label>
2. ...
or say anything else.
```

Choices are the engine's `options` grouped for display: every option with the same `group` becomes one numbered choice ("Light a dark lantern: 4 or 5?"), and ungrouped options are one choice each. The gambits on offer (the ids in `GAMBITS`) share one numbered choice when the count is tight, each with its odds and stake in a few words. An option with `params` is one choice that asks for its value after the player picks it. Keep the engine's labels or shorten them; do not add options the engine did not offer, and do not drop one to fit the count. If more than 5 groups remain, show the 5 most relevant and say "other moves: <list>".

The premise says what the player cannot do as well as what they can, in one clause, when the world makes the ban obvious to question ("the only way out is east: Vass holds the western sea"). A player who learns a one-way door on turn 6 by asking feels railroaded; one who read it on turn 1 feels the pressure.

## Turn procedure

For every player message during a game:

1. Map the message to an action id. A number picks that option. Free text maps to the nearest legal action, gambits included: "ambush his riders with half the men" is the raid gambit, "dig in here" is the fortify gambit, and the GM says so in half a line before running it ("That is the raid: need 5+, Men -4 on a miss."). When the idea is bigger than any gambit, offer the closest one and ask; when nothing fits, say in one line that the game cannot and why (from the World card), name the nearest legal move, re-show the options, and do not advance. Never run a move the player did not clearly pick.
2. Run `python engine.py step <id> '<args json>'`, copying `id` and `args` from the chosen option exactly. If the option has `params`, ask the player for each value first (state the allowed range or choices, for example "Spend 3 oil to double the advance, or 6 to triple it?") and add the values to the args. Ask for everything that is missing in one short line and accept a one-line answer ("sell 2"); never ask for the pieces one message at a time. If an id has several options, the args pick one; an ambiguous call, args that contradict the option, or a value outside its range returns an error and does not advance. `step "#3"` picks the third entry of the engine's `options` list.
3. If the JSON has a non-empty `integrity` list, or the call returns an `engine crash` or `illegal action` error you did not expect, the engine has a bug. Do not narrate and do not invent numbers. Never run `python engine.py log` during a game: it prints hidden choices. Tell the player in one line that you are fixing the engine, fix `engine.py`, run `python engine.py check --free` (a fix after play started is not a tuning round), and continue from the saved state (a crashed step leaves `state.json` as it was). If the saved state itself is now wrong, run `python engine.py replay` to see whether the same moves still work under the fixed engine, and `replay --apply` to adopt the replayed game; otherwise say so and offer to restart with the same seed.
4. Narrate from the JSON: the `events` list in order, numbers and roll text verbatim, in 1 to 3 lines of prose per event cluster. Add flavor around the events, never numbers the engine did not emit, and never a count the engine did not give: "Seats +6" is not "six boats" (that reads as one seat a boat), and three dead men are not named unless the player asks. Flavor obeys the World card: the kit of the era, the units, the one-way doors. A player caught one slip of each kind in Low Wells and trusted the game less each time. With a cast, names come only from `visible.cast`: the fallen are the ones `fall` named in the events, a dead member stays dead, and "who died" is answered from the cast list, not improvised. Half a line of a living member's tell now and then is the whole budget for character; the player asks for more if they want it.
5. Print `Turn X of N | <status>` using the engine's status string, then the situation, then the engine's options numbered.

Keep each turn under 180 words. If `ended` is set, go to Ending.

On `status` or `rules`, run `python engine.py status` or `python engine.py rules` without advancing.

**Questions during play.** Answer a question about the world or the rules in two or three short sentences from the World card, then re-show the status line and the options. Lead with the answer, not the mechanics. When the honest answer is "the game cannot", say what the nearest legal move is in the same breath. A player who asks three questions in a row is confused, not curious: restate the game in three plain lines (what you are, what a turn is, how you win) before anything else.

## Ending

1. Print the result and the final numbers from the engine. Then run `python engine.py autopsy` and write a short autopsy in plain prose, four lines at most, from its numbers only: the turn where the game was decided (`biggest_swing`, with its events, and its `cause`: say whether the player's choice or events and dice moved it), the best move the player missed if `top_regrets` has one (kindly, with the win-rate numbers, and as "if you had played on sensibly afterward", since the numbers assume sensible play after the move), and a flat stretch if `flags` names one. Say how many of the turns were real dilemmas (`dilemma_turns`) and skip forced turns. If `notes` mentions hindsight or a dropped regret, leave the regrets out. Do not invent numbers.
1a. With a cast (STORY 3 or 4), two lines of epilogue from `visible.cast`: who came through, who fell and when, and for a saga what became of the want. No speeches.
1b. Log the player's ideas. For every off-menu thing the player tried during the game (fortify, assassinate, split up, go back, trade with someone), append one line to `GM_ROOT\ideas_log.md`: `YYYY-MM-DD | <title> | <the idea in the player's words, short> | caught by <gambit id> / refused`. A refused idea is a gambit the next game of that kind should have. Read the file in Step 4 when writing gambits.
2. Append one line to `GM_ROOT\played_log.md`:
   `YYYY-MM-DD | <title> | FORM=<n> SET=<n> LOOP=<n> TWIST=<n> CURRENCY=<n> | actions=<comma list of action ids> | <win/loss> | <turns played>`
3. Record the fingerprint, silently. Run `python engine.py fingerprint` for the mechanical fields (`actions`, `tracked_count`, `turn_band`; use them as they are). Build one JSON object with `id`, `title`, `date`, `result`, `turns`, `turn_budget`, `actions`, `rolls` (every rolled value, null where not rolled), `traits` (one value for every trait in `GM_ROOT\traits.json`; the mechanical ones from the fingerprint, the rest judged from what happened and not from what you intended) and `primary_number` (the label of the main number as the status line showed it). Run `python GM_ROOT\tools\sameness.py add '<json>'`, then `python GM_ROOT\tools\sameness.py backlog`. Do not show the output to the player unless they ask. If it rejects a value, fix the value; do not skip the step.
4. Ask: `Save this one to the library? Give it a name, or say no.`

On save: run `python engine.py check` once more and save only if it has no flags. Create `GM_ROOT\library\<name>\`, copy `engine.py` into it, and write `rules.md` containing title, premise, rulesheet, rolls, tracked numbers, win and lose conditions, signature detail, and what the seed changes (the engine's `init_state` randomness: layout, prices, rival habit, event order).

## Replay (`/play <name>`)

Copy `GM_ROOT\library\<name>\engine.py` into a new session folder. Run `python engine.py check --quick` first; the harness may have grown stricter since the game was saved, so if it prints flags, fix the engine before playing. Run `python engine.py new` with no seed argument. Present with the saved rulesheet. The engine guarantees the rules are identical; the seed guarantees the game is not.

## Roll tables

### FORM (what a turn physically is) d20

1. Trading run: move, buy, sell, prices drift
2. Management sim: set a few dials, watch a week resolve
3. Tactical skirmish: units on a small grid, fog, counters
4. Blind auction: bid against rivals for lots, see results
5. Deduction: gather clues, cross-check, name the answer
6. Pursuit: chase or flee a target that moves by hidden rule
7. Build order: construct things that unlock things
8. Survival: meters decay, gather and craft against them
9. Negotiation: offers and counteroffers with parties who have hidden limits
10. Heist: plan phase with limited intel, then execute phase where the plan meets reality
11. Breeding: combine two things, inspect offspring, keep or cull
12. Logistics: route limited vehicles through a network with delays
13. Season: a schedule of matches or events; draft, train, play
14. Tile placement: lay pieces on a board; adjacency scores
15. Programming: write a short sequence of instructions, then watch it run without you
16. Market: hold positions in a few assets with news and drift
17. Triage: a queue of incoming cases, limited slots, costs for waiting
18. Campaign: win votes or favor across districts with limited visits and money
19. Dungeon keeper: you are the defense; place traps and creatures against incoming parties
20. Garden: plant, wait, tend; things grow on their own timers and interact

### SET (where) d60

1. Asteroid belt mining outposts
2. Frontier star cluster
3. Derelict generation ship
4. Trade lanes between rival stations
5. Orc and human borderlands
6. Dwarven undermountain
7. Fey forest that rearranges itself
8. Pirate archipelago
9. Shipwreck atoll
10. Arctic research station
11. Flooded coastal city
12. Expanding river colony
13. Carrier strike group at sea
14. Helicopter wing over a sprawling city
15. Submarine patrol zone
16. Besieged castle
17. Mercenary company in a civil war
18. Floating sky islands
19. Clockwork city of guilds
20. Steppe horse clans
21. Terraforming dome on Mars
22. Nuclear winter bunker network
23. Gold rush boomtown
24. A restaurant kitchen on a Friday night
25. A hedge fund during a bad quarter
26. A hospital emergency department
27. An ant colony under a suburban lawn
28. A television network's prime-time schedule
29. A small town city council
30. A wizard academy's budget office
31. A reality show production
32. The human bloodstream during an infection
33. A coral reef
34. A casino floor
35. A 1920s newspaper
36. A motor racing team's pit wall
37. A beehive in a bad summer
38. An airport control tower
39. A prison yard economy
40. A courtroom
41. A Mars rover's onboard computer
42. A haunted hotel that is still taking bookings
43. An ocean liner's crew deck
44. A record label in 1978
45. A vineyard across one harvest
46. A zoo with a funding crisis
47. A penguin colony through an Antarctic winter
48. A cat cafe
49. A monastery brewery
50. A 1980s arcade
51. A tax office in audit season
52. A volcano observatory
53. A startup with six months of runway
54. A professional wrestling promotion
55. A city bus network
56. A dungeon, seen from the monsters' side
57. A chessboard where the pieces have an economy
58. A dream that is being audited
59. A deck of cards that knows it is a deck
60. A weather system over a farming valley

### ROLE (who you are) d60

1. Freelance cargo pilot
2. Salvage captain
3. Smuggler with a debt
4. Fleet admiral with four ships
5. Warband chief
6. Fortress steward
7. Guild master
8. Caravan master
9. Castaway
10. Colony governor
11. Rail baron
12. Mercenary captain
13. Spymaster
14. Siege engineer
15. Squadron commander
16. Submarine captain
17. Monster hunter
18. Dragon with a hoard to manage
19. Beast tamer
20. Harbor master
21. Head chef
22. Fund manager
23. Triage nurse
24. Ant queen
25. Network programmer
26. Mayor with a hostile council
27. Headmaster
28. Reality show producer
29. A white blood cell
30. A reef
31. Casino pit boss
32. Newspaper editor
33. Race engineer
34. Beekeeper
35. Air traffic controller
36. Prison warden
37. Defense attorney
38. Rover's onboard AI
39. Hotel manager who can see ghosts
40. Cruise director
41. Talent scout
42. Vintner
43. Zookeeper
44. Penguin
45. Cafe owner
46. Abbot
47. Arcade owner
48. Tax auditor
49. Volcanologist
50. Startup founder
51. Wrestling booker
52. Bus dispatcher
53. Dungeon keeper
54. Chess king who must pay his pieces
55. Detective
56. A ghost
57. A minor god with one village
58. A river
59. A crow
60. A vending machine gaining sentience

### LOOP (core verb each turn) d36

1. Buy low, sell high across moving prices
2. Pick a destination, pay a cost, resolve what is there
3. Allocate workers to jobs, see output
4. Build one structure, unlock what it enables
5. Send one expedition out, keep one unit home
6. Scout then strike, fog of war
7. Hold a line against waves, repair between
8. Gather, craft, upgrade one tool
9. Choose a contract, pay a cost, roll the outcome
10. Move on a small map, reveal tiles
11. Train one thing, deploy it
12. Trade favors with factions, spend reputation
13. Ration a shrinking supply across needs
14. Chase a target that moves each turn
15. Bid against rivals for scarce lots
16. Route convoys through danger
17. Research one tech, apply it
18. Capture and hold territory nodes
19. Hunt a boss by reading its tells
20. Manage a queue of incoming emergencies
21. Dig deeper, each layer riskier and richer
22. Recruit, equip, send a squad
23. Repair a failing machine piece by piece
24. Negotiate, bluff, or fight each encounter
25. Set this week's menu, prices, and staffing; serve the rush
26. Fill a schedule grid; slots compete for the same audience
27. Draft or trade one roster piece, then play the round
28. Interrogate one source, cross-check against what you know
29. Write three instructions, run them, see where the machine ends up
30. Breed two, inspect offspring, keep one
31. Place one tile; adjacency and chains score
32. Open, hold, or close one position as news lands
33. Assign incoming cases to limited beds, bays, or desks
34. Visit one district, spend money or time, poll the result
35. Place one trap or creature; a party comes through
36. Plant or tend one plot; everything else grows on its own

### CLOCK (what pressure ends it) d24

1. Fuel or food runs out
2. Enemy arrives on turn N
3. Debt due on turn N
4. Storm season, worsening odds
5. Hull or structure decays
6. Rival is racing to the same prize
7. Plague spreads one node per turn
8. Winter closes the passes
9. Reactor meltdown countdown
10. Unrest rises when ignored
11. Water table drops
12. The map floods tile by tile
13. Heat or wanted level from authorities
14. Crew morale, mutiny at zero
15. Ammunition is finite
16. The target is getting away
17. A deadline from a patron
18. Each turn costs a fixed upkeep
19. Health inspector, auditor, or reviewer visits on turn N
20. Ratings drop each week you fail to deliver
21. The runway: cash burns, investors watch
22. A season of fixed length; standings decide
23. The audience's patience, visible and falling
24. Growth: the thing you manage gets bigger and harder every turn

### TWIST (the thing that makes this one different) d48

1. Prices invert every 5 turns
2. One faction is secretly on your side
3. The map is a ring
4. Everything you abandon becomes an enemy asset
5. You can only carry three things, ever
6. Your rival mirrors your move type each turn
7. Night doubles risk and reward
8. One reusable gadget, recharges every 3 turns
9. Information is the currency
10. One of your units is a traitor; clues each turn
11. Damage is permanent
12. Weather rolled each turn changes the rules
13. You may bank one action to spend later
14. Each location can only be visited once
15. The enemy learns your last choice and counters it
16. Your home base moves
17. Gold is heavy; carrying more slows you
18. Two currencies at a shifting rate
19. Every third turn is an auction
20. Your crew has opinions; ignoring them costs
21. A wandering threat hunts whoever is richest
22. Tech you research leaks to rivals two turns later
23. Something is where it should not be
24. You start with a huge advantage that decays
25. You can sabotage instead of compete
26. Rumors are half true; you decide which to chase
27. One resource is sentient and resists being used
28. The clock can be paid off with the win resource
29. Allies demand a cut of everything
30. Your character is slowly transforming
31. A disaster is coming; you know when, not where
32. Every victory makes the next fight harder
33. You can trade turns for resources
34. The world reacts to your reputation with a single word that changes
35. Hidden objective revealed at the halfway mark
36. Cooperative; an NPC partner acts on their own
37. Information arrives one turn late
38. You only ever see averages, never individual results
39. The rules change on a published schedule
40. Every item has a hidden second use
41. One NPC always lies; you do not know which
42. The currency inflates every turn
43. You are the villain of the story being told
44. Your opponent is your own choices from the first half, replayed
45. Double-blind: your rival bids at the same time, revealed together
46. You control the environment, not the people
47. The board is a calendar; position is time
48. What you name a thing changes what it does

### WIN (what counts as winning) d20

1. Reach a credit or gold target
2. Reach a location and get out
3. Survive the clock
4. Destroy or expose a named enemy
5. Build a specific final structure
6. Hold the most nodes when the clock ends
7. Deliver a cargo intact
8. Majority with three factions
9. Fully upgrade one thing
10. Escape with a crew of at least N
11. Map the whole board
12. Outscore a rival on a visible tally
13. Complete three of five contracts
14. Keep a settlement above a threshold until the end
15. Name the culprit with two pieces of evidence
16. Finish the season above .500 or win the final
17. Balance the budget with the reviewer satisfied
18. Reach a rating, review score, or approval number
19. Produce one specimen with all three traits
20. Get the machine to the exit square

### MAP (board shape) d14

1. Linear track of 10 stops
2. Hex ring of 8 around a center
3. 5 by 5 grid, fog
4. Star graph: hub and 6 spokes
5. Two layers: surface and below
6. Branching river delta
7. Three islands and the sea between
8. Single location with 6 districts
9. A line of 6 nodes that shifts each turn
10. No map; a deck of encounters
11. A weekly calendar grid, 7 by 3 slots
12. A bracket or league table
13. A single room with named stations
14. A 4 by 4 board you fill in

### TONE d12

1. Grim and practical
2. Dry humor
3. Pulp adventure
4. Hard sci-fi
5. Mythic
6. Military procedural
7. Weird and uncanny
8. Cozy with teeth
9. Workplace comedy
10. Nature documentary
11. Noir
12. Deadpan bureaucratic

### FINISH (how the last third resolves) d4

Never flat. The generator designs the last third for the rolled shape; `profile` warns on FLAT FINISH and the autopsy reports the turn the game was decided.

1. Final-roll: one decisive late roll whose odds the player bought over the game (a trial, a storm crossing, a launch)
2. Photo-finish: two numbers converge and the margin is one or two (the rival's tally and yours, the deadline and the delivery)
3. Collapse: an escalation the player can slow but not stop; the win is getting out before it takes everything
4. Cliff: a hard event on a known turn the player plans around (the gates close, the inspector arrives, the ice breaks)

### STORY (how much of a story the game carries) d4

1. Lean: numbers and functional NPCs (a job board, a price, a rumor), as the taste profile says
2. Lean, the same
3. Cast: four to six named people owned by the engine (`gm_cast.roster`), each with a role and one tell; losses name who fell; the opening screen lists them under "Your people"; the GM answers who and what questions from the cast
4. Saga: the cast plus one want (a cast member's or the rival's) that surfaces by the midpoint, that a gambit or a loop move can serve or spend, and that the epilogue settles

### CURRENCY (what the primary tracked number is) d12

The number the player spends, hoards and fights over. Name it in the game's own words (hours become "daylight", trust becomes "goodwill"). Only roll 9 may use money as a tracked number.

1. Time: hours, days or ticks left in the shift
2. Trust: what others will let you get away with
3. Attention: who is watching, who is listening
4. Heat: suspicion, wanted level, notoriety (spent by acting, lowered by lying low)
5. Stock: physical goods on hand
6. Light: daylight, battery, visibility
7. Slots: beds, bays, seats, room
8. Energy: stamina, fuel, charge
9. Cash: money
10. Nerve: composure, sanity, morale
11. Evidence: leads, proof, intel
12. Standing: rank, reputation, votes
