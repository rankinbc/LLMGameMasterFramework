"""Dim Ledger: /play engine.

The Warden of Skerry Nine trades Light for Morale at the consoles of the Hub while Kestrel Aune, who is writing a
serial about him, counters every trade. The Reviewer inspects the books after the last turn.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, plural, run  # noqa: E402,F401

NAMES = {"yard": "Yard", "mess": "Mess", "press": "Press", "chapel": "Chapel", "lock": "Pirate Lock"}
BASE = ["yard", "mess", "press", "chapel"]
DRIFTING = ["yard", "mess", "press"]


class G(Game):
    name = "Dim Ledger"

    CONSTANTS = {
        "TURNS": 20,
        "LOT": 3,
        "LO": 1,
        "HI": 6,
        "MIRROR": 7,
        "PUSH": 2,
        "WALK": 1,
        "BURN": 2,
        "SLUMP": 1,
        "DIM_TURN": 11,
        "BURN_LATE": 3,
        "MORALE_CAP": 12,
        "LOCK_TURN": 8,
        "LOCK_HI": 8,
        "LOCK_LOT": 4,
        "FORGE_TURN": 14,
        "FORGE_COST": 3,
        "FORGE_BONUS": 3,
        "LEDGER": 14,
        "DIE": 6,
        "NEED": 6,
        "M_STEP": 3,
        "L_STEP": 6,
        "START_LIGHT": 20,
        "START_MORALE": 6,
        "_DEAD": 1000.0,
        "_FINAL": 100.0,
        "_TIE": 0.01,
        "_BUF_M": 2,
        "_BUF_L": 2,
        "_PEN_M": 6,
        "_PEN_L": 3,
        "_PEN_LEDGER": 1.5,
        "_LEDGER_TURNS": 4,
        "_END_TURNS": 3,
        "_PW": 30.0,
    }

    RULES = """
