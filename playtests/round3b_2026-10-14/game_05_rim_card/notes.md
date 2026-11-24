# Rim Card

Premise: A washed-up wrestling booker runs a touring card through eight asteroid-belt outposts, twenty nights, while Vesper Broadcasting's number climbs away and its crews raid the longest-running shows. Noir.

## Rolls

FORM=12 (Logistics) SET=1 (Asteroid belt mining outposts) ROLE=51 (Wrestling booker) LOOP=31 (Place one tile; adjacency and chains score) CLOCK=16 (The target is getting away) TWIST=35 (Hidden objective revealed at the halfway mark) WIN=18 (Reach a rating) MAP=2 (Hex ring of 8 around a center) TONE=11 (Noir) CURRENCY=9 (Cash)

Bends: logistics is the delay (Scrap, Tag and Belt acts fly in after 1, 2 or 3 dusks); the tile is a bout booked onto one of eight outposts; the "target" is Vesper's bar; the hidden objective is the sponsor's secret favourite kind.

## Rulesheet (from `python engine.py rules`)

1. 8 outposts ring the Hub. Each night book one bout at an outpost, replacing any bout there: Scrap costs 2 cash, Tag 4, Belt 8. They go live after 1, 2 and 3 dusks.
2. Rating counts live bouts only: Scrap 1, Tag 2, Belt 3, plus 2 for each pair of neighbours of different kinds and 3 for each three neighbours in a row of three different kinds.
3. You start with 10 cash and 2 live bouts at random. Each dusk you earn 1 cash per 6 Rating. Or skip booking and work the crowd for 3 cash.
4. Vesper's bar starts at 26 and climbs 1 each dusk, 2 more on a die roll of 5+. Goal: when night 20 ends, Rating at least equals the bar. Lose if short. Nights: 20.
5. On a hidden fixed beat, every few nights, Vesper raids at dusk and poaches the outpost bout live longest (lowest outpost on a tie), leaving it dark. You see a raid only as it lands.
6. From night 13 you may counter-program instead of booking, for 3 cash: a raid due tonight is cancelled, otherwise the bar drops 2. Vesper's surge then needs a 6.
7. At night 11 the sponsor's secret favourite kind is revealed: each live bout of it adds 2 Rating. From night 11 the bar climbs 2 each dusk.
8. From night 11 book one main event at the Hub for 8 cash, replacing the last. It goes live like its kind and scores 2 per live outpost bout of that kind (+2 if favourite).

Goal: Rating at least equal to Vesper's bar when night 20 ends.   Lose if: it falls short.   Turns: 20

## Tracked

Two things: cash, and the ring of outposts (Rating is the ring's score, shown on the status line with the bar).

## Signature detail

Vesper raids the outpost bout that has been live longest, on a hidden fixed beat (every 3, 4 or 5 nights, unknown phase). The player infers the beat from two raids seen (the gap is the period), so a counter-program can be spent on the right night. Early bouts are the ones that die first, so cheap Scraps go up first and Belts later.

## Midpoint plan

Night 11: the sponsor's secret favourite kind is revealed (+2 Rating per live bout of it), the Hub opens for one main event (never raided), and the bar climbs faster (1 to 2 a dusk). Night 13: counter-programming opens (cancels a due raid, or cuts the bar by 2 if none was due, and pins Vesper's surge roll to 6; the late lever, and a cash sink for dead nights).

## Rival policy (one line)

Vesper's bar climbs 1 a dusk (2 from night 11) plus 2 more on a roll of 5+, and on a hidden fixed beat its crews raid and strip the longest-live outpost bout; the raid is shown only after it lands.

## What the seed changes

Starting layout (which 2 outposts hold which kinds), the sponsor's favourite, the raid beat (period 3 to 5 and phase), and the bar's surge dice.

## Engine notes

Options are listed best-first (kinds by best Rating per cash, outposts by Rating gained); `visible` carries `gain_if_booked` per kind per outpost and `next_raid_would_take_outpost`.
