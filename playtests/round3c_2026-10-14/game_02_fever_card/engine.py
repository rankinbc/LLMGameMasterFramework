"""Fever Card: a standing Card of bookings runs the lesion at dusk (a /play engine).

You book crews into four passes of a 4 by 4 lesion, then watch the Card run without you while Old Gold's
colony presses in and winter closes the passes one by one. Rulesheet: `python engine.py rules`.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

CREW = {"wall": "Wall", "sweep": "Sweep"}


class G(Game):
    name = "Fever Card"

    CONSTANTS = {
        "NIGHTS": 16,
        "PASSES": 4,
        "BAYS": 4,
        "HEIGHT": 4,
        "START_GERMS": 5,
        "SWEEP": 2,
        "LAND": 1,
        "DIE": 6,
        "SURGE": 5,
        "SURGE_GAIN": 2,
        "PEAK_NIGHT": 7,
        "PEAK_LAND": 3,
        "FREEZE_P4": 7,
        "FREEZE_P3": 10,
        "FREEZE_P2": 11,
        "LANCE_NIGHT": 8,
        "STOKE_NIGHT": 9,
        "STOKE_DELAY": 3,
        "STOKE_LAND": 1,
        "SEPSIS": 11,
        "_START_CAP": 3,
        "_LANCE_AT": 3,
        "_DRAIN_FROM": 2,
        "_STOKE_SLACK": 0,
    }

    RULES = """
