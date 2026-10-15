"""Dust Licence: a sealed-bid game for /play (v2 contract).

You are the pit boss of a casino ring under a Mars terraforming dome. Eight table licences circle the
Cage. Each turn one licence is auctioned in sealed bids against Madame Vey, the rival pit boss, whose
bidding habit is fixed but secret. The winning convoy must cross the dust to reach the table. The side
holding more tables when the last turn is done wins.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, plural, run  # noqa: E402

STYLES = ["miser", "gambler", "shadow"]
OWNER_WORD = {0: "open", 1: "yours", 2: "Vey's"}


class G(Game):
    name = "Dust Licence"

    CONSTANTS = {
        "TURNS": 16,
        "RING": 8,
        "START": 14,
        "VEY_TABLES": 2,
        "TAKE_MAX": 2,
        "BID_MIN": 1,
        "SIT_GAIN": 2,
        "SIT_PRICE": 1,
        "DUST_NEED": 3,
        "STORM_NEED": 4,
        "STAFF": 3,
        "UPKEEP": 3,
        "CATCHUP": 1,
        "GAMBLE_DIV": 2,
        "MISER_ADD": 2,
        "SHADOW_ADD": 1,
        "SHADOW_OPEN": 3,
        "JITTER_P": 0.25,
        "JITTER_ADD": 1,
        "MID_TURN": 9,
        "CAGE_TAKE": 2,
        "CAGE_POINTS": 3,
        "AUDIT_TURN": 12,
        "AUDIT_COST": 4,
    }

    RULES = """
