"""Trophy Route: a /play engine.

Rolls: FORM=19 dungeon keeper (you are the defense; waves come through), SET=55 city bus network,
ROLE=26 mayor with a hostile council, LOOP=32 open/hold/close one position as news lands,
CLOCK=14 crew morale (strike at zero), TWIST=38 you only ever see averages, WIN=7 deliver a cargo
intact, MAP=9 a line of 6 nodes that shifts each turn, TONE=9 workplace comedy.

Rulesheet (8 lines):
1. The Centennial Trophy (a two-ton glass bus) rides the No. 6 from the Depot through 5 stops to City Hall. Roadworks swap two stops ahead about every other turn; the order is always shown.
2. Each turn do one thing: advance one stop, post a bus (10 cash) or inspectors (8 cash) at any stop ahead, pull guards off a passed stop (+6 cash, morale -1), or hold (+8 cash, morale +2).
3. Every stop has a hidden crush crowd (up to 7) and a hidden rowdy crowd (up to 8). A bus absorbs 4 crush, inspectors absorb 4 rowdy. Two postings per stop at most.
4. On arrival the drivers roll d6 + 2 against the uncovered crowd. Short by N: trophy -5 x N, morale -1. Held: cash +8, morale +1.
5. Dispatch only ever reports averages: crush and rowdy averaged over all stops ahead, and over the next two. Some days the school run pays a 5 cash windfall.
6. Councillor Hatch rallies every turn at the stop ahead with the fewest guards (nearest on ties): rowdy +1 there. From turn 8 her rallies add 2, she heckles the drivers when she is at the next stop (morale -1), and austerity docks 3 cash a turn (morale -1 instead when the kitty is under 3).
7. Morale 0 is a strike and trophy 0 is shards: both lose. Each overload unlocks one Ride Along (morale +2, next roll +3).
8. From turn 8 you may run Express: two stops in one turn, morale -2. City Hall takes delivery from turn 12. Win: trophy 70+ delivered by turn 16.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, run  # noqa: E402

STOPS = ["Market", "Stadium", "University", "Hospital"]
DEPOT = "Depot"
HALL = "City Hall"
COST = {"bus": 10, "insp": 8}
REFUND = 6
CAP = {"crush": 7, "rowdy": 8}
ABSORB = 4
MAX_POST = 2
WIN_TROPHY = 70
HALL_OPENS = 12
DMG = 5


class G(Game):
    name = "Trophy Route"
    turns = 16

    # ------------------------------------------------------------ helpers
    def _ahead(self, s):
        return s["line"][s["pos"] + 1:]

    def _next(self, s):
        a = self._ahead(s)
        return a[0] if a else None

    def _passed(self, s):
        return s["line"][1:s["pos"] + 1]

    def _guards(self, s, stop):
        return s["guards"].get(stop, [])

    def _avg(self, s, stops, key):
        if not stops:
            return 0.0
        return round(sum(s["hidden"]["heat"][x][key] for x in stops) / len(stops), 1)

    def _report(self, s):
        a = self._ahead(s)
        n2 = a[:2]
        return (f"Dispatch averages: ahead crush {self._avg(s, a, 'crush')} / rowdy {self._avg(s, a, 'rowdy')}; "
                f"next two crush {self._avg(s, n2, 'crush')} / rowdy {self._avg(s, n2, 'rowdy')}.")

    def _mark(self, s, stop):
        g = self._guards(s, stop)
        tag = "".join("B" if x == "bus" else "I" for x in g)
        return f"{stop}[{tag}]" if tag else stop

    # ------------------------------------------------------------ contract
    def init_state(self, rng):
        mid = rng.shuffle(list(STOPS))
        line = [DEPOT] + mid + [HALL]
        heat = {
            "Market": {"crush": 3 + rng.d(4), "rowdy": rng.d(2) - 1},
            "Hospital": {"crush": 2 + rng.d(4), "rowdy": rng.d(2) - 1},
            "Stadium": {"crush": rng.d(3), "rowdy": 2 + rng.d(4)},
            "University": {"crush": rng.d(3), "rowdy": 1 + rng.d(4)},
            HALL: {"crush": 4 + rng.d(3), "rowdy": 1 + rng.d(3)},
        }
        s = {
            "cash": 20,
            "morale": 6,
            "trophy": 100,
            "pos": 0,
            "line": line,
            "guards": {},
            "streak": 0,
            "ride": False,
            "hatch_at": None,
            "report": "",
            "hidden": {"heat": heat},
        }
        s["report"] = self._report(s)
        return s

    def options(self, s):
        o = []
        nxt = self._next(s)
        if not (nxt == HALL and s["_turn"] < HALL_OPENS):
            o.append({"id": "advance", "label": f"Advance to {nxt}"})
        ahead_open = [x for x in self._ahead(s) if len(self._guards(s, x)) < MAX_POST]
        if ahead_open:
            tgt = nxt if nxt in ahead_open else ahead_open[0]
            if s["cash"] >= COST["bus"]:
                o.append({"id": "post_bus", "label": f"Post a bus at {tgt} (-10 cash, absorbs 4 crush); or name another stop ahead", "args": {"stop": tgt}})
            if s["cash"] >= COST["insp"]:
                o.append({"id": "post_insp", "label": f"Post inspectors at {tgt} (-8 cash, absorbs 4 rowdy); or name another stop ahead", "args": {"stop": tgt}})
        pulled = [x for x in self._passed(s) if self._guards(s, x)]
        if pulled and s["morale"] >= 2:
            o.append({"id": "pull", "label": f"Pull guards off {pulled[-1]} (+6 cash, morale -1)", "args": {"stop": pulled[-1]}})
        o.append({"id": "hold", "label": "Hold: run normal service (+8 cash, morale +2)"})
        if s["_turn"] >= 8 and len(self._ahead(s)) >= 2 and s["morale"] >= 3 and not (self._ahead(s)[1] == HALL and s["_turn"] < HALL_OPENS):
            a = self._ahead(s)
            o.append({"id": "express", "label": f"Express run through {a[0]} to {a[1]} (morale -2)"})
        if s["streak"] >= 1 and not s["ride"] and s["morale"] <= 8:
            o.append({"id": "ride", "label": "Ride along with the drivers (morale +2, next roll +3)"})
        return o

    def _arrive(self, s, rng):
        ev = []
        s["pos"] += 1
        stop = s["line"][s["pos"]]
        h = s["hidden"]["heat"][stop]
        g = self._guards(s, stop)
        buses = g.count("bus")
        insps = g.count("insp")
        unc_c = max(0, h["crush"] - ABSORB * buses)
        unc_r = max(0, h["rowdy"] - ABSORB * insps)
        uncovered = unc_c + unc_r
        bonus = 2 + (3 if s["ride"] else 0)
        s["ride"] = False
        d = rng.d(6)
        total = d + bonus
        ev.append(f"Arrived at {stop}: crush {h['crush']} / rowdy {h['rowdy']}, guards cover {min(h['crush'], ABSORB * buses)} crush and {min(h['rowdy'], ABSORB * insps)} rowdy, uncovered {uncovered}.")
        if total >= uncovered:
            s["cash"] += 8
            s["morale"] = min(10, s["morale"] + 1)
            ev.append(f"roll {d} (+{bonus} = {total}, need {uncovered}+) success. Crowd held. Cash +8, morale +1.")
        else:
            short = uncovered - total
            s["trophy"] -= DMG * short
            s["morale"] -= 1
            s["streak"] += 1
            ev.append(f"roll {d} (+{bonus} = {total}, need {uncovered}+) fail. Short by {short}: trophy -{DMG * short}, morale -1.")
        return ev

    def apply(self, s, a, args, rng):
        ev = []
        if a == "advance":
            ev += self._arrive(s, rng)
        elif a in ("post_bus", "post_insp"):
            kind = "bus" if a == "post_bus" else "insp"
            stop = args.get("stop")
            if stop not in self._ahead(s) or len(self._guards(s, stop)) >= MAX_POST:
                stop = self._next(s)
            s["cash"] -= COST[kind]
            s["guards"].setdefault(stop, []).append(kind)
            what = "An extra bus" if kind == "bus" else "A team of inspectors"
            ev.append(f"{what} posted at {stop}. Cash -{COST[kind]}.")
        elif a == "pull":
            stop = args.get("stop")
            if stop not in self._passed(s) or not self._guards(s, stop):
                stop = [x for x in self._passed(s) if self._guards(s, x)][-1]
            s["guards"][stop] = s["guards"][stop][:-1]
            if not s["guards"][stop]:
                del s["guards"][stop]
            s["cash"] += REFUND
            s["morale"] -= 1
            ev.append(f"Guards pulled off {stop}. Cash +{REFUND}, morale -1.")
        elif a == "hold":
            s["cash"] += 8
            s["morale"] = min(10, s["morale"] + 2)
            ev.append("Normal service. Cash +8, morale +2.")
        elif a == "express":
            s["morale"] -= 2
            ev.append("Express run: morale -2.")
            ev += self._arrive(s, rng)
            if s["trophy"] > 0 and s["morale"] > 0 and s["pos"] < len(s["line"]) - 1:
                ev += self._arrive(s, rng)
        elif a == "ride":
            s["ride"] = True
            s["morale"] = min(10, s["morale"] + 2)
            s["streak"] = 0
            ev.append("You ride along. Morale +2, next arrival roll +3.")
        return ev

    def advance(self, s, rng):
        ev = []
        t = s["_turn"]
        if t == 8:
            ev.append("Turn 8: the council passes austerity. Cash -3 a turn from now; Hatch's rallies now add 2 rowdy. The union offers Express runs.")
        if t >= 8:
            if s["cash"] >= 3:
                s["cash"] -= 3
                ev.append("Austerity: cash -3.")
            else:
                s["morale"] -= 1
                ev.append("Austerity: the kitty is under 3, so the drivers chip in. Morale -1.")
        # roadworks: swap two adjacent stops among the middle stops still ahead
        mid_idx = [i for i in range(s["pos"] + 1, len(s["line"]) - 1)]
        if len(mid_idx) >= 2 and rng.chance(0.5):
            i = rng.choice(mid_idx[:-1])
            a, b = s["line"][i], s["line"][i + 1]
            s["line"][i], s["line"][i + 1] = b, a
            ev.append(f"Roadworks: {a} and {b} swap places on the line.")
        # Hatch's rally
        ahead = self._ahead(s)
        if ahead:
            fewest = min(len(self._guards(s, x)) for x in ahead)
            target = [x for x in ahead if len(self._guards(s, x)) == fewest][0]
            bump = 2 if t >= 8 else 1
            s["hidden"]["heat"][target]["rowdy"] = min(CAP["rowdy"], s["hidden"]["heat"][target]["rowdy"] + bump)
            s["hatch_at"] = target
            if target == ahead[0] and t >= 8:
                s["morale"] -= 1
                ev.append(f"Councillor Hatch rallies at {target}, the next stop, and heckles the drivers. Morale -1.")
            else:
                ev.append(f"Councillor Hatch was seen with her megaphone at {target}.")
        if rng.chance(0.2):
            s["cash"] += 5
            ev.append("A fare windfall from the school run. Cash +5.")
        s["report"] = self._report(s)
        ev.append(s["report"])
        return ev

    def status_line(self, s):
        parts = []
        for i, stop in enumerate(s["line"]):
            m = self._mark(s, stop)
            if i == s["pos"]:
                m = f"<{m}>"
            parts.append(m)
        return f"Cash {s['cash']} | Morale {s['morale']} | Trophy {s['trophy']} | {' > '.join(parts)}"

    def check_end(self, s):
        if s["trophy"] <= 0:
            return {"result": "loss", "reason": "the trophy is shards"}
        if s["morale"] <= 0:
            return {"result": "loss", "reason": "drivers strike"}
        if s["pos"] == len(s["line"]) - 1:
            if s["trophy"] >= WIN_TROPHY:
                return {"result": "win", "reason": f"trophy delivered at {s['trophy']}"}
            return {"result": "loss", "reason": f"trophy delivered at {s['trophy']}, needed {WIN_TROPHY}"}
        if s["_turn"] > self.turns:
            return {"result": "loss", "reason": "out of turns: the unveiling went ahead without the trophy"}
        return None

    def heuristic(self, s, options, rng):
        ids = {o["id"] for o in options}
        nxt = self._next(s)
        g = self._guards(s, nxt)
        a = self._ahead(s)
        n2 = a[:2]
        c_est = self._avg(s, n2, "crush")
        r_est = self._avg(s, n2, "rowdy") + (1 if s["hatch_at"] == nxt else 0)
        unc_c = max(0.0, c_est - ABSORB * g.count("bus"))
        unc_r = max(0.0, r_est - ABSORB * g.count("insp"))
        est = unc_c + unc_r
        if "ride" in ids:
            return "ride"
        if s["morale"] <= 2 and "hold" in ids:
            return "hold"
        turns_left = self.turns - s["_turn"] + 1
        rushed = len(a) >= turns_left
        need_more = (len(g) == 0) or (est > 3 and len(g) < MAX_POST)
        if need_more and not rushed:
            want = "post_bus" if unc_c >= unc_r else "post_insp"
            if want in ids:
                return {"id": want, "args": {"stop": nxt}}
            if "pull" in ids and s["morale"] >= 8:
                return "pull"
            if "hold" in ids:
                return "hold"
        if "express" in ids and len(a) > turns_left - 1:
            return "express"
        if "advance" in ids:
            return "advance"
        if "hold" in ids:
            return "hold"
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
