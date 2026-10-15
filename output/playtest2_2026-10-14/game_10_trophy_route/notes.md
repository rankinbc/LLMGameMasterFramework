# Trophy Route - session notes

Title: Trophy Route

Rolls: FORM=19 dungeon keeper, SET=55 city bus network, ROLE=26 mayor with a hostile council,
LOOP=32 open/hold/close one position as news lands, CLOCK=14 crew morale (strike at zero),
TWIST=38 you only ever see averages, WIN=7 deliver a cargo intact, MAP=9 line of 6 nodes that
shifts each turn, TONE=9 workplace comedy.

How the rolls became the game:
- Dungeon keeper: the bus line is the dungeon, the crowds at each stop are the incoming parties,
  posted buses and inspectors are the traps and creatures. The trophy is the dungeon heart that moves.
- Open/hold/close a position: post guards (open), hold (run normal service), pull guards (close).
- Line of 6 nodes that shifts: Depot plus 5 stops; roadworks swap two stops ahead about every other turn.
- Only averages: dispatch reports crush/rowdy averaged over stops ahead and over the next two.
- Cargo intact: the Centennial Trophy, a two-ton glass bus, must arrive at City Hall at 70+ of 100.
- Crew morale: drivers strike at 0. Hatch heckles, austerity bites, express and pulls cost morale.

Rulesheet:
1. The Centennial Trophy (a two-ton glass bus) rides the No. 6 from the Depot through 5 stops to City Hall. Roadworks swap two stops ahead about every other turn; the order is always shown.
2. Each turn do one thing: advance one stop, post a bus (10 cash) or inspectors (8 cash) at any stop ahead, pull guards off a passed stop (+6 cash, morale -1), or hold (+8 cash, morale +2).
3. Every stop has a hidden crush crowd (up to 7) and a hidden rowdy crowd (up to 8). A bus absorbs 4 crush, inspectors absorb 4 rowdy. Two postings per stop at most.
4. On arrival the drivers roll d6 + 2 against the uncovered crowd. Short by N: trophy -5 x N, morale -1. Held: cash +8, morale +1.
5. Dispatch only ever reports averages: crush and rowdy averaged over all stops ahead, and over the next two. Some days the school run pays a 5 cash windfall.
6. Councillor Hatch rallies every turn at the stop ahead with the fewest guards (nearest on ties): rowdy +1 there. From turn 8 her rallies add 2, she heckles the drivers when she is at the next stop (morale -1), and austerity docks 3 cash a turn (morale -1 instead when the kitty is under 3).
7. Morale 0 is a strike and trophy 0 is shards: both lose. Each overload unlocks one Ride Along (morale +2, next roll +3).
8. From turn 8 you may run Express: two stops in one turn, morale -2. City Hall takes delivery from turn 12. Win: trophy 70+ delivered by turn 16.

Signature detail: Councillor Prudence Hatch and her megaphone. Her readable habit: she always rallies
at the stop ahead with the fewest guards, nearest first on ties, so posting guards steers her.

Midpoint plan (turn 8): escalation = austerity (cash -3 a turn, morale instead when broke) and
Hatch's rallies double to +2 rowdy; unlock = Express (two stops in one turn, morale -2).

Rival policy, one line: each turn Hatch adds rowdy to the least-guarded stop ahead (nearest on ties),
+1 before turn 8 and +2 after, and heckles the drivers (morale -1) from turn 8 when that stop is next.

Mechanics fingerprint: actions = advance, post_bus, post_insp, pull, hold, express, ride;
tracked numbers = cash, morale, trophy (plus the line with its postings, shown in the status line).

Selftest history: see summary.md tuning table.
