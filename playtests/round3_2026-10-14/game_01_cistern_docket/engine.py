"""Cistern Docket: the Collegium's cisterns are draining and the cafe owner keeps the docket.

Engine for /play (v2 contract). A triage queue of reports, two desks, a hidden-habit siphon,
a cafe owner who slowly turns into a heron. Rulesheet: run `python engine.py rules`.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, run  # noqa: E402

ISLES = ["Library", "Kitchens", "Tower"]
POOL = ["Orsk", "Pell", "Vey", "Mabry", "Tolliver", "Quillon", "Haskett", "Ingrith", "Dross", "Sabine"]
FORMS = ["Cook", "Webbed", "Heron"]


class G(Game):
    name = "Cistern Docket"

    CONSTANTS = {
        "TURNS": 13,
        "SUSPECTS": 5,
        "NAME_PIECES": 2,
        "HEARING": 10,
        "WATER_START": 33,
        "DROP": 1,
        "DROP_LATE": 2,
        "LATE_TURN": 11,
        "SIPHON": 2,
        "ARRIVE": 1,
        "ARRIVE_P": 0.5,
        "QUEUE_MAX": 4,
        "LAPSE_AGE": 3,
        "LAPSE_COST": 1,
        "TIP_TRUE": 0.3,
        "CAFE_GAIN": 1,
        "FIELD_GAIN": 2,
        "FIELD_BUSY": 1,
        "FERRY": 1,
        "CHECK_COST": 7,
        "BIND_COST": 4,
        "BIND_GAIN": 1,
        "FORM1": 4,
        "HERON": 8,
        "GLIMPSE_FALSE": 2,
    }

    RULES = """
