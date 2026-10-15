# Reef Control - session notes

Title: Reef Control

Rolls: FORM=7 (build order) SET=9 (shipwreck atoll) ROLE=35 (air traffic controller) LOOP=34 (visit one district, spend, poll) CLOCK=1 (food runs out) TWIST=39 (rules change on a published schedule) WIN=14 (keep a settlement above a threshold) MAP=3 (5x5 grid, fog) TONE=8 (cozy with teeth)

Rulesheet:
1. Each day pick one: forage a tile, or build one thing with food (labor). Camp is C3. At dawn the camp eats 1 food per 3 souls (rounded up).
2. Forage: roll d6, need 4+ for the tile's full yield, else half. Every visit, yours or Dekker's, lowers that tile's yield by 1 (min 2).
3. The inner ring is on foot; the outer ring needs the Raft. The Wreck is somewhere on the outer ring; visiting it unlocks Storehouse and Tower.
4. Builds (food): Trap 4 (water rolls +1), Raft 6, Smokehouse 6 (all rolls +1), Storehouse 7, Palisade 7, Tower 9 (day 10+).
5. Tide table: days 5, 10, 15, 20 are king tides: reef and Wreck closed, lagoon yield doubled. Dawn of day 12 a storm takes half your food unless Storehouse.
6. Dekker's crew (3 who split off) strips one tile a day near his corner. From day 10 they raid 3 food a night unless Palisade.
7. After the dawn meal: food at 0, one soul walks to Dekker; food 20+, one of Dekker's walks to you. Fewer than 6 souls and the camp is done. Two bad forage rolls in a row: Dekker offers 8 food for one soul.
8. Tower lit at dawn on days 13 and 17: roll d6, 3+ for a 12-food airdrop. Win: 8+ souls when the ship comes after day 20.

Signature detail: First Officer Dekker's splinter camp on a hidden corner of the atoll. His crew strips the richest tile within two squares of his corner every day, and the smoke tells you where (the tell reveals that tile on the map). People walk between the camps based on who has food: food 0 at dawn loses a soul to him, food 20+ pulls one of his back. The published schedule is the tide table plus the storm, the planes and the ship.

Tracked numbers: Food, Souls, Built (list of structures).

Midpoint plan: day 10 is a king tide and the day Dekker's night raids begin (3 food a night, blocked by Palisade); the Tower unlocks the same day, which turns the planes on days 13 and 17 into 12-food airdrops on a 3+. Dawn of day 12 the storm halves food unless Storehouse (which needs the Wreck, which needs the Raft).

Rival policy in one line: each day Dekker strips the highest-yield tile within Chebyshev distance 2 of his corner by 1 (min 2) and the event names the tile; from the night of day 10 he also takes 3 food unless Palisade.

Loss-streak lever: after two failed forage rolls in a row, "Dekker's bargain" (one soul for 8 food) appears while souls > 6.

Fingerprint: actions = forage_<tile> (one id per reachable tile, e.g. forage_D2), build_trap, build_raft, build_smoke, build_store, build_wall, build_tower, bargain. Tracked = food, souls, built.
