# Driftwood Cats

Rolls: FORM=14 (tile placement) SET=48 (cat cafe) ROLE=2 (salvage captain) LOOP=30 (breed two, inspect, keep one) CLOCK=19 (reviewer visits) TWIST=7 (night doubles risk and reward) WIN=5 (build a final structure) MAP=1 (linear track of 10) TONE=2 (dry humor) CURRENCY=11 (evidence) TRACKED=1.

How the rolls became the game:
- FORM and MAP: a wall of 10 spots; pieces are bolted in place and never move, so where each goes is the decision.
- LOOP: two pieces of one size join into one bigger piece (two parents, one offspring); big joins roll to see if the result is sturdy or wobbly (inspect the offspring).
- TWIST: the night dive. It costs today's piece and risks nothing more, but a success doubles tomorrow's piece.
- WIN: the Grand Tree, a cat tree built from two Towers. CLOCK: the reviewer comes by the last dusk.
- ROLE and SET: a retired salvage captain who runs a harbor cat cafe and furnishes it from salvage. The wreck and the old crew come from the role.
- TRACKED=1: the wall is the one board the player manages.
- CURRENCY 11 (evidence) was bent and does not appear. With one tracked board and a placement form, there was no sensible place for proof or leads in a cat cafe; forcing it would have produced the Dim Ledger kind of nonsense. Recorded as primary_bucket "other".

Signature detail: Admiral, the cafe's old ship's cat, picks the tallest piece every morning and climbs it at night; a wobbly piece under him loses its top.

Midpoint plan: none (cut after cold read round 2; the kitten Bilge, a day-7 new threat, made the sheet too dense). Late lever: the old crew raise the wreck's mast once, from day 11: tomorrow's piece is a Tower.

Rival policy (one line): Admiral climbs the spot that held the tallest piece at dawn (nearest the door if tied), shown each morning; a wobbly piece there loses its top.

Ending shape: final-roll (the Tower-on-Tower join; the player buys its odds by bracing the parts first, and buys a day of safety by joining onto the door side of Admiral's spot). Opening shape: grind (small pieces, nothing big yet). Rival tell: before (Admiral's spot shows each morning). Turn band: short.

## Sense card

1. Job: Each day I, a retired salvage captain who runs a harbor cat cafe, bolt the salvage the tide brings onto the cats' climbing wall and join matching pieces into bigger ones, so that a Grand Tree stands when the cafe's reviewer comes.
2. The one tracked thing, the Wall: 10 spots along the cafe wall, what is bolted to each, and whether it is wobbly. Bolting and joining build it up; Admiral breaking wobbly pieces and bolting over a piece wear it down.
3. Actions:
   - Bolt today's piece to a spot: I screw it to the wall. If the piece next to it is the same size, I join the two into one bigger piece. Costs: the day. Fact: cat furniture is built up from smaller parts, and a piece screwed to the wall stays where it is.
   - Brace a wobbly piece: I screw today's plank or shelf across a shaky frame. Costs: today's piece.
   - Dive the wreck tonight: I take the boat out to the old wreck in the harbor and bring up the other half of what is drifting in. Costs: today's piece, which washes away while I am out. Fact: I am a salvage captain and the wreck is in the harbor.
   - Call the old crew (once, late): my old salvage crew raise the wreck's mast for me. Costs: today's piece.
4. Trades: none. Nothing is bought or sold.
5. Out loud: "You run a cat cafe and build the cats a climbing wall from driftwood. Two pieces of the same size side by side make a bigger piece. Big joins can come out wobbly, and the old cat breaks wobbly pieces unless you brace them. Build the Grand Tree before the reviewer comes." Reads fine.

Tuning (final): DAYS 14, CREW_DAY 11; joins that make a Ladder or bigger need 4+ (5+ with a wobbly part); dive 3+ calm, 5+ rough; the tide brings Planks (10 in 12) and Shelves (2 in 12); 3 old pieces to start. Check rounds: 4 (cap); everything after the cap ran as check --free. Final check: heuristic 31 percent, look-ahead 66, random 0, mutation 87 percent.

Known rough edges: a player with a sturdy Tower early (and the crew unused) has a locked win once the crew's Tower arrives (QA round 1, S4): join it on the door side of Admiral's spot and brace the Grand Tree if it comes out wobbly. Making the Grand Tree unbraceable, or braceable only with a Shelf, was tried and dropped: look-ahead fell to about 25 percent, level with the heuristic, so the ending became luck. Kept the version where skill shows (look-ahead 66 against heuristic 31).

