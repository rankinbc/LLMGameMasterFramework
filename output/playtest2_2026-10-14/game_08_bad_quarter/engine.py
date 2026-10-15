"""Bad Quarter: /play engine (noir freight logistics on a ring colony).

Rolls: FORM=12 logistics (route limited vehicles through a network with delays),
SET=25 a hedge fund during a bad quarter, ROLE=10 colony governor,
LOOP=26 fill a schedule grid; slots compete for the same audience (here: weeks are the
slots, your landed tons and Carver's compete for the fund's weekly ledger),
CLOCK=14 crew morale, mutiny at zero, TWIST=23 something is where it should not be,
WIN=16 finish the season above .500 or win the final, MAP=2 hex ring of 8 around a
center, TONE=11 noir.

Rulesheet (8 lines):
1. You govern Harrow Ring for Lissom & Vane Capital: the Spindle hub and 8 docks in a circle. Each week give one order: send an idle hauler on a contract, push a hauler, rest the crews, or a special job when it appears.
2. A contract is pickup, drop, tons. The trip takes 1 week per hop from where the hauler sits (hub to any dock is 1 hop). Each week in transit a hauler rolls d6: on a 1 it slips a week.
3. Each week your landed tons face Carver Freight's. More wins the week; ties go to Carver. Every even week Carver signs the biggest unsigned contract on the board and lands it 1 week per hop; his due tons are shown ahead.
4. Push: your soonest hauler arrives one week sooner, morale -1. Rest: morale +2. A won week is morale +1, a lost week morale -1. Morale 0 is mutiny: game over.
5. Two lost weeks in a row open Night Run: your heaviest hauler in transit lands now, morale -1.
6. Week 8: Carver adds a tug (base tons 0 to 3 every week) and the Spindle yard opens: Overhaul an idle hauler at the hub (1 week, morale -1) for +2 tons on all its later deliveries.
7. A Lissom & Vane container sits at a ring dock where it should not be. Docks you land at point the way. Once found: haul it to the Spindle for 6 tons (morale -2) or let the crew fence it (morale +3).
8. Win: more weeks won than lost after week 16. Week 16 is the Final and counts double.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

NODES = ["Spindle", "Ashgate", "Brinemouth", "Cinder Row", "Dovetail",
         "Eelmarket", "Fogline", "Gallows Bend", "Halfmoon"]
HAULERS = ["Marlowe", "Quill", "Sable"]
TURNS = 16
MID = 8
BOARD_SIZE = 2


def dist(a, b):
    if a == b:
        return 0
    if a == 0 or b == 0:
        return 1
    d = abs(a - b)
    return min(d, 8 - d)


def ring_dir(frm, to):
    """Shorter direction around the ring from frm to to: 'clockwise' or 'counter-clockwise'."""
    cw = (to - frm) % 8
    return "clockwise" if cw <= 4 else "counter-clockwise"


class G(Game):
    name = "Bad Quarter"
    turns = TURNS

    # ------------------------------------------------------------ setup
    def _new_contract(self, s, rng):
        week = s["_turn"]
        kind = rng.d(10)
        if kind <= 5:
            pick, drop = 0, rng.d(8)
        elif kind <= 8:
            pick, drop = rng.d(8), 0
        else:
            pick = rng.d(8)
            drop = pick
            while drop == pick:
                drop = rng.d(8)
        tons = rng.d(3) + (2 if week >= MID else 1)
        c = {"id": s["next_cid"], "pick": pick, "drop": drop, "tons": tons, "exp": rng.d(2) + 1}
        s["next_cid"] += 1
        return c

    def init_state(self, rng):
        s = {
            "wins": 0,
            "losses": 0,
            "morale": 7,
            "streak": 0,
            "landed": 0,
            "haulers": [{"name": n, "pos": 0, "eta": 0, "tons": 0, "drop": 0, "hold": 0, "job": ""} for n in HAULERS],
            "board": [],
            "next_cid": 1,
            "carver": {"base": 0, "pending": []},
            "crate": {"found": False, "done": False},
            "last_week": "",
            "hidden": {"crate_node": rng.d(8)},
        }
        s["_turn"] = 1
        for _ in range(BOARD_SIZE):
            s["board"].append(self._new_contract(s, rng))
        return s

    # ------------------------------------------------------------ helpers
    def _idle(self, s):
        return [i for i, h in enumerate(s["haulers"]) if h["eta"] == 0]

    def _transit(self, s):
        return [i for i, h in enumerate(s["haulers"]) if h["eta"] > 0 and h["tons"] > 0]

    def _closest_idle(self, s, node):
        idle = self._idle(s)
        if not idle:
            return None
        return min(idle, key=lambda i: (dist(s["haulers"][i]["pos"], node), i))

    def _carver_due(self, s, week):
        c = s["carver"]
        return c["base"] + sum(p["tons"] for p in c["pending"] if p["week"] == week)

    def _land(self, s, h, ev, how=""):
        t = h["tons"] + (h["hold"] if h["tons"] else 0)
        if h["tons"]:
            s["landed"] += t
            ev.append(f"{h['name']} lands {t} tons at {NODES[h['drop']]}{how}.")
        else:
            ev.append(f"{h['name']} is back from the yard, hold fitted (+2 tons per delivery).")
        h["pos"] = h["drop"]
        h["tons"] = 0
        h["eta"] = 0
        h["job"] = ""
        # the stray container: clues on landing at a ring dock
        cr = s["crate"]
        if h["pos"] != 0 and not cr["found"] and not cr["done"]:
            node = s["hidden"]["crate_node"]
            if h["pos"] == node:
                cr["found"] = True
                cr["node"] = node
                ev.append(f"At {NODES[node]} a sealed Lissom & Vane container sits on the dock. The manifest says it is in a vault on Earth. Found it.")
            else:
                ev.append(f"Dockhand at {NODES[h['pos']]}: the fund's container went {ring_dir(h['pos'], node)} from here.")

    # ------------------------------------------------------------ options
    def options(self, s):
        m = s["morale"]
        sends = []
        for c in s["board"]:
            hi = self._closest_idle(s, c["pick"])
            if hi is None:
                continue
            h = s["haulers"][hi]
            L = dist(h["pos"], c["pick"]) + dist(c["pick"], c["drop"])
            tons = c["tons"] + h["hold"]
            lw = s["_turn"] + L - 1
            sends.append({
                "id": f"send_{c['id']}",
                "label": f"Send {h['name']} ({NODES[h['pos']]}): {NODES[c['pick']]} to {NODES[c['drop']]}, {tons} tons, lands week {lw} ({L} weeks)",
                "args": {"hauler": hi, "rate": round(tons / L, 2), "eta": L, "tons": tons, "land_week": lw},
            })
        sends.sort(key=lambda o: -o["args"]["rate"])

        pri = [{"id": "rest", "label": "Rest the crews (morale +2)", "args": {}}]
        if sends:
            pri.append(sends[0])
        cr = s["crate"]
        if cr["found"] and not cr["done"]:
            hi = self._closest_idle(s, cr["node"])
            if hi is not None and m >= 3:
                h = s["haulers"][hi]
                L = dist(h["pos"], cr["node"]) + 1
                pri.append({"id": "haul_crate", "label": f"Send {h['name']} to haul the stray container from {NODES[cr['node']]} to the Spindle: 6 tons, {L} weeks, morale -2", "args": {"hauler": hi, "eta": L}})
            pri.append({"id": "fence_crate", "label": "Let the crew fence the container (morale +3, it is gone)", "args": {}})
        transit = self._transit(s)
        if transit and m >= 2:
            if s["streak"] >= 2:
                hi = max(transit, key=lambda i: (s["haulers"][i]["tons"] + s["haulers"][i]["hold"], -s["haulers"][i]["eta"]))
                h = s["haulers"][hi]
                pri.append({"id": "night_run", "label": f"Night Run: {h['name']} lands {h['tons'] + h['hold']} tons at {NODES[h['drop']]} this week, morale -1", "args": {"hauler": hi}})
        if len(sends) > 1:
            pri.append(sends[1])
        if transit and m >= 2:
            hi = min(transit, key=lambda i: (s["haulers"][i]["eta"], -s["haulers"][i]["tons"]))
            h = s["haulers"][hi]
            due_now = self._carver_due(s, s["_turn"])
            pri.append({"id": "push", "label": f"Push {h['name']} ({h['tons'] + h['hold']} tons to {NODES[h['drop']]}): {h['eta']} weeks becomes {h['eta'] - 1}, morale -1", "args": {"hauler": hi, "eta": h["eta"], "tons": h["tons"] + h["hold"], "due_now": due_now}})
        if s["_turn"] >= MID and m >= 2:
            cand = [i for i in self._idle(s) if s["haulers"][i]["pos"] == 0 and s["haulers"][i]["hold"] == 0]
            if cand:
                hi = cand[0]
                pri.append({"id": "overhaul", "label": f"Overhaul {s['haulers'][hi]['name']} at the Spindle yard (1 week, morale -1, +2 tons on all its later deliveries)", "args": {"hauler": hi}})
        pri = pri[:5]
        # present: sends, specials, rest last
        rest = pri[0]
        rest_of = pri[1:]
        order = {"send": 0, "haul": 1, "fence": 2, "night": 3, "push": 4, "over": 5}
        rest_of.sort(key=lambda o: order.get(o["id"].split("_")[0], 9))
        return rest_of + [rest]

    # ------------------------------------------------------------ apply
    def apply(self, s, a, args, rng):
        ev = []
        if a.startswith("send_"):
            cid = int(a.split("_")[1])
            c = next(x for x in s["board"] if x["id"] == cid)
            h = s["haulers"][args["hauler"]]
            L = dist(h["pos"], c["pick"]) + dist(c["pick"], c["drop"])
            h["eta"] = L
            h["tons"] = c["tons"]
            h["drop"] = c["drop"]
            h["job"] = f"{NODES[c['pick']]} to {NODES[c['drop']]}"
            s["board"] = [x for x in s["board"] if x["id"] != cid]
            ev.append(f"{h['name']} signs the {NODES[c['pick']]} to {NODES[c['drop']]} job: {c['tons'] + h['hold']} tons, due to land in {L} weeks.")
        elif a == "push":
            h = s["haulers"][args["hauler"]]
            h["eta"] -= 1
            s["morale"] -= 1
            ev.append(f"{h['name']} pushed: morale -1.")
            if h["eta"] <= 0:
                self._land(s, h, ev, " early")
            else:
                ev.append(f"{h['name']} now lands in {h['eta']} weeks.")
        elif a == "night_run":
            h = s["haulers"][args["hauler"]]
            s["morale"] -= 1
            ev.append(f"Night Run: morale -1.")
            self._land(s, h, ev, " under running lights")
        elif a == "rest":
            s["morale"] = min(10, s["morale"] + 2)
            ev.append(f"Crews rest. Morale +2 (now {s['morale']}).")
        elif a == "overhaul":
            h = s["haulers"][args["hauler"]]
            h["eta"] = 1
            h["tons"] = 0
            h["drop"] = 0
            h["hold"] = 2
            h["job"] = "in the yard"
            s["morale"] -= 1
            ev.append(f"{h['name']} goes into the Spindle yard for a bigger hold. Morale -1. Back next week.")
        elif a == "haul_crate":
            h = s["haulers"][args["hauler"]]
            cr = s["crate"]
            h["eta"] = dist(h["pos"], cr["node"]) + 1
            h["tons"] = 6
            h["drop"] = 0
            h["job"] = "stray container to Spindle"
            cr["done"] = True
            s["morale"] -= 2
            ev.append(f"{h['name']} signs for the fund's container: 6 tons to the Spindle, lands in {h['eta']} weeks. The crew goes quiet. Morale -2.")
        elif a == "fence_crate":
            s["crate"]["done"] = True
            s["morale"] = min(10, s["morale"] + 3)
            ev.append(f"The container leaves on the night shuttle in pieces. The crew is paid in cash. Morale +3 (now {s['morale']}).")
        return ev

    # ------------------------------------------------------------ advance
    def advance(self, s, rng):
        ev = []
        week = s["_turn"] - 1  # the week being resolved
        # transit: delay rolls, then movement
        rolls = []
        for h in s["haulers"]:
            if h["eta"] > 0:
                ok, txt = rng.check(2, label=f"{h['name']} transit")
                if not ok:
                    h["eta"] += 1
                    rolls.append(f"{txt}, slips a week")
                else:
                    rolls.append(txt)
        if rolls:
            ev.append("Transit: " + "; ".join(rolls) + ".")
        for h in s["haulers"]:
            if h["eta"] > 0:
                h["eta"] -= 1
                if h["eta"] == 0:
                    self._land(s, h, ev)
        # the week's ledger
        carver = self._carver_due(s, week)
        mine = s["landed"]
        final = week == TURNS
        won = mine > carver
        pts = 2 if final else 1
        if won:
            s["wins"] += pts
            s["streak"] = 0
            s["morale"] = min(10, s["morale"] + 1)
            verdict = "WIN (morale +1)"
        else:
            s["losses"] += pts
            s["streak"] += 1
            s["morale"] -= 1
            verdict = "LOSS (morale -1)"
        tag = " THE FINAL, counts double" if final else ""
        ev.append(f"Week {week} ledger: you {mine} tons, Carver {carver}. {verdict}.{tag} Record {s['wins']}-{s['losses']}.")
        s["last_week"] = f"W{week}: you {mine} vs Carver {carver} {verdict}"
        s["landed"] = 0
        s["carver"]["pending"] = [p for p in s["carver"]["pending"] if p["week"] > week]
        if s["morale"] <= 0:
            return ev
        # board ages
        kept = []
        for c in s["board"]:
            c["exp"] -= 1
            if c["exp"] <= 0:
                ev.append(f"The {NODES[c['pick']]} to {NODES[c['drop']]} job went stale and came off the board.")
            else:
                kept.append(c)
        s["board"] = kept
        # midpoint
        if s["_turn"] == MID:
            s["carver"]["base"] = 3
            ev.append("Week 8: Carver's new tug is working the ring; his base is now 3 tons a week. The Spindle yard is open for overhauls.")
        # Carver signs
        if s["board"] and s["_turn"] % 2 == 1:
            c = max(s["board"], key=lambda x: (x["tons"], -x["id"]))
            s["board"] = [x for x in s["board"] if x["id"] != c["id"]]
            land = s["_turn"] - 1 + dist(c["pick"], c["drop"])
            s["carver"]["pending"].append({"week": land, "tons": c["tons"], "label": f"{NODES[c['pick']]} to {NODES[c['drop']]}"})
            ev.append(f"Carver's man signed the {NODES[c['pick']]} to {NODES[c['drop']]} job: {c['tons']} tons, his tug lands it week {land}.")
        # refill
        while len(s["board"]) < BOARD_SIZE:
            c = self._new_contract(s, rng)
            s["board"].append(c)
            ev.append(f"New on the board: {NODES[c['pick']]} to {NODES[c['drop']]}, {c['tons']} tons, expires in {c['exp']} weeks.")
        if s["_turn"] <= TURNS:
            ev.append(f"Carver due week {s['_turn']}: {self._carver_due(s, s['_turn'])} tons.")
        return ev

    # ------------------------------------------------------------ status
    def status_line(self, s):
        hs = []
        for h in s["haulers"]:
            if h["eta"] == 0:
                hs.append(f"{h['name']}@{NODES[h['pos']]}{'+' if h['hold'] else ''}")
            elif h["tons"] == 0:
                hs.append(f"{h['name']} yard {h['eta']}w")
            else:
                hs.append(f"{h['name']}>{NODES[h['drop']]} {h['tons'] + h['hold']}t {h['eta']}w")
        due = self._carver_due(s, s["_turn"]) if s["_turn"] <= TURNS else 0
        return f"Record {s['wins']}-{s['losses']} | Morale {s['morale']} | {', '.join(hs)} | Carver due {due}"

    def check_end(self, s):
        if s["morale"] <= 0:
            return {"result": "loss", "reason": f"mutiny: morale hit 0 with record {s['wins']}-{s['losses']}"}
        if s["_turn"] > TURNS:
            if s["wins"] > s["losses"]:
                return {"result": "win", "reason": f"season {s['wins']}-{s['losses']}"}
            return {"result": "loss", "reason": f"season {s['wins']}-{s['losses']}, needed a winning record"}
        return None

    # ------------------------------------------------------------ heuristic
    def heuristic(self, s, options, rng):
        ids = {o["id"]: o for o in options}
        m = s["morale"]
        if m <= 2 and "rest" in ids:
            return "rest"
        if "night_run" in ids and m >= 3:
            return "night_run"
        if "fence_crate" in ids and m <= 5:
            return "fence_crate"
        if "haul_crate" in ids and m >= 5:
            return "haul_crate"
        if "overhaul" in ids and m >= 5 and s["_turn"] <= 12:
            return "overhaul"
        sends = [o for o in options if o["id"].startswith("send_")]
        if sends:
            def value(o):
                a = o["args"]
                lw = a["land_week"]
                if lw > TURNS:
                    return -1
                mine = s["landed"] if lw == s["_turn"] else 0
                mine += sum(h["tons"] + h["hold"] for h in s["haulers"] if h["tons"] and s["_turn"] + h["eta"] - 1 == lw)
                due = self._carver_due(s, lw)
                v = a["rate"]
                if mine > due:
                    v *= 0.4
                elif mine + a["tons"] <= due:
                    v *= 0.3
                return v
            best = max(sends, key=value)
            if value(best) > 0:
                return best
        if "push" in ids and m >= 5:
            a = ids["push"]["args"]
            if a["tons"] + s["landed"] > a["due_now"] and s["landed"] <= a["due_now"]:
                return "push"
        return "rest"


if __name__ == "__main__":
    run(G)
