"""Greywater Wing: a mercenary helicopter wing over a city that rearranges itself.

Rolls: FORM=16 market (hold positions with news and drift), SET=14 helicopter wing over a
sprawling city, ROLE=12 mercenary captain, LOOP=15 bid against rivals for scarce lots,
CLOCK=20 ratings drop each week you fail to deliver, TWIST=5 you can only carry three things,
WIN=16 finish the season above .500 or win the final, MAP=9 a line of 6 nodes that shifts each
turn, TONE=7 weird and uncanny.

Rulesheet (8 lines):
1. Each week do one thing: fly a job, buy a lot, or refit. Weeks 1-3 are preseason; from week 4 a week with no delivery is an L on the Board.
2. Fly: d6 against the need shown. Matching gear -3, each refit (20 cash, max 2) -1, +1 per 2 districts from the Yards. Hit: W and the pay. Miss: L, and on a roll of 1 the city keeps the gear you used.
3. Gear: 3 slots, never more, 1 cash a week each. Lots sell at market value, which moves with the news.
4. Two lots a week. The Hollow Wing circles one and bids high: outbidding it costs listed +6 and still loses on a tie (1 in 6). The other lot is yours at listed.
5. Each night two neighboring districts swap places. Jobs stay in their districts, so distances change. Jobs last two weeks.
6. Week 9 on, the Low Fog: jobs need +1 and pay +5. With 3 gear you may fly both jobs in one week for 6 cash.
7. After two missed sorties in a row: Press the Tower, 8 cash for need -2 on this week's sortie.
8. Week 16 is the Long Night, a job that wants two gear types. Win: record above .500 after week 16, or hit the Long Night. Lose: cash below 0.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

TYPES = ["fire", "riot", "medevac", "cargo"]
GEAR = {"fire": "Bambi bucket", "riot": "Gun pod", "medevac": "Litter rig", "cargo": "Sling"}
JOBNAME = {"fire": "cold fire", "riot": "marching crowd", "medevac": "unnamed patient", "cargo": "humming crate"}
DISTRICTS = ["Ashfall", "Spire", "Yards", "Canal Row", "Hollowmere", "Ninth Market"]
HANGAR = "Yards"
TURNS = 16
FOG_WEEK = 9
PRESEASON = 3
START_CASH = 30
UPKEEP = 1
REFIT_COST = 20
TOWER_COST = 8
DOUBLE_COST = 6
OUTBID = 6
FINALE_PAY = 50


class G(Game):
    name = "Greywater Wing"
    turns = TURNS

    # ------------------------------------------------------------ helpers
    def _dist(self, s, district):
        return abs(s["line"].index(district) - s["line"].index(HANGAR))

    def _need(self, s, job, mod=0):
        n = 5 + (1 if s["_turn"] >= FOG_WEEK else 0)
        if job["type"] in s["gear"]:
            n -= 3
        n -= s["refits"]
        n += self._dist(s, job["district"]) // 2
        n += mod
        return max(2, min(6, n))

    def _finale_need(self, s, mod=0):
        f = s["finale"]
        n = 8
        for t in f["types"]:
            if t in s["gear"]:
                n -= 1
        n -= s["refits"]
        n += mod
        return max(2, min(6, n))

    def _news(self, s, rng):
        d = rng.choice(s["line"])
        t = rng.choice(TYPES)
        s["hot"] = {"district": d, "type": t}
        for k in TYPES:
            if k == t:
                s["market"][k] = min(20, s["market"][k] + 3)
            else:
                s["market"][k] = rng.drift(s["market"][k], 8, 20)

    def _new_job(self, s, rng, hot=False):
        if hot:
            t, d = s["hot"]["type"], s["hot"]["district"]
            pay = 10 + rng.d(6) + 6
        else:
            t, d = rng.choice(TYPES), rng.choice(s["line"])
            pay = 10 + rng.d(6)
        if s["_turn"] >= FOG_WEEK:
            pay += 5
        return {"type": t, "district": d, "pay": pay, "life": 2}

    def _fill_jobs(self, s, rng, hot_first=True):
        if hot_first and len(s["jobs"]) < 2:
            s["jobs"].append(self._new_job(s, rng, hot=True))
        while len(s["jobs"]) < 2:
            s["jobs"].append(self._new_job(s, rng))

    def _new_lots(self, s, rng):
        types = list(TYPES)
        rng.shuffle(types)
        picked = types[:2]
        s["lots"] = [{"type": t, "listed": s["market"][t]} for t in picked]
        hot = s["hot"]["type"]
        if hot in picked:
            s["circled"] = picked.index(hot)
        elif s["lots"][0]["listed"] != s["lots"][1]["listed"]:
            s["circled"] = 0 if s["lots"][0]["listed"] > s["lots"][1]["listed"] else 1
        else:
            s["circled"] = rng.choice([0, 1])

    def _job_text(self, job):
        return f"{JOBNAME[job['type']]} in {job['district']}"

    def _sortie(self, s, job, rng, mod, ev):
        n = self._need(s, job, mod)
        v = rng.d(6)
        ok = v >= n
        txt = f"roll {v} (need {n}+) {'success' if ok else 'fail'}"
        if ok:
            s["wins"] += 1
            s["cash"] += job["pay"]
            s["streak"] = 0
            ev.append(f"{self._job_text(job).capitalize()}: {txt}. W on the Board, paid {job['pay']}.")
        else:
            s["losses"] += 1
            s["streak"] += 1
            ev.append(f"{self._job_text(job).capitalize()}: {txt}. L on the Board.")
            if v == 1 and job["type"] in s["gear"]:
                s["gear"].remove(job["type"])
                ev.append(f"The city kept the {GEAR[job['type']]}. Slot empty.")
        s["jobs"].remove(job)
        return ok

    # ------------------------------------------------------------ contract
    def init_state(self, rng):
        s = {
            "cash": START_CASH,
            "wins": 0,
            "losses": 0,
            "gear": [rng.choice(TYPES)],
            "refits": 0,
            "market": {t: 12 for t in TYPES},
            "line": list(DISTRICTS),
            "hot": None,
            "jobs": [],
            "lots": [],
            "circled": 0,
            "streak": 0,
            "finale": None,
            "finale_won": False,
            "_turn": 1,
            "hidden": {},
        }
        rng.shuffle(s["line"])
        self._news(s, rng)
        self._fill_jobs(s, rng)
        self._new_lots(s, rng)
        return s

    def options(self, s):
        o = []
        for i, job in enumerate(s["jobs"]):
            n = self._need(s, job)
            d = self._dist(s, job["district"])
            o.append({"id": f"fly:{i}", "label": f"Fly the {self._job_text(job)} (need {n}+, pay {job['pay']}, {d} away, {job['life']} wk left)"})
        if s["finale"] and s["_turn"] == TURNS:
            n = self._finale_need(s)
            names = " and ".join(GEAR[t] for t in s["finale"]["types"])
            o.append({"id": "finale", "label": f"Fly the Long Night (need {n}+, wants {names}, pay {FINALE_PAY}, hit it and the season is yours)"})
        reserve = 3 * UPKEEP * (len(s["gear"]) + 1)
        if len(s["gear"]) < 3:
            for i, lot in enumerate(s["lots"]):
                if lot["type"] in s["gear"]:
                    continue
                if i == s["circled"]:
                    price = lot["listed"] + OUTBID
                    if s["cash"] >= price + reserve:
                        o.append({"id": f"lot:{i}", "label": f"Outbid the Hollow Wing for the {GEAR[lot['type']]} ({price} cash, 5 in 6)"})
                else:
                    if s["cash"] >= lot["listed"] + reserve:
                        o.append({"id": f"lot:{i}", "label": f"Buy the {GEAR[lot['type']]} ({lot['listed']} cash, uncontested)"})
        if s["refits"] < 2 and s["cash"] >= REFIT_COST + reserve:
            o.append({"id": "refit", "label": f"Refit the airframe ({REFIT_COST} cash, -1 need on every sortie, {s['refits']}/2 done)"})
        if s["streak"] >= 2 and s["cash"] >= TOWER_COST + reserve and s["jobs"]:
            best = min(s["jobs"], key=lambda j: self._need(s, j))
            o.append({"id": "tower", "label": f"Press the Tower ({TOWER_COST} cash) and fly the {self._job_text(best)} at need {self._need(s, best, -2)}+"})
        if s["_turn"] >= FOG_WEEK and len(s["gear"]) == 3 and len(s["jobs"]) == 2 and s["cash"] >= DOUBLE_COST + reserve:
            o.append({"id": "double", "label": f"Double sortie: fly both jobs this week ({DOUBLE_COST} cash)"})
        return o

    def apply(self, s, a, args, rng):
        ev = []
        attempted = False
        if a.startswith("fly:"):
            job = s["jobs"][int(a.split(":")[1])]
            self._sortie(s, job, rng, 0, ev)
            attempted = True
        elif a == "finale":
            n = self._finale_need(s)
            v = rng.d(6)
            ok = v >= n
            txt = f"roll {v} (need {n}+) {'success' if ok else 'fail'}"
            if ok:
                s["wins"] += 1
                s["cash"] += FINALE_PAY
                s["finale_won"] = True
                ev.append(f"The Long Night: {txt}. W on the Board, paid {FINALE_PAY}.")
            else:
                s["losses"] += 1
                ev.append(f"The Long Night: {txt}. L on the Board.")
            attempted = True
        elif a.startswith("lot:"):
            i = int(a.split(":")[1])
            lot = s["lots"][i]
            if i == s["circled"]:
                bid = lot["listed"] + OUTBID
                rival = lot["listed"] - 3 + rng.d(6) + 4
                if bid > rival:
                    s["cash"] -= bid
                    s["gear"].append(lot["type"])
                    ev.append(f"Hollow Wing bid {rival}. Your {bid} takes the {GEAR[lot['type']]}. Cash -{bid}.")
                else:
                    ev.append(f"Hollow Wing bid {rival}. Your {bid} ties and the tie goes to them. No gear, no cash spent.")
            else:
                s["cash"] -= lot["listed"]
                s["gear"].append(lot["type"])
                ev.append(f"Bought the {GEAR[lot['type']]} for {lot['listed']}. Cash -{lot['listed']}.")
        elif a == "refit":
            s["cash"] -= REFIT_COST
            s["refits"] += 1
            ev.append(f"Refit done. Cash -{REFIT_COST}. Every sortie now needs 1 less (refits {s['refits']}/2).")
        elif a == "tower":
            s["cash"] -= TOWER_COST
            best = min(s["jobs"], key=lambda j: self._need(s, j))
            ev.append(f"The Tower clears the sky for you. Cash -{TOWER_COST}.")
            self._sortie(s, best, rng, -2, ev)
            attempted = True
        elif a == "double":
            s["cash"] -= DOUBLE_COST
            ev.append(f"Both airframes up. Cash -{DOUBLE_COST}.")
            for job in list(s["jobs"]):
                self._sortie(s, job, rng, 0, ev)
            attempted = True
        if not attempted:
            if s["_turn"] > PRESEASON:
                s["losses"] += 1
                ev.append("No delivery this week. The Board marks an L.")
            else:
                ev.append("No delivery this week. Preseason, the Board stays quiet.")
        return ev

    def advance(self, s, rng):
        ev = []
        if s["_turn"] > TURNS:
            return ev
        if s["gear"]:
            up = UPKEEP * len(s["gear"])
            s["cash"] -= up
            ev.append(f"Crew pay {up}.")
            if s["cash"] < 0:
                return ev
        i = rng.d(5) - 1
        a, b = s["line"][i], s["line"][i + 1]
        s["line"][i], s["line"][i + 1] = b, a
        ev.append(f"Overnight, {a} and {b} traded places. The line is now {' - '.join(s['line'])}.")
        for job in s["jobs"]:
            job["life"] -= 1
        gone = [j for j in s["jobs"] if j["life"] <= 0]
        for j in gone:
            s["jobs"].remove(j)
            ev.append(f"The city forgot the {self._job_text(j)}.")
        self._news(s, rng)
        ev.append(f"News: {JOBNAME[s['hot']['type']]} in {s['hot']['district']}. {GEAR[s['hot']['type']]} market {s['market'][s['hot']['type']]}.")
        if s["_turn"] == PRESEASON + 1:
            ev.append("Preseason is over. From now on a week without a delivery is an L.")
        if s["_turn"] == FOG_WEEK:
            ev.append("The Low Fog has come in. Jobs need +1 and pay +5 from now on. Three gear unlocks the double sortie.")
        self._fill_jobs(s, rng)
        self._new_lots(s, rng)
        c = s["lots"][s["circled"]]
        other = s["lots"][1 - s["circled"]]
        ev.append(f"The Hollow Wing circles the {GEAR[c['type']]} lot (listed {c['listed']}). Other lot: {GEAR[other['type']]} at {other['listed']}.")
        if s["_turn"] == 12:
            t = list(TYPES)
            rng.shuffle(t)
            s["finale"] = {"types": t[:2]}
            ev.append(f"The Board posts the Long Night for week 16. It wants the {GEAR[t[0]]} and the {GEAR[t[1]]}.")
        if s["_turn"] == TURNS:
            ev.append("Week 16. The Long Night is on the Board.")
        return ev

    def status_line(self, s):
        slots = [GEAR[t] for t in s["gear"]] + ["-"] * (3 - len(s["gear"]))
        return f"Cash {s['cash']} | Record {s['wins']}-{s['losses']} | Gear {' / '.join(slots)} | Refits {s['refits']}"

    def check_end(self, s):
        if s["cash"] < 0:
            return {"result": "loss", "reason": f"grounded: cash {s['cash']}"}
        if s["finale_won"]:
            return {"result": "win", "reason": f"hit the Long Night, record {s['wins']}-{s['losses']}"}
        if s["_turn"] > TURNS:
            if s["wins"] > s["losses"]:
                return {"result": "win", "reason": f"season {s['wins']}-{s['losses']}, above .500"}
            return {"result": "loss", "reason": f"season {s['wins']}-{s['losses']}, not above .500"}
        return None

    # ------------------------------------------------------------ selftest policy
    def _p(self, n):
        return (7 - n) / 6

    def heuristic(self, s, options, rng):
        ids = {o["id"] for o in options}
        upkeep = UPKEEP * len(s["gear"])
        flies = [(self._p(self._need(s, j)), i) for i, j in enumerate(s["jobs"])]
        best_p, best_i = max(flies) if flies else (0, None)
        if "finale" in ids:
            fp = self._p(self._finale_need(s))
            if s["wins"] <= s["losses"] or fp >= best_p:
                return "finale"
        if "double" in ids and all(p >= 0.5 for p, _ in flies) and s["cash"] >= DOUBLE_COST + upkeep:
            return "double"
        if "tower" in ids and s["cash"] >= TOWER_COST + upkeep:
            best = min(s["jobs"], key=lambda j: self._need(s, j))
            if self._p(self._need(s, best, -2)) >= best_p + 0.3:
                return "tower"
        if best_p >= 0.67:
            return f"fly:{best_i}"
        lots = [o["id"] for o in options if o["id"].startswith("lot:")]
        if lots and s["_turn"] <= 12:
            unc = [l for l in lots if int(l.split(":")[1]) != s["circled"]]
            pick = unc[0] if unc else lots[0]
            price = s["lots"][int(pick.split(":")[1])]["listed"] + (0 if unc else OUTBID)
            if s["cash"] >= price + upkeep + 2:
                return pick
        if "refit" in ids and s["cash"] >= REFIT_COST + upkeep + 6 and s["_turn"] <= 13:
            return "refit"
        if best_i is not None:
            return f"fly:{best_i}"
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
