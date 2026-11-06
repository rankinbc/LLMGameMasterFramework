# GM - Generated Games

Home for the `/play` skill (`~/.claude/skills/play/SKILL.md`). Each `/play` invents a new lightweight text game from random rolls, writes a Python engine for it, selftests it, and runs it in chat. The engine owns numbers, dice, clock and rival. The LLM owns words.

## Layout

| Path | Purpose |
|------|---------|
| `taste_profile.md` | What the player enjoys, distilled from `../GameAnalysis2`. Generator reads it first. |
| `engine/gm_base.py` | Engine contract and CLI runtime. Every game engine subclasses `Game` and calls `run`. |
| `engine/gm_checks.py` | Universal bug checks (JSON round trip, text and plural lint, gates, reach, check_end at the budget, fuzz, determinism) and the rule-test harness `T`. |
| `engine/gm_cast.py` | A named cast the engine owns (`roster`, `fall`, `fallen_text`) for games whose STORY roll is 3 or 4, so "who died" has one true answer. |
| `engine/gm_analysis.py`, `engine/gm_mutate.py` | `profile`, `autopsy`, `ablate`, `replay`; and the mutation pass that measures how strong a game's rule tests are. |
| `engine/example_lantern_chain/` | Reference engine. Copy its shape for new games, never its content. |
| `library/<name>/` | Saved games: `rules.md` plus `engine.py`. `/play <name>` reruns one with a fresh seed. |
| `sessions/<date>_<slug>/` | A live game: `engine.py`, `state.json`, `rolls.log`, `notes.md`. `/play resume` picks up the newest. |
| `played_log.md` | One line per finished game with rolls and action ids. Used for the novelty check. |
| `ideas_log.md` | One line per off-menu idea a player tried in play, and whether a gambit caught it. Step 4 reads it when writing gambits. |
| `traits.json`, `fingerprints.jsonl`, `variation_backlog.md` | Trait vocabulary, one fingerprint per finished game, and the traits that stayed the same too long (candidates for new roll axes). |
| `tools/sameness.py` | `brief`, `novelty`, `verbs`, `add`, `report`, `backlog`, `phrases`. Finds repetition across games and runs the novelty check. |
| `tools/check_all.py` | Runs `check --quick` over many engines (the library, old games). |
| `tools/qa_prompt.md` | The independent-review prompt: a fresh agent plays a new game three times, sends bad input and compares the sheet with the code. Step 7 of the skill uses it. |
| `tools/coldread_prompt.md` | The cold-read prompt: a fresh agent sees only the opening screen and says what it thinks the game is, what each action physically is (NONSENSE if it cannot be), its first move and whether it would keep playing. Step 7 (4a) uses it, before the QA review. |
| `tests/` | Regression suite for the harness: unit tests plus one mutant engine per bug class, each of which must be caught. |
| `output/playtest_<date>/` | Playtest transcripts, summaries and the analysis report. |

## Engine CLI

Run from a session folder.

```
python engine.py new [seed]              start; prints turn 1 JSON
python engine.py step <id> [json]        apply, advance, save, print turn JSON (same id, different args: pass the args)
python engine.py step "#3"               pick the 3rd entry of the options list
python engine.py status                  current state, no advance
python engine.py rules                   the rulesheet, built from CONSTANTS
python engine.py check                   random, heuristic and look-ahead play, sheet audit, coverage; counts tuning rounds (cap 4)
python engine.py check --free            same, without counting a round
python engine.py sweep K=a,b [K2=c,d]    try constants at several values
python engine.py check --quick           serial and without the mutation pass, for the regression suite (not for tuning)
python engine.py texts [games]           every distinct event, option, status and end wording the game can produce; read it once
python engine.py trace [seed] [random] [--do haul,light:lantern=3]   one full game as text; script the first moves to test a trick
python engine.py profile [n] [k]         tension per turn: flat opening, middle, finish (warnings)
python engine.py ablate [n]              ban each action in turn; which ones nobody misses (warnings)
python engine.py autopsy [k]             after a finished game: swing turn and its cause, regrets, dilemma turns
python engine.py replay [--apply]        re-run history.jsonl on the saved seed after an engine fix
python engine.py fingerprint             mechanical traits (actions, tracked count, turn band) for the sameness detector
python engine.py selftest 300 <policy>   one policy: random | heuristic | lookahead
python engine.py log                     every die rolled, in order
```

