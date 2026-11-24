"""Mirror Migration: a nature documentary on a chessboard (v2 contract).

A smuggler pawn owes the Bishop a season of tithe. Five files face the migration road. Each week you
build one thing, and the party of wild pieces crosses the file opposite it. Raise dens on all five
files and hold them through the Great Crossing.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

LETTERS = "abcdefgh"
CROSSING = 4  # queue marker for the Great Crossing; 0 to 3 are deck cards
CARD_NAMES = {0: "Pilgrims", 1: "Stragglers", 2: "Herd", 3: "Stampede", 4: "Great Crossing"}


class G(Game):
    name = "Mirror Migration"

    CONSTANTS = {
        "WEEKS": 16,
        "FILES": 5,
        "DIE": 6,
        "START_STANDING": 10,
        "DEN_COST": 3,
        "SNARE_COST": 1,
        "RUN_NEED": 4,
        "SCREEN_NEED": 3,
        "SCREEN_DENS": 3,
        "RUN_GAIN": 5,
        "RUN_FAIL": 1,
        "BASE_NEED": 4,
        "NEED_MIN": 2,
        "NEED_MAX": 6,
        "DEN_DEF": 2,
        "ADJ_BONUS": 1,
        "SNARE_BONUS": 3,
        "HOLD_GAIN": 1,
        "CROSS_COST": 1,
        "PILGRIM_PAY": 3,
        "STIPEND": 1,
        "TITHE": 1,
        "TITHE_LATE": 2,
        "MID_WEEK": 9,
        "MID_BOOST": 1,
        "WRIT_COST": 12,
        "FINAL_STR": 5,
        "DEBT": 18,
        "_VIEW": 2,
        "_DECK": [0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3],
    }

    RULES = """
