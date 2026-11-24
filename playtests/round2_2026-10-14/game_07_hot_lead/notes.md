# Hot Lead - session notes

Title: Hot Lead
Date: 2026-10-14 (playtest2, game 07)

## Rolls

FORM=11 Breeding | SET=35 A 1920s newspaper | ROLE=13 Spymaster | LOOP=24 Negotiate, bluff, or fight each encounter | CLOCK=10 Unrest rises when ignored | TWIST=41 One NPC always lies | WIN=11 Map the whole board | MAP=12 A bracket | TONE=9 Workplace comedy

How they became the game:
- Breeding -> cross two leads into a draft, inspect the fact-check verdict, keep (press) or cull (spike).
- Spymaster in a newspaper -> the city editor runs a ring of four stringers (informants).
- Negotiate/bluff/fight -> pay / bluff / lean on the stringer at your desk each day.
- Unrest rises when ignored -> newsroom Unrest +1 each quiet day; 12 is a walkout.
- One NPC always lies -> one stringer is the liar; any story with their lead is false; deduce and fire them.
- Map the whole board on a bracket -> 4 rackets -> 2 lieutenants -> Mr. Gray; all 7 mapped wins.
- Workplace comedy -> sulking stringers, gossip column, the morgue, Kessler at the Bugle.

## Rulesheet

1. Each day one stringer brings a lead on an open node. Pay (5/7/9 cash by tier), bluff (roll 4+; 3+ if they are cleared), or lean (free and sure, but they sulk 4 days and bring nothing).
2. Cross two leads on the same node from different stringers into a draft. The fact-checker rolls 3+ (2+ if one source is cleared, no roll if both are) to call it solid or shaky; a miss is unclear.
3. Solid drafts go to press next day. Shaky drafts are burned on the spot. Unclear drafts go to press next day unless you spike them, which returns the leads.
4. True story: node mapped, +8 cash, Unrest -4, both stringers cleared. False: retraction, -6 cash, Unrest +3, and one of the two is your liar.
5. One of your four stringers always lies; any story with their lead is false. Prove who and they are fired.
6. From day 4, Unrest +1 each day nothing prints. Unrest 12 and the newsroom walks out.
7. Mapping both rackets under a lieutenant opens him; both lieutenants open the Boss; leads left on a mapped node point up at the man above. Kessler at the Bugle hunts Docks, Hooch, Numbers, Union, Cronin, Pike in that order: his scoop maps the node for Unrest +1, but he waits while you hold a draft on it; beat him to it for +4 cash. Only you can map the Boss.
8. Any day with no draft waiting you may run the gossip column instead: Unrest -2, +3 cash, counts as printing. Two failed rolls in a row open the morgue for a free, always-honest archive lead; from day 13 (election week: Kessler prints on 3+, leads cost 2 more) the morgue is open every day. Win: all 7 mapped by day 24.

## Signature detail

The morgue (the paper's clippings archive) is a fifth source that never lies, so crossing an archive clipping with a stringer's lead is a clean test of that stringer. Also the newsroom rule "two sources, kid": you can never cross two leads from the same stringer.

## Tracked numbers

Cash, Unrest (0-12), Mapped (the bracket, 7 nodes with rules). Status also shows the lead count.

## Midpoint plan

Day 13 is election week: Kessler prints on 3+ instead of 5+, every lead costs 2 more, and the morgue opens every day (free honest lead daily) so the expensive lieutenant and Boss tiers stay reachable.

## Rival policy (one line)

Kessler at the Evening Bugle sniffs the first open node in the fixed order Docks, Hooch, Numbers, Union, Cronin, Pike, announces it, then each night rolls 5+ (3+ from day 13) to scoop it unless you hold a draft on it; after a scoop or being beaten he rests 3 days.

## Loss-streak lever

Two failed rolls in a row (bluff or fact-check) open the morgue: a free, always-honest archive lead.

## Fingerprint

Action ids: pay, bluff, lean, cross, spike, morgue, gossip (phones is a never-seen fallback).
Tracked numbers: cash, unrest, mapped (bracket list).
