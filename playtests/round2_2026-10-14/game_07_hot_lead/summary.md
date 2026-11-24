# Hot Lead - playtest summary (game 07)

## Game

**Title:** Hot Lead

**Premise:** It is 1928 and you run the city desk of the Daily Clarion. Four stringers feed you leads, one of them makes things up, and a crime bracket on the wall (four rackets, two lieutenants, Mr. Gray at the top) has to be exposed node by node before day 24. You breed stories by crossing two leads on the same node, inspect the fact-checker's verdict, and press or spike. Every day nothing prints the newsroom grumbles; at Unrest 12 they walk out. Kessler at the Evening Bugle hunts the same rackets in a fixed order and will happily scoop you.

**Rolls:** `FORM=11 SET=35 ROLE=13 LOOP=24 CLOCK=10 TWIST=41 WIN=11 MAP=12 TONE=9`

| Roll | Table entry | What it became |
|---|---|---|
| FORM 11 | Breeding: combine two, inspect offspring, keep or cull | Cross two leads into a draft, read the fact-check verdict (solid / shaky / unclear), press or spike |
| SET 35 | A 1920s newspaper | The Daily Clarion city desk, 1928 |
| ROLE 13 | Spymaster | The city editor runs a ring of four informants (stringers) |
| LOOP 24 | Negotiate, bluff, or fight each encounter | Pay / bluff (d6) / lean on the stringer at your desk each day |
| CLOCK 10 | Unrest rises when ignored | Newsroom Unrest +1 each quiet day from day 4; 12 = walkout |
| TWIST 41 | One NPC always lies; you do not know which | One stringer's leads are always false; prove it by set logic and fire them |
| WIN 11 | Map the whole board | All 7 bracket nodes mapped |
| MAP 12 | A bracket | Docks, Hooch, Numbers, Union -> Cronin, Pike -> Mr. Gray |
| TONE 9 | Workplace comedy | Sulking stringers, the gossip column, the morgue that never lies |

**Rulesheet (verbatim, final):**

1. Each day one stringer brings a lead on an open node. Pay (5/7/9 cash by tier), bluff (roll 4+; 3+ if they are cleared), or lean (free and sure, but they sulk 4 days and bring nothing).
2. Cross two leads on the same node from different stringers into a draft. The fact-checker rolls 3+ (2+ if one source is cleared, no roll if both are) to call it solid or shaky; a miss is unclear.
3. Solid drafts go to press next day. Shaky drafts are burned on the spot. Unclear drafts go to press next day unless you spike them, which returns the leads.
4. True story: node mapped, +8 cash, Unrest -4, both stringers cleared. False: retraction, -6 cash, Unrest +3, and one of the two is your liar.
5. One of your four stringers always lies; any story with their lead is false. Prove who and they are fired.
6. From day 4, Unrest +1 each day nothing prints. Unrest 12 and the newsroom walks out.
7. Mapping both rackets under a lieutenant opens him; both lieutenants open the Boss; leads left on a mapped node point up at the man above. Kessler at the Bugle hunts Docks, Hooch, Numbers, Union, Cronin, Pike in that order: his scoop maps the node for Unrest +1, but he waits while you hold a draft on it; beat him to it for +4 cash. Only you can map the Boss.
8. Any day with no draft waiting you may run the gossip column instead: Unrest -2, +3 cash, counts as printing. Two failed rolls in a row open the morgue for a free, always-honest archive lead; from day 13 (election week: Kessler prints on 3+, leads cost 2 more) the morgue is open every day. Win: all 7 mapped by day 24.

**Fingerprint:**
- Action ids: `pay`, `bluff`, `lean`, `cross` (as `cross-<node>-<a>-<b>`), `spike`, `morgue`, `gossip` (`phones` exists as a never-offered fallback).
- Tracked numbers: Cash, Unrest (0 to 12), Mapped (the 7-node bracket, a list with rules). Status line adds the lead count.
- Signature detail: the morgue (clippings archive) is a fifth source that never lies, so Morgue + stringer is a clean test of that stringer. House rule "two sources, kid": never two leads from the same stringer.
- Rival: Kessler at the Bugle, fixed hunting order, one-day tell, waits while you hold a draft on his target.

## Engine

**Tuning rounds** (300 games per policy each run):

