"""Drawdown Depot: a /play engine (v2 contract).

You run three night buses for the Low Ward, in debt to a creditor whose lien is the Ward itself.
The water table is dropping: tunnels below the street drain open, the Ward's wells fail, and a
bureaucratic Assessor hunts whichever layer is making the most money.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

LAYER = ["the Street", "Layer 1", "Layer 2", "Layer 3"]
SHORT = ["S", "L1", "L2", "L3"]


class G(Game):
    name = "Drawdown Depot"

    CONSTANTS = {
        "TURNS": 16,
        "BUSES": 3,
        "START_BEDS": 14,
        "PAY_0": 1,
        "PAY_1": 2,
        "PAY_2": 3,
        "PAY_3": 5,
        "STALL_1": 1,
        "STALL_2": 2,
        "STALL_3": 3,
        "TABLE0": 16,
        "L3_AT": 10,
        "WELLS": 8,
        "DRIP": 2,
        "DRY": 5,
        "RICH_N": 2,
        "HAUNT_N": 1,
        "HOME_N": 1,
        "IMPOUND": 1,
        "RECESS_P": 0.08,
        "SHORE_COST": 1,
        "SHORE_CUT": 1,
        "SINK_COST": 6,
        "SINK_CUT": 2,
        "KEEP": 14,
        "FLOOR": 3,
        "_SINK_BUFFER": 5,
        "_SINK_MIN_LEFT": 5,
        "_SHORE_BUFFER": 4,
    }

    RULES = """
