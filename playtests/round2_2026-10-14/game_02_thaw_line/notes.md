# Thaw Line (playtest game 02)

## Rolls
FORM=10 Heist | SET=10 Arctic research station | ROLE=39 Hotel manager who can see ghosts | LOOP=31 Place one tile, adjacency scores | CLOCK=12 Map floods tile by tile | TWIST=24 Huge advantage that decays | WIN=19 Specimen with all three traits | MAP=10 Deck of encounters | TONE=2 Dry humor

## How the rolls became the game
- Heist: turns 1-9 are the plan phase (build the station line with limited intel from the ghosts), turns 10-18 the execute phase (the shelf calves, the plan meets the hidden crack order).
- Arctic station + hotel manager: Kelvin Station pays its bills with Bunks; guests pay in diesel.
- Ghosts: the 1971 crew know the crack order and will tell you two slots at a time, for 2 fuel, before the calving.
- Tile placement: 12 slots, hand of 3 modules, next empty slot only. Adjacency: a Generator powers everything within two slots.
- Flood: one slot per turn drowns at the end of turns 10 to 17, hidden order, one-turn groan warning.
- Decaying advantage: 52 fuel at start, burned every night; only powered Bunks refill it.
- Three traits: SEQ, ALIVE, STABLE, each proven by a d6 trial whose target drops with powered Labs.
- Deck of encounters: storm, charter, supply drop, ghost sighting, quiet night.

## Rulesheet
1. The station is a line of 12 slots; slots 1-3 hold a Freezer, a Bunk and a Generator. Each turn place one of your 3 drawn modules in the next empty slot, or do one other thing (hunkering down redraws the hand and saves 1 fuel).
2. A module is powered if a Generator stands within two slots of it, water or not. Each turn burns 2 fuel plus 1 per Generator; each powered Bunk pays 3 back. Fuel starts at 52 and only guests refill it.
3. Trials (3 fuel, need a powered Lab) prove one trait each: roll d6, need 5 minus powered Labs (min 3). SEQUENCED any time; ALIVE and STABLE only after the thaw on turn 10.
4. After turn 9 the shelf calves: one slot drowns at the end of each of turns 10 to 17 in a hidden order, and the ice groans under the next one a turn early. Before the calving, ask the ghosts (2 fuel) to learn when the two lowest unrevealed slots drown.
5. The Specimen lives in your Freezers: with no powered Freezer standing you cannot run trials or board the plane.
6. Swap (2 fuel): trade the groaning module with its ridge-side neighbour (sea-side if there is none) before the sea takes the slot.
7. Two failed trials in a row open a Seance (2 fuel): your next trial needs only 2+.
8. Win: three traits, then Call the plane (2 fuel): roll d6, need 4 minus powered Radios (min 2). Lose: fuel 0, nothing standing, or the end of turn 18 (the plane lands then anyway: win only with 3 traits and a powered Freezer).

## Signature detail
The 1971 crew (Dr. Pernille Vang and company) are the intel source: they died in the ice and know exactly which slot goes when, but only talk before the calving. They call the shelf Gunnar.

## Midpoint plan
Turn 10: Gunnar calves. Escalation: one slot drowns per turn through turn 17 in a hidden order. Unlock: ALIVE and STABLE trials open. The ghosts stop answering.

## Rival policy
The shelf (Gunnar): a hidden shuffled crack order over the 12 slots; each execute-phase turn it drowns the next slot and groans under the one after.

## Fingerprint
Actions: place_G, place_L, place_F, place_B, place_R, trial_seq, trial_alive, trial_stable, ask, swap, seance, call, hold
Tracked numbers: Fuel; the Line (12 slots of modules with power and flood rules); Traits 0-3.

## Tuning log
See summary.md for the rounds table.
