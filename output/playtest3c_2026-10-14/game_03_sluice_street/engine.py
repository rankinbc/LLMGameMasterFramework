"""Sluice Street Audit: a /play game (v3 contract).

Caravan master of the last wagon train into Pyrite Flat. Lay depots along a creekside street whose
pay-dirt slides downstream every night, sell what you learn to the Land Office, keep Voss Freight from
the best lots, and satisfy the Territorial Auditor before the snow closes the pass.

Rulesheet: run `python engine.py rules`.
"""

import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, plural, run  # noqa: E402

NAMES = {"R": "Rich", "F": "Fair", "P": "Poor"}


def _open_count(game, s):
    """Depots of yours that stand on open lots."""
    return sum(1 for i in range(game.C["LOTS"]) if s["lots"][i] == "M" and i >= s["snow"])


def _known_count(game, s):
    return sum(1 for k in s["known"] if k)


def _can_file(game, s):
    return _known_count(game, s) > 0


def _can_build(game, s):
    return bool(game._build_lots(s))


def _can_scout(game, s):
    return any(not s["known"][i] for i in range(s["snow"], game.C["LOTS"]))


def _can_raise(game, s):
    return any(s["lots"][i] == "M" and not s["raised"][i] for i in range(s["snow"], game.C["LOTS"]))


