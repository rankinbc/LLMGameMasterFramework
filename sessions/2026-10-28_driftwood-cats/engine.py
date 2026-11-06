"""Driftwood Cats: a retired salvage captain builds the cats' climbing wall of a harbor cafe from salvage.

Each morning the tide brings a Plank or a Shelf and shows tomorrow's. Bolt it to one of the wall's spots; whenever
two pieces of one size sit side by side they join into the next size on the spot nearer the door. Big joins roll to
see if the result is sturdy. Admiral, the ship's cat, picks the tallest piece each morning and climbs that spot at
night, breaking the top off a wobbly piece. A night dive on the wreck makes tomorrow's piece a size bigger; late on,
the old crew can raise the mast once. Win: a sturdy Grand Tree at dusk.

Rulesheet: run `python engine.py rules`.
"""

import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, plural, run  # noqa: E402,F401

NAME = {1: "Plank", 2: "Shelf", 3: "Ladder", 4: "Tower", 5: "Grand Tree"}
NAMES = {1: "Planks", 2: "Shelves", 3: "Ladders", 4: "Towers"}
LETTER = {1: "P", 2: "S", 3: "L", 4: "T", 5: "G"}


def _tallest(g, s):
    return max(s["wall"])


def _pieces(g, s):
    return sum(1 for v in s["wall"] if v)


def _wobbles(g, s):
    return sum(1 for w in s["wobbly"] if w)


