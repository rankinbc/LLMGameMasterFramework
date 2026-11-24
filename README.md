# GM: a game master that writes a new game every time you ask

Type `/play` in Claude Code and you get a text game that did not exist a minute ago. It is rolled from dice tables, built as a real Python engine, attacked by an automated test harness, reviewed by a fresh agent that has never seen it, and only then dealt to you in chat.

The model narrates. It never does the arithmetic.

```
T7 | Fleet 3 v Kessler 4 | Credits 44 | Ore 8 | Price 2 a ton
  do: Raid a Kessler barge (roll 4+: Kessler -1 ship, +8 tons; miss: you lose the ship)
    - roll 6 (need 4+) raid success. Your boarders take a Kessler barge and its 8 tons;
      its crew limps home in the lifeboat. Kessler's fleet is 3.
    - Your ships dig 8 tons: Rock 6 3, Rock 8 5.
    - Kessler digs beside you on Rock 8.
    - Rock 8 is worked out.
```

That is turn 7 of Belt Claim, the reference game: you run a two-sloop mining outfit against a rival whose fleet grows on a schedule, and you have 32 turns to out-build or out-raid him before the survey closes.

## What it is

A Claude Code skill and a Python framework that generate, test and run text games.

Each `/play` produces a new game in two parts: a Python engine that holds the state, the dice and the rules, and a model that narrates what the engine reports. The framework supplies the engine base class, a command line for playing a game, and a test harness that every generated game must pass before it is played.

The two parts have fixed jobs:

| The engine owns | The model owns |
|-----------------|----------------|
| Every number and every die | The concept and the setting |
| The clock and the turn budget | The rulesheet wording and option labels |
| The rival's policy | Narration |
| Legal actions, win and loss | Mapping what the player types onto an engine action |

The model never changes a number the engine did not print. Each turn it runs `python engine.py step <action>`, reads the JSON that comes back, and tells you what happened. Dice are always shown: `roll 7 (need 5+) success`.

## What a `/play` does

1. **Reads the player.** `data/taste_profile.md` distills eleven favorite games (Counter-Strike 1.6, StarCraft, Warcraft II, Cities: Skylines, Escape Velocity and others) into the mechanics they share: economies that snowball, deposits that run out, ladders to climb, more than one way to win.
2. **Rolls, does not choose.** Fourteen dice pick the economy, what grows, what pushes back, the two winning paths, the setting, the role, the clock, a twist, the win, the map, the tone, the length, the finish and how much story the game carries. A game can be a kitchen, a hedge fund, a beehive or an election.
3. **Checks for novelty.** A sameness detector compares the rolls and the verbs with every earlier game and names what to reroll.
4. **Writes an engine.** One Python file on top of `engine/gm_base.py`, declaring its constants, rules, actions, economy, ladder, paths and gambits.
5. **Tunes it.** `python engine.py check` plays hundreds of games with three policies and fails the engine on anything from a crash to a win path nobody uses. At most four tuning rounds.
6. **Gets it reviewed.** One fresh agent sees only the opening screen and says what it thinks the game is. Another plays it three times, sends bad input and compares the rulesheet with the code.
7. **Runs it in chat.** One decision per turn, a status line that never changes shape, a rulesheet of eight lines or fewer.

A finished game the player likes goes to `library/` and can be replayed with a fresh seed.

## Every game must grow

Thirty-four games in, the player turned one down: "these games are kind of boring and similar." The fingerprints agreed. All thirty-four had one skeleton: a budget to spend and recover, a rival with a hidden rule, a die at the end. The game in question had passed every check, seven cold reads and three review rounds. The harness measured clean and balanced; it could not measure dull.

Version 4 made growth part of the contract. An engine now declares four things, and `check` proves each one by playing:

| Declaration | What it says | What `check` fails |
|-------------|--------------|--------------------|
| `GROWTH` | One number that gets bigger: a fleet, a herd, land, income | Sensible play does not double it by two thirds of the game |
| `ECONOMY` | An income, a stock, and sinks, one of which raises the income | Parts that are named but do not exist in the state |
| `LADDER` | Three tiers, each unlocking an action and bringing a problem | Tier 2 or tier 3 out of reach |
| `PATHS` | Two families of action that can each carry a win | The second path is behind fewer than 30 percent of wins |

Games run 24 to 40 turns so there is room to compound. The full reasoning is in `plans/2026-11-06_growth_redesign.md`.

## The harness

`check` is the part that makes generated games trustworthy. It runs on every new engine before a player sees it.