1. {FILES} files, lettered from a, face the road. Each week do one thing: raise a den on an empty file ({DEN_COST} Standing), lay one snare on a den's file ({SNARE_COST}), or run contraband.
2. A run rolls a d{DIE} for {RUN_NEED}+ ({SCREEN_NEED}+ with {SCREEN_DENS} or more dens) and pays +{RUN_GAIN} Standing; a miss pays +{RUN_FAIL}. You start with {START_STANDING} Standing.
3. Each week a party crosses the file opposite your latest build (a with e, b with d, c with c). If you run, it repeats last week's file; before week 1 that file is random.
4. This week's party and next week's are shown with a strength, drawn from a deck. Pilgrims are harmless and pay +{PILGRIM_PAY} Standing if the file they cross holds a den.
5. A den on the crossed file holds on a d{DIE} roll of {BASE_NEED} plus strength minus defense, from {NEED_MIN}+ to {NEED_MAX}+. Defense: {DEN_DEF}, +{ADJ_BONUS} per neighbouring den, +{SNARE_BONUS} for a snare. A hold pays +{HOLD_GAIN}.
6. A snare is used up when its den rolls to hold. A party that crosses an empty file, or breaks a den, costs {CROSS_COST} Standing, and a broken den is gone.
7. At dusk each den pays +{STIPEND} Standing and the Bishop takes {TITHE}. Below 0 Standing he forecloses and you lose. From week {MID_WEEK} the tithe is {TITHE_LATE} and every party but Pilgrims gains +{MID_BOOST} strength.
8. Once from week {MID_WEEK}, a {WRIT_COST}-Standing Writ turns that week's party back. Week {WEEKS} is the Great Crossing (strength {FINAL_STR}); after its dusk, win with a den on every file and {DEBT} Standing.
"""

    ACTIONS = ["den", "snare", "run", "writ"]
    TAGS = ["midpoint", "pilgrims", "hold", "den_lost", "snare_aid", "toll", "writ", "final", "screen"]
    TRACKED = ["standing", "files"]

    BOUNDS = {"standing": (-12, 150), "last": (0, 4), "dens": (0, 5), "snares": (0, 5)}
    REACH = {"standing": ("<=", -1), "dens": 5, "snares": 2, "surplus": 0}
    DERIVED = {
        "dens": lambda g, s: sum(c["d"] for c in s["files"]),
        "snares": lambda g, s: sum(c["s"] for c in s["files"]),
        "surplus": lambda g, s: s["standing"] - g.C["DEBT"],
    }
    GATES = {
        "den": {"standing": "DEN_COST", "_if": lambda g, s: any(not c["d"] for c in s["files"])},
        "snare": {"standing": "SNARE_COST", "_if": lambda g, s: any(c["d"] and not c["s"] for c in s["files"])},
        "writ": {"standing": "WRIT_COST", "_turn": "MID_WEEK", "!writ_used": 1},
    }

    @property
    def turns(self):
        return self.C["WEEKS"]

    # ------------------------------------------------------------------ helpers

    def _board(self, spec):
        """'.D.sB' -> a files list. D den, s snare, B both, . empty."""
        out = []
        for ch in spec:
            out.append({"d": 1 if ch in "DB" else 0, "s": 1 if ch in "sB" else 0})
        return out

    def _strength(self, card, week):
        C = self.C
        if card == CROSSING:
            return C["FINAL_STR"]
        if card == 0:
            return 0
        return card + (C["MID_BOOST"] if week >= C["MID_WEEK"] else 0)

    def _need(self, strength, defense):
        C = self.C
        return max(C["NEED_MIN"], min(C["NEED_MAX"], C["BASE_NEED"] + strength - defense))

    def _defense(self, files, f):
        C = self.C
        d = C["DEN_DEF"]
        for j in (f - 1, f + 1):
            if 0 <= j < len(files) and files[j]["d"]:
                d += C["ADJ_BONUS"]
        if files[f]["s"]:
            d += C["SNARE_BONUS"]
        return d

    def _mirror(self, f):
        return self.C["FILES"] - 1 - f

    def _tithe(self, week):
        C = self.C
        return C["TITHE_LATE"] if week >= C["MID_WEEK"] else C["TITHE"]

    def _board_text(self, files):
        out = ""
        for c in files:
            out += "B" if (c["d"] and c["s"]) else "D" if c["d"] else "s" if c["s"] else "."
        return out

    def _party_text(self, s):
        parts = []
        for i, card in enumerate(s["queue"]):
            parts.append(f"{CARD_NAMES[card]} {self._strength(card, s['_turn'] + i)}")
        return " / ".join(parts) if parts else "done"

    # ------------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        G_ = self

        def dusk(dens, week):
            return dens * C["STIPEND"] - G_._tithe(week)

        def r1(t):
            s = t.fresh()
            t.eq(len(s["files"]), C["FILES"], "five files")
            t.eq(G_._board_text(s["files"]), "." * C["FILES"], "an empty board at the start")
            t.eq(t.ids(s), ["den", "run"], "a den and a run on week 1; a snare needs a den")
            t.eq(s["standing"], C["START_STANDING"], "starting standing")
            s = t.fresh(standing=10)
            t.apply(s, "den", {"file": "c"})
            t.eq(s["standing"], 10 - C["DEN_COST"], "a den costs DEN_COST")
            t.eq(s["files"][2], {"d": 1, "s": 0}, "the den stands on file c")
            t.eq(s["last"], 2, "building on c is remembered")
            s = t.fresh(standing=10, files=G_._board("D...."))
            t.apply(s, "snare", {"file": "a"})
            t.eq(s["standing"], 10 - C["SNARE_COST"], "a snare costs SNARE_COST")
            t.eq(s["files"][0], {"d": 1, "s": 1}, "the snare lies beside the den on file a")
            t.eq(s["last"], 0, "laying a snare on a is remembered")
            # one den and one snare per file; a snare needs a den
            s = t.fresh(standing=10, files=G_._board("DB.D."))
            t.ok(not t.offered(s, "den", file="a"), "no second den on a file")
            t.ok(not t.offered(s, "den", file="b"), "no second den on a file with both")
            t.ok(t.offered(s, "den", file="c"), "an empty file takes a den")
            t.ok(t.offered(s, "den", file="e"), "another empty file takes a den")
            t.ok(not t.offered(s, "snare", file="b"), "no second snare on a file")
            t.ok(t.offered(s, "snare", file="a"), "a file with a den takes a snare")
            t.ok(t.offered(s, "snare", file="d"), "another file with a den takes a snare")
            t.ok(not t.offered(s, "snare", file="c"), "no snare on an empty file")
            t.ok(not t.offered(s, "snare", file="e"), "no snare on another empty file")
            s = t.fresh(standing=10, files=G_._board("DDDDD"))
            t.ok("den" not in t.ids(s), "no den option when every file has one")
            t.ok("snare" in t.ids(s), "snares remain when every file has a den")
            s = t.fresh(standing=10, files=G_._board("BBBBB"))
            t.ok("snare" not in t.ids(s), "no snare option when every file has one")
            # affordability edges
            s = t.fresh(standing=C["DEN_COST"] - 1)
            t.ok("den" not in t.ids(s), "a den one short is not offered")
            s = t.fresh(standing=C["DEN_COST"])
            t.ok("den" in t.ids(s), "exactly enough for a den is enough")
            s = t.fresh(standing=C["SNARE_COST"] - 1, files=G_._board("D...."))
            t.ok("snare" not in t.ids(s), "a snare one short is not offered")
            s = t.fresh(standing=C["SNARE_COST"], files=G_._board("D...."))
            t.ok("snare" in t.ids(s), "exactly enough for a snare is enough")
            t.ok("run" in t.ids(t.fresh(standing=0)), "a run is always possible")
            # one action ends the week
            s = t.fresh(standing=10)
            s, _ = t.step(s, "den", {"file": "a"})
            t.eq(s["_turn"], 2, "one action ends the week")

        def r2(t):
            s = t.fresh(standing=10, files=G_._board("D...."))
            t.apply(s, "run", dice=[C["RUN_NEED"]])
            t.eq(s["standing"], 10 + C["RUN_GAIN"], "a run at the needed roll pays RUN_GAIN")
            s = t.fresh(standing=10, files=G_._board("D...."))
            t.apply(s, "run", dice=[C["RUN_NEED"] - 1])
            t.eq(s["standing"], 10 + C["RUN_FAIL"], "a miss pays RUN_FAIL")
            few = "D" * (C["SCREEN_DENS"] - 1) + "." * (C["FILES"] - C["SCREEN_DENS"] + 1)
            many = "D" * C["SCREEN_DENS"] + "." * (C["FILES"] - C["SCREEN_DENS"])
            s = t.fresh(standing=10, files=G_._board(few))
            t.apply(s, "run", dice=[C["SCREEN_NEED"]])
            t.eq(s["standing"], 10 + C["RUN_FAIL"], "too few dens: the screened roll is not enough")
            s = t.fresh(standing=10, files=G_._board(many))
            self._hits.clear()
            t.apply(s, "run", dice=[C["SCREEN_NEED"]])
            t.eq(s["standing"], 10 + C["RUN_GAIN"], "enough dens: the screened roll pays")
            t.ok("screen" in self._hits, "a screened run is noted")
            s = t.fresh(standing=10, files=G_._board(many))
            t.apply(s, "run", dice=[C["SCREEN_NEED"] - 1])
            t.eq(s["standing"], 10 + C["RUN_FAIL"], "below the screened roll still misses")
            s = t.fresh(standing=10, files=G_._board(few))
            self._hits.clear()
            t.apply(s, "run", dice=[C["RUN_NEED"]])
            t.ok("screen" not in self._hits, "an unscreened run is not noted")
            s = t.fresh(last=3)
            t.apply(s, "run", dice=[1])
            t.eq(s["last"], 3, "a run does not change the remembered file")
            for spec, want in ((few, C["RUN_NEED"]), (many, C["SCREEN_NEED"])):
                s = t.fresh(standing=10, files=G_._board(spec))
                label = [o["label"] for o in self.options(s) if o["id"] == "run"][0]
                t.ok(f"roll {want}+" in label, f"the run label shows the real need {want}")

        def r3(t):
            for f in range(C["FILES"]):
                m = C["FILES"] - 1 - f
                spec = ["."] * C["FILES"]
                spec[m] = "D"
                s = t.fresh(standing=10, files=G_._board("".join(spec)), last=f, queue=[1, 1])
                ev = t.advance(s, turn=2, dice=[C["DIE"]])
                t.eq(s["standing"], 10 + C["HOLD_GAIN"] + dusk(1, 1), f"last {f}: the party crosses the opposite file {m}, the one with the den")
                t.has(ev, f"File {LETTERS[m]} faces", "the crossed file is named")
            # placing a den or a snare sets the mirror; a run keeps it
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[1, 1])
            t.apply(s, "den", {"file": "a"})
            t.eq(s["last"], 0, "the den on a is remembered")
            ev = t.advance(s, turn=2, dice=[C["DIE"]])
            t.eq(s["standing"], 10 - C["DEN_COST"] + C["HOLD_GAIN"] + dusk(2, 1), "a den on a meets the party on e")
            s = t.fresh(standing=10, files=G_._board("DD.D."), queue=[1, 1], last=4)
            t.apply(s, "snare", {"file": "d"})
            t.eq(s["last"], 3, "the snare on d is remembered")
            ev = t.advance(s, turn=2, dice=[C["DIE"]])
            t.eq(s["standing"], 10 - C["SNARE_COST"] + C["HOLD_GAIN"] + dusk(3, 1), "a snare on d meets the party on b")
            s = t.fresh(standing=10, files=G_._board("D...."), last=4, queue=[1, 1])
            t.apply(s, "run", dice=[1])
            t.eq(s["last"], 4, "a run keeps last as e")
            ev = t.advance(s, turn=2, dice=[C["DIE"]])
            t.eq(s["standing"], 10 + C["RUN_FAIL"] + C["HOLD_GAIN"] + dusk(1, 1), "after a run with last e the party crosses a")
            t.has(ev, "File a faces", "the crossed file is named")
            # the first file is random across seeds
            seen = set()
            for sd in range(1, 41):
                seen.add(t.fresh(seed=sd)["last"])
            t.eq(sorted(seen), list(range(C["FILES"])), "the opening file is random over every file")

        def r4(t):
            s = t.fresh()
            t.eq(len(s["queue"]), C["_VIEW"], "this week and next week are shown")
            st = G_.status_line(s)
            t.ok(CARD_NAMES[s["queue"][0]] in st, "the status shows this week's party")
            t.ok(CARD_NAMES[s["queue"][1]] in st, "the status shows next week's party")
            for sd in (1, 2, 3):
                s = t.fresh(seed=sd)
                t.eq(len(s["queue"]) + len(s["hidden"]["deck"]), C["WEEKS"] - 1, "one deck card for every week before the Crossing")
                t.eq(sorted(s["queue"] + s["hidden"]["deck"]), sorted(C["_DECK"]), "the deck holds its fixed mix")
            s = t.fresh(queue=[1, 1], hidden__deck=[])
            t.advance(s, turn=2)
            t.eq(len(s["queue"]), C["_VIEW"], "an empty deck still refills the view")
            t.eq(s["queue"][-1], 2, "an empty deck falls back to a Herd")
            # the deck refills one card a week, and ends with the Great Crossing
            s = t.fresh(queue=[1, 2], hidden__deck=[3, 2])
            t.advance(s, turn=2)
            t.eq(s["queue"], [2, 3], "the queue shifts and draws from the deck")
            t.eq(s["hidden"]["deck"], [2], "the deck loses the drawn card")
            s = t.fresh(queue=[1, 2], hidden__deck=[3])
            t.advance(s, turn=C["WEEKS"] - 1)
            t.eq(s["queue"], [2, CROSSING], "week WEEKS is the Great Crossing")
            s = t.fresh(queue=[1, CROSSING], hidden__deck=[])
            t.advance(s, turn=C["WEEKS"])
            t.eq(s["queue"], [CROSSING], "nothing is drawn after the Crossing is queued")
            s = t.fresh(queue=[CROSSING], hidden__deck=[])
            t.advance(s, turn=C["WEEKS"] + 1)
            t.eq(s["queue"], [], "the queue empties after the last week")
            # pilgrims: harmless, pay a den, spend no snare, cost nothing on an empty file
            s = t.fresh(standing=10, files=G_._board("D...."), queue=[0, 1], last=4)
            self._hits.clear()
            ev = t.advance(s, turn=2)
            t.eq(s["standing"], 10 + C["PILGRIM_PAY"] + dusk(1, 1), "pilgrims pay a den")
            t.ok(not any("roll" in e for e in ev), "pilgrims never roll")
            t.ok("pilgrims" in self._hits, "pilgrims are noted")
            s = t.fresh(standing=10, files=G_._board("B...."), queue=[0, 1], last=4)
            t.advance(s, turn=2)
            t.eq(s["files"][0], {"d": 1, "s": 1}, "pilgrims do not spring a snare")
            s = t.fresh(standing=10, files=G_._board(".D..."), queue=[0, 1], last=4)
            t.advance(s, turn=2)
            t.eq(s["standing"], 10 + dusk(1, 1), "pilgrims on an empty file cost nothing and pay nothing")
            s = t.fresh(standing=10, files=G_._board("....."), queue=[0, 1], last=4)
            t.advance(s, turn=C["MID_WEEK"] + 1)
            t.eq(s["standing"], 10 + dusk(0, C["MID_WEEK"]), "pilgrims stay at zero strength after the midpoint")
            s = t.fresh(standing=10, files=G_._board("D...."), queue=[0, 1], last=4)
            ev = t.advance(s, turn=C["MID_WEEK"] + 1)
            t.eq(s["standing"], 10 + C["PILGRIM_PAY"] + dusk(1, C["MID_WEEK"]), "pilgrims still pay after the midpoint")

        def r5(t):
            # a lone den vs a Herd (2) before the midpoint: need BASE + 2 - DEN_DEF
            need = C["BASE_NEED"] + 2 - C["DEN_DEF"]
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            ev = t.advance(s, turn=2, dice=[need])
            t.eq(s["standing"], 10 + C["HOLD_GAIN"] + dusk(1, 1), "a hold at the needed roll pays HOLD_GAIN")
            t.eq(s["files"][4]["d"], 1, "the den stands")
            t.has(ev, f"need {need}+", "the roll text shows the need")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            t.advance(s, turn=2, dice=[need - 1])
            t.eq(s["files"][4]["d"], 0, "a miss breaks the den")
            t.eq(s["standing"], 10 - C["CROSS_COST"] + dusk(0, 1), "a broken den costs CROSS_COST")
            # neighbours: one on each side
            need3 = max(C["NEED_MIN"], C["BASE_NEED"] + 3 - (C["DEN_DEF"] + 2 * C["ADJ_BONUS"]))
            s = t.fresh(standing=10, files=G_._board(".DDD."), queue=[3, 3], last=2)
            t.advance(s, turn=2, dice=[need3])
            t.eq(s["files"][2]["d"], 1, "two neighbours lend ADJ_BONUS each")
            s = t.fresh(standing=10, files=G_._board(".DDD."), queue=[3, 3], last=2)
            t.advance(s, turn=2, dice=[need3 - 1])
            t.eq(s["files"][2]["d"], 0, "one under the need with two neighbours is a miss")
            # one neighbour only
            need2 = max(C["NEED_MIN"], C["BASE_NEED"] + 3 - (C["DEN_DEF"] + C["ADJ_BONUS"]))
            s = t.fresh(standing=10, files=G_._board("DD..."), queue=[3, 3], last=4)
            t.advance(s, turn=2, dice=[need2])
            t.eq(s["files"][0]["d"], 1, "an edge den counts its one neighbour")
            s = t.fresh(standing=10, files=G_._board("DD..."), queue=[3, 3], last=4)
            t.advance(s, turn=2, dice=[need2 - 1])
            t.eq(s["files"][0]["d"], 0, "an edge den has no neighbour on the far side")
            # a neighbour two files away does not help
            s = t.fresh(standing=10, files=G_._board("D.D.."), queue=[3, 3], last=4)
            needf = max(C["NEED_MIN"], C["BASE_NEED"] + 3 - C["DEN_DEF"])
            t.advance(s, turn=2, dice=[needf - 1])
            t.eq(s["files"][0]["d"], 0, "a den two files away lends nothing")
            # snare adds SNARE_BONUS
            needs = max(C["NEED_MIN"], C["BASE_NEED"] + 3 - (C["DEN_DEF"] + C["SNARE_BONUS"]))
            s = t.fresh(standing=10, files=G_._board("....B"), queue=[3, 3], last=0)
            t.advance(s, turn=2, dice=[needs])
            t.eq(s["files"][4]["d"], 1, "a snare adds SNARE_BONUS")
            s = t.fresh(standing=10, files=G_._board("....B"), queue=[3, 3], last=0)
            t.advance(s, turn=2, dice=[needs - 1])
            t.eq(s["files"][4]["d"], 0, "one under the need with a snare is a miss")
            # clamps: never better than NEED_MIN, never worse than NEED_MAX
            s = t.fresh(standing=10, files=G_._board("BBBBB"), queue=[1, 1], last=2)
            t.advance(s, turn=2, dice=[C["NEED_MIN"] - 1])
            t.eq(s["files"][2]["d"], 0, "even full defense can miss")
            s = t.fresh(standing=10, files=G_._board("BBBBB"), queue=[1, 1], last=2)
            t.advance(s, turn=2, dice=[C["NEED_MIN"]])
            t.eq(s["files"][2]["d"], 1, "full defense holds on the best need")
            saved = C["BASE_NEED"]
            C["BASE_NEED"] = C["NEED_MAX"] + 3
            try:
                s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
                t.advance(s, turn=2, dice=[C["NEED_MAX"]])
                t.eq(s["files"][4]["d"], 1, "a roll of NEED_MAX always holds")
                s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
                t.advance(s, turn=2, dice=[C["NEED_MAX"] - 1])
                t.eq(s["files"][4]["d"], 0, "below NEED_MAX never holds")
            finally:
                C["BASE_NEED"] = saved
            # the midpoint boost applies from MID_WEEK, to the week it names
            needb = max(C["NEED_MIN"], C["BASE_NEED"] + 2 + C["MID_BOOST"] - C["DEN_DEF"])
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            t.advance(s, turn=C["MID_WEEK"] + 1, dice=[needb - 1])
            t.eq(s["files"][4]["d"], 0, "the party of week MID_WEEK is boosted")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            t.advance(s, turn=C["MID_WEEK"] + 1, dice=[needb])
            t.eq(s["files"][4]["d"], 1, "the boosted party can still be held")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            t.advance(s, turn=C["MID_WEEK"], dice=[need])
            t.eq(s["files"][4]["d"], 1, "the party of the week before MID_WEEK is not boosted")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[2, 2], last=0)
            t.advance(s, turn=C["MID_WEEK"], dice=[need - 1])
            t.eq(s["files"][4]["d"], 0, "the week before MID_WEEK is unboosted but still a miss under its need")

        def r6(t):
            # a snare beside a den is used up on a hold and on a break
            s = t.fresh(standing=10, files=G_._board("....B"), queue=[1, 1], last=0)
            self._hits.clear()
            t.advance(s, turn=2, dice=[6])
            t.eq(s["files"][4], {"d": 1, "s": 0}, "the snare is used up on a hold")
            t.ok("snare_aid" in self._hits, "a snare that adds to a den is noted")
            s = t.fresh(standing=10, files=G_._board("....B"), queue=[3, 3], last=0)
            t.advance(s, turn=2, dice=[1])
            t.eq(s["files"][4], {"d": 0, "s": 0}, "the den and the snare are gone on a break")
            # a snare elsewhere is untouched
            s = t.fresh(standing=10, files=G_._board("B...B"), queue=[3, 3], last=0)
            t.advance(s, turn=2, dice=[6])
            t.eq((s["files"][0]["s"], s["files"][4]["s"]), (1, 0), "only the crossed file's snare is used")
            # an empty file costs a toll
            s = t.fresh(standing=10, files=G_._board("....."), queue=[1, 1], last=0)
            self._hits.clear()
            t.advance(s, turn=2)
            t.eq(s["standing"], 10 - C["CROSS_COST"] + dusk(0, 1), "an empty file costs CROSS_COST")
            t.ok("toll" in self._hits, "a toll is noted")
            # a broken den is gone and costs CROSS_COST, and the neighbours stay
            s = t.fresh(standing=10, files=G_._board("..DDD"), queue=[3, 3], last=0)
            self._hits.clear()
            t.advance(s, turn=2, dice=[1])
            t.eq(G_._board_text(s["files"]), "..DD.", "the broken den is removed")
            t.eq(s["standing"], 10 - C["CROSS_COST"] + dusk(2, 1), "a broken den costs CROSS_COST")
            t.ok("den_lost" in self._hits, "a lost den is noted")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[1, 1], last=0)
            self._hits.clear()
            t.advance(s, turn=2, dice=[6])
            t.ok("hold" in self._hits, "a hold is noted")

        def r7(t):
            s = t.fresh(standing=10, files=G_._board("DD.D."), queue=[0, 1], last=2)
            t.advance(s, turn=2)
            t.eq(s["standing"], 10 + 3 * C["STIPEND"] - C["TITHE"], "each den pays STIPEND, then the tithe")
            s = t.fresh(standing=10, files=G_._board("....."), queue=[0, 1], last=4)
            t.advance(s, turn=C["MID_WEEK"])
            t.eq(s["standing"], 10 - C["TITHE"], "the tithe is TITHE through the week before MID_WEEK")
            s = t.fresh(standing=10, files=G_._board("....."), queue=[0, 1], last=4)
            t.advance(s, turn=C["MID_WEEK"] + 1)
            t.eq(s["standing"], 10 - C["TITHE_LATE"], "the tithe is TITHE_LATE from week MID_WEEK")
            s = t.fresh(standing=10, files=G_._board("....."), queue=[0, 1], last=4)
            self._hits.clear()
            ev = t.advance(s, turn=C["MID_WEEK"])
            t.ok("midpoint" in self._hits, "the midpoint is announced when week MID_WEEK begins")
            t.has(ev, f"Week {C['MID_WEEK']}:", "the announcement names the week")
            s = t.fresh(standing=10, files=G_._board("....."), queue=[0, 1], last=4)
            self._hits.clear()
            t.advance(s, turn=C["MID_WEEK"] - 1)
            t.ok("midpoint" not in self._hits, "no announcement a week early")
            # foreclosure: below zero loses, zero lives
            s = t.fresh(standing=-1)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "Standing below zero forecloses")
            s = t.fresh(standing=0)
            t.ok(self.check_end(s) is None, "exactly zero Standing is alive")
            s = t.fresh(standing=C["TITHE"] - 1, files=G_._board("....."), queue=[0, 1], last=4)
            t.advance(s, turn=2)
            end = self.check_end(s)
            t.ok(s["standing"] == -1 and end and end["result"] == "loss", "the tithe can foreclose at dusk")
            s = t.fresh(standing=C["TITHE"], files=G_._board("....."), queue=[0, 1], last=4)
            t.advance(s, turn=2)
            t.ok(s["standing"] == 0 and self.check_end(s) is None, "ending dusk at zero is alive")
            # the stipend counts dens after the clash
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[3, 3], last=0)
            t.advance(s, turn=2, dice=[1])
            t.eq(s["standing"], 10 - C["CROSS_COST"] + 0 * C["STIPEND"] - C["TITHE"], "a den lost in the clash pays no stipend")

        def r8(t):
            # the Writ: from MID_WEEK, once, priced
            s = t.fresh(standing=C["WRIT_COST"] + 5)
            s["_turn"] = C["MID_WEEK"] - 1
            t.ok("writ" not in t.ids(s), "no Writ before MID_WEEK")
            s["_turn"] = C["MID_WEEK"]
            t.ok("writ" in t.ids(s), "the Writ opens at MID_WEEK")
            s = t.fresh(standing=C["WRIT_COST"] - 1)
            s["_turn"] = C["MID_WEEK"]
            t.ok("writ" not in t.ids(s), "a Writ one short is not offered")
            s = t.fresh(standing=C["WRIT_COST"])
            s["_turn"] = C["MID_WEEK"]
            t.ok("writ" in t.ids(s), "exactly enough for the Writ is enough")
            s = t.fresh(standing=20, files=G_._board("DDDDB"), queue=[3, 3], last=0)
            s["_turn"] = C["MID_WEEK"]
            self._hits.clear()
            t.apply(s, "writ")
            t.eq(s["standing"], 20 - C["WRIT_COST"], "the Writ costs WRIT_COST")
            ev = t.advance(s, turn=C["MID_WEEK"] + 1)
            t.eq(G_._board_text(s["files"]), "DDDDB", "the Writ turns the party back: no clash, no snare spent")
            t.eq(s["standing"], 20 - C["WRIT_COST"] + dusk(5, C["MID_WEEK"]), "only dusk changes Standing after a Writ")
            t.ok("writ" in self._hits, "the Writ is noted")
            t.ok(not any("roll" in e for e in ev), "no roll on a Writ week")
            t.ok(s["writ_used"], "the Writ is spent")
            t.ok(not s["writ_now"], "the Writ's turning back lasts one week")
            t.ok("writ" not in t.ids(s), "a Writ is once only")
            s2 = t.fresh(standing=20, files=G_._board("....."), queue=[3, 3], last=0)
            s2["_turn"] = C["MID_WEEK"]
            t.apply(s2, "writ")
            t.advance(s2, turn=C["MID_WEEK"] + 1)
            t.eq(s2["standing"], 20 - C["WRIT_COST"] + dusk(0, C["MID_WEEK"]), "a Writ week costs no toll")
            s3 = t.fresh(standing=20, files=G_._board("....D"), queue=[3, 3], last=0)
            s3["_turn"] = C["MID_WEEK"] + 1
            t.apply(s3, "writ")
            t.advance(s3, turn=C["MID_WEEK"] + 2, dice=[1])
            t.eq(s3["files"][4]["d"], 1, "the week after a Writ is a normal week again only if the flag was cleared")
            # the Great Crossing: strength FINAL_STR, not boosted
            needf = C["BASE_NEED"] + C["FINAL_STR"] - C["DEN_DEF"]
            needf = max(C["NEED_MIN"], min(C["NEED_MAX"], needf))
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[CROSSING], last=0)
            self._hits.clear()
            t.advance(s, turn=C["WEEKS"] + 1, dice=[needf])
            t.eq(s["files"][4]["d"], 1, "the Crossing is held at its need")
            t.ok("final" in self._hits, "the Crossing is noted")
            s = t.fresh(standing=10, files=G_._board("....D"), queue=[CROSSING], last=0)
            t.advance(s, turn=C["WEEKS"] + 1, dice=[needf - 1])
            t.eq(s["files"][4]["d"], 0, "one under the need breaks the den at the Crossing")
            # winning: a den on every file after the Crossing
            s = t.fresh(standing=C["DEBT"], files=G_._board("DDDDD"))
            s["_turn"] = C["WEEKS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "a den on every file and the debt in Standing wins")
            s = t.fresh(standing=C["DEBT"] - 1, files=G_._board("DDDDD"))
            s["_turn"] = C["WEEKS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "one Standing short of the debt loses")
            s = t.fresh(standing=C["DEBT"] + 9, files=G_._board("DDDD."))
            s["_turn"] = C["WEEKS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "a gap after the Crossing loses however rich you are")
            for spec, n in (("DDDD.", 1), ("D.D.D", 2), ("..D.D", 3)):
                s = t.fresh(standing=C["DEBT"], files=G_._board(spec))
                s["_turn"] = C["WEEKS"] + 1
                end = self.check_end(s)
                t.ok(f"{n} gap" in end["reason"], f"the reason counts {n} gaps")
            s = t.fresh(standing=C["DEBT"], files=G_._board("DDDD."))
            s["_turn"] = C["WEEKS"]
            t.ok(self.check_end(s) is None, "the last week is still played")
            s = t.fresh(standing=C["DEBT"], files=G_._board("DDDDD"))
            s["_turn"] = C["WEEKS"]
            t.ok(self.check_end(s) is None, "a full wall and the debt before the Crossing is not yet a win")
            s = t.fresh(standing=-1, files=G_._board("DDDDD"))
            s["_turn"] = C["WEEKS"] + 1  # (a negative Standing can never reach the debt, so this is the foreclosure order)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "foreclosure at the last dusk beats a full wall")
            t.eq(self.turns, C["WEEKS"], "the budget is WEEKS")

        return [
            (1, "files and actions", r1), (2, "run", r2), (3, "mirror", r3), (4, "deck and pilgrims", r4),
            (5, "hold roll", r5), (6, "snare and breaks", r6), (7, "dusk and midpoint", r7), (8, "writ and crossing", r8),
        ]

    # ------------------------------------------------------------------ the game

    def resample_hidden(self, s, rng):
        """The rest of the deck is unseen. Redraw its order; the two shown cards stay."""
        rng.shuffle(s["hidden"]["deck"])

    def init_state(self, rng):
        C = self.C
        need = C["WEEKS"] - 1
        deck = list(C["_DECK"])[:need]
        while len(deck) < need:
            deck.append(2)
        rng.shuffle(deck)
        last = rng.d(C["FILES"]) - 1
        view = C["_VIEW"]
        return {
            "standing": C["START_STANDING"],
            "files": [{"d": 0, "s": 0} for _ in range(C["FILES"])],
            "last": last,
            "queue": deck[:view],
            "writ_used": False,
            "writ_now": False,
            "hidden": {"deck": deck[view:]},
        }

    def visible(self, s):
        v = {k: val for k, val in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "_seed")}
        v["party"] = [{"name": CARD_NAMES[c], "strength": self._strength(c, s["_turn"] + i)} for i, c in enumerate(s["queue"])]
        v["run_crosses"] = LETTERS[self._mirror(s["last"])]
        v["board"] = self._board_text(s["files"])
        return v

    def options(self, s):
        C = self.C
        o = []
        empty = [LETTERS[i] for i, c in enumerate(s["files"]) if not c["d"]]
        if empty and s["standing"] >= C["DEN_COST"]:
            o.append({"id": "den", "label": f"Raise a den ({C['DEN_COST']} Standing) on a file; the party crosses the opposite file",
                      "args": {}, "params": {"file": {"choices": empty}}})
        bare = [LETTERS[i] for i, c in enumerate(s["files"]) if c["d"] and not c["s"]]
        if bare and s["standing"] >= C["SNARE_COST"]:
            o.append({"id": "snare", "label": f"Lay a snare ({C['SNARE_COST']} Standing) on a file; the party crosses the opposite file",
                      "args": {}, "params": {"file": {"choices": bare}}})
        dens = sum(c["d"] for c in s["files"])
        need = C["SCREEN_NEED"] if dens >= C["SCREEN_DENS"] else C["RUN_NEED"]
        o.append({"id": "run", "label": f"Run contraband (roll {need}+ for +{C['RUN_GAIN']} Standing, else +{C['RUN_FAIL']}); "
                                        f"the party crosses file {LETTERS[self._mirror(s['last'])]}", "args": {}})
        if s["_turn"] >= C["MID_WEEK"] and not s["writ_used"] and s["standing"] >= C["WRIT_COST"]:
            o.append({"id": "writ", "label": f"Buy the Writ ({C['WRIT_COST']} Standing, once): this week's party turns back", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "den":
            f = LETTERS.index(args["file"])
            s["standing"] -= C["DEN_COST"]
            s["files"][f]["d"] = 1
            s["last"] = f
            ev.append(f"A den goes up on file {args['file']}. Standing -{C['DEN_COST']}.")
        elif a == "snare":
            f = LETTERS.index(args["file"])
            s["standing"] -= C["SNARE_COST"]
            s["files"][f]["s"] = 1
            s["last"] = f
            ev.append(f"A snare is laid on file {args['file']}. Standing -{C['SNARE_COST']}.")
        elif a == "run":
            dens = sum(c["d"] for c in s["files"])
            screened = dens >= C["SCREEN_DENS"]
            need = C["SCREEN_NEED"] if screened else C["RUN_NEED"]
            if screened:
                self.hit("screen")
            ok, txt = rng.check(need, C["DIE"], "run")
            if ok:
                s["standing"] += C["RUN_GAIN"]
                ev.append(f"{txt}. The load gets through: Standing +{C['RUN_GAIN']}.")
            else:
                s["standing"] += C["RUN_FAIL"]
                ev.append(f"{txt}. Most of it is seized: Standing +{C['RUN_FAIL']}.")
        elif a == "writ":
            s["standing"] -= C["WRIT_COST"]
            s["writ_used"] = True
            s["writ_now"] = True
            self.hit("writ")
            ev.append(f"The Writ is bought. Standing -{C['WRIT_COST']}.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        week = s["_turn"] - 1
        card = s["queue"].pop(0)
        name = CARD_NAMES[card]
        strength = self._strength(card, week)
        f = self._mirror(s["last"])
        letter = LETTERS[f]
        cell = s["files"][f]
        if card == CROSSING:
            self.hit("final")
        if s["writ_now"]:
            s["writ_now"] = False
            ev.append(f"The Writ is read at the border: the {name} turns back from file {letter}.")
        elif strength == 0:
            if cell["d"]:
                s["standing"] += C["PILGRIM_PAY"]
                ev.append(f"File {letter} faces the {name} (strength {strength}). Offerings reach the den: Standing +{C['PILGRIM_PAY']}.")
            else:
                ev.append(f"File {letter} faces the {name} (strength {strength}). They pass harmlessly.")
            self.hit("pilgrims")
        elif cell["d"]:
            defense = self._defense(s["files"], f)
            need = self._need(strength, defense)
            ok, txt = rng.check(need, C["DIE"], f"den {letter}")
            if cell["s"]:
                self.hit("snare_aid")
                cell["s"] = 0
            if ok:
                s["standing"] += C["HOLD_GAIN"]
                self.hit("hold")
                ev.append(f"File {letter} faces the {name} (strength {strength}), defense {defense}. {txt}. The den holds: Standing +{C['HOLD_GAIN']}.")
            else:
                cell["d"] = 0
                s["standing"] -= C["CROSS_COST"]
                self.hit("den_lost")
                ev.append(f"File {letter} faces the {name} (strength {strength}), defense {defense}. {txt}. The den falls: Standing -{C['CROSS_COST']}.")
        else:
            s["standing"] -= C["CROSS_COST"]
            self.hit("toll")
            ev.append(f"File {letter} faces the {name} (strength {strength}). No den stands there: Standing -{C['CROSS_COST']}.")
        # dusk
        dens = sum(c["d"] for c in s["files"])
        pay = dens * C["STIPEND"]
        tithe = self._tithe(week)
        s["standing"] += pay - tithe
        ev.append(f"Dusk: stipend +{pay} from {plural(dens, 'den')}; tithe -{tithe}.")
        # the next card
        nxt = week + C["_VIEW"]
        if nxt == self.turns:
            s["queue"].append(CROSSING)
        elif nxt < self.turns:
            deck = s["hidden"]["deck"]
            s["queue"].append(deck.pop(0) if deck else 2)
        if s["_turn"] == C["MID_WEEK"]:
            self.hit("midpoint")
            ev.append(f"Week {C['MID_WEEK']}: the herds grow and the Bishop raises the tithe to {C['TITHE_LATE']}. The Writ is now on sale.")
        return ev

    def status_line(self, s):
        return f"Standing {s['standing']} | Files {self._board_text(s['files'])} | Party {self._party_text(s)} | T{min(s['_turn'], self.turns)}/{self.turns}"

    def check_end(self, s):
        if s["standing"] < 0:
            return {"result": "loss", "reason": "the Bishop foreclosed on your Standing"}
        if s["_turn"] > self.turns:
            gaps = sum(1 for c in s["files"] if not c["d"])
            short = self.C["DEBT"] - s["standing"]
            if gaps == 0 and short <= 0:
                return {"result": "win", "reason": "the Wall stands and the debt is cleared"}
            if gaps:
                return {"result": "loss", "reason": f"the Wall had {plural(gaps, 'gap')} after the Great Crossing"}
            return {"result": "loss", "reason": f"the Wall stands but Standing is {short} short of the debt"}
        return None

    # ------------------------------------------------------------------ policy

    def _variants(self, options):
        out = []
        for o in options:
            params = o.get("params")
            if not params:
                out.append({"id": o["id"], "args": dict(o.get("args", {}))})
                continue
            for name, spec in params.items():
                for v in spec["choices"]:
                    out.append({"id": o["id"], "args": {**o.get("args", {}), name: v}})
        return out

    def _score(self, s, aid, args):
        C = self.C
        T = self.turns
        week = s["_turn"]
        left = T - week
        files = [dict(c) for c in s["files"]]
        st = float(s["standing"])
        last = s["last"]
        value = 0.0
        den_val = C["DEN_COST"] + 0.5 * C["STIPEND"] * left + 2.0
        snare_val = 1.2 * C["SNARE_COST"]
        stop = False
        if aid == "den":
            f = LETTERS.index(args["file"])
            st -= C["DEN_COST"]
            files[f]["d"] = 1
            last = f
            value += den_val
        elif aid == "snare":
            f = LETTERS.index(args["file"])
            st -= C["SNARE_COST"]
            files[f]["s"] = 1
            last = f
        elif aid == "run":
            need = C["SCREEN_NEED"] if sum(c["d"] for c in files) >= C["SCREEN_DENS"] else C["RUN_NEED"]
            p = (C["DIE"] - need + 1) / C["DIE"]
            st += p * C["RUN_GAIN"] + (1 - p) * C["RUN_FAIL"]
        elif aid == "writ":
            st -= C["WRIT_COST"]
            stop = True
            value -= 0.0 if week == T else 6.0
        strength = self._strength(s["queue"][0], week)
        m = self._mirror(last)
        surv = 1.0
        if not stop:
            cell = files[m]
            if strength == 0:
                if cell["d"]:
                    st += C["PILGRIM_PAY"]
            elif cell["d"]:
                need = self._need(strength, self._defense(files, m))
                surv = (C["DIE"] - need + 1) / C["DIE"]
                st += surv * C["HOLD_GAIN"] - (1 - surv) * C["CROSS_COST"]
                value -= (1 - surv) * den_val
                if cell["s"]:
                    value -= 0.6 * snare_val
            else:
                st -= C["CROSS_COST"]
        dens = sum(c["d"] for c in files)
        exp_dens = dens - (1 - surv)
        st += exp_dens * C["STIPEND"] - self._tithe(week)
        if week == T:
            if dens == C["FILES"] and st >= C["DEBT"]:
                return 100.0 * surv + 0.01 * st
            return -50.0 + 0.01 * st
        score = st + value
        if st < 0:
            score -= 30.0
        elif st < 3:
            score -= (3 - st) * 2.0
        return score

    def heuristic(self, s, options, rng):
        best, best_score = None, None
        for v in self._variants(options):
            sc = self._score(s, v["id"], v["args"])
            if best_score is None or sc > best_score + 1e-9:
                best, best_score = v, sc
        return best


if __name__ == "__main__":
    run(G)