1. {SUSPECTS} suspects, one draining the cisterns. From night {HEARING} you may name the culprit while holding {NAME_PIECES} pieces of evidence against them: right wins, wrong loses. Water at 0 or no verdict in {TURNS} nights also loses.
2. Water starts at {WATER_START} and falls {DROP} a night ({DROP_LATE} from night {LATE_TURN}). Each night the siphon strikes one isle by a fixed habit you must infer from past strikes, and draws {SIPHON} Water.
3. {ARRIVE} report arrives each night, and a second {ARRIVE_P:.0%} of the time. The queue holds {QUEUE_MAX}; past that the oldest is bumped. A report unworked for {LAPSE_AGE} nights lapses. Each lapse or bump costs {LAPSE_COST} Water.
4. Each report comes from an isle and names a suspect: {TIP_TRUE:.0%} name the culprit, the rest an innocent at random.
5. Each night assign one report to a free desk. Cafe desk: gossip, +{CAFE_GAIN} Evidence. Field desk: +{FIELD_GAIN} Evidence and one piece against the suspect named, then busy {FIELD_BUSY} night; crossing to another isle costs {FERRY} Water.
6. Cross-check a suspect for {CHECK_COST} Evidence. An innocent is cleared: their pieces are struck, none are gained later, they cannot be named. The culprit's alibi cracks: +1 piece, once.
7. Bind your ledger once for {BIND_COST} Evidence: every desk then yields +{BIND_GAIN} Evidence.
8. From night {FORM1} you are Webbed: ferries are free. From night {HERON} you are Heron: the cafe desk closes, but you may stand watch on an isle instead of working. If the siphon strikes it you glimpse a hooded figure: +1 piece against the culprit and against {GLIMPSE_FALSE} innocents at random, and it draws nothing.
"""

    ACTIONS = ["cafe", "field", "check", "bind", "watch", "name"]
    TAGS = ["hearing", "webbed", "heron", "late_drop", "lapse", "bump", "crack", "clear", "bind", "catch", "miss", "cleared_tip"]

    BOUNDS = {
        "evidence": (0, 80), "water": (-15, 80), "isle": (0, 2), "field_ready": (0, 40),
        "seq": (0, 300), "named": (0, 9),
    }
    REACH = {"water": ("<=", 0), "evidence": 7}
    GATES = {
        "cafe": {"_if": lambda g, s: bool(s["queue"]) and g._form(s) < 2},
        "field": {"_if": lambda g, s: any(g._can_field(s, r) for r in s["queue"])},
        "check": {"evidence": "CHECK_COST",
                  "_if": lambda g, s: any(not s["cleared"][i] and not s["cracked"][i] for i in range(len(s["pieces"])))},
        "bind": {"evidence": "BIND_COST", "!bound": 1},
        "watch": {"_turn": "HERON"},
        "name": {"_turn": "HEARING",
                 "_if": lambda g, s: any(s["pieces"][i] >= g.C["NAME_PIECES"] and not s["cleared"][i]
                                         for i in range(len(s["pieces"])))},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    @staticmethod
    def _pc(n):
        return f"{n} piece" if n == 1 else f"{n} pieces"

    def _form(self, s):
        t = s["_turn"]
        return 2 if t >= self.C["HERON"] else 1 if t >= self.C["FORM1"] else 0

    def _bonus(self, s):
        return self.C["BIND_GAIN"] if s["bound"] else 0

    def _fare(self, s, r):
        if r["isle"] == s["isle"] or self._form(s) >= 1:
            return 0
        return self.C["FERRY"]

    def _can_field(self, s, r):
        return s["_turn"] >= s["field_ready"] and s["water"] > self._fare(s, r)

    def _drop(self, night):
        return self.C["DROP_LATE"] if night >= self.C["LATE_TURN"] else self.C["DROP"]

    def _counts(self, s):
        return [sum(1 for r in s["queue"] if r["isle"] == i) for i in range(3)]

    def _target(self, s):
        h = s["hidden"]
        if h["habit"] == 2:
            counts = self._counts(s)
            return counts.index(max(counts))
        stride = 1 if h["habit"] == 0 else 2
        return (h["pos"] + stride) % 3

    def _report(self, s, rid):
        for r in s["queue"]:
            if r["id"] == rid:
                return r
        return None

    def _spawn(self, s, rng, ev):
        C = self.C
        h = s["hidden"]
        n = C["SUSPECTS"]
        isle = rng.d(3) - 1
        if rng.chance(C["TIP_TRUE"]):
            names = h["culprit"]
        else:
            innocents = [i for i in range(n) if i != h["culprit"]]
            names = innocents[rng.d(len(innocents)) - 1]
        rid = max([s["seq"]] + [r["id"] for r in s["queue"]]) + 1
        s["seq"] = rid
        s["queue"].append({"id": rid, "isle": isle, "age": 0, "names": names})
        ev.append(f"Report {rid} arrives from the {ISLES[isle]}, naming {s['suspects'][names]}.")

    def _arrive(self, s, rng, ev):
        C = self.C
        count = C["ARRIVE"] + (1 if rng.chance(C["ARRIVE_P"]) else 0)
        for _ in range(count):
            self._spawn(s, rng, ev)

    # ------------------------------------------------------------ state

    def init_state(self, rng):
        C = self.C
        pool = list(POOL)
        rng.shuffle(pool)
        names = pool[: C["SUSPECTS"]]
        n = C["SUSPECTS"]
        s = {
            "evidence": 0,
            "water": C["WATER_START"],
            "isle": 1,
            "bound": False,
            "field_ready": 0,
            "seq": 0,
            "queue": [],
            "suspects": names,
            "pieces": [0] * n,
            "cleared": [False] * n,
            "cracked": [False] * n,
            "strikes": [],
            "watch": None,
            "named": None,
            "hidden": {"culprit": rng.d(n) - 1, "habit": rng.d(3) - 1, "pos": rng.d(3) - 1},
        }
        self._arrive(s, rng, [])
        return s

    def visible(self, s):
        names = s["suspects"]
        board = []
        for i, nm in enumerate(names):
            state = "cleared" if s["cleared"][i] else "cracked" if s["cracked"][i] else "open"
            board.append({"suspect": nm, "pieces": s["pieces"][i], "state": state})
        return {
            "evidence": s["evidence"],
            "water": s["water"],
            "isle": ISLES[s["isle"]],
            "form": FORMS[self._form(s)],
            "ledger": "bound" if s["bound"] else "unbound",
            "queue": [{"id": r["id"], "isle": ISLES[r["isle"]], "names": names[r["names"]], "waiting": r["age"]}
                      for r in s["queue"]],
            "board": board,
            "desks": {
                "cafe": "closed" if self._form(s) >= 2 else "open",
                "field": "ready" if s["_turn"] >= s["field_ready"] else f"busy until night {s['field_ready']}",
            },
            "strikes": [{"night": k + 1, "isle": ISLES[x[0]], "waiting_reports": x[1:]} for k, x in enumerate(s["strikes"])],
        }

    # ------------------------------------------------------------ options

    def options(self, s):
        C = self.C
        names = s["suspects"]
        o = []
        form = self._form(s)
        bonus = self._bonus(s)
        for r in s["queue"]:
            grp = f"Report {r['id']} ({ISLES[r['isle']]}, names {names[r['names']]}, waiting {r['age']})"
            if form < 2:
                o.append({"id": "cafe", "label": f"Cafe desk: gossip over report {r['id']} (+{C['CAFE_GAIN'] + bonus} Evidence)",
                          "args": {"report": r["id"]}, "group": grp})
            if self._can_field(s, r):
                fare = self._fare(s, r)
                piece = "no piece, suspect cleared" if s["cleared"][r["names"]] else f"+1 piece on {names[r['names']]}"
                cost = f", -{fare} Water ferry" if fare else ""
                o.append({"id": "field", "label": f"Field desk: report {r['id']} at the {ISLES[r['isle']]} (+{C['FIELD_GAIN'] + bonus} Evidence, {piece}{cost})",
                          "args": {"report": r["id"]}, "group": grp})
        if s["evidence"] >= C["CHECK_COST"]:
            for i, nm in enumerate(names):
                if not s["cleared"][i] and not s["cracked"][i]:
                    o.append({"id": "check", "label": f"Cross-check {nm} (-{C['CHECK_COST']} Evidence, {self._pc(s['pieces'][i])} held)",
                              "args": {"suspect": i}, "group": "Cross-check a suspect"})
        if s["evidence"] >= C["BIND_COST"] and not s["bound"]:
            o.append({"id": "bind", "label": f"Bind the ledger (-{C['BIND_COST']} Evidence, every desk +{C['BIND_GAIN']} Evidence after)",
                      "args": {}})
        if form >= 2:
            for i, nm in enumerate(ISLES):
                o.append({"id": "watch", "label": f"Stand watch on the {nm} (skip desk work, catch the siphon if it strikes there)",
                          "args": {"isle": i}, "group": "Stand watch on an isle"})
        if s["_turn"] >= C["HEARING"]:
            for i, nm in enumerate(names):
                if s["pieces"][i] >= C["NAME_PIECES"] and not s["cleared"][i]:
                    o.append({"id": "name", "label": f"Name {nm} as the culprit ({self._pc(s['pieces'][i])} held)",
                              "args": {"suspect": i}, "group": "Name the culprit"})
        return o

    # ------------------------------------------------------------ apply

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        names = s["suspects"]
        if a in ("cafe", "field"):
            r = self._report(s, args["report"])
            bonus = self._bonus(s)
            if a == "cafe":
                gain = C["CAFE_GAIN"] + bonus
                s["evidence"] += gain
                ev.append(f"Gossip at the cafe over report {r['id']} ({ISLES[r['isle']]}, names {names[r['names']]}). Evidence +{gain}.")
            else:
                fare = self._fare(s, r)
                if fare:
                    s["water"] -= fare
                    ev.append(f"The ferry to the {ISLES[r['isle']]} draws on the cisterns. Water -{fare}.")
                s["isle"] = r["isle"]
                gain = C["FIELD_GAIN"] + bonus
                s["evidence"] += gain
                s["field_ready"] = s["_turn"] + C["FIELD_BUSY"] + 1
                who = names[r["names"]]
                if s["cleared"][r["names"]]:
                    self.hit("cleared_tip")
                    ev.append(f"Field work on report {r['id']} at the {ISLES[r['isle']]}. Evidence +{gain}. {who} is already cleared, so no piece.")
                else:
                    s["pieces"][r["names"]] += 1
                    ev.append(f"Field work on report {r['id']} at the {ISLES[r['isle']]}. Evidence +{gain}, and one piece against {who}.")
            s["queue"] = [q for q in s["queue"] if q["id"] != r["id"]]
        elif a == "check":
            i = args["suspect"]
            s["evidence"] -= C["CHECK_COST"]
            if i == s["hidden"]["culprit"]:
                s["cracked"][i] = True
                s["pieces"][i] += 1
                self.hit("crack")
                ev.append(f"Cross-check on {names[i]}: the alibi cracks. One more piece against {names[i]}. Evidence -{C['CHECK_COST']}.")
            else:
                s["cleared"][i] = True
                s["pieces"][i] = 0
                self.hit("clear")
                ev.append(f"Cross-check on {names[i]}: the alibi holds. {names[i]} is cleared and their pieces are struck. Evidence -{C['CHECK_COST']}.")
        elif a == "bind":
            s["evidence"] -= C["BIND_COST"]
            s["bound"] = True
            self.hit("bind")
            ev.append(f"You bind the ledger. Every desk now yields +{C['BIND_GAIN']} Evidence. Evidence -{C['BIND_COST']}.")
        elif a == "watch":
            s["watch"] = args["isle"]
            s["isle"] = args["isle"]
            ev.append(f"You carry a lantern to the {ISLES[args['isle']]} cistern and wait out the night.")
        elif a == "name":
            i = args["suspect"]
            s["named"] = i
            who = names[i]
            if i == s["hidden"]["culprit"]:
                ev.append(f"You name {who} before the Bursar. The pieces hold, and the siphon is stopped.")
            else:
                ev.append(f"You name {who} before the Bursar. The hearing clears {who}, and the real culprit walks.")
        return ev

    # ------------------------------------------------------------ advance

    def advance(self, s, rng):
        C = self.C
        h = s["hidden"]
        ev = []
        night = s["_turn"] - 1
        if s["_turn"] == C["HEARING"]:
            self.hit("hearing")
            ev.append(f"Night {s['_turn']}: the Bursar opens the hearing. Names may be given from tonight.")
        if s["_turn"] == C["FORM1"]:
            self.hit("webbed")
            ev.append(f"Night {s['_turn']}: your fingers have webbed. The ferries cost you nothing now.")
        if s["_turn"] == C["HERON"]:
            self.hit("heron")
            ev.append(f"Night {s['_turn']}: you wake a heron. The regulars flee the cafe, but you can stand a watch.")
        if s["_turn"] == C["LATE_TURN"]:
            self.hit("late_drop")
            ev.append(f"Night {s['_turn']}: the aquifer cracks. The table will fall {C['DROP_LATE']} a night.")
        # reports age; the stale ones lapse
        keep = []
        for r in s["queue"]:
            r["age"] += 1
            if r["age"] >= C["LAPSE_AGE"]:
                s["water"] -= C["LAPSE_COST"]
                self.hit("lapse")
                ev.append(f"Report {r['id']} lapses unworked. Water -{C['LAPSE_COST']}.")
            else:
                keep.append(r)
        s["queue"] = keep
        # new reports; an overfull queue bumps its oldest
        self._arrive(s, rng, ev)
        while len(s["queue"]) > C["QUEUE_MAX"]:
            oldest = max(s["queue"], key=lambda q: (q["age"], -q["id"]))
            s["queue"] = [q for q in s["queue"] if q["id"] != oldest["id"]]
            s["water"] -= C["LAPSE_COST"]
            self.hit("bump")
            ev.append(f"The queue overflows and report {oldest['id']} is bumped. Water -{C['LAPSE_COST']}.")
        # the siphon strikes
        target = self._target(s)
        counts = self._counts(s)
        qtxt = ", ".join(f"{ISLES[i]} {counts[i]}" for i in range(3))
        s["strikes"].append([target] + counts)
        h["pos"] = target
        if s["watch"] is not None and s["watch"] == target:
            self.hit("catch")
            culprit = h["culprit"]
            s["pieces"][culprit] += 1
            cands = [i for i in range(C["SUSPECTS"]) if i != culprit and not s["cleared"][i]]
            hit_names = []
            for _ in range(min(C["GLIMPSE_FALSE"], len(cands))):
                j = cands.pop(rng.d(len(cands)) - 1)
                s["pieces"][j] += 1
                hit_names.append(s["suspects"][j])
            extra = (" and against " + " and ".join(hit_names)) if hit_names else ""
            ev.append(f"The siphon strikes the {ISLES[target]} cistern and finds you waiting. A hooded figure bolts: one piece against {s['suspects'][culprit]}{extra}. The siphon draws nothing.")
        else:
            if s["watch"] is not None:
                self.hit("miss")
                ev.append(f"You watched the {ISLES[s['watch']]}, but the siphon struck the {ISLES[target]}.")
            s["water"] -= C["SIPHON"]
            ev.append(f"The siphon strikes the {ISLES[target]} cistern (waiting reports: {qtxt}). Water -{C['SIPHON']}.")
        s["watch"] = None
        drop = self._drop(night)
        s["water"] -= drop
        ev.append(f"The table falls. Water -{drop}.")
        return ev

    # ------------------------------------------------------------ status, end

    def status_line(self, s):
        return f"Evidence {s['evidence']} | Water {max(0, s['water'])} | Isle: {ISLES[s['isle']]} | Form: {FORMS[self._form(s)]}"

    def check_end(self, s):
        names = s["suspects"]
        if s["named"] is not None:
            c = s["hidden"]["culprit"]
            if s["named"] == c:
                return {"result": "win", "reason": f"{names[c]} was the culprit and the pieces held"}
            return {"result": "loss", "reason": f"{names[s['named']]} was innocent; the culprit was {names[c]}"}
        if s["water"] <= 0:
            return {"result": "loss", "reason": "the cisterns ran dry"}
        if s["_turn"] > self.turns:
            return {"result": "loss", "reason": f"no verdict in {self.turns} nights"}
        return None

    # ------------------------------------------------------------ the sensible player

    def _fits(self, s):
        """Habits consistent with the strikes seen so far: 0 ring up, 1 ring down, 2 busiest isle."""
        st = s["strikes"]
        fits = []
        for hb in (0, 1, 2):
            ok = True
            if hb in (0, 1):
                stride = 1 if hb == 0 else 2
                for a, b in zip(st, st[1:]):
                    if (a[0] + stride) % 3 != b[0]:
                        ok = False
            else:
                for x in st:
                    if x[1:].index(max(x[1:])) != x[0]:
                        ok = False
            if ok:
                fits.append(hb)
        return fits

    def heuristic(self, s, options, rng):
        C = self.C
        by = {}
        for o in options:
            by.setdefault(o["id"], []).append(o)
        pcs, cl, cr = s["pieces"], s["cleared"], s["cracked"]
        n = len(pcs)
        live = [i for i in range(n) if not cl[i]]
        for o in by.get("name", []):
            if cr[o["args"]["suspect"]]:
                return o
        if "name" in by:
            top0 = max(by["name"], key=lambda o: pcs[o["args"]["suspect"]])
            if s["water"] <= C["SIPHON"] + self._drop(s["_turn"]) + 1:
                return top0  # the cisterns will not outlast another night: name now
        if "check" in by:
            cand = [o for o in by["check"] if pcs[o["args"]["suspect"]] >= 1]
            if cand:
                return max(cand, key=lambda o: pcs[o["args"]["suspect"]])
        if "name" in by:
            top = max(by["name"], key=lambda o: pcs[o["args"]["suspect"]])
            i = top["args"]["suspect"]
            rival = max([pcs[j] for j in live if j != i], default=0)
            margin = pcs[i] - rival
            if margin >= 2 or (margin >= 1 and s["water"] <= 8) or s["water"] <= 5:
                return top
        if "watch" in by:
            fits = self._fits(s)
            if len(s["strikes"]) >= 2 and len(fits) == 1 and fits[0] in (0, 1):
                stride = 1 if fits[0] == 0 else 2
                tgt = (s["strikes"][-1][0] + stride) % 3
                for o in by["watch"]:
                    if o["args"]["isle"] == tgt:
                        return o
        if "bind" in by and s["_turn"] <= 5:
            return by["bind"][0]
        work = by.get("field", []) + by.get("cafe", [])
        if work:
            def value(o):
                r = self._report(s, o["args"]["report"])
                v = 0
                v += 4 if o["id"] == "field" else 0
                v += 2 * r["age"]
                v += 1 if not cl[r["names"]] else -3
                v += 1 if r["isle"] == s["isle"] else 0
                return v
            return max(work, key=value)
        return by["watch"][0] if "watch" in by else options[0]

    # ------------------------------------------------------------ the executable spec

    def rule_tests(self):
        C = self.C

        def rep(i, isle, names, age=0):
            return {"id": i, "isle": isle, "names": names, "age": age}

        def r1(t):
            s = t.fresh(hidden__culprit=2, pieces=[0, 0, C["NAME_PIECES"], 0, 0], _turn=C["HEARING"] - 1)
            t.ok(not t.offered(s, "name", suspect=2), "no naming before the hearing night")
            s["_turn"] = C["HEARING"]
            t.ok(t.offered(s, "name", suspect=2), "naming is open from the hearing night")
            s["pieces"] = [0, 0, C["NAME_PIECES"] - 1, 0, 0]
            t.ok(not t.offered(s, "name", suspect=2), "too few pieces to name")
            s["pieces"] = [C["NAME_PIECES"], 0, C["NAME_PIECES"], 0, 0]
            t.eq(len(t.ids(s)) > 0, True, "options exist")
            right, _ = t.step(copy_state(s), "name", {"suspect": 2})
            t.eq(right["_ended"]["result"], "win", "naming the culprit with enough pieces wins")
            wrong, _ = t.step(copy_state(s), "name", {"suspect": 0})
            t.eq(wrong["_ended"]["result"], "loss", "naming an innocent loses")
            dry = t.fresh(water=0)
            t.eq((self.check_end(dry) or {}).get("result"), "loss", "Water at 0 loses")
            late = t.fresh()
            late["_turn"] = C["TURNS"] + 1
            t.eq((self.check_end(late) or {}).get("result"), "loss", "no verdict in time loses")
            t.eq(len(t.fresh()["suspects"]), C["SUSPECTS"], "the suspect count")

        def r2(t):
            s0 = t.fresh()
            t.eq(s0["water"], C["WATER_START"], "starting Water")
            s = t.fresh(queue=[], water=40, hidden__habit=0, hidden__pos=0)
            ev = t.advance(s, turn=2, chances=[0.99, 0.99])
            t.eq(s["water"], 40 - C["DROP"] - C["SIPHON"], "the siphon and the base fall")
            t.eq(s["strikes"][-1][0], 1, "ring habit steps one isle")
            t.ok(any("siphon strikes the Kitchens" in e for e in ev), "the strike is told after it happens")
            t.ok("habit" not in str(self.visible(s)), "the habit stays hidden")
            s = t.fresh(queue=[], water=40, hidden__habit=1, hidden__pos=0)
            t.advance(s, turn=2, chances=[0.99, 0.99])
            t.eq(s["strikes"][-1][0], 2, "the other ring habit steps the other way")
            s = t.fresh(queue=[rep(1, 2, 0), rep(2, 2, 1)], water=40, hidden__habit=2, hidden__pos=0)
            t.advance(s, turn=2, chances=[0.99, 0.99], dice=[1, 1])
            t.eq(s["strikes"][-1][0], 2, "the busiest habit hits the isle with most waiting reports")
            s = t.fresh(queue=[], water=40, hidden__habit=0, hidden__pos=0)
            t.advance(s, turn=C["LATE_TURN"], chances=[0.99, 0.99])
            t.eq(s["water"], 40 - C["DROP"] - C["SIPHON"], "the base fall before the late night")
            s = t.fresh(queue=[], water=40, hidden__habit=0, hidden__pos=0)
            t.advance(s, turn=C["LATE_TURN"] + 1, chances=[0.99, 0.99])
            t.eq(s["water"], 40 - C["DROP_LATE"] - C["SIPHON"], "the late fall from the late night")

        def r3(t):
            s = t.fresh(queue=[], water=40)
            t.advance(s, turn=2, chances=[0.99, 0.99])
            t.eq(len(s["queue"]), C["ARRIVE"], "one report a night")
            s = t.fresh(queue=[], water=40)
            t.advance(s, turn=2, chances=[0.0, 0.99, 0.99])
            t.eq(len(s["queue"]), C["ARRIVE"] + 1, "a second report sometimes")
            s = t.fresh(queue=[rep(1, 0, 0, C["LAPSE_AGE"] - 1), rep(2, 0, 1, 0)], water=40, hidden__habit=0, hidden__pos=0)
            t.advance(s, turn=2, chances=[0.99, 0.99])
            t.ok(all(r["id"] != 1 for r in s["queue"]), "a report unworked for LAPSE_AGE nights lapses")
            t.ok(any(r["id"] == 2 and r["age"] == 1 for r in s["queue"]), "a younger report waits and ages")
            t.eq(s["water"], 40 - C["LAPSE_COST"] - C["DROP"] - C["SIPHON"], "a lapse costs Water")
            full = [rep(i + 1, 0, 1, 0) for i in range(C["QUEUE_MAX"])]
            full[0]["age"] = C["LAPSE_AGE"] - 2
            s = t.fresh(queue=full, water=40, hidden__habit=0, hidden__pos=0)
            t.advance(s, turn=2, chances=[0.99, 0.99])
            t.eq(len(s["queue"]), C["QUEUE_MAX"], "the queue holds QUEUE_MAX")
            t.ok(all(r["id"] != 1 for r in s["queue"]), "the oldest is bumped")
            t.eq(s["water"], 40 - C["LAPSE_COST"] - C["DROP"] - C["SIPHON"], "a bump costs Water")

        def r4(t):
            s = t.fresh(queue=[], hidden__culprit=3)
            t.advance(s, turn=2, chances=[0.99, C["TIP_TRUE"] - 0.001], dice=[2])
            t.eq(s["queue"][-1]["names"], 3, "a true report names the culprit")
            t.eq(s["queue"][-1]["isle"], 1, "the report comes from an isle")
            s = t.fresh(queue=[], hidden__culprit=3)
            t.advance(s, turn=2, chances=[0.99, C["TIP_TRUE"]], dice=[3, 1])
            t.eq(s["queue"][-1]["names"], 0, "a false report names an innocent")
            t.eq(s["queue"][-1]["isle"], 2, "the false report comes from an isle")

        def r5(t):
            s = t.fresh(evidence=0, queue=[rep(1, 1, 2)], isle=1, _turn=2, water=30)
            t.apply(s, "cafe", {"report": 1})
            t.eq(s["evidence"], C["CAFE_GAIN"], "cafe gain")
            t.eq(s["pieces"], [0] * C["SUSPECTS"], "gossip yields no piece")
            t.eq(s["queue"], [], "the worked report leaves the queue")
            s = t.fresh(evidence=0, queue=[rep(1, 1, 2), rep(2, 1, 3)], isle=1, _turn=2, water=30)
            t.apply(s, "field", {"report": 1})
            t.eq(s["evidence"], C["FIELD_GAIN"], "field gain")
            t.eq(s["pieces"][2], 1, "field work adds a piece against the named suspect")
            t.eq(s["water"], 30, "no ferry on the same isle")
            s["_turn"] = 2 + C["FIELD_BUSY"]
            t.ok(not t.offered(s, "field", report=2), "the field desk is busy")
            s["_turn"] = 2 + C["FIELD_BUSY"] + 1
            t.ok(t.offered(s, "field", report=2), "the field desk is free again")
            t.ok(t.offered(s, "cafe", report=2), "the cafe desk is free while the field desk is busy")
            s = t.fresh(queue=[rep(1, 0, 2)], isle=1, _turn=1, water=30)
            t.apply(s, "field", {"report": 1})
            t.eq(s["water"], 30 - C["FERRY"], "crossing to another isle costs Water")
            t.eq(s["isle"], 0, "you end on the new isle")

        def r6(t):
            s = t.fresh(evidence=C["CHECK_COST"], pieces=[0, 2, 0, 0, 0], hidden__culprit=3, _turn=2)
            t.apply(s, "check", {"suspect": 1})
            t.eq(s["evidence"], 0, "cross-check cost")
            t.eq(s["pieces"][1], 0, "a cleared suspect's pieces are struck")
            t.ok(not t.offered(s, "check", suspect=1), "no second check on a cleared suspect")
            s["queue"] = [rep(7, 1, 1)]
            s["_turn"] = 3
            t.apply(s, "field", {"report": 7})
            t.eq(s["pieces"][1], 0, "no piece is gained against a cleared suspect")
            s = t.fresh(evidence=C["CHECK_COST"], pieces=[0, 0, 0, 0, 0], hidden__culprit=3, _turn=C["HEARING"])
            t.apply(s, "check", {"suspect": 3})
            t.eq(s["pieces"][3], 1, "the culprit's alibi cracks for one piece")
            t.ok(not t.offered(s, "check", suspect=3), "once only")
            t.ok(not t.offered(t.fresh(evidence=C["CHECK_COST"] - 1, _turn=2), "check", suspect=0), "cross-check needs Evidence")
            s = t.fresh(pieces=[0, 3, 0, 0, 0], cleared=[False, True, False, False, False], _turn=C["HEARING"])
            t.ok(not t.offered(s, "name", suspect=1), "a cleared suspect cannot be named")

        def r7(t):
            s = t.fresh(evidence=C["BIND_COST"] - 1, _turn=2)
            t.ok(not t.offered(s, "bind"), "binding needs Evidence")
            s = t.fresh(evidence=C["BIND_COST"], queue=[rep(1, 1, 2), rep(2, 1, 2)], isle=1, _turn=2)
            t.apply(s, "bind")
            t.eq(s["evidence"], 0, "bind cost")
            t.ok(not t.offered(s, "bind"), "once only")
            t.apply(s, "cafe", {"report": 1})
            t.eq(s["evidence"], C["CAFE_GAIN"] + C["BIND_GAIN"], "the bound ledger lifts the cafe desk")
            t.apply(s, "field", {"report": 2})
            t.eq(s["evidence"], C["CAFE_GAIN"] + C["BIND_GAIN"] + C["FIELD_GAIN"] + C["BIND_GAIN"], "and the field desk")

        def r8(t):
            s = t.fresh(queue=[rep(1, 0, 2)], isle=1, water=30, _turn=C["FORM1"] - 1)
            t.apply(s, "field", {"report": 1})
            t.eq(s["water"], 30 - C["FERRY"], "ferries cost before Webbed")
            t.ok("Form: Cook" in self.status_line(s), "the form is shown")
            s = t.fresh(queue=[rep(1, 0, 2)], isle=1, water=30, _turn=C["FORM1"])
            t.apply(s, "field", {"report": 1})
            t.eq(s["water"], 30, "ferries are free once Webbed")
            t.ok("Form: Webbed" in self.status_line(s), "the form is shown")
            s = t.fresh(queue=[rep(1, 0, 2)], _turn=C["HERON"] - 1)
            t.ok(t.offered(s, "cafe", report=1) and not t.offered(s, "watch", isle=0), "before Heron: cafe open, no watch")
            s["_turn"] = C["HERON"]
            t.ok(not t.offered(s, "cafe", report=1), "from Heron the cafe desk is closed")
            t.ok(all(t.offered(s, "watch", isle=i) for i in range(3)), "from Heron you may stand watch")
            t.ok("Form: Heron" in self.status_line(s), "the form is shown")
            drop = self._drop(C["HERON"])
            s = t.fresh(queue=[], water=30, hidden__culprit=3, hidden__habit=0, hidden__pos=0, _turn=C["HERON"],
                        pieces=[0] * C["SUSPECTS"])
            t.apply(s, "watch", {"isle": 1})
            t.advance(s, turn=C["HERON"] + 1, chances=[0.99, 0.99], dice=[1, 1, 2, 1])
            t.eq(s["pieces"][3], 1, "a catch gives a piece against the culprit")
            t.eq(sum(s["pieces"]), 1 + C["GLIMPSE_FALSE"], "and one against each of GLIMPSE_FALSE innocents")
            t.ok(all(p <= 1 for p in s["pieces"]), "distinct suspects")
            t.eq(s["water"], 30 - drop, "a caught siphon draws nothing")
            s = t.fresh(queue=[], water=30, hidden__culprit=3, hidden__habit=0, hidden__pos=0, _turn=C["HERON"],
                        pieces=[0] * C["SUSPECTS"])
            t.apply(s, "watch", {"isle": 0})
            t.advance(s, turn=C["HERON"] + 1, chances=[0.99, 0.99], dice=[1, 1])
            t.eq(sum(s["pieces"]), 0, "a miss gives nothing")
            t.eq(s["water"], 30 - drop - C["SIPHON"], "a missed watch still pays the siphon")

        return [
            (1, "goal and hearing", r1), (2, "water and siphon", r2), (3, "queue and lapse", r3),
            (4, "reports name suspects", r4), (5, "desks", r5), (6, "cross-check", r6),
            (7, "ledger", r7), (8, "webbed and heron", r8),
        ]


def copy_state(s):
    import json
    return json.loads(json.dumps(s))


if __name__ == "__main__":
    run(G)