class G(Game):
    name = "Driftwood Cats"

    CONSTANTS = {
        "DAYS": 14,
        "SPOTS": 10,
        "DIE": 6,
        "JOIN_NEED": 4,
        "JOIN_WOBBLY": 5,
        "DIVE_CALM": 3,
        "DIVE_ROUGH": 5,
        "CREW_DAY": 11,
        "_TREE": 5,
        "_TOWER": 4,
        "_ROLL_FROM": 3,
        "_DIVE_MAX": 3,
        "_CREW_SIZE": 4,
        "_FIND_DIE": 12,
        "_SHELF_FROM": 11,
        "_P_CALM": 0.5,
        "START_PIECES": 3,
        "_START_MAX": 2,
    }

    RULES = """
1. The cafe wall has {SPOTS|spot}, numbered from the door; {START_PIECES|old piece} are already up. Each morning the tide brings a Plank or a Shelf, and you see tomorrow's. One action a day; unused pieces wash away.
2. Sizes, smallest first: Plank, Shelf, Ladder, Tower, Grand Tree. Bolt today's piece to any spot; a piece already there is thrown out. Pieces never slide along the wall.
3. Whenever two same-size pieces sit side by side, they join into one piece a size bigger on the spot nearer the door; the other empties. This repeats, pair nearest the door first, until none is left.
4. A join that makes a Ladder or bigger rolls a d{DIE}: sturdy on {JOIN_NEED}+, or {JOIN_WOBBLY}+ if a part was wobbly; otherwise it is wobbly (lower case on the wall). Everything else is sturdy.
5. Or brace a wobbly piece with today's piece to make it sturdy. Or dive the wreck tonight: roll {DIVE_CALM}+ in a calm sea or {DIVE_ROUGH}+ in a rough one, and tomorrow's Plank or Shelf comes in a size bigger.
6. Each morning Admiral, the ship's cat, picks the tallest piece (nearest the door if tied). At night he climbs that spot, or naps if it is empty. A wobbly piece under him loses its top: one size down, sturdy.
7. Once, from day {CREW_DAY}, spend the day calling your old crew (today's piece washes away): they raise the wreck's mast, and tomorrow's piece is a Tower. Neither the crew nor a dive works on the last day.
8. Win: a sturdy Grand Tree on the wall at dusk on any day, after Admiral climbs; you call the reviewer in. Lose: no such tree by dusk of day {DAYS}, when the reviewer comes anyway.
"""

    ACTIONS = ["bolt", "brace", "dive", "crew"]
    TAGS = ["join", "chain", "wobbly_join", "night_join", "bolt_over", "brace", "dive_ok", "dive_fail", "rough_dive",
            "admiral_break", "admiral_miss", "crew", "tree", "tree_falls"]
    # the wall is the one board the player manages: what is bolted to each spot and whether it is wobbly
    TRACKED = ["wall"]

    DERIVED = {"tallest": _tallest, "pieces": _pieces, "wobbles": _wobbles}
    BOUNDS = {"today": (1, 4), "next": (1, 4), "admiral": (0, 10), "tallest": (0, 5), "pieces": (0, 10),
              "wobbles": (0, 10)}
    REACH = {"tallest": "_TREE", "today": "_TOWER", "wobbles": 1}
    GATES = {
        "brace": {"_if": lambda g, s: any(s["wobbly"])},
        "dive": {"_if": lambda g, s: s["next"] < g.C["_DIVE_MAX"] and s["_turn"] < g.C["DAYS"]},
        "crew": {"_turn": "CREW_DAY", "!crew_used": 1, "_if": lambda g, s: s["_turn"] < g.C["DAYS"]},
    }

    @property
    def turns(self):
        return self.C["DAYS"]

    # ------------------------------------------------------------ tests

    def rule_tests(self):
        C = self.C
        S = C["SPOTS"]

        def wall(**spots):
            """wall(s3=2, s4=1) -> sizes list with a Shelf at spot 3 and a Plank at spot 4."""
            w = [0] * S
            for k, v in spots.items():
                w[int(k[1:]) - 1] = v
            return w

        def wob(*spots):
            """wob(4) -> the wobbly list with spot 4 wobbly."""
            return [i + 1 in spots for i in range(S)]

        def r1(t):
            s = t.fresh(seed=3)
            t.eq(len(s["wall"]), S, "the wall has SPOTS spots")
            t.eq(len(s["wobbly"]), S, "every spot has a wobbly mark")
            t.ok(s["today"] in (1, 2) and s["next"] in (1, 2), "the tide brings a Plank or a Shelf")
            t.ok("bolt" in t.ids(s), "bolting is always possible")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=2, calm=True, admiral=0)
            t.eq(t.status(s), f"Wall: . . . . . . . . . . | Today: Plank, next Shelf | Tonight: calm sea, Admiral on the counter | Day 1/{C['DAYS']}",
                 "the status line")
            s2, _ = t.step(t.copy(s), "bolt", {"spot": 5})
            t.eq(s2["_turn"], 2, "one action ends the day")
            t.eq(s2["today"], 2, "tomorrow's piece becomes today's")
            t.ok(s2["next"] in (1, 2), "a new piece is drifting in behind it")
            s3, _ = t.step(t.copy(s), "dive")
            t.eq(sum(s3["wall"]), 0, "a piece you do not use washes away; it is not on the wall")
            t.eq(t.label(s, "bolt"), f"Bolt today's Plank to a spot (1 to {S})", "the bolt label counts spots from 1")
            starts = set()
            for i in range(1, 60):
                f = t.fresh(seed=i)
                starts |= {f["today"], f["next"]}
                t.eq(_pieces(self, f), C["START_PIECES"], "the wall starts with START_PIECES old pieces")
                t.ok(not any(f["wobbly"]), "the old pieces start sturdy")
                t.ok(all(not (f["wall"][k] and f["wall"][k] == f["wall"][k + 1]) for k in range(S - 1)),
                     "no two old pieces of one size side by side")
            t.eq(starts, {1, 2}, "the tide brings Planks and Shelves")
            for roll, size in ((C["_SHELF_FROM"] - 1, 1), (C["_SHELF_FROM"], 2), (C["_FIND_DIE"], 2), (1, 1)):
                t.eq(self._find(t.rng(dice=[roll])), size, f"a find roll of {roll}")

        def r2(t):
            s = t.fresh(wall=wall(s4=3), wobbly=wob(), today=1, next=1)
            events = t.apply(s, "bolt", {"spot": 4})
            t.eq(s["wall"][3], 1, "bolting over a spot replaces the piece there")
            t.in_order(events, ["Took down the Ladder at spot 4 and threw it out.", "Bolted today's Plank to spot 4."])
            s = t.fresh(wall=wall(s2=2, s9=3), wobbly=wob(), today=1, next=1, calm=True, admiral=9)
            t.apply(s, "bolt", {"spot": 6})
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["wall"], wall(s2=2, s6=1, s9=3), "bolted pieces stay put overnight")
            t.ok(not t.offered(s, "bolt", spot=0) and not t.offered(s, "bolt", spot=S + 1), "only spots 1 to SPOTS")
            t.ok(t.offered(s, "bolt", spot=1) and t.offered(s, "bolt", spot=S), "spots 1 and SPOTS are both on the wall")
            t.eq([NAME[i] for i in range(1, 6)], ["Plank", "Shelf", "Ladder", "Tower", "Grand Tree"], "sizes, smallest first")

        def r3(t):
            s = t.fresh(wall=wall(s5=1), wobbly=wob(), today=1, next=1)
            events = t.apply(s, "bolt", {"spot": 6}, dice=[1])
            t.eq(s["wall"], wall(s5=2), "two Planks join into a Shelf on the spot nearer the door")
            t.in_order(events, ["Bolted today's Plank to spot 6.", "The two Planks at spots 5 and 6 join into a Shelf at spot 5."])
            s = t.fresh(wall=wall(s7=1), wobbly=wob(), today=1, next=1)
            t.apply(s, "bolt", {"spot": 6})
            t.eq(s["wall"], wall(s6=2), "bolted on the door side, the pair lands on your spot")
            s = t.fresh(wall=wall(s3=2, s5=2), wobbly=wob(), today=2, next=1)
            t.apply(s, "bolt", {"spot": 4}, dice=[6])
            t.eq(s["wall"], wall(s3=3, s5=2), "joins run from the door end; the other Shelf is left over")
            s = t.fresh(wall=wall(s1=2, s3=1), wobbly=wob(), today=1, next=1)
            self._hits.clear()
            events = t.apply(s, "bolt", {"spot": 2}, dice=[6])
            t.ok("chain" in self._hits, "two joins from one bolt is a chain")
            t.eq(s["wall"], wall(s1=3), "a new piece that matches its neighbor joins again")
            t.in_order(events, ["Bolted today's Plank to spot 2.", "The two Planks at spots 2 and 3 join",
                                "The two Shelves at spots 1 and 2 join"])
            t.has(events, "Now a sturdy Ladder at spot 1.")
            s = t.fresh(wall=wall(s5=2, s7=1), wobbly=wob(), today=1, next=1)
            t.apply(s, "bolt", {"spot": 8})
            t.eq(s["wall"], wall(s5=2, s7=2), "the new Shelf at 7 does not reach the Shelf at 5")
            s = t.fresh(wall=wall(s1=3, s3=1), wobbly=wob(), today=1, next=1)
            self._hits.clear()
            t.apply(s, "bolt", {"spot": 2})
            t.eq(s["wall"], wall(s1=3, s2=2), "pieces of different sizes do not join")
            t.ok("chain" not in self._hits, "one join is not a chain")
            s = t.fresh(wall=wall(s3=4), wobbly=wob(), today=4, next=1)
            events = t.apply(s, "bolt", {"spot": 4}, dice=[6])
            t.eq(s["wall"], wall(s3=5), "two Towers make the Grand Tree")
            t.has(events, "Now a sturdy Grand Tree at spot 3.")
            s = t.fresh(wall=wall(s3=2), wobbly=wob(), today=1, next=1)
            t.apply(s, "bolt", {"spot": 5})
            t.eq(s["wall"], wall(s3=2, s5=1), "no join two spots apart")
            s = t.fresh(wall=wall(s3=5, s4=5), wobbly=wob(), today=1, next=1)
            t.apply(s, "bolt", {"spot": 8})
            t.eq(s["wall"], wall(s3=5, s4=5, s8=1), "the Grand Tree is the biggest size; two never join")
            s = t.fresh(wall=wall(s4=4, s5=3), wobbly=wob(4, 5), today=1, next=1, admiral=4)
            events = t.advance(s, turn=2, chances=[0.99], dice=[C["JOIN_WOBBLY"] - 1, 1])
            t.ok(s["wall"] == wall(s4=4) and s["wobbly"][3], "a night join with a wobbly part needs JOIN_WOBBLY")
            t.has(events, f"(need {C['JOIN_WOBBLY']}+)")
            s = t.fresh(wall=wall(s4=3, s5=2), wobbly=wob(4), today=1, next=1, admiral=4)
            self._hits.clear()
            events = t.advance(s, turn=2, chances=[0.99], dice=[6, 1])
            t.eq(s["wall"], wall(s4=3), "a cat's break can make a pair, and it joins at night")
            t.ok(not s["wobbly"][3], "the night join rolled sturdy")
            t.in_order(events, ["broke its top off", "The two Shelves at spots 4 and 5 join"], "the break comes before the join")
            t.ok("night_join" in self._hits, "a night join is noted")

        def r4(t):
            def joined(dice, wobbly=False):
                s = t.fresh(wall=wall(s5=2), wobbly=wob(5) if wobbly else wob(), today=2, next=1)
                ev = t.apply(s, "bolt", {"spot": 6}, dice=dice)
                return s, ev
            s, ev = joined([C["JOIN_NEED"]])
            t.ok(s["wall"][4] == 3 and not s["wobbly"][4], "a join on JOIN_NEED is sturdy")
            t.has(ev, f"The two Shelves at spots 5 and 6 join: roll {C['JOIN_NEED']} (need {C['JOIN_NEED']}+) join success. Now a sturdy Ladder at spot 5.")
            s, ev = joined([C["JOIN_NEED"] - 1])
            t.ok(s["wall"][4] == 3 and s["wobbly"][4], "a join below JOIN_NEED is wobbly")
            t.has(ev, "Now a wobbly Ladder at spot 5.")
            t.ok("Wall: . . . . l . . . . ." in t.status(s), "a wobbly piece shows in lower case")
            t.eq(_wobbles(self, s), 1, "one wobbly piece")
            self._hits.clear()
            s, ev = joined([C["JOIN_WOBBLY"] - 1], wobbly=True)
            t.ok(s["wobbly"][4], "a wobbly part needs JOIN_WOBBLY")
            t.has(ev, f"(need {C['JOIN_WOBBLY']}+)")
            t.ok("wobbly_join" in self._hits, "a wobbly join is noted")
            s, ev = joined([C["JOIN_WOBBLY"]], wobbly=True)
            t.ok(not s["wobbly"][4], "JOIN_WOBBLY with a wobbly part is sturdy")
            s = t.fresh(wall=wall(s5=1), wobbly=wob(), today=1, next=1)
            events = t.apply(s, "bolt", {"spot": 6}, dice=[1])
            t.ok(not s["wobbly"][4], "a Shelf join never rolls and is sturdy")
            t.ok(not any("roll" in e for e in events), "no roll for a Shelf")
            s = t.fresh(wall=wall(s6=3), wobbly=wob(6), today=3, next=1)
            events = t.apply(s, "bolt", {"spot": 5}, dice=[C["JOIN_WOBBLY"] - 1])
            t.ok(s["wall"][4] == 4 and s["wobbly"][4], "a wobbly part on the far side also needs JOIN_WOBBLY")
            t.has(events, f"(need {C['JOIN_WOBBLY']}+)")
            s = t.fresh(wall=wall(s4=3), wobbly=wob(4), today=1, next=1)
            t.apply(s, "bolt", {"spot": 4})
            t.ok(not s["wobbly"][3], "a piece bolted over a wobbly one is new salvage, sturdy")
            s = t.fresh(wall=wall(s1=3, s3=2), wobbly=wob(), today=2, next=1)
            events = t.apply(s, "bolt", {"spot": 2}, dice=[1, C["JOIN_WOBBLY"] - 1])
            t.ok(s["wall"][0] == 4 and s["wobbly"][0], "a part made wobbly earlier in the same chain needs JOIN_WOBBLY")
            t.in_order(events, [f"(need {C['JOIN_NEED']}+)", f"(need {C['JOIN_WOBBLY']}+)"])
            s = t.fresh(wall=wall(s2=1), wobbly=wob(), today=1, next=1)
            t.apply(s, "bolt", {"spot": 8})
            t.ok(not any(s["wobbly"]), "new salvage is sturdy")

        def r5(t):
            s = t.fresh(wall=wall(s2=3), wobbly=wob(), today=1, next=1)
            t.ok(not t.offered(s, "brace", spot=2), "no brace without a wobbly piece")
            s = t.fresh(wall=wall(s2=3), wobbly=wob(2), today=1, next=2)
            t.eq(t.label(s, "brace", spot=2), "Brace the wobbly Ladder at spot 2 with today's Plank", "brace label")
            events = t.apply(s, "brace", {"spot": 2})
            t.ok(not s["wobbly"][1] and s["wall"] == wall(s2=3), "a braced piece is sturdy and today's piece is used")
            t.has(events, "Braced the wobbly Ladder at spot 2 with today's Plank. It is sturdy now.")
            s = t.fresh(wall=wall(s2=3, s6=4), wobbly=wob(2, 6), today=1, next=2)
            t.ok(t.offered(s, "brace", spot=2) and t.offered(s, "brace", spot=6), "each wobbly piece can be braced")
            t.apply(s, "brace", {"spot": 6})
            t.ok(s["wobbly"][1] and not s["wobbly"][5], "a brace fixes only its own piece")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=2, calm=True)
            t.eq(t.label(s, "dive"), f"Dive the wreck tonight: tomorrow's Shelf comes in as a Ladder (need {C['DIVE_CALM']}+, calm sea); today's Plank washes away",
                 "dive label shows the odds")
            events = t.apply(s, "dive", dice=[C["DIVE_CALM"]])
            t.eq(s["next"], 3, "a calm dive on DIVE_CALM makes tomorrow's piece a size bigger")
            t.in_order(events, [f"You leave today's Plank to the tide and dive the wreck in a calm sea: roll {C['DIVE_CALM']} (need {C['DIVE_CALM']}+) dive success.",
                                "You raise a matching Shelf from the wreck. Tomorrow you get a Ladder instead."])
            events = t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.has(events, "Morning: the Ladder you raised from the wreck is on the slipway, with a Plank drifting in behind it.")
            t.eq(s["raised"], "", "the slipway note is used once")
            events = t.advance(s, turn=3, chances=[0.99], dice=[1])
            t.has(events, "Morning: the tide brings a Plank")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=2, calm=True)
            events = t.apply(s, "dive", dice=[C["DIVE_CALM"] - 1])
            t.eq(s["next"], 2, "a failed dive changes nothing tomorrow")
            t.has(events, "You come up empty-handed.")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=2, calm=False)
            t.apply(s, "dive", dice=[C["DIVE_ROUGH"] - 1])
            t.eq(s["next"], 2, "a rough sea needs DIVE_ROUGH")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=2, calm=False)
            t.apply(s, "dive", dice=[C["DIVE_ROUGH"]])
            t.eq(s["next"], 3, "a rough dive on DIVE_ROUGH succeeds")
            for big in (3, 4):
                s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=big, calm=True)
                t.ok(not t.offered(s, "dive"), "no dive when tomorrow's piece is a Ladder or a Tower")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=1, calm=True)
            t.ok(t.offered(s, "dive"), "a dive for a Plank")
            s["_turn"] = C["DAYS"]
            t.ok(not t.offered(s, "dive"), "no dive on the last day")
            s["_turn"] = C["DAYS"] - 1
            t.ok(t.offered(s, "dive"), "a dive the day before the last")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=1, calm=False)
            t.ok("Tonight: rough sea" in t.status(s), "tonight's sea shows")
            got = set()
            for i in range(1, 40):
                f = t.fresh(seed=i)
                t.advance(f, turn=2, seed=i)
                got.add(f["calm"])
            t.eq(got, {True, False}, "the sea can be calm or rough")

        def r6(t):
            s = t.fresh(wall=wall(s4=3, s7=2), wobbly=wob(4), today=1, next=1, admiral=4)
            self._hits.clear()
            events = t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["wall"], wall(s4=2, s7=2), "Admiral breaks the top off the wobbly piece on his spot")
            t.ok(not s["wobbly"][3], "what is left is sturdy")
            t.has(events, "Admiral climbed the wobbly Ladder at spot 4 and broke its top off. It is a sturdy Shelf now.")
            t.ok("admiral_break" in self._hits, "the break is noted")
            s = t.fresh(wall=wall(s4=3, s7=2), wobbly=wob(), today=1, next=1, admiral=4)
            self._hits.clear()
            events = t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["wall"], wall(s4=3, s7=2), "a sturdy piece holds")
            t.ok("admiral_break" not in self._hits, "a held piece is no break")
            t.has(events, "Admiral slept on the Ladder at spot 4. It held.")
            t.ok("Admiral has his eye on the Ladder at spot 4." in events[-1], "his pick for tomorrow shows in the morning")
            t.ok("Admiral at spot 4" in t.status(s), "and in the status line")
            s = t.fresh(wall=wall(s4=3, s7=2), wobbly=wob(4), today=1, next=1, admiral=7)
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.ok(s["wall"][3] == 3 and s["wobbly"][3], "a wobbly piece off his spot is safe tonight")
            t.eq(s["admiral"], 4, "and it is his pick for tomorrow")
            s = t.fresh(wall=wall(s3=3), wobbly=wob(), today=3, next=1, admiral=3)
            t.apply(s, "bolt", {"spot": 4}, dice=[1])
            t.ok(s["wall"][2] == 4 and s["wobbly"][2], "a wobbly Tower lands on his spot today")
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["wall"][2], 3, "he climbs his spot, whatever is there by night")
            s = t.fresh(wall=wall(s2=3, s7=3), wobbly=wob(), today=1, next=1, admiral=0)
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["admiral"], 2, "tied: he picks the one nearest the door")
            s = t.fresh(wall=wall(s2=1, s7=3), wobbly=wob(), today=1, next=1, admiral=0)
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["admiral"], 7, "he picks the tallest")
            s = t.fresh(wall=wall(s2=2, s7=1), wobbly=wob(2), today=1, next=1, admiral=2)
            t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.eq(s["wall"], wall(s2=1, s7=1), "a wobbly Shelf drops to a Plank")
            s = t.fresh(wall=wall(s7=1), wobbly=wob(), today=1, next=1, admiral=5)
            events = t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.has(events, "Admiral found spot 5 empty and napped on the counter.")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=1, admiral=0)
            events = t.advance(s, turn=2, chances=[0.99], dice=[1])
            t.has(events, "Admiral found nothing to climb")
            t.ok("Admiral has nothing to climb." in events[-1], "an empty wall in the morning")
            for i in range(1, 30):
                f = t.fresh(seed=i)
                t.eq(f["admiral"], f["wall"].index(max(f["wall"])) + 1, "on day 1 he has picked the tallest piece")

        def r7(t):
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=1)
            s["_turn"] = C["CREW_DAY"] - 1
            t.ok(not t.offered(s, "crew"), "no crew before CREW_DAY")
            s["_turn"] = C["CREW_DAY"]
            t.ok(t.offered(s, "crew"), "the crew from CREW_DAY")
            s0 = t.copy(s)
            events = t.apply(s, "crew")
            t.eq(s["next"], C["_TOWER"], "tomorrow's piece is a Tower")
            t.has(events, "Your old crew raise the wreck's mast. Tomorrow's piece will be a Tower. Today's Plank washes away.")
            t.eq(t.label(s0, "crew"), "Call your old crew: tomorrow's piece is a Tower (once); today's Plank washes away", "crew label")
            events = t.advance(s, turn=C["CREW_DAY"], chances=[0.99], dice=[1])
            t.has(events, "Morning: your crew's Tower is on the slipway, with a Plank drifting in behind it.")
            t.eq(sum(s["wall"]), 0, "today's piece washes away")
            t.ok(not t.offered(s, "crew"), "once only")
            s = t.fresh(wall=wall(), wobbly=wob(), today=1, next=1)
            s["_turn"] = C["DAYS"]
            t.ok(not t.offered(s, "crew"), "no crew on the last day")
            s["_turn"] = C["DAYS"] - 1
            t.ok(t.offered(s, "crew"), "the crew the day before the last")

        def r8(t):
            s = t.fresh(wall=wall(s3=5), wobbly=wob(), today=1, next=1, admiral=3)
            events = t.advance(s, turn=4, chances=[0.99], dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "a sturdy Grand Tree at dusk wins")
            t.eq(s["_ended"]["reason"], "the Grand Tree at spot 3 stood at dusk on day 4; you called the reviewer in", "win reason")
            t.has(events, "You call the reviewer in.")
            t.in_order(events, ["Admiral slept on the Grand Tree at spot 3", "At dusk the Grand Tree at spot 3 is sturdy and standing"])
            t.ok(not any("Morning" in e for e in events), "no morning after a win")
            s = t.fresh(wall=wall(s3=5), wobbly=wob(3), today=1, next=1, admiral=0)
            t.advance(s, turn=4, chances=[0.99], dice=[1])
            t.ok(not s.get("_ended") and s["wall"][2] == 5, "a wobbly Grand Tree off his spot stands, but does not win")
            t.eq(s["admiral"], 3, "he picks it for tomorrow")
            s = t.fresh(wall=wall(s3=5), wobbly=wob(3), today=1, next=1, admiral=3)
            self._hits.clear()
            t.advance(s, turn=4, chances=[0.99], dice=[1])
            t.ok(not s.get("_ended") and s["wall"][2] == 4, "a wobbly Grand Tree on his spot loses its top")
            t.ok("tree_falls" in self._hits, "the fall of a Grand Tree is noted")
            s = t.fresh(wall=wall(s3=5), wobbly=wob(3), today=1, next=1, admiral=3)
            t.apply(s, "brace", {"spot": 3})
            t.advance(s, turn=4, chances=[0.99], dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "a braced Grand Tree is sturdy and wins at dusk")
            s = t.fresh(wall=wall(s4=5, s5=4), wobbly=wob(4), today=1, next=1, admiral=4)
            events = t.advance(s, turn=4, chances=[0.99], dice=[6])
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "a Tower rejoined at night into a sturdy Grand Tree wins at dusk")
            t.in_order(events, ["broke its top off", "The two Towers at spots 4 and 5 join", "At dusk the Grand Tree at spot 4"])
            s = t.fresh(wall=wall(s2=5, s6=5), wobbly=wob(), today=1, next=1, admiral=2)
            t.advance(s, turn=4, chances=[0.99], dice=[1])
            t.ok("spot 2" in s["_ended"]["reason"], "with two trees, the one nearest the door is named")
            s = t.fresh(wall=wall(s2=3), wobbly=wob(), today=1, next=2, calm=False, admiral=2)
            s["_turn"] = C["DAYS"]
            t.eq(t.status(s), f"Wall: . L . . . . . . . . | Today: Plank, last day | Tonight: the reviewer comes, Admiral at spot 2 | Day {C['DAYS']}/{C['DAYS']}",
                 "the last day's status has no tomorrow")
            s = t.fresh(wall=wall(s3=4), wobbly=wob(), today=4, next=1)
            t.apply(s, "bolt", {"spot": 4}, dice=[6])
            t.ok(not s.get("_ended") and self.check_end(s) is None, "building the Grand Tree is not yet a win; it must stand at dusk")
            s = t.fresh(wall=wall(s3=5), wobbly=wob(), today=1, next=1, admiral=3)
            t.advance(s, turn=C["DAYS"], chances=[0.99], dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "a sturdy Grand Tree at dusk of the last day still wins")
            t.eq(self.turns, C["DAYS"], "the budget is DAYS")
            s = t.fresh(wall=wall(s1=4), wobbly=wob(), today=1, next=1)
            s["_turn"] = C["DAYS"]
            s, _ = t.step(s, "bolt", {"spot": 5})
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss" and s["_turn"] == C["DAYS"] + 1, "no Grand Tree by the last dusk loses")
            t.eq(s["_ended"]["reason"], f"the reviewer came at dusk of day {C['DAYS']} and found no Grand Tree; the tallest piece was a Tower",
                 "loss reason")
            s = t.fresh(wall=wall(s6=5), wobbly=wob(6), today=1, next=1, admiral=0)
            s["_turn"] = C["DAYS"]
            s, _ = t.step(s, "bolt", {"spot": 1})
            t.eq(s["_ended"]["reason"], f"the reviewer came at dusk of day {C['DAYS']}; the Grand Tree at spot 6 was still wobbly",
                 "a wobbly Grand Tree at the end is named as such")
            s = t.fresh(wall=wall(s1=4), wobbly=wob(), today=1, next=1)
            events = t.advance(s, turn=C["DAYS"], chances=[0.99], dice=[1])
            t.ok(not any("Morning" in e for e in events), "no morning after the last dusk")
            events = t.advance(s, turn=C["DAYS"] - 1, chances=[0.99], dice=[1])
            t.has(events, "Morning: the tide brings a Plank. It is the last day: the reviewer comes tonight.", "the last morning")
            t.ok(not any("drifting" in e or "sea" in e for e in events), "no tomorrow and no sea on the last morning")
            events = t.advance(s, turn=C["DAYS"] - 2, chances=[0.99], dice=[1])
            t.has(events, "drifting in behind it", "the morning before that still shows tomorrow")

        return [
            (1, "the wall, the tide, one action", r1), (2, "sizes and bolting", r2), (3, "joins", r3),
            (4, "the join roll", r4), (5, "brace and dive", r5), (6, "Admiral", r6), (7, "the crew", r7),
            (8, "win and loss", r8),
        ]

    # ------------------------------------------------------------ state

    @staticmethod
    def _pick(wall):
        """Admiral's spot for tonight: the tallest piece, nearest the door if tied; 0 for an empty wall."""
        top = max(wall)
        return wall.index(top) + 1 if top else 0

    def _find(self, rng):
        C = self.C
        return 2 if rng.d(C["_FIND_DIE"]) >= C["_SHELF_FROM"] else 1  # lit-ok: a Shelf or a Plank

    def init_state(self, rng):
        C = self.C
        S = C["SPOTS"]
        wall = [0] * S
        spots = list(range(S))
        rng.shuffle(spots)
        for i in sorted(spots[: C["START_PIECES"]]):
            size = rng.d(C["_START_MAX"])
            if i and wall[i - 1] == size:
                size = size % C["_START_MAX"] + 1  # old pieces never match a neighbor: they would have joined
            wall[i] = size
        today = self._find(rng)
        nxt = self._find(rng)
        return {
            "wall": wall,
            "wobbly": [False] * S,
            "admiral": self._pick(wall),
            "today": today,
            "next": nxt,
            "calm": rng.chance(C["_P_CALM"]),
            "crew_used": False,
            "raised": "",
            "hidden": {},
        }

    # ------------------------------------------------------------ options

    def options(self, s):
        C = self.C
        t = NAME[s["today"]]
        last = s["_turn"] >= C["DAYS"]  # no tomorrow: a dive or the crew could not matter
        o = [{"id": "bolt", "label": f"Bolt today's {t} to a spot (1 to {C['SPOTS']})", "args": {},
              "params": {"spot": {"choices": list(range(1, C["SPOTS"] + 1))}}}]
        for i, v in enumerate(s["wall"]):
            if v and s["wobbly"][i]:
                o.append({"id": "brace", "label": f"Brace the wobbly {NAME[v]} at spot {i + 1} with today's {t}",
                          "args": {"spot": i + 1}, "group": "Brace a wobbly piece"})
        if s["next"] < C["_DIVE_MAX"] and not last:
            need = C["DIVE_CALM"] if s["calm"] else C["DIVE_ROUGH"]
            sea = "calm" if s["calm"] else "rough"
            o.append({"id": "dive", "args": {},
                      "label": f"Dive the wreck tonight: tomorrow's {NAME[s['next']]} comes in as a "
                               f"{NAME[s['next'] + 1]} (need {need}+, {sea} sea); today's {t} washes away"})
        if s["_turn"] >= C["CREW_DAY"] and not s["crew_used"] and not last:
            o.append({"id": "crew", "args": {},
                      "label": f"Call your old crew: tomorrow's piece is a {NAME[C['_CREW_SIZE']]} (once); today's {t} washes away"})
        return o

    # ------------------------------------------------------------ joins

    def _settle(self, s, rng, ev):
        """Join every pair of same-size neighbors, from the door end, until none is left. Returns the join count."""
        C = self.C
        w, wb = s["wall"], s["wobbly"]
        joins = 0
        while True:
            k = next((i for i in range(C["SPOTS"] - 1) if w[i] and w[i] == w[i + 1] and w[i] < C["_TREE"]), None)
            if k is None:
                return joins
            old, new = w[k], w[k] + 1
            if new >= C["_ROLL_FROM"]:
                ok, txt = rng.check(C["JOIN_WOBBLY"] if wb[k] or wb[k + 1] else C["JOIN_NEED"], C["DIE"], "join")
                ev.append(f"The two {NAMES[old]} at spots {k + 1} and {k + 2} join: {txt}. "
                          f"Now a {'sturdy' if ok else 'wobbly'} {NAME[new]} at spot {k + 1}.")
            else:
                ok = True
                ev.append(f"The two {NAMES[old]} at spots {k + 1} and {k + 2} join into a {NAME[new]} at spot {k + 1}.")
            w[k], wb[k] = new, not ok
            w[k + 1], wb[k + 1] = 0, False
            joins += 1
            self.hit("join")
            if not ok:
                self.hit("wobbly_join")
            if new == C["_TREE"]:
                self.hit("tree")

    # ------------------------------------------------------------ the player's action

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        t = s["today"]
        if a == "bolt":
            i = args["spot"] - 1
            if s["wall"][i]:
                ev.append(f"Took down the {NAME[s['wall'][i]]} at spot {i + 1} and threw it out.")
                self.hit("bolt_over")
            s["wall"][i] = t
            s["wobbly"][i] = False
            ev.append(f"Bolted today's {NAME[t]} to spot {i + 1}.")
            if self._settle(s, rng, ev) >= 2:
                self.hit("chain")
        elif a == "brace":
            i = args["spot"] - 1
            s["wobbly"][i] = False
            self.hit("brace")
            ev.append(f"Braced the wobbly {NAME[s['wall'][i]]} at spot {i + 1} with today's {NAME[t]}. It is sturdy now.")
        elif a == "dive":
            sea = "calm" if s["calm"] else "rough"
            need = C["DIVE_CALM"] if s["calm"] else C["DIVE_ROUGH"]
            ok, txt = rng.check(need, C["DIE"], "dive")
            ev.append(f"You leave today's {NAME[t]} to the tide and dive the wreck in a {sea} sea: {txt}.")
            if not s["calm"]:
                self.hit("rough_dive")
            if ok:
                ev.append(f"You raise a matching {NAME[s['next']]} from the wreck. Tomorrow you get a {NAME[s['next'] + 1]} instead.")
                s["next"] += 1
                s["raised"] = "dive"
                self.hit("dive_ok")
            else:
                ev.append("You come up empty-handed.")
                self.hit("dive_fail")
        elif a == "crew":
            s["crew_used"] = True
            s["next"] = C["_CREW_SIZE"]
            self.hit("crew")
            s["raised"] = "crew"
            ev.append(f"Your old crew raise the wreck's mast. Tomorrow's piece will be a {NAME[C['_CREW_SIZE']]}. "
                      f"Today's {NAME[t]} washes away.")
        return ev

    # ------------------------------------------------------------ dusk

    def advance(self, s, rng):
        C = self.C
        ev = []
        a = s["admiral"]
        if a and s["wall"][a - 1]:
            i = a - 1
            v = s["wall"][i]
            if s["wobbly"][i]:
                s["wall"][i] = v - 1
                s["wobbly"][i] = False
                self.hit("admiral_break")
                if v == C["_TREE"]:
                    self.hit("tree_falls")
                ev.append(f"Admiral climbed the wobbly {NAME[v]} at spot {a} and broke its top off. "
                          f"It is a sturdy {NAME[v - 1]} now.")
                if self._settle(s, rng, ev):
                    self.hit("night_join")
            else:
                ev.append(f"Admiral slept on the {NAME[v]} at spot {a}. It held.")
        elif a:
            ev.append(f"Admiral found spot {a} empty and napped on the counter.")
            self.hit("admiral_miss")
        else:
            ev.append("Admiral found nothing to climb and napped on the counter.")
        trees = [i for i, v in enumerate(s["wall"]) if v == C["_TREE"] and not s["wobbly"][i]]
        if trees:
            i = trees[0]
            ev.append(f"At dusk the Grand Tree at spot {i + 1} is sturdy and standing. You call the reviewer in.")
            self.finish(s, "win", f"the Grand Tree at spot {i + 1} stood at dusk on day {s['_turn']}; you called the reviewer in")
            return ev
        if s["_turn"] >= C["DAYS"]:
            return ev  # the reviewer comes tonight: no morning
        s["today"] = s["next"]
        s["next"] = self._find(rng)
        s["calm"] = rng.chance(C["_P_CALM"])
        s["admiral"] = self._pick(s["wall"])
        eye = (f"Admiral has his eye on the {NAME[s['wall'][s['admiral'] - 1]]} at spot {s['admiral']}."
               if s["admiral"] else "Admiral has nothing to climb.")
        came = {"dive": f"the {NAME[s['today']]} you raised from the wreck is on the slipway",
                "crew": f"your crew's {NAME[s['today']]} is on the slipway"}.get(s["raised"], f"the tide brings a {NAME[s['today']]}")
        s["raised"] = ""
        if s["_turn"] + 1 >= C["DAYS"]:
            ev.append(f"Morning: {came}. It is the last day: the reviewer comes tonight. {eye}")
        else:
            ev.append(f"Morning: {came}, with a {NAME[s['next']]} drifting in behind it. "
                      f"Tonight's sea: {'calm' if s['calm'] else 'rough'}. {eye}")
        return ev

    # ------------------------------------------------------------ display and end

    def status_line(self, s):
        C = self.C
        wall = " ".join(LETTER[v].lower() if s["wobbly"][i] else LETTER[v] if v else "." for i, v in enumerate(s["wall"]))
        last = s["_turn"] >= C["DAYS"]
        today = f"{NAME[s['today']]}, last day" if last else f"{NAME[s['today']]}, next {NAME[s['next']]}"
        tonight = "the reviewer comes, " if last else f"{'calm' if s['calm'] else 'rough'} sea, "
        tonight += f"Admiral at spot {s['admiral']}" if s["admiral"] else "Admiral on the counter"
        return f"Wall: {wall} | Today: {today} | Tonight: {tonight} | Day {min(s['_turn'], C['DAYS'])}/{C['DAYS']}"

    def check_end(self, s):
        return None

    def final_check(self, s):
        C = self.C
        top = max(s["wall"])
        if top == C["_TREE"]:
            return {"result": "loss", "reason": f"the reviewer came at dusk of day {C['DAYS']}; the Grand Tree at spot "
                                                f"{s['wall'].index(top) + 1} was still wobbly"}
        best = f"a {NAME[top]}" if top else "nothing"
        return {"result": "loss", "reason": f"the reviewer came at dusk of day {C['DAYS']} and found no Grand Tree; "
                                            f"the tallest piece was {best}"}

    # ------------------------------------------------------------ sensible play

    def _settled(self, w):
        """Sizes after every join, assuming each comes out sturdy; and how many joins rolled."""
        C = self.C
        w, rolls = list(w), 0
        while True:
            k = next((i for i in range(len(w) - 1) if w[i] and w[i] == w[i + 1] and w[i] < C["_TREE"]), None)
            if k is None:
                return w, rolls
            rolls += w[k] + 1 >= C["_ROLL_FROM"]
            w[k] += 1
            w[k + 1] = 0

    def _score(self, w):
        sc = sum(4 ** v for v in w if v)  # lit-ok: heuristic weights
        for i in range(len(w) - 1):
            if w[i] and w[i + 1] and abs(w[i] - w[i + 1]) == 1:
                sc += 4 ** min(w[i], w[i + 1]) * 0.3  # lit-ok: a staircase: the next piece of the smaller size joins up
        return sc

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        wall, wob = s["wall"], s["wobbly"]
        t, nx = s["today"], s["next"]
        p = (C["DIE"] - C["JOIN_NEED"] + 1) / C["DIE"]
        base = self._score(wall)
        best_i, best_gain, joined = None, None, False
        for i in range(C["SPOTS"]):
            if wall[i] >= max(t, 2) and wall[i] != t:
                continue  # never throw out a real piece for a smaller one
            w2 = list(wall)
            w2[i] = t
            res, rolls = self._settled(w2)
            gain = self._score(res) * (1 + p ** rolls) / 2 - base  # lit-ok: a wobbly result is braced or lost
            if best_gain is None or gain > best_gain:
                best_i, best_gain, joined = i, gain, max(res) > max(wall)
        for o in options:
            if o["id"] == "brace" and wall[o["args"]["spot"] - 1] == C["_TREE"]:
                return o  # a braced Grand Tree wins at dusk
        ai = s["admiral"] - 1
        if ai >= 0 and 3 <= wall[ai] < C["_TREE"] and wob[ai] and not joined:
            return {"id": "brace", "args": {"spot": ai + 1}}
        for i, v in enumerate(wall):
            if 3 <= v < C["_TREE"] and wob[i] and not joined and max(wall) == v:
                return {"id": "brace", "args": {"spot": i + 1}}
        if "crew" in ids and (C["_TOWER"] in wall or s["_turn"] >= C["DAYS"] - 2) and not joined:
            return "crew"
        if "dive" in ids and not joined and nx == 2 and (s["calm"] or t == 1):
            return "dive"
        if best_i is None:
            best_i = wall.index(min(wall))
        return {"id": "bolt", "args": {"spot": best_i + 1}}


if __name__ == "__main__":
    run(G)
