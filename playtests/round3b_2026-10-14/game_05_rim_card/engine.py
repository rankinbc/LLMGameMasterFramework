"""Rim Card: a wrestling booker runs a touring card through eight asteroid-belt outposts while Vesper
Broadcasting's number climbs away and Vesper's crews raid the longest-running shows. Noir.
Two tracked things: cash, and the ring of outposts (Rating is the ring's score and also pays the gate).

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

KINDS = ["scrap", "tag", "belt"]
NAME = {"scrap": "Scrap", "tag": "Tag", "belt": "Belt"}
CH = {"scrap": "S", "tag": "T", "belt": "B"}
OUTPOSTS = ["Ceres Dock", "Pallas Pit", "Vesta Yard", "Hygiea Hole", "Juno Camp", "Iris Spur", "Flora Heap", "Psyche Rig"]


class G(Game):
    name = "Rim Card"

    CONSTANTS = {
        "NIGHTS": 20,
        "RING": 8,
        "MID": 11,
        "CP_NIGHT": 13,
        "CASH0": 10,
        "START_BOUTS": 2,
        "SCRAP_COST": 2,
        "TAG_COST": 4,
        "BELT_COST": 8,
        "SCRAP_LEAD": 1,
        "TAG_LEAD": 2,
        "BELT_LEAD": 3,
        "SCRAP_PTS": 1,
        "TAG_PTS": 2,
        "BELT_PTS": 3,
        "PAIR": 2,
        "TRIPLE": 3,
        "DIV": 6,
        "HUSTLE": 3,
        "BAR0": 26,
        "STEP": 1,
        "STEP_LATE": 2,
        "HOT": 2,
        "HOT_NEED": 5,
        "HOT_PINNED": 6,
        "FAV": 2,
        "HUB_COST": 8,
        "HUB_PTS": 2,
        "CP_COST": 3,
        "CP_CUT": 2,
        "_PERIODS": [3, 4, 5],
        "_H_MIN": 0.35,
        "_H_BLOCK_MIN": 3,
        "_H_KEEP": 2,
    }

    RULES = """
