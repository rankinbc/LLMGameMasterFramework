# Cold-read prompt for a generated game

Used by Step 7 (4a) of the `/play` skill, before the independent QA review. Replace `<OPENING_SCREEN>` with the exact text the player will see before turn 1 (title, premise, how to play, rules, goal, turn 1 with its options). Pass the whole text below to a general-purpose subagent. Give it nothing else: no folder path, no notes, no engine. The reviewer must not read files or run commands, because a player has only the screen.

The QA review finds bugs for a reader who knows the engine. This one finds games that do not make sense for a reader who does not. Run it with a fresh agent each round.

---

You are a player who has never seen this game. Below is exactly what it shows before turn 1. Do not read any files and do not run any commands; use only this text. Be blunt. If the game is confusing, that is the finding.

<OPENING_SCREEN>

Answer in under 350 words, with exactly these headings:

1. What I think this is. In three sentences: what am I, what do I do on a turn, what am I trying to achieve.
2. What each option physically is. One line per option: what would a person in this setting actually be doing? Write NONSENSE after any action or number where a real person there could not do that, or where the thing described does not exist (for example buying a feeling for a price, paying with something nobody would accept, a code word with no meaning).
3. My first move. One line: which option I would pick and why. Then one line: what I am afraid of.
4. Lines I had to read twice, or could not understand. Quote them.
5. Would I keep playing. A score from 1 to 10 and one sentence on why.

---

## How the GM reads the answer

The game passes only if all of these hold:

- Heading 1 matches what the engine really does (the GM checks it against `rules` and `notes.md`).
- Heading 2 has no NONSENSE.
- Heading 3 names a move that is reasonable under the sheet, for a reason the sheet supports.
- Heading 4 quotes at most two lines.
- Heading 5 is 7 or higher.

Calibration: on the first game this reader ever saw (Dim Ledger, a market that sold crew morale for Light) it scored 6, marked the market NONSENSE and quoted nine lines. A score of 6 alone is therefore not a pass.

On a fail, change the game, not just the words: the action, the number or the premise that did not make sense. Then run a fresh reader. Three rounds at most. The reader's report is data, not an order: a complaint that the game is hard or short is not a fail.