1. {RING} tables ring the Cage at the centre, each with a take of 1 to {TAKE_MAX} Standing. You and Vey, the rival pit boss, start with {START} Standing. You hold one table; Vey, the incumbent, holds {VEY_TABLES}, opposite you.
2. Each turn one lot comes up from the posted docket. You seal a bid of {BID_MIN} or more Standing, never more than you hold; Vey seals hers, within her means. Revealed together: the higher bid wins and pays it. A tie goes to Vey.
3. Or sit out: bid nothing and gain {SIT_GAIN} Standing. Vey then wins the lot, paying {SIT_PRICE} or all she has, and you learn nothing of her habit.
4. The winner's convoy must reach the lot. Safe if the lot touches a table the winner holds (ring neighbours; the Cage touches all). Otherwise roll {DUST_NEED}+ or the convoy is lost: the bid is still paid and the lot stays as it was.
5. At dusk each side earns the takes of its {STAFF} best tables, the side with fewer tables gains {CATCHUP}, then each pays {UPKEEP} upkeep. Your Standing below 0 after dusk ends your licence and you lose; Vey cannot fall below 0.
6. Vey has one fixed secret habit: she bids the lot's take plus {MISER_ADD}, or her Standing divided by {GAMBLE_DIV} (rounded down, at least {BID_MIN}), or your last bid plus {SHADOW_ADD} ({SHADOW_OPEN} if none). On {JITTER_P:.0%} of turns she bids {JITTER_ADD} more.
7. From turn {MID_TURN} the dust season starts: convoys need {STORM_NEED}+. On turns {MID_TURN} and {TURNS} the lot is the Cage itself: take {CAGE_TAKE}, and it counts as {CAGE_POINTS} tables.
8. Once, from turn {AUDIT_TURN}: instead of bidding, pay {AUDIT_COST} Standing to audit Vey, strip one of her tables and withdraw the lot. After turn {TURNS} the side with more tables wins; a tie goes to Vey.
"""

    ACTIONS = ["bid", "sit", "audit"]
    TAGS = [
        "storm", "cage", "audit", "convoy_lost", "tie_to_vey", "jitter", "sit_out", "vey_broke",
        "steal", "defend", "catchup", "finale",
    ]
    TRACKED = ["standing", "ring"]

    BOUNDS = {
        "standing": (-40, 200), "vey": (0, 200), "last_bid": (0, 200), "mine": (0, 12), "hers": (0, 12),
    }
    REACH = {"standing": ("<=", -1)}
    DERIVED = {
        "mine": lambda g, s: g.points(s, 1),
        "hers": lambda g, s: g.points(s, 2),
    }
    GATES = {
        "bid": {"standing": "BID_MIN"},
        "sit": {},
        "audit": {
            "standing": "AUDIT_COST", "_turn": "AUDIT_TURN", "!audit_used": 1,
            "_if": lambda g, s: any(v == 2 for v in s["ring"]),
        },
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ board helpers

    def cage(self):
        return self.C["RING"]

    def neighbors(self, i):
        n = self.C["RING"]
        if i == n:
            return list(range(n))
        return [(i - 1) % n, (i + 1) % n, n]

    def safe(self, s, who, lot):
        return any(s["ring"][j] == who for j in self.neighbors(lot))

    def take(self, s, i):
        return self.C["CAGE_TAKE"] if i == self.cage() else s["takes"][i]

    def income(self, s, who):
        takes = sorted((self.take(s, i) for i, v in enumerate(s["ring"]) if v == who), reverse=True)
        return sum(takes[: self.C["STAFF"]])

    def points(self, s, who):
        n = self.C["RING"]
        pts = sum(1 for i in range(n) if s["ring"][i] == who)
        if s["ring"][n] == who:
            pts += self.C["CAGE_POINTS"]
        return pts

    def points_of(self, i):
        return self.C["CAGE_POINTS"] if i == self.cage() else 1

    def lot_of(self, s, turn=None):
        t = s["_turn"] if turn is None else turn
        t = max(1, min(t, self.turns))
        return s["lots"][t - 1]

    def lot_name(self, i):
        return "the Cage" if i == self.cage() else f"Table {i + 1}"

    def need_on(self, turn):
        return self.C["STORM_NEED"] if turn >= self.C["MID_TURN"] else self.C["DUST_NEED"]

    # ------------------------------------------------------------ Vey's habit

    def habit(self, style, take, vey, last):
        C = self.C
        if style == "miser":
            raw = take + C["MISER_ADD"]
        elif style == "gambler":
            raw = max(C["BID_MIN"], vey // C["GAMBLE_DIV"])
        else:
            raw = last + C["SHADOW_ADD"] if last > 0 else C["SHADOW_OPEN"]
        return min(vey, raw)

    def consistent(self, style, e):
        pred = self.habit(style, e["take"], e["vey"], e["last"])
        return e["bid"] in (pred, min(e["vey"], pred + self.C["JITTER_ADD"]))

    def possible_styles(self, s):
        return [st for st in STYLES if all(self.consistent(st, e) for e in s["seen"])]

    def resample_hidden(self, s, rng):
        """Vey's habit is secret. Redraw it from the habits that explain every bid the player has seen."""
        cands = self.possible_styles(s) or list(STYLES)
        s["hidden"]["style"] = rng.choice(cands)

    # ------------------------------------------------------------ the executable spec

    def rule_tests(self):
        """One test per rule line, written from the sentence of the rule. They call the game's own apply and advance."""
        C = self.C
        N = C["RING"]
        UP = C["UPKEEP"]
        V = 1 + C["MISER_ADD"]  # a miser's bid on a lot with take 1

        def board(t, ring=None, **kw):
            s = t.fresh(seed=1, **kw)
            s["ring"] = [0] * (N + 1)
            for i, v in (ring or {}).items():
                s["ring"][i] = v
            return s

        def play(t, s, tn, lot, kind="bid", amount=1, dice=None, chances=None, args=None):
            s["_turn"] = tn
            s["lots"][tn - 1] = lot
            if kind == "bid":
                t.apply(s, "bid", {"amount": amount})
            else:
                t.apply(s, kind, args or {})
            return t.advance(s, turn=tn + 1, dice=dice, chances=[0.99] if chances is None else chances)

        def r1(t):
            homes = set()
            lo = hi = False
            for sd in range(1, 41):
                s = t.fresh(seed=sd)
                t.eq(len(s["ring"]), N + 1, "the ring has RING tables plus the Cage")
                t.eq((s["ring"].count(1), s["ring"].count(2)), (1, C["VEY_TABLES"]), "one table for you, VEY_TABLES for Vey")
                a = s["ring"].index(1)
                t.eq([i for i, v in enumerate(s["ring"]) if v == 2], sorted((a + N // 2 + k) % N for k in range(C["VEY_TABLES"])), "Vey's tables start opposite you")
                t.eq(s["ring"][N], 0, "the Cage starts open")
                t.eq(len(s["takes"]), N, "every table has a take")
                t.ok(all(1 <= x <= C["TAKE_MAX"] for x in s["takes"]), "take is 1 to TAKE_MAX")
                lo = lo or 1 in s["takes"]
                hi = hi or C["TAKE_MAX"] in s["takes"]
                t.eq((s["standing"], s["vey"]), (C["START"], C["START"]), "both start with START Standing")
                homes.add(a)
            t.ok(lo and hi, "takes span 1 to TAKE_MAX")
            t.ok(len(homes) > 1, "the starting tables vary with the seed")
            s = t.fresh()
            t.eq(self.turns, C["TURNS"], "the budget is TURNS")
            t.eq(len(s["lots"]), C["TURNS"], "one lot per turn on the docket")
            t.eq(s["lots"][C["MID_TURN"] - 1], N, "the Cage is the lot on the middle turn")
            t.eq(s["lots"][C["TURNS"] - 1], N, "and again on the last turn")
            first = s["lots"][: C["MID_TURN"] - 1]
            t.eq(len(set(first)), min(N, len(first)), "the docket does not repeat a table before the ring is done")
            t.ok(all(0 <= x < N for i, x in enumerate(s["lots"]) if i not in (C["MID_TURN"] - 1, C["TURNS"] - 1)), "other lots are ring tables")
            line = self.status_line(s)
            t.ok(f"Standing {s['standing']}" in line and f"Vey {s['vey']}" in line, "status shows both Standing")
            t.eq(s["last_bid"], 0, "a fresh game has no previous bid")
            lot0 = s["lots"][0]
            t.ok(f"Lot: {lot0 + 1} (take {s['takes'][lot0]})" in line, "status names the lot and its take")
            s["_turn"] = C["MID_TURN"]
            t.ok(f"Lot: Cage (take {C['CAGE_TAKE']})" in self.status_line(s), "status names the Cage on its turns")
            t.eq(self.visible(s)["tables"], {"you": 1, "vey": C["VEY_TABLES"]}, "visible shows the table counts")

        def r2(t):
            kw = dict(standing=10, vey=10, hidden__style="miser", takes=[1] * N)
            s = board(t, {4: 1, 2: 2}, **kw)
            ev = play(t, s, 1, 3, amount=V + 1)
            t.has(ev, f"you bid {V + 1}, Vey bids {V}", "bids are revealed together")
            t.eq(s["ring"][3], 1, "the higher bid wins the lot")
            t.eq(s["standing"], 10 - (V + 1) + 2 - UP, "the winner pays its bid; two tables of take 1 earn 2")
            t.eq(s["vey"], 10 + 1 + C["CATCHUP"] - UP, "the loser pays nothing")
            s = board(t, {4: 1, 2: 2}, **kw)
            self._hits.clear()
            play(t, s, 1, 3, amount=V)
            t.eq(s["ring"][3], 2, "a tie goes to Vey")
            t.ok("tie_to_vey" in self._hits, "a tie is noted")
            t.eq(s["vey"], 10 - V + 2 - UP, "Vey pays her tied bid")
            t.eq(s["standing"], 10 + 1 + C["CATCHUP"] - UP, "the tied loser pays nothing")
            if V - 1 >= C["BID_MIN"]:
                s = board(t, {4: 1, 2: 2}, **kw)
                self._hits.clear()
                play(t, s, 1, 3, amount=V - 1)
                t.eq(s["ring"][3], 2, "a lower bid loses")
                t.ok("tie_to_vey" not in self._hits, "no tie note when the bids differ")
            s = board(t, {4: 1, 2: 2}, **kw)
            self._hits.clear()
            play(t, s, 1, 3, amount=V + C["JITTER_ADD"], chances=[C["JITTER_P"] - 0.01])
            t.eq(s["ring"][3], 2, "a jittered bid ties and Vey wins it")
            t.ok("jitter" in self._hits, "a jittered bid is noted")
            s = board(t, {4: 1, 2: 2}, **kw)
            self._hits.clear()
            play(t, s, 1, 3, amount=V + C["JITTER_ADD"], chances=[C["JITTER_P"]])
            t.eq(s["ring"][3], 1, "chance at exactly JITTER_P is no jitter")
            t.ok("jitter" not in self._hits, "no jitter note")
            s = board(t, {4: 1}, standing=7)
            opt = [o for o in self.options(s) if o["id"] == "bid"][0]
            t.eq((opt["params"]["amount"]["min"], opt["params"]["amount"]["max"]), (C["BID_MIN"], 7), "bid from BID_MIN up to all you hold")
            t.ok(t.offered(s, "bid", amount=7) and not t.offered(s, "bid", amount=8), "never more than you hold")
            t.ok(not t.offered(s, "bid", amount=C["BID_MIN"] - 1), "at least BID_MIN")
            s = board(t, standing=C["BID_MIN"] - 1)
            t.ok("bid" not in t.ids(s), "no bid with nothing to bid")
            s = board(t, standing=C["BID_MIN"])
            t.ok("bid" in t.ids(s), "exactly BID_MIN is enough to bid")
            s = board(t, {4: 1}, standing=10, vey=0, hidden__style="miser")
            self._hits.clear()
            play(t, s, 1, 3, amount=C["BID_MIN"])
            t.eq(s["ring"][3], 1, "any bid beats a broke Vey")
            t.ok("vey_broke" in self._hits, "a broke Vey is noted")
            s = board(t, {4: 1}, standing=10, vey=1, hidden__style="miser")
            self._hits.clear()
            play(t, s, 1, 3, amount=C["BID_MIN"] + 1)
            t.ok("vey_broke" not in self._hits, "Vey with 1 Standing is not broke")
            def label(st):
                return [o["label"] for o in self.options(st) if o["id"] == "bid"][0]
            s = board(t, {3: 1, 7: 2}, standing=10)
            s["lots"][0] = 3
            t.ok("yours" in label(s) and "no convoy" in label(s), "the label says the table is yours")
            s = board(t, {4: 1, 7: 2}, standing=10)
            s["lots"][0] = 3
            t.ok("open" in label(s) and "safe route" in label(s), "the label says the route is safe")
            s = board(t, {5: 1, 3: 2}, standing=10)
            s["lots"][0] = 3
            t.ok("Vey's" in label(s) and f"dust route, roll {C['DUST_NEED']}+" in label(s), "the label shows the dust roll")
            s["_turn"] = C["MID_TURN"]
            s["lots"][C["MID_TURN"] - 1] = 3
            t.ok(f"roll {C['STORM_NEED']}+" in label(s), "and the storm roll from the middle turn")
            s = t.fresh(seed=3)
            lot = s["lots"][0]
            t.eq(self.lot_of(s), lot, "the lot is the first on the docket")
            s["_turn"] = 2
            t.eq(self.lot_of(s), s["lots"][1], "the next turn brings the next lot")

        def r3(t):
            lot = 3
            kw = dict(standing=10, vey=10, hidden__style="gambler", takes=[1] * N, last_bid=7)
            s = board(t, {6: 1, 2: 2}, **kw)
            s["lots"][0] = lot
            t.ok(t.offered(s, "sit"), "sitting out is always offered")
            self._hits.clear()
            t.apply(s, "sit")
            t.eq(s["standing"], 10 + C["SIT_GAIN"], "sitting out gains SIT_GAIN at once")
            t.ok("sit_out" in self._hits, "sitting out is noted")
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["ring"][lot], 2, "Vey wins the lot")
            t.eq(s["vey"], 10 - C["SIT_PRICE"] + 2 - UP, "Vey pays SIT_PRICE, not her habit bid, and earns two tables")
            t.eq(s["standing"], 10 + C["SIT_GAIN"] + 1 + C["CATCHUP"] - UP, "your own dusk follows")
            t.eq(s["seen"], [], "you learn nothing of her habit when you sit out")
            t.eq(s["last_bid"], 0, "a sat-out turn leaves no bid for her to copy")
            s = board(t, {6: 1, 2: 2}, **dict(kw, vey=0))
            s["lots"][0] = lot
            t.apply(s, "sit")
            t.advance(s, turn=2, chances=[0.99])
            t.eq(s["ring"][lot], 2, "a broke Vey still wins the lot, paying all she has")
            t.eq(s["vey"], 0, "and stays at 0")
            s = board(t, {6: 1, 2: 2}, **dict(kw, standing=C["BID_MIN"] - 1))
            t.eq(t.ids(s), ["sit"], "with nothing to bid you can still sit out")

        def r4(t):
            lot = 3
            kw = dict(standing=10, vey=10, hidden__style="miser", takes=[1] * N)
            for mine in ((lot - 1) % N, (lot + 1) % N, N):
                s = board(t, {mine: 1, 7: 2}, **kw)
                play(t, s, 1, lot, amount=8, dice=[1])
                t.eq(s["ring"][lot], 1, f"a lot touching {mine} is safe without a roll")
            for mine in ((lot + 2) % N, (lot - 2) % N):
                s = board(t, {mine: 1, 7: 2}, **kw)
                play(t, s, 1, lot, amount=8, dice=[C["DUST_NEED"] - 1])
                t.eq(s["ring"][lot], 0, "a failed roll loses the convoy")
                t.eq(s["standing"], 10 - 8 + 1 - UP, "the bid is paid even when the convoy is lost")
                s = board(t, {mine: 1, 7: 2}, **kw)
                self._hits.clear()
                ev = play(t, s, 1, lot, amount=8, dice=[C["DUST_NEED"]])
                t.eq(s["ring"][lot], 1, "a roll of DUST_NEED arrives")
                t.eq(s["standing"], 10 - 8 + 2 - UP, "two tables earn 2 after the bid")
                t.has(ev, f"roll {C['DUST_NEED']} (need {C['DUST_NEED']}+)", "the roll is shown")
                t.ok("convoy_lost" not in self._hits, "an arrived convoy is not a lost one")
            s = board(t, {5: 1, 7: 2}, **kw)
            self._hits.clear()
            ev = play(t, s, 1, lot, amount=8, dice=[C["DUST_NEED"]])
            t.ok("steal" not in self._hits, "taking an open table is not a steal")
            t.has(ev, "Your convoy", "the event names your convoy")
            s = board(t, {5: 1, 7: 2}, **kw)
            ev = play(t, s, 1, lot, amount=C["BID_MIN"], dice=[C["DUST_NEED"]])
            t.has(ev, "Vey's convoy", "the event names Vey's convoy")
            top = 0
            for sd in range(1, 121):
                s = board(t, {5: 1, 7: 2}, **kw)
                s["lots"][0] = lot
                t.apply(s, "bid", {"amount": 8})
                ev = t.advance(s, turn=2, seed=sd)
                for e in ev:
                    if "convoy crosses" in e:
                        top = max(top, int(e.split("roll ")[1].split(" ")[0]))
            t.eq(top, 6, "the convoy roll is a six-sided die")
            s = board(t, {5: 1, 3: 2}, **kw)
            self._hits.clear()
            play(t, s, 1, lot, amount=8, dice=[C["DUST_NEED"] - 1])
            t.eq(s["ring"][lot], 2, "a lost convoy leaves the lot with its old holder")
            t.ok("convoy_lost" in self._hits and "steal" not in self._hits, "a lost raid is noted")
            s = board(t, {5: 1, 3: 2}, **kw)
            self._hits.clear()
            play(t, s, 1, lot, amount=8, dice=[C["DUST_NEED"]])
            t.eq(s["ring"][lot], 1, "a raid that arrives takes the lot")
            t.ok("steal" in self._hits, "taking a held table is a steal")
            s = board(t, {3: 1, 7: 2}, **kw)
            self._hits.clear()
            ev = play(t, s, 1, lot, amount=8, dice=[1])
            t.eq(s["ring"][lot], 1, "a table you hold stays yours")
            t.ok("defend" in self._hits, "renewing your own table is noted")
            t.ok(not any("dust" in e for e in ev), "no convoy is needed for a table you hold")
            t.eq(s["standing"], 10 - 8 + 1 - UP, "the renewal bid is paid")
            s = board(t, {7: 2}, **kw)
            play(t, s, 1, lot, amount=C["BID_MIN"], dice=[C["DUST_NEED"] - 1])
            t.eq(s["ring"][lot], 0, "Vey's convoy is lost on a failed roll too")
            t.eq(s["vey"], 10 - V + 1 - UP, "Vey still pays her bid")
            s = board(t, {7: 2}, **kw)
            play(t, s, 1, lot, amount=C["BID_MIN"], dice=[C["DUST_NEED"]])
            t.eq(s["ring"][lot], 2, "Vey's convoy arrives on a roll of DUST_NEED")
            s = board(t, {2: 2}, **kw)
            play(t, s, 1, lot, amount=C["BID_MIN"], dice=[1])
            t.eq(s["ring"][lot], 2, "Vey is safe next to her own table")
            s = board(t, {N - 1: 1}, **kw)
            play(t, s, 1, 0, amount=8, dice=[1])
            t.eq(s["ring"][0], 1, "the ring wraps: table 1 touches the last table")
            s = board(t, {0: 1}, **kw)
            play(t, s, 1, N - 1, amount=8, dice=[1])
            t.eq(s["ring"][N - 1], 1, "and the last table touches table 1")

        def r5(t):
            tk = [2, 1, 1, 1, 3, 1, 1, 1]
            s = board(t, {0: 1, 4: 2}, standing=10, vey=10, takes=tk, last_bid=7)
            self._hits.clear()
            t.advance(s, turn=2)
            t.eq(s["last_bid"], 0, "a turn without a bid leaves no bid on record")
            t.eq((s["standing"], s["vey"]), (10 + 2 - UP, 10 + 3 - UP), "equal tables: takes and upkeep only")
            t.ok("catchup" not in self._hits, "no catch-up when level")
            s = board(t, {0: 1, 1: 1, 4: 2}, standing=10, vey=10, takes=tk)
            self._hits.clear()
            t.advance(s, turn=2)
            t.eq((s["standing"], s["vey"]), (10 + 3 - UP, 10 + 3 + C["CATCHUP"] - UP), "the side with fewer tables gains CATCHUP")
            t.ok("catchup" in self._hits, "catch-up is noted")
            s = board(t, {0: 1, 4: 2, 5: 2}, standing=10, vey=10, takes=tk)
            t.advance(s, turn=2)
            t.eq((s["standing"], s["vey"]), (10 + 2 + C["CATCHUP"] - UP, 10 + 4 - UP), "you gain CATCHUP when you hold fewer")
            s = board(t, {N: 1, 4: 2}, standing=10, vey=10, takes=tk)
            t.advance(s, turn=2)
            t.eq(s["standing"], 10 + C["CAGE_TAKE"] - UP, "the Cage earns CAGE_TAKE")
            t.eq(s["vey"], 10 + 3 + (C["CATCHUP"] if C["CAGE_POINTS"] > 1 else 0) - UP, "the Cage counts as CAGE_POINTS tables for the catch-up")
            vt = [4, 5, 6, 7][: C["CAGE_POINTS"]]
            s = board(t, {N: 1, **{i: 2 for i in vt}}, standing=10, vey=10, takes=[1] * N)
            t.advance(s, turn=2)
            t.eq(s["standing"], 10 + C["CAGE_TAKE"] - UP, "equal points: no catch-up for you")
            t.eq(s["vey"], 10 + len(vt) - UP, "equal points: no catch-up for Vey")
            tk2 = [1, 2, 2, 1, 1, 1, 1, 1]
            s = board(t, {0: 1, 1: 1, 2: 1, 3: 1, 5: 2}, standing=10, vey=10, takes=tk2)
            t.advance(s, turn=2)
            best = sum(sorted([1, 2, 2, 1], reverse=True)[: C["STAFF"]])
            t.eq(s["standing"], 10 + best - UP, "only the STAFF best takes pay")
            t.eq(s["vey"], 10 + 1 + C["CATCHUP"] - UP, "the single table pays its take")
            s = board(t, {0: 1}, standing=UP - 2 - 1, vey=10, takes=tk)
            t.advance(s, turn=2)
            t.eq(s["standing"], -1, "Standing may fall below 0")
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "below 0 after dusk loses")
            s = board(t, {0: 1}, standing=UP - 2, vey=10, takes=tk)
            t.advance(s, turn=2)
            t.eq(s["standing"], 0, "exactly 0 after dusk")
            t.ok(self.check_end(s) is None, "0 is still alive")
            s = board(t, {4: 2}, standing=10, vey=1, takes=[1] * N)
            t.advance(s, turn=2)
            t.eq(s["vey"], 0, "Vey cannot fall below 0")
            s = board(t, {0: 1, 4: 2}, standing=10, vey=10, takes=tk)
            s2, ev = t.step(s, "sit")
            t.eq(s2["_turn"], 2, "one action then dusk ends the turn")

        def r6(t):
            big = dict(vey=50, standing=20)
            for style, lot, take, vey, last, want in (
                ("miser", 0, 1, 50, 0, 1 + C["MISER_ADD"]),
                ("miser", 1, 2, 50, 9, 2 + C["MISER_ADD"]),
                ("miser", 1, 2, 1, 0, 1),
                ("gambler", 0, 1, 50, 9, 50 // C["GAMBLE_DIV"]),
                ("gambler", 0, 1, 11, 0, 11 // C["GAMBLE_DIV"]),
                ("gambler", 0, 1, C["GAMBLE_DIV"] - 1, 0, max(C["BID_MIN"], 0)),
                ("shadow", 0, 1, 50, 5, 5 + C["SHADOW_ADD"]),
                ("shadow", 0, 1, 50, 0, C["SHADOW_OPEN"]),
                ("shadow", 0, 1, 3, 9, 3),
                ("shadow", 0, 1, 50, 1, 1 + C["SHADOW_ADD"]),
            ):
                s = board(t, {4: 2}, takes=[1, 2] + [1] * (N - 2), hidden__style=style, last_bid=last, **dict(big, vey=vey))
                play(t, s, 1, lot, amount=1, dice=[6])
                e = s["seen"][-1]
                t.eq((e["bid"], e["take"], e["vey"], e["last"]), (want, take, vey, last), f"{style} habit")
            s = board(t, {4: 2}, takes=[1] * N, hidden__style="miser", **big)
            play(t, s, 1, 0, amount=1, dice=[6], chances=[C["JITTER_P"] - 0.01])
            t.eq(s["seen"][-1]["bid"], 1 + C["MISER_ADD"] + C["JITTER_ADD"], "one turn in a few she bids JITTER_ADD more")
            s = board(t, {4: 2}, takes=[1] * N, hidden__style="miser", **big)
            play(t, s, 1, 0, amount=1, dice=[6], chances=[C["JITTER_P"]])
            t.eq(s["seen"][-1]["bid"], 1 + C["MISER_ADD"], "no jitter at exactly JITTER_P")
            s = board(t, {4: 2}, takes=[1] * N, hidden__style="miser", **dict(big, vey=2))
            play(t, s, 1, 0, amount=1, dice=[6], chances=[0.0])
            t.eq(s["seen"][-1]["bid"], 2, "she cannot bid more than she holds, jitter or not")
            s = board(t, {4: 2}, takes=[1] * N, hidden__style="miser", **dict(big, vey=0))
            play(t, s, 1, 0, amount=1, dice=[6], chances=[0.0])
            t.eq(s["seen"][-1]["bid"], 0, "a broke Vey bids nothing")
            e = {"take": 1, "vey": 50, "last": 0, "bid": 1 + C["MISER_ADD"]}
            t.ok(self.consistent("miser", e), "a habit bid is consistent")
            t.ok(self.consistent("miser", dict(e, bid=e["bid"] + C["JITTER_ADD"])), "a jittered bid is consistent")
            t.ok(not self.consistent("miser", dict(e, bid=e["bid"] + C["JITTER_ADD"] + 1)), "two over is not")
            t.ok(not self.consistent("miser", dict(e, bid=e["bid"] - 1)), "under is not")
            t.eq(self.possible_styles({"seen": [dict(e, bid=50)]}), [], "no habit explains an impossible bid")
            t.ok("miser" in self.possible_styles({"seen": [e]}), "the miser explains a miser's bid")
            jit = 0
            for sd in range(1, 401):
                s = board(t, {4: 2}, takes=[1] * N, hidden__style="miser", **big)
                s["lots"][0] = 0
                t.apply(s, "bid", {"amount": 1})
                t.advance(s, turn=2, seed=sd, dice=[6])
                jit += s["seen"][-1]["bid"] > 1 + C["MISER_ADD"]
            t.ok(abs(jit / 400 - C["JITTER_P"]) < 0.08, f"jitter should hit about {C['JITTER_P']:.0%} of turns, got {jit / 400:.0%}")
            s = board(t, {4: 2}, takes=[1] * N, hidden__style="shadow", **big)
            s["lots"][0] = 0
            s["lots"][1] = 1
            s, _ = t.step(s, "bid", {"amount": 5})
            t.eq(s["last_bid"], 5, "your bid is remembered")
            s, _ = t.step(s, "bid", {"amount": 3})
            t.eq(s["seen"][-1]["last"], 5, "she answers the previous turn's bid")
            t.ok(s["seen"][-1]["bid"] in (5 + C["SHADOW_ADD"], 5 + C["SHADOW_ADD"] + C["JITTER_ADD"]), "and bids it plus SHADOW_ADD")
            t.eq(s["hidden"]["style"], "shadow", "the habit never changes")
            t.ok("shadow" not in str(self.visible(s)) and "miser" not in str(self.visible(s)), "the habit is not shown")
            t.eq(len(s["seen"]), 2, "each revealed bid is on record")

        def r7(t):
            kw = dict(standing=10, vey=10, hidden__style="miser", takes=[1] * N)
            s = t.fresh(seed=2)
            t.eq(s["lots"][C["MID_TURN"] - 1], N, "the Cage is the lot on the middle turn")
            s["_turn"] = C["MID_TURN"]
            lab = [o["label"] for o in self.options(s) if o["id"] == "bid"][0]
            t.ok("the Cage" in lab and f"take {C['CAGE_TAKE']}" in lab, "the bid on that turn is for the Cage")
            s = board(t, {5: 1, 7: 2}, **kw)
            play(t, s, C["MID_TURN"] - 1, 3, amount=8, dice=[C["DUST_NEED"]])
            t.eq(s["ring"][3], 1, "before the middle turn DUST_NEED is enough")
            s = board(t, {5: 1, 7: 2}, **kw)
            play(t, s, C["MID_TURN"], 3, amount=8, dice=[C["STORM_NEED"] - 1])
            t.eq(s["ring"][3], 0, "from the middle turn STORM_NEED is required")
            s = board(t, {5: 1, 7: 2}, **kw)
            play(t, s, C["MID_TURN"], 3, amount=8, dice=[C["STORM_NEED"]])
            t.eq(s["ring"][3], 1, "STORM_NEED arrives")
            s = board(t, {7: 2}, **kw)
            play(t, s, C["MID_TURN"], N, amount=8, dice=[C["STORM_NEED"] - 1])
            t.eq(s["ring"][N], 0, "the Cage needs a roll when you hold no table")
            s = board(t, {7: 2}, **kw)
            play(t, s, C["MID_TURN"], N, amount=8, dice=[C["STORM_NEED"]])
            t.eq(s["ring"][N], 1, "and arrives on STORM_NEED")
            s = board(t, {5: 1, 7: 2}, **kw)
            play(t, s, C["MID_TURN"], N, amount=8, dice=[1])
            t.eq(s["ring"][N], 1, "with any table the Cage is safe")
            self._hits.clear()
            s = board(t, {5: 1, 7: 2}, **kw)
            ev = t.advance(s, turn=C["MID_TURN"], chances=[0.99])
            t.ok("storm" in self._hits and "cage" in self._hits, "the dust season and the Cage are announced")
            t.has(ev, "dust season", "the storm is announced")
            t.ok("finale" not in self._hits, "no closing time at the middle turn")
            self._hits.clear()
            s = board(t, {5: 1, 7: 2}, **kw)
            t.advance(s, turn=C["MID_TURN"] - 1, chances=[0.99])
            t.ok("storm" not in self._hits and "cage" not in self._hits, "not before")
            t.advance(s, turn=C["MID_TURN"] + 1, chances=[0.99])
            t.ok("storm" not in self._hits and "cage" not in self._hits, "and not after")
            self._hits.clear()
            ev = t.advance(s, turn=C["TURNS"], chances=[0.99])
            t.ok("finale" in self._hits, "closing time is noted on the last turn")
            t.has(ev, "closing time", "closing time is announced")
            t.ok("storm" not in self._hits, "the dust season is not announced twice")
            self._hits.clear()
            t.advance(s, turn=C["TURNS"] - 1, chances=[0.99])
            t.ok("finale" not in self._hits, "no closing time before the last turn")
            s["_turn"] = C["TURNS"]
            lab = [o["label"] for o in self.options(s) if o["id"] == "bid"][0]
            t.ok("the Cage" in lab, "the last lot is the Cage")
            s = board(t, {5: 1, 7: 2}, **kw)
            play(t, s, C["TURNS"], N, amount=8, dice=[C["STORM_NEED"] - 1])
            t.eq(s["ring"][N], 1, "the Cage is safe with a table of your own, even in the dust season")

        def r8(t):
            kw = dict(standing=C["AUDIT_COST"], vey=10, hidden__style="miser", takes=[1] * N)
            s = board(t, {4: 2, 5: 2, 0: 1}, **kw)
            s["_turn"] = C["AUDIT_TURN"] - 1
            t.ok(not t.offered(s, "audit", table=4), "not before AUDIT_TURN")
            s["_turn"] = C["AUDIT_TURN"]
            t.ok(t.offered(s, "audit", table=4) and t.offered(s, "audit", table=5), "offered from AUDIT_TURN")
            t.ok(not t.offered(s, "audit", table=0), "only Vey's tables can be audited")
            t.ok(not t.offered(s, "audit", table=N), "an open Cage cannot be audited")
            s["standing"] = C["AUDIT_COST"] - 1
            t.ok("audit" not in t.ids(s), "needs AUDIT_COST Standing")
            s = board(t, {0: 1}, **kw)
            s["_turn"] = C["AUDIT_TURN"]
            t.ok("audit" not in t.ids(s), "nothing to audit when Vey holds no table")
            s = board(t, {4: 2, 5: 2, 0: 1}, **kw)
            self._hits.clear()
            lot = 3
            s["lots"][C["AUDIT_TURN"] - 1] = lot
            s["_turn"] = C["AUDIT_TURN"]
            s["last_bid"] = 6
            t.apply(s, "audit", {"table": 4})
            t.eq(s["standing"], 0, "the audit costs AUDIT_COST")
            t.eq(s["ring"][4], 0, "the table is stripped")
            t.eq(s["ring"][5], 2, "only that one")
            t.ok("audit" in self._hits, "the audit is noted")
            t.ok(s["audit_used"], "once only")
            t.advance(s, turn=C["AUDIT_TURN"] + 1, chances=[0.0])
            t.eq(s["ring"][lot], 0, "the lot is withdrawn: nobody wins it")
            t.eq(s["seen"], [], "no bids were revealed")
            t.eq(s["last_bid"], 0, "an audit turn leaves no bid for her to copy")
            t.eq(s["vey"], 10 + 1 - UP, "Vey earns the one table she kept, and pays upkeep")
            s["standing"] = 50
            s["_turn"] = C["AUDIT_TURN"] + 1
            t.ok("audit" not in t.ids(s), "the audit is once per game")
            s = board(t, {4: 2, 5: 2, 0: 1}, **kw)
            s["lots"][C["AUDIT_TURN"] - 1] = 4
            s["_turn"] = C["AUDIT_TURN"]
            ev = t.apply(s, "audit", {"table": 4})
            t.has(ev, "stripped from Vey and withdrawn", "auditing the lot itself says so")
            t.eq(s["ring"][4], 0, "the lot's own table is stripped")
            s = board(t, {N: 1}, standing=5, vey=10)
            s["_turn"] = C["TURNS"]
            t.ok(self.check_end(s) is None, "the last turn is still played")
            s["_turn"] = C["TURNS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "more table points after the last turn wins (Vey has none)")
            vt = [4, 5, 6, 7][: C["CAGE_POINTS"]]
            s = board(t, {N: 1, **{i: 2 for i in vt}}, standing=5, vey=10)
            s["_turn"] = C["TURNS"] + 1
            t.eq(self.check_end(s)["result"], "loss", "a tie goes to Vey")
            s = board(t, {N: 1, **{i: 2 for i in vt[:-1]}}, standing=5, vey=10)
            s["_turn"] = C["TURNS"] + 1
            t.eq(self.check_end(s)["result"], "win", "one table ahead wins")
            s = board(t, {N: 1}, standing=-1, vey=10)
            s["_turn"] = C["TURNS"] + 1
            t.eq(self.check_end(s)["result"], "loss", "a revoked licence loses even when ahead")
            s = board(t, {4: 1}, standing=100, vey=100, takes=[1] * N)
            steps = 0
            while not s.get("_ended") and steps < 40:
                s, _ = t.step(s, "sit")
                steps += 1
            t.eq(steps, C["TURNS"], "exactly TURNS actions are played")
            t.eq(s["_turn"], C["TURNS"] + 1, "the turn counter ends one past the budget")

        return [
            (1, "ring and start", r1), (2, "bids", r2), (3, "sit out", r3), (4, "convoy", r4),
            (5, "dusk", r5), (6, "Vey's habit", r6), (7, "dust season and Cage", r7), (8, "audit and ending", r8),
        ]

    # ------------------------------------------------------------ contract

    def init_state(self, rng):
        C = self.C
        n = C["RING"]
        takes = [rng.d(C["TAKE_MAX"]) for _ in range(n)]
        home = rng.d(n) - 1
        ring = [0] * (n + 1)
        ring[home] = 1
        for k in range(C["VEY_TABLES"]):
            ring[(home + n // 2 + k) % n] = 2
        stream = []
        while len(stream) < C["TURNS"]:
            perm = list(range(n))
            rng.shuffle(perm)
            stream += perm
        lots = []
        for t in range(1, C["TURNS"] + 1):
            lots.append(n if t in (C["MID_TURN"], C["TURNS"]) else stream.pop(0))
        return {
            "standing": C["START"],
            "vey": C["START"],
            "ring": ring,
            "takes": takes,
            "lots": lots,
            "last_bid": 0,
            "audit_used": False,
            "pending": None,
            "seen": [],
            "hidden": {"style": rng.choice(STYLES)},
        }

    def options(self, s):
        C = self.C
        t = s["_turn"]
        lot = self.lot_of(s)
        name = self.lot_name(lot)
        take = self.take(s, lot)
        holder = s["ring"][lot]
        if holder == 1:
            route = "yours already, no convoy needed"
        elif self.safe(s, 1, lot):
            route = "safe route"
        else:
            route = f"dust route, roll {self.need_on(t)}+"
        o = []
        if s["standing"] >= C["BID_MIN"]:
            o.append({
                "id": "bid", "label": f"Seal a bid for {name} (take {take}, {OWNER_WORD[holder]}, {route})",
                "args": {}, "params": {"amount": {"min": C["BID_MIN"], "max": s["standing"], "step": 1}},
            })
        o.append({
            "id": "sit", "label": f"Sit out {name} (+{C['SIT_GAIN']} Standing, Vey wins it for {C['SIT_PRICE']})", "args": {},
        })
        theirs = [i for i, v in enumerate(s["ring"]) if v == 2]
        if t >= C["AUDIT_TURN"] and s["standing"] >= C["AUDIT_COST"] and not s["audit_used"] and theirs:
            o.append({
                "id": "audit", "label": f"Audit Vey (-{C['AUDIT_COST']} Standing): strip one of her tables, withdraw {name}",
                "args": {}, "params": {"table": {"choices": theirs}},
            })
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        lot = self.lot_of(s)
        if a == "bid":
            s["pending"] = {"kind": "bid", "amount": int(args["amount"])}
            ev.append(f"You seal a bid for {self.lot_name(lot)}.")
        elif a == "sit":
            s["standing"] += C["SIT_GAIN"]
            s["pending"] = {"kind": "sit", "amount": 0}
            self.hit("sit_out")
            ev.append(f"You sit out {self.lot_name(lot)}. Standing +{C['SIT_GAIN']}.")
        elif a == "audit":
            i = int(args["table"])
            s["standing"] -= C["AUDIT_COST"]
            s["ring"][i] = 0
            s["audit_used"] = True
            s["pending"] = {"kind": "audit", "amount": 0}
            self.hit("audit")
            if i == lot:
                ev.append(f"Audit: {self.lot_name(i)} is stripped from Vey and withdrawn. Standing -{C['AUDIT_COST']}.")
            else:
                ev.append(f"Audit: {self.lot_name(i)} is stripped from Vey and {self.lot_name(lot)} is withdrawn. Standing -{C['AUDIT_COST']}.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        t = s["_turn"] - 1
        lot = s["lots"][t - 1]
        p = s["pending"] or {"kind": "none", "amount": 0}
        mine = p["amount"]
        if p["kind"] in ("bid", "sit"):
            ev += self.auction(s, rng, lot, t, mine, p["kind"] == "sit")
        s["pending"] = None
        s["last_bid"] = mine
        gain, vgain = self.income(s, 1), self.income(s, 2)
        a, b = self.points(s, 1), self.points(s, 2)
        extra, vextra = 0, 0
        if a < b:
            extra = C["CATCHUP"]
            self.hit("catchup")
        elif b < a:
            vextra = C["CATCHUP"]
            self.hit("catchup")
        s["standing"] += gain + extra - C["UPKEEP"]
        s["vey"] = max(0, s["vey"] + vgain + vextra - C["UPKEEP"])
        ev.append(
            f"Dusk: your tables earn {gain}{f', catch-up {extra}' if extra else ''}, upkeep {C['UPKEEP']}. "
            f"Vey's tables earn {vgain}{f', catch-up {vextra}' if vextra else ''}. Standing {s['standing']}, Vey {s['vey']}."
        )
        nt = s["_turn"]
        if nt == C["MID_TURN"]:
            self.hit("storm")
            self.hit("cage")
            ev.append(f"Turn {nt}: the dust season begins, convoys now need {C['STORM_NEED']}+. The Cage itself is the lot.")
        if nt == C["TURNS"]:
            self.hit("finale")
            ev.append(f"Turn {nt}: closing time. The Cage is the lot once more.")
        return ev

    def auction(self, s, rng, lot, t, mine, sat):
        """Reveal both bids, pay the winner, send the convoy. Vey's habit lives here and nowhere else."""
        C = self.C
        ev = []
        name = self.lot_name(lot)
        take = self.take(s, lot)
        vey_has = s["vey"]
        if sat:
            vbid = min(vey_has, C["SIT_PRICE"])
        else:
            if vey_has <= 0:
                self.hit("vey_broke")
            raw = self.habit(s["hidden"]["style"], take, vey_has, s["last_bid"])
            if rng.chance(C["JITTER_P"]):
                self.hit("jitter")
                raw = min(vey_has, raw + C["JITTER_ADD"])
            vbid = raw
            s["seen"].append({"take": take, "vey": vey_has, "last": s["last_bid"], "bid": vbid})
            ev.append(f"Reveal for {name}: you bid {mine}, Vey bids {vbid}.")
        if sat:
            winner, price = 2, vbid
        elif mine > vbid:
            winner, price = 1, mine
        else:
            winner, price = 2, vbid
            if mine == vbid:
                self.hit("tie_to_vey")
                ev.append("A tie goes to Vey.")
        if winner == 1:
            s["standing"] -= price
            ev.append(f"You win {name} and pay {price}.")
        else:
            s["vey"] -= price
            ev.append(f"Vey wins {name} and pays {price}.")
        holder = s["ring"][lot]
        who = "Your" if winner == 1 else "Vey's"
        if holder == winner:
            self.hit("defend")
            ev.append(f"{who} hold on {name} is renewed.")
            return ev
        if self.safe(s, winner, lot):
            arrived = True
            ev.append(f"{who} convoy has a safe road to {name}.")
        else:
            arrived, txt = rng.check(self.need_on(t), 6, "convoy")
            ev.append(f"{who} convoy crosses the dust: {txt}.")
        if arrived:
            s["ring"][lot] = winner
            if holder != 0:
                self.hit("steal")
            ev.append(f"{name[0].upper() + name[1:]} now belongs to {'you' if winner == 1 else 'Vey'}.")
        else:
            self.hit("convoy_lost")
            ev.append(f"The convoy is lost; {name} stays as it was.")
        return ev

    def ring_text(self, s):
        n = self.C["RING"]
        return "".join(".YV"[v] for v in s["ring"][:n]) + " [" + ".YV"[s["ring"][n]] + "]"

    def status_line(self, s):
        lot = self.lot_of(s)
        lot_label = "Cage" if lot == self.cage() else str(lot + 1)
        return f"Standing {s['standing']} vs Vey {s['vey']} | Ring: {self.ring_text(s)} | Lot: {lot_label} (take {self.take(s, lot)})"

    def visible(self, s):
        v = {k: x for k, x in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "_seed")}
        lot = self.lot_of(s)
        v["lot"] = {"name": self.lot_name(lot), "take": self.take(s, lot), "holder": OWNER_WORD[s["ring"][lot]]}
        v["docket"] = [self.lot_name(i) for i in s["lots"]]
        v["tables"] = {"you": self.points(s, 1), "vey": self.points(s, 2)}
        return v

    def check_end(self, s):
        if s["standing"] < 0:
            return {"result": "loss", "reason": f"Standing fell to {s['standing']}; the Council revoked your licence"}
        if s["_turn"] > self.turns:
            a, b = self.points(s, 1), self.points(s, 2)
            if a > b:
                return {"result": "win", "reason": f"you hold {a} to Vey's {b}"}
            return {"result": "loss", "reason": f"you hold {a} to Vey's {b}; ties go to Vey"}
        return None

    # ------------------------------------------------------------ the sensible player

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        t = s["_turn"]
        lot = self.lot_of(s)
        left = self.turns - t + 1
        me, her = self.points(s, 1), self.points(s, 2)
        income = self.income(s, 1)
        behind = C["CATCHUP"] if me < her else 0
        theirs = [i for i, v in enumerate(s["ring"]) if v == 2]
        if "audit" in ids and theirs and me <= her and left <= 5:
            if s["standing"] - C["AUDIT_COST"] + income + behind - C["UPKEEP"] >= 0:
                best = max(theirs, key=lambda i: (self.points_of(i), self.take(s, i)))
                return {"id": "audit", "args": {"table": best}}
        take = self.take(s, lot)
        cands = [st for st in STYLES if all(self.consistent(st, e) for e in s["seen"])] or list(STYLES)
        preds = [self.habit(st, take, s["vey"], s["last_bid"]) for st in cands]
        if len(cands) == 1:
            target = preds[0] + C["JITTER_ADD"] + 1
        else:
            target = (sum(preds) + len(preds) - 1) // len(preds) + 1
        holder = s["ring"][lot]
        swing = self.points_of(lot) * (2 if holder == 2 else 1)
        arrive = 1.0
        if holder != 1 and not self.safe(s, 1, lot):
            arrive = (7 - self.need_on(t)) / 6
        worth = int((take * left // 2 + 3 * swing) * arrive)
        cap = s["standing"] + income + behind - C["UPKEEP"]
        if left <= 2:
            worth = max(worth, cap)
        cap = min(cap, s["standing"])
        if "bid" in ids and C["BID_MIN"] <= target <= min(worth, cap):
            return {"id": "bid", "args": {"amount": target}}
        if "bid" in ids and s["vey"] <= 0 and cap >= C["BID_MIN"]:
            return {"id": "bid", "args": {"amount": C["BID_MIN"]}}
        return "sit"


if __name__ == "__main__":
    run(G)