Bands: random wins under 35 percent, heuristic 25 to 45 percent, look-ahead 60 to 90 percent (a warning). An engine declares CONSTANTS, RULES, ACTIONS and TAGS so `check` can catch sheet drift, hidden actions and unreachable twists, and GAMBITS plus RIVAL_KEYS so `check` can prove the player has risky moves off the loop and that one of them really touches the rival.

## Tests

```
python -m unittest discover -s tests -v     from the GM folder; about two minutes
python -m ruff check                        lint, configured in ruff.toml (sessions, library and output are excluded)
python tools/check_all.py "library/*/engine.py"
```

Change `gm_base.py` or `gm_checks.py` only with the suite green and ruff clean. The skill runs from `~/.claude/skills/play/SKILL.md`; `skill/play/SKILL.md` is the versioned copy, and a unit test fails when the two differ (copy the live file over). To add a bug class, add a mutant to `tests/test_mutants.py` first and watch it fail.

## Rules of the house

- Rulesheets stay at 8 lines or fewer, 3 tracked numbers max, one decision per turn. Caps live in the skill; edit them there.
- An engine with flags from `check` is not presented. Tune first, at most 4 rounds. Warnings are read, not obeyed blindly.
- A turn is the player's action (`apply`), then dusk (`advance`), then the counter goes up. `_turn` is the turn being played in `apply`, `advance` and `check_end`; the budget is scored in `final_check`. A fatal event calls `self.finish(...)`.
- A new game gets an independent review (Step 7) before it is presented, repeated with a fresh reviewer until a round finds no S1 or S2 and at most two S3. Measured on 8 attacked games: no wrong arithmetic; about four wording or sheet slips a game after two reviews. Every bug it finds in the harness becomes a mutant or a unit test first.
- A turn whose JSON carries a non-empty `integrity` list is an engine bug. Stop, fix, recheck; never narrate over it.
- A game must make sense to a stranger (skill limits 9 and 10). Feelings and standings (morale, trust, nerve, suspicion) are never bought, sold or priced; a rolled number is not a currency just because it was rolled; action labels are plain verbs, not code words. `check` flags the worst case as SENSE, warns on MOVE (a menu number needing two answers) and STATUS (more than 5 numbers), and the cold read (Step 7, 4a) catches the rest. Origin: Dim Ledger (2026-10-16) sold crew morale for Light at four "consoles" and passed `check` and two QA rounds, because both test the engine, not whether the game makes sense.
- The player can push back (skill limit 11). Every new game has two or three gambits, risky moves off the loop that the setting invites, one of them against the rival. `check` flags a rival gambit that never changes a RIVAL_KEYS value and warns on no gambits, a rarely offered gambit, or one no policy plays; a GAMBIT warning is never accepted for a new game. Origin: Low Wells (2026-11-06), four player ideas in a row met "the game cannot".
- The finish is rolled (FINISH d4: final-roll, photo-finish, collapse, cliff), never flat.
- Story is rolled (STORY d4: 1 to 2 lean, 3 cast, 4 saga). With a cast, names live in `s["cast"]` and losses go through `gm_cast.fall`; the GM never invents a name. Origin: Low Wells, "what were the names of those who died".
- A game whose rolls a sensible player never meets gets a DICE warning from `check`; like GAMBIT, it is never accepted for a new game.
- Sessions are disposable. Library is the keeper. Only save after finishing a game.