1. Each turn visit one console (Yard, Mess, Press, Chapel): LAMP up to {LOT} Morale, paying its rate in Light a point, or CUT up to {LOT} Morale, selling it at that rate in Light.
2. Or walk the wards: Morale +{WALK}, no trade. Rates run {LO} to {HI}. At dusk the Yard, Mess and Press each drift 1 up, 1 down or stay; the Chapel's rate is always {MIRROR} minus the Yard's.
3. Kestrel Aune, Number 31, writes a serial about you and counters your trade: at dusk that console's rate moves {PUSH} to punish a repeat (up after a LAMP, down after a CUT). A walk gives her nothing to counter.
4. You, the Warden, start with {START_LIGHT} Light and {START_MORALE} Morale. Every dusk the mirrors burn {BURN} Light and Morale slumps {SLUMP}. From turn {DIM_TURN} the mirrors have swung from the sun and dusk burns {BURN_LATE} Light.
5. Light under 0 at dusk is darkness and you lose; Morale at 0 is mutiny and you lose (darkness first). Morale cannot pass {MORALE_CAP}, and a CUT never leaves it under 1.
6. From turn {LOCK_TURN} the Pirate Lock is a fifth console. Its rate is redrawn every dusk from {LO} to {LOCK_HI}, its lot is {LOCK_LOT}, and Kestrel cannot counter a trade there.
7. From turn {FORGE_TURN}, once, instead of a trade you may doctor the ledger for {FORGE_COST} Light: the Reviewer's roll gets +{FORGE_BONUS}, but a roll of 1 always fails. Kestrel has nothing to counter.
8. After turn {TURNS}'s dusk, burn included, Reviewer Oyelaran inspects. Light under {LEDGER} fails the books. Otherwise roll d{DIE}, +1 per {M_STEP} Morale and +1 per {L_STEP} Light above {LEDGER}; {NEED}+ passes. Pass to win.
"""

    ACTIONS = ["lamp", "cut", "walk", "forge"]
    TAGS = ["counter", "lock_open", "lock_trade", "dim", "forge", "walk", "darkness", "mutiny", "inspect_pass", "inspect_books", "exposed"]
    TRACKED = ["light", "morale"]

    BOUNDS = {
        "light": (-10, 250),
        "morale": (-1, "MORALE_CAP"),
        "yard": ("LO", "HI"),
        "mess": ("LO", "HI"),
        "press": ("LO", "HI"),
        "lock": (0, "LOCK_HI"),
        "chapel": ("LO", "HI"),
    }
    DERIVED = {"chapel": lambda g, s: g.rate(s, "chapel")}
    REACH = {
        "light": ("<=", -1),
        "morale": ("<=", 0),
        "yard": "HI",
        "mess": ("<=", "LO"),
        "chapel": "HI",
        "lock": "LOCK_HI",
    }
    GATES = {
        "lamp": {"_if": lambda g, s: any(g.lamp_max(s, c) >= 1 for c in g.open_consoles(s))},
        "cut": {"_if": lambda g, s: any(g.cut_max(s, c) >= 1 for c in g.open_consoles(s))},
        "walk": {"_if": lambda g, s: s["morale"] < g.C["MORALE_CAP"]},
        "forge": {"_turn": "FORGE_TURN", "light": "FORGE_COST", "!forged": 1},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    def open_consoles(self, s):
        return BASE + (["lock"] if s["lock"] > 0 else [])

    def rate(self, s, c):
        if c == "chapel":
            return self.C["MIRROR"] - s["yard"]
        return s[c]

    def set_rate(self, s, c, v):
        C = self.C
        v = max(C["LO"], min(C["HI"], v))
        if c == "chapel":
            s["yard"] = max(C["LO"], min(C["HI"], C["MIRROR"] - v))
        else:
            s[c] = v

    def lot(self, c):
        return self.C["LOCK_LOT"] if c == "lock" else self.C["LOT"]

    def lamp_max(self, s, c):
        r = self.rate(s, c)
        n = min(self.lot(c), self.C["MORALE_CAP"] - s["morale"])
        while n > 0 and n * r > s["light"]:
            n -= 1
        return max(n, 0)

    def cut_max(self, s, c):
        return max(0, min(self.lot(c), s["morale"] - 1))  # lit-ok: a CUT never leaves Morale under 1

    def span(self, n):
        return "1" if n == 1 else f"1 to {n}"  # lit-ok: a range of one point reads "1"

    def burn_at(self, turn):
        return self.C["BURN_LATE"] if turn >= self.C["DIM_TURN"] else self.C["BURN"]

    def bonus(self, light, morale):
        C = self.C
        return morale // C["M_STEP"], max(0, light - C["LEDGER"]) // C["L_STEP"]

    def need_now(self, light, morale, forged=False):
        """The number the d6 must reach. A doctored ledger lowers it but a 1 always fails, so it never drops under 2."""
        C = self.C
        bm, bl = self.bonus(light, morale)
        need = C["NEED"] - bm - bl
        if forged:
            return max(2, need - C["FORGE_BONUS"])  # lit-ok: a roll of 1 always fails
        return max(1, need)  # lit-ok: a d6 never rolls under 1

    def pass_p(self, light, morale, forged=False):
        C = self.C
        if light < C["LEDGER"]:
            return 0.0
        need = self.need_now(light, morale, forged)
        return max(0.0, min(1.0, (C["DIE"] - need + 1) / C["DIE"]))  # lit-ok: faces from need to the top

    # ------------------------------------------------------------ contract

    def init_state(self, rng):
        C = self.C
        span = C["HI"] - C["LO"] + 1

        def draw():
            return C["LO"] - 1 + rng.d(span)  # lit-ok: d(span) is 1-based

        yard, mess, press = draw(), draw(), draw()
        return {
            "light": C["START_LIGHT"],
            "morale": C["START_MORALE"],
            "yard": yard,
            "mess": mess,
            "press": press,
            "lock": 0,
            "chapter": 0,
            "trade": None,
            "forged": False,
            "verdict": None,
            "hidden": {},
        }

    def options(self, s):
        C = self.C
        o = []
        for c in self.open_consoles(s):
            nm = NAMES[c]
            r = self.rate(s, c)
            n = self.lamp_max(s, c)
            if n >= 1:  # lit-ok: at least one point
                o.append({
                    "id": "lamp", "label": f"Lamp the {nm} at {r} Light a point (buy {self.span(n)} Morale)",
                    "args": {"console": c}, "group": nm, "params": {"amount": {"min": 1, "max": n}},  # lit-ok
                })
            n = self.cut_max(s, c)
            if n >= 1:  # lit-ok
                o.append({
                    "id": "cut", "label": f"Cut the {nm} at {r} Light a point (sell {self.span(n)} Morale)",
                    "args": {"console": c}, "group": nm, "params": {"amount": {"min": 1, "max": n}},  # lit-ok
                })
        if s["morale"] < C["MORALE_CAP"]:
            o.append({"id": "walk", "label": f"Walk the wards (Morale +{C['WALK']}, no trade)", "args": {}})
        if s["_turn"] >= C["FORGE_TURN"] and not s["forged"] and s["light"] >= C["FORGE_COST"]:
            o.append({
                "id": "forge",
                "label": f"Doctor the ledger (Light -{C['FORGE_COST']}; the Reviewer's roll +{C['FORGE_BONUS']}, but a 1 always fails)",
                "args": {},
            })
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        s["trade"] = None
        if a in ("lamp", "cut"):
            c, n = args["console"], args["amount"]
            r = self.rate(s, c)
            nm = NAMES[c]
            if a == "lamp":
                s["light"] -= r * n
                s["morale"] += n
                s["trade"] = [c, 1]  # lit-ok: +1 pushes the rate up
                ev.append(f"You lamp the {nm}: Light -{r * n}, Morale +{n} ({r} Light a point).")
            else:
                s["light"] += r * n
                s["morale"] -= n
                s["trade"] = [c, -1]  # lit-ok: -1 pushes the rate down
                ev.append(f"You cut the {nm}: Light +{r * n}, Morale -{n} ({r} Light a point).")
        elif a == "walk":
            gain = min(C["WALK"], C["MORALE_CAP"] - s["morale"])
            s["morale"] += gain
            self.hit("walk")
            ev.append(f"You walk the wards. Morale +{gain}.")
        elif a == "forge":
            s["light"] -= C["FORGE_COST"]
            s["forged"] = True
            self.hit("forge")
            ev.append(f"You doctor the ledger: Light -{C['FORGE_COST']}. The Reviewer's roll gets +{C['FORGE_BONUS']}, unless it is a 1.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        t = s["_turn"]
        # Kestrel counters the console you used
        tr, s["trade"] = s["trade"], None
        if tr:
            c, d = tr
            nm = NAMES[c]
            if c == "lock":
                self.hit("lock_trade")
                ev.append("The Pirate Lock is beyond Kestrel's reach, so her serial has no chapter on that trade.")
            else:
                old, yard_before = self.rate(s, c), s["yard"]
                self.set_rate(s, c, old + d * C["PUSH"])
                new = self.rate(s, c)
                s["chapter"] += 1
                self.hit("counter")
                title = f"The Warden {'Lights' if d > 0 else 'Sells'} the {nm}"  # lit-ok: d > 0 is a LAMP
                tail = f"Its rate goes {old} to {new}." if new != old else f"Its rate cannot move; it stays at {new}."
                if s["yard"] != yard_before and c == "yard":
                    tail += f" The Chapel follows: {C['MIRROR'] - yard_before} to {C['MIRROR'] - s['yard']}."
                elif s["yard"] != yard_before and c == "chapel":
                    tail += f" The Yard follows: {yard_before} to {s['yard']}."
                ev.append(f"Kestrel's serial, chapter {s['chapter']}, \"{title}\": the {nm} turns on you. {tail}")
        # rates drift
        changes = []
        for k in DRIFTING:
            old = s[k]
            s[k] = rng.drift(old, C["LO"], C["HI"])
            if s[k] != old:
                changes.append(f"{NAMES[k]} {old} to {s[k]}")
                if k == "yard":
                    changes.append(f"Chapel {C['MIRROR'] - old} to {C['MIRROR'] - s[k]}")
        ev.append("Rates drift: " + ", ".join(changes) + "." if changes else "No drift tonight.")
        # the mirrors burn Light, the wards slump
        burn = self.burn_at(t)
        s["light"] -= burn
        s["morale"] -= C["SLUMP"]
        ev.append(f"Dusk: the mirrors burn {burn} Light and Morale slumps {C['SLUMP']}.")
        if s["light"] < 0:
            self.hit("darkness")
            self.finish(s, "loss", "darkness: the lamps went out before the mirrors could pay for them")
            return ev
        if s["morale"] <= 0:
            self.hit("mutiny")
            self.finish(s, "loss", "mutiny: the wards broke the doors")
            return ev
        if t == C["TURNS"]:
            ev += self.inspect(s, rng)
            return ev
        # tells for tomorrow come after every fatal check
        if t + 1 == C["DIM_TURN"]:
            self.hit("dim")
            ev.append(f"The mirror train swings out of the sun. From tomorrow dusk burns {C['BURN_LATE']} Light.")
        if t + 1 >= C["LOCK_TURN"]:
            span = C["LOCK_HI"] - C["LO"] + 1
            before = s["lock"]
            s["lock"] = C["LO"] - 1 + rng.d(span)  # lit-ok: d(span) is 1-based
            if t + 1 == C["LOCK_TURN"]:
                self.hit("lock_open")
                ev.append(f"The Pirate Lock opens: a factor is paying {s['lock']} Light a point.")
            elif s["lock"] != before:
                ev.append(f"The Pirate Lock's rate goes {before} to {s['lock']}.")
        return ev

    def inspect(self, s, rng):
        C = self.C
        ev = []
        if s["light"] < C["LEDGER"]:
            s["verdict"] = "books"
            self.hit("inspect_books")
            ev.append(f"Reviewer Oyelaran opens the ledger: Light {s['light']}, under the {C['LEDGER']} required. The books do not balance.")
            return ev
        bm, bl = self.bonus(s["light"], s["morale"])
        need = self.need_now(s["light"], s["morale"], s["forged"])
        def bon(n):
            return f"+{n} to the roll" if n else "no bonus"

        line = f"Reviewer Oyelaran opens the ledger: Light {s['light']} clears {C['LEDGER']} ({bon(bl)}), Morale {s['morale']} ({bon(bm)})"
        if s["forged"]:
            line += f", doctored pages ({bon(C['FORGE_BONUS'])})"
        ev.append(line + ".")
        v = rng.d(C["DIE"])
        ok = v >= need
        ev.append(f"roll {v} (need {need}+) {'success' if ok else 'fail'}.")
        s["verdict"] = "pass" if ok else "roll"
        if ok:
            self.hit("inspect_pass")
        elif s["forged"] and v == 1:  # lit-ok: the face that exposes a forgery
            s["verdict"] = "exposed"
            self.hit("exposed")
            ev.append("The Reviewer holds a page to the lamp. The forgery shows.")
        return ev

    def status_line(self, s):
        rates = f"Yard {s['yard']} Mess {s['mess']} Press {s['press']} Chapel {self.rate(s, 'chapel')}"
        if s["lock"] > 0:
            rates += f" Lock {s['lock']}"
        return f"Light {s['light']} | Morale {s['morale']} | Rates: {rates} | Ledger: {'doctored' if s['forged'] else 'honest'}"

    def check_end(self, s):
        if s["light"] < 0:
            return {"result": "loss", "reason": "darkness: the lamps went out before the mirrors could pay for them"}
        if s["morale"] <= 0:
            return {"result": "loss", "reason": "mutiny: the wards broke the doors"}
        return None

    def final_check(self, s):
        v = s.get("verdict")
        if v == "pass":
            return {"result": "win", "reason": "Reviewer Oyelaran signs the ledger, and the serial ends with its villain unpunished"}
        if v == "exposed":
            return {"result": "loss", "reason": "the forgery was found and the Reviewer is not satisfied"}
        if v == "books":
            return {"result": "loss", "reason": f"the books do not balance: Light {s['light']} is under {self.C['LEDGER']}"}
        return {"result": "loss", "reason": "the Reviewer is not satisfied"}

    def visible(self, s):
        out = {k: v for k, v in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "_seed", "trade", "verdict")}
        out["chapel"] = self.rate(s, "chapel")
        if s.get("_ended"):
            return out
        light = s["light"] - self.burn_at(s["_turn"])
        morale = s["morale"] - self.C["SLUMP"]
        preview = {"light": light, "morale": morale, "assumes": "no trade, inspected after this dusk"}
        if light < 0:
            preview["fatal"] = "darkness"
        elif morale <= 0:
            preview["fatal"] = "mutiny"
        else:
            bm, bl = self.bonus(light, morale)
            preview.update({
                "books_balance": light >= self.C["LEDGER"],
                "bonus": bm + bl + (self.C["FORGE_BONUS"] if s["forged"] else 0),
                "need": self.need_now(light, morale, s["forged"]),
            })
        out["inspection_preview"] = preview
        return out

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C

        def r1(t):
            s = t.fresh(light=20, morale=6, yard=4, mess=2, press=5, lock=0)
            t.eq(t.ids(s), ["cut", "lamp", "walk"], "no forgery and no Lock on turn 1")
            t.ok(t.offered(s, "lamp", console="yard", amount=C["LOT"]), "a LAMP of a full lot is legal")
            t.ok(not t.offered(s, "lamp", console="yard", amount=C["LOT"] + 1), "a LAMP is capped at the lot")
            t.ok(not t.offered(s, "lamp", console="lock", amount=1), "no Lock console yet")
            t.eq(t.label(s, "lamp", console="mess"), f"Lamp the Mess at 2 Light a point (buy 1 to {C['LOT']} Morale)", "lamp label")
            t.eq(t.label(s, "cut", console="press"), f"Cut the Press at 5 Light a point (sell 1 to {C['LOT']} Morale)", "cut label")
            t.eq(t.label(s, "walk"), f"Walk the wards (Morale +{C['WALK']}, no trade)", "walk label")
            events = t.apply(s, "lamp", {"console": "yard", "amount": 2})
            t.eq((s["light"], s["morale"]), (20 - 2 * 4, 6 + 2), "a LAMP pays the rate in Light for each Morale")
            t.has(events, "You lamp the Yard: Light -8, Morale +2 (4 Light a point).")
            events = t.apply(s, "cut", {"console": "press", "amount": 3})
            t.eq((s["light"], s["morale"]), (12 + 3 * 5, 8 - 3), "a CUT sells Morale at the rate")
            t.has(events, "You cut the Press: Light +15, Morale -3 (5 Light a point).")
            s = t.fresh(light=20, morale=6)
            events = t.apply(s, "walk")
            t.eq((s["light"], s["morale"], s["trade"]), (20, 6 + C["WALK"], None), "a walk is free and leaves no trade")
            t.has(events, f"You walk the wards. Morale +{C['WALK']}.")
            s = t.fresh(light=20, morale=C["MORALE_CAP"] - 1, mess=2)
            t.ok(t.offered(s, "lamp", console="mess", amount=1) and not t.offered(s, "lamp", console="mess", amount=2), "Morale cannot pass the cap")
            t.eq(t.label(s, "lamp", console="mess"), "Lamp the Mess at 2 Light a point (buy 1 Morale)", "a range of one point reads as one")
            t.eq(t.label(t.fresh(light=20, morale=2, mess=4), "cut", console="mess"), "Cut the Mess at 4 Light a point (sell 1 Morale)", "and so does a CUT")
            s = t.fresh(light=20, morale=C["MORALE_CAP"])
            t.ok("lamp" not in t.ids(s) and "walk" not in t.ids(s), "at the cap there is nothing to buy and nothing to walk")
            s = t.fresh(light=20, morale=2)
            t.ok(t.offered(s, "cut", console="yard", amount=1) and not t.offered(s, "cut", console="yard", amount=2), "a CUT never leaves Morale under 1")
            s = t.fresh(light=20, morale=1)
            t.ok("cut" not in t.ids(s), "at Morale 1 there is nothing to cut")
            s = t.fresh(light=9, morale=6, yard=4, mess=5)
            t.ok(t.offered(s, "lamp", console="yard", amount=2) and not t.offered(s, "lamp", console="yard", amount=3), "a LAMP must be paid for")
            t.ok(t.offered(s, "lamp", console="mess", amount=1) and not t.offered(s, "lamp", console="mess", amount=2), "exactly enough Light is enough")
            s = t.fresh(light=0, morale=6, yard=4)
            t.ok("lamp" not in t.ids(s), "no Light, no LAMP")
            walk, C["WALK"] = C["WALK"], 3
            try:
                s = t.fresh(light=20, morale=C["MORALE_CAP"] - 1)
                events = t.apply(s, "walk")
                t.eq(s["morale"], C["MORALE_CAP"], "a walk cannot pass the cap")
                t.has(events, "You walk the wards. Morale +1.")
            finally:
                C["WALK"] = walk
            s = t.fresh(light=30, morale=5, lock=0)
            s, _ = t.step(s, "walk")
            t.eq(s["_turn"], 2, "one action ends the turn")
            s = t.fresh(light=20, morale=6, yard=4, mess=2, press=5)
            t.eq(t.status(s), "Light 20 | Morale 6 | Rates: Yard 4 Mess 2 Press 5 Chapel 3 | Ledger: honest", "the status line")

        def r2(t):
            s = t.fresh(yard=4, mess=2, press=5)
            t.eq(self.rate(s, "chapel"), C["MIRROR"] - 4, "the Chapel's rate is the mirror minus the Yard's")
            events = t.advance(s, turn=2, drifts=[1, -1, 0])
            t.eq((s["yard"], s["mess"], s["press"]), (5, 1, 5), "each console drifts by at most 1")
            t.eq(self.rate(s, "chapel"), C["MIRROR"] - 5, "the Chapel follows the Yard")
            t.has(events, f"Rates drift: Yard 4 to 5, Chapel {C['MIRROR'] - 4} to {C['MIRROR'] - 5}, Mess 2 to 1.")
            s = t.fresh(yard=4, mess=2, press=5)
            events = t.advance(s, turn=2, drifts=[0, 0, 0])
            t.has(events, "No drift tonight.")
            s = t.fresh(yard=C["HI"], mess=C["LO"], press=C["HI"])
            t.advance(s, turn=2, drifts=[1, -1, 1])
            t.eq((s["yard"], s["mess"], s["press"]), (C["HI"], C["LO"], C["HI"]), "rates stay inside the range")
            s = t.fresh(yard=C["LO"], mess=3, press=3)
            t.advance(s, turn=2, drifts=[-1, 0, 0])
            t.eq(self.rate(s, "chapel"), C["HI"], "the Chapel tops out when the Yard bottoms out")
            starts = [t.fresh(seed=i) for i in range(1, 120)]
            t.eq({x["yard"] for x in starts}, set(range(C["LO"], C["HI"] + 1)), "any rate in the range can open the game")
            t.ok(all(C["LO"] <= x[k] <= C["HI"] for x in starts for k in DRIFTING), "opening rates stay in the range")
            t.eq(t.fresh()["light"], C["START_LIGHT"], "starting Light")
            t.eq(t.fresh()["morale"], C["START_MORALE"], "starting Morale")
            t.eq(self.turns, C["TURNS"], "the turn budget")

        def r3(t):
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=3)
            t.apply(s, "lamp", {"console": "mess", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["mess"], 3 + C["PUSH"], "a LAMP raises the console's rate")
            t.has(events, f"Kestrel's serial, chapter 1, \"The Warden Lights the Mess\": the Mess turns on you. Its rate goes 3 to {3 + C['PUSH']}.")
            t.eq(s["chapter"], 1, "the first chapter is chapter 1")
            t.eq(s["trade"], None, "the trade is spent at dusk")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=5)
            t.apply(s, "cut", {"console": "press", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["press"], 5 - C["PUSH"], "a CUT lowers the console's rate")
            t.has(events, f"\"The Warden Sells the Press\": the Press turns on you. Its rate goes 5 to {5 - C['PUSH']}.")
            t.ok("counter" in self._hits, "the counter is noted")
            s = t.fresh(light=30, morale=6, yard=2, mess=3, press=3)
            t.apply(s, "cut", {"console": "chapel", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(self.rate(s, "chapel"), C["MIRROR"] - 2 - C["PUSH"], "a CUT at the Chapel lowers the Chapel's rate")
            t.eq(s["yard"], 2 + C["PUSH"], "which raises the Yard's")
            t.has(events, "the Chapel turns on you.")
            s = t.fresh(light=30, morale=6, yard=C["HI"], mess=3, press=3)
            t.apply(s, "lamp", {"console": "yard", "amount": 1})
            t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["yard"], C["HI"], "the counter cannot push past the top of the range")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=C["LO"])
            t.apply(s, "cut", {"console": "press", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["press"], C["LO"], "or below the bottom")
            t.has(events, f"the Press turns on you. Its rate cannot move; it stays at {C['LO']}.")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=3, chapter=7)
            t.apply(s, "lamp", {"console": "yard", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["chapter"], 8, "chapters are counted as they are written")
            t.has(events, f"chapter 8, \"The Warden Lights the Yard\": the Yard turns on you. Its rate goes 3 to {3 + C['PUSH']}. The Chapel follows: {C['MIRROR'] - 3} to {C['MIRROR'] - 3 - C['PUSH']}.")
            s = t.fresh(light=30, morale=6, yard=2, mess=3, press=3)
            t.apply(s, "cut", {"console": "chapel", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.has(events, f"Its rate goes {C['MIRROR'] - 2} to {C['MIRROR'] - 2 - C['PUSH']}. The Yard follows: 2 to {2 + C['PUSH']}.")
            s = t.fresh(light=30, morale=6, yard=C["HI"], mess=3, press=3)
            t.apply(s, "lamp", {"console": "yard", "amount": 1})
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.has(events, f"it stays at {C['HI']}.")
            t.ok(not any("follows" in e for e in events), "a counter that moves nothing moves no follower")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=3)
            t.apply(s, "walk")
            t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq(s["chapter"], 0, "a walk writes no chapter")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=3)
            t.apply(s, "walk")
            events = t.advance(s, turn=4, drifts=[0, 0, 0])
            t.eq((s["yard"], s["mess"], s["press"]), (3, 3, 3), "a walk gives Kestrel nothing to counter")
            t.ok(not any("Kestrel" in e for e in events), "no chapter about a walk")
            s = t.fresh(light=30, morale=6, yard=3, mess=3, press=3)
            t.apply(s, "lamp", {"console": "mess", "amount": 1})
            events = t.advance(s, turn=4, drifts=[1, 0, 0])
            t.in_order(events, ["turns on you", "Rates drift"], "the counter is narrated before the drift")
            t.eq(s["yard"], 4, "the drift still happens")

        def r4(t):
            s = t.fresh(light=20, morale=5)
            events = t.advance(s, turn=2, drifts=[0, 0, 0])
            t.eq((s["light"], s["morale"]), (20 - C["BURN"], 5 - C["SLUMP"]), "dusk burns Light and slumps Morale")
            t.has(events, f"Dusk: the mirrors burn {C['BURN']} Light and Morale slumps {C['SLUMP']}.")
            s = t.fresh(light=20, morale=5)
            events = t.advance(s, turn=C["DIM_TURN"] - 1, drifts=[0, 0, 0])
            t.eq(s["light"], 20 - C["BURN"], "the burn is still the old burn the night before")
            t.has(events, f"From tomorrow dusk burns {C['BURN_LATE']} Light.")
            t.ok("dim" in self._hits, "the dimming is noted")
            s = t.fresh(light=20, morale=5)
            events = t.advance(s, turn=C["DIM_TURN"], drifts=[0, 0, 0])
            t.eq(s["light"], 20 - C["BURN_LATE"], "from the dimming turn dusk burns more")
            t.has(events, f"Dusk: the mirrors burn {C['BURN_LATE']} Light")
            t.ok(not any("From tomorrow" in e for e in events), "the warning is given once")

        def r5(t):
            s = t.fresh(light=C["BURN"] - 1, morale=5)
            events = t.advance(s, turn=2, drifts=[0, 0, 0])
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss" and "darkness" in s["_ended"]["reason"], "Light under 0 is darkness")
            t.ok(not any("tomorrow" in e or "Lock opens" in e for e in events), "no tell for a tomorrow that will not come")
            t.ok("darkness" in self._hits, "darkness is noted")
            s = t.fresh(light=C["BURN"], morale=5)
            t.advance(s, turn=2, drifts=[0, 0, 0])
            t.ok(s["_ended"] is None and s["light"] == 0, "exactly 0 Light is still alive")
            s = t.fresh(light=20, morale=C["SLUMP"])
            t.advance(s, turn=2, drifts=[0, 0, 0])
            t.ok(s["_ended"] and "mutiny" in s["_ended"]["reason"], "Morale 0 is mutiny")
            t.ok("mutiny" in self._hits, "mutiny is noted")
            s = t.fresh(light=20, morale=C["SLUMP"] + 1)
            t.advance(s, turn=2, drifts=[0, 0, 0])
            t.ok(s["_ended"] is None and s["morale"] == 1, "Morale 1 is still alive")  # lit-ok
            s = t.fresh(light=C["BURN"] - 1, morale=C["SLUMP"])
            t.advance(s, turn=2, drifts=[0, 0, 0])
            t.ok("darkness" in s["_ended"]["reason"], "darkness comes before mutiny")
            s = t.fresh(light=-1, morale=5)
            t.ok(self.check_end(s)["result"] == "loss", "check_end sees darkness")
            t.ok(self.check_end(t.fresh(light=0, morale=5)) is None, "check_end: 0 Light is alive")
            t.ok(self.check_end(t.fresh(light=5, morale=1)) is None, "check_end: Morale 1 is alive")
            s = t.fresh(light=5, morale=0)
            t.ok("mutiny" in self.check_end(s)["reason"], "check_end sees mutiny")

        def r6(t):
            s = t.fresh(light=20, morale=5)
            events = t.advance(s, turn=C["LOCK_TURN"] - 2, drifts=[0, 0, 0])
            t.eq(s["lock"], 0, "no Lock before the night before its turn")
            t.ok(not any("Lock opens" in e for e in events), "no announcement yet")
            s = t.fresh(light=20, morale=5)
            events = t.advance(s, turn=C["LOCK_TURN"] - 1, drifts=[0, 0, 0], dice=[5])
            t.eq(s["lock"], 5, "the Lock's rate is drawn at the dusk before it opens")
            t.has(events, "The Pirate Lock opens: a factor is paying 5 Light a point.")
            t.ok("lock_open" in self._hits, "the Lock opening is noted")
            t.ok("lamp" in t.ids(s), "the Lock is a console once it is open")
            s["light"], s["morale"] = 60, C["LOCK_LOT"] + 1
            t.eq(t.label(s, "cut", console="lock"), f"Cut the Pirate Lock at 5 Light a point (sell 1 to {C['LOCK_LOT']} Morale)", "lock label")
            s["light"], s["morale"] = 60, 3
            t.ok(t.offered(s, "lamp", console="lock", amount=C["LOCK_LOT"]), "the Lock's lot is larger")
            t.ok(not t.offered(s, "lamp", console="lock", amount=C["LOCK_LOT"] + 1), "but still capped")
            t.ok("Chapel" in t.status(s) and t.status(s).split("Rates: ")[1].split(" |")[0].endswith("Lock 5"), "the Lock shows in the rates")
            s["_turn"] = C["LOCK_TURN"]
            events = t.advance(s, turn=C["LOCK_TURN"], drifts=[0, 0, 0], dice=[C["LOCK_HI"]])
            t.eq(s["lock"], C["LOCK_HI"], "the Lock's rate is redrawn every dusk, up to its top")
            t.ok(not any("Lock opens" in e for e in events), "it opens once")
            s = t.fresh(light=60, morale=5, lock=4)
            t.advance(s, turn=C["LOCK_TURN"], drifts=[0, 0, 0], dice=[1])
            t.eq(s["lock"], C["LO"], "and down to the bottom of the range")
            seen = set()
            for sd in range(1, 200):
                s2 = t.fresh(light=20, morale=5)
                t.advance(s2, turn=C["LOCK_TURN"] - 1, seed=sd, drifts=[0, 0, 0])
                seen.add(s2["lock"])
            t.eq(seen, set(range(C["LO"], C["LOCK_HI"] + 1)), "the Lock's rate can be any value in its range, and only those")
            t.ok(t.offered(s, "cut", console="lock", amount=1), "a Lock at the bottom rate is still a console")
            s = t.fresh(light=20, morale=5, lock=4)
            events = t.advance(s, turn=C["LOCK_TURN"], drifts=[0, 0, 0], dice=[7])
            t.has(events, "The Pirate Lock's rate goes 4 to 7.")
            s = t.fresh(light=20, morale=5, lock=4)
            events = t.advance(s, turn=C["LOCK_TURN"], drifts=[0, 0, 0], dice=[4])
            t.ok(not any("Lock's rate" in e for e in events), "an unchanged Lock rate is not narrated")
            s = t.fresh(light=20, morale=5, lock=4)
            events = t.advance(s, turn=C["TURNS"] - 1, drifts=[0, 0, 0], dice=[2])
            t.eq(s["lock"], 2, "the Lock is redrawn at the dusk before the last turn")
            s = t.fresh(light=30, morale=5, lock=4)
            t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[2])
            t.eq(s["lock"], 4, "but not after the last turn's dusk")
            t.ok(t.offered(t.fresh(lock=1), "lamp", console="lock", amount=1), "a Lock at rate 1 is open")
            t.ok(not t.offered(t.fresh(lock=0), "lamp", console="lock", amount=1), "a Lock at 0 is shut")
            s = t.fresh(light=60, morale=6, yard=3, mess=3, press=3, lock=4)
            t.apply(s, "cut", {"console": "lock", "amount": 2})
            t.eq((s["light"], s["morale"]), (60 + 8, 6 - 2), "a trade at the Lock works like any other")
            events = t.advance(s, turn=C["LOCK_TURN"], drifts=[0, 0, 0], dice=[4])
            t.eq((s["yard"], s["mess"], s["press"]), (3, 3, 3), "Kestrel cannot counter a trade at the Lock")
            t.has(events, "The Pirate Lock is beyond Kestrel's reach")
            t.ok("lock_trade" in self._hits, "a Lock trade is noted")

        def r7(t):
            s = t.fresh(light=30, morale=8)
            s["_turn"] = C["FORGE_TURN"] - 1
            t.ok("forge" not in t.ids(s), "no forgery before its turn")
            s["_turn"] = C["FORGE_TURN"]
            t.ok("forge" in t.ids(s), "the forgery is offered from its turn")
            t.eq(
                t.label(s, "forge"),
                f"Doctor the ledger (Light -{C['FORGE_COST']}; the Reviewer's roll +{C['FORGE_BONUS']}, but a 1 always fails)",
                "label",
            )
            events = t.apply(s, "forge")
            t.eq(s["light"], 30 - C["FORGE_COST"], "the forgery costs Light")
            t.ok(s["forged"], "the ledger is doctored")
            t.has(events, f"You doctor the ledger: Light -{C['FORGE_COST']}. The Reviewer's roll gets +{C['FORGE_BONUS']}, unless it is a 1.")
            t.ok("forge" in self._hits, "the lever is noted")
            t.ok("forge" not in t.ids(s), "once only")
            t.ok("Ledger: doctored" in t.status(s), "the status line shows it")
            s = t.fresh(light=C["FORGE_COST"], morale=8)
            s["_turn"] = C["FORGE_TURN"]
            t.ok("forge" in t.ids(s), "exactly enough Light is enough")
            s = t.fresh(light=C["FORGE_COST"] - 1, morale=8)
            s["_turn"] = C["FORGE_TURN"]
            t.ok("forge" not in t.ids(s), "the forgery must be paid for")
            rich = dict(light=C["LEDGER"] + 2 * C["L_STEP"] + C["BURN_LATE"], morale=2 * C["M_STEP"] + C["SLUMP"])  # +4 before the forgery
            s = t.fresh(**rich)
            s["forged"] = True
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[1])
            t.eq(s["verdict"], "exposed", "a 1 exposes the forgery")
            t.has(events, "roll 1 (need 2+) fail.")
            t.has(events, "The forgery shows.")
            t.ok("exposed" in self._hits, "the exposure is noted")
            t.ok("forgery was found" in self.final_check(s)["reason"] and self.final_check(s)["result"] == "loss", "final_check: exposed")
            s = t.fresh(light=C["LEDGER"] + 3 * C["L_STEP"] + C["BURN_LATE"], morale=C["MORALE_CAP"])
            s["forged"] = True
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[1])
            t.eq(s["verdict"], "exposed", "even a huge bonus cannot save a 1")
            s = t.fresh(**rich)
            s["forged"] = True
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[2])
            t.eq(s["verdict"], "pass", "a 2 passes a doctored ledger that needs 2 or less")
            t.has(events, "doctored pages (+%d to the roll)" % C["FORGE_BONUS"])

        def r8(t):
            L, M = C["LEDGER"], C["M_STEP"]
            s = t.fresh(light=L - 1 + C["BURN_LATE"], morale=6)
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0])
            t.eq(s["verdict"], "books", "Light under the ledger fails the books")
            t.has(events, f"Light {L - 1}, under the {L} required. The books do not balance.")
            t.ok("inspect_books" in self._hits, "the books failure is noted")
            end = self.final_check(s)
            t.ok(end["result"] == "loss" and "the books do not balance" in end["reason"], "final_check: books")
            need = C["NEED"] - 2 * 1 - 1 * 1  # Morale 2 steps, 1 step of surplus Light
            s = t.fresh(light=L + C["L_STEP"] + C["BURN_LATE"], morale=2 * M + C["SLUMP"])
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[need])
            t.eq(s["verdict"], "pass", "a roll equal to the need passes")
            t.has(events, f"Light {L + C['L_STEP']} clears {L} (+1 to the roll), Morale {2 * M} (+2 to the roll).")
            t.has(events, f"roll {need} (need {need}+) success.")
            t.in_order(events, ["Dusk:", "opens the ledger", "roll "], "the inspection follows the dusk")
            t.ok("inspect_pass" in self._hits, "a pass is noted")
            t.eq(self.final_check(s), {"result": "win", "reason": "Reviewer Oyelaran signs the ledger, and the serial ends with its villain unpunished"}, "final_check: pass")
            s = t.fresh(light=L + C["L_STEP"] + C["BURN_LATE"], morale=2 * M + C["SLUMP"])
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[need - 1])
            t.eq(s["verdict"], "roll", "a roll under the need fails")
            t.has(events, f"roll {need - 1} (need {need}+) fail.")
            t.ok("not satisfied" in self.final_check(s)["reason"] and self.final_check(s)["result"] == "loss", "final_check: roll")
            s = t.fresh(light=L + C["BURN_LATE"], morale=C["SLUMP"] + 1)
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[C["NEED"]])
            t.ok(s["verdict"] == "pass", "exactly the ledger in Light still balances the books")
            t.has(events, f"roll {C['NEED']} (need {C['NEED']}+) success.")
            s = t.fresh(light=60, morale=C["MORALE_CAP"] - 2, yard=3)
            s["_turn"] = C["TURNS"]
            t.ok(self.check_end(s) is None, "the last turn is still played")
            s, events = t.step(s, "walk")
            t.ok(s["_ended"] and s["_ended"]["phase"] == "budget" and s["_turn"] == C["TURNS"] + 1, "the inspection ends the game after the last dusk")
            t.ok(not any("tomorrow" in e for e in events), "no tell after the last dusk")
            s = t.fresh(light=1, morale=3)
            s["_turn"] = C["TURNS"]
            s, _ = t.step(s, "walk")
            t.ok("darkness" in s["_ended"]["reason"] and s["_ended"]["phase"] == "dusk", "darkness on the last dusk comes before the inspection")

        def r8b(t):
            L, M, S = C["LEDGER"], C["M_STEP"], C["L_STEP"]
            t.eq(self.bonus(L + 2 * S + 1, 3 * M - 1), (2, 2), "bonus: Morale steps and surplus Light steps")
            t.eq(self.bonus(L - 5, 3 * M), (3, 0), "bonus: no negative surplus")
            t.eq(self.need_now(L, 0), C["NEED"], "need with no bonus")
            t.eq(self.need_now(L + S, M), C["NEED"] - 2, "need with two bonus steps")
            t.eq(self.need_now(L + 10 * S, 10 * M), 1, "a d6 never needs under 1")  # lit-ok
            t.eq(self.need_now(L, 0, True), C["NEED"] - C["FORGE_BONUS"], "forgery lowers the need")
            t.eq(self.need_now(L + 10 * S, 10 * M, True), 2, "but a forged roll still needs 2")  # lit-ok
            t.eq(self.pass_p(L - 1, 10 * M), 0.0, "the books must balance for any chance")
            t.eq(self.pass_p(L + 10 * S, 10 * M), 1.0, "need 1 always passes")
            t.eq(self.pass_p(L + 10 * S, 10 * M, True), (C["DIE"] - 1) / C["DIE"], "a forged roll never passes on a 1")  # lit-ok
            t.eq(self.pass_p(L, 0), (C["DIE"] - C["NEED"] + 1) / C["DIE"] if C["NEED"] <= C["DIE"] else 0.0, "pass chance from the need")  # lit-ok
            t.eq(self.pass_p(L, 0, True), (C["DIE"] - (C["NEED"] - C["FORGE_BONUS"]) + 1) / C["DIE"], "forged pass chance")  # lit-ok
            s = t.fresh(light=L + S + C["BURN"], morale=M + C["SLUMP"])
            v = self.visible(s)["inspection_preview"]
            t.eq(v, {"light": L + S, "morale": M, "assumes": "no trade, inspected after this dusk", "books_balance": True, "bonus": 2, "need": C["NEED"] - 2}, "the player is shown the odds as they will stand after this dusk")
            s["_turn"] = C["DIM_TURN"]
            v = self.visible(s)["inspection_preview"]
            t.eq(v["light"], L + S + C["BURN"] - C["BURN_LATE"], "the preview uses tonight's burn")
            s = t.fresh(light=L + S + C["BURN"], morale=M + C["SLUMP"])
            s["forged"] = True
            v = self.visible(s)["inspection_preview"]
            t.eq(v["bonus"], 2 + C["FORGE_BONUS"], "and the forgery in them")
            t.eq(v["need"], max(2, C["NEED"] - 2 - C["FORGE_BONUS"]), "and its need")  # lit-ok
            t.eq(self.visible(t.fresh(light=L))["inspection_preview"]["books_balance"], False, "and when the burn breaks the books")
            t.eq(self.visible(t.fresh(light=L + C["BURN"]))["inspection_preview"]["books_balance"], True, "and when the burn just leaves the books balanced")
            t.eq(self.visible(t.fresh(light=C["BURN"] - 1))["inspection_preview"]["fatal"], "darkness", "the preview names darkness first")
            t.eq(self.visible(t.fresh(light=30, morale=C["SLUMP"]))["inspection_preview"]["fatal"], "mutiny", "and mutiny")
            t.ok("need" not in self.visible(t.fresh(light=30, morale=C["SLUMP"]))["inspection_preview"], "a fatal dusk has no inspection odds")
            ended = t.fresh(light=-5, morale=3)
            ended["_ended"] = {"result": "loss", "reason": "x"}
            t.ok("inspection_preview" not in self.visible(ended), "an ended game shows no preview")
            v = self.visible(t.fresh(light=30, morale=3, lock=4, chapter=5))
            t.eq((v["lock"], v["chapter"]), (4, 5), "visible carries the Lock and the chapter")
            # a forged ledger with the books failing is a books loss, not a forgery loss
            s = t.fresh(light=L - 1 + C["BURN_LATE"], morale=6)
            s["forged"] = True
            t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[1])
            t.eq(s["verdict"], "books", "the books are checked before the roll, forged or not")
            # no bonus reads as no bonus
            s = t.fresh(light=L + C["BURN_LATE"], morale=C["SLUMP"] + 1)
            events = t.advance(s, turn=C["TURNS"], drifts=[0, 0, 0], dice=[C["DIE"]])
            t.has(events, f"Light {L} clears {L} (no bonus), Morale 1 (no bonus)")
            # counter and drift on the same console in one dusk, clamped partway
            s = t.fresh(light=30, morale=6, yard=C["HI"] - 1, mess=3, press=3)
            t.apply(s, "lamp", {"console": "yard", "amount": 1})
            events = t.advance(s, turn=4, drifts=[-1, 0, 0])
            t.eq(s["yard"], C["HI"] - 1, "the push clamps at the top and then the drift takes one back")
            t.has(events, f"Its rate goes {C['HI'] - 1} to {C['HI']}. The Chapel follows: {C['MIRROR'] - C['HI'] + 1} to {C['MIRROR'] - C['HI']}.")
            t.has(events, f"Rates drift: Yard {C['HI']} to {C['HI'] - 1}, Chapel {C['MIRROR'] - C['HI']} to {C['MIRROR'] - C['HI'] + 1}.")

        def r8c(t):
            k = (C["LO"] + C["HI"]) / 2
            walk = {"id": "walk", "args": {}}
            base = t.fresh(light=20, morale=6)
            burn = C["BURN"]
            want = (20 - burn) + k * (6 + C["WALK"] - C["SLUMP"])
            t.eq(self._value(base, walk, 2, 9, burn, k), want, "heuristic: a quiet walk is worth the wealth after dusk")
            lamp = {"id": "lamp", "args": {"console": "mess", "amount": 2}}
            s = t.fresh(light=20, morale=6, mess=3)
            t.eq(self._value(s, lamp, 2, 9, burn, k), (20 - 6 - burn) + k * (6 + 2 - C["SLUMP"]), "heuristic: a LAMP trades Light for Morale")
            cut = {"id": "cut", "args": {"console": "mess", "amount": 2}}
            t.eq(self._value(s, cut, 2, 9, burn, k), (20 + 6 - burn) + k * (6 - 2 - C["SLUMP"]), "heuristic: a CUT trades Morale for Light")
            dead = t.fresh(light=burn - 1, morale=6)
            t.eq(self._value(dead, walk, 2, 9, burn, k), -C["_DEAD"], "heuristic: darkness at dusk is ruled out")
            t.ok(self._value(t.fresh(light=burn, morale=6), walk, 2, 9, burn, k) > -C["_DEAD"], "heuristic: exactly enough Light survives")
            mut = t.fresh(light=20, morale=C["SLUMP"] + 2, mess=3)
            one = {"id": "cut", "args": {"console": "mess", "amount": 1}}
            t.eq(self._value(mut, {"id": "cut", "args": {"console": "mess", "amount": 2}}, 2, 9, burn, k), -C["_DEAD"], "heuristic: mutiny at dusk is ruled out")
            t.ok(self._value(mut, one, 2, 9, burn, k) > -C["_DEAD"], "heuristic: Morale 1 at dusk survives")
            low_m = t.fresh(light=20, morale=C["SLUMP"] + C["_BUF_M"])
            gap = C["SLUMP"] + C["_BUF_M"] - (C["SLUMP"] + C["_BUF_M"] + C["WALK"] - C["SLUMP"])
            want = (20 - burn) + k * (C["_BUF_M"] + C["WALK"]) - max(0, gap) * C["_PEN_M"]
            t.eq(self._value(low_m, walk, 2, 9, burn, k), want, "heuristic: thin Morale at dusk is penalized")
            thin = t.fresh(light=burn + C["_BUF_L"] - 1 + 0, morale=6)
            want = (thin["light"] - burn) + k * (6 + C["WALK"] - C["SLUMP"]) - (burn + C["_BUF_L"] - (thin["light"] - burn)) * C["_PEN_L"]
            t.eq(self._value(thin, walk, 2, 9, burn, k), want, "heuristic: thin Light at dusk is penalized")
            late = t.fresh(light=C["LEDGER"] - 3 + burn, morale=6)
            want = (C["LEDGER"] - 3) + k * (6 + C["WALK"] - C["SLUMP"]) - 3 * C["_PEN_LEDGER"]
            t.eq(self._value(late, walk, 2, C["_LEDGER_TURNS"], burn, k), want + 0 * C["_PW"], "heuristic: the ledger floor is felt in the last turns" if C["_LEDGER_TURNS"] > C["_END_TURNS"] else "n/a")
            rich = t.fresh(light=C["LEDGER"] + 6 + burn, morale=6)
            wealth = (C["LEDGER"] + 6) + k * (6 + C["WALK"] - C["SLUMP"])
            t.eq(self._value(rich, walk, 2, C["_END_TURNS"], burn, k), wealth + C["_PW"] * self.pass_p(C["LEDGER"] + 6, 6 + C["WALK"] - C["SLUMP"]), "heuristic: the inspection odds count near the end")
            t.eq(self._value(rich, walk, 2, C["_END_TURNS"] + 1, burn, k), wealth, "heuristic: and not before")
            final = self._value(rich, walk, 20, 0, burn, k)
            t.eq(final, C["_FINAL"] * self.pass_p(C["LEDGER"] + 6, 6 + C["WALK"] - C["SLUMP"]) + C["_TIE"] * wealth, "heuristic: on the last turn only the odds matter")
            forge = {"id": "forge", "args": {}}
            fin = self._value(rich, forge, 20, 0, burn, k)
            t.eq(fin, C["_FINAL"] * self.pass_p(C["LEDGER"] + 6 - C["FORGE_COST"], 6 - C["SLUMP"], True) + C["_TIE"] * ((C["LEDGER"] + 6 - C["FORGE_COST"]) + k * (6 - C["SLUMP"])), "heuristic: a forgery is valued by its odds")
            s = t.fresh(light=20, morale=8, yard=3, mess=C["HI"], press=3)
            pick = self.heuristic(s, self.options(s), t.rng())
            t.eq((pick["id"], pick["args"]["console"]), ("cut", "mess"), "heuristic: sells where Morale is dearest")

        return [
            (1, "trade and walk", r1), (2, "rates, drift and the mirror", r2), (3, "Kestrel counters", r3),
            (4, "burn and slump", r4), (5, "darkness and mutiny", r5), (6, "the Pirate Lock", r6),
            (7, "doctored ledger", r7), (8, "the inspection", lambda t: (r8(t), r8b(t), r8c(t))),
        ]

    # ------------------------------------------------------------ policy

    def heuristic(self, s, options, rng):
        C = self.C
        t = s["_turn"]
        left = C["TURNS"] - t
        burn = self.burn_at(t)
        k = (C["LO"] + C["HI"]) / 2
        best, best_v = None, None
        for o in options:
            if o.get("params"):
                spec = o["params"]["amount"]
                variants = [{"id": o["id"], "args": {**o["args"], "amount": n}} for n in range(spec["min"], spec["max"] + 1)]
            else:
                variants = [{"id": o["id"], "args": dict(o["args"])}]
            for v in variants:
                val = self._value(s, v, t, left, burn, k)
                if best is None or val > best_v:
                    best, best_v = v, val
        return best

    def _value(self, s, v, t, left, burn, k):
        C = self.C
        a, args = v["id"], v["args"]
        light, morale = s["light"], s["morale"]
        forged = s["forged"]
        if a in ("lamp", "cut"):
            r = self.rate(s, args["console"])
            n = args["amount"]
            light += -r * n if a == "lamp" else r * n
            morale += n if a == "lamp" else -n
        elif a == "walk":
            morale = min(C["MORALE_CAP"], morale + C["WALK"])
        elif a == "forge":
            light -= C["FORGE_COST"]
            forged = True
        light -= burn
        morale -= C["SLUMP"]
        if light < 0 or morale < 1:  # lit-ok
            return -C["_DEAD"]
        if left == 0:
            return C["_FINAL"] * self.pass_p(light, morale, forged) + C["_TIE"] * (light + k * morale)
        value = light + k * morale
        if left <= C["_END_TURNS"]:
            value += C["_PW"] * self.pass_p(light, morale, forged)
        buffer_m = C["SLUMP"] + C["_BUF_M"]
        if morale < buffer_m:
            value -= (buffer_m - morale) * C["_PEN_M"]
        if light < burn + C["_BUF_L"]:
            value -= (burn + C["_BUF_L"] - light) * C["_PEN_L"]
        if left <= C["_LEDGER_TURNS"] and light < C["LEDGER"]:
            value -= (C["LEDGER"] - light) * C["_PEN_LEDGER"]
        return value


if __name__ == "__main__":
    run(G)
