# Bad Quarter - playtest summary (game 08)

## Game

**Title:** Bad Quarter

**Premise:** Lissom & Vane Capital is having a bad quarter and you govern the one colony it still owns: Harrow Ring, eight docks in a circle around the Spindle hub. You run three haulers (Marlowe, Quill, Sable) on contracts off a two-job board, one order per week, against Carver Freight, whose man signs the biggest unsigned job on the board every even week. Each week your landed tons face Carver's on the fund's ledger; ties go to Carver. A won week is morale +1, a lost week morale -1, mutiny at 0. Week 8 Carver adds a tug (base 0 to 3) and the Spindle yard opens for +2 hold overhauls. A sealed fund container sits at a ring dock it should not be at; dockhands point the way. Win: more weeks won than lost after 16, with the Final counting double.

**Rolls and what they became:**
- FORM=12 Logistics: three haulers routed around a ring with transit delays (d6, a 1 slips a week).
- SET=25 Hedge fund in a bad quarter: Lissom & Vane Capital owns the colony; the weekly ledger is the game.
- ROLE=10 Colony governor: you govern Harrow Ring, bent to dispatcher-governor.
- LOOP=26 Fill a schedule grid, slots compete for the same audience: weeks are the slots; your landings and Carver's compete for each week's ledger, and Carver takes jobs off the same board you use.
- CLOCK=14 Crew morale, mutiny at zero: morale swings with wins and losses and is spent on pushes, night runs, overhauls.
- TWIST=23 Something is where it should not be: a fund container at a hidden dock, a direction clue on each landing; haul it (6 tons, morale -2) or fence it (morale +3).
- WIN=16 Finish above .500 or win the final: winning record after 16; week 16 counts double.
- MAP=2 Hex ring of 8 around a center: Spindle hub plus 8 named docks, 1 hop per ring step, hub to any dock 1 hop.
- TONE=11 Noir: rain, dockhands, Carver's horn, the night dispatcher.

**Rulesheet (verbatim):**
1. You govern Harrow Ring for Lissom & Vane Capital: the Spindle hub and 8 docks in a circle. Each week give one order: send an idle hauler on a contract, push a hauler, rest the crews, or a special job when it appears.
2. A contract is pickup, drop, tons. The trip takes 1 week per hop from where the hauler sits (hub to any dock is 1 hop). Each week in transit a hauler rolls d6: on a 1 it slips a week.
3. Each week your landed tons face Carver Freight's. More wins the week; ties go to Carver. Every even week Carver signs the biggest unsigned contract on the board and lands it 1 week per hop; his due tons are shown ahead.
4. Push: your soonest hauler arrives one week sooner, morale -1. Rest: morale +2. A won week is morale +1, a lost week morale -1. Morale 0 is mutiny: game over.
5. Two lost weeks in a row open Night Run: your heaviest hauler in transit lands now, morale -1.
6. Week 8: Carver adds a tug (base tons 0 to 3 every week) and the Spindle yard opens: Overhaul an idle hauler at the hub (1 week, morale -1) for +2 tons on all its later deliveries.
7. A Lissom & Vane container sits at a ring dock where it should not be. Docks you land at point the way. Once found: haul it to the Spindle for 6 tons (morale -2) or let the crew fence it (morale +3).
8. Win: more weeks won than lost after week 16. Week 16 is the Final and counts double.

**Fingerprint:**
- Action ids: send_<cid>, push, rest, night_run, overhaul, haul_crate, fence_crate
- Tracked numbers: Record (W-L), Morale, Haulers (position, cargo tons, eta, hold)
- Signature detail: Dell Carver's readable habit (biggest unsigned job, even weeks) and the misfiled container.

## Engine

**Tuning rounds:**

