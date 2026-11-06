# Closure Order

Rolls: FORM=6 (pursuit) SET=2 (frontier star cluster) ROLE=15 (squadron commander) LOOP=29 (write three instructions, run them) CLOCK=1 (fuel runs out) TWIST=1 (prices invert every 5 turns) WIN=10 (escape with a crew) MAP=1 (linear track of 10 stops) TONE=12 (deadpan bureaucratic) CURRENCY=5 (stock: goods on hand) TRACKED=1

Bends: the rival is a schedule, not a hunter (the sameness brief asked for it): the Bureau closes the lanes behind the squadron on a hidden repeating timetable. LOOP (write a program, watch it run) is bent to "set the autopilot's order for the turn": one plain order a turn, so one answer per move. WIN (escape with a crew of N) is bent to "get through the last gate"; there is no crew number (TRACKED=1). TWIST (prices invert) is the lane tide: short hops are cheap on a low tide, long skips are cheap on a high tide.

## Sense card

1. Job: Each turn I, the squadron commander, choose how to move down a chain of jump gates so that I reach the last gate before the Bureau's Closure Order shuts the lane around me.
2. Tracked number: Fuel. It is the squadron's fuel, held in the ships' tanks. Siphoning from a gate depot raises it; jumping and life support lower it. Not tracked but shown: my gate, the gate the Closure Order has reached, and the tide.
3. Actions:
   - Hop: I jump one gate. Burns fuel by the tide. A jump drive burns fuel.
   - Skip: I jump two gates in one go. Burns fuel by the tide.
   - Hold: I stay and siphon fuel from the depot at this gate. Gates have depots.
   - Seal: I shut the gate behind me, once, for fuel. The Bureau needs a night to unlock a sealed gate.
4. Trades: none. Nobody buys or sells anything. Fuel is burned by moving and gained by siphoning.
5. Out loud: "You are fleeing down a chain of gates. A bureaucratic closure order is shutting the lane behind you, some nights faster than others. You spend fuel to jump. Cheap jumps change every five turns with the tide. Get to the last gate." Reads fine.

Signature detail: the Closure Order's pace is a hidden repeating pattern (it shuts 1 gate on two nights and stalls for paperwork on the third); the player learns which night is the stall by watching the lines.

Midpoint plan: the tide flips on turn 6 and again on turn 11; the seal opens on turn 7 (late lever: pauses the Closure Order for two dusks).

Rival policy (one line): every dusk the Closure Order advances by the next step of a hidden 3-step pattern (advance, advance, stall, in a hidden rotation), shown after it lands; a seal skips a night and the pattern waits.

Ending shape: photo-finish (your gate and the Closure Order converge). Opening shape: free-choice. Rival type: schedule. Rival tell: after. Turn band: short (12).

## Opening screen (as presented; cold-read input)

Closure Order
You lead a small squadron of ships out of a remote star cluster. The only way out is a line of 12 jump gates, which work like doors between star systems, and a government office called the Bureau is closing them behind you one by one. Each turn you decide how far to jump and how much fuel to spend, and you win by getting through the last gate before the closed stretch catches you.

Your numbers
- Fuel: what the squadron has left in its tanks. Jumping and life support use it; siphoning from a gate's depot refills it.
- Gate: where you are on the line of 12. Gate 12 is the way out.
- Closure: the last gate the Bureau has closed. If it reaches your gate, you are trapped.
- Tide: the current in the jump lanes. It decides which jumps are cheap.

Rules: the output of `python engine.py rules`. Goal: get through Gate 12. Lose if: fuel runs out, the Closure Order reaches your gate, or the 12 turns end first. Turns: 12.

Known deviations: GATES is 12, not the 10 the MAP roll gave, to keep games near full length. The depot yield varies (2 to 4) so outcomes are not a pure puzzle. The FORCED warning (about a third of turns offer only a hold) is accepted: those are the turns the squadron is too low on fuel to move, a consequence of earlier spending. The seal is a late lever that look-ahead rarely picks.

## Cold-read log

Round 1 (Dim Ledger-era prompt, first draft of the screen): score 6, no NONSENSE in the actions, eight unclear lines (pattern wording, "under 0", nights versus dusks, hold vs the Closure Order, dusk burn not in the move cost). Round 2: score 6, the seal flagged as nonsense (fuel paying to pause an office), "skip" read as landing a gate further, "with an order" garbled, tide timing unclear. Round 3: score 7, nothing flagged as nonsense, six clarifications asked (afford vs the dusk burn, tide on turns 11 and 12, what the lock covers, equals vs passes, depots running dry, the hidden rhythm). All six were fixed in the sheet afterwards without a fourth round (round cap). The seal became "lock the gate" (the Bureau's crews take 2 dusks to cut through), skip became "leap".
Skipped as asked by the player for this test build: profile, ablate and the three-game independent QA review.
