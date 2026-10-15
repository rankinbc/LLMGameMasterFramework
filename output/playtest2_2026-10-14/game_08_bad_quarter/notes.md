# Bad Quarter - session notes

Title: Bad Quarter
Rolls: FORM=12 SET=25 ROLE=10 LOOP=26 CLOCK=14 TWIST=23 WIN=16 MAP=2 TONE=11

Rulesheet
1. You govern Harrow Ring for Lissom & Vane Capital: the Spindle hub and 8 docks in a circle. Each week give one order: send an idle hauler on a contract, push a hauler, rest the crews, or a special job when it appears.
2. A contract is pickup, drop, tons. The trip takes 1 week per hop from where the hauler sits (hub to any dock is 1 hop). Each week in transit a hauler rolls d6: on a 1 it slips a week.
3. Each week your landed tons face Carver Freight's. More wins the week; ties go to Carver. Every even week Carver signs the biggest unsigned contract on the board and lands it 1 week per hop; his due tons are shown ahead.
4. Push: your soonest hauler arrives one week sooner, morale -1. Rest: morale +2. A won week is morale +1, a lost week morale -1. Morale 0 is mutiny: game over.
5. Two lost weeks in a row open Night Run: your heaviest hauler in transit lands now, morale -1.
6. Week 8: Carver adds a tug (base tons 0 to 3 every week) and the Spindle yard opens: Overhaul an idle hauler at the hub (1 week, morale -1) for +2 tons on all its later deliveries.
7. A Lissom & Vane container sits at a ring dock where it should not be. Docks you land at point the way. Once found: haul it to the Spindle for 6 tons (morale -2) or let the crew fence it (morale +3).
8. Win: more weeks won than lost after week 16. Week 16 is the Final and counts double.

Signature detail: Dell Carver of Carver Freight, who always signs the biggest unsigned job on the board on even weeks (readable habit, so the player can take it first or leave him a bad one). The stray Lissom & Vane container whose manifest says it is in a vault on Earth.
Midpoint plan: week 8 Carver's base goes 0 to 3 (escalation); the Spindle yard opens for +2 hold overhauls (unlock).
Rival policy: Carver base tons per week (0, then 3) plus the biggest unsigned contract every even week, landing dist(pick, drop) weeks later; due tons are announced ahead.
Tracked numbers: Record (W-L), Morale, Haulers (position, cargo, eta, hold).
Fingerprint actions: send_<cid>, push, rest, night_run, overhaul, haul_crate, fence_crate.

Selftest history
1. base 1/3, contracts any-to-any, loss -1 only: random 0.00 (early_end 0.19 SHORT), heuristic 0.05 TOO HARD.
2. base 0/2, 60 percent drops at hub, tons 2-4 then 3-5: random 0.00 (early_end 0.24 SHORT), heuristic 0.04 TOO HARD.
3. contracts 50/30/20 hub-out/hub-in/ring, won week morale +1, timing-aware heuristic: random 0.00 clean, heuristic 0.16 TOO HARD.
4. Carver signs every other week all game (was every week after 8): random 0.02, heuristic 0.67, clean.
5. Carver base 3 after week 8: random 0.01, heuristic 0.43, clean.
6. Carver lands dist weeks after signing (sheet/engine mismatch fix): random 0.02, heuristic 0.51, clean. Final.
