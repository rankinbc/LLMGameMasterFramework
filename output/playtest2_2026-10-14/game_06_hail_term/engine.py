"""Hail Term: a /play engine.

Rolls: FORM=17 triage (a queue of storms, limited board, waiting costs), SET=60 a weather system over a
farming valley, ROLE=27 headmaster (of the Valley Weather School), LOOP=21 dig deeper (each storm deepens a
layer while it waits: richer and riskier), CLOCK=3 debt of 60 due on turn 14, TWIST=37 information arrives one turn
late (storm reports are a day old), WIN=18 reach an approval number, MAP=8 one valley with six districts,
TONE=2 dry humor.

Rulesheet (8 lines):
1. Each turn do one thing: send the students to one storm, hold a tuition day (+12 cash), or buy gear. Wages cost 3 a turn.
2. Storms queue over six districts. A storm that has waited 2+ turns costs 1 approval a turn. The board holds 3; a fourth pushes the oldest out for -3 approval.
3. A storm has a layer 1 to 3. Sending rolls d6, need layer+2. Success pays 8/14/22 cash and +5/+7/+10 approval. Fail: -2 approval, storm stays.
4. Each turn a waiting storm may deepen one layer (1 in 3; 1 in 2 from turn 10): richer, harder. Layer 4 bursts: -6 approval, storm gone.
5. Reports are a day old: a storm's shown layer is last turn's, and new storms show "?". Students on site learn the true layer.
6. Pell's cloud-seeding wagon names the longest-waiting storm that has sat a day; next turn he takes it if it is still there (-2 approval, no pay).
7. Gear ladder: kites 20, barometer 20 (+1 to every roll each), then from turn 10 the semaphore line 35 (reports same day). From turn 10 storms come faster.
8. The bank takes 60 cash as turn 14 opens. Cash below 0 or approval 0 closes the school. After two failed sends old Agnes clears the longest-waiting storm for 12. Win: approval 70+ after turn 20.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

DISTRICTS = ["Mill Row", "Orchard End", "Hop Flats", "Sheepfold", "Fen Bottom", "Upper Terraces"]
KINDS = ["hail", "frost", "fog", "gale", "flood", "drought"]
PAY = {1: 8, 2: 14, 3: 22}
APPROVAL = {1: 5, 2: 7, 3: 10}
GEAR = [("kites", 20), ("barometer", 20), ("semaphore line", 35)]
BOARD = 3
DEBT = 60
DEBT_TURN = 14
TARGET = 70
SEASON_TURN = 10
WAGES = 3


class G(Game):
    name = "Hail Term"
    turns = 20

    # ------------------------------------------------------------ helpers
    def _spawn(self, s, rng, known=False):
        v = rng.d(6)
        layer = 1 if v <= 3 else (2 if v <= 5 else 3)
        c = {"id": s["next_id"], "district": rng.choice(DISTRICTS), "kind": rng.choice(KINDS),
             "seen": layer if (known or s["gear"] >= 3) else None, "age": 0}
        s["next_id"] += 1
        s["hidden"]["layers"][str(c["id"])] = layer
        s["queue"].append(c)
        return c

    def _find(self, s, cid):
        for c in s["queue"]:
            if c["id"] == cid:
                return c
        return None

    def _remove(self, s, c):
        s["queue"] = [x for x in s["queue"] if x["id"] != c["id"]]
        s["hidden"]["layers"].pop(str(c["id"]), None)

    def _oldest(self, s, min_age=0):
        pool = [c for c in s["queue"] if c["age"] >= min_age]
        if not pool:
            return None
        return max(pool, key=lambda c: (c["age"], -c["id"]))

    def _name(self, c):
        return f"{c['district']} {c['kind']}"

    def _shown(self, c):
        return "?" if c["seen"] is None else str(c["seen"])

    # ------------------------------------------------------------ contract
    def init_state(self, rng):
        s = {"cash": 30, "approval": 40, "gear": 0, "queue": [], "pell": None, "streak": 0, "next_id": 1,
             "closed": None, "hidden": {"layers": {}}}
        for _ in range(2):
            self._spawn(s, rng, known=True)
        s["queue"][0]["age"] = 1
        s["pell"] = s["queue"][0]["id"]
        return s

    def options(self, s):
        o = []
        for c in s["queue"]:
            tag = ", Pell's target" if s["pell"] == c["id"] else ""
            o.append({"id": "send",
                      "label": f"Send the students to {self._name(c)} (layer {self._shown(c)}, waited {c['age']}{tag})",
                      "args": {"case": c["id"]}})
        o.append({"id": "tuition", "label": "Hold a tuition day (+12 cash, nobody goes out)", "args": {}})
        if s["streak"] >= 2 and s["queue"] and s["cash"] >= 12:
            old = self._oldest(s)
            o.append({"id": "agnes", "label": f"Fetch old Agnes out of retirement (-12 cash): she clears {self._name(old)}",
                      "args": {}})
        elif s["gear"] < len(GEAR):
            name, cost = GEAR[s["gear"]]
            if s["cash"] >= cost and (s["gear"] < 2 or s["_turn"] >= SEASON_TURN):
                what = "+1 to every roll" if s["gear"] < 2 else "reports arrive same day"
                o.append({"id": "gear", "label": f"Buy the {name} (-{cost} cash, {what})", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        ev = []
        if a == "send":
            c = self._find(s, args.get("case"))
            if c is None:
                c = s["queue"][0]
            actual = s["hidden"]["layers"][str(c["id"])]
            if c["seen"] != actual:
                ev.append(f"On the road the report catches up: {self._name(c)} is layer {actual}.")
            bonus = min(s["gear"], 2)
            need = max(1, actual + 2 - bonus)
            ok, txt = rng.check(need, label=self._name(c))
            if ok:
                s["cash"] += PAY[actual]
                s["approval"] += APPROVAL[actual]
                s["streak"] = 0
                self._remove(s, c)
                ev.append(f"{txt}. The farmers pay {PAY[actual]}. Approval +{APPROVAL[actual]}.")
            else:
                s["approval"] -= 2
                s["streak"] += 1
                c["seen"] = actual
                ev.append(f"{txt}. The storm is still there. Approval -2.")
        elif a == "tuition":
            s["cash"] += 12
            ev.append("Tuition day. The fees bring 12 cash.")
        elif a == "gear":
            name, cost = GEAR[s["gear"]]
            s["cash"] -= cost
            s["gear"] += 1
            if s["gear"] == 3:
                for c in s["queue"]:
                    c["seen"] = s["hidden"]["layers"][str(c["id"])]
                ev.append(f"Bought the {name} for {cost}. Reports now arrive the same day; the board is corrected.")
            else:
                ev.append(f"Bought the {name} for {cost}. Rolls now get +{s['gear']}.")
        elif a == "agnes":
            s["cash"] -= 12
            c = self._oldest(s)
            actual = s["hidden"]["layers"][str(c["id"])]
            s["approval"] += APPROVAL[actual]
            s["streak"] = 0
            self._remove(s, c)
            ev.append(f"Agnes walks into {self._name(c)} (layer {actual}) and walks out again. Approval +{APPROVAL[actual]}. No fee; she does not do invoices.")
        return ev

    def advance(self, s, rng):
        ev = []
        t = s["_turn"]
        s["cash"] -= WAGES
        ev.append(f"Wages {WAGES}.")
        if t == SEASON_TURN:
            ev.append("Turn 10: storm season. Storms come faster and deepen more often. The semaphore line is for sale.")
        stale = [c for c in s["queue"] if c["age"] >= 2]
        n = len(stale)
        if n:
            s["approval"] -= n
            ev.append(f"{n} storm{'s' if n > 1 else ''} left waiting two days or more: approval -{n}.")
        # Pell takes the storm he named last turn
        if s["pell"] is not None:
            c = self._find(s, s["pell"])
            if c is not None:
                self._remove(s, c)
                s["approval"] -= 2
                ev.append(f"Pell's wagon seeded {self._name(c)} before you got there. Approval -2.")
            s["pell"] = None
        # reports and deepening
        p = 0.5 if t >= SEASON_TURN else 0.35
        for c in list(s["queue"]):
            c["age"] += 1
            key = str(c["id"])
            actual = s["hidden"]["layers"][key]
            if s["gear"] < 3:
                c["seen"] = actual
            if rng.chance(p):
                actual += 1
                if actual >= 4:
                    self._remove(s, c)
                    s["approval"] -= 6
                    ev.append(f"{self._name(c)} burst over the fields. Approval -6.")
                    continue
                s["hidden"]["layers"][key] = actual
            if s["gear"] >= 3:
                c["seen"] = actual
        # arrivals
        k = 1 + (1 if rng.chance(0.5 if t >= SEASON_TURN else 0.15) else 0)
        for _ in range(k):
            c = self._spawn(s, rng)
            ev.append(f"Word from {c['district']}: {c['kind']} coming in, layer {self._shown(c)}.")
            if len(s["queue"]) > BOARD:
                old = self._oldest(s)
                self._remove(s, old)
                s["approval"] -= 3
                ev.append(f"The board is full. {self._name(old)} goes unanswered. Approval -3.")
        # Pell names his next target: the longest-waiting storm that has sat at least a day
        old = self._oldest(s, min_age=1)
        if old is not None:
            s["pell"] = old["id"]
            ev.append(f"Pell's wagon is pointed at {old['district']}.")
        else:
            ev.append("Pell's wagon sits idle outside the inn.")
        # the bank
        if t == DEBT_TURN - 1:
            ev.append(f"The bank's man will be here tomorrow for {DEBT}.")
        elif t == DEBT_TURN:
            if s["cash"] >= DEBT:
                s["cash"] -= DEBT
                ev.append(f"The bank's man takes {DEBT} and leaves a receipt.")
            else:
                s["closed"] = f"the bank came for {DEBT} and found {s['cash']}"
                ev.append(f"The bank's man came for {DEBT} and found {s['cash']}.")
        return ev

    def status_line(self, s):
        return f"Cash {s['cash']} | Approval {s['approval']} | Board {len(s['queue'])}/{BOARD} | Roll +{min(s['gear'], 2)}"

    def visible(self, s):
        v = {k: x for k, x in s.items() if k not in ("hidden", "_rng", "_turn", "_ended")}
        pc = self._find(s, s["pell"]) if s["pell"] is not None else None
        v["pell_target"] = self._name(pc) if pc else None
        v["gear_owned"] = [g[0] for g in GEAR[:s["gear"]]]
        return v

    def check_end(self, s):
        if s["closed"]:
            return {"result": "loss", "reason": s["closed"]}
        if s["cash"] < 0:
            return {"result": "loss", "reason": "out of cash"}
        if s["approval"] <= 0:
            return {"result": "loss", "reason": "the valley stopped answering the school's letters"}
        if s["_turn"] > self.turns:
            if s["approval"] >= TARGET:
                return {"result": "win", "reason": f"approval {s['approval']} after turn {self.turns}"}
            return {"result": "loss", "reason": f"approval {s['approval']}, needed {TARGET}"}
        return None

    def heuristic(self, s, options, rng):
        ids = {o["id"] for o in options}
        t = s["_turn"]
        bonus = min(s["gear"], 2)
        # projected cash on bank day, assuming sends net about +4 a turn after wages
        left = max(0, DEBT_TURN - t)
        proj = s["cash"] + 4 * left
        if "agnes" in ids and s["cash"] - 12 >= 10 and (t >= DEBT_TURN or proj - 12 >= DEBT + 6):
            return "agnes"
        if "gear" in ids:
            cost = GEAR[s["gear"]][1]
            if s["gear"] < 2 and t <= 6 and s["cash"] - cost >= 12:
                return "gear"
            if s["gear"] < 2 and t > DEBT_TURN and t <= 17 and s["cash"] - cost >= 12:
                return "gear"
            if s["gear"] == 2 and t > DEBT_TURN and t <= 16 and s["cash"] - cost >= 12:
                return "gear"
        sends = [o for o in options if o["id"] == "send"]
        best, best_v = None, -99.0
        for o in sends:
            c = self._find(s, o["args"]["case"])
            est = c["seen"] if c["seen"] is not None else 1.5
            est_i = int(round(est))
            need = max(1, est_i + 2 - bonus)
            pr = max(0.0, min(1.0, (7 - need) / 6))
            v = pr * APPROVAL[min(3, est_i)] - (1 - pr) * 2
            if s["pell"] == c["id"]:
                v += 2.5
            if c["seen"] == 3:
                v += 1.5  # about to burst
            if c["age"] >= 1:
                v += 1.0  # it starts costing soon
            if best is None or v > best_v:
                best, best_v = o, v
        # money first when the bank is near and the projection is short
        if t < DEBT_TURN and t >= 8 and proj < DEBT + 2:
            return "tuition"
        if best is not None and best_v > -0.5:
            return best
        if t < DEBT_TURN and proj < DEBT + 6:
            return "tuition"
        if best is not None:
            return best
        return "tuition"


if __name__ == "__main__":
    run(G)
