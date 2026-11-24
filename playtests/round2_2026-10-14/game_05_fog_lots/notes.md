# Fog Lots - session notes

Title: Fog Lots
Date: 2026-10-14 (playtest2, game 05)
Seed: 34962

## Rolls
FORM=4 blind auction | SET=38 airport control tower | ROLE=26 mayor with a hostile council | LOOP=36 plant or tend one plot, the rest grows on its own | CLOCK=1 fuel runs out | TWIST=27 one resource is sentient and resists being used | WIN=17 balance the budget with the reviewer satisfied | MAP=8 single location with 6 districts | TONE=8 cozy with teeth

## Rulesheet
1. Each week one lot goes to sealed bid against Councillor Vane: bid 8, 14 or 22 cash, or pass and tend instead. Higher bid wins and pays; ties go to Vane. A losing bid costs nothing.
2. Lots are tankers (+8 fuel) or leases on one of the airport's 6 districts. A leased district flies 1 flight a week, 2 once it matures after 3 weeks (or tend it to mature now).
3. Each flight burns 1 fuel and pays 8 cash; the runway lights burn 1 fuel a week regardless and the tower keeps 5 fuel back for them; fog weeks (rolled, shown) ground all flights. Fuel 0: the airport goes dark, you lose.
4. Bess the runway is alive and resents work: she takes at most 5 flights a week, and on 4 or more she heaves on a roll of 1-2 (closed next week, -10 cash). Tend her (10 cash) and she tolerates anything for 3 weeks.
5. Council levy 4 cash a week. Cash below 0 is impeachment: you lose.
6. Vane's clerk talks: each week you hear whether her next bid will be HIGH (11-21) or LOW (6-11). The clerk is right 5 weeks in 6.
7. Lose two auctions in a row and the fishing co-op sells you an emergency drum: 3 fuel for 12 cash.
8. Week 8: tankers shrink to 5 fuel, Vane's high bids reach 24, and the Mail Contract lot appears once (+1 flight a week paying 12). Week 16 the auditor comes: win with cash 90+ and 4+ districts leased.

## Signature detail
Bess, the runway, is alive (the sentient resource): she tolerates 3 flights a week, grumbles at 4 or 5, and heaves on a 1-2 unless walked at dusk with a thermos and a wire brush. Councillor Vane's clerk leaks her bid mode each week, wrong one week in six.

## Midpoint plan (week 8)
Escalation: tankers shrink from 8 to 5 fuel; Vane's high band moves from 2d6+9 to 2d6+12 (so a 22 bid is no longer a lock); her high-bid chance rises 15 points.
Unlock: the Mail Contract lot appears once at week 8 (+1 flight a week that pays 12).

## Rival policy (one line)
Vane bids HIGH (2d6+9, 2d6+12 after week 8) with probability 0.35, 0.75 on a tanker when your fuel is 4 or under, 0.6 on the mail, +0.15 after week 8; otherwise LOW (d6+5); ties go to her; her clerk reports the mode truthfully 5 times in 6.

## Fingerprint
actions = bid_low, bid_mid, bid_high, tend_bess, tend_plot, drum (wait as an emergency fallback only)
tracked = cash, fuel, districts (list with level/age rules)

## Tuning log
See summary.md for the round table.