| Run | Policy | win_rate | turn_avg | early_end | Flags | What changed before this run |
|---|---|---|---|---|---|---|
| 1 | random | 0.00 | 6.0 | 1.00 | SHORT | First draft: unrest start 3, scoop +2, idle +1 (+2 after day 13), fact-check 4+, visitors bring random nodes |
| 1 | heuristic | 0.00 | 8.2 | 0.85 | TOO HARD, SHORT | |
| 2 | random | 0.00 | 6.9 | 0.99 | SHORT | Visitors bring a lead on the node the desk is already working (concentration rule); unrest start 2; Kessler rests 3 after a scoop |
| 2 | heuristic | 0.00 | 10.4 | 0.73 | TOO HARD, SHORT | |
| 3 | random | 0.00 | 7.2 | 0.95 | SHORT | True story Unrest -4 (was -3); idle +1 all game; Kessler waits while you hold a draft on his target; midpoint escalation becomes Kessler 3+ and leads +2 instead of idle +2 |
| 3 | heuristic | 0.10 | 12.8 | 0.57 | TOO HARD, SHORT | |
| 4 | random | 0.01 | 7.8 | 0.92 | SHORT | Bugle scoop Unrest +1 (was +2) |
| 4 | heuristic | 0.14 | 14.0 | 0.51 | TOO HARD, SHORT | |
| 5 | random | 0.00 | 8.9 | 0.85 | SHORT | Fact-check 3+ / 2+ with one cleared (was 4+ / 3+); unrest start 1; heuristic spikes unclear at p >= 0.5 and pays rather than bluffs when unrest is high |
| 5 | heuristic | 0.09 | 15.1 | 0.49 | TOO HARD, SHORT | |
| 6 | random | 0.00 | 14.1 | 0.44 | SHORT | Gossip column available from day 1 as the pressure valve; midpoint unlock becomes the morgue open daily |
| 6 | heuristic | 0.14 | 18.8 | 0.11 | TOO HARD | |
| 7 | random | 0.14 | 14.5 | 0.45 | SHORT | Leads on a node that gets mapped move up to the parent node instead of being binned; visitor tiebreak no longer favors Kessler's target |
| 7 | heuristic | 0.40 | 18.5 | 0.15 | none | |
| 8 | random | 0.18 | 17.6 | 0.27 | SHORT | Unrest walkout 12 (was 10); heuristic valve thresholds 7 -> 9 |
| 8 | heuristic | 0.50 | 19.4 | 0.06 | none | |
| 9 | random | 0.21 | 19.6 | 0.13 | none | Grace period: idle Unrest starts day 4 |
| 9 | heuristic | 0.58 | 21.4 | 0.00 | none | |
| 10 | random | 0.21 | 19.6 | 0.13 | none | Pre-flight: rulesheet gained the "leads point up" clause and the gossip "no draft waiting" clause; heuristic leans when broke (lean still only 0.02 per game) |
| 10 | heuristic | 0.58 | 21.4 | 0.00 | none | |
| 11 | random | 0.25 | 22.5 | 0.01 | none | Lean reworked: no Unrest cost, stringer sulks 4 days (was Unrest +1, 3 days); heuristic leans when cash < cost + 6 and 3+ stringers are free (lean now 2.2 per game) |
| 11 | heuristic | 0.56 | 20.9 | 0.00 | none | Presented with these numbers |
| 12 | random | 0.27 | 22.7 | 0.01 | none | Mid-play fix: liar proof by set intersection (see below) |
| 12 | heuristic | 0.65 | 21.5 | 0.00 | none | |

**Final selftest (engine as it stands, run 12):** random win 0.27, crashes 0, turn_avg 22.7, early_end 0.01, early wins 0, no flags. Heuristic win 0.65, crashes 0, turn_avg 21.5 (0.90 of the 24-turn budget), early_end 0.00, early wins 0, no flags. The version presented to the player (run 11) was 0.25 / 0.56.

**Crash or mismatch found during play:** one rulesheet/engine mismatch, found on day 6 before the sixth step. Rule 5 says "prove who and they are fired", but the engine only recognized two proof shapes: a shaky or false pair where the other source was already cleared, or three stringers cleared. After day 3 (one of Mabel/Lou lies), a solid Ox + Lou draft would have cleared Lou and therefore proven Mabel, and a shaky Ox + Lou draft would have proven Lou by intersection, and the engine would have fired nobody in either case. Fixed by recording every liar-containing pair in s["pairs"] and deducing candidates = uncleared stringers intersected with every pair; one candidate left fires. The saved state was migrated by adding the one pair already known from the day 3 event ([["Lou","Mabel"]]), nothing else was touched, and both selftests were rerun before continuing (run 12). The fix fired on day 7 exactly as the player expected. No crashes. Engine file: `engine.py` in this folder.

Minor engine warts seen in play: the option count reached 6 on days 7, 14, 16, 17 and 18 (the skill asks for 3 to 5); while a draft waits on node X the engine still offers leads on X (visitor and morgue), which turned out to be a legal and strong play because of the lead-migration rule; and the final day's options were pure filler.

**Free-text refusal:** on day 5 the player typed "Send Mabel away and put a call out for Ox or Fitz." The GM said in one line that there is no action for summoning a stringer, re-showed the four options, and did not advance. The player then picked a listed action. Clean.

**Status check:** on day 12 the player typed `status`; the GM ran `engine.py status` and printed the status line and visible state without advancing. Clean.

## Playthrough

