# BLACK LANTERNS - playthrough transcript

## Rolls

Command: `echo "SET=$((RANDOM%40+1)) ROLE=$((RANDOM%40+1)) LOOP=$((RANDOM%24+1)) CLOCK=$((RANDOM%18+1)) TWIST=$((RANDOM%36+1)) WIN=$((RANDOM%14+1)) MAP=$((RANDOM%10+1)) TONE=$((RANDOM%8+1))"`

Result: `SET=11 ROLE=32 LOOP=21 CLOCK=1 TWIST=14 WIN=6 MAP=5 TONE=6`

- SET 11: Pirate archipelago
- ROLE 32: Lighthouse keeper with a boat
- LOOP 21: Dig deeper, each layer riskier and richer
- CLOCK 1: Fuel or food runs out
- TWIST 14: Each location can only be visited once
- WIN 6: Hold the most nodes when the clock ends
- MAP 5: Two layers: surface and below
- TONE 6: Military procedural

Novelty check skipped (no played_log). In-game dice: 100 d6 pre-rolled with Bash before play and consumed strictly in order for every roll (player dive first, then the Vixen's hidden roll each turn): `1 4 5 2 2 4 3 1 2 5 1 3 2 4 ...`

## Present

```
BLACK LANTERNS
The Navy has quit the Tern Islands; you keep the last Admiralty light on Beacon Rock, and with one boat and a shrinking oil store you must put more beacons alight than the pirate Sable Morrow before her black lanterns own the archipelago.

Rules
1. One order per turn: SAIL to a linked islet (1 oil), DIVE one deck deeper at this islet's wreck, LIGHT this islet's beacon (2 oil), or HOME to Beacon Rock (1 oil) to buy oil and gear.
2. Beacon Rock burns 1 oil every turn regardless. Oil 0 means the great light dies and you lose.
3. Wrecks have 3 decks. Deck 1: d6 need 2+, pays 2 silver. Deck 2: need 3+, 4 silver. Deck 3: need 4+, 7 silver. Outer-ring wrecks pay +2 per deck. A failed roll collapses the wreck: dive over, lose 2 oil.
4. When you sail away from an islet its channel is marked FOUL. You can never return there or pass through it, so dive and light before you leave.
5. Captain Morrow's sloop Vixen lights black lanterns on free islets. You may LIGHT an islet she holds: d6 need 4+ (2 oil; on a fail she keeps it and you lose 1 more oil).
6. At Beacon Rock: oil costs about 2 silver each (price drifts). Diving Bell 6 silver (+1 on every dive roll). Chart 3 silver (reveals Morrow's next two targets).
7. Links: Beacon Rock touches the four inner islets. Each inner islet touches its two inner neighbours and one outer islet. Each outer islet touches its two outer neighbours.

Goal: Hold more lit beacons than Morrow when turn 16 ends (ties go to her).   Lose if: Oil hits 0.   Turns: 16

Turn 1 of 16 | Oil 24 | Silver 0 | Beacons 0 vs Vixen 0 | Beacon Rock
Keeper's log, first watch. Inner ring: Gull Spit (N), Hangman's Key (E), Coral Bar (S), Dutchman's Rest (W). Outer ring beyond each: Widow Reef, the Anvil, Saltmarsh Cay, Blackwater Hole.
Vixen's topsails sighted bearing east, beyond the Anvil, standing in.
Store: 24 casks of oil, no silver, no gear. Nothing to buy yet.
1. Sail north to Gull Spit
2. Sail east to Hangman's Key
3. Sail south to Coral Bar
4. Sail west to Dutchman's Rest
or say anything else.
```

## Turns

**Player:** Quick math first: the Rock burns 16 of my 24 before I so much as cast off. Every sail and every light comes out of the other 8, so I need dive silver early. She's east, so the east islets go first if I don't take them. 2.

```
Sail east. Oil 24, minus 1 for the passage, minus 1 for the Rock's burn: 22.
Hangman's Key: a gibbet post on the spit and, under the lee, HMS Resolute, navy brig, broken on the bar. Forward hatch open. Burn scoring along the hull line, old powder marks.
Dusk. A black lantern flares on the Anvil, two miles east. Morrow has her first.
Note for the log: Beacon Rock is reached only through an inner islet you have not yet left. Each inner islet is a door home that closes behind you.

Turn 2 of 16 | Oil 22 | Silver 0 | Beacons 0 vs Vixen 1 | Hangman's Key
The Resolute's deck 1 is the gun deck, hatch clear. Deck 1 needs 2+ and pays 2 silver.
1. Dive deck 1
2. Light the beacon here (2 oil)
3. Sail to the Anvil (hers, outer, 1 oil)
4. Sail to Gull Spit or Coral Bar (1 oil)
or say anything else.
```

**Player:** 1. Dive deck 1.

```
Dive. roll 4 (need 2+) success. Gun deck: brass fittings and a pay chest, 2 silver aboard.
Below the gun deck the Resolute's magazine is still packed. Deck 2 here: a failed roll costs 3 oil, not 2.
Rock burns 1. Vixen not sighted this watch.

Turn 3 of 16 | Oil 21 | Silver 2 | Beacons 0 vs Vixen 1 | Hangman's Key
Deck 2 needs 3+ and pays 4 silver. Deck 3 beyond it needs 4+ and pays 7.
1. Dive deck 2 (magazine risk)
2. Light the beacon here (2 oil)
3. Sail to the Anvil (hers, 1 oil)
4. Sail to Gull Spit or Coral Bar (1 oil)
or say anything else.
```

**Player:** Two in three for 4 silver, and 4 silver is two oil. The downside is 3 oil. Expected value is positive, barely, and I need silver to matter at all. 1.

```
Dive deck 2. roll 2 (need 3+) FAIL. A bulkhead gives, the magazine floods and goes up in a soft thump that lifts the whole wreck. You surface in a slick of split casks. Lose 3 oil. The Resolute is finished.
Rock burns 1. South, across the sound, a second black lantern lights on Saltmarsh Cay.

Turn 4 of 16 | Oil 17 | Silver 2 | Beacons 0 vs Vixen 2 | Hangman's Key
Nothing left to dive here. The beacon cairn stands dry on the spit.
1. Light the beacon here (2 oil)
2. Sail to the Anvil (hers, 1 oil)
3. Sail to Gull Spit (1 oil)
4. Sail to Coral Bar (1 oil)
or say anything else.
```

**Player:** Light it. Leaving an islet unlit after all that is throwing away the only thing that scores. 1.

```
Light. 2 oil into the cairn lamp; the Hangman's Key beacon takes and holds, white against her two black. Rock burns 1.
Vixen's sails seen south-west of the Anvil, running before the wind. Nothing lit this watch.

Turn 5 of 16 | Oil 14 | Silver 2 | Beacons 1 vs Vixen 2 | Hangman's Key
The moment you sail, Hangman's Key is FOUL behind you. From here: the Anvil (outer, hers, wreck undived), Gull Spit or Coral Bar (inner, free).
1. Sail to the Anvil (1 oil)
2. Sail to Gull Spit (1 oil)
3. Sail to Coral Bar (1 oil)
or say anything else.
```

**Player:** 14 oil, 11 turns. Outer wrecks pay 4/6/9, nearly double. Plan: Anvil, dive, contest her lantern, then Widow Reef, Gull Spit, home with a purse. Three sails and a light before I'm home. Tight, but inner wrecks won't fund anything. 1.

```
Sail east, a hard beat round the Hangman's bar. Oil 12 after passage and burn. Hangman's Key: FOUL.
The Anvil: a black iron rock with Morrow's lantern on a cairn, burning tar. Below, the Peregrine, India merchantman, deep-hulled and unbroken. Outer wreck: 4, 6, 9 silver by deck.
Vixen nowhere in sight. She has moved on.

Turn 6 of 16 | Oil 12 | Silver 2 | Beacons 1 vs Vixen 2 | The Anvil (hers)
1. Dive deck 1 (need 2+, 4 silver)
2. Light here, contest her lantern (2 oil, need 4+)
3. Sail to Widow Reef (1 oil)
4. Sail to Saltmarsh Cay (hers, 1 oil)
or say anything else.
```

**Player:** 1.

```
Dive. roll 1 (need 2+) FAIL. The Peregrine's hatch coaming shears as you go through and the deck comes down on the hold. You claw out under a drifting beam. Lose 2 oil. The wreck is sealed.
Rock burns 1. Across the sound a third black lantern: Coral Bar. Morrow holds the inner south now.

Turn 7 of 16 | Oil 9 | Silver 2 | Beacons 1 vs Vixen 3 | The Anvil (hers)
Her lantern still burns on the cairn above you. Widow Reef north, Saltmarsh south. Hangman's is FOUL.
1. Light here, contest her lantern (2 oil, need 4+; fail costs 1 more)
2. Sail to Widow Reef (1 oil)
3. Sail to Saltmarsh Cay (hers, 1 oil)
or say anything else.
```

**Player:** status

```
Turn 7 of 16 | Oil 9 | Silver 2 | Beacons 1 vs Vixen 3 | The Anvil (hers)
Yours: Hangman's Key. Hers: the Anvil, Saltmarsh Cay, Coral Bar. Free: Gull Spit, Dutchman's Rest, Widow Reef, Blackwater Hole.
FOUL: Hangman's Key. Wrecks collapsed: Resolute (Hangman's), Peregrine (Anvil).
Gear: none. Rock burns 1 oil per turn; 9 turns remain.
Routes home: Widow Reef to Gull Spit to Beacon Rock, or Saltmarsh Cay to Coral Bar to Beacon Rock.
```

**Player:** Nine oil, nine turns, home two sails off. A contest at even odds could leave me at 5 with nothing to show. Widow Reef is free and undived. 2.

```
Sail north along the outer reef. Oil 7 after passage and burn. The Anvil: FOUL.
Widow Reef: a low coral crescent, free, no lantern. On the seaward side, HMS Tern, Admiralty lightship, lying on her beam. Her lantern tower is intact, which is more than most wrecks keep. Outer wreck: 4, 6, 9 by deck.
Vixen: a sail far to the south, bound west.

Turn 8 of 16 | Oil 7 | Silver 2 | Beacons 1 vs Vixen 3 | Widow Reef
1. Dive deck 1 (need 2+, 4 silver)
2. Light the beacon here (2 oil)
3. Sail to Gull Spit (1 oil)
4. Sail to Blackwater Hole (1 oil)
or say anything else.
```

**Player:** Deck 1 is five in six. Without the silver there is no point going home. 1.

```
Dive. roll 1 (need 2+) FAIL. The Tern's tower, the one sound thing on her, rolls off its mount as the hull settles and pins the forward companion. You get clear with your lungs on fire. Lose 2 oil.
Rock burns 1. No lantern lit this watch; Morrow is somewhere west.

Turn 9 of 16 | Oil 4 | Silver 2 | Beacons 1 vs Vixen 3 | Widow Reef
The Rock takes 1 a turn. Gull Spit is one sail, Beacon Rock two. Your purse buys 1 oil, perhaps 2.
1. Light the beacon here (2 oil)
2. Sail to Gull Spit (1 oil)
3. Sail to Blackwater Hole (1 oil)
or say anything else.
```

**Player:** Let me do the arithmetic. Four oil. Sail Gull Spit: 2. Sail home: 1, buy at best 2 oil with my 2 silver: 3, burn: 2. Then I'm at the Rock with 2 oil, nothing to sell, and the Rock eats me in two turns. No wreck in reach pays before I'm dark. There is no line back. Light Widow Reef. If the Rock goes out, it goes out with two Admiralty beacons burning.

```
Light. 2 oil into the Tern's own lantern, hauled up onto the reef cairn. Widow Reef shows white. Rock burns 1.
Morrow's sail comes north along the outer ring, sights your new light on Widow Reef, and stands off. By dark a black lantern burns on Blackwater Hole instead.

Turn 10 of 16 | Oil 1 | Silver 2 | Beacons 2 vs Vixen 4 | Widow Reef
One cask left. Any order burns it.
1. Sail to Gull Spit (1 oil)
2. Sail to Blackwater Hole (hers, 1 oil)
3. Stand your watch here
or say anything else.
```

**Player:** Sail for Gull Spit. If the light is going out, I'll be pointed at home when it does. 1.

```
Sail south-west for Gull Spit. The last cask goes into the boat's lamp for the passage and Beacon Rock has nothing left to burn. Halfway across the sound the great light on the Rock gutters, flares once, and goes dark. Oil 0.

RESULT: LOSS. The great light died on turn 10 of 16.
Final: Oil 0 | Silver 2 | Beacons 2 vs Vixen 4
Verdict: three failed dives in four cost 7 oil and the silver that would have bought it back; after the Anvil collapse no route home paid.

Save this one to the library? Give it a name, or say no.
```

**Player:** No. Not as it stands. Fix the oil and I'd try it again.

(played_log.md and library writes skipped per playtest instructions.)