1. {RING} outposts ring the Hub. Each night book one bout at an outpost, replacing any bout there: Scrap costs {SCRAP_COST} cash, Tag {TAG_COST}, Belt {BELT_COST}. They go live after {SCRAP_LEAD}, {TAG_LEAD} and {BELT_LEAD} dusks.
2. Rating counts live bouts only: Scrap {SCRAP_PTS}, Tag {TAG_PTS}, Belt {BELT_PTS}, plus {PAIR} for each pair of neighbours of different kinds and {TRIPLE} for each three neighbours in a row of three different kinds.
3. You start with {CASH0} cash and {START_BOUTS} live bouts at random. Each dusk you earn 1 cash per {DIV} Rating. Or skip booking and work the crowd for {HUSTLE} cash.
4. Vesper's bar starts at {BAR0} and climbs {STEP} each dusk, {HOT} more on a die roll of {HOT_NEED}+. Goal: when night {NIGHTS} ends, Rating at least equals the bar. Lose if short. Nights: {NIGHTS}.
5. On a hidden fixed beat, every few nights, Vesper raids at dusk and poaches the outpost bout live longest (lowest outpost on a tie), leaving it dark. You see a raid only as it lands.
6. From night {CP_NIGHT} you may counter-program instead of booking, for {CP_COST} cash: a raid due tonight is cancelled, otherwise the bar drops {CP_CUT}. Vesper's surge then needs a {HOT_PINNED}.
7. At night {MID} the sponsor's secret favourite kind is revealed: each live bout of it adds {FAV} Rating. From night {MID} the bar climbs {STEP_LATE} each dusk.
8. From night {MID} book one main event at the Hub for {HUB_COST} cash, replacing the last. It goes live like its kind and scores {HUB_PTS} per live outpost bout of that kind (+{FAV} if favourite).
"""

    ACTIONS = ["book", "main", "hustle", "block"]
    TAGS = ["raid", "blocked", "smear", "reveal", "hub_open", "late_bar", "replace", "fav_booked", "broke"]
    TRACKED = ["cash", "ring"]

    BOUNDS = {"cash": (0, 600), "bar": (0, 300), "rating": (0, 200), "gap": (-300, 200), "live": (0, 8)}
    REACH = {"gap": 0, "live": 8}
    DERIVED = {
        "rating": lambda g, s: g.rating(s),
        "gap": lambda g, s: g.rating(s) - s["bar"],
        "live": lambda g, s: sum(1 for b in s["ring"] if b and b["wait"] == 0),
    }
    GATES = {
        "book": {"_if": lambda g, s: g.can_book(s)},
        "main": {"cash": "HUB_COST", "_turn": "MID", "_if": lambda g, s: g.can_main(s)},
        "hustle": {},
        "block": {"cash": "CP_COST", "_turn": "CP_NIGHT"},
    }

    @property
    def turns(self):
        return self.C["NIGHTS"]

    # ------------------------------------------------------------ small helpers

    def cost(self, kind):
        return self.C[kind.upper() + "_COST"]

    def lead(self, kind):
        return self.C[kind.upper() + "_LEAD"]

    def pts(self, kind):
        return self.C[kind.upper() + "_PTS"]

    def can_book(self, s):
        for k in KINDS:
            if s["cash"] >= self.cost(k) and any((not b) or b["k"] != k for b in s["ring"]):
                return True
        return False

    def can_main(self, s):
        return any((not s["hub"]) or s["hub"]["k"] != k for k in KINDS)

    def score(self, kinds, hub, fav):
        """Rating of a ring of kinds (None for an empty or not-yet-live outpost) and a hub kind."""
        C = self.C
        n = len(kinds)
        total = 0
        for i in range(n):
            a = kinds[i]
            if a is None:
                continue
            total += self.pts(a)
            if fav is not None and a == fav:
                total += C["FAV"]
            b = kinds[(i + 1) % n]
            if b is not None and b != a:
                total += C["PAIR"]
                c = kinds[(i + 2) % n]
                if c is not None and c != a and c != b:
                    total += C["TRIPLE"]
        if hub is not None:
            total += C["HUB_PTS"] * sum(1 for k in kinds if k == hub)
            if fav is not None and hub == fav:
                total += C["FAV"]
        return total

    def live_kinds(self, s):
        return [b["k"] if b and b["wait"] == 0 else None for b in s["ring"]]

    def rating(self, s):
        hub = s["hub"]["k"] if s["hub"] and s["hub"]["wait"] == 0 else None
        return self.score(self.live_kinds(s), hub, s["fav"])

    def potential(self, s):
        """Rating if every bout already booked were live."""
        kinds = [b["k"] if b else None for b in s["ring"]]
        hub = s["hub"]["k"] if s["hub"] else None
        return self.score(kinds, hub, s["fav"])

    def gains(self, s):
        """What booking each kind at each outpost would add to the potential Rating (None where it is the same kind)."""
        kinds = [b["k"] if b else None for b in s["ring"]]
        hub = s["hub"]["k"] if s["hub"] else None
        base = self.score(kinds, hub, s["fav"])
        out = {}
        for k in KINDS:
            row = []
            for i in range(len(kinds)):
                if kinds[i] == k:
                    row.append(None)
                    continue
                new = list(kinds)
                new[i] = k
                row.append(self.score(new, hub, s["fav"]) - base)
            out[k] = row
        return out

    def raid_target(self, s):
        """Index of the live outpost bout that has been live longest (lowest outpost on a tie), or None."""
        best = None
        for i, b in enumerate(s["ring"]):
            if b and b["wait"] == 0 and (best is None or b["since"] < s["ring"][best]["since"]):
                best = i
        return best

    def due_tonight(self, s):
        """The beat as the player can read it: two raids seen give the gap, so the next one is due at last + gap."""
        sp = s["specials"]
        if len(sp) < 2:
            return False
        return sp[-1] + (sp[-1] - sp[-2]) == s["_turn"]

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        N = C["RING"]

        def empty(t, **over):
            base = {"ring": [None] * N, "hub": None, "cash": 50, "fav": None, "hidden__period": 999, "hidden__offset": 998}
            base.update(over)
            return t.fresh(**copy.deepcopy(base))

        def live(kind, since=0):
            return {"k": kind, "wait": 0, "since": since}

        def ring_of(**slots):
            r = [None] * N
            for key, v in slots.items():
                r[int(key[1:])] = v
            return r

        def r1(t):
            for kind in KINDS:
                s = empty(t)
                t.apply(s, "book", {"kind": kind, "outpost": 3})
                t.eq(s["cash"], 50 - self.cost(kind), f"{kind} cost")
                t.eq(s["ring"][2]["k"], kind, f"{kind} is booked at the chosen outpost")
                t.eq(s["ring"][2]["wait"], self.lead(kind), f"{kind} goes live after its lead")
                t.eq(sum(1 for b in s["ring"] if b), 1, "one bout per booking")
            s = empty(t, ring=ring_of(r0=live("scrap")))
            t.apply(s, "book", {"kind": "tag", "outpost": 1})
            t.eq((s["ring"][0]["k"], s["ring"][0]["wait"]), ("tag", C["TAG_LEAD"]), "a booking replaces the bout there, even a live one")
            t.ok(not t.offered(s, "book", kind="tag", outpost=1), "re-booking the same kind is pointless and not offered")
            t.ok(t.offered(s, "book", kind="scrap", outpost=1), "another kind can replace it")
            t.ok(t.offered(s, "book", kind="tag", outpost=N), "the last outpost is bookable")
            t.ok(not t.offered(s, "book", kind="tag", outpost=N + 1), "only the ring's outposts")
            t.ok(not t.offered(s, "book", kind="tag", outpost=0), "outposts count from 1")
            for kind in KINDS:
                s = empty(t, cash=self.cost(kind))
                t.ok(t.offered(s, "book", kind=kind, outpost=1), f"exactly enough cash books a {kind}")
                s = empty(t, cash=self.cost(kind) - 1)
                t.ok(not t.offered(s, "book", kind=kind, outpost=1), f"one cash short cannot book a {kind}")
            s = empty(t)
            s2, ev = t.step(s, "book", {"kind": "belt", "outpost": 2})
            t.eq(s2["_turn"], 2, "one booking ends the night")
            s = empty(t, cash=C["SCRAP_COST"])
            self._hits.clear()
            t.apply(s, "book", {"kind": "scrap", "outpost": 1})
            t.eq(s["cash"], 0, "spending the last cash is allowed")
            t.ok("broke" in self._hits, "being left with no cash is noted")
            s = empty(t, cash=C["SCRAP_COST"] + 1)
            self._hits.clear()
            t.apply(s, "book", {"kind": "scrap", "outpost": 1})
            t.ok("broke" not in self._hits, "one cash left is not broke")
            s = empty(t, ring=ring_of(r0=live("scrap")))
            self._hits.clear()
            t.apply(s, "book", {"kind": "tag", "outpost": 1})
            t.ok("replace" in self._hits, "bumping a bout is noted")
            s = empty(t)
            self._hits.clear()
            t.apply(s, "book", {"kind": "tag", "outpost": 1})
            t.ok("replace" not in self._hits, "booking an empty outpost bumps nothing")
            for kind in KINDS:
                s = empty(t)
                t.apply(s, "book", {"kind": kind, "outpost": 2})
                lead = self.lead(kind)
                for d in range(lead):
                    t.eq(s["ring"][1]["wait"], lead - d, f"{kind} still travelling before dusk {d + 1}")
                    t.eq(self.rating(s), 0, f"a travelling {kind} scores nothing")
                    t.advance(s, turn=2 + d)
                t.eq(s["ring"][1]["wait"], 0, f"{kind} is live after {lead} dusks")
                t.eq(s["ring"][1]["since"], 1 + lead, f"{kind} is live from the night after its last dusk")
                t.eq(self.rating(s), self.pts(kind), f"{kind} scores once live")

        def r2(t):
            s = empty(t)
            t.eq(self.rating(s), 0, "an empty ring scores nothing")
            for kind in KINDS:
                s = empty(t, ring=ring_of(r0=live(kind)))
                t.eq(self.rating(s), self.pts(kind), f"a lone {kind}")
            s = empty(t, ring=ring_of(r0={"k": "belt", "wait": 1, "since": None}))
            t.eq(self.rating(s), 0, "a bout still travelling does not score")
            s = empty(t, ring=ring_of(r0=live("scrap"), r1=live("tag")))
            t.eq(self.rating(s), C["SCRAP_PTS"] + C["TAG_PTS"] + C["PAIR"], "neighbours of different kinds add the pair bonus")
            s = empty(t, ring=ring_of(r0=live("tag"), r1=live("tag")))
            t.eq(self.rating(s), 2 * C["TAG_PTS"], "neighbours of the same kind add nothing")
            s = empty(t, ring=ring_of(r0=live("scrap"), r2=live("belt")))
            t.eq(self.rating(s), C["SCRAP_PTS"] + C["BELT_PTS"], "bouts that are not neighbours add nothing")
            last = "r%d" % (N - 1)
            s = empty(t, ring=ring_of(r0=live("scrap"), **{last: live("belt")}))
            t.eq(self.rating(s), C["SCRAP_PTS"] + C["BELT_PTS"] + C["PAIR"], "the ring wraps: outpost 1 and the last are neighbours")
            want = C["SCRAP_PTS"] + C["TAG_PTS"] + C["BELT_PTS"] + 2 * C["PAIR"] + C["TRIPLE"]
            s = empty(t, ring=ring_of(r0=live("scrap"), r1=live("tag"), r2=live("belt")))
            t.eq(self.rating(s), want, "three different kinds in a row add the triple bonus once")
            s = empty(t, ring=ring_of(r0=live("belt"), r1=live("scrap"), r2=live("tag")))
            t.eq(self.rating(s), want, "the order inside the three does not matter")
            s = empty(t, ring=ring_of(r0=live("scrap"), r1=live("tag"), r2=live("scrap")))
            t.eq(self.rating(s), 2 * C["SCRAP_PTS"] + C["TAG_PTS"] + 2 * C["PAIR"], "S T S is two pairs and no triple")
            s = empty(t, ring=ring_of(r0=live("scrap"), r1={"k": "tag", "wait": 1, "since": None}, r2=live("belt")))
            t.eq(self.rating(s), C["SCRAP_PTS"] + C["BELT_PTS"], "a travelling bout in the middle breaks the run")
            s = empty(t, ring=ring_of(r0=live("tag"), r1=live("belt"), **{last: live("scrap")}))
            t.eq(self.rating(s), want, "a run of three may wrap around the ring")
            second = "r%d" % (N - 2)
            s = empty(t, ring=ring_of(r0=live("scrap"), **{second: live("tag"), last: live("belt")}))
            t.eq(self.rating(s), want, "a run of three may start on the second to last outpost")
            s = empty(t, ring=ring_of(r0=live("scrap"), r1=live("tag"), r2=live("belt"), r3=live("scrap")))
            t.eq(self.rating(s), 2 * C["SCRAP_PTS"] + C["TAG_PTS"] + C["BELT_PTS"] + 3 * C["PAIR"] + 2 * C["TRIPLE"], "four in a row hold two triples")

        def r3(t):
            s = t.fresh()
            t.eq(s["cash"], C["CASH0"], "starting cash")
            t.eq(sum(1 for b in s["ring"] if b), C["START_BOUTS"], "starting bouts")
            t.ok(all(b["wait"] == 0 for b in s["ring"] if b), "starting bouts are live")
            t.eq(s["hub"], None, "the Hub starts empty")
            ring = ring_of(r0=live("belt"), r2=live("belt"), r4=live("belt"), r6=live("belt"))
            s = empty(t, ring=ring, cash=7)
            r = self.rating(s)
            t.eq(r, 4 * C["BELT_PTS"], "four lone Belts")
            t.advance(s, turn=2)
            t.eq(s["cash"], 7 + r // C["DIV"], "the gate pays Rating over DIV, rounded down")
            s = empty(t, ring=ring_of(r0=live("belt"), r1=live("tag")), cash=7)
            r = self.rating(s)
            t.advance(s, turn=2)
            t.eq(s["cash"], 7 + r // C["DIV"], "the gate pays Rating over DIV again")
            s = empty(t, ring=ring_of(r0=live("scrap")), cash=7)
            t.advance(s, turn=2)
            t.eq(s["cash"], 7 + C["SCRAP_PTS"] // C["DIV"], "a Rating under DIV pays nothing")
            s = empty(t, ring=ring_of(r0={"k": "belt", "wait": 1, "since": None}), cash=7)
            t.advance(s, turn=2)
            t.eq(s["cash"], 7, "a bout that goes live at this dusk pays from the next one")
            s = empty(t, cash=5)
            t.ok(t.offered(s, "hustle"), "working the crowd is always offered")
            t.apply(s, "hustle")
            t.eq(s["cash"], 5 + C["HUSTLE"], "working the crowd pays")
            t.eq(sum(1 for b in s["ring"] if b), 0, "working the crowd books nothing")
            s = empty(t, cash=0)
            t.eq(t.ids(s), ["hustle"], "with no cash the crowd is the only move")

        def r4(t):
            s = empty(t)
            t.eq(s["bar"], C["BAR0"], "the bar starts at BAR0")
            t.eq(self.turns, C["NIGHTS"], "the budget is NIGHTS")
            bar = s["bar"]
            for n in range(1, 6):
                t.advance(s, turn=n + 1, dice=[1])
                t.eq(s["bar"] - bar, C["STEP"], f"the bar climbs STEP at dusk {n}")
                bar = s["bar"]
            for roll, extra in ((C["HOT_NEED"] - 1, 0), (C["HOT_NEED"], C["HOT"]), (6, C["HOT"])):
                bar = s["bar"]
                ev = t.advance(s, turn=3, dice=[roll])
                t.eq(s["bar"] - bar, C["STEP"] + extra, f"a surge roll of {roll} adds {extra}")
                t.ok(any(f"roll {roll}" in e for e in ev), "the die is shown")
            s = empty(t)
            s["bar"] = 5
            s["_turn"] = C["NIGHTS"]
            t.ok(self.check_end(s) is None, "the last night is still played")
            ring = ring_of(r0=live("belt"))
            for bar, want in ((C["BELT_PTS"] - 1, "win"), (C["BELT_PTS"], "win"), (C["BELT_PTS"] + 1, "loss")):
                s = empty(t, ring=ring, bar=bar)
                s["_turn"] = C["NIGHTS"] + 1
                end = self.check_end(s)
                t.ok(end and end["result"] == want, f"Rating {C['BELT_PTS']} against bar {bar} is a {want}")
            s = empty(t, ring=ring, bar=1)
            s["_turn"] = C["NIGHTS"] - 1
            t.ok(self.check_end(s) is None, "a lead before the end wins nothing")
            ring = ring_of(r0=live("belt"), r2=live("belt"), r4=live("belt"))
            s = empty(t, ring=ring, bar=1)
            s["_turn"] = C["NIGHTS"]
            s2, ev = t.step(s, "hustle")
            t.ok(s2["_ended"] and s2["_turn"] == C["NIGHTS"] + 1, "the game ends when the last night does")
            t.eq(s2["_ended"]["result"], "win", "the last night's dusk is scored")
            s = empty(t, ring=ring, bar=100)
            s["_turn"] = C["NIGHTS"]
            s2, ev = t.step(s, "hustle")
            t.eq(s2["_ended"]["result"], "loss", "short of the bar at the end is a loss")

        def r5(t):
            s = empty(t, hidden__period=4, hidden__offset=1, ring=ring_of(r0=live("scrap", 0)))
            seen = []
            for n in range(1, 8):
                s["ring"][0] = live("scrap", 0)
                ev = t.advance(s, turn=n + 1)
                if s["ring"][0] is None:
                    seen.append(n)
                    t.ok(any("raid" in e.lower() for e in ev), "a raid is announced as it lands")
                else:
                    t.ok(not any("raid" in e.lower() for e in ev), f"night {n} is quiet")
            t.eq(seen, [1, 5], "period 4 offset 1 raids on nights 1 and 5")
            t.eq(s["specials"], [1, 5], "the player sees the nights it raided")
            s = empty(t, hidden__period=3, hidden__offset=0)
            for n in range(1, 8):
                t.advance(s, turn=n + 1)
            t.eq(s["specials"], [3, 6], "offset 0 raids on the period itself")
            s = empty(t, hidden__period=4, hidden__offset=0, ring=ring_of(r0=live("belt", 5), r3=live("scrap", 2), r5=live("tag", 2)))
            self._hits.clear()
            t.advance(s, turn=5)
            t.eq([b is None for b in s["ring"]][:6], [False, True, True, True, True, False], "the oldest, lowest outpost goes dark")
            t.ok(s["ring"][0] is not None and s["ring"][5] is not None, "the others stay")
            t.ok("raid" in self._hits, "the raid is noted")
            s = empty(t, hidden__period=4, hidden__offset=0, ring=ring_of(r0=live("belt", 5), r3=live("scrap", 2), r5=live("tag", 1)))
            t.advance(s, turn=5)
            t.ok(s["ring"][5] is None and s["ring"][3] is not None, "the longest-live bout is poached, whatever its kind")
            s = empty(t, hidden__period=4, hidden__offset=0, ring=ring_of(r0={"k": "belt", "wait": 1, "since": None}, r2=live("scrap", 9)))
            t.advance(s, turn=5)
            t.ok(s["ring"][2] is None and s["ring"][0] is not None, "a travelling bout cannot be raided")
            s = empty(t, hidden__period=4, hidden__offset=0, hub=live("belt"))
            t.advance(s, turn=5)
            t.ok(s["hub"] is not None, "the Hub is never raided")
            t.eq(s["specials"], [4], "a raid that finds nothing is still seen")
            s = empty(t, hidden__period=4, hidden__offset=0, ring=ring_of(r0=live("scrap", 0), r1=live("scrap", 0)))
            t.advance(s, turn=5)
            t.ok(s["ring"][0] is None and s["ring"][1] is not None, "a tie goes to the lowest outpost")
            s = empty(t, hidden__period=4, hidden__offset=1, ring=ring_of(r0=live("scrap", 0)))
            t.advance(s, turn=5)
            t.ok(s["ring"][0] is not None, "no raid off the beat")
            s = empty(t)
            s["specials"] = [4, 9]
            s["_turn"] = 14
            t.ok(self.due_tonight(s), "two raids show the beat")
            s["_turn"] = 13
            t.ok(not self.due_tonight(s), "a quiet night is not due")
            s["specials"] = [9]
            s["_turn"] = 14
            t.ok(not self.due_tonight(s), "one raid does not yet show the beat")

        def r6(t):
            s = empty(t, cash=C["CP_COST"])
            s["_turn"] = C["CP_NIGHT"] - 1
            t.ok(not t.offered(s, "block"), "no counter-programming before its night")
            s["_turn"] = C["CP_NIGHT"]
            t.ok(t.offered(s, "block"), "counter-programming from its night")
            s = empty(t, cash=C["CP_COST"] - 1)
            s["_turn"] = C["CP_NIGHT"]
            t.ok(not t.offered(s, "block"), "it needs CP_COST in hand")
            s = empty(t, cash=10)
            s["_turn"] = C["CP_NIGHT"]
            t.apply(s, "block")
            t.eq(s["cash"], 10 - C["CP_COST"], "counter-programming costs CP_COST")
            t.eq(s["block"], True, "the block is set")
            t.eq(sum(1 for b in s["ring"] if b), 0, "counter-programming books nothing")
            s2, ev = t.step(s, "block")
            t.eq(s2["_turn"], C["CP_NIGHT"] + 1, "counter-programming uses up the night")
            s = empty(t, cash=10, hidden__period=4, hidden__offset=0, ring=ring_of(r0=live("belt", 1)))
            s["block"] = True
            bar = s["bar"]
            self._hits.clear()
            t.advance(s, turn=5, dice=[1])
            t.ok(s["ring"][0] is not None, "a cancelled raid takes nothing")
            t.eq(s["bar"] - bar, C["STEP"], "a cancelled raid leaves the bar's climb alone")
            t.eq(s["block"], False, "the block is spent")
            t.ok("blocked" in self._hits and "smear" not in self._hits, "the cancel is noted")
            t.eq(s["specials"], [4], "the player still learns the raid was due")
            s = empty(t, cash=10, hidden__period=4, hidden__offset=0)
            s["block"] = True
            bar = s["bar"]
            self._hits.clear()
            t.advance(s, turn=4, dice=[1])
            t.eq(s["bar"] - bar, C["STEP"] - C["CP_CUT"], "with no raid due it cuts the bar")
            t.eq(s["block"], False, "the block is spent either way")
            t.ok("smear" in self._hits and "blocked" not in self._hits, "the cut is noted")
            t.eq(s["specials"], [], "nothing due, nothing logged")
            s = empty(t, cash=10, hidden__period=4, hidden__offset=0, ring=ring_of(r0=live("belt", 1)))
            bar = s["bar"]
            self._hits.clear()
            t.advance(s, turn=5, dice=[1])
            t.ok(s["ring"][0] is None, "without the block the raid lands")
            t.eq(s["bar"] - bar, C["STEP"], "and no cut")
            t.ok("smear" not in self._hits, "no cut is noted")
            for blocked, roll, extra in ((True, C["HOT_NEED"], 0), (True, C["HOT_PINNED"], C["HOT"]), (False, C["HOT_NEED"], C["HOT"])):
                s = empty(t, cash=10)
                s["block"] = blocked
                bar = s["bar"]
                ev = t.advance(s, turn=4, dice=[roll])
                cut = C["CP_CUT"] if blocked else 0
                t.eq(s["bar"] - bar, C["STEP"] + extra - cut, f"a surge roll of {roll} with the block {blocked}")
                if blocked:
                    t.ok(any(f"need {C['HOT_PINNED']}+" in e for e in ev), "the pinned target is shown")

        def r7(t):
            s = empty(t, hidden__fav="belt", ring=ring_of(r0=live("belt")))
            t.eq(s["fav"], None, "the favourite starts unknown")
            t.eq(self.visible(s)["fav"], None, "the player cannot see it yet")
            t.eq(self.rating(s), C["BELT_PTS"], "no favourite bonus before the reveal")
            self._hits.clear()
            t.advance(s, turn=C["MID"] - 1)
            t.eq(s["fav"], None, "not revealed before night MID")
            t.ok("reveal" not in self._hits, "no reveal tag yet")
            t.advance(s, turn=C["MID"])
            t.eq(s["fav"], "belt", "revealed when night MID begins")
            t.ok("reveal" in self._hits and "hub_open" in self._hits, "the reveal and the Hub opening are noted")
            t.ok("late_bar" not in self._hits, "the bar has not climbed faster yet")
            t.eq(self.rating(s), C["BELT_PTS"] + C["FAV"], "each live bout of the favourite adds FAV")
            s = empty(t, fav="belt", ring=ring_of(r0=live("scrap")))
            t.eq(self.rating(s), C["SCRAP_PTS"], "other kinds get nothing")
            s = empty(t, fav="belt")
            self._hits.clear()
            t.apply(s, "book", {"kind": "belt", "outpost": 1})
            t.ok("fav_booked" in self._hits, "booking the favourite is noted")
            s = empty(t, fav="belt")
            self._hits.clear()
            t.apply(s, "book", {"kind": "tag", "outpost": 1})
            t.ok("fav_booked" not in self._hits, "booking another kind is not")
            s = empty(t, fav=None, hidden__fav="belt")
            self._hits.clear()
            t.apply(s, "book", {"kind": "belt", "outpost": 1})
            t.ok("fav_booked" not in self._hits, "before the reveal nobody knows the favourite")
            s = empty(t, fav="belt", ring=ring_of(r0={"k": "belt", "wait": 1, "since": None}))
            t.eq(self.rating(s), 0, "a travelling favourite adds nothing")
            s = empty(t, hidden__fav="belt")
            before = s["bar"]
            t.advance(s, turn=C["MID"], dice=[1])
            t.eq(s["bar"] - before, C["STEP"], "the dusk before night MID still climbs by STEP")
            before = s["bar"]
            self._hits.clear()
            t.advance(s, turn=C["MID"] + 1, dice=[1])
            t.ok("late_bar" in self._hits, "the faster climb is noted")
            t.eq(s["bar"] - before, C["STEP_LATE"], "from night MID the bar climbs by STEP_LATE")
            before = s["bar"]
            t.advance(s, turn=C["MID"] + 2, dice=[1])
            t.eq(s["bar"] - before, C["STEP_LATE"], "and keeps climbing by STEP_LATE")
            before = s["bar"]
            t.advance(s, turn=C["MID"] + 3, dice=[C["HOT_NEED"]])
            t.eq(s["bar"] - before, C["STEP_LATE"] + C["HOT"], "a surge adds to the late climb")
            t.advance(s, turn=C["NIGHTS"] + 1)
            t.eq(s["fav"], "belt", "the favourite stays known")

        def r8(t):
            s = empty(t, cash=C["HUB_COST"])
            s["_turn"] = C["MID"] - 1
            t.ok(not t.offered(s, "main", kind="tag"), "no main event before night MID")
            s["_turn"] = C["MID"]
            t.ok(t.offered(s, "main", kind="tag"), "main event from night MID")
            s = empty(t, cash=C["HUB_COST"] - 1)
            s["_turn"] = C["MID"]
            t.ok(not t.offered(s, "main", kind="tag"), "the main event needs HUB_COST")
            for kind in KINDS:
                s = empty(t, cash=30)
                s["_turn"] = C["MID"]
                t.apply(s, "main", {"kind": kind})
                t.eq(s["cash"], 30 - C["HUB_COST"], "the main event costs HUB_COST whatever the kind")
                t.eq((s["hub"]["k"], s["hub"]["wait"]), (kind, self.lead(kind)), f"a {kind} main event goes live like a {kind}")
                t.ok(not t.offered(s, "main", kind=kind), "the same kind is not offered again")
            t.apply(s, "main", {"kind": "tag"})
            t.eq((s["hub"]["k"], s["hub"]["wait"]), ("tag", C["TAG_LEAD"]), "a new main event replaces the last")
            s = empty(t, fav="belt", cash=30)
            s["_turn"] = C["MID"]
            self._hits.clear()
            t.apply(s, "main", {"kind": "belt"})
            t.ok("fav_booked" in self._hits, "a favourite main event is noted")
            s = empty(t, fav="belt", cash=30)
            s["_turn"] = C["MID"]
            self._hits.clear()
            t.apply(s, "main", {"kind": "tag"})
            t.ok("fav_booked" not in self._hits, "another kind is not")
            ring = ring_of(r0=live("scrap"), r2=live("scrap"), r4=live("scrap"))
            s = empty(t, ring=ring)
            base = self.rating(s)
            s["hub"] = live("scrap")
            t.eq(self.rating(s), base + 3 * C["HUB_PTS"], "the main event scores HUB_PTS per live outpost bout of its kind")
            s["hub"] = live("belt")
            t.eq(self.rating(s), base, "no outpost bout of its kind, no points")
            s["hub"] = {"k": "scrap", "wait": 1, "since": None}
            t.eq(self.rating(s), base, "a travelling main event scores nothing")
            s["hub"] = live("scrap")
            s["ring"][4] = {"k": "scrap", "wait": 1, "since": None}
            t.eq(self.rating(s), base - C["SCRAP_PTS"] + 2 * C["HUB_PTS"], "only live outpost bouts count for it")
            s = empty(t, ring=ring, fav="scrap")
            s["hub"] = live("scrap")
            t.eq(self.rating(s), 3 * C["SCRAP_PTS"] + 3 * C["FAV"] + 3 * C["HUB_PTS"] + C["FAV"], "a favourite main event adds FAV too")
            s = empty(t, hub=live("scrap"), cash=0, hidden__period=4, hidden__offset=0)
            t.advance(s, turn=C["MID"] + 3)
            t.eq(s["cash"], 0, "the Hub on its own scores nothing and pays nothing")

        return [
            (1, "booking", r1), (2, "rating", r2), (3, "gate and crowd", r3), (4, "bar and goal", r4),
            (5, "raids", r5), (6, "counter-program", r6), (7, "midpoint", r7), (8, "main event", r8),
        ]

    # ------------------------------------------------------------ hidden facts

    def resample_hidden(self, s, rng):
        """The favourite is unknown until night MID; the beat is whatever fits the raids seen so far."""
        h = s["hidden"]
        if s["fav"] is None:
            h["fav"] = rng.choice(KINDS)
        last = s["_turn"] - 1
        seen = set(s["specials"])
        fits = []
        for p in self.C["_PERIODS"]:
            for o in range(p):
                if all(((m % p) == o) == (m in seen) for m in range(1, last + 1)):
                    fits.append([p, o])
        if fits:
            p, o = rng.choice(fits)
            h["period"], h["offset"] = p, o

    # ------------------------------------------------------------ engine contract

    def init_state(self, rng):
        C = self.C
        n = C["RING"]
        ring = [None] * n
        spots = list(range(n))
        rng.shuffle(spots)
        for i in spots[: C["START_BOUTS"]]:
            ring[i] = {"k": rng.choice(KINDS), "wait": 0, "since": 0}
        p = rng.choice(C["_PERIODS"])
        o = rng.choice(list(range(p)))
        return {
            "cash": C["CASH0"],
            "ring": ring,
            "hub": None,
            "bar": C["BAR0"],
            "fav": None,
            "specials": [],
            "block": False,
            "hidden": {"fav": rng.choice(KINDS), "period": p, "offset": o},
        }

    def options(self, s):
        C = self.C
        n = s["_turn"]
        o = []
        # shown best first: kinds by their best Rating per cash, outposts by Rating gained
        gains = self.gains(s)
        rows = []
        for k in KINDS:
            cost = self.cost(k)
            if s["cash"] < cost:
                continue
            slots = sorted((i for i, g in enumerate(gains[k]) if g is not None), key=lambda i: (-gains[k][i], i))
            if not slots:
                continue
            rows.append((-gains[k][slots[0]] / cost, KINDS.index(k), k, [i + 1 for i in slots]))
        rows.sort()
        for _, _, k, slots in rows:
            o.append({
                "id": "book",
                "label": f"Book a {NAME[k]} bout ({self.cost(k)} cash, live after {plural(self.lead(k), 'dusk')})",
                "args": {"kind": k},
                "group": "Book an outpost bout",
                "params": {"outpost": {"choices": slots}},
            })
        if n >= C["MID"] and s["cash"] >= C["HUB_COST"]:
            hub_now = s["hub"]["k"] if s["hub"] else None
            kinds_pot = [b["k"] if b else None for b in s["ring"]]
            ordered = sorted((k for k in KINDS if k != hub_now), key=lambda k: (-self.score(kinds_pot, k, s["fav"]), KINDS.index(k)))
            for k in ordered:
                o.append({
                    "id": "main",
                    "label": f"Main event at the Hub: a {NAME[k]} ({C['HUB_COST']} cash, live after {plural(self.lead(k), 'dusk')})",
                    "args": {"kind": k},
                    "group": "Main event at the Hub",
                })
        o.append({"id": "hustle", "label": f"Work the crowd (+{C['HUSTLE']} cash, no booking tonight)", "args": {}})
        if n >= C["CP_NIGHT"] and s["cash"] >= C["CP_COST"]:
            o.append({
                "id": "block",
                "label": f"Counter-program tonight ({C['CP_COST']} cash: cancels a raid if one is due, otherwise cuts the bar by {C['CP_CUT']}; Vesper's surge needs a {C['HOT_PINNED']})",
                "args": {},
            })
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "book":
            k, slot = args["kind"], int(args["outpost"])
            old = s["ring"][slot - 1]
            s["cash"] -= self.cost(k)
            s["ring"][slot - 1] = {"k": k, "wait": self.lead(k), "since": None}
            if old:
                self.hit("replace")
                ev.append(f"Outpost {slot}: the {NAME[old['k']]} is bumped for a {NAME[k]} ({self.cost(k)} cash), live after {plural(self.lead(k), 'dusk')}.")
            else:
                ev.append(f"Outpost {slot}: a {NAME[k]} is booked ({self.cost(k)} cash), live after {plural(self.lead(k), 'dusk')}.")
            if s["fav"] is not None and k == s["fav"]:
                self.hit("fav_booked")
        elif a == "main":
            k = args["kind"]
            s["cash"] -= C["HUB_COST"]
            s["hub"] = {"k": k, "wait": self.lead(k), "since": None}
            ev.append(f"The Hub: a {NAME[k]} main event is booked ({C['HUB_COST']} cash), live after {plural(self.lead(k), 'dusk')}.")
            if s["fav"] is not None and k == s["fav"]:
                self.hit("fav_booked")
        elif a == "hustle":
            s["cash"] += C["HUSTLE"]
            ev.append(f"You work the crowd: cash +{C['HUSTLE']}.")
        elif a == "block":
            s["cash"] -= C["CP_COST"]
            s["block"] = True
            ev.append(f"You line up counter-programming for tonight ({C['CP_COST']} cash).")
        if s["cash"] == 0:
            self.hit("broke")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        n = s["_turn"] - 1  # the night that just ended
        h = s["hidden"]
        # the gate pays on the Rating that was live as the night closed
        r = self.rating(s)
        pay = r // C["DIV"]
        s["cash"] += pay
        ev.append(f"Dusk: Rating {r} pays {pay} cash.")
        # Vesper's raid, on the live bouts as they stood
        due = (n % h["period"]) == h["offset"]
        if due:
            s["specials"].append(n)
            if s["block"]:
                self.hit("blocked")
                ev.append("Vesper's crews move in, but your counter-programming cancels the raid.")
            else:
                i = self.raid_target(s)
                if i is None:
                    ev.append("Vesper's crews raid and find no live outpost bout to poach.")
                else:
                    gone = s["ring"][i]
                    s["ring"][i] = None
                    self.hit("raid")
                    ev.append(f"Vesper raids outpost {i + 1} and poaches the {NAME[gone['k']]}. The outpost goes dark.")
        # travelling bouts move up
        for i, b in enumerate(s["ring"]):
            if b and b["wait"] > 0:
                b["wait"] -= 1
                if b["wait"] == 0:
                    b["since"] = s["_turn"]
                    ev.append(f"Outpost {i + 1}: the {NAME[b['k']]} goes live.")
        hub = s["hub"]
        if hub and hub["wait"] > 0:
            hub["wait"] -= 1
            if hub["wait"] == 0:
                hub["since"] = s["_turn"]
                ev.append(f"The Hub: the {NAME[hub['k']]} main event goes live.")
        # Vesper's bar
        step = C["STEP_LATE"] if n >= C["MID"] else C["STEP"]
        ok, txt = rng.check(C["HOT_PINNED"] if s["block"] else C["HOT_NEED"], 6, "surge")
        if ok:
            step += C["HOT"]
        s["bar"] += step
        ev.append(f"{txt}: Vesper's bar climbs {step}.")
        if s["block"] and not due:
            s["bar"] -= C["CP_CUT"]
            self.hit("smear")
            ev.append(f"No raid was due, so your counter-programming cuts the bar by {C['CP_CUT']}.")
        s["block"] = False
        if n == C["MID"]:
            self.hit("late_bar")
        # the midpoint
        if s["_turn"] == C["MID"]:
            s["fav"] = h["fav"]
            self.hit("reveal")
            self.hit("hub_open")
            ev.append(f"Night {C['MID']} opens: the sponsor's favourite kind is the {NAME[s['fav']]}, and the Hub is open for a main event.")
        return ev

    def status_line(self, s):
        ring = "".join(("." if not b else CH[b["k"]] if b["wait"] == 0 else CH[b["k"]].lower()) for b in s["ring"])
        hub = s["hub"]
        hub_ch = "." if not hub else CH[hub["k"]] if hub["wait"] == 0 else CH[hub["k"]].lower()
        return f"Cash {s['cash']} | Rating {self.rating(s)} | Bar {s['bar']} | Ring {ring} Hub {hub_ch}"

    def visible(self, s):
        v = {k: s[k] for k in ("cash", "ring", "hub", "bar", "fav", "specials")}
        v["rating"] = self.rating(s)
        v["rating_if_all_live"] = self.potential(s)
        v["gap"] = self.rating(s) - s["bar"]
        v["night"] = min(s["_turn"], self.turns)
        v["nights_left_after_tonight"] = max(0, self.turns - s["_turn"])
        v["gain_if_booked"] = self.gains(s)
        t = self.raid_target(s)
        v["next_raid_would_take_outpost"] = None if t is None else t + 1
        v["outposts"] = OUTPOSTS[: len(s["ring"])]
        return v

    def check_end(self, s):
        if s["_turn"] > self.turns:
            r = self.rating(s)
            if r >= s["bar"]:
                return {"result": "win", "reason": f"Rating {r} met Vesper's bar of {s['bar']}"}
            return {"result": "loss", "reason": f"Rating {r} fell short of Vesper's bar of {s['bar']}"}
        return None

    # ------------------------------------------------------------ the sensible player

    def heuristic(self, s, options, rng):
        C = self.C
        left = self.turns - s["_turn"] + 1  # dusks left, tonight included
        kinds = [b["k"] if b else None for b in s["ring"]]
        hub = s["hub"]["k"] if s["hub"] else None
        fav = s["fav"]
        base = self.score(kinds, hub, fav)
        best, best_val, best_gain = None, 0.0, 0
        for o in options:
            if o["id"] == "book":
                k = o["args"]["kind"]
                if self.lead(k) > left:
                    continue
                cost = self.cost(k)
                for slot in o["params"]["outpost"]["choices"]:
                    new = list(kinds)
                    new[slot - 1] = k
                    gain = self.score(new, hub, fav) - base
                    val = gain / cost
                    if val > best_val:
                        best, best_val, best_gain = {"id": "book", "args": {"kind": k, "outpost": slot}}, val, gain
            elif o["id"] == "main":
                k = o["args"]["kind"]
                if self.lead(k) > left:
                    continue
                gain = self.score(kinds, k, fav) - base
                val = gain / C["HUB_COST"]
                if val > best_val:
                    best, best_val, best_gain = {"id": "main", "args": {"kind": k}}, val, gain
        ids = {o["id"] for o in options}
        if "block" in ids and self.due_tonight(s):
            victim = self.raid_target(s)
            if victim is not None:
                live = self.live_kinds(s)
                lhub = s["hub"]["k"] if s["hub"] and s["hub"]["wait"] == 0 else None
                full = self.score(live, lhub, fav)
                live[victim] = None
                drop = full - self.score(live, lhub, fav)
                if drop >= max(best_gain, C["_H_BLOCK_MIN"]):
                    return "block"
        if best is not None and best_val >= C["_H_MIN"]:
            return best
        if "block" in ids and s["cash"] >= C["CP_COST"] + C["_H_KEEP"]:
            return "block"
        return "hustle"


if __name__ == "__main__":
    run(G)