| Run | Policy | win_rate | turn_avg | Flags | What changed before this run |
|---|---|---|---|---|---|
| 1 | random | 0.00 | 14.4 | SHORT GAMES (early_end 0.19) | first draft: Carver base 1 then 3, any-to-any contracts, lost week morale -1 only |
| 1 | heuristic | 0.05 | 17.0 | TOO HARD | |
| 2 | random | 0.00 | 13.9 | SHORT GAMES (early_end 0.24) | Carver base 0 then 2, 60 percent of drops at hub, tons 2-4 then 3-5 |
| 2 | heuristic | 0.04 | 17.0 | TOO HARD | |
| 3 | random | 0.00 | 16.4 | none (early_end 0.02) | contracts 50/30/20 hub-out, hub-in, dock-to-dock; won week morale +1; labels show landing week; timing-aware heuristic |
| 3 | heuristic | 0.16 | 17.0 | TOO HARD | |
| 4 | random | 0.02 | 16.7 | none | Carver signs every other week all game (was every week after week 8) |
| 4 | heuristic | 0.67 | 17.0 | none | |
| 5 | random | 0.01 | 16.6 | none | Carver base 3 after week 8 (was 2) |
| 5 | heuristic | 0.43 | 17.0 | none | |
| 6 | random | 0.02 | 16.4 | none | Carver lands dist weeks after signing, not dist+1 (sheet and engine disagreed) |
| 6 | heuristic | 0.51 | 17.0 | none | final |

A per-week analysis between runs 3 and 4 found the hole: after week 8 Carver averaged 5.5 to 6 tons a week against the player's 3, so the back half was unwinnable regardless of play. Making Carver sign every other week instead of every week fixed the design rather than the numbers.

**Final selftest:** random 300 games: win_rate 0.02, crashes 0, turn_min 7, turn_avg 16.4, early_wins_before_half 0, early_end_rate 0.02, no flags. Heuristic 300 games: win_rate 0.51, crashes 0, turn_avg 17.0, early_wins_before_half 0, early_end_rate 0.00, no flags.

**Crashes during play:** none. All 16 steps plus one `status` call ran clean.

**Rulesheet and engine mismatches found during play:**
1. Rule 6 says an overhaul takes 1 week; the engine applies the transit slip roll to a hauler in the yard, and Quill's overhaul slipped to 2 weeks at turn 13. Either exempt yard time from the roll or say "1 week, may slip" on the sheet.
2. Minor: send labels say "lands week 17" for a 3-week job sent at turn 15, which is true without a push but hides that a push can drag it into week 16. The label is honest; the sheet could say pushes count toward the Final.
3. Minor: the sheet says "Docks you land at point the way" and the engine only gives clues and finds on a drop, never on a pickup. Consistent, but it made the twist unreachable (see Problems).

**Free-text refusal:** At turn 9 the player typed "Send Sable round to Eelmarket to pick up that container before Carver finds it." No action maps to it (no contract to Eelmarket, container not yet found). The GM answered in one line that haulers only move on signed contracts and the container only appears on a landing, re-listed the four options, and did not advance. The engine was never called. Worked as the skill specifies.

## Playthrough

Marlowe opened with a one-hop 4-ton run and the game's first clue; then Quill rolled a 1 on her own one-hop and week 2 was lost 0 to 0 under the tie rule. Sable's slip at turn 3 shoved her landing into Carver's 6-ton week 5, so the player bought week 4 with a push and conceded week 5. The front half closed 5-2 on short hub-out jobs while Carver's man kept signing into weeks he already owned, and one job expired before he could sign it at all. At the midpoint Marlowe and Quill both slipped, Carver's base went to 3, and two zero-landing weeks opened Night Run; the player used it not as a rescue but as tempo, teleporting Sable's 5 tons home three weeks early so all three haulers sat at the hub for the yard. Two overhauls (one of which slipped) turned every 3-ton job into a 5 or 7, which is the margin over Carver's base. At 8-6 with one point needed, the board locked: both jobs landed week 17 from any berth, nothing was in transit, and a full board posts nothing new. The only line was to sign the 3-week Cinder Row to Eelmarket job and plan to push it into the Final; the clean transit roll on week 15 plus the board slot that signing opened produced a one-hop Spindle to Halfmoon run for Quill's 7 tons. Quill rolled exactly a 2 (need 2+) in the Final: 7 tons to Carver's 3, double points, season 10-7.