The first cross on day 3 came back shaky, so from the opening the game was a liar hunt: one of Mabel or Lou was fabricating, which made Ox and Fitz clean by elimination. The player leaned on both suspects in turn, partly for free leads and partly to bench them so only the clean stringers could walk through the door, then crossed Ox with Lou on day 7 and the checker named Lou, who was fired on the spot. The first real story, Hooch, did not print until the night of day 10, and that same night Kessler scooped Docks, which opened Cronin without any work. Election week opened the morgue, and Fitz plus a free archive clipping became a no-roll solid machine: Numbers printed on day 15 under Kessler's nose for a +4 bonus. On day 16 the player counted ten actions against eight days and found the only winning line: leave the finished Union pair on the desk as bait, let Kessler scoop it so the leads rode up the bracket to Pike, and spend the days on Cronin instead. Kessler took it on day 19, the same night Cronin printed, and the player had already noticed that a lead taken on a node the night it prints migrates upward, so a free Cronin clipping became the first Gray lead. Pike printed on day 21, Ox's Pike lead migrated to Gray, Gray crossed on day 22 and printed at the end of day 23.

**Result:** Win, day 23 (23 turns played of 24). **Final numbers:** Cash 40, Unrest 0/12, Mapped 7/7 (Clarion 5, Bugle 2), liar Lou fired day 7, Mabel, Fitz and Ox cleared.

## Decisions

23 turns. Genuinely hard: 6 (day 1 lean vs pay, day 4 how to handle a suspect, day 5 benching the second suspect, day 7 which pair to test, day 16 the Kessler gambit, day 19 the migration trick). Moderate: 5 (days 2, 10, 11, 14, 18). Obvious: 12, of which 1 (day 23) was a dead turn with no decision at all. Ratio of real decisions to turns about 11 of 23.

## Emergence

Moments where the systems produced something the design did not script (6):

1. The sulk rule as a scouting tool: leaning on both suspects benched them, which forced the rotation to deliver only clean stringers for three days.
2. Two shaky pairs intersecting to name Lou on day 7 (only possible after the mid-play fix, which is itself evidence the player's deduction ran ahead of the engine).
3. Hooch printing and Kessler scooping Docks on the same night, so Cronin opened on day 10 with zero leads spent on Docks.
4. Kessler sniffing Numbers while a draft sat on it: the "he waits" rule turned a threat into a +4 bonus the next night.
5. The rival as a tool: leaving Union uncrossed so the Bugle would scoop it and migrate the leads to Pike, trading 12 cash and a point of Unrest for two days.
6. Pre-stocking Gray: taking leads on Cronin and Pike on the night each printed, so they migrated upward and Gray was ready to cross the day it opened.

One negative surprise: the day 11 bluff on a cleared stringer at 3+ failed and cost a day; the morgue was still a day away.

## Problems

- Broken: the liar-proof gap (fixed mid-play, documented above). Nothing else broke.
- Boring: the opening is slow. Nine days passed before anything printed, and three of the first twelve turns were the same pay/bluff/lean choice with nothing on the desk to cross. The last turn is pure filler because a solid draft locks out gossip and every option is a lead nobody needs.
- Repetitive: pay/bluff/lean is the same menu every day, and the player never chooses which node a stringer brings; the engine's concentration rule does that. Once the liar is fired and two stringers are cleared, the fact-checker is never rolled again (five crosses in a row were "no roll needed"), so rule 2 goes quiet for the whole back half.
- Unfair: nothing felt unfair. Kessler's one-day tell and the waiting rule make him readable.
- Too easy or hard: the first half is the hard part (the selftest's losses are almost all games where the liar is never found); the back half is too easy. Lead migration plus the daily morgue made Cronin, Pike and Gray fall in five days with no risk. Cash never bound (ended at 40; the 11-cash Boss leads were avoidable with lean and the morgue), so the cash sink promised for the last third did not bite.
- Compared with the selftest: the heuristic predicted about a 0.56 to 0.65 win rate for sensible play, average finish around day 21, losses mostly to turns-out with 3 to 5 mapped or late unrest. The real game won on day 23 with Unrest peaking at 8 on day 15, consistent with the prediction. The selftest did not predict the strength of the migration trick because the heuristic never takes a lead on a node it holds a draft on; a smarter heuristic would probably push the win rate above 0.7, which says the back half needs a counterweight (for example, migrated leads should arrive stale and need a roll, or the morgue should close on Gray).

## Fun rating

7 out of 10. The liar hunt and the day 16 Kessler gambit were real strategy: I was doing arithmetic on days and leads and the systems rewarded it, and watching my benched suspects force the rotation was the kind of trick I play games for. Once Lou was gone and the morgue opened, though, it became a scheduling puzzle I could solve on paper, and the last five days needed something to push back.

## Would replay

Yes. A different liar and a different rotation change the whole opening, and I want to try the other line: race Kessler on Docks for the bonus instead of conceding it, and see whether paying for stringers early beats benching them.