class G(Game):
    name = "Sluice Street Audit"

    CONSTANTS = {
        "TURNS": 16,
        "LOTS": 6,
        "START_STANDING": 12,
        "RICH_PAY": 3,
        "FAIR_PAY": 1,
        "POOR_PAY": 0,
        "ADJ_PAY": 1,
        "FILE_PAY": 5,
        "BUILD_COST": 8,
        "BUYOUT_COST": 16,
        "RAISE_FROM": 8,
        "RAISE_COST": 10,
        "RAISE_PAY": 3,
        "VOSS_FROM": 3,
        "VOSS_EVERY": 4,
        "SNOW_FROM": 8,
        "SNOW_EVERY": 2,
        "SNOW_MAX": 3,
        "PLOUGH_COST": 5,
        "LEVY": 132,
        "INSPECT": 3,
        "FLOOD_FROM": 9,
        "FLOOD_TO": 15,
        "_DIE": 6,
        "_RICH_UP": 1,
        "_FAIR_UP": 4,
    }

    RULES = """
1. {LOTS} lots run in a line from the pass (lot 1) to the creek (lot {LOTS}). Each night you do one thing: scout, build, file, raise or plough. You start with {START_STANDING} Standing.
2. Every lot lies on Rich, Fair or Poor ground, hidden until scouted. At dusk each open depot of yours pays by its ground (Rich {RICH_PAY}, Fair {FAIR_PAY}, Poor {POOR_PAY}), plus {ADJ_PAY} for each open depot of yours beside it.
3. After pay, the ground slides one lot toward the creek with what you know; lot {LOTS}'s ground is lost, lot 1 gets unseen ground. One unannounced night from {FLOOD_FROM} to {FLOOD_TO}, a flood slides it twice and washes out lot {LOTS}.
4. Scouting a lot shows its ground. Filing your survey pays {FILE_PAY} Standing for each lot whose ground you know, then the Land Office keeps your notes and you know nothing.
5. Build a depot on an empty open lot for {BUILD_COST} Standing, or buy out one of Voss's for {BUYOUT_COST}. From night {RAISE_FROM}, raising a depot (once each) costs {RAISE_COST}, and it then pays {RAISE_PAY} more a night.
6. Voss Freight stakes the empty open lot with the richest ground (nearest the creek on a tie) after the dusk slide on night {VOSS_FROM} and every {VOSS_EVERY} nights after. His stake shows you the ground beneath it.
7. From night {SNOW_FROM} snow closes lot 1, another lot every {SNOW_EVERY} nights to lot {SNOW_MAX}. Closed lots cannot be scouted, built on or raised; their depots pay nothing. Once lot {SNOW_MAX} closes, one plough ({PLOUGH_COST} Standing) reopens it for good.
8. After night {TURNS} the Auditor arrives on the last wagon. You win if Standing is at least the Levy of {LEVY} (the books balance) and at least {INSPECT} of your depots are open (he is satisfied).
"""

    ACTIONS = ["scout", "build", "file", "raise", "plough"]
    TAGS = ["scout", "file", "build", "buyout", "raise", "plough", "stake", "snow", "flood",
            "closed_depot", "neighbour_pay", "lost_known", "washout"]
    TRACKED = ["standing", "lots", "snow"]

    BOUNDS = {"standing": (0, 400), "snow": (0, 6), "open": (0, 6), "known": (0, 6), "ploughed": (0, 1)}
    REACH = {"standing": 132, "snow": 3, "open": 3, "known": 4}
    DERIVED = {"open": _open_count, "known": _known_count}
    GATES = {
        "scout": {"_if": _can_scout},
        "build": {"standing": "BUILD_COST", "_if": _can_build},
        "file": {"_if": _can_file},
        "raise": {"standing": "RAISE_COST", "_turn": "RAISE_FROM", "_if": _can_raise},
        "plough": {"standing": "PLOUGH_COST", "snow": "SNOW_MAX", "!ploughed": 1},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    def _pay(self, ground):
        C = self.C
        return {"R": C["RICH_PAY"], "F": C["FAIR_PAY"], "P": C["POOR_PAY"]}[ground]

    def _draw(self, rng):
        C = self.C
        v = rng.d(C["_DIE"])
        if v <= C["_RICH_UP"]:
            return "R"
        if v <= C["_FAIR_UP"]:
            return "F"
        return "P"

    def _build_lots(self, s):
        """Lot numbers (1-based) the player can build on or buy out right now."""
        C = self.C
        out = []
        for i in range(s["snow"], C["LOTS"]):
            if s["lots"][i] == "" and s["standing"] >= C["BUILD_COST"]:
                out.append(i + 1)
            elif s["lots"][i] == "V" and s["standing"] >= C["BUYOUT_COST"]:
                out.append(i + 1)
        return out

    def _is_stake_night(self, n):
        C = self.C
        return n >= C["VOSS_FROM"] and (n - C["VOSS_FROM"]) % C["VOSS_EVERY"] == 0

    def _stake_night_from(self, n):
        """The first night on or after night n on which Voss stakes."""
        C = self.C
        gaps = -(-(max(n, C["VOSS_FROM"]) - C["VOSS_FROM"]) // C["VOSS_EVERY"])  # rounded up
        return C["VOSS_FROM"] + gaps * C["VOSS_EVERY"]

    # ------------------------------------------------------------ the contract

    def resample_hidden(self, s, rng):
        """Ground the player has not seen is redrawn; so is the flood night if it has not happened."""
        C = self.C
        g = s["hidden"]["ground"]
        for i in range(C["LOTS"]):
            if s["known"][i]:
                g[i] = s["known"][i]
            else:
                g[i] = self._draw(rng)
        if not s["flooded"]:
            lo = max(s["_turn"], C["FLOOD_FROM"])
            hi = C["FLOOD_TO"]
            if lo > hi:
                lo = hi
            s["hidden"]["flood"] = lo - 1 + rng.d(hi - lo + 1)

    def init_state(self, rng):
        C = self.C
        L = C["LOTS"]
        ground = [self._draw(rng) for _ in range(L)]
        flood = C["FLOOD_FROM"] - 1 + rng.d(C["FLOOD_TO"] - C["FLOOD_FROM"] + 1)
        return {
            "standing": C["START_STANDING"],
            "snow": 0,
            "ploughed": 0,
            "lots": [""] * L,
            "raised": [False] * L,
            "known": [""] * L,
            "flooded": False,
            "hidden": {"ground": ground, "flood": flood},
        }

    def visible(self, s):
        v = {k: x for k, x in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "_seed")}
        nxt = self._stake_night_from(s["_turn"])
        v["voss_stakes_on_night"] = nxt if nxt <= self.C["TURNS"] else None
        v["legend"] = ("Street cell = lot number, building, ground. Building: . empty, D your depot, "
                       "H your raised depot, V Voss Freight. Ground: ? unknown, R Rich, F Fair, P Poor. "
                       "Brackets mean the lot is closed by snow.")
        return v

    def options(self, s):
        C = self.C
        L = C["LOTS"]
        o = []
        unknown = [i + 1 for i in range(s["snow"], L) if not s["known"][i]]
        if unknown:
            o.append({"id": "scout", "label": "Scout a lot (see its ground)", "args": {},
                      "params": {"lot": {"choices": unknown}}})
        build = self._build_lots(s)
        if build:
            voss = [n for n in build if s["lots"][n - 1] == "V"]
            if voss and len(voss) == len(build):
                label = f"Buy out a Voss stake ({C['BUYOUT_COST']} Standing)"
            elif voss:
                label = f"Build a depot ({C['BUILD_COST']} Standing on an empty lot, {C['BUYOUT_COST']} to buy out Voss)"
            else:
                label = f"Build a depot on an empty lot ({C['BUILD_COST']} Standing)"
            o.append({"id": "build", "label": label, "args": {}, "params": {"lot": {"choices": build}}})
        n_known = _known_count(self, s)
        if n_known:
            o.append({"id": "file",
                      "label": f"File your survey ({plural(n_known, 'lot')} known: Standing +{n_known * C['FILE_PAY']}, then your notes are gone)",
                      "args": {}})
        if s["_turn"] >= C["RAISE_FROM"] and s["standing"] >= C["RAISE_COST"]:
            up = [i + 1 for i in range(s["snow"], L) if s["lots"][i] == "M" and not s["raised"][i]]
            if up:
                o.append({"id": "raise",
                          "label": f"Raise a depot ({C['RAISE_COST']} Standing, then it pays {C['RAISE_PAY']} more a night)",
                          "args": {}, "params": {"lot": {"choices": up}}})
        if s["snow"] >= C["SNOW_MAX"] and not s["ploughed"] and s["standing"] >= C["PLOUGH_COST"]:
            o.append({"id": "plough",
                      "label": f"Plough lot {s['snow']} clear of snow for good ({C['PLOUGH_COST']} Standing)",
                      "args": {}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "scout":
            n = args["lot"]
            s["known"][n - 1] = s["hidden"]["ground"][n - 1]
            ev.append(f"Lot {n} scouted: {NAMES[s['known'][n - 1]]} ground.")
            self.hit("scout")
        elif a == "build":
            n = args["lot"]
            if s["lots"][n - 1] == "V":
                s["standing"] -= C["BUYOUT_COST"]
                ev.append(f"Voss Freight sold you its stake on lot {n} (Standing -{C['BUYOUT_COST']}). The depot is yours.")
                self.hit("buyout")
            else:
                s["standing"] -= C["BUILD_COST"]
                ev.append(f"Depot built on lot {n} (Standing -{C['BUILD_COST']}).")
                self.hit("build")
            s["lots"][n - 1] = "M"
        elif a == "file":
            n = _known_count(self, s)
            gain = n * C["FILE_PAY"]
            s["standing"] += gain
            s["known"] = [""] * C["LOTS"]
            ev.append(f"Survey filed: {plural(n, 'lot')} reported, Standing +{gain}. The Land Office keeps the notes.")
            self.hit("file")
        elif a == "raise":
            n = args["lot"]
            s["standing"] -= C["RAISE_COST"]
            s["raised"][n - 1] = True
            ev.append(f"Depot on lot {n} raised (Standing -{C['RAISE_COST']}). It pays {C['RAISE_PAY']} more a night.")
            self.hit("raise")
        elif a == "plough":
            n = s["snow"]
            s["standing"] -= C["PLOUGH_COST"]
            s["snow"] -= 1
            s["ploughed"] = 1
            ev.append(f"The plough gang cleared lot {n} (Standing -{C['PLOUGH_COST']}).")
            self.hit("plough")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        t = s["_turn"]
        L = C["LOTS"]
        h = s["hidden"]
        nxt = t + 1

        # 1. depots pay by the ground under them
        n_open = ground_pay = near_pay = up_pay = 0
        for i in range(s["snow"], L):
            if s["lots"][i] != "M":
                continue
            n_open += 1
            ground_pay += self._pay(h["ground"][i])
            if i + 1 < L and s["lots"][i + 1] == "M":
                near_pay += 2 * C["ADJ_PAY"]  # a pair of neighbours: each depot of the pair is paid for the other
            if s["raised"][i]:
                up_pay += C["RAISE_PAY"]
        total = ground_pay + near_pay + up_pay
        s["standing"] += total
        if near_pay:
            self.hit("neighbour_pay")
        if any(s["lots"][i] == "M" for i in range(s["snow"])):
            self.hit("closed_depot")
        if n_open == 0:
            ev.append("Dusk: no depot of yours is open, so nothing was paid.")
        elif total == 0:
            ev.append(f"Dusk: {plural(n_open, 'open depot')} paid nothing.")
        else:
            parts = []
            if near_pay:
                parts.append(f"neighbours {near_pay}")
            if up_pay:
                parts.append(f"raises {up_pay}")
            extra = f" ({', '.join(parts)})" if parts else ""
            ev.append(f"Dusk: {plural(n_open, 'open depot')} paid Standing +{total}{extra}.")

        # 2. the ground slides toward the creek
        slides = 1
        flood = not s["flooded"] and h["flood"] == t
        if flood:
            slides += 1
            s["flooded"] = True
            self.hit("flood")
            owner = s["lots"][L - 1]
            s["lots"][L - 1] = ""
            s["raised"][L - 1] = False
            if owner == "M":
                self.hit("washout")
                ev.append(f"The creek flooded in the night: the ground slid two lots and your depot on lot {L} was washed out.")
            elif owner == "V":
                self.hit("washout")
                ev.append(f"The creek flooded in the night: the ground slid two lots and Voss Freight lost its stake on lot {L}.")
            else:
                ev.append("The creek flooded in the night: the ground slid two lots.")
        lost = []
        for k in range(slides):
            gone_known = s["known"][-1]
            if gone_known:
                lost.append((L - k, gone_known))
            h["ground"] = [self._draw(rng)] + h["ground"][:-1]
            s["known"] = [""] + s["known"][:-1]
        for lot, kind in lost:
            self.hit("lost_known")
            ev.append(f"The creek carried off your notes on lot {lot}: it was {NAMES[kind]} ground.")

        # 3. Voss Freight
        if self._is_stake_night(t):
            empties = [i for i in range(s["snow"], L) if s["lots"][i] == ""]
            if empties:
                pick = max(empties, key=lambda i: (self._pay(h["ground"][i]), i))
                s["lots"][pick] = "V"
                s["known"][pick] = h["ground"][pick]
                self.hit("stake")
                ev.append(f"Voss Freight staked lot {pick + 1}: {NAMES[h['ground'][pick]]} ground.")
            else:
                ev.append("Voss Freight found no empty open lot to stake.")
        if nxt <= C["TURNS"] and self._is_stake_night(nxt):
            ev.append(f"Voss Freight will stake at dusk on night {nxt}.")
        # 4. snow moves for tomorrow (Voss and the pay above saw tonight's snow line)
        if (nxt <= C["TURNS"] and nxt >= C["SNOW_FROM"] and (nxt - C["SNOW_FROM"]) % C["SNOW_EVERY"] == 0
                and s["snow"] < C["SNOW_MAX"] - s["ploughed"]):
            s["snow"] += 1
            self.hit("snow")
            if s["snow"] == 1:
                ev.append(f"Snow closes lot 1 from night {nxt}.")
            else:
                ev.append(f"Snow reaches lot {s['snow']} from night {nxt}.")
        return ev

    def status_line(self, s):
        C = self.C
        cells = []
        for i in range(C["LOTS"]):
            b = {"": ".", "M": "D", "V": "V"}[s["lots"][i]]
            if b == "D" and s["raised"][i]:
                b = "H"
            cell = f"{i + 1}{b}{s['known'][i] or '?'}"
            if i < s["snow"]:
                cell = f"({cell})"
            cells.append(cell)
        return f"Standing {s['standing']} | Snow {s['snow']} | Open {_open_count(self, s)} | Street: {' '.join(cells)}"

    def check_end(self, s):
        return None

    def final_check(self, s):
        C = self.C
        n = _open_count(self, s)
        rich = s["standing"] >= C["LEVY"]
        seen = n >= C["INSPECT"]
        if rich and seen:
            return {"result": "win",
                    "reason": f"the Auditor signed: Standing {s['standing']} covers the Levy of {C['LEVY']} and {plural(n, 'open depot')} passed inspection"}
        if not rich and not seen:
            return {"result": "loss",
                    "reason": f"the Auditor refused to sign: Standing {s['standing']} is short of the Levy of {C['LEVY']} and he counted {plural(n, 'open depot')} against the {C['INSPECT']} he needs"}
        if not rich:
            return {"result": "loss",
                    "reason": f"the Auditor found the books short: Standing {s['standing']} against a Levy of {C['LEVY']}"}
        return {"result": "loss",
                "reason": f"the Auditor found too few open depots: {n} where he needs {C['INSPECT']}"}

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"]: o for o in options}
        t = s["_turn"]
        left = C["TURNS"] - t + 1
        L = C["LOTS"]
        opn = _open_count(self, s)
        known = _known_count(self, s)
        safe = sum(1 for i in range(L) if s["lots"][i] == "M" and i >= C["SNOW_MAX"])
        short = opn < C["INSPECT"]
        # a depot stands on the newest closed lot: ploughing is worth it when the inspection is short or there is time to earn
        if "plough" in ids and s["lots"][s["snow"] - 1] == "M" and (
                short or (left >= 3 and s["standing"] >= C["PLOUGH_COST"] + C["BUILD_COST"])):
            return "plough"
        # too few depots near the end: rebuild where it is cheapest and nearest the creek
        if short and left <= 4 and "build" in ids:
            pick = max(ids["build"]["params"]["lot"]["choices"], key=lambda n: (s["lots"][n - 1] == "", n))
            return {"id": "build", "args": {"lot": pick}}
        if "file" in ids and left <= 1:
            return "file"
        if "build" in ids and left >= 4:
            best, best_score = None, 0
            for n in ids["build"]["params"]["lot"]["choices"]:
                i = n - 1
                cost = C["BUYOUT_COST"] if s["lots"][i] == "V" else C["BUILD_COST"]
                est = self._pay(s["known"][i]) if s["known"][i] else 1
                near = sum(1 for j in (i - 1, i + 1) if 0 <= j < L and s["lots"][j] == "M")
                nights = left if i >= C["SNOW_MAX"] else max(0, C["SNOW_FROM"] + i * C["SNOW_EVERY"] - t)
                score = (est + near * C["ADJ_PAY"]) * nights - cost
                if i >= C["SNOW_MAX"] and safe < C["INSPECT"]:
                    score += 6
                if score > best_score:
                    best, best_score = n, score
            if best is not None:
                return {"id": "build", "args": {"lot": best}}
        if "raise" in ids and left >= 5:
            reserve = C["BUILD_COST"] if (not s["flooded"] and s["lots"][L - 1] == "M") else 0  # the flood may wash out the last lot
            if s["standing"] >= C["RAISE_COST"] + reserve + 2:
                picks = [n for n in ids["raise"]["params"]["lot"]["choices"] if s["flooded"] or n < L]
                if picks:
                    return {"id": "raise", "args": {"lot": picks[0]}}
        if "file" in ids and (known >= 3 or "scout" not in ids):
            return "file"
        if "scout" in ids:
            return {"id": "scout", "args": {"lot": ids["scout"]["params"]["lot"]["choices"][0]}}
        return "file"

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        L = C["LOTS"]
        POOR = C["_DIE"]       # a die that draws Poor ground
        FAIR = C["_FAIR_UP"]   # a die that draws Fair ground
        RICH = C["_RICH_UP"]   # a die that draws Rich ground
        BLANK = [""] * L

        def lot_choices(s, aid):
            for o in self.options(s):
                if o["id"] == aid:
                    return o["params"]["lot"]["choices"]
            return []

        def r1(t):
            s = t.fresh()
            t.eq(len(s["lots"]), L, "a street of LOTS lots")
            t.eq(s["lots"], BLANK, "the street starts empty")
            t.eq(s["standing"], C["START_STANDING"], "starting Standing")
            t.eq(t.ids(s), ["build", "scout"], "night 1 offers only scout and build")
            t.eq(lot_choices(s, "scout"), list(range(1, L + 1)), "every lot can be scouted, counted from 1")
            t.eq(lot_choices(s, "build"), list(range(1, L + 1)), "every lot can be built on, counted from 1")
            t.eq(t.status(s), f"Standing {C['START_STANDING']} | Snow 0 | Open 0 | Street: 1.? 2.? 3.? 4.? 5.? 6.?", "the status line")
            t.eq(t.label(s, "build", lot=1), f"Build a depot on an empty lot ({C['BUILD_COST']} Standing)", "the build label")
            t.eq(t.label(s, "scout", lot=1), "Scout a lot (see its ground)", "the scout label")
            s2, _ = t.step(s, "scout", {"lot": 1})
            t.eq(s2["_turn"], 2, "one action ends the night")
            s3 = t.fresh(standing=C["BUILD_COST"] - 1)
            t.eq(t.ids(s3), ["scout"], "a poor caravan can only scout")
            s4 = t.fresh(known=["R", "", "", "", "", ""])
            t.ok("file" in t.ids(s4), "a known lot can be filed")
            starts = set()
            for sd in range(1, 60):
                starts |= set(t.fresh(seed=sd)["hidden"]["ground"])
            t.eq(starts, {"R", "F", "P"}, "the ground can be Rich, Fair or Poor, and nothing else")
            t.eq(t.fresh()["known"], BLANK, "you know no ground at the start")
            t.ok("hidden" not in self.visible(s), "the ground is hidden")

        def r2(t):
            s = t.fresh(lots=["M", "M", "", "", "", ""], hidden__ground=["R", "F", "P", "P", "P", "P"], standing=0)
            ev = t.advance(s, turn=2, dice=[POOR])
            want = C["RICH_PAY"] + C["FAIR_PAY"] + 2 * C["ADJ_PAY"]
            t.eq(s["standing"], want, "Rich and Fair ground pay, and each depot has one neighbour")
            t.has(ev, f"Dusk: 2 open depots paid Standing +{want} (neighbours {2 * C['ADJ_PAY']}).")
            t.ok(not any("ground" in e for e in ev), "the dusk line does not name the ground under your depots")
            t.ok("neighbour_pay" in self._hits, "neighbour pay is noted")
            s = t.fresh(lots=["M", "", "M", "", "", ""], hidden__ground=["F", "F", "F", "P", "P", "P"], standing=0)
            ev = t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], 2 * C["FAIR_PAY"], "depots with a gap between them are not neighbours")
            t.has(ev, f"Dusk: 2 open depots paid Standing +{2 * C['FAIR_PAY']}.")
            s = t.fresh(lots=["", "", "", "", "M", "M"], hidden__ground=["P", "P", "P", "P", "F", "F"], standing=0)
            t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], 2 * C["FAIR_PAY"] + 2 * C["ADJ_PAY"], "the pair at the creek end are neighbours")
            s = t.fresh(lots=["", "", "M", "", "", ""], hidden__ground=["P", "P", "P", "P", "P", "P"], standing=5)
            ev = t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], 5 + C["POOR_PAY"], "Poor ground pays POOR_PAY")
            t.has(ev, "Dusk: 1 open depot paid nothing.")
            s = t.fresh(lots=["", "", "M", "", "M", ""], hidden__ground=["P", "P", "R", "P", "R", "P"], standing=0)
            t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], 2 * C["RICH_PAY"], "the true ground pays, whether or not you scouted it")
            s = t.fresh(lots=BLANK, hidden__ground=["R"] * L, standing=3)
            ev = t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], 3, "no depots, no pay")
            t.has(ev, "Dusk: no depot of yours is open, so nothing was paid.")
            s = t.fresh(lots=["M", "M", "", "", "", ""], hidden__ground=["R", "F", "P", "P", "P", "P"], snow=1, standing=0)
            ev = t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], C["FAIR_PAY"], "a closed depot pays nothing and is no neighbour")
            t.ok("closed_depot" in self._hits, "a shut depot is noted")
            s = t.fresh(lots=["V", "M", "", "", "", ""], hidden__ground=["F", "F", "P", "P", "P", "P"], standing=0)
            t.advance(s, turn=2, dice=[POOR])
            t.eq(s["standing"], C["FAIR_PAY"], "a depot of Voss's is no neighbour of yours")

        def r3(t):
            g0 = ["R", "F", "P", "R", "P", "F"]
            s = t.fresh(lots=["M", "", "", "", "", ""], hidden__ground=g0, known=["R", "", "", "", "", "F"], standing=0, flooded=True)
            ev = t.advance(s, turn=2, dice=[FAIR])
            t.eq(s["standing"], C["RICH_PAY"], "the depot is paid before the ground slides")
            t.eq(s["hidden"]["ground"], ["F"] + g0[:-1], "the ground slides one lot toward the creek; new ground arrives at lot 1")
            t.eq(s["known"], ["", "R", "", "", "", ""], "what you know slides with it, and lot 6 is lost")
            t.has(ev, f"The creek carried off your notes on lot {L}: it was Fair ground.")
            t.ok("lost_known" in self._hits, "lost knowledge is noted")
            t.ok(not any("flooded" in e for e in ev), "no flood once the flood is spent")
            s = t.fresh(hidden__ground=g0, known=["", "", "", "", "", ""], flooded=True)
            ev = t.advance(s, turn=2, dice=[RICH])
            t.ok(not any("carried off" in e for e in ev), "nothing known, nothing lost")
            s = t.fresh(hidden__ground=g0, hidden__flood=2, known=["R", "F", "", "", "P", "F"], flooded=False)
            ev = t.advance(s, turn=2, dice=[RICH, FAIR])
            t.eq(s["hidden"]["ground"], ["F", "R"] + g0[:-2], "a flood slides the ground two lots")
            t.eq(s["known"], ["", "", "R", "F", "", ""], "and what you know with it")
            t.ok(s["flooded"], "the flood is spent")
            t.has(ev, "The creek flooded in the night: the ground slid two lots.")
            t.has(ev, f"The creek carried off your notes on lot {L}: it was Fair ground.")
            t.has(ev, f"The creek carried off your notes on lot {L - 1}: it was Poor ground.")
            t.ok("flood" in self._hits, "the flood is noted")
            s = t.fresh(hidden__ground=g0, hidden__flood=3, flooded=False)
            ev = t.advance(s, turn=2, dice=[RICH])
            t.ok(not s["flooded"] and s["hidden"]["ground"] == ["R"] + g0[:-1], "no flood on another night")
            s = t.fresh(hidden__ground=g0, hidden__flood=2, flooded=True)
            t.advance(s, turn=2, dice=[RICH, FAIR])
            t.eq(s["hidden"]["ground"], ["R"] + g0[:-1], "the flood happens once")
            s = t.fresh(hidden__ground=g0, hidden__flood=2, flooded=False, lots=["", "", "", "", "", "M"], raised=[False] * 5 + [True], standing=0)
            ev = t.advance(s, turn=2, dice=[RICH, FAIR])
            t.eq((s["lots"][L - 1], s["raised"][L - 1]), ("", False), "a flood washes out the depot on the last lot, raised or not")
            t.has(ev, f"The creek flooded in the night: the ground slid two lots and your depot on lot {L} was washed out.")
            t.eq(s["standing"], C["FAIR_PAY"] + C["RAISE_PAY"], "the washed-out depot is still paid for the night before the flood")
            t.ok("washout" in self._hits, "a washout is noted")
            s = t.fresh(hidden__ground=g0, hidden__flood=2, flooded=False, lots=["", "", "", "", "", "V"])
            ev = t.advance(s, turn=2, dice=[RICH, FAIR])
            t.eq(s["lots"][L - 1], "", "a flood washes out Voss's stake as well")
            t.has(ev, f"The creek flooded in the night: the ground slid two lots and Voss Freight lost its stake on lot {L}.")
            s = t.fresh(hidden__ground=g0, hidden__flood=2, flooded=False, lots=["M", "M", "M", "M", "M", ""])
            ev = t.advance(s, turn=2, dice=[RICH, FAIR])
            t.eq(s["lots"], ["M", "M", "M", "M", "M", ""], "a flood washes out only the last lot")
            t.has(ev, "The creek flooded in the night: the ground slid two lots.")
            t.ok(not any("washed out" in e for e in ev), "nothing stood there, nothing washed out")
            s = t.fresh(hidden__ground=g0, hidden__flood=3, flooded=False, lots=["", "", "", "", "", "M"])
            t.advance(s, turn=2, dice=[RICH])
            t.eq(s["lots"][L - 1], "M", "no washout without a flood")
            floods = {t.fresh(seed=sd)["hidden"]["flood"] for sd in range(1, 300)}
            t.eq(floods, set(range(C["FLOOD_FROM"], C["FLOOD_TO"] + 1)), "the flood night is any night in its window")
            t.eq(t.fresh()["flooded"], False, "no flood yet at the start")

        def r4(t):
            s = t.fresh(hidden__ground=["R", "F", "P", "P", "P", "P"])
            ev = t.apply(s, "scout", {"lot": 1})
            t.eq(s["known"][0], "R", "scouting shows the ground")
            t.has(ev, "Lot 1 scouted: Rich ground.")
            t.has(t.apply(s, "scout", {"lot": 2}), "Lot 2 scouted: Fair ground.")
            t.has(t.apply(s, "scout", {"lot": 3}), "Lot 3 scouted: Poor ground.")
            t.ok(not t.offered(s, "scout", lot=1), "a known lot is not scouted again")
            t.ok(t.offered(s, "scout", lot=4), "an unknown lot can be scouted")
            t.ok("scout" in self._hits, "scouting is noted")
            s = t.fresh(known=["R", "F", "", "", "", "P"], hidden__ground=["R", "F", "P", "P", "P", "P"], standing=0)
            t.eq(t.label(s, "file"), f"File your survey (3 lots known: Standing +{3 * C['FILE_PAY']}, then your notes are gone)", "the file label")
            ev = t.apply(s, "file")
            t.eq(s["standing"], 3 * C["FILE_PAY"], "filing pays for each known lot")
            t.eq(s["known"], BLANK, "and you forget them")
            t.has(ev, f"Survey filed: 3 lots reported, Standing +{3 * C['FILE_PAY']}. The Land Office keeps the notes.")
            t.eq(s["hidden"]["ground"], ["R", "F", "P", "P", "P", "P"], "the ground itself is unchanged")
            t.ok("file" in self._hits, "filing is noted")
            s = t.fresh(known=["", "", "", "F", "", ""], standing=0)
            t.eq(t.label(s, "file"), f"File your survey (1 lot known: Standing +{C['FILE_PAY']}, then your notes are gone)", "one lot, singular")
            t.has(t.apply(s, "file"), f"Survey filed: 1 lot reported, Standing +{C['FILE_PAY']}.")
            t.ok("file" not in t.ids(t.fresh()), "nothing known, nothing to file")
            s = t.fresh(snow=2)
            t.eq(lot_choices(s, "scout"), [3, 4, 5, 6], "a closed lot cannot be scouted")
            s = t.fresh(snow=1, known=["F", "", "", "", "", ""], standing=0)
            t.apply(s, "file")
            t.eq(s["standing"], C["FILE_PAY"], "notes on a closed lot are still filed")
            s = t.fresh(lots=["V", "M", "", "", "", ""])
            t.eq(lot_choices(s, "scout"), [1, 2, 3, 4, 5, 6], "any open lot with unknown ground can be scouted, depots and Voss's stakes included")

        def r5(t):
            s = t.fresh(standing=C["BUILD_COST"])
            t.ok(t.offered(s, "build", lot=3), "exactly enough Standing builds")
            ev = t.apply(s, "build", {"lot": 3})
            t.eq(s["standing"], 0, "building costs BUILD_COST")
            t.eq(s["lots"][2], "M", "the depot stands on lot 3")
            t.has(ev, f"Depot built on lot 3 (Standing -{C['BUILD_COST']}).")
            t.ok("build" in self._hits, "building is noted")
            t.ok(not t.offered(s, "build", lot=3), "a lot with a depot cannot be built on")
            t.ok("build" not in t.ids(s), "no Standing, no building")
            s = t.fresh(standing=C["BUILD_COST"] - 1)
            t.ok("build" not in t.ids(s), "one short of the cost")
            s = t.fresh(standing=C["BUYOUT_COST"], lots=["V", "", "", "", "", ""])
            t.ok(t.offered(s, "build", lot=1), "exactly enough Standing buys Voss out")
            t.eq(t.label(s, "build", lot=1), f"Build a depot ({C['BUILD_COST']} Standing on an empty lot, {C['BUYOUT_COST']} to buy out Voss)", "the label with a buyout")
            s_only = t.fresh(standing=C["BUYOUT_COST"], lots=["V"] + ["M"] * (L - 1))
            t.eq(t.label(s_only, "build", lot=1), f"Buy out a Voss stake ({C['BUYOUT_COST']} Standing)", "the buyout label with no empty lot")
            ev = t.apply(s, "build", {"lot": 1})
            t.eq((s["standing"], s["lots"][0]), (0, "M"), "the buyout costs BUYOUT_COST and the depot is yours")
            t.has(ev, f"Voss Freight sold you its stake on lot 1 (Standing -{C['BUYOUT_COST']}). The depot is yours.")
            t.ok("buyout" in self._hits, "a buyout is noted")
            s = t.fresh(standing=C["BUYOUT_COST"] - 1, lots=["V", "", "", "", "", ""])
            t.ok(not t.offered(s, "build", lot=1), "one short of the buyout")
            t.ok(t.offered(s, "build", lot=2), "an empty lot is still open to build on")
            s = t.fresh(standing=C["BUYOUT_COST"] - 1, lots=["V", "M", "M", "M", "M", "M"])
            t.ok("build" not in t.ids(s), "a Voss lot alone, one short of the buyout")
            s = t.fresh(standing=50, snow=2, lots=["", "", "", "", "", ""])
            t.eq(lot_choices(s, "build"), [3, 4, 5, 6], "a closed lot cannot be built on")
            # raise
            s = t.fresh(standing=C["RAISE_COST"], lots=["M", "", "", "", "", ""])
            s["_turn"] = C["RAISE_FROM"] - 1
            t.ok("raise" not in t.ids(s), "no raising before its night")
            s["_turn"] = C["RAISE_FROM"]
            t.ok(t.offered(s, "raise", lot=1), "raising is open from its night, with exactly enough Standing")
            t.eq(t.label(s, "raise", lot=1), f"Raise a depot ({C['RAISE_COST']} Standing, then it pays {C['RAISE_PAY']} more a night)", "the raise label")
            ev = t.apply(s, "raise", {"lot": 1})
            t.eq((s["standing"], s["raised"][0]), (0, True), "raising costs RAISE_COST")
            t.has(ev, f"Depot on lot 1 raised (Standing -{C['RAISE_COST']}). It pays {C['RAISE_PAY']} more a night.")
            t.ok("raise" in self._hits, "raising is noted")
            s["hidden"]["ground"] = ["P"] * L
            ev = t.advance(s, turn=C["RAISE_FROM"], dice=[POOR])
            t.eq(s["standing"], C["RAISE_PAY"], "a raised depot pays RAISE_PAY more")
            t.has(ev, f"Dusk: 1 open depot paid Standing +{C['RAISE_PAY']} (raises {C['RAISE_PAY']}).")
            t.eq(self.status_line(s).split(" | ")[3], "Street: 1H? 2.? 3.? 4.? 5.? 6.?", "a raised depot shows as H")
            t.ok("raise" not in t.ids(s), "a depot is raised once")
            s = t.fresh(standing=C["RAISE_COST"] - 1, lots=["M", "", "", "", "", ""])
            s["_turn"] = C["RAISE_FROM"]
            t.ok("raise" not in t.ids(s), "one short of the raise")
            s = t.fresh(standing=50, lots=["V", "", "M", "", "", ""], snow=3)
            s["_turn"] = C["RAISE_FROM"]
            t.ok("raise" not in t.ids(s), "a closed depot and a Voss lot cannot be raised")
            s = t.fresh(standing=50, lots=["V", "", "M", "", "M", ""], snow=3)
            s["_turn"] = C["RAISE_FROM"]
            t.eq(lot_choices(s, "raise"), [5], "only your open depots can be raised")

        def r6(t):
            for n in range(1, C["TURNS"] + 1):
                s = t.fresh(standing=0, flooded=True)
                s["snow"] = 0
                ev = t.advance(s, turn=n, dice=[POOR])
                staked = s["lots"].count("V")
                due = n >= C["VOSS_FROM"] and (n - C["VOSS_FROM"]) % C["VOSS_EVERY"] == 0
                t.eq(staked, 1 if due else 0, f"Voss stakes on night {n} only if the schedule says so")
                t.eq(any("staked lot" in e for e in ev), due, f"the stake is announced on night {n}")
            s = t.fresh(hidden__ground=["P", "F", "R", "F", "P", "P"], flooded=True)
            ev = t.advance(s, turn=C["VOSS_FROM"], dice=[POOR])
            t.eq(s["lots"], ["", "", "", "V", "", ""], "Voss stakes the lot with the richest ground, after the slide")
            t.eq(s["known"][3], "R", "his stake shows you the ground")
            t.has(ev, "Voss Freight staked lot 4: Rich ground.")
            t.ok("stake" in self._hits, "a stake is noted")
            s = t.fresh(hidden__ground=["F", "P", "F", "P", "F", "P"], flooded=True)
            ev = t.advance(s, turn=C["VOSS_FROM"], dice=[FAIR])
            t.eq(s["lots"], ["", "", "", "", "", "V"], "a tie goes to the lot nearest the creek")
            t.has(ev, f"Voss Freight staked lot {L}: Fair ground.")
            s = t.fresh(hidden__ground=["F", "P", "F", "P", "F", "P"], flooded=True, lots=["", "", "", "", "", "M"])
            t.advance(s, turn=C["VOSS_FROM"], dice=[FAIR])
            t.eq(s["lots"].index("V"), 3, "he stakes only an empty lot: the next richest, not the occupied one")
            s = t.fresh(hidden__ground=["R", "P", "P", "P", "P", "P"], flooded=True, snow=3)
            t.advance(s, turn=C["VOSS_FROM"], dice=[POOR])
            t.eq(s["lots"], ["", "", "", "", "", "V"], "he stakes only an open lot")
            s = t.fresh(flooded=True, lots=["M"] * L)
            ev = t.advance(s, turn=C["VOSS_FROM"], dice=[POOR])
            t.has(ev, "Voss Freight found no empty open lot to stake.")
            old_from = C["VOSS_FROM"]
            try:
                C["VOSS_FROM"] = C["SNOW_FROM"] - 1
                s = t.fresh(flooded=True, lots=[""] + ["M"] * (L - 1))
                ev = t.advance(s, turn=C["SNOW_FROM"] - 1, dice=[POOR])
                t.eq(s["lots"][0], "V", "Voss may stake a lot that snow closes tomorrow: tonight it is open")
                t.eq(s["snow"], 1, "and the snow still closes it for tomorrow")
                C["VOSS_FROM"] = 2
                s = t.fresh(hidden__ground=["R", "R", "R", "R", "R", "R"], hidden__flood=2, flooded=False, lots=["M"] * L)
                ev = t.advance(s, turn=2, dice=[RICH, RICH])
                t.eq(s["lots"], ["M"] * (L - 1) + ["V"], "on a flood night Voss stakes the lot the flood has just emptied")
                t.ok(ev.index(f"The creek flooded in the night: the ground slid two lots and your depot on lot {L} was washed out.") < ev.index(f"Voss Freight staked lot {L}: Rich ground."), "the flood comes before the stake")
            finally:
                C["VOSS_FROM"] = old_from
            t.eq(self.status_line(t.fresh(lots=["V", "", "", "", "", ""])).split(" | ")[3], "Street: 1V? 2.? 3.? 4.? 5.? 6.?", "Voss's lot shows as V")
            for n in range(1, C["TURNS"] + 1):
                s = t.fresh(flooded=True)
                ev = t.advance(s, turn=n, dice=[POOR])
                tomorrow_due = n + 1 >= C["VOSS_FROM"] and (n + 1 - C["VOSS_FROM"]) % C["VOSS_EVERY"] == 0 and n + 1 <= C["TURNS"]
                t.eq(any(e == f"Voss Freight will stake at dusk on night {n + 1}." for e in ev), tomorrow_due, f"the tell comes the night before a stake (night {n})")
            old_from, old_every = C["VOSS_FROM"], C["VOSS_EVERY"]
            try:
                C["VOSS_FROM"] = C["TURNS"]
                ev = t.advance(t.fresh(flooded=True), turn=C["TURNS"] - 1, dice=[POOR])
                t.has(ev, f"Voss Freight will stake at dusk on night {C['TURNS']}.")
                C["VOSS_FROM"] = C["TURNS"] + 1
                ev = t.advance(t.fresh(flooded=True), turn=C["TURNS"], dice=[POOR])
                t.ok(not any("will stake" in e for e in ev), "no tell for a night that is never played")
                C["VOSS_FROM"] = 3
                for n, want in ((1, 3), (2, 3), (3, 3), (4, 7), (7, 7), (8, 11), (11, 11)):
                    C["VOSS_EVERY"] = 4
                    t.eq(self._stake_night_from(n), want, f"the next stake night on or after night {n}")
                C["VOSS_EVERY"] = old_every
            finally:
                C["VOSS_FROM"] = old_from
                C["VOSS_EVERY"] = old_every
            v = self.visible(t.fresh())
            t.eq(v["voss_stakes_on_night"], C["VOSS_FROM"], "the next stake night is visible")
            s = t.fresh()
            s["_turn"] = C["TURNS"]
            t.eq(self.visible(s)["voss_stakes_on_night"], None, "no stake is left to come")

        def r7(t):
            for n in range(1, C["TURNS"] + 1):
                tomorrow = n + 1
                before = 0
                if tomorrow - 1 >= C["SNOW_FROM"]:
                    before = min(C["SNOW_MAX"], (tomorrow - 1 - C["SNOW_FROM"]) // C["SNOW_EVERY"] + 1)
                s = t.fresh(flooded=True, snow=before)
                t.advance(s, turn=n, dice=[POOR])
                want = before
                if tomorrow >= C["SNOW_FROM"] and (tomorrow - C["SNOW_FROM"]) % C["SNOW_EVERY"] == 0 and before < C["SNOW_MAX"]:
                    want = before + 1
                t.eq(s["snow"], want, f"snow after dusk of night {n} (the lots closed for night {tomorrow})")
            s = t.fresh(flooded=True)
            ev = t.advance(s, turn=C["SNOW_FROM"] - 1, dice=[POOR])
            t.has(ev, f"Snow closes lot 1 from night {C['SNOW_FROM']}.")
            t.ok("snow" in self._hits, "snow is noted")
            s = t.fresh(flooded=True, snow=1)
            ev = t.advance(s, turn=C["SNOW_FROM"] - 1 + C["SNOW_EVERY"], dice=[POOR])
            t.has(ev, f"Snow reaches lot 2 from night {C['SNOW_FROM'] + C['SNOW_EVERY']}.")
            s = t.fresh(flooded=True, snow=C["SNOW_MAX"])
            ev = t.advance(s, turn=C["SNOW_FROM"] - 1 + C["SNOW_EVERY"] * C["SNOW_MAX"], dice=[POOR])
            t.eq(s["snow"], C["SNOW_MAX"], "snow stops at SNOW_MAX")
            old = (C["SNOW_EVERY"], C["SNOW_MAX"])
            try:
                C["SNOW_EVERY"], C["SNOW_MAX"] = 1, L
                s = t.fresh(flooded=True, snow=2)
                t.advance(s, turn=C["TURNS"] - 1, dice=[POOR])
                t.eq(s["snow"], 3, "snow still falls for the last night")
                s = t.fresh(flooded=True, snow=2)
                t.advance(s, turn=C["TURNS"], dice=[POOR])
                t.eq(s["snow"], 2, "no snowfall is announced for a night that is never played")
            finally:
                C["SNOW_EVERY"], C["SNOW_MAX"] = old
            old = C["SNOW_EVERY"]
            try:
                C["SNOW_EVERY"] = 3
                for n, want in ((C["SNOW_FROM"] - 2, 0), (C["SNOW_FROM"] - 1, 1), (C["SNOW_FROM"], 0), (C["SNOW_FROM"] + 1, 0), (C["SNOW_FROM"] + 2, 1)):
                    s = t.fresh(flooded=True, snow=0)
                    t.advance(s, turn=n, dice=[POOR])
                    t.eq(s["snow"], want, f"with a gap of 3 nights, snow after dusk of night {n}")
            finally:
                C["SNOW_EVERY"] = old
            s = t.fresh(snow=C["SNOW_MAX"], lots=["M"] * L)
            t.eq(self.status_line(s).split(" | ")[2], "Open 3", "the first open lot counts as open")
            s = t.fresh(flooded=True, lots=["M"] + [""] * (L - 1), hidden__ground=["R"] + ["P"] * (L - 1), standing=0)
            t.advance(s, turn=C["SNOW_FROM"] - 1, dice=[POOR])
            t.eq((s["standing"], s["snow"]), (C["RICH_PAY"], 1), "a depot on the lot that closes tomorrow is still paid tonight")
            s = t.fresh(snow=1, lots=["M", "", "", "", "", ""])
            t.eq(self.status_line(s).split(" | ")[3], "Street: (1D?) 2.? 3.? 4.? 5.? 6.?", "a closed lot shows in brackets")
            t.eq(self.status_line(s).split(" | ")[1], "Snow 1", "the status shows the snow")
            top = C["SNOW_MAX"]
            s = t.fresh(standing=C["PLOUGH_COST"], snow=top)
            t.eq(t.label(s, "plough"), f"Plough lot {top} clear of snow for good ({C['PLOUGH_COST']} Standing)", "the plough label")
            ev = t.apply(s, "plough")
            t.eq((s["standing"], s["snow"], s["ploughed"]), (0, top - 1, 1), "the plough costs PLOUGH_COST and reopens the newest closed lot")
            t.has(ev, f"The plough gang cleared lot {top} (Standing -{C['PLOUGH_COST']}).")
            s = t.fresh(standing=C["PLOUGH_COST"], snow=top, lots=[""] * (top - 1) + ["M"] + [""] * (L - top), raised=[False] * (top - 1) + [True] + [False] * (L - top))
            t.apply(s, "plough")
            t.eq(s["raised"][top - 1], True, "a raised depot keeps its raise through the closing and the plough")
            t.eq(_open_count(self, s), 1, "and counts as open again")
            t.ok(t.offered(s, "scout", lot=top), "the ploughed lot can be scouted again")
            t.ok(not t.offered(s, "scout", lot=top - 1), "the lot before it is still closed")
            t.ok("plough" in self._hits, "ploughing is noted")
            late = C["SNOW_FROM"] - 1 + C["SNOW_EVERY"] * top
            t.advance(s, turn=late, dice=[POOR])
            t.eq(s["snow"], top - 1, "a ploughed lot stays open when the next snowfall night comes")
            s = t.fresh(standing=50, snow=top, ploughed=1)
            t.ok("plough" not in t.ids(s), "one plough only")
            s = t.fresh(standing=C["PLOUGH_COST"] - 1, snow=top)
            t.ok("plough" not in t.ids(s), "one short of the plough")
            s = t.fresh(standing=50, snow=top - 1)
            t.ok("plough" not in t.ids(s), "no plough until the snow has reached its last lot")
            s = t.fresh(standing=50, snow=0)
            t.ok("plough" not in t.ids(s), "nothing to plough without snow")

        def r8(t):
            need = C["INSPECT"]
            creek = [""] * (L - need) + ["M"] * need   # depots on the last INSPECT lots, which snow never closes
            s = t.fresh(snow=C["SNOW_MAX"], standing=C["LEVY"], lots=creek)
            end = self.final_check(s)
            t.eq(end["result"], "win", "exactly the Levy and exactly the inspection wins")
            t.eq(end["reason"], f"the Auditor signed: Standing {C['LEVY']} covers the Levy of {C['LEVY']} and {plural(need, 'open depot')} passed inspection", "the win reason")
            s = t.fresh(snow=C["SNOW_MAX"], standing=C["LEVY"] - 1, lots=creek)
            end = self.final_check(s)
            t.eq(end["result"], "loss", "one short of the Levy loses")
            t.eq(end["reason"], f"the Auditor found the books short: Standing {C['LEVY'] - 1} against a Levy of {C['LEVY']}", "the books-short reason")
            few = ["M"] * (L - 1) + ["V"]   # the last lot is Voss's: only INSPECT - 1 open depots stand beyond the snow
            s = t.fresh(snow=C["SNOW_MAX"], standing=C["LEVY"], lots=few)
            end = self.final_check(s)
            t.eq(end["result"], "loss", "closed depots and Voss's lots do not count as open")
            t.eq(end["reason"], f"the Auditor found too few open depots: {need - 1} where he needs {need}", "the inspection reason")
            s = t.fresh(snow=C["SNOW_MAX"], standing=C["LEVY"] - 1, lots=["M"] * (L - 2) + ["", ""])
            end = self.final_check(s)
            t.eq(end["reason"], f"the Auditor refused to sign: Standing {C['LEVY'] - 1} is short of the Levy of {C['LEVY']} and he counted {plural(1, 'open depot')} against the {need} he needs", "both fail")
            s = t.fresh(snow=C["SNOW_MAX"], standing=C["LEVY"] - 1, lots=["M"] * L)
            s["lots"][-need:] = [""] * need
            end = self.final_check(s)
            t.has([end["reason"]], "he counted 0 open depots against", "an empty creek is zero depots")
            s = t.fresh(snow=0, standing=C["LEVY"], lots=["M"] * need + [""] * (L - need))
            t.eq(self.final_check(s)["result"], "win", "with no snow every depot is open")
            s = t.fresh(snow=0, standing=C["LEVY"], lots=["M"] * (need - 1) + [""] * (L - need + 1))
            t.eq(self.final_check(s)["result"], "loss", "one depot too few is not enough")
            t.eq(self.turns, C["TURNS"], "the turn budget is TURNS")
            s = t.fresh(standing=C["LEVY"] - 1, lots=creek, snow=C["SNOW_MAX"], flooded=True)
            s["_turn"] = C["TURNS"]
            t.ok(self.check_end(s) is None, "the last night is still played")
            s["hidden"]["ground"] = ["P", "P", "P", "R", "R", "P"]
            s, ev = t.step(s, "scout", {"lot": C["SNOW_MAX"] + 1})
            t.ok(s["_ended"] and s["_ended"]["phase"] == "budget" and s["_turn"] == C["TURNS"] + 1, "the audit follows the last night's dusk")
            t.eq(s["_ended"]["result"], "win", "the last dusk's pay counts toward the Levy")
            s = t.fresh(standing=0, lots=BLANK, flooded=True)
            s["_turn"] = C["TURNS"]
            s, ev = t.step(s, "scout", {"lot": 1})
            t.eq(s["_ended"]["result"], "loss", "an empty street loses")

        return [
            (1, "the street and the night", r1), (2, "ground and pay", r2), (3, "the slide and the flood", r3),
            (4, "scout and file", r4), (5, "build, buy out, raise", r5), (6, "Voss stakes", r6),
            (7, "snow and plough", r7), (8, "the audit", r8),
        ]


if __name__ == "__main__":
    run(G)
