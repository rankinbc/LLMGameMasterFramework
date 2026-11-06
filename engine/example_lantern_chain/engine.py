"""Lantern Chain: reference engine for /play (v2 contract).

A hand-made example, not a roll result. It shows the shape, not the content: a wind rival that acts
every night with a readable habit, a clock, a midpoint storm and unlock, a loss lever, merged
options (one "light" id, one option per dark lantern), a gambit against the rival (the windbreak:
a priced roll that turns the wind for a night), CONSTANTS plus a RULES template so the sheet
cannot drift from the code, and TAGS so `check` can prove every twist is reachable.

Copy the structure. Change the nouns, the rival's habit, the win condition and the primary number.
Do not copy the lantern, the wind or the oil into the next game.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gm_base import Game, plural, run  # noqa: E402


class G(Game):
    name = "Lantern Chain"

    CONSTANTS = {
        "NIGHTS": 16,
        "LANTERNS": 5,
        "START_OIL": 12,
        "LIGHT_COST": 2,
        "DIE": 6,
        "HAUL_NEED": 3,
        "HAUL_GAIN": 9,
        "HAUL_FAIL": 2,
        "STORM_NIGHT": 9,
        "SIGNAL_NIGHT": 8,
        "SIGNAL_COST": 3,
        "SIGNAL_MAX": 6,
        "SLED_GAIN": 6,
        "WINDBREAK_COST": 2,
        "WINDBREAK_NEED": 4,
        "STALL_P": 0.2,
        "GOAL": 34,
        "_START_LIT": 3,
        "_STRIDES": 3,
        "_CRISIS": 2,
        "_SEEN_NEEDED": 3,
        "_SEEN_KEPT": 8,
    }

    RULES = """
