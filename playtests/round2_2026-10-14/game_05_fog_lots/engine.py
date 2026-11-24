"""Fog Lots: sealed-bid airport lots on a foggy island, for /play hybrid mode.

Rolls: FORM=4 blind auction, SET=38 airport control tower, ROLE=26 mayor with a hostile council,
LOOP=36 plant or tend one plot and the rest grows on its own, CLOCK=1 fuel runs out,
TWIST=27 one resource is sentient and resists being used (Bess, the runway), WIN=17 balance the
budget with the reviewer satisfied, MAP=8 single location with 6 districts, TONE=8 cozy with teeth.

Rulesheet (8 lines):
1. Each week one lot goes to sealed bid against Councillor Vane: bid 8, 14 or 22 cash, or pass and tend instead. Higher bid wins and pays; ties go to Vane. A losing bid costs nothing.
2. Lots are tankers (+8 fuel) or leases on one of the airport's 6 districts. A leased district flies 1 flight a week, 2 once it matures after 3 weeks (or tend it to mature now).
3. Each flight burns 1 fuel and pays 8 cash; the runway lights burn 1 fuel a week regardless and the tower keeps 5 fuel back for them; fog weeks (rolled, shown) ground all flights. Fuel 0: the airport goes dark, you lose.
4. Bess the runway is alive and resents work: she takes at most 5 flights a week, and on 4 or more she heaves on a roll of 1-2 (closed next week, -10 cash). Tend her (10 cash) and she tolerates anything for 3 weeks.
5. Council levy 4 cash a week. Cash below 0 is impeachment: you lose.
6. Vane's clerk talks: each week you hear whether her next bid will be HIGH (11-21) or LOW (6-11). The clerk is right 5 weeks in 6.
7. Lose two auctions in a row and the fishing co-op sells you an emergency drum: 3 fuel for 12 cash.
8. Week 8: tankers shrink to 5 fuel, Vane's high bids reach 24, and the Mail Contract lot appears once (+1 flight a week paying 12). Week 16 the auditor comes: win with cash 90+ and 4+ districts leased.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, run  # noqa: E402

DISTRICTS = ["Terminal", "Apron", "Hangar", "Fuel Farm", "Cargo Shed", "Tower Cafe"]
BIDS = {"bid_low": 8, "bid_mid": 14, "bid_high": 22}
MIDPOINT = 8
WIN_CASH = 90
WIN_DEV = 4
FUEL_START = 15
TANKER_EARLY = 8
TANKER_LATE = 5
RESERVE = 5  # fuel the tower keeps back for the lights
LEVY = 4


class G(Game):
    name = "Fog Lots"
    turns = 16

    # ------------------------------------------------------------ setup
    def init_state(self, rng):
        leases = DISTRICTS[1:]
        rng.shuffle(leases)
        early = [["tanker", None]] * 4 + [["lease", d] for d in leases[:3]]
        rng.shuffle(early)
        late = [["tanker", None]] * 5 + [["lease", d] for d in leases[3:]]
        rng.shuffle(late)
        deck = early + [["mail", None]] + late + [["tanker", None]]  # 16 lots for weeks 1..16
        s = {
            "cash": 60,
            "fuel": FUEL_START,
            "dev": {"Terminal": {"level": 1, "age": 0}},
            "mail": False,
            "calm": 0,
            "closed": False,
            "streak": 0,
            "lot": None,
            "tell": None,
            "fog": False,
            "_turn": 1,
            "hidden": {"deck": deck, "vane_high": False},
        }
        self._draw_lot(s, rng)
        return s

    # ------------------------------------------------------------ helpers
    def _draw_lot(self, s, rng):
        idx = s["_turn"] - 1
        deck = s["hidden"]["deck"]
        kind, district = deck[idx] if idx < len(deck) else ["tanker", None]
        s["lot"] = {"kind": kind, "district": district}
        # Vane's policy: she bids high 35 percent of the time, 75 percent when it is fuel and you are low,
        # 60 percent on the mail, and 15 points more often after the midpoint. The clerk reports her
        # mode, wrong 1 week in 6.
        p = 0.35
        if kind == "tanker" and s["fuel"] <= 4:
            p = 0.75
        if kind == "mail":
            p = 0.6
        if s["_turn"] >= MIDPOINT:
            p += 0.15
        high = rng.chance(p)
        s["hidden"]["vane_high"] = high
        truthful = rng.d(6) != 1
        s["tell"] = "HIGH" if (high == truthful) else "LOW"

    def _lot_label(self, s):
        lot = s["lot"]
        if lot["kind"] == "tanker":
            n = TANKER_LATE if s["_turn"] >= MIDPOINT else TANKER_EARLY
            return f"Tanker (+{n} fuel)"
        if lot["kind"] == "lease":
            return f"Lease: {lot['district']}"
        return "Mail Contract"

    def _potential(self, s):
        return sum(d["level"] for d in s["dev"].values()) + (1 if s["mail"] else 0)

    def _tendable(self, s):
        young = [(n, d) for n, d in s["dev"].items() if d["level"] == 1]
        if not young:
            return None
        young.sort(key=lambda x: -x[1]["age"])
        return young[0][0]

    # ------------------------------------------------------------ contract
    def options(self, s):
        o = []
        lot = self._lot_label(s)
        for aid, amt in BIDS.items():
            if s["cash"] >= amt:
                o.append({"id": aid, "label": f"Bid {amt} on {lot}"})
        if s["calm"] == 0 and s["cash"] >= 10:
            o.append({"id": "tend_bess", "label": "Pass the lot; tend Bess (10 cash, calm 3 weeks)"})
        t = self._tendable(s)
        if t:
            o.append({"id": "tend_plot", "label": f"Pass the lot; tend {t} (matures now, 2 flights a week)"})
        if s["streak"] >= 2 and s["cash"] >= 12:
            o.append({"id": "drum", "label": "Pass the lot; buy the co-op's emergency drum (12 cash, +3 fuel)"})
        if not o:
            o.append({"id": "wait", "label": "Sit the week out"})
        return o

    def apply(self, s, a, args, rng):
        ev = []
        if a in BIDS:
            amt = BIDS[a]
            high = s["hidden"]["vane_high"]
            if high:
                vb = rng.roll(2, 6) + (12 if s["_turn"] >= MIDPOINT else 9)
            else:
                vb = rng.d(6) + 5
            tag = "HIGH" if high else "LOW"
            if amt > vb:
                s["cash"] -= amt
                s["streak"] = 0
                ev.append(f"Sealed bids opened: you {amt}, Vane {vb} ({tag}). You win the lot for {amt}.")
                ev += self._award(s)
            else:
                s["streak"] += 1
                ev.append(f"Sealed bids opened: you {amt}, Vane {vb} ({tag}). Vane takes it. Losses in a row: {s['streak']}.")
        elif a == "tend_bess":
            s["cash"] -= 10
            s["calm"] = 3
            ev.append("You walk Bess at dusk with a thermos and a wire brush. She is calm for 3 weeks.")
        elif a == "tend_plot":
            t = self._tendable(s)
            s["dev"][t]["level"] = 2
            s["dev"][t]["age"] = 3
            ev.append(f"{t} matured early: 2 flights a week from here.")
        elif a == "drum":
            s["cash"] -= 12
            s["fuel"] += 3
            s["streak"] = 0
            ev.append("The co-op rolls a drum up from the harbour. Fuel +3.")
        elif a == "wait":
            ev.append("You sit the week out.")
        return ev

    def _award(self, s):
        lot = s["lot"]
        if lot["kind"] == "tanker":
            n = TANKER_LATE if s["_turn"] >= MIDPOINT else TANKER_EARLY
            s["fuel"] += n
            return [f"Tanker unloads. Fuel +{n}."]
        if lot["kind"] == "lease":
            d = lot["district"]
            s["dev"][d] = {"level": 1, "age": 0}
            return [f"{d} leased: 1 flight a week, matures in 3 weeks. Districts {len(s['dev'])}/6."]
        s["mail"] = True
        return ["Mail Contract signed: +1 flight a week paying 12."]

    def advance(self, s, rng):
        ev = []
        t = s["_turn"]  # already incremented: this is the week that now begins
        week = t - 1    # the week that just resolved
        s["fog"] = rng.chance(0.15)
        potential = self._potential(s)
        if s["closed"]:
            flights = 0
            s["closed"] = False
            ev.append("Bess is closed this week; no flights.")
        elif s["fog"]:
            flights = 0
            ev.append("Fog week: the island is socked in, no flights.")
        else:
            flights = min(potential, max(0, s["fuel"] - 1 - RESERVE), 5)
            if flights < potential:
                ev.append(f"Only {flights} of {potential} flights could be fuelled (tower keeps {RESERVE} back for the lights).")
        income = flights * 8 + (4 if s["mail"] and flights >= 1 else 0)
        s["fuel"] -= flights + 1
        s["cash"] += income
        ev.append(f"Week {week}: {flights} flights, +{income} cash, fuel -{flights + 1} (lights included).")
        s["cash"] -= LEVY
        ev.append(f"Council levy -{LEVY}.")
        if s["calm"] > 0:
            s["calm"] -= 1
        elif flights >= 4:
            ok, txt = rng.check(3, label="Bess")
            if ok:
                ev.append(f"{txt}. Bess grumbles but holds.")
            else:
                s["closed"] = True
                s["cash"] -= 10
                ev.append(f"{txt}. Bess heaves: closed next week, -10 cash for the crew.")
        for n, d in s["dev"].items():
            if d["level"] == 1:
                d["age"] += 1
                if d["age"] >= 3:
                    d["level"] = 2
                    ev.append(f"{n} matured: 2 flights a week now.")
        if t == MIDPOINT:
            ev.append(f"Week 8: mainland fuel prices jump. Tankers now carry {TANKER_LATE}. Vane's purse is heavier. The Mail Contract is on the block.")
        if t <= self.turns:
            self._draw_lot(s, rng)
            ev.append(f"Next lot: {self._lot_label(s)}. Vane's clerk says her bid will be {s['tell']}.")
        return ev

    def status_line(self, s):
        return f"Cash {s['cash']} | Fuel {s['fuel']} | Districts {len(s['dev'])}/6 | Lot {self._lot_label(s)}, tell {s['tell']}"

    def check_end(self, s):
        if s["fuel"] <= 0:
            return {"result": "loss", "reason": "fuel ran out; the runway lights went dark"}
        if s["cash"] < 0:
            return {"result": "loss", "reason": "cash below 0; the council impeached you"}
        if s["_turn"] > self.turns:
            n = len(s["dev"])
            if s["cash"] >= WIN_CASH and n >= WIN_DEV:
                return {"result": "win", "reason": f"auditor satisfied: cash {s['cash']}, districts {n}/6"}
            return {"result": "loss", "reason": f"auditor unsatisfied: cash {s['cash']} (need {WIN_CASH}), districts {n} (need {WIN_DEV})"}
        return None

    def visible(self, s):
        v = {k: v for k, v in s.items() if k not in ("hidden", "_rng", "_turn", "_ended")}
        v["flights_potential"] = self._potential(s)
        return v

    # ------------------------------------------------------------ policy
    def heuristic(self, s, options, rng):
        """Fuel first, then districts up to the auditor's 4, then cash for the audit."""
        ids = {o["id"] for o in options}
        t = s["_turn"]
        lot = s["lot"]["kind"]
        n = len(s["dev"])
        left = self.turns - t + 1
        potential = self._potential(s)
        burn = 1 + min(potential, 5)
        weeks_of_fuel = s["fuel"] / burn
        usable = s["fuel"] - RESERVE
        fuel_ok = usable >= 1
        if "drum" in ids and usable <= 0 and lot != "tanker":
            return "drum"
        if "tend_bess" in ids and potential >= 4 and fuel_ok and s["cash"] >= 30 and lot != "tanker":
            return "tend_bess"
        want = False
        if lot == "tanker":
            need_total = burn * left  # fuel to fly everything until the audit
            want = (usable < 3 * burn or usable <= 8) and s["fuel"] < need_total
        elif lot == "lease":
            want = n < WIN_DEV or (n < 6 and left >= 5 and usable >= 5)
        elif lot == "mail":
            want = True
        urgent = lot == "tanker" and usable <= 1 and left > 2
        if lot == "lease" and n < WIN_DEV and left <= 6:
            urgent = True
        reserve = 10 if t < 12 else 30
        if urgent:
            reserve = 0
        if want:
            if urgent and "bid_high" in ids:
                return "bid_high"
            if s["tell"] == "LOW":
                if "bid_mid" in ids and s["cash"] - 14 >= reserve:
                    return "bid_mid"
                if "bid_low" in ids:
                    return "bid_low"
            else:
                if "bid_high" in ids and s["cash"] - 22 >= reserve:
                    return "bid_high"
                if "bid_mid" in ids and (urgent or t < MIDPOINT) and s["cash"] - 14 >= reserve:
                    return "bid_mid"
                if "bid_low" in ids and urgent:
                    return "bid_low"
        if "drum" in ids and usable <= 0:
            return "drum"
        if "tend_plot" in ids and usable >= 4:
            return "tend_plot"
        if "tend_bess" in ids and potential >= 4 and fuel_ok and s["cash"] >= 20:
            return "tend_bess"
        if "bid_low" in ids and lot == "tanker":
            return "bid_low"
        if "bid_low" in ids and lot == "lease" and n < 6 and fuel_ok:
            return "bid_low"
        if "wait" in ids:
            return "wait"
        if "bid_low" in ids:
            return "bid_low"
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