**Result:** WIN, season 10-7.
**Final numbers:** Record 10-7 | Morale 4 | Marlowe>Eelmarket 7t 1w, Quill@Halfmoon+, Sable@Spindle. Container never found.
**Turns played:** 16 of 16, plus one `status` and one refused free-text order.

## Decisions

- Genuinely hard turns: 9 (T4 push vs deny Carver the Fogline job; T8 stack week 10 vs feed week 9; T10 Night Run as tempo; T11 overhaul vs send; T12 which job around Carver's 9-ton week 13; T13 overhaul Quill at morale 6; T14 Night Run vs send Sable; T15 the "week 17" gambit; T16 send vs push at equal odds).
- Obvious turns: 7 (T1, T2, T3, T5, T6, T7, T9: one job clearly dominated, or every landing week was already decided).

## Emergence

1. A one-hop sure thing slipped at turn 2 and the tie rule turned 0 vs 0 into a loss and a morale hit.
2. Sable's slip at turn 3 collided her landing with Carver's week 5, which made a one-morale push the right answer for week 4.
3. The Halfmoon to Dovetail job aged off the board the same week Carver's man came to sign, so he signed nothing (the board ages before Carver signs).
4. Carver's biggest-job habit became a tool: at turn 12 the player left him the Cinder Row job so it landed in week 13, a week he already owned at 6, instead of poisoning week 14.
5. Night Run, designed as a loss-streak rescue, was the best tempo play of the game: it brought Sable home three weeks early into a week already won.
6. The yard slip: an overhaul advertised as 1 week took 2 because the engine rolls transit for yard time.
7. Board lock at turn 15: a full board of 3-week jobs with nothing in transit meant no option could touch weeks 15 or 16, and the only way out was signing a job labelled "week 17".
8. Signing that job opened a slot, and the slot posted the one-hop run that actually won the Final: the fix created the solution.
9. The container was triangulated to Eelmarket by turn 5 and never reached; no contract dropped there until the week after the ledger closed.

Count: 9.

## Problems

- **Twist inert (broken-ish):** The container is discoverable only on a drop at its dock, and the player cannot steer a hauler there without a contract that happens to end there. Every clue pointed at the same dock from turn 5 and the haul-or-fence choice never came. Needs a cheap "sweep a dock" order, or finding on pickup as well as drop.
- **Too many conceded weeks (repetitive):** 6 of 16 weeks (5, 8, 9, 12, 13, 15) had zero landings, half of them structurally unavoidable because one order per week and 2-3 week trips cannot cover every slot. The weeks themselves were quick, but the "nothing lands, LOSS" line got familiar.
- **Hidden hauler choice (unfair, mild):** send options always use the closest idle hauler, so the player cannot pick a worse-placed hauler on purpose (to keep the overhauled one at the hub, for instance). It never bit this game but it will.
- **Board lock (unfair, late):** a full board of long jobs with nothing in transit at turn 15 left no option that reached the Final. A clutch line existed, but only because the player read the push rule against the label; a less careful player sees "week 17, week 17, rest" and loses 8-9.
- **Yard slip mismatch:** see Engine.
- **Difficulty vs selftest:** the heuristic predicted 0.51. The human went 10-7 but needed a 5-in-6 roll in the Final after a nine-turn stretch of near-even play; that matches a coin-flip-plus design, so the prediction held. Not too easy, not too hard, but swingier on dice than the average suggests (6 slips in the first 13 transit rolls).

## Fun rating

7/10. The ledger-slot idea gave every dispatch a landing week to think about, Carver's schedule was readable enough to play around, and the overhaul decision was a real economy call with a visible payoff. The dead twist and the stretch of forced zero weeks keep it from an 8.

## Would replay

Yes. The seed changes the board, the container dock and the slip rolls, and I want to try keeping one hauler parked at the hub for one-hop jobs from week 8 on, which I think removes most of the conceded weeks. If the container hunt got a sweep order it would be a clear 8.
