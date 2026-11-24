# Dust Licence: generator report (round 3b, game 4)

Saved by the lead from the generating agent's final reply.

## Title and premise

Dust Licence. The player is the pit boss of a casino ring under a Mars dome. Each turn one table licence is auctioned in sealed bids against Madame Vey, and the winner's convoy must cross the dust to reach it.

## Rolls

FORM 4, SET 21, ROLE 31, LOOP 16, CLOCK 18, TWIST 45, WIN 6, MAP 2, TONE 8, CURRENCY 12 (Standing). No reroll. The brief was met on purpose: 2 tracked numbers (Standing, the ring), bidder rival, upkeep clock, bid decision, hidden habit, final-roll ending.

## Check log

- R1: heuristic too easy (0.49); tests for rules 5 and 8 crashed (the agent's own bug: int keys in `dict(**)`). Mutation 0.84.
- R2: clean. Random 0.06, heuristic 0.45, look-ahead 0.70, mutation 0.90. Trace and profile showed a snowball and a sit-out stalemate (88 percent of games decided early).
- R3: clean (random 0.02, heuristic 0.44, look-ahead 0.72, mutation 0.90) after rival and economy fixes. Profile still warned of a flat finish (83 percent decided early).
- R4 (cap): added a closing Cage lot and a STAFF income cap. Random 0.04, heuristic 0.47, look-ahead 0.80, mutation 0.90.
- Three free reruns after adding tests: mutation 0.98 (64 of 65).
- Final profile: no warnings, 21 percent decided early. Final verdict FLAGS: one flag, heuristic over 0.45 by 0.02.

## Declarations

params: bid amount (min 1, max Standing, step 1) and audit table (choices). resample_hidden: Vey's habit is one of three styles, redrawn from the styles that explain every bid revealed so far; the heuristic does the same inference from visible history. DERIVED: mine and hers. 12 tags, all fire.

## Warnings accepted

The heuristic band miss (0.47 against 0.45) is within noise (reruns gave 0.44 to 0.49). Six sheet lines of 37 to 45 words. Ablate calls `sit` and `audit` unproven: `sit` is the deliberate decoy and eco-save; `audit` is the late lever and look-ahead does pick it.

## Harness feedback

1. Mutation only covers init_state, options, apply, advance and check_end. Logic in helpers (auction, habit, safe) is not mutated; extending the scope exposed about 20 survivors and drove 14 new tests.
2. The cap note says accept band misses within 0.1 but the verdict stays FLAGS and the skill says flagged games are never presented. These conflict.
3. The engine hash covers rule_tests, so adding tests counts as a tuning round.
4. The contract says the rival acts in advance, but simultaneous bids force a pending-then-resolve pattern, and advance sees the next turn number.
5. A param without `step` accepts 3.5 or 3.0, which made Standing a float. A default step of 1 for int ranges would be safer.
6. status_labels reads the letters before the first digit as the label, so "Ring Y.V" looks like a changing label; "Ring:" with a colon fixed it.
7. The skill asks for 3 to 5 choices but a parametric bid game offers 2 or 3.
8. profile was the most useful tool (it caught the snowball). A long Bash command containing a path was blocked once as secret-shaped.

## Time and effort

About 70 to 80 minutes and 55 tool calls, mostly economy redesign after profile and traces exposed a snowball.