## Cold-read log

Round 1: score 6, no NONSENSE, six lines quoted: where a joined piece lands and whether the neighbor's spot empties, what "leans on a piece or wall end beyond it" means, what bracing does, "the other half of tomorrow's piece", the input format, and a misreading that Admiral breaks a new piece the same night. Game change: a joined pair now always lands on its door-side spot and the other spot empties, and the lean bonus comes only from the spot on the door side or from standing at spot 1 (it used to be "beyond the piece, away from its partner", either side). That made the game harder (heuristic 19 percent), so after the cap one number moved, LEAN 1 to 2: a leaning join is now 3+ instead of 5+, which makes where you build matter more. check --free: clean, heuristic 33, look-ahead 66, random 0. The sheet also says plainly that a brace makes the piece sturdy, that a dive brings up a match for tomorrow's piece, and that Admiral climbs his morning spot whatever is there.

Round 2: score 6, no NONSENSE, seven lines quoted; the reader understood the game and picked a sensible first move, but called eight dense rules full of clauses too much. Game change (simplify, round cap in sight): cut the kitten Bilge and the lean bonus; joins became one standing fact, "whenever two pieces of one size sit side by side they join on the spot nearer the door" (so a cat's break can cause a night join); the win line says the check comes after Admiral climbs. Five mechanics now: joining, the join roll and brace, the dive, Admiral, the crew. Engine rewritten; the earlier version is kept as temp_engine_v1_kitten_lean.py. check --free: clean, heuristic 31, look-ahead 66, random 0, mutation 87 percent.

## Opening screen (cold-read input, round 3)

Same layout as round 2, with the round-3 sheet from `python engine.py rules`, the Tonight line naming only Admiral, the Day line as "which of the 14 days it is", and the dive option at need 3+.

Round 3: score 7, no NONSENSE, first move "1 at 1" (joins the Planks at 1 and 2 into a Shelf, away from Admiral), heading 1 correct. Six lines quoted, all wording: whether joins cascade, "Bolted pieces never move" next to joins, an empty Admiral spot, whether the crew call uses today's piece, whether a win can come before day 14, and the standard "or say anything else". Fixed in the sheet without a fourth round (round cap): rule 3 says the joining repeats, pair nearest the door first; rule 2 says pieces never slide; rule 6 says he naps on an empty spot; rule 7 says today's piece washes away; rule 8 says "at dusk on any day". Passed 4 of 5 criteria; the line count is the one miss, all wording.

## QA log

Round 1 (fresh reviewer, 4 games): no S1 or S2. S3: day 1 has no morning event (harness: `new` prints no events; the GM narrates day 1); the sheet did not say the wall starts with old pieces (rule 1 now says 3); the morning said "the tide brings a Tower" after the crew and "a Ladder" after a dive (now "your crew's Tower is on the slipway", "the Ladder you raised from the wreck is on the slipway"); the last day's status showed tomorrow's piece and the sea (now "Today: Plank, last day | Tonight: the reviewer comes"); "You bring up a match" (now "You raise a matching Shelf from the wreck. Tomorrow you get a Ladder instead."); stale notes (fixed). S4: the locked win (see rough edges); "Tower" hard-coded in the crew text (now from the constant); two defensive branches that cannot run in play (the dive gate on a Ladder or Tower tomorrow, an empty wall), kept on purpose. Rule-test gaps closed: a wobbly part on the far side, bolting over a wobbly piece, two Grand Trees never join, the tree named in the win, a night join with a wobbly part, a Grand Tree made by a night join, the last day's status.

Round 2 (fresh reviewer, 4 games, 1500 fuzz games): no S1 or S2. S3 fixed: the morning before the last day still promised a tomorrow and a sea (now "It is the last day: the reviewer comes tonight."); the reviewer was never named on the sheet and the two win texts disagreed (rule 8 now names the reviewer; win reason "you called the reviewer in"; loss reasons "the reviewer came at dusk of day 14 ..."); the crew label did not say today's piece washes away (now it does). S3 harness, not fixed here: the status line after the game ends still shows the last morning's fields. S4 kept: the win locks early for a skilled player (autopsy shows 1.00 from turn 8 on two seeds), and a decoy piece as tall as the work nearer the door keeps Admiral off fresh joins; the harness's autopsy and profile do not see a locked win while a blunder stays on the menu (harness follow-up). Test gaps closed: the last morning's wording, a day-14 win, two wobbly pieces braced one at a time, a wobbly part made earlier in the same chain.