1. {LANTERNS} lanterns line the ridge, numbered from camp. Each night take one action: light a dark lantern, shield a lit one, or haul oil.
2. Lighting costs {LIGHT_COST} oil. Shielding is free and keeps that lantern lit through tonight's wind. A windbreak costs {WINDBREAK_COST} oil: roll {WINDBREAK_NEED}+ and the wind turns, snuffing nothing tonight.
3. Hauling: roll {HAUL_NEED}+ on a d{DIE} to bring back {HAUL_GAIN} oil, otherwise {HAUL_FAIL}.
4. You start with {START_OIL} oil. At dusk each lit lantern burns 1 oil. Oil below 0 puts every lantern out and the column turns back.
5. The wind snuffs one unshielded lantern a night, stepping along the ridge by a fixed hidden stride. On {STALL_P:.0%} of nights it lingers where it was.
6. Tonight's wind target is shown at dusk. From night {STORM_NIGHT} the storm snuffs two lanterns a night.
7. The column advances each night by the run of lit lanterns starting at lantern 1. From night {SIGNAL_NIGHT} signal a rush: {SIGNAL_COST} oil doubles tonight's advance, {SIGNAL_MAX} oil triples it.
8. After two failed hauls in a row the depot sends a sled once: a sure {SLED_GAIN} oil. Goal: column at {GOAL} within {NIGHTS} nights.
"""

    ACTIONS = ["light", "shield", "haul", "windbreak", "signal", "sled"]
    TAGS = ["storm", "signal", "sled", "windbreak", "lantern1_out", "oil_crisis", "stall"]
    # risky moves off the main loop; the windbreak acts on the rival (the wind), so it must change a RIVAL_KEYS value
    GAMBITS = {"windbreak": {"rival": True}}
    RIVAL_KEYS = ["wind"]
    # every number or board the player must manage, including ones kept off the status line (3 at most)
    TRACKED = ["oil", "column", "lit"]

    # ranges the numbers may take; leaving one is a bug
    BOUNDS = {"oil": (-10, 80), "column": (0, 120), "fails": (0, 20)}
    # values the sheet promises can happen; never seen in play is a bug (a clamp, a dead rule)
    REACH = {"column": 32, "oil": ("<=", -1), "fails": 2}
    # when each priced or gated action must be offered; checked at every state of every selftest game
    GATES = {
        "light": {"oil": "LIGHT_COST", "_if": lambda g, s: not all(s["lit"])},
        "signal": {"oil": "SIGNAL_COST", "_turn": "SIGNAL_NIGHT"},
        "sled": {"fails": 2, "!sled_used": 1},
        "windbreak": {"oil": "WINDBREAK_COST", "_if": lambda g, s: any(s["lit"][i] for i in s["wind"])},
    }

    @property
    def turns(self):
        return self.C["NIGHTS"]

    def rule_tests(self):
        """One test per rule line. They call the game's own apply and advance, and assert what the sheet says."""
        C = self.C

        def r1(t):
            s = t.fresh(seed=1, oil=20, wind=[4])
            t.ok({"light", "haul"} <= set(t.ids(s)), "a dark lantern and a depot must be actionable on night 1")
            s = t.fresh(seed=1, oil=20, wind=[0])
            t.ok(t.offered(s, "shield", lantern=0), "a lit lantern under the wind must be shieldable")
            s, _ = t.step(s, "haul")
            t.eq(s["_turn"], 2, "one action ends the night")
            s = t.fresh(oil=12, wind=[2], lit=[True, True, True, False, False])
            t.eq(t.label(s, "light", lantern=3), f"Light lantern 4 (-{C['LIGHT_COST']} oil)", "the label counts lanterns from 1")
            t.eq(t.label(s, "shield", lantern=2), "Shield lantern 3 from tonight's wind", "the shield label counts from 1")
            t.eq(t.status(s), f"Oil 12 | Column 0/{C['GOAL']} | Ridge ###.. | Wind 3", "the status line")
            s0 = t.fresh()
            t.eq((s0["column"], s0["fails"], s0["signal"], s0["shield"], s0["sled_used"]), (0, 0, 0, None, False), "a fresh game starts clean")
            t.eq(s0["lit"], [True, True, True, False, False], "three of the five lanterns start lit")
            t.ok(0 <= s0["wind"][0] < C["LANTERNS"], "the first wind target is a lantern")
            starts = {t.fresh(seed=i)["wind"][0] for i in range(1, 80)}
            t.eq(starts, set(range(C["LANTERNS"])), "the first wind target can be any lantern, and only a lantern")

        def r2(t):
            s = t.fresh(oil=10, wind=[4])
            events = t.apply(s, "light", {"lantern": 3})
            t.has(events, "Lantern 4 lit.", "the event counts lanterns from 1")
            t.eq(s["oil"], 10 - C["LIGHT_COST"], "lighting cost")
            t.ok(s["lit"][3], "lantern lit")
            s = t.fresh(oil=10, wind=[0])
            events = t.apply(s, "shield", {"lantern": 0})
            t.has(events, "Lantern 1 shielded for the night.")
            t.eq(s["oil"], 10, "shielding is free")
            events = t.advance(s, turn=2, chances=[0.99])
            t.has(events, "The wind leaned on lantern 1. The shield held.")
            t.ok(s["lit"][0], "a shielded lantern survives the wind")
            # the windbreak: a priced roll against the wind itself
            s = t.fresh(oil=10, wind=[0, 1], lit=[True] * 5)
            t.eq(t.label(s, "windbreak"), f"Raise a windbreak (-{C['WINDBREAK_COST']} oil, roll {C['WINDBREAK_NEED']}+: the wind snuffs nothing tonight)")
            events = t.apply(s, "windbreak", dice=[C["WINDBREAK_NEED"]])
            t.eq(s["oil"], 10 - C["WINDBREAK_COST"], "the windbreak costs its oil")
            t.eq(s["wind"], [], "a good roll turns the wind: no target tonight")
            t.has(events, "The wind turns on the windbreak. Nothing is snuffed tonight.")
            t.eq(t.status(s), f"Oil 8 | Column 0/{C['GOAL']} | Ridge ##### | Wind -", "the status shows a turned wind")
            t.ok(not t.offered(s, "shield", lantern=0), "nothing to shield once the wind is turned")
            events = t.advance(s, turn=2, chances=[0.99, 0.99])
            t.ok(all(s["lit"]), "every lantern survives the night")
            t.has(events, "The windbreak held: no lantern was snuffed.")
            s = t.fresh(oil=10, wind=[0, 1], lit=[True] * 5)
            events = t.apply(s, "windbreak", dice=[C["WINDBREAK_NEED"] - 1])
            t.eq(s["oil"], 10 - C["WINDBREAK_COST"], "a failed windbreak still costs its oil")
            t.eq(s["wind"], [0, 1], "a failed windbreak leaves the wind on its targets")
            t.has(events, "The windbreak collapses before dusk.")
            s = t.fresh(oil=10, wind=[4], lit=[True, True, True, False, False])
            t.ok(not t.offered(s, "windbreak"), "no windbreak when the wind aims at a dark lantern (nothing to save)")
            s = t.fresh(oil=C["WINDBREAK_COST"] - 1, wind=[0])
            t.ok(not t.offered(s, "windbreak"), "a windbreak needs its oil")
            s = t.fresh(oil=C["WINDBREAK_COST"], wind=[0])
            t.ok(t.offered(s, "windbreak"), "exactly enough oil is enough")

        def r3(t):
            s = t.fresh(oil=5, wind=[4])
            events = t.apply(s, "haul", dice=[C["HAUL_NEED"]])
            t.has(events, f"Oil +{C['HAUL_GAIN']}.")
            t.eq(s["oil"], 5 + C["HAUL_GAIN"], "haul success")
            s = t.fresh(oil=5, wind=[4])
            t.apply(s, "haul", dice=[C["HAUL_NEED"] - 1])
            t.eq(s["oil"], 5 + C["HAUL_FAIL"], "haul failure")
            t.eq(s["fails"], 1, "a failed haul counts")
            s = t.fresh(oil=5, fails=1, wind=[4])
            t.apply(s, "haul", dice=[C["HAUL_NEED"] - 1])
            t.eq(s["fails"], 2, "two failed hauls in a row")
            s = t.fresh(oil=5, fails=1, wind=[4])
            t.apply(s, "haul", dice=[C["HAUL_NEED"]])
            t.eq(s["fails"], 0, "a good haul resets the count")
            wins = 0
            for sd in range(1, 301):  # unscripted dice: a haul succeeds on HAUL_NEED or better on a d6
                s = t.fresh(oil=5, wind=[4])
                t.apply(s, "haul", seed=sd)
                wins += s["oil"] == 5 + C["HAUL_GAIN"]
            want = (C["DIE"] - C["HAUL_NEED"] + 1) / C["DIE"]
            t.ok(abs(wins / 300 - want) < 0.08, f"a haul should succeed about {want:.0%} of the time, got {wins / 300:.0%}")

        def r4(t):
            s = t.fresh()
            t.eq(s["oil"], C["START_OIL"], "starting oil")
            s = t.fresh(oil=10, wind=[4])
            t.advance(s, turn=2, chances=[0.99])
            t.eq(s["oil"], 10 - 3, "three lit lanterns burn three oil")
            s = t.fresh(oil=2, wind=[4])
            t.advance(s, turn=2, chances=[0.99])
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "oil below zero ends the game in a loss")
            s = t.fresh(oil=2, wind=[4])
            events = t.advance(s, turn=2, chances=[0.99])
            t.ok(s["_ended"] and "oil ran out" in s["_ended"]["reason"], "the dusk itself ends the game")
            t.ok(not any("Wind building" in e for e in events), "no tell for a tomorrow that will not come")
            s = t.fresh(oil=3, wind=[4])
            self._hits.clear()
            t.advance(s, turn=2, chances=[0.99])
            t.eq(s["oil"], 0, "three lit lanterns burn three oil")
            t.ok(self.check_end(s) is None, "exactly zero oil is still alive")
            t.ok("oil_crisis" in self._hits, "oil at 2 or less is a crisis")
            s = t.fresh(oil=6, wind=[4])
            self._hits.clear()
            t.advance(s, turn=2, chances=[0.99])
            t.ok("oil_crisis" not in self._hits, "oil at 3 is not yet a crisis")
            s = t.fresh(oil=5, wind=[4])
            self._hits.clear()
            t.advance(s, turn=2, chances=[0.99])
            t.ok("oil_crisis" in self._hits, "oil at exactly 2 is a crisis")
            s = t.fresh(oil=9, wind=[0], shield=0, signal=3)
            t.advance(s, turn=2, chances=[0.99])
            t.ok(s["shield"] is None and s["signal"] == 0, "the shield and the signal last one night")

        def r5(t):
            s = t.fresh(hidden__stride=2, hidden__pos=0, wind=[0], lit=[True] * 5)
            events = t.advance(s, turn=2, chances=[0.99])
            t.ok(not s["lit"][0], "an unshielded lit lantern under the wind goes out")
            t.eq(s["wind"], [2], "the wind steps by its stride")
            t.has(events, "The wind snuffed lantern 1.")
            t.has(events, "Wind building on lantern 3.")
            s = t.fresh(hidden__stride=2, hidden__pos=3, wind=[4])
            events = t.advance(s, turn=2, chances=[0.99])
            t.has(events, "The wind found lantern 5 already dark.")
            s = t.fresh(hidden__stride=2, hidden__pos=0, wind=[0])
            t.advance(s, turn=2, chances=[0.0])
            t.eq(s["wind"], [0], "a stall leaves the wind where it was")
            self._hits.clear()
            s = t.fresh(hidden__stride=2, hidden__pos=0, wind=[0], lit=[True] * 5)
            t.advance(s, turn=2, chances=[0.99])
            t.ok("lantern1_out" in self._hits, "losing lantern 1 is noted")
            s = t.fresh(hidden__stride=2, hidden__pos=0, wind=[1], lit=[True] * 5)
            self._hits.clear()
            t.advance(s, turn=2, chances=[0.99])
            t.ok("lantern1_out" not in self._hits, "losing lantern 2 is not")

        def r6(t):
            s = t.fresh(wind=[4])
            t.advance(s, turn=C["STORM_NIGHT"] - 2, chances=[0.99])
            t.eq(len(s["wind"]), 1, "one target before the storm")
            t.ok("storm" not in self._hits, "no storm yet")
            s = t.fresh(wind=[4])
            events = t.advance(s, turn=C["STORM_NIGHT"] - 1, chances=[0.99, 0.99])
            t.eq(len(s["wind"]), 2, "two targets from the storm night")
            t.has(events, f"Night {C['STORM_NIGHT']}: the storm arrives.")
            t.ok(any(e.startswith("Wind building on lantern ") and " and lantern " in e for e in events), "the storm shows two targets")
            t.ok("storm" in self._hits, "the storm is noted")
            t.ok("Wind" in self.status_line(s), "the target is shown in the status line")

        def r7(t):
            s = t.fresh(lit=[True, True, False, True, True], wind=[2], oil=30)
            c0 = s["column"]
            t.advance(s, turn=2, chances=[0.99])
            t.eq(s["column"] - c0, 2, "only the run from lantern 1 counts")
            s = t.fresh(oil=30, wind=[4])
            s["_turn"] = C["SIGNAL_NIGHT"] - 1
            t.ok(not t.offered(s, "signal", oil=C["SIGNAL_COST"]), "no signal before its night")
            s["_turn"] = C["SIGNAL_NIGHT"]
            t.ok(t.offered(s, "signal", oil=C["SIGNAL_COST"]), "signal offered from its night")
            t.ok(not t.offered(s, "signal", oil=C["SIGNAL_COST"] + 1), "only the two stated prices are allowed")
            t.apply(s, "signal", {"oil": C["SIGNAL_COST"]})
            t.eq(s["oil"], 30 - C["SIGNAL_COST"], "the small signal costs SIGNAL_COST")
            c0 = s["column"]
            events = t.advance(s, turn=C["SIGNAL_NIGHT"] + 1, chances=[0.99])
            t.eq(s["column"] - c0, 6, "the small signal doubles the advance (run of 3, doubled)")
            t.has(events, "The column advanced 6 (3 lit in a row, times 2).")
            s = t.fresh(oil=30, wind=[4])
            s["_turn"] = C["SIGNAL_NIGHT"]
            t.apply(s, "signal", {"oil": C["SIGNAL_MAX"]})
            t.eq(s["oil"], 30 - C["SIGNAL_MAX"], "the big signal costs SIGNAL_MAX")
            c0 = s["column"]
            events = t.advance(s, turn=C["SIGNAL_NIGHT"] + 1, chances=[0.99])
            t.eq(s["column"] - c0, 9, "the big signal triples the advance")
            t.has(events, "The column advanced 9 (3 lit in a row, times 3).")
            s = t.fresh(oil=C["SIGNAL_COST"], wind=[4])
            s["_turn"] = C["SIGNAL_NIGHT"]
            t.ok(not t.offered(s, "signal", oil=C["SIGNAL_MAX"]), "the big signal needs the oil")
            s = t.fresh(oil=C["SIGNAL_MAX"], wind=[4])
            s["_turn"] = C["SIGNAL_NIGHT"]
            t.ok(t.offered(s, "signal", oil=C["SIGNAL_MAX"]), "exactly enough oil is enough")

        def r8(t):
            s = t.fresh(oil=5, fails=2, wind=[4])
            t.ok(t.offered(s, "sled"), "sled offered after two failed hauls")
            t.apply(s, "sled")
            t.eq(s["oil"], 5 + C["SLED_GAIN"], "the sled brings a sure amount")
            t.ok(s["sled_used"] and s["fails"] == 0, "the sled is spent and the failed-haul count resets")
            t.ok(not t.offered(s, "sled"), "once only")
            s = t.fresh(column=C["GOAL"])
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "reaching the goal wins")
            t.eq(self.turns, C["NIGHTS"], "the turn budget is NIGHTS")
            s = t.fresh(column=C["GOAL"] - 1)
            s["_turn"] = C["NIGHTS"]
            t.ok(self.check_end(s) is None, "the last night is still played")
            end = self.final_check(s)
            t.ok(end["result"] == "loss" and str(C["GOAL"]) in end["reason"], "short of the goal after the last night is a loss")
            s = t.fresh(column=0, oil=60, wind=[4])
            s["_turn"] = C["NIGHTS"]
            s, _ = t.step(s, "haul")
            t.ok(s["_ended"] and s["_ended"]["phase"] == "budget" and s["_turn"] == C["NIGHTS"] + 1, "the budget ends the game after the last night's dusk")
            s = t.fresh(oil=5, fails=1, wind=[4])
            t.ok(not t.offered(s, "sled"), "one failed haul does not bring the sled")

        return [
            (1, "one action a night", r1), (2, "light and shield", r2), (3, "haul", r3),
            (4, "start oil, burn, loss", r4), (5, "the wind", r5), (6, "tell and storm", r6),
            (7, "column and signal", r7), (8, "sled and goal", r8),
        ]

    def resample_hidden(self, s, rng):
        """The wind's stride is hidden. A player who has watched three strikes can infer it; before that, redraw it."""
        if len(s["seen"]) < self.C["_SEEN_NEEDED"]:
            s["hidden"]["stride"] = rng.d(self.C["_STRIDES"])

    def init_state(self, rng):
        C = self.C
        L = C["LANTERNS"]
        pos = rng.d(L) - 1
        return {
            "oil": C["START_OIL"],
            "column": 0,
            "lit": [i < C["_START_LIT"] for i in range(L)],
            "wind": [pos],
            "seen": [pos],
            "shield": None,
            "signal": 0,
            "fails": 0,
            "sled_used": False,
            "hidden": {"stride": rng.d(C["_STRIDES"]), "pos": pos},
        }

    def options(self, s):
        C = self.C
        o = []
        for i, on in enumerate(s["lit"]):
            if not on and s["oil"] >= C["LIGHT_COST"]:
                o.append({"id": "light", "label": f"Light lantern {i + 1} (-{C['LIGHT_COST']} oil)",
                          "args": {"lantern": i}, "group": "Light a dark lantern"})
        for i in s["wind"]:
            if s["lit"][i]:
                o.append({"id": "shield", "label": f"Shield lantern {i + 1} from tonight's wind",
                          "args": {"lantern": i}, "group": "Shield a lantern"})
        o.append({"id": "haul", "label": f"Haul oil from the depot (roll {C['HAUL_NEED']}+ for +{C['HAUL_GAIN']})",
                  "args": {}})
        if s["oil"] >= C["WINDBREAK_COST"] and any(s["lit"][i] for i in s["wind"]):
            o.append({"id": "windbreak", "args": {},
                      "label": f"Raise a windbreak (-{C['WINDBREAK_COST']} oil, roll {C['WINDBREAK_NEED']}+: the wind snuffs nothing tonight)"})
        if s["_turn"] >= C["SIGNAL_NIGHT"] and s["oil"] >= C["SIGNAL_COST"]:
            spend = [c for c in (C["SIGNAL_COST"], C["SIGNAL_MAX"]) if s["oil"] >= c]
            o.append({"id": "signal", "label": "Signal a rush (spend oil: double or triple tonight's advance)",
                      "args": {}, "params": {"oil": {"choices": spend}}})
        if s["fails"] >= 2 and not s["sled_used"]:
            o.append({"id": "sled", "label": f"Call the depot sled (sure +{C['SLED_GAIN']} oil, once)", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "light":
            s["oil"] -= C["LIGHT_COST"]
            s["lit"][args["lantern"]] = True
            ev.append(f"Lantern {args['lantern'] + 1} lit.")
        elif a == "shield":
            s["shield"] = args["lantern"]
            ev.append(f"Lantern {args['lantern'] + 1} shielded for the night.")
        elif a == "haul":
            ok, txt = rng.check(C["HAUL_NEED"], C["DIE"], "haul")
            if ok:
                s["oil"] += C["HAUL_GAIN"]
                s["fails"] = 0
                ev.append(f"{txt}. Oil +{C['HAUL_GAIN']}.")
            else:
                s["oil"] += C["HAUL_FAIL"]
                s["fails"] += 1
                ev.append(f"{txt}. Oil +{C['HAUL_FAIL']}.")
        elif a == "windbreak":
            s["oil"] -= C["WINDBREAK_COST"]
            ok, txt = rng.check(C["WINDBREAK_NEED"], C["DIE"], "windbreak")
            if ok:
                s["wind"] = []  # the rival's move is undone: this is what makes it a rival gambit
                self.hit("windbreak")
                ev.append(f"{txt}. The wind turns on the windbreak. Nothing is snuffed tonight.")
            else:
                ev.append(f"{txt}. The windbreak collapses before dusk.")
        elif a == "signal":
            s["oil"] -= args["oil"]
            s["signal"] = 3 if args["oil"] == C["SIGNAL_MAX"] else 2  # lit-ok: triple or double, as the sheet says
            self.hit("signal")
            ev.append(f"Signal sent for {args['oil']} oil. The column will rush tonight.")
        elif a == "sled":
            s["oil"] += C["SLED_GAIN"]
            s["sled_used"] = True
            s["fails"] = 0
            self.hit("sled")
            ev.append(f"The sled arrives. Oil +{C['SLED_GAIN']}.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        # wind hits tonight's targets (none, if a windbreak turned it)
        if not s["wind"]:
            ev.append("The windbreak held: no lantern was snuffed.")
        for i in s["wind"]:
            if not s["lit"][i]:
                ev.append(f"The wind found lantern {i + 1} already dark.")
            elif s["shield"] == i:
                ev.append(f"The wind leaned on lantern {i + 1}. The shield held.")
            else:
                s["lit"][i] = False
                ev.append(f"The wind snuffed lantern {i + 1}.")
                if i == 0:
                    self.hit("lantern1_out")
        # column advances along the unbroken run from lantern 1
        run_len = 0
        for on in s["lit"]:
            if not on:
                break
            run_len += 1
        mult = s["signal"] or 1
        gain = run_len * mult
        s["column"] += gain
        ev.append(f"The column advanced {gain} ({run_len} lit in a row{f', times {mult}' if mult > 1 else ''}).")
        # dusk burn
        burn = sum(1 for on in s["lit"] if on)
        s["oil"] -= burn
        ev.append(f"Dusk: {plural(burn, 'lit lantern')} burned {burn} oil.")
        if s["oil"] < 0:
            self.finish(s, "loss", "oil ran out, every lantern went dark")
            return ev  # nothing after a fatal event: no tells for a tomorrow that will not come
        if s["oil"] <= C["_CRISIS"]:
            self.hit("oil_crisis")
        s["shield"] = None
        s["signal"] = 0
        # the wind picks tomorrow's target(s) and shows them
        h = s["hidden"]
        tomorrow = s["_turn"] + 1
        count = 2 if tomorrow >= C["STORM_NIGHT"] else 1
        if tomorrow == C["STORM_NIGHT"]:
            self.hit("storm")
            ev.append(f"Night {tomorrow}: the storm arrives. The wind will snuff two lanterns a night.")
        L = C["LANTERNS"]
        targets = []
        for _ in range(count):
            if rng.chance(C["STALL_P"]):
                self.hit("stall")
            else:
                h["pos"] = (h["pos"] + h["stride"]) % L
            targets.append(h["pos"])
        s["wind"] = sorted(set(targets))
        s["seen"] = (s["seen"] + [targets[-1]])[-C["_SEEN_KEPT"]:]
        ev.append("Wind building on " + " and ".join(f"lantern {i + 1}" for i in s["wind"]) + ".")
        return ev

    def status_line(self, s):
        ridge = "".join("#" if on else "." for on in s["lit"])
        wind = ",".join(str(i + 1) for i in s["wind"]) or "-"
        return f"Oil {s['oil']} | Column {s['column']}/{self.C['GOAL']} | Ridge {ridge} | Wind {wind}"

    def check_end(self, s):
        if s["column"] >= self.C["GOAL"]:
            return {"result": "win", "reason": f"column reached {s['column']}"}
        if s["oil"] < 0:
            return {"result": "loss", "reason": "oil ran out, every lantern went dark"}
        return None

    def final_check(self, s):
        return {"result": "loss", "reason": f"column stopped at {s['column']}, needed {self.C['GOAL']}"}

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        burn = sum(1 for on in s["lit"] if on)
        run_len = 0
        for on in s["lit"]:
            if not on:
                break
            run_len += 1
        if "sled" in ids and s["oil"] < burn + 4:
            return "sled"
        if s["oil"] <= burn + 1:
            return "haul"
        threatened = [i for i in s["wind"] if s["lit"][i] and i < run_len]
        if "windbreak" in ids and len(threatened) >= 2 and s["oil"] >= burn + C["WINDBREAK_COST"] + 2:
            return "windbreak"  # a shield saves one lantern; in the storm the windbreak can save both
        for o in options:
            if o["id"] == "shield" and o["args"]["lantern"] < run_len:
                return o
        if "signal" in ids and run_len >= 3 and s["oil"] >= burn + C["SIGNAL_COST"] + 1:
            big = run_len >= 4 and s["oil"] >= burn + C["SIGNAL_MAX"] + 3
            return {"id": "signal", "args": {"oil": C["SIGNAL_MAX"] if big else C["SIGNAL_COST"]}}
        darks = [o for o in options if o["id"] == "light"]
        if darks and s["oil"] >= burn + C["LIGHT_COST"] + 3:
            return min(darks, key=lambda o: o["args"]["lantern"])
        return "haul"


if __name__ == "__main__":
    run(G)
