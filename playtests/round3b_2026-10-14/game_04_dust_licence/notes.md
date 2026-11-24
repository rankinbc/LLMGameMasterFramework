# Dust Licence

Premise: You are the pit boss of a casino ring under a Mars terraforming dome. Eight table licences circle the Cage; each turn one is auctioned in sealed bids against Madame Vey, the incumbent rival, and the winner's convoy must cross the dust to reach it.

## Rolls

FORM=4 (blind auction) SET=21 (terraforming dome on Mars) ROLE=31 (casino pit boss) LOOP=16 (route convoys through danger) CLOCK=18 (fixed upkeep each turn) TWIST=45 (double-blind: rival bids at the same time, revealed together) WIN=6 (hold the most nodes when the clock ends) MAP=2 (hex ring of 8 around a center) TONE=8 (cozy with teeth) CURRENCY=12 (Standing)

Brief constraints met on purpose: tracked_count 2 (Standing, the ring), rival_type bidder, clock_shape upkeep, decision_unit bid (amount param), rival tell hidden and inferable from history, ending shape final-roll (the Cage is auctioned again on the last turn).

## Rulesheet

1. 8 tables ring the Cage at the centre, each with a take of 1 to 2 Standing. You and Vey, the rival pit boss, start with 14 Standing. You hold one table; Vey, the incumbent, holds 2, opposite you.
2. Each turn one lot comes up from the posted docket. You seal a bid of 1 or more Standing, never more than you hold; Vey seals hers, within her means. Revealed together: the higher bid wins and pays it. A tie goes to Vey.
3. Or sit out: bid nothing and gain 2 Standing. Vey then wins the lot, paying 1 or all she has, and you learn nothing of her habit.
4. The winner's convoy must reach the lot. Safe if the lot touches a table the winner holds (ring neighbours; the Cage touches all). Otherwise roll 3+ or the convoy is lost: the bid is still paid and the lot stays as it was.
5. At dusk each side earns the takes of its 3 best tables, the side with fewer tables gains 1, then each pays 3 upkeep. Your Standing below 0 after dusk ends your licence and you lose; Vey cannot fall below 0.
6. Vey has one fixed secret habit: she bids the lot's take plus 2, or her Standing divided by 2 (rounded down, at least 1), or your last bid plus 1 (3 if none). On 25% of turns she bids 1 more.
7. From turn 9 the dust season starts: convoys need 4+. On turns 9 and 16 the lot is the Cage itself: take 2, and it counts as 3 tables.
8. Once, from turn 12: instead of bidding, pay 4 Standing to audit Vey, strip one of her tables and withdraw the lot. After turn 16 the side with more tables wins; a tie goes to Vey.

Goal: hold more tables than Vey after turn 16 (the Cage counts as 3).   Lose if: Standing is below 0 after dusk, or you do not finish ahead (ties go to Vey).   Turns: 16

## Signature detail

Madame Vey bids by one fixed secret habit, drawn per seed: the lot's take plus 2 (miser), half her Standing (gambler), or your last bid plus 1 (shadow, which punishes big bids by answering them). Her bids are revealed with yours every turn, so the habit can be read from history. The Cage, centre of the ring, touches every table and is the lot twice: turn 9 and turn 16.

## Midpoint plan

Turn 9: the dust season starts (convoys need 4+ instead of 3+) and the Cage is the lot (take 2, counts as 3 tables). Late lever: from turn 12, once, audit Vey (4 Standing) to strip one of her tables and withdraw the lot. Turn 16: the Cage is the lot again, the closing showdown. The decoy is sitting out: +2 Standing, but Vey takes the lot for 1.

## Rival policy (one line)

Vey bids her seed's habit (lot take + 2, or half her Standing, or your last bid + 1) every turn, adds 1 on 25 percent of turns, never bids more than she holds, wins ties, and wins any lot you sit out for 1.
