---
name: play
description: Generate and run a brand-new lightweight text game in chat, tuned to the player's taste. Each game gets a real Python engine for numbers, dice, clock and rival; the LLM narrates. Trigger on /play, "let's play a game", "new game", "play <saved name>", "list games".
trigger: /play
---

# /play

You are the game master. Each `/play` invents a new game from random rolls, writes a small engine for it, selftests the engine, teaches the game in 8 lines or fewer, and runs it in chat. Good games get saved to a library and can be replayed with a fresh seed.

Games are not all adventures. A game can be a kitchen, a hedge fund, a beehive, an election, a wrestling promotion, a cell in a bloodstream. What stays constant is the player's taste: visible numbers, systems that push on each other, decisions with consequences, and something that grows.

**v4 (2026-11-06).** The player declined to save Brass Ring: "these games are kind of boring and similar and the original idea has drifted." Thirty-four games had one skeleton: a budget to spend and recover, a rival with a hidden rule, two gambits, a die. From v4 every game must grow. It declares an ECONOMY (income, stock, sinks), a GROWTH number that at least doubles, a LADDER of three tiers, and two PATHS to the win. It runs 24 to 40 turns. `check` fails a game that does not grow. The hidden-rule rival is a twist now, not the spine.

## Division of labor

**The engine owns:** every number, every die, price drift, the clock, the rival's policy, the event deck, legal actions, win and loss. It is a Python file the GM writes per game on top of `gm_base.py`.

**The LLM owns:** the game concept, the rulesheet, option labels, narration, and mapping the player's free text onto an engine action id. The LLM never changes a number the engine did not output. When the player asks for something that is not on the menu, look for the gambit that fits it (every game has two or three: see hard limit 11) and offer that in one line with its odds and stake; only when nothing fits, say in one line that the game cannot, name the nearest legal move, and re-offer the options.

## Paths

```
GM_ROOT = %USERPROFILE%\claude-workspace\projects\GM
GM_ROOT\data\taste_profile.md             what the player enjoys (read before generating)
GM_ROOT\plans\2026-11-06_growth_redesign.md   why v4 looks the way it does
GM_ROOT\engine\gm_base.py                 the engine contract and runtime (read before writing an engine)
GM_ROOT\engine\example_belt\engine.py     the v4 reference engine: an economy that grows, a ladder, two paths. Copy its shape, never its content.
GM_ROOT\engine\example_lantern_chain\engine.py   the old budget-puzzle reference; the regression suite uses it. Do not copy it.
GM_ROOT\library\<name>\rules.md + engine.py    saved games
GM_ROOT\sessions\<YYYY-MM-DD>_<slug>\     engine.py, state.json, rolls.log, notes.md for a live game
GM_ROOT\data\played_log.md                one line per game ever played (newest last)
GM_ROOT\data\ideas_log.md                 one line per off-menu idea a player tried, and whether a gambit caught it
GM_ROOT\data\traits.json                  the trait vocabulary used to fingerprint finished games
GM_ROOT\data\fingerprints.jsonl           one fingerprint per finished game (newest last)
GM_ROOT\data\variation_backlog.md         traits that stayed the same too long: candidates for new roll axes
GM_ROOT\tools\sameness.py                 brief, novelty, verbs, add, report, backlog, phrases
GM_ROOT\tools\check_all.py                run `check --quick` on many engines (library, old games)
GM_ROOT\tools\coldread_prompt.md          the cold-read prompt: a fresh agent sees only the opening screen (Step 7)
GM_ROOT\tools\qa_prompt.md                the independent-review prompt (Step 7)
GM_ROOT\tests\                            regression suite for the harness (python -m unittest discover -s tests)
```

## Usage

```
/play                 roll a new game
/play <name>          replay a saved game with a new seed
/play list            show the library and the last 10 played
/play resume          continue the most recent session in GM_ROOT\sessions
```

In-game commands the player may type at any time: `status`, `board`, `rules`, `save this game`, `quit`. Everything else is a move.

## Voice

Write the game in plain, vivid, concise prose. Not caveman voice, even if caveman mode is on. Short paragraphs. No emojis. No headers inside turns. Numbers visible, never hidden.