1. The lesion is {PASSES} passes of {BAYS} bays and starts with {START_GERMS} germs. A bay is free, a brick or a germ. Free bays in open passes are your Slots. Each night you make one move, then dusk runs.
2. A pass holds one booking, and a new one replaces it: Wall crew or Sweep crew. A finished pass takes no booking. Bookings run at dusk, pass 1 first.
3. Wall lays a brick in a free bay, {HEIGHT} per pass at most, and waits if no bay is free. Sweep kills up to {SWEEP} germs.
4. Then Old Gold lands germs, {LAND} a dusk, in the pass Bloom names, as many as fit. Each landing rolls a d{DIE} first: on {SURGE}+ it surges and lands {SURGE_GAIN} more. That die is Old Gold's own pace.
5. Bloom then moves to the open pass with the most free bays (lowest number on a tie), or to none if none has room, and nothing lands. From night {PEAK_NIGHT} the fever peaks: Old Gold lands {PEAK_LAND} a dusk.
6. Winter closes passes: pass 4 freezes after dusk on night {FREEZE_P4}, pass 3 on {FREEZE_P3}, pass 2 on {FREEZE_P2}; pass 1 never does. A frozen pass keeps its contents, runs nothing, takes no germs; its bays leave your Slots.
7. From night {LANCE_NIGHT} Lance a pass instead of booking: its germs die, its booking stays. Once, from night {STOKE_NIGHT}, Stoke the fever: coming freezes slip {STOKE_DELAY} nights, but Old Gold lands {STOKE_LAND} more a dusk from then on.
8. Goal: raise the Granuloma, a Wall of {HEIGHT} bricks in every pass, within {NIGHTS} nights. Lose if germs reach {SEPSIS} (sepsis) or a pass freezes short of {HEIGHT} bricks.
"""

    ACTIONS = ["wall", "sweep", "lance", "stoke", "hold"]
    TAGS = ["lance_open", "peak", "freeze", "finish", "jam", "denied", "surge", "lance", "stoke"]
    TRACKED = ["slots", "germs", "built"]

    BOUNDS = {"slots": (0, 16), "germs": (0, 16), "built": (0, 16), "bloom": (-1, 3)}
    REACH = {"germs": 10, "built": 16}
    GATES = {
        "wall": {"_if": lambda g, s: any(
            not s["frozen"][k] and s["brick"][k] < g.C["HEIGHT"] and s["orders"][k] != "wall"
            for k in range(g.C["PASSES"]))},
        "sweep": {"_if": lambda g, s: any(
            not s["frozen"][k] and s["brick"][k] < g.C["HEIGHT"] and s["orders"][k] != "sweep"
            for k in range(g.C["PASSES"]))},
        "lance": {"night": "LANCE_NIGHT", "_if": lambda g, s: any(
            not s["frozen"][k] and s["germ"][k] > 0 for k in range(g.C["PASSES"]))},
        "stoke": {"night": "STOKE_NIGHT", "!stoked": 1, "_if": lambda g, s: any(
            not s["frozen"][k] for k in g.FREEZE_KEY)},
    }

    DERIVED = {"night": lambda g, s: s["_turn"]}  # the night being played, so GATES can name it

    # pass index -> the constant that names its freeze night (pass 1 never freezes)
    FREEZE_KEY = {1: "FREEZE_P2", 2: "FREEZE_P3", 3: "FREEZE_P4"}
    HORDER = [3, 2, 1, 0]  # the heuristic works the passes in this order

    @property
    def turns(self):
        return self.C["NIGHTS"]

    # ------------------------------------------------------------ helpers

    def _free(self, s, k):
        return self.C["BAYS"] - s["brick"][k] - s["germ"][k]

    def _tally(self, s):
        """Recompute the three tracked numbers from the board, so they can never drift."""
        s["slots"] = sum(self._free(s, k) for k in range(self.C["PASSES"]) if not s["frozen"][k])
        s["germs"] = sum(s["germ"])
        s["built"] = sum(s["brick"])

    def _bloom(self, s):
        """The open pass with the most free bays, lowest number on a tie; -1 if no open pass has a free bay."""
        best, most = -1, 0
        for k in range(self.C["PASSES"]):
            if not s["frozen"][k] and self._free(s, k) > most:
                best, most = k, self._free(s, k)
        return best

    def _landing(self, s, night):
        n = self.C["PEAK_LAND"] if night >= self.C["PEAK_NIGHT"] else self.C["LAND"]
        return n + (self.C["STOKE_LAND"] if s["stoked"] else 0)

    def _freeze_night(self, s, k):
        return self.C[self.FREEZE_KEY[k]] + (self.C["STOKE_DELAY"] if s["stoked"] else 0)

    def _goal(self):
        return self.C["PASSES"] * self.C["HEIGHT"]

    def visible(self, s):
        """What the player may see, counted the way the sheet counts: passes from 1, Bloom as a pass number."""
        board, passes = [], []
        for k in range(self.C["PASSES"]):
            row = "B" * s["brick"][k] + "." * self._free(s, k) + "G" * s["germ"][k]
            note = "frozen" if s["frozen"][k] else (CREW.get(s["orders"][k], "no") + " booking")
            board.append(f"Pass {k + 1}: {row} ({note})")
            last = None if (k not in self.FREEZE_KEY or s["frozen"][k]) else self._freeze_night(s, k)
            passes.append({"pass": k + 1, "bricks": s["brick"][k], "germs": s["germ"][k], "free": self._free(s, k),
                           "booking": CREW.get(s["orders"][k]), "frozen": s["frozen"][k], "last_dusk": last})
        bloom = s["bloom"] + 1 if s["bloom"] >= 0 else None
        return {"slots": s["slots"], "germs": s["germs"], "built": s["built"], "bloom": bloom,
                "stoked": s["stoked"], "passes": passes, "board": board}

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        """One test per rule line, written from the sheet's sentences."""
        C = self.C

        def mk(t, brick=None, germ=None, orders=None, frozen=None, turn=1, stoked=False, bloom=None):
            s = t.fresh(seed=1)
            n = C["PASSES"]
            s["brick"] = list(brick) if brick is not None else [0] * n
            s["germ"] = list(germ) if germ is not None else [0] * n
            s["orders"] = list(orders) if orders is not None else [""] * n
            s["frozen"] = list(frozen) if frozen is not None else [False] * n
            s["stoked"] = stoked
            s["_turn"] = turn
            self._tally(s)
            s["bloom"] = self._bloom(s) if bloom is None else bloom
            return s

        def pk(k):
            return {"pass": k}

        def open_wall():
            """Passes 2 to 4 finished, pass 1 not: a state that is not yet won."""
            return [0] + [C["HEIGHT"]] * (C["PASSES"] - 1)

        def r1(t):
            s = t.fresh(seed=1)
            t.eq(len(s["brick"]), C["PASSES"], "four passes")
            t.eq(s["brick"], [0] * C["PASSES"], "no bricks at the start")
            t.eq(s["germs"], C["START_GERMS"], "the lesion starts with its germs")
            t.eq(sum(s["germ"]), C["START_GERMS"], "the germs sit on the board")
            for sd in range(1, 60):
                g0 = t.fresh(seed=sd)["germ"]
                t.ok(max(g0) <= C["_START_CAP"] and sum(g0) == C["START_GERMS"], "no pass starts crowded, and every germ is placed")
            t.eq(s["slots"], C["PASSES"] * C["BAYS"] - C["START_GERMS"], "free bays are the Slots")
            t.eq((s["built"], s["stoked"], s["orders"], s["frozen"]),
                 (0, False, [""] * C["PASSES"], [False] * C["PASSES"]), "a fresh game starts clean")
            layouts = {tuple(t.fresh(seed=i)["germ"]) for i in range(1, 40)}
            t.ok(len(layouts) > 3, "the starting germs land in different places")
            s = mk(t, brick=[1, 0, 0, 2], germ=[0, 2, 0, 1], frozen=[False, False, False, True])
            t.eq(s["slots"], (C["BAYS"] - 1) + (C["BAYS"] - 2) + C["BAYS"], "a frozen pass's bays leave the Slots")
            t.eq((s["germs"], s["built"]), (3, 3), "frozen bricks and germs still count")
            s = mk(t)
            s["_turn"] = 1
            s2, events = t.step(s, "hold")
            t.eq(s2["_turn"], 2, "one move ends the night")
            t.has(events, "The bookings stand.", "hold wording")
            s = mk(t, brick=[1, 0, 0, 0], germ=[0, 2, 0, 0], turn=1)
            t.eq(t.status(s), f"Slots {C['PASSES'] * C['BAYS'] - 3} | Germs 2/{C['SEPSIS']} | Wall 1/{C['PASSES'] * C['HEIGHT']} | Bloom: P3",
                 "the status line")
            s["bloom"] = -1
            t.eq(t.status(s).split(" | ")[-1], "Bloom: none", "no bloom pass")

        def r2(t):
            s = mk(t)
            events = t.apply(s, "wall", pk(2))
            t.eq(s["orders"], ["", "wall", "", ""], "a booking sits in its own pass")
            t.has(events, "Pass 2: Wall crew booked.", "a booking")
            events = t.apply(s, "sweep", pk(2))
            t.eq(s["orders"], ["", "sweep", "", ""], "a new booking replaces the old one")
            t.has(events, "Pass 2: Sweep crew booked in place of the Wall crew.", "a replaced booking")
            events = t.apply(s, "wall", pk(2))
            t.has(events, "Pass 2: Wall crew booked in place of the Sweep crew.", "a replaced booking, the other way")
            s = mk(t, brick=[1, 0, C["HEIGHT"], 0], germ=[0, 0, 0, 0], orders=["wall", "sweep", "", "wall"])
            t.ok(not t.offered(s, "wall", **pk(1)), "a pass already working a Wall crew is not offered one")
            t.ok(t.offered(s, "wall", **pk(2)), "a Wall crew may replace a Sweep crew")
            t.ok(not t.offered(s, "wall", **pk(3)), "a finished pass takes no more bricks")
            t.ok(not t.offered(s, "sweep", **pk(3)), "a finished pass takes no booking of either kind")
            t.ok(not t.offered(s, "sweep", **pk(2)), "a pass already sweeping is not offered a Sweep")
            t.eq(t.label(s, "wall", **pk(2)), "Book a Wall crew in a pass (lays a brick each dusk)", "wall label")
            t.eq(t.label(s, "sweep", **pk(1)), f"Book a Sweep crew in a pass (kills {plural(C['SWEEP'], 'germ')} each dusk)", "sweep label")
            t.eq(t.label(s, "hold"), "Hold: leave the bookings as they stand", "hold label")
            s = mk(t, orders=["wall", "wall", "", ""], bloom=-1)
            events = t.advance(s, turn=2)
            first = [i for i, e in enumerate(events) if e.startswith("Pass 1:")]
            second = [i for i, e in enumerate(events) if e.startswith("Pass 2:")]
            t.ok(first and second and first[0] < second[0], "pass 1 runs first")
        def r2b(t):
            s = mk(t, brick=[0, 0, 0, 0], orders=["wall", "", "", ""], bloom=-1)
            events = t.advance(s, turn=2)
            t.eq(s["brick"][0], 1, "Wall lays one brick")
            t.eq(s["built"], 1, "the Wall total counts it")
            t.has(events, f"Pass 1: the Wall crew lays a brick (1 of {C['HEIGHT']}).", "a brick")
            s = mk(t, brick=[C["HEIGHT"] - 1, 0, 0, 0], orders=["wall", "", "", ""], bloom=-1)
            events = t.advance(s, turn=2)
            t.eq((s["brick"][0], s["orders"][0]), (C["HEIGHT"], ""), "a finished pass clears its booking")
            t.has(events, f"Pass 1: the Wall crew lays a brick ({C['HEIGHT']} of {C['HEIGHT']}), and the pass is finished.", "the last brick")
            t.ok("finish" in self._hits, "finishing a pass is noted")
            s = mk(t, brick=[1, 0, 0, 0], germ=[C["BAYS"] - 2, 0, 0, 0], orders=["wall", "", "", ""], bloom=-1)
            t.advance(s, turn=2)
            t.eq(s["brick"][0], 2, "exactly one free bay is enough for a brick")
            self._hits.clear()
            s = mk(t, brick=[1, 0, 0, 0], germ=[C["BAYS"] - 1, 0, 0, 0], orders=["wall", "", "", ""], bloom=-1)
            events = t.advance(s, turn=2)
            t.eq(s["brick"][0], 1, "no free bay, no brick")
            t.eq(s["orders"][0], "wall", "a waiting crew stays booked")
            t.has(events, "Pass 1: the Wall crew waits, no free bay.", "a waiting crew")
            t.ok("jam" in self._hits, "a jam is noted")
            s = mk(t, germ=[4, 3, 1, 0], orders=["sweep", "sweep", "sweep", "sweep"], bloom=-1)
            events = t.advance(s, turn=2)
            t.eq(s["germ"], [4 - C["SWEEP"], 3 - C["SWEEP"], 0, 0], "Sweep kills its count, never below zero")
            t.has(events, f"Pass 1: the Sweep crew kills {plural(C['SWEEP'], 'germ')}.", "a sweep")
            t.has(events, "Pass 3: the Sweep crew kills 1 germ.", "a sweep of one germ")
            t.ok(not any(e.startswith("Pass 4:") for e in events), "a sweep of an empty pass says nothing")
            t.eq(s["germs"], sum(s["germ"]), "the germ total follows the sweep")

        def r3(t):
            s = mk(t, germ=[1, 0, 0, 0])
            t.eq(s["bloom"], 1, "Bloom starts at the roomiest pass")
            s = mk(t, germ=[0, 2, 0, 2])
            t.eq(s["bloom"], 0, "the lowest number wins a tie")
            s = mk(t, brick=[0, 0, 0, 0], germ=[3, 3, 2, 3], frozen=[False, False, False, False])
            t.eq(s["bloom"], 2, "the roomiest pass, not the first")
            s = mk(t, germ=[0, 0, 0, 0], frozen=[True, False, False, False])
            t.eq(s["bloom"], 1, "a frozen pass is never the Bloom")
            s = mk(t, brick=[1, 1, 1, 1], germ=[3, 3, 3, 3])
            t.eq(s["bloom"], -1, "no open pass with a free bay: no Bloom")
            s = mk(t, brick=[1, 1, 1, 1], germ=[C["BAYS"] - 2, C["BAYS"] - 2, C["BAYS"] - 1, C["BAYS"] - 1])
            t.eq(s["bloom"], 0, "one free bay is enough to be the Bloom")
            s = mk(t, germ=[0, 0, 0, 0], bloom=2)
            events = t.advance(s, turn=2, dice=[1])
            t.eq(s["germ"], [0, 0, C["LAND"], 0], "the colony lands in the pass Bloom names")
            t.has(events, f"Old Gold lands {plural(C['LAND'], 'germ')} in pass 3.", "a landing")
            t.eq(s["bloom"], 0, "Bloom moves to the roomiest pass after the landing")
            t.has(events, "Old Gold masses at pass 1.", "the new Bloom is announced")
            s = mk(t, germ=[0, 1, 0, 0], bloom=0)
            t.advance(s, turn=2, dice=[1])
            t.eq(s["bloom"], 2, "after landing, Bloom is the roomiest pass, lowest number on a tie")
            s = mk(t, brick=[C["BAYS"] - 1, 0, 0, 0], germ=[0, 0, 0, 0], bloom=0, orders=["", "", "", ""])
            self._hits.clear()
            events = t.advance(s, turn=C["PEAK_NIGHT"], dice=[1])
            t.eq(s["germ"][0], 1, "only as many germs as there are free bays land")
            t.has(events, f"Old Gold lands {plural(1, 'germ')} in pass 1; the rest find no room.", "a partial landing")
            self._hits.clear()
            s = mk(t, brick=[1, 0, 0, 0], germ=[C["BAYS"] - 1, 0, 0, 0], bloom=0)
            events = t.advance(s, turn=2, dice=[1])
            t.eq(s["germ"][0], C["BAYS"] - 1, "a full pass takes nothing")
            t.has(events, "Old Gold finds pass 1 full.", "a full pass")
            t.ok("denied" in self._hits, "a denied landing is noted")
            s = mk(t, brick=[C["BAYS"] - 2, 0, 0, 0], germ=[1, 0, 0, 0], orders=["wall", "", "", ""], bloom=0)
            events = t.advance(s, turn=2, dice=[1])
            t.eq((s["brick"][0], s["germ"][0]), (C["BAYS"] - 1, 1), "bookings run before the colony lands: the last bay is taken")
            t.has(events, "Old Gold finds pass 1 full.", "the Wall crew took the bay first")
            t.ok(not any(e.startswith("roll") for e in events), "no landing, so no die")
            s = mk(t, germ=[C["BAYS"]] * C["PASSES"])
            t.eq(s["bloom"], -1, "setup: no free bay anywhere")
            events = t.advance(s, turn=2)
            t.has(events, "Old Gold finds no room to mass.", "no pass to mass in")
            t.ok(not any(e.startswith(("roll", "Old Gold lands")) for e in events), "nothing lands with no Bloom, and no die is rolled")
            s = mk(t, bloom=-1)
            t.advance(s, turn=2)
            t.eq(s["germs"], 0, "nothing lands with no Bloom")
            t.eq(s["bloom"], 0, "Bloom is named again at dusk")

        def r4(t):
            s = mk(t, bloom=1)
            events = t.advance(s, turn=2, dice=[C["SURGE"]])
            t.eq(s["germ"][1], C["LAND"] + C["SURGE_GAIN"], "a surge lands its extra germs")
            t.has(events, f"roll {C['SURGE']} (need {C['SURGE']}+) surge.", "a surge is shown")
            t.ok("surge" in self._hits, "a surge is noted")
            self._hits.clear()
            s = mk(t, bloom=1)
            events = t.advance(s, turn=2, dice=[C["SURGE"] - 1])
            t.eq(s["germ"][1], C["LAND"], "one below the surge number is no surge")
            t.has(events, f"roll {C['SURGE'] - 1} (need {C['SURGE']}+) no surge.", "no surge is shown")
            t.ok("surge" not in self._hits, "no surge, no note")
            s = mk(t, bloom=1)
            t.advance(s, turn=C["PEAK_NIGHT"] - 1, dice=[1])
            t.eq(s["germ"][1], C["LAND"], "before the peak the colony lands its base count")
            s = mk(t, bloom=1)
            t.advance(s, turn=C["PEAK_NIGHT"], dice=[1])
            t.eq(s["germ"][1], C["PEAK_LAND"], "from the peak night it lands the peak count")
            s = mk(t, bloom=1)
            t.advance(s, turn=C["PEAK_NIGHT"], dice=[C["SURGE"]])
            t.eq(s["germ"][1], min(C["BAYS"], C["PEAK_LAND"] + C["SURGE_GAIN"]), "the surge comes on top of the peak")
            s = mk(t, bloom=1)
            events = t.advance(s, turn=C["PEAK_NIGHT"] - 1, dice=[1])
            t.has(events, f"Night {C['PEAK_NIGHT']}: the fever peaks. Old Gold lands {plural(C['PEAK_LAND'], 'germ')} at every dusk.", "the peak is announced")
            t.ok("peak" in self._hits, "the peak is noted")
            self._hits.clear()
            s = mk(t, bloom=1)
            events = t.advance(s, turn=C["PEAK_NIGHT"] - 2, dice=[1])
            t.ok(not any("fever peaks" in e for e in events), "no peak announcement two nights ahead")
            t.ok("peak" not in self._hits, "no peak yet")
            s = mk(t, bloom=1)
            events = t.advance(s, turn=C["PEAK_NIGHT"], dice=[1])
            t.ok(not any("fever peaks" in e for e in events), "the peak is announced once")
            hits = 0
            for sd in range(1, 301):
                s = mk(t, bloom=1)
                t.advance(s, turn=2, seed=sd)
                hits += s["germ"][1] == C["LAND"] + C["SURGE_GAIN"]
            want = (C["DIE"] - C["SURGE"] + 1) / C["DIE"]
            t.ok(abs(hits / 300 - want) < 0.08, f"a surge should come about {want:.0%} of the time, got {hits / 300:.0%}")

        def r5(t):
            n = C["PASSES"]
            for k, key in ((3, "FREEZE_P4"), (2, "FREEZE_P3"), (1, "FREEZE_P2")):
                night = C[key]
                gone = [False] * (k + 1) + [True] * (n - k - 1)
                s = mk(t, brick=open_wall(), frozen=gone, bloom=-1)
                self._hits.clear()
                t.advance(s, turn=night - 1)
                t.ok(not s["frozen"][k], f"pass {k + 1} is open the night before it freezes")
                t.ok("freeze" not in self._hits, "no freeze yet")
                events = t.advance(s, turn=night)
                t.ok(s["frozen"][k], f"pass {k + 1} freezes after dusk on its night")
                t.has(events, f"Winter closes pass {k + 1} at {plural(C['HEIGHT'], 'brick')} of {C['HEIGHT']}.", "a freeze")
                t.ok("freeze" in self._hits, "a freeze is noted")
            s = mk(t, brick=open_wall(), frozen=[False, True, True, True], bloom=-1)
            t.advance(s, turn=C["NIGHTS"])
            t.ok(not s["frozen"][0], "pass 1 never freezes")
            s = mk(t, brick=open_wall(), bloom=-1)
            t.advance(s, turn=C["FREEZE_P4"])
            t.eq(s["frozen"], [False, False, False, True], "only pass 4 freezes on its night")
            s = mk(t, brick=[0, 0, 0, C["HEIGHT"] - 1], orders=["", "", "", "wall"], bloom=-1)
            t.advance(s, turn=C["FREEZE_P4"])
            t.eq(s["brick"][3], C["HEIGHT"], "a pass still runs on the dusk it freezes")
            t.eq(s["orders"][3], "", "a frozen pass keeps no booking")
            s = mk(t, brick=[0, 0, 0, C["HEIGHT"] - 2], orders=["", "", "", "wall"], bloom=-1)
            t.advance(s, turn=C["FREEZE_P4"])
            t.eq((s["brick"][3], s["frozen"][3]), (C["HEIGHT"] - 1, True), "a short pass freezes short")
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "a short pass freezing is a loss")
            s = mk(t, brick=[0, 0, 0, 1], frozen=[False, False, False, True], bloom=-1)
            t.eq(s["slots"], 3 * C["BAYS"], "frozen bays leave the Slots")
            s = mk(t, germ=[1, 1, 1, 0], frozen=[False, False, False, True])
            t.eq(s["bloom"], 0, "the colony never names a frozen pass, even the roomiest")
            for aid in ("wall", "sweep"):
                t.ok(not t.offered(s, aid, **pk(4)), f"no {aid} booking in a frozen pass")
            s = mk(t, germ=[0, 0, 0, 2], frozen=[False, False, False, True], orders=["", "", "", "sweep"], bloom=-1, turn=C["LANCE_NIGHT"])
            t.advance(s, turn=C["LANCE_NIGHT"])
            t.eq(s["germ"][3], 2, "a frozen pass runs no Sweep crew")
            t.ok(not t.offered(s, "lance", **pk(4)), "no Lance into a frozen pass")
            s = mk(t, brick=[0, 0, 0, 1], orders=["", "", "", "wall"], bloom=-1)
            events = t.advance(s, turn=C["FREEZE_P4"] - 1)
            t.has(events, f"Winter nears pass 4: night {C['FREEZE_P4']} is its last dusk, at 2 bricks of {C['HEIGHT']}.", "the warning")
            s = mk(t, brick=[0, 0, 0, C["HEIGHT"]], bloom=-1)
            events = t.advance(s, turn=C["FREEZE_P4"] - 1)
            t.ok(not any("Winter nears" in e for e in events), "no warning for a finished pass")
            s = mk(t, brick=[0, 0, 0, 0], bloom=-1)
            events = t.advance(s, turn=C["FREEZE_P4"] - 2)
            t.ok(not any("Winter nears" in e for e in events), "no warning two nights ahead")
            s = mk(t, brick=[0, 0, 0, 0], bloom=-1)
            events = t.advance(s, turn=C["FREEZE_P4"])
            t.has(events, f"Winter closes pass 4 at {plural(0, 'brick')} of {C['HEIGHT']}.", "a freeze with no bricks")
            s = mk(t, brick=[1, 0, 2, 0], germ=[0, 1, 0, 0], orders=["wall", "", "sweep", ""], frozen=[False, False, False, True], bloom=1)
            v = self.visible(s)
            t.eq(v["bloom"], 2, "the narrator sees Bloom as a pass number")
            t.eq([p["pass"] for p in v["passes"]], [1, 2, 3, 4], "passes are counted from 1")
            t.eq(v["passes"][0]["booking"], "Wall", "the booking is named")
            t.eq(v["passes"][1]["booking"], None, "no booking")
            t.eq([p["last_dusk"] for p in v["passes"]], [None, C["FREEZE_P2"], C["FREEZE_P3"], None], "the last dusk of each pass that can still freeze")
            t.eq(v["passes"][3]["frozen"], True, "a frozen pass is shown frozen")
            s["bloom"] = -1
            t.eq(self.visible(s)["bloom"], None, "no Bloom is shown as none")
            s["stoked"] = True
            t.eq(self.visible(s)["passes"][1]["last_dusk"], C["FREEZE_P2"] + C["STOKE_DELAY"], "a Stoke moves the last dusk")

        def r6(t):
            s = mk(t, germ=[0, 3, 0, 0], turn=C["LANCE_NIGHT"] - 1)
            t.ok(not t.offered(s, "lance", **pk(2)), "no Lance before its night")
            s = mk(t, germ=[0, 3, 0, 0], turn=C["LANCE_NIGHT"])
            t.ok(t.offered(s, "lance", **pk(2)), "Lance opens on its night")
            t.ok(not t.offered(s, "lance", **pk(1)), "no Lance into a pass without germs")
            t.eq(t.label(s, "lance", **pk(2)), "Lance a pass (every germ in it dies at once)", "lance label")
            s["orders"][1] = "sweep"
            slots0 = s["slots"]
            events = t.apply(s, "lance", pk(2))
            t.eq(s["germ"], [0, 0, 0, 0], "every germ in the pass dies")
            t.eq(s["slots"], slots0 + 3, "the freed bays are Slots again")
            t.eq(s["germs"], 0, "the germ total follows the Lance")
            t.eq(s["orders"][1], "sweep", "a Lance leaves the booking alone")
            t.has(events, "Pass 2: the lance drains 3 germs.", "a Lance")
            t.ok("lance" in self._hits, "a Lance is noted")
            s = mk(t, brick=[0, C["HEIGHT"], C["HEIGHT"], C["HEIGHT"]], germ=[1, 0, 0, 0], frozen=[False, True, True, True], turn=C["LANCE_NIGHT"])
            s2, events = t.step(s, "lance", pk(1))
            t.has(events, "Pass 1: the lance drains 1 germ.", "a Lance of one germ")
            t.eq(s2["_turn"], C["LANCE_NIGHT"] + 1, "a Lance is the night's move, then dusk runs")
            self._hits.clear()
            s = mk(t, bloom=1)
            events = t.advance(s, turn=C["LANCE_NIGHT"] - 1, dice=[1])
            t.has(events, f"Night {C['LANCE_NIGHT']}: you may now Lance a pass.", "the unlock is announced")
            t.ok("lance_open" in self._hits, "the unlock is noted")
            self._hits.clear()
            s = mk(t, bloom=1)
            events = t.advance(s, turn=C["LANCE_NIGHT"], dice=[1])
            t.ok(not any("opens the Lance" in e for e in events), "the unlock is announced once")
            t.ok("lance_open" not in self._hits, "no second unlock")

        def r7(t):
            s = mk(t, turn=C["STOKE_NIGHT"] - 1)
            t.ok(not t.offered(s, "stoke"), "no Stoke before its night")
            s = mk(t, turn=C["STOKE_NIGHT"])
            t.ok(t.offered(s, "stoke"), "Stoke opens on its night")
            t.eq(t.label(s, "stoke"), f"Stoke the fever, once (freezes slip {plural(C['STOKE_DELAY'], 'night')}, Old Gold lands {plural(C['STOKE_LAND'], 'more germ')} at every dusk)", "stoke label")
            events = t.apply(s, "stoke")
            t.ok(s["stoked"], "the fever is stoked")
            t.ok("stoke" in self._hits, "a Stoke is noted")
            t.has(events, f"You stoke the fever. Winter slips {plural(C['STOKE_DELAY'], 'night')}.", "a Stoke")
            t.ok(not t.offered(s, "stoke"), "once only")
            s = mk(t, turn=C["STOKE_NIGHT"], frozen=[False, True, True, True])
            t.ok(not t.offered(s, "stoke"), "no Stoke when every freeze has come")
            s = mk(t, turn=C["STOKE_NIGHT"], frozen=[False, False, True, True])
            t.ok(t.offered(s, "stoke"), "a Stoke is worth offering while a freeze is still to come")
            s = mk(t, brick=open_wall(), stoked=True, bloom=-1)
            t.advance(s, turn=C["FREEZE_P4"])
            t.ok(not s["frozen"][3], "a Stoke pushes pass 4's freeze back")
            t.advance(s, turn=C["FREEZE_P4"] + C["STOKE_DELAY"] - 1)
            t.ok(not s["frozen"][3], "pass 4 stays open until its new night")
            t.advance(s, turn=C["FREEZE_P4"] + C["STOKE_DELAY"])
            t.ok(s["frozen"][3], "pass 4 freezes on its new night")
            s = mk(t, brick=open_wall(), stoked=True, frozen=[False, False, True, True], bloom=-1)
            t.advance(s, turn=C["FREEZE_P2"] + C["STOKE_DELAY"] - 1)
            t.ok(not s["frozen"][1], "pass 2 is pushed back too")
            t.advance(s, turn=C["FREEZE_P2"] + C["STOKE_DELAY"])
            t.ok(s["frozen"][1], "pass 2 freezes on its new night")
            s = mk(t, brick=open_wall(), stoked=True, frozen=[False, False, False, True], bloom=-1)
            t.advance(s, turn=C["FREEZE_P3"] + C["STOKE_DELAY"] - 1)
            t.ok(not s["frozen"][2], "pass 3 is pushed back too")
            t.advance(s, turn=C["FREEZE_P3"] + C["STOKE_DELAY"])
            t.ok(s["frozen"][2], "pass 3 freezes on its new night")
            s = mk(t, brick=[0, 0, 0, 0], stoked=True, bloom=-1)
            events = t.advance(s, turn=C["FREEZE_P4"] + C["STOKE_DELAY"] - 1)
            t.has(events, "Winter nears pass 4", "the warning moves with the freeze")
            s = mk(t, stoked=True, bloom=1)
            t.advance(s, turn=2, dice=[1])
            t.eq(s["germ"][1], C["LAND"] + C["STOKE_LAND"], "a stoked fever lands more at every dusk")
            s = mk(t, stoked=True, bloom=1)
            t.advance(s, turn=C["PEAK_NIGHT"], dice=[1])
            t.eq(s["germ"][1], min(C["BAYS"], C["PEAK_LAND"] + C["STOKE_LAND"]), "the Stoke adds to the peak")
            s = mk(t, stoked=True, bloom=1)
            events = t.advance(s, turn=C["PEAK_NIGHT"] - 1, dice=[1])
            t.has(events, f"Old Gold lands {plural(C['PEAK_LAND'] + C['STOKE_LAND'], 'germ')} at every dusk.", "the peak announcement counts the Stoke")

        def r8(t):
            s = mk(t, brick=[C["HEIGHT"]] * C["PASSES"])
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "the Wall in every pass wins")
            t.eq(end["reason"], f"the Granuloma closes, {plural(C['HEIGHT'], 'brick')} in every pass", "win wording")
            s = mk(t, brick=[C["HEIGHT"]] * (C["PASSES"] - 1) + [C["HEIGHT"] - 1])
            t.eq(self.check_end(s), None, "one brick short is not a win")
            def spread(count):
                return [min(C["BAYS"], max(0, count - k * C["BAYS"])) for k in range(C["PASSES"])]

            s = mk(t, brick=[0, 0, 0, 0], germ=spread(C["SEPSIS"]), bloom=-1)
            t.eq(s["germs"], C["SEPSIS"], "setup: exactly the sepsis count")
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "sepsis loses at the stated count")
            t.eq(end["reason"], f"sepsis, {C['SEPSIS']} germs in the lesion", "sepsis wording")
            s = mk(t, brick=[0, 0, 0, 0], germ=spread(C["SEPSIS"] - 1), bloom=-1)
            t.eq(self.check_end(s), None, "one germ under the sepsis count lives")
            s = mk(t, brick=[1, 0, 0, 0], frozen=[False, False, False, True])
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "a pass frozen short loses")
            t.eq(end["reason"], f"winter closed pass 4 at {plural(0, 'brick')} of {C['HEIGHT']}", "freeze loss wording")
            s = mk(t, brick=[0, 0, C["HEIGHT"] - 1, C["HEIGHT"]], frozen=[False, False, True, True])
            end = self.check_end(s)
            t.eq(end["reason"], f"winter closed pass 3 at {plural(C['HEIGHT'] - 1, 'brick')} of {C['HEIGHT']}", "the short pass is named")
            s = mk(t, brick=[0, C["HEIGHT"], C["HEIGHT"], C["HEIGHT"]], frozen=[False, True, True, True])
            t.eq(self.check_end(s), None, "frozen passes that are finished are fine")
            t.eq(self.turns, C["NIGHTS"], "the budget is NIGHTS")
            s = mk(t, brick=[1, 1, 1, 1], turn=C["NIGHTS"])
            t.eq(self.check_end(s), None, "the last night is still played")
            end = self.final_check(s)
            t.ok(end["result"] == "loss", "short of the Wall after the last night is a loss")
            t.eq(end["reason"], f"the {plural(C['NIGHTS'], 'night')} ran out with 4 of {C['PASSES'] * C['HEIGHT']} bricks laid", "budget wording")
            s = mk(t, brick=[C["HEIGHT"], C["HEIGHT"], C["HEIGHT"], C["HEIGHT"] - 1], orders=["", "", "", "wall"], turn=C["NIGHTS"], bloom=-1)
            s2, events = t.step(s, "hold")
            t.ok(s2["_ended"] and s2["_ended"]["result"] == "win" and s2["_ended"]["phase"] == "dusk", "the last brick wins at dusk")
            t.ok(not any(e.startswith(("roll", "Old Gold", "Winter")) for e in events), "nothing happens after the winning brick")
            s = mk(t, brick=[1, C["HEIGHT"], C["HEIGHT"], C["HEIGHT"]], frozen=[False, True, True, True], turn=C["NIGHTS"], bloom=-1)
            s2, events = t.step(s, "hold")
            t.ok(s2["_ended"] and s2["_ended"]["phase"] == "budget" and s2["_turn"] == C["NIGHTS"] + 1, "the budget ends the game after the last night's dusk")
            t.eq(s2["_ended"]["result"], "loss", "the unfinished Wall loses at the budget")

        def r67(t):
            r6(t)
            r7(t)

        return [
            (1, "the lesion and the move", r1), (2, "bookings and their order", r2), (3, "the two crews", r2b),
            (4, "the landing, Bloom and the die", r3), (5, "Bloom's move, the surge and the peak", r4), (6, "winter", r5),
            (7, "the Lance and the Stoke", r67), (8, "goal and losses", r8),
        ]

    # ------------------------------------------------------------ play

    def init_state(self, rng):
        C = self.C
        n = C["PASSES"]
        s = {"brick": [0] * n, "germ": [0] * n, "orders": [""] * n, "frozen": [False] * n, "stoked": False}
        for _ in range(C["START_GERMS"]):
            open_passes = [k for k in range(n) if s["germ"][k] < C["_START_CAP"]]
            s["germ"][rng.choice(open_passes)] += 1
        self._tally(s)
        s["bloom"] = self._bloom(s)
        return s

    def options(self, s):
        C = self.C
        live = [k for k in range(C["PASSES"]) if not s["frozen"][k]]
        o = []
        walls = [k + 1 for k in live if s["brick"][k] < C["HEIGHT"] and s["orders"][k] != "wall"]
        if walls:
            o.append({"id": "wall", "label": "Book a Wall crew in a pass (lays a brick each dusk)", "args": {},
                      "params": {"pass": {"choices": walls}}})
        sweeps = [k + 1 for k in live if s["brick"][k] < C["HEIGHT"] and s["orders"][k] != "sweep"]
        if sweeps:
            o.append({"id": "sweep", "label": f"Book a Sweep crew in a pass (kills {plural(C['SWEEP'], 'germ')} each dusk)",
                      "args": {}, "params": {"pass": {"choices": sweeps}}})
        if s["_turn"] >= C["LANCE_NIGHT"]:
            lances = [k + 1 for k in live if s["germ"][k] > 0]
            if lances:
                o.append({"id": "lance", "label": "Lance a pass (every germ in it dies at once)", "args": {},
                          "params": {"pass": {"choices": lances}}})
        if s["_turn"] >= C["STOKE_NIGHT"] and not s["stoked"] and any(not s["frozen"][k] for k in self.FREEZE_KEY):
            o.append({"id": "stoke", "label": (
                f"Stoke the fever, once (freezes slip {plural(C['STOKE_DELAY'], 'night')}, "
                f"Old Gold lands {plural(C['STOKE_LAND'], 'more germ')} at every dusk)"), "args": {}})
        o.append({"id": "hold", "label": "Hold: leave the bookings as they stand", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a in CREW:
            k = args["pass"] - 1
            old = s["orders"][k]
            s["orders"][k] = a
            if old:
                ev.append(f"Pass {k + 1}: {CREW[a]} crew booked in place of the {CREW[old]} crew.")
            else:
                ev.append(f"Pass {k + 1}: {CREW[a]} crew booked.")
        elif a == "lance":
            k = args["pass"] - 1
            n = s["germ"][k]
            s["germ"][k] = 0
            self.hit("lance")
            ev.append(f"Pass {k + 1}: the lance drains {plural(n, 'germ')}.")
        elif a == "stoke":
            s["stoked"] = True
            self.hit("stoke")
            ev.append(f"You stoke the fever. Winter slips {plural(C['STOKE_DELAY'], 'night')}.")
        else:
            ev.append("The bookings stand.")
        self._tally(s)
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        t = s["_turn"]
        # bookings run, pass 1 first
        for k in range(C["PASSES"]):
            if s["frozen"][k]:
                continue
            crew = s["orders"][k]
            if crew == "wall":
                if self._free(s, k) > 0:
                    s["brick"][k] += 1
                    done = s["brick"][k] >= C["HEIGHT"]
                    tail = ", and the pass is finished" if done else ""
                    ev.append(f"Pass {k + 1}: the Wall crew lays a brick ({s['brick'][k]} of {C['HEIGHT']}){tail}.")
                    if done:
                        s["orders"][k] = ""
                        self.hit("finish")
                else:
                    self.hit("jam")
                    ev.append(f"Pass {k + 1}: the Wall crew waits, no free bay.")
            elif crew == "sweep":
                killed = min(C["SWEEP"], s["germ"][k])
                if killed > 0:
                    s["germ"][k] -= killed
                    ev.append(f"Pass {k + 1}: the Sweep crew kills {plural(killed, 'germ')}.")
        self._tally(s)
        if s["built"] >= self._goal():
            return ev  # the Granuloma is closed: nothing else happens tonight
        # the colony lands where Bloom said
        b = s["bloom"]
        if b >= 0 and self._free(s, b) <= 0:
            self.hit("denied")
            ev.append(f"Old Gold finds pass {b + 1} full.")
        elif b >= 0:
            roll = rng.d(C["DIE"])
            surge = roll >= C["SURGE"]
            if surge:
                self.hit("surge")
            ev.append(f"roll {roll} (need {C['SURGE']}+) {'surge' if surge else 'no surge'}.")
            want = self._landing(s, t) + (C["SURGE_GAIN"] if surge else 0)
            placed = min(want, self._free(s, b))
            s["germ"][b] += placed
            rest = "; the rest find no room" if placed < want else ""
            ev.append(f"Old Gold lands {plural(placed, 'germ')} in pass {b + 1}{rest}.")
        # winter
        for k in sorted(self.FREEZE_KEY):
            if s["frozen"][k]:
                continue
            night = self._freeze_night(s, k)
            if t >= night:
                s["frozen"][k] = True
                s["orders"][k] = ""
                self.hit("freeze")
                ev.append(f"Winter closes pass {k + 1} at {plural(s['brick'][k], 'brick')} of {C['HEIGHT']}.")
            elif t + 1 == night and s["brick"][k] < C["HEIGHT"]:
                ev.append(f"Winter nears pass {k + 1}: night {night} is its last dusk, at {plural(s['brick'][k], 'brick')} of {C['HEIGHT']}.")
        # the published bulletin for tomorrow
        if t + 1 == C["LANCE_NIGHT"]:
            self.hit("lance_open")
            ev.append(f"Night {t + 1}: you may now Lance a pass.")
        if t + 1 == C["PEAK_NIGHT"]:
            self.hit("peak")
            ev.append(f"Night {C['PEAK_NIGHT']}: the fever peaks. Old Gold lands {plural(self._landing(s, C['PEAK_NIGHT']), 'germ')} at every dusk.")
        self._tally(s)
        s["bloom"] = self._bloom(s)
        if s["bloom"] >= 0:
            ev.append(f"Old Gold masses at pass {s['bloom'] + 1}.")
        else:
            ev.append("Old Gold finds no room to mass.")
        return ev

    def status_line(self, s):
        bloom = f"P{s['bloom'] + 1}" if s["bloom"] >= 0 else "none"
        return f"Slots {s['slots']} | Germs {s['germs']}/{self.C['SEPSIS']} | Wall {s['built']}/{self._goal()} | Bloom: {bloom}"

    def check_end(self, s):
        C = self.C
        if s["built"] >= self._goal():
            return {"result": "win", "reason": f"the Granuloma closes, {plural(C['HEIGHT'], 'brick')} in every pass"}
        for k in range(C["PASSES"]):
            if s["frozen"][k] and s["brick"][k] < C["HEIGHT"]:
                return {"result": "loss", "reason": f"winter closed pass {k + 1} at {plural(s['brick'][k], 'brick')} of {C['HEIGHT']}"}
        if s["germs"] >= C["SEPSIS"]:
            return {"result": "loss", "reason": f"sepsis, {plural(s['germs'], 'germ')} in the lesion"}
        return None

    def final_check(self, s):
        return {"result": "loss", "reason": f"the {plural(self.C['NIGHTS'], 'night')} ran out with {s['built']} of {self._goal()} bricks laid"}

    def heuristic(self, s, options, rng):
        C = self.C
        H, t = C["HEIGHT"], s["_turn"]
        legal = {o["id"]: set(o["params"]["pass"]["choices"]) for o in options if o.get("params")}

        def can(aid, k):
            return k + 1 in legal.get(aid, ())

        def pick(aid, k):
            return {"id": aid, "args": {"pass": k + 1}}

        order = list(self.HORDER)  # the passes that freeze soonest come first
        if any(o["id"] == "stoke" for o in options):
            for k in order:
                if k not in self.FREEZE_KEY or s["frozen"][k] or s["brick"][k] >= H:
                    continue
                left = self._freeze_night(s, k) - t + 1
                need = H - s["brick"][k]
                ready = s["orders"][k] == "wall" and self._free(s, k) >= need
                if need + (0 if ready else 1) + C["_STOKE_SLACK"] > left:
                    return "stoke"
        # pass 1 never freezes and the colony camps there on ties: keep a Sweep crew in it as a drain
        # until the passes that freeze are done
        others = sum(1 for k in self.FREEZE_KEY if s["frozen"][k] or s["brick"][k] >= H)
        drain = t >= C["_DRAIN_FROM"] and others < len(self.FREEZE_KEY) and s["brick"][0] < H
        if drain and s["orders"][0] != "sweep" and can("sweep", 0):
            return pick("sweep", 0)
        todo = [k for k in order if not s["frozen"][k] and s["brick"][k] < H and not (drain and k == 0)]
        for k in todo:  # a crew that waits for room: clear the pass
            if s["orders"][k] == "wall" and self._free(s, k) == 0:
                if can("lance", k):
                    return pick("lance", k)
                if can("sweep", k):
                    return pick("sweep", k)
        for k in todo:  # production first: a crew wherever a bay is free
            if s["orders"][k] != "wall" and self._free(s, k) > 0 and can("wall", k):
                return pick("wall", k)
        for k in todo:  # then clear the packed passes
            if s["orders"][k] != "wall" and s["germ"][k] > 0:
                if can("lance", k) and s["germ"][k] >= C["_LANCE_AT"]:
                    return pick("lance", k)
                if can("sweep", k):
                    return pick("sweep", k)
        return "hold"


if __name__ == "__main__":
    run(G)
