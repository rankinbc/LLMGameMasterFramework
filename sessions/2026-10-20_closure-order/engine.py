"""Closure Order: a squadron outruns the Bureau's lane closures down a chain of jump gates.

One tracked number (fuel). Each turn one plain order: hop, skip, hold and siphon, or (late, once) seal the gate behind.
The rival is a schedule: the Closure Order advances by a hidden repeating pattern, and tells you after it lands.
The twist is the lane tide: it flips every few turns and swaps which jumps are cheap.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402


class G(Game):
    name = "Closure Order"

    CONSTANTS = {
        "TURNS": 12,
        "GATES": 12,
        "START_POS": 4,
        "START_CLOSE": 1,
        "START_FUEL": 6,
        "SIPHON_MIN": 2,
        "SIPHON_MAX": 4,
        "SYSTEMS": 1,
        "TIDE_EVERY": 5,
        "HOP_LOW": 2,
        "HOP_HIGH": 4,
        "SKIP_LOW": 5,
        "SKIP_HIGH": 3,
        "CLOSE_STEP": 1,
        "PERIOD": 3,
        "SEAL_TURN": 7,
        "SEAL_COST": 2,
        "SEAL_DUSKS": 2,
    }

    RULES = """
1. You command a squadron fleeing down {GATES} jump gates, from Gate {START_POS} to Gate {GATES}. Each turn give one order: hop one gate, leap two gates, or hold and siphon {SIPHON_MIN} to {SIPHON_MAX} fuel (random) from the depot, which never runs dry.
2. A hop burns {HOP_LOW} fuel at low tide and {HOP_HIGH} at high tide; a leap burns {SKIP_LOW} at low tide and {SKIP_HIGH} at high tide. The tide alternates in blocks of {TIDE_EVERY|turn}: low first, then high, then low again.
3. You start with {START_FUEL} fuel. A move that costs more than the fuel you have is not offered.
4. Each dusk, the end of a turn, life support burns {SYSTEMS} fuel. If fuel is then below 0 the squadron drifts dry and you lose; exactly 0 is safe. So a move that leaves you with less than {SYSTEMS} fuel loses at dusk.
5. The Bureau's Closure Order shuts the lane behind you, starting at Gate {START_CLOSE}. Each dusk, whatever you did, it advances {CLOSE_STEP|gate}, except one dusk in every {PERIOD} when it stalls for paperwork. The stalls follow a fixed rhythm you learn by watching.
6. From turn {SEAL_TURN}, once, you may lock the gate behind you instead of moving, for {SEAL_COST} fuel. The Bureau's crews take {SEAL_DUSKS|dusk} to cut through, so the Closure Order stands still for that long, this turn's dusk first; its stall rhythm then resumes.
7. Reach Gate {GATES} on any turn, the last included, and the squadron is through: you win. If the Closure Order reaches or passes your gate, or the {TURNS} turns run out first, you lose.
"""

    ACTIONS = ["hop", "skip", "hold", "seal"]
    TAGS = ["tide_flip", "seal", "closure_stall"]
    TRACKED = ["fuel"]

    BOUNDS = {"fuel": (-10, 80), "pos": (1, 12), "close": (1, 14)}
    DERIVED = {"lead": lambda g, s: s["pos"] - s["close"]}
    REACH = {"pos": "GATES", "fuel": ("<=", -1), "lead": ("<=", 0)}
    GATES = {
        "hop": {"_if": lambda g, s: s["pos"] < g.C["GATES"] and s["fuel"] >= g._cost("hop", s["_turn"])},
        "skip": {"_if": lambda g, s: s["pos"] <= g.C["GATES"] - 2 and s["fuel"] >= g._cost("skip", s["_turn"])},  # lit-ok: a skip is two gates
        "seal": {"fuel": "SEAL_COST", "_turn": "SEAL_TURN", "!seal_used": 1},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------------ helpers

    def _high(self, turn):
        """The tide on this turn: low for the first TIDE_EVERY turns, then high, and so on."""
        return ((turn - 1) // self.C["TIDE_EVERY"]) % 2 == 1  # lit-ok: two tides

    def _cost(self, order, turn):
        key = ("HOP" if order == "hop" else "SKIP") + ("_HIGH" if self._high(turn) else "_LOW")
        return self.C[key]

    def _cycle(self):
        """The Closure Order's pattern: CLOSE_STEP gates on all but one dusk of the period, and a stall (0) on the last."""
        C = self.C
        return [C["CLOSE_STEP"]] * (C["PERIOD"] - 1) + [0]  # lit-ok: the stall

    def _worst_next(self, s):
        """Biggest next Closure step consistent with the steps the player has seen."""
        C = self.C
        cyc = self._cycle()
        seen = s["seen"]
        phases = [p for p in range(C["PERIOD"]) if all(cyc[(p + i) % C["PERIOD"]] == a for i, a in enumerate(seen))]
        nxt = [cyc[(p + len(seen)) % C["PERIOD"]] for p in phases] or [max(cyc)]
        return max(nxt)

    def _loss(self, s):
        """The loss the state is in, dry first, or None."""
        if s["fuel"] < 0:
            return f"the squadron ran dry at Gate {s['pos']} and drifted"
        if s["close"] >= s["pos"]:
            return f"the Closure Order reached Gate {s['pos']} and shut the lane around the squadron"
        return None

    def resample_hidden(self, s, rng):
        """The Closure Order's phase is hidden. The steps the player has seen narrow it; redraw among the rest."""
        C = self.C
        cyc = self._cycle()
        seen = s["seen"]
        phases = [p for p in range(C["PERIOD"]) if all(cyc[(p + i) % C["PERIOD"]] == a for i, a in enumerate(seen))]
        if phases:
            s["hidden"]["phase"] = rng.choice(phases)

    # ------------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        cyc = self._cycle()

        def r1(t):
            s = t.fresh()
            t.eq(t.ids(s), ["hold", "hop", "skip"], "hop, skip and hold on turn 1")
            t.eq(t.label(s, "hop"), f"Hop one gate to Gate {C['START_POS'] + 1} (burns {C['HOP_LOW']} fuel)", "the hop label counts gates")
            t.eq(t.label(s, "skip"), f"Leap two gates to Gate {C['START_POS'] + 2} (burns {C['SKIP_LOW']} fuel)", "the skip label counts gates")
            t.eq(t.label(s, "hold"), f"Hold at Gate {C['START_POS']} and siphon {C['SIPHON_MIN']} to {C['SIPHON_MAX']} fuel (random)", "the hold label")
            t.eq(t.status(s), f"Fuel {C['START_FUEL']} | Gate {C['START_POS']}/{C['GATES']} | Closure: Gate {C['START_CLOSE']} | Tide: low", "the status line")
            span = C["SIPHON_MAX"] - C["SIPHON_MIN"] + 1  # lit-ok: both ends are possible
            s = t.fresh()
            events = t.apply(s, "hold", dice=[1])
            t.eq(s["fuel"], C["START_FUEL"] + C["SIPHON_MIN"], "the smallest yield")
            t.eq(s["pos"], C["START_POS"], "holding stays put")
            t.has(events, f"siphons {C['SIPHON_MIN']} fuel")
            s = t.fresh()
            events = t.apply(s, "hold", dice=[span])
            t.eq(s["fuel"], C["START_FUEL"] + C["SIPHON_MAX"], "the largest yield")
            t.has(events, f"siphons {C['SIPHON_MAX']} fuel")
            s = t.fresh()
            events = t.apply(s, "hop")
            t.eq(s["pos"], C["START_POS"] + 1, "a hop is one gate")
            t.has(events, f"Gate {C['START_POS'] + 1}")
            s = t.fresh()
            events = t.apply(s, "skip")
            t.eq(s["pos"], C["START_POS"] + 2, "a skip is two gates")
            t.has(events, f"Gate {C['START_POS'] + 2}")
            s = t.fresh(pos=C["GATES"] - 2, fuel=20)
            t.ok(t.offered(s, "skip"), "a skip is offered with two gates to go")
            s = t.fresh(pos=C["GATES"] - 1, fuel=20)
            t.ok(not t.offered(s, "skip") and t.offered(s, "hop"), "no skip past the last gate")
            s2, _ = t.step(t.fresh(), "hold")
            t.eq(s2["_turn"], 2, "one order ends the turn")

        def r2(t):
            for turn, high in ((1, False), (C["TIDE_EVERY"], False), (C["TIDE_EVERY"] + 1, True), (2 * C["TIDE_EVERY"], True), (2 * C["TIDE_EVERY"] + 1, False)):  # lit-ok: the second flip
                hop = C["HOP_HIGH"] if high else C["HOP_LOW"]
                skip = C["SKIP_HIGH"] if high else C["SKIP_LOW"]
                s = t.fresh(fuel=30)
                s["_turn"] = turn
                t.eq(t.label(s, "hop"), f"Hop one gate to Gate {C['START_POS'] + 1} (burns {hop} fuel)", f"hop label on turn {turn}")
                t.apply(s, "hop")
                t.eq(s["fuel"], 30 - hop, f"hop cost on turn {turn}")
                s = t.fresh(fuel=30)
                s["_turn"] = turn
                t.apply(s, "skip")
                t.eq(s["fuel"], 30 - skip, f"skip cost on turn {turn}")
            s = t.fresh()
            t.ok("Tide: low" in t.status(s), "the tide starts low")
            s["_turn"] = C["TIDE_EVERY"] + 1
            t.ok("Tide: high" in t.status(s), "the tide is high after the flip")
            s = t.fresh(fuel=30)
            self._hits.clear()
            events = t.advance(s, turn=C["TIDE_EVERY"])
            t.has(events, f"The tide turns high: next turn a hop burns {C['HOP_HIGH']} and a leap burns {C['SKIP_HIGH']}.")
            t.ok("tide_flip" in self._hits, "the flip is noted")
            s = t.fresh(fuel=30)
            events = t.advance(s, turn=C["TIDE_EVERY"] - 1)
            t.ok(not any("The tide turns" in e for e in events), "no flip a turn early")
            s = t.fresh(fuel=30)
            events = t.advance(s, turn=2 * C["TIDE_EVERY"])  # lit-ok: the second flip
            t.has(events, f"The tide turns low: next turn a hop burns {C['HOP_LOW']} and a leap burns {C['SKIP_LOW']}.")

        def r3(t):
            s = t.fresh()
            t.eq(s["fuel"], C["START_FUEL"], "starting fuel")
            s = t.fresh(fuel=C["HOP_LOW"] - 1)
            t.ok(not t.offered(s, "hop"), "a hop that costs more than the fuel you have is not offered")
            s = t.fresh(fuel=C["HOP_LOW"])
            t.ok(t.offered(s, "hop"), "a hop that costs exactly the fuel you have is offered")
            s = t.fresh(fuel=C["SKIP_LOW"] - 1)
            t.ok(not t.offered(s, "skip"), "a leap that costs more than the fuel you have is not offered")
            s = t.fresh(fuel=0)
            t.eq(t.ids(s), ["hold"], "with no fuel only holding is left")

        def r3b(t):
            s = t.fresh(fuel=6, pos=5, close=1)
            events = t.advance(s, turn=2)
            t.eq(s["fuel"], 6 - C["SYSTEMS"], "life support burns at dusk")
            t.has(events, f"Dusk: life support burns {C['SYSTEMS']} fuel.")
            s = t.fresh(fuel=C["SYSTEMS"], pos=5, close=1)
            t.advance(s, turn=2)
            t.eq(s["fuel"], 0, "burning down to exactly zero")
            t.ok(self.check_end(s) is None and not s.get("_ended"), "exactly zero fuel is still alive")
            s = t.fresh(fuel=C["SYSTEMS"] - 1, pos=5, close=1)
            events = t.advance(s, turn=2)
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss" and "ran dry at Gate 5" in s["_ended"]["reason"], "fuel under zero at dusk is a loss")
            t.ok(not any("Closure Order" in e for e in events), "nothing after a fatal event")

        def r4(t):
            s0 = t.fresh()
            t.eq(s0["close"], C["START_CLOSE"], "the Closure Order starts at its gate")
            t.eq({t.fresh(seed=i)["hidden"]["phase"] for i in range(1, 80)}, set(range(C["PERIOD"])), "the pattern can start anywhere in its cycle")
            s = t.fresh(pos=9, close=1, fuel=60, hidden__phase=0, hidden__k=0)  # lit-ok: far ahead of the Closure Order
            steps = []
            for i in range(C["PERIOD"]):
                before = s["close"]
                events = t.advance(s, turn=2 + i)
                steps.append(s["close"] - before)
                if steps[-1]:
                    t.has(events, f"shuts {plural(steps[-1], 'gate')} and now stands at Gate {s['close']}.")
                else:
                    t.has(events, f"stalls for paperwork and stays at Gate {s['close']}.")
            t.eq(steps, cyc, "the pattern follows the cycle")
            t.eq(steps.count(0), 1, "one stall a period")  # lit-ok: one stall
            t.eq(steps.count(C["CLOSE_STEP"]), C["PERIOD"] - 1, "every other dusk advances")  # lit-ok: one stall
            t.eq(s["seen"], cyc, "the steps the player has seen are kept")
            s = t.fresh(pos=9, close=1, fuel=60, hidden__phase=C["PERIOD"] - 1, hidden__k=0)  # lit-ok: start at the stall
            self._hits.clear()
            t.advance(s, turn=2)
            t.ok("closure_stall" in self._hits, "the stall is noted")
            s = t.fresh(seen=[C["CLOSE_STEP"], C["CLOSE_STEP"]])
            t.eq(self._worst_next(s), 0, "after two advances the stall is next")  # lit-ok: the stall
            self.resample_hidden(s, t.rng())
            t.eq(s["hidden"]["phase"], 0, "the pattern is narrowed by what was seen")  # lit-ok: the only consistent phase
            t.eq(self._worst_next(t.fresh()), C["CLOSE_STEP"], "before anything is seen the worst case is an advance")
            s = t.fresh(pos=4, close=3, fuel=20, hidden__phase=0, hidden__k=0)  # lit-ok: just behind
            t.advance(s, turn=2)
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss" and "reached Gate 4 and shut the lane" in s["_ended"]["reason"], "reaching your gate is a loss")
            s = t.fresh(pos=5, close=3, fuel=20, hidden__phase=0, hidden__k=0)  # lit-ok: one gate to spare
            t.advance(s, turn=2)
            t.ok(not s.get("_ended"), "one gate behind is still alive")
            s = t.fresh(pos=4, close=3, fuel=0, hidden__phase=0, hidden__k=0)  # lit-ok: both fatal at once
            t.advance(s, turn=2)
            t.ok(s["_ended"] and "ran dry" in s["_ended"]["reason"], "dry comes before the Closure Order")

        def r5(t):
            s = t.fresh(fuel=20, hidden__phase=0, hidden__k=0)  # lit-ok: first step is an advance
            s["_turn"] = C["SEAL_TURN"] - 1
            t.ok(not t.offered(s, "seal"), "no seal before its turn")
            s["_turn"] = C["SEAL_TURN"]
            t.ok(t.offered(s, "seal"), "seal offered from its turn")
            t.eq(t.label(s, "seal"), f"Lock the gate behind you (burns {C['SEAL_COST']} fuel; the Bureau's crews need {plural(C['SEAL_DUSKS'], 'dusk')} to cut through)", "the seal label")
            s2 = t.fresh(fuel=C["SEAL_COST"])
            s2["_turn"] = C["SEAL_TURN"]
            t.ok(t.offered(s2, "seal"), "exactly enough fuel is enough")
            s2 = t.fresh(fuel=C["SEAL_COST"] - 1)
            s2["_turn"] = C["SEAL_TURN"]
            t.ok(not t.offered(s2, "seal"), "not without the fuel")
            self._hits.clear()
            events = t.apply(s, "seal")
            t.eq(s["fuel"], 20 - C["SEAL_COST"], "the seal costs fuel")  # lit-ok: test fuel
            t.eq(s["pos"], C["START_POS"], "sealing does not move you")
            t.has(events, f"Lock: the squadron locks the gate behind it, burning {C['SEAL_COST']} fuel.")
            t.ok("seal" in self._hits, "the seal is noted")
            c0, k0 = s["close"], s["hidden"]["k"]
            for i in range(C["SEAL_DUSKS"]):
                events = t.advance(s, turn=C["SEAL_TURN"] + i)
                t.eq(s["close"], c0, f"the Closure Order does not advance at sealed dusk {i + 1}")  # lit-ok: 1-based
                t.eq(s["hidden"]["k"], k0, "its pattern waits")
                t.has(events, "The locked gate holds the Closure Order at this dusk.")
            t.ok(not t.offered(s, "seal"), "once only")
            t.advance(s, turn=C["SEAL_TURN"] + C["SEAL_DUSKS"])
            t.ok(s["close"] > c0, "the dusk after the seal advances again")

        def r6(t):
            end = self.check_end(t.fresh(pos=C["GATES"]))
            t.ok(end and end["result"] == "win" and f"Gate {C['GATES']}" in end["reason"], "reaching the last gate wins")
            s2, _ = t.step(t.fresh(pos=C["GATES"] - 1, fuel=10), "hop")  # lit-ok: test fuel
            t.ok(s2["_ended"] and s2["_ended"]["result"] == "win", "a hop through the last gate wins")
            s2, _ = t.step(t.fresh(pos=C["GATES"] - 2, fuel=10), "skip")  # lit-ok: test fuel
            t.ok(s2["_ended"] and s2["_ended"]["result"] == "win", "a skip through the last gate wins")
            t.eq(self.turns, C["TURNS"], "the turn budget is TURNS")
            s = t.fresh(pos=5, close=1, fuel=40)  # lit-ok: test numbers
            s["_turn"] = C["TURNS"]
            t.ok(self.check_end(s) is None, "the last turn is still played")
            end = self.final_check(s)
            t.ok(end["result"] == "loss" and f"{C['TURNS']} turns ran out" in end["reason"], "running out of turns is a loss")
            s2, _ = t.step(s, "hold")
            t.ok(s2["_ended"] and s2["_ended"]["phase"] == "budget" and s2["_turn"] == C["TURNS"] + 1, "the budget ends the game after the last dusk")

        return [
            (1, "orders", r1), (2, "tide", r2), (3, "start fuel", r3),
            (4, "life support", r3b), (5, "the Closure Order", r4), (6, "lock", r5), (7, "win and turn limit", r6),
        ]

    # ------------------------------------------------------------------ the game

    def init_state(self, rng):
        C = self.C
        return {
            "fuel": C["START_FUEL"],
            "pos": C["START_POS"],
            "close": C["START_CLOSE"],
            "seal": 0,
            "seal_used": False,
            "seen": [],
            "hidden": {"phase": rng.d(C["PERIOD"]) - 1, "k": 0},  # lit-ok: d() counts from 1
        }

    def options(self, s):
        C = self.C
        t = s["_turn"]
        o = []
        if s["pos"] < C["GATES"] and s["fuel"] >= self._cost("hop", t):
            o.append({"id": "hop", "label": f"Hop one gate to Gate {s['pos'] + 1} (burns {self._cost('hop', t)} fuel)", "args": {}})
        if s["pos"] <= C["GATES"] - 2 and s["fuel"] >= self._cost("skip", t):  # lit-ok: a skip is two gates
            o.append({"id": "skip", "label": f"Leap two gates to Gate {s['pos'] + 2} (burns {self._cost('skip', t)} fuel)", "args": {}})  # lit-ok: a skip is two gates
        o.append({"id": "hold", "label": f"Hold at Gate {s['pos']} and siphon {C['SIPHON_MIN']} to {C['SIPHON_MAX']} fuel (random)", "args": {}})
        if t >= C["SEAL_TURN"] and not s["seal_used"] and s["fuel"] >= C["SEAL_COST"]:
            o.append({"id": "seal", "label": f"Lock the gate behind you (burns {C['SEAL_COST']} fuel; the Bureau's crews need {plural(C['SEAL_DUSKS'], 'dusk')} to cut through)", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        t = s["_turn"]
        ev = []
        if a == "hop":
            cost = self._cost("hop", t)
            s["fuel"] -= cost
            s["pos"] += 1  # lit-ok: one gate
            ev.append(f"Hop: the squadron moves to Gate {s['pos']} and burns {cost} fuel.")
        elif a == "skip":
            cost = self._cost("skip", t)
            s["fuel"] -= cost
            s["pos"] += 2  # lit-ok: two gates
            ev.append(f"Leap: the squadron leaps to Gate {s['pos']} and burns {cost} fuel.")
        elif a == "hold":
            got = C["SIPHON_MIN"] + rng.d(C["SIPHON_MAX"] - C["SIPHON_MIN"] + 1) - 1  # lit-ok: d() counts from 1
            s["fuel"] += got
            ev.append(f"Hold: the squadron siphons {got} fuel at Gate {s['pos']}.")
        elif a == "seal":
            s["fuel"] -= C["SEAL_COST"]
            s["seal"] = C["SEAL_DUSKS"]
            s["seal_used"] = True
            self.hit("seal")
            ev.append(f"Lock: the squadron locks the gate behind it, burning {C['SEAL_COST']} fuel.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        s["fuel"] -= C["SYSTEMS"]
        ev.append(f"Dusk: life support burns {C['SYSTEMS']} fuel.")
        reason = self._loss(s)
        if reason and s["fuel"] < 0:
            self.finish(s, "loss", reason)
            return ev  # nothing after a fatal event
        h = s["hidden"]
        if s["seal"] > 0:  # lit-ok: sealed dusks left
            s["seal"] -= 1  # lit-ok: one dusk used
            ev.append("The locked gate holds the Closure Order at this dusk.")
        else:
            step = self._cycle()[(h["phase"] + h["k"]) % C["PERIOD"]]
            h["k"] += 1  # lit-ok: one step of the pattern
            s["close"] += step
            s["seen"] = s["seen"] + [step]
            if step:
                ev.append(f"The Closure Order shuts {plural(step, 'gate')} and now stands at Gate {s['close']}.")
            else:
                self.hit("closure_stall")
                ev.append(f"The Closure Order stalls for paperwork and stays at Gate {s['close']}.")
        reason = self._loss(s)
        if reason:
            self.finish(s, "loss", reason)
            return ev
        t = s["_turn"]
        if t % C["TIDE_EVERY"] == 0 and t < C["TURNS"]:
            high = self._high(t + 1)  # lit-ok: tomorrow
            hop = C["HOP_HIGH"] if high else C["HOP_LOW"]
            skip = C["SKIP_HIGH"] if high else C["SKIP_LOW"]
            self.hit("tide_flip")
            ev.append(f"The tide turns {'high' if high else 'low'}: next turn a hop burns {hop} and a leap burns {skip}.")
        return ev

    def visible(self, s):
        return {"fuel": s["fuel"], "gate": s["pos"], "closure": s["close"], "gap": s["pos"] - s["close"], "high_tide": self._high(s["_turn"])}

    def status_line(self, s):
        tide = "high" if self._high(s["_turn"]) else "low"
        return f"Fuel {s['fuel']} | Gate {s['pos']}/{self.C['GATES']} | Closure: Gate {s['close']} | Tide: {tide}"

    def check_end(self, s):
        if s["pos"] >= self.C["GATES"]:
            return {"result": "win", "reason": f"the squadron passed Gate {self.C['GATES']} and the Bureau lost the file"}
        reason = self._loss(s)
        if reason:
            return {"result": "loss", "reason": reason}
        return None

    def final_check(self, s):
        return {"result": "loss", "reason": f"the {self.C['TURNS']} turns ran out with the squadron at Gate {s['pos']}"}

    def heuristic(self, s, options, rng):
        C = self.C
        t = s["_turn"]
        ids = {o["id"] for o in options}
        w = self._worst_next(s)
        moves = []
        for oid, gates in (("hop", 1), ("skip", 2)):  # lit-ok: gates per order
            if oid in ids:
                cost = self._cost(oid, t)
                new_pos = s["pos"] + gates
                if new_pos >= C["GATES"]:
                    return oid
                dies = s["fuel"] - cost - C["SYSTEMS"] < 0
                moves.append((oid, cost, gates, new_pos - (s["close"] + w), dies))
        hold_lead = s["pos"] - (s["close"] + w)
        safe = [m for m in moves if m[3] >= 1 and not m[4]]  # lit-ok: stay a gate clear
        if safe:
            if hold_lead >= 1 and s["fuel"] < C["SYSTEMS"] + C["SIPHON_MIN"]:  # lit-ok: stay a gate clear
                return "hold"
            return min(safe, key=lambda m: (m[1] / m[2], -m[2]))[0]
        if "seal" in ids and hold_lead < 1:  # lit-ok: stay a gate clear
            return "seal"
        if hold_lead >= 1:  # lit-ok: stay a gate clear
            return "hold"
        alive = [m for m in moves if not m[4]]
        if alive:
            return max(alive, key=lambda m: m[2])[0]
        return "hold"


if __name__ == "__main__":
    run(G)