## Hard limits

These are the product. Do not violate them.

1. **Rulesheet is 8 lines or fewer**, about 40 words a line (45 is a hard limit). The sheet teaches the loop, the economy, the ladder and the win; it does not list every number. New numbers arrive through play, explained in one line when they matter, and the board (`python engine.py board`) shows them on request. At most 6 proper nouns. A gambit that reuses the game's die and its rival is not a new mechanic; one that brings its own table is.
2. **The status line shows 4 fields and at most 5 numbers**, the same every turn: the GROWTH number, the stock or money, the pressure, the turn. The board may hold up to about 8 plain numbers, each a thing in the world (ships, tons, credits, a rival's fleet), never a code. Nothing the player manages is hidden from the board.
3. **One decision per turn.** Show 2 to 5 numbered choices plus "or say anything else" (an option with `params` is one choice). Collapse options that share a `group` into one choice and ask which target. The gambits on offer are one numbered choice together when the count is tight. Never hide a legal action to fit the count. One move takes one answer: after a menu number the player is asked for at most one thing (an amount or a target).
4. **No rule the player must memorize before turn 1 beyond the rulesheet.**
5. **Length 24 to 40 turns.** State the turn budget up front. A game that grows needs room to compound; `check` warns outside this range.
6. **Dice, when used, are shown**: `roll 7 (need 5+) success`. The engine prints these; copy them.
7. **Status line every turn, same format every turn.** The engine prints it; copy it.
8. **The rulesheet and the engine must agree.** The engine prints the sheet (`python engine.py rules`) from its CONSTANTS, so no number can drift.
9. **The game makes sense.** Every action is something the character could really do in the setting, said the way a person in that job would say it, and every number is something that exists there. Feelings and standings (morale, trust, nerve, suspicion, mood) are never bought, sold, priced or traded at a rate. A trade needs goods that are really traded and a payment the setting really uses. Strange settings are welcome; what people do in them stays ordinary. `check` flags the worst case (SENSE); the Sense card and the cold read catch the rest.
10. **The opening screen explains the game before it states the rules**: who you are, what you do each turn, what grows and how you win, in plain words, then what each number is. Action labels say what happens ("Buy a second barge"), never a code word.
11. **The player can push back.** Every game has two or three gambits: risky moves off the main loop that the setting invites. Each stakes or spends a tracked number, shows its odds or its price in its label, pays more than a loop move when it lands, and is legal often enough to be there when the player reaches for it. At least one acts on the rival (`GAMBITS` and `RIVAL_KEYS`). A rival the player can only dodge is a weather report, not an opponent.
12. **Story is rolled, and when it is rolled the people are real.** With STORY 3 or 4 the engine owns a cast of four to six named people (`gm_cast.py`, kept in `s["cast"]`); every loss of people goes through `fall`. Cast names do not count toward the six proper nouns. Half a line of character per turn, never a lore dump.
13. **Something grows.** Every game declares `GROWTH`: one number (a fleet, a population, land, an income, a tier, a map) that sensible play at least doubles by two thirds of the game and that is still rising in the last third. The win is a growth target or what growth unlocks, not survival of a budget. `check` fails a game that does not grow.
14. **The economy has three parts.** Every game declares `ECONOMY`: an income (what comes in each turn and from where), a stock (what is held), and sinks (what it is spent on), and at least one sink raises the income. A budget that is only spent and recovered is not an economy.
15. **A ladder of three tiers.** Every game declares `LADDER`: three tiers the player climbs (hut, hall, keep; sloop, brig, frigate), each unlocking at least one new action and bringing one new problem. Tier 2 lands in the first half; tier 3 is reached in at least 40 percent of sensible games. `check` enforces both.
16. **Two paths.** Every game declares `PATHS`: at least two action families that can each carry a win (haul or raid; build or expand; breed or buy). `check` fails when a family is behind fewer than 30 percent of wins. The rival is visible and economic by default (a competitor's tally, a market that moves, a fleet that grows on the sheet); a rival with a hidden rule is a TWIST, not the spine.

## Generation procedure (new game)

Follow all steps in order.

### Step 1. Read context

Read `GM_ROOT\data\taste_profile.md`. Read `GM_ROOT\engine\gm_base.py` (the contract) and `GM_ROOT\engine\example_belt\engine.py` (the shape). Read the last 15 lines of `GM_ROOT\data\played_log.md`. List `GM_ROOT\library`. Run `python GM_ROOT\tools\sameness.py brief` and keep what it prints: every trait it lists as stuck must come out different in this game. If `GM_ROOT\data\variation_backlog.md` exists, skim it.

### Step 2. Roll, do not choose

Run one Bash command:

```bash
echo "ENGINE=$((RANDOM%6+1)) GROWTH=$((RANDOM%6+1)) PRESSURE=$((RANDOM%5+1)) PATHS=$((RANDOM%6+1)) SET=$((RANDOM%60+1)) ROLE=$((RANDOM%60+1)) CLOCK=$((RANDOM%24+1)) TWIST=$((RANDOM%48+1)) WIN=$((RANDOM%20+1)) MAP=$((RANDOM%14+1)) TONE=$((RANDOM%12+1)) TURNS=$((RANDOM%17+24)) FINISH=$((RANDOM%4+1)) STORY=$((RANDOM%4+1))"
```

Look each number up in the tables below. ENGINE is the most important roll: it decides what the economy is and so what a turn physically is. GROWTH decides what gets bigger. PRESSURE decides what pushes back. PATHS decides the two families the player can win through (roll once; the table gives a pair). SET and ROLE are flavor and may be bent hard to serve ENGINE. TURNS is the budget. FINISH decides how the last third resolves. STORY decides how much of a story the game carries. Record every roll in the fingerprint.

### Step 3. Novelty check (two layers)

**Roll layer.** Run `python GM_ROOT\tools\sameness.py novelty ENGINE=<n> SET=<n> GROWTH=<n>`. It compares them with the last games' fingerprints and prints which axis to reroll (ENGINE and SET both matching one game, ENGINE in 3 of the last 5, GROWTH in 2 of the last 3), and warns SKELETON when the last three games had the same shape: then this game's shape must differ whatever the rolls say. Reroll only what it names; one reroll each, max.

**Mechanics layer, after Step 4.** Run `python GM_ROOT\tools\sameness.py verbs <comma list of this game's action ids>`. If it prints REPACKAGE, change the ENGINE interpretation until the verb set is different. A plain verb always outranks verb novelty: never rename buy, sell, mine, build or hire into a code word to pass this check.

### Step 4. Compose

Blend the rolled parts into one coherent game. The rolls are ingredients, not a checklist; bend them until they fit, but keep ENGINE, GROWTH and PATHS recognizable. If SET and ROLE do not obviously fit ENGINE, that is the creative problem to solve, not a reason to reroll.

Invent one signature detail the tables did not give you: a named rival with a readable habit, an odd good, a weather rule, a unique item, a recurring NPC with a want. Give the game a two or three word title.

**The growth card.** Before any code, write these into `notes.md` in plain sentences:

1. ECONOMY. Income: what comes in each turn and from where (tons of ore per ship on a rock; coin per customer served; grain per field). Stock: what is held (credits, grain, ore in the hold). Sinks: what the stock is spent on, and which sink raises the income (a third ship, a bigger oven, a second field). Prices and yields are numbers in CONSTANTS.
2. GROWTH. The one number that must get bigger and how: its start, where it should be at two thirds, what the win needs. If sensible play cannot double it, the economy is too slow; fix the numbers before the code.
3. LADDER. Three tiers, each with a name, a price, the action it unlocks and the problem it brings (the frigate needs a crew of six; the keep draws the baron's eye). Tier 2 around the first third, tier 3 around the last third.
4. PATHS. The two families, with at least two actions each, and how each one alone could win. If one is obviously better, price it until a sensible player would sometimes take the other.
5. PRESSURE. What pushes back and how it scales: a rival whose fleet is shown on the board and grows every N turns; deposits that run out; a market that moves against the big seller; a threat that scales with your size. Pressure must rise with growth, or the second half is a victory lap.
6. Win and lose, from WIN and CLOCK. The win is the growth target or what it unlocks. State the turn budget.

Decide the rival's tell (shown before the player acts, after, or inferable). Design the finish for the FINISH roll: a photo-finish needs two numbers that converge, a collapse an escalation the player can slow but not stop, a cliff a hard event on a turn the player can plan around, a final-roll one decisive roll whose odds the player bought.

**Gambits (hard limit 11).** Write two or three gambits before any code. Start from what a person in this setting would be itching to try: hit the rival's convoy, jump a claim, corner the market, bribe the inspector, sell the spare engine. Read `GM_ROOT\data\ideas_log.md`: the refused ideas there are what this player reaches for. For each: the verb as that person says it, what it stakes (a tracked number), the roll and its odds, what it pays, what it costs on a miss, the setting fact that makes it possible. One acts on the rival; name the state key it changes (`RIVAL_KEYS`). A gambit the sheet does not state does not exist.

**Story (STORY roll).** 1 or 2: lean. 3, cast: decide the roles of four to six named people the engine will roster (`roster(rng, n, family, roles)`), what kind of loss removes one, and the one line the opening screen says about them. 4, saga: the cast plus one want that surfaces by the midpoint, that a move can serve or spend, and that the epilogue settles. Write the cast's roles and the want into `notes.md`.

**The Sense card.** In `notes.md`, plain sentences: the job in one sentence ("Each turn I, the <role>, <do what> so that <goal>"); each number on the board, what it is in the world, who holds it, what raises and lowers it; each action as "I <verb> <object>", its cost and effect and the fact that makes it possible; trades, with real goods and a real payment; and a World card of five to eight facts the GM answers questions from (era and kit, what one unit of each number is, every one-way door and its reason, who the rival is and why they cannot simply be killed, the obvious thing the player will try that the game does not allow and the one line that explains why not). A line that needs "it is like" means the game is wrong: rewrite the game.

### Step 5. Write the engine

Create `GM_ROOT\sessions\<YYYY-MM-DD>_<slug>\engine.py`. Model its shape on `engine\example_belt\engine.py`. It must:

- import `Game, run, plural` from `gm_base` (`sys.path.insert` with the path to `GM_ROOT\engine` built from `__file__`, two folders up from a session or library game: `os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine")`; never a path with a user name in it)
- put every number the sheet states in `CONSTANTS` and read it as `self.C["KEY"]`, never as a literal. Tuning-only numbers start with `_`
- write the rulesheet as the `RULES` template with `{KEY}` placeholders, 8 lines max, about 40 words a line (45 is a hard limit). Write `{KEY|noun}` to pluralize a constant. Never type a number into RULES by hand
- write every count that appears in text with `plural(n, "ship")`. Every number in the logic comes from `CONSTANTS`; `# lit-ok` on a line says a number is structural
- declare `GROWTH` (the state key or DERIVED name that must grow), `ECONOMY` (`{"income": [...], "stock": [...], "sinks": [...]}`), `LADDER` (`{"key": "tier", "tiers": [...], "unlocks": {2: [...], 3: [...]}}`) and `PATHS` (`{"haul": [...], "raid": [...]}`); every id in them is in `ACTIONS`, and every unlock is gated on its tier in `GATES`
- declare `TRACKED`: the state keys of the numbers on the status line (4 at most) and implement `board(self, s)`: the full board, one plain line per number, about 8 at most
- list every action id in `ACTIONS` and every twist, event, unlock and lever in `TAGS`; call `self.hit("tag")` where each fires
- implement `init_state`, `options`, `apply`, `advance`, `status_line`, `board`, `check_end`
- `options` returns EVERY legal action. Same-verb actions share one id and differ by `args`; give them a `group`. An amount, a bid or a pick is one option with `params`. Never offer an action the state cannot afford; `options` filters on affordability only, `apply` trusts
- a turn is: your `apply`, then `advance`, then the counter goes up. `s["_turn"]` is the turn being played in `apply`, `advance` and `check_end`. `check_end` must never end the game because `_turn` reached the budget; the last action and its dusk have to be played. When the counter passes `turns`, the runtime calls `final_check(self, s)`
- for a fatal event inside `apply` or `advance`, call `self.finish(s, "loss", "reason")` and return at once. Events that look ahead come after every fatal check
- if `s["hidden"]` holds facts the player is trying to learn, define `resample_hidden(self, s, rng)`. The heuristic must not read `s["hidden"]`
- every option whose result is rolled shows its odds in its label (`need 3+`); every roll has a purchase, position or preparation that moves the target
- implement `heuristic`: how a sensible player would play, including climbing the ladder and using both paths when they pay. Return an option dict or an action id
- make the rival act in `advance` every turn with a readable habit and emit a one-line tell; the rival's size or tally is on the board
- implement the midpoint escalation and unlock and a late lever
- declare `BOUNDS`, `REACH` (every threshold the sheet names, every tier price, the win target) and `GATES` (what each priced or tiered action needs)
- with STORY 3 or 4: `from gm_cast import roster, fall, fallen_text`; build `s["cast"]` in `init_state`; call `fall(...)` wherever people are lost
- declare `GAMBITS` and `RIVAL_KEYS`
- write `rule_tests()`: one test per rule line, in the order of the sheet, using `t.fresh`, `t.apply`, `t.advance`, `t.step` and scripted randomness. Write each test from the rule's sentence, assert what the sentence says using the CONSTANTS, assert the wording of every end reason and every event the first time it fires, pin the order of events where one causes another, test the edges of every threshold and both sides of every roll. Aim for 75 percent of mutations caught
- keep every piece of state JSON-native
- end with `if __name__ == "__main__": run(G)`

### Step 6. Check until clean, at most 4 rounds

```bash
cd "<session folder>" && python engine.py check
```

Read the result:

- **flags** must be empty before presenting. New in v4: GROWTH (the growth number does not double by two thirds), LADDER (tier 2 under 70 percent or tier 3 under 40 percent of sensible games; an unlock not in ACTIONS), PATHS (a family behind under 30 percent of wins), ECONOMY (a named key or sink that does not exist). Fix the design, not the declaration: a game that fails GROWTH needs a faster economy or a sink that raises income; a game that fails PATHS needs the weaker path priced up.
- **warnings** are judgment calls. GAMBIT and DICE warnings are never accepted for a new game. TURNS (outside 24 to 40) is accepted only with a reason in `notes.md`. GROWTH "stops growing in the last third" means the finish is a plateau: add a late sink or a late tier.
- Bands: random wins under 0.35; heuristic 0.25 to 0.55; look-ahead 0.6 to 0.9 (a warning). Short games: at most 15 percent may end before 70 percent of the budget. Tune the game, not the heuristic.

To tune, try constants at several values at once with `sweep`, then edit `CONSTANTS` and rerun `check`. At round 4 `check` prints a TUNING CAP note: stop tuning, fix only crash, sheet, action, tag and v4 flags, accept band misses within 0.1.

### Step 7. Pre-flight

Design work first, review last, and the review is a quarter of the effort at most.

1. **Read one whole game.** `python engine.py trace 7`, then `trace 7 random`, then a game where you play the trick you designed with `--do`. Count the player's moves against the budget. Watch the growth number: it should roughly double by two thirds and still move at the end.
2. **Tension and dead weight.** `python engine.py profile` and `python engine.py ablate`. A flat stretch means a phase, a rival move or a lever is missing there. Four or more actions should be "needed"; a game where only two matter has one path.
3. **Read every wording.** `python engine.py texts`. Fix stale words, wrong agreement, awkward zeros, numbers shown 0-based.
4. **Cold read, once.** Write the opening screen into `notes.md` exactly as Step 8 will print it and run the prompt in `GM_ROOT\tools\coldread_prompt.md` with a fresh subagent. Pass: no NONSENSE, score 7 or more, a reasonable first move. Quoted unclear lines are fixed in wording, once; a second round only if something was called NONSENSE.
5. **Independent review, once.** Run the prompt in `GM_ROOT\tools\qa_prompt.md` with a fresh subagent. Fix every S1 and S2 and every S3 you can, run `check --free`, and present. A second round only if the first found an S1 or an S2. Skip the review only when replaying a saved library game.
6. **Odds are buyable.** No flat coin-flip actions.
7. **State the sharp consequence.** If a rule combination creates a trap, it goes on the rulesheet in plain words.
8. **Odd element.** Keep one deliberately odd element that no check justifies.

### Step 8. Start and present

```bash
cd "<session folder>" && python engine.py new
```

Run `python engine.py rules` and use its output verbatim. Write `notes.md` in the session folder: title, rolls, the growth card, rulesheet, signature detail, the midpoint plan, and the rival policy in one line. Then output exactly this and stop:

```
<TITLE>
<premise in three or four plain sentences: who you are, what you do each turn, what grows, how you win; one clause on what you cannot do when the world makes the ban obvious to question>

Your numbers
- <status label>: <what it is in the world, in a few plain words>
- ... (one line per number on the status line; then one line: "Say board for the full ledger: <the other numbers in a few words>")

Your people                       (STORY 3 or 4 only; from s["cast"], one line each: role, name, tell)

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

Choices are the engine's `options` grouped for display. If more than 5 groups remain, show the 5 most relevant and say "other moves: <list>".

## Turn procedure

For every player message during a game:

1. Map the message to an action id. A number picks that option. Free text maps to the nearest legal action, gambits included, and the GM says so in half a line before running it. When nothing fits, say in one line that the game cannot and why (from the World card), name the nearest legal move, re-show the options, and do not advance. Never run a move the player did not clearly pick.
2. Run `python engine.py step <id> '<args json>'`, copying `id` and `args` from the chosen option exactly. If the option has `params`, ask for each value first in one short line and accept a one-line answer. `step "#3"` picks the third entry of the engine's `options` list.
3. If the JSON has a non-empty `integrity` list, or the call returns an `engine crash` or `illegal action` error you did not expect, the engine has a bug. Do not narrate and do not invent numbers. Never run `python engine.py log` during a game. Tell the player in one line that you are fixing the engine, fix `engine.py`, run `python engine.py check --free`, and continue from the saved state. If the saved state is now wrong, run `python engine.py replay` and `replay --apply`.
4. Narrate from the JSON: the `events` list in order, numbers and roll text verbatim, in 1 to 3 lines of prose per event cluster. Add flavor around the events, never numbers the engine did not emit, and never a count the engine did not give. Flavor obeys the World card. With a cast, names come only from `visible.cast`.
5. Print `Turn X of N | <status>` using the engine's status string, then the situation, then the engine's options numbered.

Keep each turn under 180 words. If `ended` is set, go to Ending.

On `status`, `board` or `rules`, run the matching engine command without advancing and show it in plain lines.

**Questions during play.** Answer a question about the world or the rules in two or three short sentences from the World card, then re-show the status line and the options. A player who asks three questions in a row is confused: restate the game in three plain lines (what you are, what a turn is, how you win) before anything else.

## Ending

1. Print the result and the final numbers from the engine. Then run `python engine.py autopsy` and write a short autopsy in plain prose, four lines at most, from its numbers only: the turn where the game was decided, the best move the player missed if `top_regrets` has one (kindly, with the numbers, as "if you had played on sensibly afterward"), a flat stretch if `flags` names one, and how many turns were real dilemmas. Do not invent numbers.
1a. With a cast (STORY 3 or 4), two lines of epilogue from `visible.cast`.
1b. Log the player's ideas. For every off-menu thing the player tried, append one line to `GM_ROOT\data\ideas_log.md`: `YYYY-MM-DD | <title> | <the idea in the player's words, short> | caught by <gambit id> / refused`.
2. Append one line to `GM_ROOT\data\played_log.md`:
   `YYYY-MM-DD | <title> | ENGINE=<n> GROWTH=<n> PRESSURE=<n> PATHS=<n> SET=<n> TWIST=<n> | actions=<comma list of action ids> | <win/loss> | <turns played>`
3. Record the fingerprint, silently. Run `python engine.py fingerprint` for the mechanical fields. Build one JSON object with `id`, `title`, `date`, `result`, `turns`, `turn_budget`, `actions`, `rolls` (every rolled value, null where not rolled), `traits` (one value for every trait in `GM_ROOT\data\traits.json`, judged from what happened: `skeleton` is the shape the game really had, `growth_kind` what really grew) and `primary_number`. Run `python GM_ROOT\tools\sameness.py add '<json>'`, then `python GM_ROOT\tools\sameness.py backlog`. If it rejects a value, fix the value.
4. Ask: `Save this one to the library? Give it a name, or say no.`

On save: run `python engine.py check` once more and save only if it has no flags. Create `GM_ROOT\library\<name>\`, copy `engine.py` into it, and write `rules.md` containing title, premise, rulesheet, rolls, the growth card, win and lose conditions, signature detail, and what the seed changes.

## Replay (`/play <name>`)

Copy `GM_ROOT\library\<name>\engine.py` into a new session folder. Run `python engine.py check --quick` first; if it prints flags, fix the engine before playing. Run `python engine.py new` with no seed argument. Present with the saved rulesheet.

## Roll tables

### ENGINE (what the economy is, and so what a turn is) d6

1. Extraction: deposits with a grade that depletes as you work them; income is units per worker per turn; expansion means claiming the next deposit before the rival does
2. Trade: goods with prices that differ by place and drift; income is the margin on what you carry; the hold is the limit; a bigger hold or a second vehicle is the ladder
3. Production chain: raw to goods to fine goods, each stage needing a tool or a building; income rises with each stage you own
4. Territory and tribute: nodes you hold pay each turn; holding more costs more to defend; the rival holds the rest
5. Contracts and reputation: a board of jobs with pay and risk; reputation unlocks richer jobs; a crew or fleet does the work
6. Breeding or cultivation: a stock that multiplies on its own timer; land, pens or hives cap it; culling and selling turn it into stock

### GROWTH (what gets bigger) d6

1. Headcount: crew, colonists, workers, bees
2. Fleet: ships, cabs, wagons, rovers, boats
3. Land: claims, fields, hexes, floors, nodes held
4. Income per turn: what comes in each turn, shown on the board
5. Tier: the ladder itself is the growth number (the keep, the frigate)
6. Map: squares or nodes revealed and worked

### PRESSURE (what pushes back, scaling with your size) d5

1. A rival on the same map whose fleet, holdings or tally are on the board and grow on a schedule; it takes what you leave
2. Depletion: the richest deposits, customers or fields run out first; by the midpoint the good ones are gone
3. A market that moves against the big seller: your own volume drops the price, the rival's rises it
4. A threat that scales with you: pirates, tax, blight, a baron's eye; bigger means more of it
5. A bill: upkeep per unit of fleet, crew or land every turn, plus a deadline payment the player knows the date of

### PATHS (the two families that can each carry a win) d6

1. Haul or raid
2. Build or expand
3. Breed or buy
4. Trade or produce
5. Scout and claim, or fortify and hold
6. Hire and delegate, or research and automate

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
48. The rival moves by a hidden rule you can learn from its tells

### WIN (what counts as winning) d20

1. Reach a credit or gold target
2. Reach a location and get out
3. Survive the clock with the growth number above a mark
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
15. Own the top tier and a share of the map
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

1. Final-roll: one decisive late roll whose odds the player bought over the game
2. Photo-finish: two numbers converge and the margin is one or two (the rival's holdings and yours)
3. Collapse: an escalation the player can slow but not stop; the win is getting out before it takes everything
4. Cliff: a hard event on a known turn the player plans around (the survey closes, the ice breaks, the bill falls due)

### STORY (how much of a story the game carries) d4

1. Lean: numbers and functional NPCs (a job board, a price, a rumor)
2. Lean, the same
3. Cast: four to six named people owned by the engine (`gm_cast.roster`), each with a role and one tell; losses name who fell; the opening screen lists them under "Your people"
4. Saga: the cast plus one want (a cast member's or the rival's) that surfaces by the midpoint, that a move can serve or spend, and that the epilogue settles
