# Fever Card

Premise: you are the booker for the body's night shift. Each night you book one crew into one of four capillary passes, the Card runs at dusk without you, and you must raise the Granuloma (a Wall of bricks in every pass) before winter freezes the passes and Old Gold's staph colony takes the room.

## Rolls

FORM=15 (Programming) SET=32 (human bloodstream during an infection) ROLE=51 (wrestling booker) LOOP=32 (open, hold or close one position as news lands) CLOCK=8 (winter closes the passes) TWIST=39 (the rules change on a published schedule) WIN=5 (build a specific final structure) MAP=14 (a 4 by 4 board you fill in) TONE=10 (nature documentary) CURRENCY=7 (slots) TRACKED=3

Tracked numbers: Slots (free bays in open passes, the CURRENCY), Germs (total, sepsis limit), Wall (bricks laid out of the goal). The status line also shows Bloom (the colony's announced landing pass).

## Rulesheet (python engine.py rules)

1. The lesion is 4 passes of 4 bays and starts with 5 germs. A bay is free, a brick or a germ. Free bays in open passes are your Slots. Each night you make one move, then dusk runs.
2. A pass holds one booking, and a new one replaces it: Wall crew or Sweep crew. A finished pass takes no booking. Bookings run at dusk, pass 1 first.
3. Wall lays a brick in a free bay, 4 per pass at most, and waits if no bay is free. Sweep kills up to 2 germs.
4. Then Old Gold lands germs, 1 a dusk, in the pass Bloom names, as many as fit. Each landing rolls a d6 first: on 5+ it surges and lands 2 more. That die is Old Gold's own pace.
5. Bloom then moves to the open pass with the most free bays (lowest number on a tie), or to none if none has room, and nothing lands. From night 7 the fever peaks: Old Gold lands 3 a dusk.
6. Winter closes passes: pass 4 freezes after dusk on night 7, pass 3 on 10, pass 2 on 11; pass 1 never does. A frozen pass keeps its contents, runs nothing, takes no germs; its bays leave your Slots.
7. From night 8 Lance a pass instead of booking: its germs die, its booking stays. Once, from night 9, Stoke the fever: coming freezes slip 3 nights, but Old Gold lands 1 more a dusk from then on.
8. Goal: raise the Granuloma, a Wall of 4 bricks in every pass, within 16 nights. Lose if germs reach 11 (sepsis) or a pass freezes short of 4 bricks.

## Signature detail

Old Gold, a named staph colony with a readable habit: it always lands in the open pass with the most free bays, lowest number on a tie, and names that pass one night ahead (Bloom). Published bulletin: passes freeze on nights 7, 10 and 11; the fever peaks on night 7; Lance opens on night 8; Stoke opens on night 9.

## Midpoint plan

Night 7 the fever peaks (colony lands 3 a dusk) and pass 4 freezes; night 8 the Lance unlock (instant germ kill in one pass); night 9 the Stoke lever (freezes slip 3 nights, colony lands 1 more a dusk, a deliberate double-edged panic button).

## Rival policy (one line)

Each dusk, after bookings run, Old Gold rolls a d6 (5+ is a surge of 2 more), lands germs in the Bloom pass as many as fit, then re-names Bloom as the roomiest open pass (lowest number on a tie).

## Opening shape

Pass 1 is the colony's camp on ties and never freezes: the strong opening books a Sweep crew there as a drain while Wall crews start in the freezing passes (4, then 3, then 2).

## Known rough edges (accepted)

- Look-ahead wins about 79 percent against the heuristic's 32 percent: the strong line (Sweep drain in pass 1 from night 2, Wall crews in freeze order, Lance plus Wall last) is learnable, the heuristic does not play it fully.
- Stoke is a deliberate decoy: ablate shows it unmissed, because a good player finishes the freezing passes in time.
- From night 7 the surge die rarely changes a landing (4 bays per pass); it is still shown.
