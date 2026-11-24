# Styx Arcade

Premise: In a 1980s arcade where the cabinets are fed with the coins of the dead, you are a smuggler in the Ferryman's debt, hunting the skimmer who is robbing the Owner before the season's audit.

## Rolls

FORM=5 (Deduction) SET=50 (A 1980s arcade) ROLE=3 (Smuggler with a debt) LOOP=16 (Route convoys through danger)
CLOCK=22 (A season of fixed length; standings decide) TWIST=18 (Two currencies at a shifting rate) WIN=15 (Name the culprit with two pieces of evidence)
MAP=10 (No map; a deck of encounters) TONE=5 (Mythic) CURRENCY=11 (Evidence)

The first CLOCK roll was 5 (hull decays). `sameness.py brief` said clock_shape had to leave "decay", so CLOCK was rerolled once (22).
Novelty check: OK, no reroll needed. Verbs check (run, exchange, accuse, ledger): 0 percent overlap with the nearest earlier game.

## Rulesheet

1. 6 regulars work the floor and one is the Skimmer. Each plays one game, wears one coat and works one shift, all posted on the roster. You start with 2 Hearsay and no Proof.
2. Each night the deck deals 3 aisle cards (hazard up to 4, haul of hazard plus 2 Hearsay). On 50% of nights one card has a witness who knows the Skimmer's game, coat or shift.
3. Run one aisle, bribing up to 3 Hearsay, and roll a d6: caught on a roll up to hazard minus bribes. Safe: take the haul and hear the witness. Caught: no haul, no report, and the Walker confiscates 1 Proof.
4. Instead of running, swap Hearsay for Proof at the Pawnbroker's rate, stamped on one regular in doubt; stamping another voids the old file. The rate drifts a step each dusk, 6 to 9 Hearsay per Proof.
5. Instead of running, accuse the regular on a file holding 3 Proof: right wins, wrong loses. A report clearing the file's regular voids it. No accusation by the end of night 12: the audit calls your debt.
6. Each dusk the Magpie lifts 1 Proof from your file if it holds 3 or more, so buy extra to cover him before the night you accuse.
7. From night 6 the Back Booth opens as a fourth aisle (hazard 4, two topics), and the Magpie lifts from a file of 2 Proof or more.
8. From night 8 you may read the Owner's ledger for 3 Hearsay instead of running: you learn one topic of your choice for sure, no roll.

Goal: accuse the Skimmer with 3 Proof on the file. Lose if: a wrong name, or no accusation by the end of night 12. Turns: 12.

## Design choices made on purpose (from the brief)

- Tracked numbers: 2 (Hearsay, Proof). Rate and Suspects are shown on the status line but are a price and a roster count, not stocks the player manages.
- Rival: the Magpie, a saboteur with a fixed habit, tell shown after it lands. Not a hunter.
- Clock shape: deadline (the audit on a fixed night). Ending shape: cliff (the last night is the last chance to accuse).
- Decision unit: allocate and assign (bribe amounts, Proof swaps stamped on a chosen regular, aisle picks). Not a route.
- Two currencies: Hearsay (cheap, from convoys) and Proof (stamped by the Pawnbroker at a rate that drifts 6 to 9 Hearsay per Proof). Both are Evidence in the fiction.

## Signature detail

The Pawnbroker's file: Proof is stamped on one named regular, never on "the case" in general. Stamp a different regular and the old file is voided; a witness report that clears the file's regular voids it too. So buying Proof is a bet on a suspect, and the Magpie's lift (from a file of 3, or 2 after the middle night) means you must buy one more Proof than you need to accuse.

## Midpoint plan (night 6 of 12)

Escalation: the Magpie lifts from a file of 2 Proof instead of 3. Unlock: the Back Booth opens as a fourth aisle (hazard 4, two witness topics). The booth is announced at dusk of night 5.

## Late lever

From night 8 the Owner's ledger: pay 3 Hearsay (instead of running) to learn one topic of your choice for sure. Worth it when two regulars remain and Hearsay is not short.

## Rival policy (one line)

Every dusk the Magpie lifts 1 Proof from the file if it holds 3 or more (2 or more from night 6), and says so after the fact; no dice, no hidden state.

## Seed changes

The roster (names, who has which game, coat and shift), which regular is the Skimmer, the deck (hazards, which night has a witness and on which card and topic), the Pawnbroker's rate drift and every convoy roll.

## Engine notes

Hidden: only the Skimmer (`hidden.culprit`, a roster index). `resample_hidden` redraws it among the regulars consistent with the reports learned so far. The heuristic never reads it.
Known rough edges (from check): look-ahead wins about 32 percent against the heuristic's 39 (the harness look-ahead is noisy on small repeated income choices); `seized` and `voided` fire in few heuristic games (rare events by design).