1. You run {BUSES} night buses for the Low Ward, each starting on the Street, Layer 1 or Layer 2 by lot. Each night take one action: move a bus to the Street or an open layer, shore a layer, sink the well, or hold. A bus you move pays nothing tonight.
2. Working buses pay beds overnight: Street +{PAY_0}, Layer 1 +{PAY_1}, Layer 2 +{PAY_2}, Layer 3 +{PAY_3}. Below the Street a bus rolls a d6 and stalls (no pay) on {STALL_1} or less on Layer 1, {STALL_2} on Layer 2, {STALL_3} on Layer 3.
3. The water table starts at {TABLE0} and drops 1 each dawn. Layers 1 and 2 are open from the start; Layer 3 opens at table {L3_AT} or below.
4. The Ward loses {DRIP} beds a night. At table {WELLS} or below its wells fail and it loses {DRY} a night instead.
5. After the runs the Assessor works a hidden cycle, repeating in a fixed order you infer from past strikes: {RICH_N} nights on the layer whose buses paid most in total tonight, {HAUNT_N} on its haunt (a fixed hidden layer from the Street to Layer 2), {HOME_N} at home.
6. A strike impounds one bus there: it pays nothing tonight, stays out {IMPOUND} more night(s) per the regulations, then returns to the Street. About {RECESS_P:.0%} of nights the Assessor is at recess and does not strike. You learn where it struck only afterward.
7. Purchases: shore a layer once for {SHORE_COST} bed (its stall number drops by {SHORE_CUT}); sink a well once, after the wells fail, for {SINK_COST} beds (the wells then cost {SINK_CUT} less a night).
8. The Ward starts with {START_BEDS} beds and your creditor holds the lien on it: win with at least {KEEP} beds after night {TURNS}; lose the moment beds drop below {FLOOR}.
"""

    ACTIONS = ["move", "shore", "sink", "hold"]
    TAGS = [
        "layer3", "wells", "stall", "strike_rich", "strike_haunt", "strike_empty",
        "impound", "release", "recess", "shore", "sink", "all_stalled", "stays_home",
    ]

    BOUNDS = {"beds": (-30, 90), "table": (-2, 16), "sunk": (0, 1), "last": (-1, 3)}
    GATES = {}  # set below, needs lambdas that read the class helpers

    @property
    def REACH(self):  # noqa: N802
        C = self.C
        return {"beds": ("<=", C["FLOOR"] - 1), "table": ("<=", C["WELLS"]), "sunk": 1}

    @property
    def turns(self):
        return self.C["TURNS"]

    # ---------------------------------------------------------------- helpers

    def pay(self, layer):
        return self.C[f"PAY_{layer}"]

    def stall(self, s, layer):
        """The roll a bus on this layer stalls on, or less. Street never stalls."""
        if layer == 0:
            return 0
        return max(0, self.C[f"STALL_{layer}"] - (self.C["SHORE_CUT"] if s["shored"][layer - 1] else 0))

    def open_layers(self, s):
        out = [0, 1, 2]
        if s["table"] <= self.C["L3_AT"]:
            out.append(3)
        return out

    def wells_failed(self, s):
        return s["table"] <= self.C["WELLS"]

    def can_afford(self, s, cost):
        return s["beds"] - cost >= self.C["FLOOR"]

    def movable(self, s):
        """(first bus index on each layer, in bus order) for buses that are free to move."""
        seen, out = set(), []
        for i in range(self.C["BUSES"]):
            if s["held"][i] > 0:
                continue
            lay = s["layer"][i]
            if lay in seen:
                continue
            seen.add(lay)
            out.append((i, lay))
        return out

    def shorable(self, s):
        return [
            L for L in (1, 2, 3)
            if L in self.open_layers(s) and not s["shored"][L - 1] and self.can_afford(s, self.C["SHORE_COST"])
        ]

    def can_sink(self, s):
        return self.wells_failed(s) and not s["sunk"] and self.can_afford(s, self.C["SINK_COST"])

    # ---------------------------------------------------------------- rule tests

    def rule_tests(self):
        C = self.C
        B = C["BUSES"]

        def has(s, aid, **args):
            """Exact match on id and args (t.offered returns True for the only option of an id whatever its args)."""
            return any(o["id"] == aid and all(o["args"].get(k) == v for k, v in args.items()) for o in self.options(s))

        def quiet(s):
            """Park every bus in the impound so a test sees only what it means to."""
            s["layer"] = [-1] * B
            s["held"] = [99] * B
            return s

        def r1(t):
            s = t.fresh(seed=1)
            t.ok(all(L in (0, 1, 2) for L in s["layer"]), "each bus starts on the Street, Layer 1 or Layer 2")
            t.eq(len(s["layer"]), B, "the fleet size")
            t.ok({"move", "shore", "hold"} <= set(t.ids(s)), "move, shore and hold are offered on night 1")
            t.ok(has(s, "move", bus=0, to=1), "a bus may move to an open layer")
            s2, _ = t.step(s, "hold")
            t.eq(s2["_turn"], 2, "one action ends the night")
            s = t.fresh(beds=20, layer=[0] * B)
            t.apply(s, "move", {"bus": 0, "to": 1})
            t.eq(s["layer"][0], 1, "the bus moves")
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["beds"], 20 + (B - 1) * C["PAY_0"] - C["DRIP"], "a bus moved tonight pays nothing, the others work the Street")

        def r2(t):
            for lay in (1, 2, 3):
                s = quiet(t.fresh(beds=20))
                s["layer"][0], s["held"][0] = lay, 0
                t.advance(s, turn=2, dice=[C[f"STALL_{lay}"] + 1], chances=[0.0])
                t.eq(s["beds"], 20 + C[f"PAY_{lay}"] - C["DRIP"], f"layer {lay} pays when the roll clears its stall number")
                s = quiet(t.fresh(beds=20))
                s["layer"][0], s["held"][0] = lay, 0
                t.advance(s, turn=2, dice=[C[f"STALL_{lay}"]], chances=[0.0])
                t.eq(s["beds"], 20 - C["DRIP"], f"layer {lay} stalls on its stall number or less")
            s = quiet(t.fresh(beds=20))
            s["layer"][0], s["held"][0] = 0, 0
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["beds"], 20 + C["PAY_0"] - C["DRIP"], "the Street pays without a roll")

        def r3(t):
            s = t.fresh()
            t.eq(s["table"], C["TABLE0"], "the table starts at TABLE0")
            t.ok(has(s, "move", bus=0, to=1) and has(s, "move", bus=0, to=2), "layers 1 and 2 are open from the start")
            t.ok(not has(s, "move", bus=0, to=3), "layer 3 is closed at the start")
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["table"], C["TABLE0"] - 1, "the table drops 1 each dawn")
            s = t.fresh(table=C["L3_AT"] + 1)
            t.ok(not has(s, "move", bus=0, to=3), "layer 3 stays closed above its table level")
            s = t.fresh(table=C["L3_AT"])
            t.ok(has(s, "move", bus=0, to=3), "layer 3 opens at its table level")

        def r4(t):
            s = quiet(t.fresh(beds=20, table=C["WELLS"] + 1))
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["beds"], 20 - C["DRIP"], "the Ward loses DRIP a night while the wells hold")
            s = quiet(t.fresh(beds=20, table=C["WELLS"]))
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["beds"], 20 - C["DRY"], "the Ward loses DRY a night once the wells fail")

        def r5(t):
            # a "rich" night strikes the layer that paid most (a bus on layer 3 here)
            s = t.fresh(beds=30, layer=[3, 1, 0], held=[0] * B, hidden__haunt=2, hidden__cycle=["rich"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1, C["STALL_1"] + 1], chances=[0.99])
            t.eq(s["held"][0], C["IMPOUND"], "a rich night strikes the richest layer")
            t.eq(s["last"], 3, "the strike is recorded")
            # a "haunt" night strikes the haunt and spares the rich layer
            s = t.fresh(beds=30, layer=[3, 1, 0], held=[0] * B, hidden__haunt=1, hidden__cycle=["haunt"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1, C["STALL_1"] + 1], chances=[0.99])
            t.eq(s["held"][1], C["IMPOUND"], "a haunt night strikes the haunt")
            t.eq(s["held"][0], 0, "the rich layer is spared")
            # a "home" night strikes nobody
            s = t.fresh(beds=30, layer=[3, 1, 0], held=[0] * B, hidden__haunt=1, hidden__cycle=["home"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1, C["STALL_1"] + 1], chances=[0.99])
            t.eq(s["held"], [0] * B, "a home night strikes nobody")
            # the cycle repeats in its fixed order
            s = t.fresh(beds=30, layer=[3, 0, 0], held=[0] * B, hidden__haunt=0, hidden__cycle=["home", "rich"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1], chances=[0.99])
            t.eq(s["held"], [0] * B, "night 1 of the cycle is home")
            t.advance(s, turn=3, dice=[C["STALL_3"] + 1], chances=[0.99])
            t.eq(s["held"][0], C["IMPOUND"], "night 2 of the cycle is rich")
            s = t.fresh(beds=30, layer=[3, 0, 0], held=[0] * B, hidden__haunt=0, hidden__cycle=["home", "rich"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1], chances=[0.99])
            t.advance(s, turn=3, dice=[C["STALL_3"] + 1], chances=[0.0])
            t.advance(s, turn=4, dice=[C["STALL_3"] + 1], chances=[0.99])
            t.eq(s["held"], [0] * B, "night 3 wraps round to home")
            # the layer paying most is struck, ties go deeper
            s = t.fresh(beds=30, layer=[0, 0, 1], held=[0] * B, hidden__haunt=0, hidden__cycle=["rich"])
            t.advance(s, turn=2, dice=[C["STALL_1"] + 1], chances=[0.99])
            t.eq(s["last"], 1 if C["PAY_1"] >= 2 * C["PAY_0"] else 0, "the layer paying most is struck")
            # nothing paid: the haunt
            s = quiet(t.fresh(beds=30, hidden__haunt=0, hidden__cycle=["rich"]))
            s["layer"][0], s["held"][0] = 2, 0
            t.advance(s, turn=2, dice=[C["STALL_2"]], chances=[0.99])
            t.eq(s["last"], 0, "when nothing paid, a rich night goes to the haunt")

        def r6(t):
            s = t.fresh(beds=30, layer=[3, 0, 0], held=[0] * B, hidden__haunt=0, hidden__cycle=["rich"])
            ev = t.advance(s, turn=2, dice=[C["STALL_3"] + 1], chances=[0.99])
            t.eq(s["held"][0], C["IMPOUND"], "the struck bus is impounded")
            t.eq(s["layer"][0], -1, "the struck bus leaves its layer")
            t.eq(s["beds"], 30 + (B - 1) * C["PAY_0"] - C["DRIP"], "the struck bus pays nothing tonight")
            t.has(ev, "impounded", "the strike is reported")
            beds = s["beds"]
            for n in range(1, C["IMPOUND"] + 1):
                t.advance(s, turn=2 + n, chances=[0.0])
                beds += (B - 1) * C["PAY_0"] - C["DRIP"]
                t.eq(s["beds"], beds, f"night {n} of the impound: the bus is out")
            t.eq(s["layer"][0], 0, "the bus returns to the Street")
            t.advance(s, turn=3 + C["IMPOUND"], chances=[0.0])
            beds += B * C["PAY_0"] - C["DRIP"]
            t.eq(s["beds"], beds, "the bus works again the night after its return")
            # recess: no strike, and the chance is the sheet's number
            s = t.fresh(beds=30, layer=[3, 0, 0], held=[0] * B, hidden__cycle=["rich"])
            ev = t.advance(s, turn=2, dice=[C["STALL_3"] + 1], chances=[C["RECESS_P"] / 2])
            t.eq(s["held"], [0] * B, "nobody is impounded at recess")
            t.has(ev, "recess", "recess is reported")
            s = t.fresh(beds=30, layer=[3, 0, 0], held=[0] * B, hidden__cycle=["rich"])
            t.advance(s, turn=2, dice=[C["STALL_3"] + 1], chances=[C["RECESS_P"] + 0.01])
            t.ok(sum(s["held"]) > 0, "just above the recess chance the Assessor strikes")
            shown = repr(self.visible(s))
            t.ok("haunt" not in shown and "cycle" not in shown, "the haunt and the cycle are not shown")

        def r7(t):
            s = t.fresh(beds=20)
            t.ok(has(s, "shore", layer=2), "shore is offered on an open layer")
            t.ok(not has(s, "shore", layer=3), "a closed layer cannot be shored")
            t.apply(s, "shore", {"layer": 2})
            t.eq(s["beds"], 20 - C["SHORE_COST"], "shore cost")
            t.ok(not has(s, "shore", layer=2), "each layer is shored once")
            s2 = quiet(s)
            s2["layer"][0], s2["held"][0] = 2, 0
            before = s2["beds"]
            t.advance(s2, turn=2, dice=[C["STALL_2"] - C["SHORE_CUT"] + 1], chances=[0.0])
            t.eq(s2["beds"], before + C["PAY_2"] - C["DRIP"], "a shored layer pays one roll lower")
            s2 = quiet(t.fresh(beds=20))
            s2["layer"][0], s2["held"][0], s2["shored"][1] = 2, 0, 1
            t.advance(s2, turn=2, dice=[C["STALL_2"] - C["SHORE_CUT"]], chances=[0.0])
            t.eq(s2["beds"], 20 - C["DRIP"], "and still stalls at its lowered number")
            s = t.fresh(beds=20, table=C["WELLS"] + 1)
            t.ok(not t.offered(s, "sink"), "no well can be sunk before the wells fail")
            s = t.fresh(beds=20, table=C["WELLS"])
            t.ok(t.offered(s, "sink"), "sink is offered once the wells fail")
            t.apply(s, "sink")
            t.eq(s["beds"], 20 - C["SINK_COST"], "sink cost")
            t.ok(not t.offered(s, "sink"), "once only")
            s = quiet(s)
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["beds"], 20 - C["SINK_COST"] - (C["DRY"] - C["SINK_CUT"]), "the sunk well cuts the nightly loss")

        def r8(t):
            s = t.fresh()
            t.eq(s["beds"], C["START_BEDS"], "starting beds")
            t.eq(self.turns, C["TURNS"], "the turn budget is TURNS")
            s = t.fresh(beds=C["KEEP"], _turn=C["TURNS"] + 1)
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "KEEP beds after the last night wins")
            s = t.fresh(beds=C["KEEP"] - 1, _turn=C["TURNS"] + 1)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "short of KEEP after the last night loses")
            s = t.fresh(beds=C["FLOOR"] - 1, _turn=3)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "below FLOOR loses at once")
            s = t.fresh(beds=C["FLOOR"], _turn=3)
            t.ok(self.check_end(s) is None, "exactly FLOOR is still alive")
            s = t.fresh(beds=C["KEEP"] + 5, _turn=C["TURNS"])
            t.ok(self.check_end(s) is None, "a high bed count does not win early")

        return [
            (1, "fleet and actions", r1), (2, "pay and stall", r2), (3, "table and layers", r3),
            (4, "wells", r4), (5, "the strike target", r5), (6, "impound and recess", r6),
            (7, "purchases", r7), (8, "goal and floor", r8),
        ]

    # ---------------------------------------------------------------- state

    def _cycle(self, rng):
        C = self.C
        order = ["rich"] * C["RICH_N"] + ["haunt"] * C["HAUNT_N"] + ["home"] * C["HOME_N"]
        rng.shuffle(order)
        return order

    def init_state(self, rng):
        C = self.C
        return {
            "beds": C["START_BEDS"],
            "table": C["TABLE0"],
            "layer": [rng.d(3) - 1 for _ in range(C["BUSES"])],
            "held": [0] * C["BUSES"],
            "moved": [0] * C["BUSES"],
            "shored": [0, 0, 0],
            "sunk": 0,
            "last": -1,
            "hidden": {"haunt": rng.d(3) - 1, "cycle": self._cycle(rng)},
        }

    def visible(self, s):
        buses = []
        for i in range(self.C["BUSES"]):
            if s["held"][i] > 0:
                where = f"impounded, {s['held'][i]} nights to go"
            else:
                where = LAYER[s["layer"][i]]
            buses.append({"bus": i + 1, "at": where})
        return {
            "beds": s["beds"],
            "table": s["table"],
            "open_layers": [LAYER[L] for L in self.open_layers(s)],
            "buses": buses,
            "shored": [LAYER[L + 1] for L in range(3) if s["shored"][L]],
            "well_sunk": bool(s["sunk"]),
            "wells_failed": self.wells_failed(s),
            "last_strike": LAYER[s["last"]] if s["last"] >= 0 else "none yet",
        }

    # ---------------------------------------------------------------- player moves

    def options(self, s):
        C = self.C
        o = []
        opened = self.open_layers(s)
        for i, frm in self.movable(s):
            for to in opened:
                if to == frm:
                    continue
                o.append({
                    "id": "move",
                    "label": f"Move a bus from {LAYER[frm]} to {LAYER[to]} (it pays nothing tonight)",
                    "args": {"bus": i, "to": to},
                    "group": "Move a bus",
                })
        for L in self.shorable(s):
            stall = self.stall(s, L)
            o.append({
                "id": "shore",
                "label": f"Shore {LAYER[L]} (-{C['SHORE_COST']} bed; its stall number {stall} becomes {max(0, stall - C['SHORE_CUT'])})",
                "args": {"layer": L},
                "group": "Shore a layer",
            })
        if self.can_sink(s):
            o.append({
                "id": "sink",
                "label": f"Sink a well (-{C['SINK_COST']} beds; the wells then cost {C['SINK_CUT']} less a night)",
                "args": {},
            })
        o.append({"id": "hold", "label": "Hold the roster and file the usual forms", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "move":
            i, to = args["bus"], args["to"]
            frm = s["layer"][i]
            s["layer"][i] = to
            s["moved"][i] = 1
            ev.append(f"Form 11: a bus is reassigned from {LAYER[frm]} to {LAYER[to]}. It pays nothing tonight.")
        elif a == "shore":
            L = args["layer"]
            s["beds"] -= C["SHORE_COST"]
            s["shored"][L - 1] = 1
            self.hit("shore")
            ev.append(f"{LAYER[L]} is shored. Beds -{C['SHORE_COST']}. Its stall number is now {self.stall(s, L)}.")
        elif a == "sink":
            s["beds"] -= C["SINK_COST"]
            s["sunk"] = 1
            self.hit("sink")
            ev.append(f"A deep well is sunk. Beds -{C['SINK_COST']}. The wells will cost {C['SINK_CUT']} less a night.")
        elif a == "hold":
            ev.append("Roster held. The usual forms are filed in triplicate.")
        return ev

    # ---------------------------------------------------------------- the night

    def advance(self, s, rng):
        C = self.C
        B = C["BUSES"]
        ev = []

        # impounded buses serve their time; the one that finishes returns to the Street, idle tonight
        for i in range(B):
            if s["held"][i] > 0:
                s["held"][i] -= 1
                if s["held"][i] == 0:
                    s["layer"][i] = 0
                    s["moved"][i] = 1
                    self.hit("release")
                    ev.append("An impounded bus is released to the Street. It pays nothing tonight.")

        # the runs
        paid = [0] * B
        street = 0
        for i in range(B):
            if s["held"][i] > 0:
                continue
            if s["moved"][i]:
                s["moved"][i] = 0
                continue
            lay = s["layer"][i]
            if lay == 0:
                paid[i] = C["PAY_0"]
                street += 1
                continue
            ok, txt = rng.check(self.stall(s, lay) + 1, 6, SHORT[lay])
            if ok:
                paid[i] = self.pay(lay)
                ev.append(f"{LAYER[lay]} bus: {txt}. Pays {paid[i]}.")
            else:
                self.hit("stall")
                ev.append(f"{LAYER[lay]} bus: {txt}. Stalled, no pay.")
        if street:
            ev.append(f"Street run: {street} bus{'es' if street > 1 else ''} pay{'' if street > 1 else 's'} {street * C['PAY_0']}.")

        by_layer = [0, 0, 0, 0]
        for i in range(B):
            if paid[i]:
                by_layer[s["layer"][i]] += paid[i]
        if not any(paid):
            self.hit("all_stalled")

        # the Assessor
        if rng.chance(C["RECESS_P"]):
            self.hit("recess")
            s["last"] = -1
            ev.append("The Assessor's office is at recess tonight. No strike.")
        else:
            night = s["_turn"] - 1
            cyc = s["hidden"]["cycle"]
            mode = cyc[(night - 1) % len(cyc)]
            target = None
            how = ""
            if mode == "rich" and max(by_layer) > 0:
                top = max(by_layer)
                target = max(L for L in range(4) if by_layer[L] == top)
                self.hit("strike_rich")
                how = "the richest layer"
            elif mode in ("rich", "haunt"):
                target = s["hidden"]["haunt"]
                self.hit("strike_haunt")
                how = "its haunt" if mode == "haunt" else "its haunt (nothing paid)"
            if target is None:
                s["last"] = -1
                self.hit("stays_home")
                ev.append("The Assessor stays home tonight.")
            else:
                victims = [i for i in range(B) if s["layer"][i] == target and s["held"][i] == 0]
                s["last"] = target
                if victims:
                    w = max(victims, key=lambda i: (paid[i], -i))
                    forfeit = paid[w]
                    paid[w] = 0
                    s["held"][w] = C["IMPOUND"]
                    s["layer"][w] = -1
                    self.hit("impound")
                    ev.append(f"The Assessor visits {how}: {LAYER[target]}. A bus is impounded for {C['IMPOUND']} more night{'s' if C['IMPOUND'] != 1 else ''}{f', forfeiting {forfeit}' if forfeit else ''}.")
                else:
                    self.hit("strike_empty")
                    ev.append(f"The Assessor visits {how}: {LAYER[target]}. It finds no bus there.")

        s["beds"] += sum(paid)
        if sum(paid):
            ev.append(f"The runs bring in {sum(paid)} bed{'s' if sum(paid) != 1 else ''}.")

        # the Ward's nightly loss
        if self.wells_failed(s):
            loss = C["DRY"] - (C["SINK_CUT"] if s["sunk"] else 0)
            ev.append(f"The wells are dry: the Ward loses {loss} beds.")
        else:
            loss = C["DRIP"]
            ev.append(f"The Ward loses {loss} beds.")
        s["beds"] -= loss

        # dawn: the table drops and tunnels drain
        s["table"] -= 1
        if s["table"] == C["L3_AT"]:
            self.hit("layer3")
            ev.append(f"Dawn: the table falls to {s['table']}. Layer 3 is drained and open to traffic.")
        elif s["table"] == C["WELLS"]:
            self.hit("wells")
            ev.append(f"Dawn: the table falls to {s['table']}. The Ward's wells have failed.")
        return ev

    def status_line(self, s):
        runs = " ".join("X" if s["held"][i] > 0 else SHORT[s["layer"][i]] for i in range(self.C["BUSES"]))
        last = "-" if s["last"] < 0 else SHORT[s["last"]]
        return f"Beds {s['beds']} | Runs {runs} | Table {s['table']} | Struck {last}"

    def check_end(self, s):
        C = self.C
        if s["beds"] < C["FLOOR"]:
            return {"result": "loss", "reason": f"the Ward fell to {s['beds']} bed(s) and was condemned"}
        if s["_turn"] > self.turns:
            if s["beds"] >= C["KEEP"]:
                return {"result": "win", "reason": f"the Ward closed the audit with {s['beds']} beds"}
            return {"result": "loss", "reason": f"the audit found {s['beds']} beds, short of {C['KEEP']}"}
        return None

    # ---------------------------------------------------------------- the sensible player

    def heuristic(self, s, options, rng):
        C = self.C
        by = {}
        for o in options:
            by.setdefault(o["id"], []).append(o)
        left = self.turns - s["_turn"] + 1
        if "sink" in by and left >= C["_SINK_MIN_LEFT"] and s["beds"] - C["SINK_COST"] >= C["FLOOR"] + C["_SINK_BUFFER"]:
            return by["sink"][0]

        opened = self.open_layers(s)

        def val(L):
            if L == 0:
                return C["PAY_0"]
            return self.pay(L) * (6 - self.stall(s, L)) / 6.0

        ranked = sorted(opened, key=lambda L: -val(L))
        free = [i for i in range(C["BUSES"]) if s["held"][i] == 0]
        want = {}
        plan = [ranked[0], ranked[0], ranked[1], ranked[1]]
        for k in range(len(free)):
            want[plan[k]] = want.get(plan[k], 0) + 1
        have = {}
        for i in free:
            have[s["layer"][i]] = have.get(s["layer"][i], 0) + 1

        if "shore" in by and s["beds"] - C["SHORE_COST"] >= C["FLOOR"] + C["_SHORE_BUFFER"] and left >= 6:
            best = None
            for o in by["shore"]:
                L = o["args"]["layer"]
                if have.get(L, 0) > 0 or want.get(L, 0) > 0:
                    sc = val(L) * (1 + have.get(L, 0))
                    if best is None or sc > best[0]:
                        best = (sc, o)
            if best:
                return best[1]

        over = [L for L in have if have[L] > want.get(L, 0)]
        under = [L for L in want if want[L] > have.get(L, 0)]
        if over and under and "move" in by:
            frm = min(over, key=lambda L: val(L) if L in opened else -1)
            to = max(under, key=val)
            for o in by["move"]:
                if s["layer"][o["args"]["bus"]] == frm and o["args"]["to"] == to:
                    return o
        return by["hold"][0]


G.GATES = {
    "move": {"_if": lambda g, s: any(to != frm for _, frm in g.movable(s) for to in g.open_layers(s))},
    "shore": {"_if": lambda g, s: bool(g.shorable(s))},
    "sink": {"_if": lambda g, s: g.can_sink(s)},
    "hold": {},
}


if __name__ == "__main__":
    run(G)