- **Three players.** A random policy, a heuristic one and a look-ahead one each play the game many times. Random should win under 35 percent, heuristic 25 to 55, look-ahead 60 to 90. A game random play can win is not a game; a game look-ahead cannot win is not fair.
- **Universal bug checks.** JSON round trip of the state, text and plural lint, gates, reachability, the end check at the turn budget, fuzzing with bad input, determinism from a seed.
- **Sheet audit.** The rulesheet is printed from the engine's own `CONSTANTS`, so a number in the rules cannot drift from the number in the code.
- **Coverage.** Hidden actions, unreachable twists and dice a sensible player never meets are all reported.
- **Sense.** A game that prices a feeling (morale, trust, nerve) or uses a code word for an action is flagged. This check exists because a game once sold crew morale at four "consoles" and passed everything else.
- **Gambits.** Every game needs two or three risky moves off the main loop, one of them against the rival, and `check` proves that move really changes the rival's numbers.
- **Mutation pass.** The harness mutates the engine and counts how many mutants the game's own rule tests catch.

Here is the reference engine's report, trimmed:

```json
{
 "verdict": "CLEAN",
 "flags": [],
 "warnings": [
  "GROWTH: fleet stops growing in the last third (median 6 at turn 21, 6 at the end); the finish is a plateau"
 ],
 "random":    { "win": 0.0,  "turn_avg": 32.0 },
 "heuristic": { "win": 0.51, "turn_avg": 32.0 },
 "lookahead": { "win": 0.6,  "turn_avg": 32.0 },
 "universal": {
  "fuzz_steps": 4004,
  "gambits": {
   "raid": { "offered_share": 0.68, "played": 483, "rival_touched": 306 },
   "jump": { "offered_share": 0.97, "played": 759, "rival_touched": 366 }
  }
 }
}
```

A flag blocks the game. A warning is read and judged; the one above is accepted and explained in the engine's docstring.

### The harness is tested too

`tests/` holds 137 tests. The suite also builds 42 mutant engines: copies of a reference game with one bug class injected (a rulesheet number that drifted, an action the menu hides, a path nobody can win by, a rival gambit that touches nothing). Each mutant must be caught, and the untouched reference must come back clean. A new bug class starts as a mutant that fails.

## It learns what it keeps repeating

`tools/sameness.py` fingerprints every finished game against a trait vocabulary (`data/traits.json`) and looks for streaks. A trait that stays the same too long lands in `data/variation_backlog.md`, either as a candidate for a new roll axis or as a roll the generator keeps bending back into the same shape. The next `/play` reads the brief and must come out different on every stuck trait.

`data/ideas_log.md` does the same for the player. Every off-menu idea tried in play is logged with whether the game could answer it ("hunt Vass and assassinate him: refused"). Refusals become the gambits of later games.

## Try the reference game

The engine is plain Python with no dependencies outside the standard library.

```
cd engine/example_belt
python engine.py rules          # the rulesheet, built from the engine's constants
python engine.py new 7          # start a game on seed 7; prints turn 1 as JSON
python engine.py board          # every number the player may see
python engine.py step move '{"to": 8}'
python engine.py trace 7        # a whole game played by the heuristic policy, as text
python engine.py check --free   # the full report, without counting a tuning round
```

`new` and `step` write `state.json` and `rolls.log` into the current folder, so play from a scratch copy if you want the repository left clean.

More commands, for tuning and analysis:

| Command | Purpose |
|---------|---------|
| `sweep K=a,b` | Try constants at several values |
| `texts` | Every wording the game can produce, to read once |
| `profile` | Tension per turn: a flat opening, middle or finish |
| `ablate` | Ban each action in turn and see which ones nobody misses |
| `autopsy` | After a game: the swing turn, its cause, the regrets |
| `replay` | Re-run a saved history after an engine fix |
| `log` | Every die rolled, in order |

## Layout

| Path | Purpose |
|------|---------|
| `skill/play/SKILL.md` | The `/play` skill: roll tables, hard limits, the generation procedure |
| `engine/gm_base.py` | The engine contract and CLI runtime; every game subclasses `Game` |
| `engine/gm_checks.py` | The universal bug checks and the rule-test harness |
| `engine/gm_cast.py` | A named cast the engine owns, so "who died" has one true answer |
| `engine/gm_analysis.py`, `engine/gm_mutate.py` | Profile, autopsy, ablate, replay, and the mutation pass |
| `engine/example_belt/` | The v4 reference game |
| `tools/` | The sameness detector, the batch checker, the cold-read and review prompts |
| `tests/` | The regression suite for the harness |
| `data/` | The taste profile, the trait vocabulary, and the record of every game: played log, fingerprints, ideas log, variation backlog |
| `sessions/` | Games played in chat: the engine and the design notes for each |
| `playtests/` | Five rounds of automated self-play: a report per round, and per game a transcript, a summary and (from round 2) the engine |
| `library/` | Saved games, replayable with a fresh seed |
| `plans/` | Design plans, newest first |

## Development

```
python -m unittest discover -s tests -v     about two minutes
python -m ruff check
python tools/check_all.py "library/*/engine.py"
```

The skill runs from `~/.claude/skills/play/SKILL.md`; `skill/play/SKILL.md` is the versioned copy, and a unit test fails when the two differ. `CLAUDE.md` holds the house rules and where each one came from.
