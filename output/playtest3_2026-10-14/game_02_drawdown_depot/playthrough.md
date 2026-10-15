# Drawdown Depot - playthrough (seed 360553)

GM presentation

Drawdown Depot
A smuggler in debt runs three night buses for the Low Ward, whose beds are the creditor's collateral, while the falling water table opens deeper tunnels and dries the wells.

Rules (from `engine.py rules`, 8 lines): fleet and one action a night; pay and stall per layer; water table opens Layer 3 at 10; wells fail at 8; the Assessor's hidden cycle (2 richest nights, 1 haunt, 1 home); impound; purchases (shore, sink); goal.

Goal: at least 14 beds after night 16.   Lose if: beds below 3.   Turns: 16

Plan going in: the Assessor strikes the layer whose buses paid most IN TOTAL, so stacking cheap buses on one layer deflects it from a dearer bus. Learn the cycle from the strike texts.

| Turn | Status at start | Choice | Narration |
|------|-----------------|--------|-----------|
| 1 | Beds 14 / Runs S S L2 / Table 16 / Struck - | Move a bus Street to Layer 1 | The Layer 2 bus stalled on a 2; the Assessor stayed home, so it is a home night; the Ward drips down to 13. |
| 2 | Beds 13 / Runs L1 S L2 / Table 15 / Struck - | Move a bus Street to Layer 1 | The new Layer 1 bus pays nothing, the old one stalls, and the Assessor visits its haunt: Layer 1. One bus is impounded. The haunt is Layer 1, and since night 1 was home and night 2 haunt, nights 3 and 4 must be richest nights. |
| 3 | Beds 14 / Runs X L1 L2 / Table 14 / Struck L1 | Shore Layer 2 (-1 bed) | Layer 2 is shored (stall 2 to 1). The Layer 2 bus stalls anyway on a 1, and the Assessor takes the richest layer, Layer 1, impounding the Layer 1 bus (forfeits 2). Beds 11. |
| 4 | Beds 11 / Runs S X L2 / Table 13 / Struck L1 | Move a bus Street to Layer 2 | A rich night: the Layer 2 bus pays 3 but is the richest, so it is impounded and forfeits it. Beds 9, and the fleet is Layer 2, Street, impounded. Next night is a known home night. |
| 5 | Beds 9 / Runs L2 S X / Table 12 / Struck L2 | Move a bus Street to Layer 2 | A safe home night; the new bus is in transit, the old Layer 2 bus stalls on a 1 despite the shoring, and nobody earns. Beds 7. |
| 6 | Beds 7 / Runs L2 L2 S / Table 11 / Struck - | Move a bus Street to Layer 2 | A haunt night and Layer 1 is empty, so the Assessor finds nothing; two Layer 2 buses pay 6. Beds 11. The table falls to 10 and Layer 3 opens. |
| 7 | Beds 11 / Runs L2 L2 L2 / Table 10 / Struck L1 | Hold the roster | Three Layer 2 buses pay 9 and the Assessor takes the richest layer as predicted, impounding one and forfeiting 3. Beds 15. |
| 8 | Beds 15 / Runs X L2 L2 / Table 9 / Struck L2 | Hold the roster | Another rich night: the Assessor impounds a second Layer 2 bus, forfeiting 3. Beds 16; the table falls to 8 and the wells fail. |
| 9 | Beds 16 / Runs S X L2 / Table 8 / Struck L2 | Move a bus Street to Layer 2 | A home night, so the Assessor stays home. The wells are dry: the Ward loses 5. Beds 14. |
| 10 | Beds 14 / Runs L2 S L2 / Table 7 / Struck - | Sink a well (-6 beds) | A haunt night with Layer 1 empty, so no strike. One Layer 2 bus stalls, the wells now cost only 3. Beds 9. (Calculated the plan: after this I tried small simulations of my own fixed plans; moving the Street bus to Layer 2 as soon as possible won best, about one game in three.) |
| 11 | Beds 9 / Runs L2 S L2 / Table 6 / Struck L1 | Move a bus Street to Layer 2 | A rich night: the moving bus is safe, two Layer 2 buses pay 6, and the Assessor impounds one, forfeiting 3. Beds 9. |
| 12 | Beds 9 / Runs X L2 L2 / Table 5 / Struck L2 | Hold the roster | Another rich night; the Assessor impounds the second bus in a row, forfeiting 3. Beds 9 with four nights left. |
| 13 | Beds 9 / Runs L2 S L2 / Table 4 / Struck L2 | Move a bus Street to Layer 2 | The Assessor is at recess on what should have been a home night, so nothing strikes. One bus pays 3 while the others are in transit; beds hold at 9 with three nights left and 14 needed. |
| 14 | Beds 9 / Runs L2 S L2 / Table 3 / Struck - | Move a bus Street to Layer 3 | A haunt night with Layer 1 empty, so no strike; the Layer 3 bus is in transit, one Layer 2 bus stalls again (a 1), and beds stay at 9 with two rich nights left and 14 needed. |
| 15 | Beds 9 / Runs L2 L3 L2 / Table 2 / Struck L1 | Hold the roster | Bad dice: a Layer 2 bus and the Layer 3 bus both stall, and the Assessor impounds the only paying Layer 2 bus. Beds 6; even a perfect last night cannot reach 14. |
| 16 | Beds 6 / Runs L2 L3 X / Table 1 / Struck L2 | Hold the roster | The Assessor takes recess; one Layer 2 bus pays 3, Layer 3 stalls, the wells take 3. Final: 6 beds, short of 14. LOSS. |

## Result

LOSS after 16 of 16 turns: the audit found 6 beds, short of 14 (seed 360553). Beds peaked at 16 on turn 9, then bled under the dry wells and three more Assessor hits; two stalls on night 15 put the goal out of reach before the last night.

## Autopsy (as shown to the player)

You lost the audit with 6 beds against the 14 needed, and by turn 15 even the best move won only 8 percent of games (0.075).
The game turned on turn 2 (win chance 0.57 down to 0.35): a second bus sent to Layer 1 sat on the Assessor's hidden haunt and was impounded; moving the Layer 1 bus to Layer 2 instead would have lifted your odds from 0.25 to 0.58, though nothing on the table could have told you that yet.
The other missed move was turn 6, where holding (0.30) beat sending the third bus to Layer 2 (0.15).
Fourteen of your sixteen turns had a clearly better and worse option, and no flat stretch was flagged.
