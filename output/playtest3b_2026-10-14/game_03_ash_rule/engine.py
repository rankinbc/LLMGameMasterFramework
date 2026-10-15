"""Ash Rule: an abbot in a nuclear-winter bunker network writes two-instruction Rules for a runner.

FORM 15 (programming): a turn is writing a short Rule, then watching the runner carry it out alone.
SET 22 (bunker network), ROLE 46 (abbot), LOOP 34 (visit a district, poll the result), CLOCK 1 (food runs out,
as a fixed upkeep), TWIST 2 (one faction is secretly on your side), WIN 9 (fully upgrade one bunker),
MAP 9 (a line of bunkers that slides every dusk), TONE 1 (grim and practical), CURRENCY 5 (stock).

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import sys

sys.path.insert(0, "C:/Users/Brian.Rankin/claude-workspace/projects/GM/engine")
from gm_base import Game, plural, run  # noqa: E402

FACS = ["Tillers", "Smelters", "Wardens"]
NAMES = [
    "Salt Row", "Kiln Hall", "Deep Pantry", "Pump Gallery", "Lamp Vault", "Cold Store",
    "Seed Annex", "Drum Cellar", "Rope Bay", "Tallow Cell", "Mill Shaft", "Brine Hold",
]


class G(Game):
    name = "Ash Rule"

    CONSTANTS = {
        "TURNS": 16,
        "LINE": 6,
        "PILE_MAX": 8,
        "CYCLES": 3,
        "TAKE_MAX": 2,
        "SWEEP_MAX": 1,
        "MID": 9,
        "RAISE_BASE": 4,
        "TIERS": 3,
        "TIER_REGROW": 1,
        "FINAL_NEED": 4,
        "FINAL_OFFER": 3,
        "REGROW_DIE": 3,
        "REGROW_CUT": 1,
        "EAT": 7,
        "START_STOCK": 17,
        "CAMP_EARLY": 1,
        "CAMP_LATE": 2,
        "ALLY_EXTRA": 1,
        "LEVER": 11,
        "FAVOUR": 10,
        "_PILE_LO": 2,
        "_PILE_HI": 5,
        "_RESERVE": 1,
        "_RAISE_DAY": 4,
        "_SLACK": 0,
        "_FAVOUR_EDGE": 2,
    }

    RULES = """
1. {LINE} bunkers stand in a line, each held by one faction, with a pile of goods up to {PILE_MAX}. At dusk each pile regrows by a d{REGROW_DIE} roll minus {REGROW_CUT}, and the line slides: the head bunker goes to the back.
2. Each day write a Rule, raise a bunker, keep a vigil or call a favour. A Rule is a first and a then instruction that your runner repeats {CYCLES} times from the head of the line, alone.
3. Take lifts up to {TAKE_MAX} here. Walk steps to the next bunker, stopping at the last. Sweep, unlocked on day {MID}, lifts up to {SWEEP_MAX} here and steps on. Lifted goods become stock.
4. Raise: pay {RAISE_BASE} stock times the new tier to lift one bunker a tier; the last tier, {TIERS}, needs a vigil instead. A raise costs the day's run. A raised bunker regrows {TIER_REGROW} more per tier and cannot be camped.
5. Vigil, for the last tier: roll d6 for {FINAL_NEED}+, one lower for each stock you add, up to {FINAL_OFFER}. A hit pays {RAISE_BASE} stock times {TIERS}. A miss loses only the added stock, and the day.
6. The Gleaners camp the bunkers you lifted most from, most first: {CAMP_EARLY} a dusk, {CAMP_LATE} from day {MID}. A camped bunker yields nothing for one day. A day with no lifts leaves no trail.
7. One faction is secretly your ally: its keepers add {ALLY_EXTRA} to every lift that finds goods. A bonus names it, as does getting none from every other faction. From day {LEVER} a known ally can send {FAVOUR} stock, once, instead of a run.
8. Goal: one bunker at tier {TIERS} within {TURNS} days. You start with {START_STOCK} stock; the brothers eat {EAT} each dusk, and stock below zero after that starves the cloister and loses.
"""

    ACTIONS = ["write", "raise", "vigil", "favour"]
    TAGS = [
        "unlock", "second_camp", "camp", "no_trail", "blocked", "dry", "end_of_line",
        "bonus", "ally_found", "elimination", "raise", "vigil_miss", "tier_max", "favour", "starve",
    ]
    TRACKED = ["stock", "line"]

    BOUNDS = {
        "stock": (-10, 200),
        "top_tier": (0, 3),
        "camps": (0, 6),
        "max_pile": (0, 8),
        "min_pile": (0, 8),
    }
    REACH = {
        "stock": ("<=", -1),
        "top_tier": 3,
        "camps": 2,
        "max_pile": 8,
        "min_pile": ("<=", 0),
    }
    DERIVED = {
        "top_tier": lambda g, s: max(b["tier"] for b in s["line"]),
        "camps": lambda g, s: sum(1 for b in s["line"] if b["camp"]),
        "max_pile": lambda g, s: max(b["pile"] for b in s["line"]),
        "min_pile": lambda g, s: min(b["pile"] for b in s["line"]),
    }
    GATES = {
        "write": {"_if": lambda g, s: True},
        "raise": {"_if": lambda g, s: bool(g._raise_choices(s))},
        "vigil": {"_if": lambda g, s: bool(g._vigil_choices(s))},
        "favour": {"_if": lambda g, s: g._favour_ready(s)},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    def _mk(self, piles, facs=None, tiers=None):
        """A line for rule tests: bunkers B1, B2, ... with the given piles."""
        n = len(piles)
        facs = facs or [0] * n
        tiers = tiers or [0] * n
        return [{"name": f"B{i + 1}", "fac": facs[i], "pile": piles[i], "tier": tiers[i], "camp": False} for i in range(n)]

    def _kinds(self, s):
        return ["take", "walk"] + (["sweep"] if s["_turn"] >= self.C["MID"] else [])

    def _raise_cost(self, b):
        return self.C["RAISE_BASE"] * (b["tier"] + 1)

    def _raise_choices(self, s):
        """Bunkers a plain raise can lift now: below the last step and affordable."""
        C = self.C
        return [b["name"] for b in s["line"] if b["tier"] < C["TIERS"] - 1 and s["stock"] >= self._raise_cost(b)]

    def _vigil_choices(self, s):
        """Bunkers one step from the top whose cost is covered."""
        C = self.C
        return [b["name"] for b in s["line"] if b["tier"] == C["TIERS"] - 1 and s["stock"] >= self._raise_cost(b)]

    def _favour_ready(self, s):
        return s["_turn"] >= self.C["LEVER"] and s["known"]["ally"] is not None and not s["favour_used"]

    def _run(self, line, first, then, ally, log=None):
        """Carry a Rule out on `line` (changes the piles in place; pass a copy to look ahead).
        Returns the stock brought home, what was lifted per bunker, and which factions did or did not add a bonus."""
        C = self.C
        last = len(line) - 1
        pos = 0
        gain = 0
        lifted = {}
        seen = {}
        for _ in range(C["CYCLES"]):
            for ins in (first, then):
                b = line[pos]
                got = 0
                bonus = 0
                why = ""
                if ins != "walk":
                    if b["camp"]:
                        why = "camp"
                    else:
                        cap = C["TAKE_MAX"] if ins == "take" else C["SWEEP_MAX"]
                        got = min(cap, b["pile"])
                        b["pile"] -= got
                        if got == 0:
                            why = "dry"
                        else:
                            lifted[pos] = lifted.get(pos, 0) + got
                            if b["fac"] == ally:
                                bonus = C["ALLY_EXTRA"]
                            seen[b["fac"]] = bonus > 0
                    gain += got + bonus
                end = False
                if ins != "take":
                    if pos < last:
                        pos += 1
                    else:
                        end = True
                if log is not None:
                    log.append({"ins": ins, "name": b["name"], "to": line[pos]["name"], "got": got, "bonus": bonus,
                                "why": why, "pile": b["pile"], "end": end})
        return {"gain": gain, "lifted": [[line[p]["name"], a] for p, a in sorted(lifted.items())], "seen": seen}

    def _learn(self, s, seen, ev):
        """Update what the player knows about the secret ally from the lifts that just happened."""
        k = s["known"]
        if k["ally"] is not None:
            return
        for f in sorted(seen):
            if seen[f]:
                k["ally"] = f
                self.hit("ally_found")
                ev.append(f"The {FACS[f]}' keepers add to your lift unasked: the {FACS[f]} are on your side.")
                return
        for f in sorted(seen):
            if f not in k["cleared"]:
                k["cleared"].append(f)
                ev.append(f"The {FACS[f]}' keepers add nothing: not your friends.")
        if len(k["cleared"]) == len(FACS) - 1:
            rest = [f for f in range(len(FACS)) if f not in k["cleared"]][0]
            k["ally"] = rest
            self.hit("elimination")
            ev.append(f"Every other faction is cleared, so the {FACS[rest]} must be on your side.")

    def _step_text(self, e):
        ins, name = e["ins"], e["name"]
        if ins == "walk":
            return f"walk: the line ends at {name}, the runner stays." if e["end"] else f"walk: on to {e['to']}."
        if e["why"] == "camp":
            text = f"{ins} at {name}: the Gleaners sit on it, nothing lifted."
        elif e["why"] == "dry":
            text = f"{ins} at {name}: the pile is empty."
        else:
            text = f"{ins} at {name}: lifted {e['got']}"
            if e["bonus"]:
                text += f" and the keeper adds {e['bonus']}"
            text += f", pile now {e['pile']}."
        if ins == "sweep":
            text += " The line ends, the runner stays." if e["end"] else f" On to {e['to']}."
        return text

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        n = C["LINE"]

        def r1(t):
            s = t.fresh()
            t.eq(len(s["line"]), n, "the line holds LINE bunkers")
            t.ok(all(0 <= b["pile"] <= C["PILE_MAX"] for b in s["line"]), "piles start within the cap")
            t.eq(len({b["name"] for b in s["line"]}), n, "bunker names are unique")
            t.eq(len({b["fac"] for b in s["line"]}), len(FACS), "every faction holds a bunker")
            t.ok(all(0 <= b["fac"] < len(FACS) for b in s["line"]), "each bunker is held by a faction")
            t.ok(all(b["tier"] == 0 and b["camp"] is False for b in s["line"]), "no bunker starts raised or camped")
            t.eq((s["known"], s["favour_used"], s["lifted"]), ({"ally": None, "cleared": []}, False, []), "nothing is known or used on day 1")
            starts, allies = set(), set()
            for sd in range(1, 61):
                f = t.fresh(seed=sd)
                starts |= {b["pile"] for b in f["line"]}
                allies.add(f["hidden"]["ally"])
            t.eq((min(starts), max(starts)), (C["_PILE_LO"], C["_PILE_HI"]), "starting piles span exactly their range")
            t.eq(sorted(allies), list(range(len(FACS))), "the secret ally can be any faction")
            s = t.fresh(line=self._mk(list(range(1, n + 1))))
            t.advance(s, turn=2, dice=[1] * n)
            want = [f"B{i}" for i in range(2, n + 1)] + ["B1"]
            t.eq([b["name"] for b in s["line"]], want, "the head bunker goes to the back")
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n))
            t.advance(s, turn=2, dice=[C["REGROW_DIE"]] * n)
            t.ok(all(b["pile"] == C["PILE_MAX"] for b in s["line"]), "a pile never passes the cap")
            s = t.fresh(line=self._mk([C["PILE_MAX"] - 1] * n))
            t.advance(s, turn=2, dice=[C["REGROW_CUT"] + 1] * n)
            t.ok(all(b["pile"] == C["PILE_MAX"] for b in s["line"]), "a pile may grow exactly to the cap")
            s = t.fresh(line=self._mk([C["PILE_MAX"] - 2] * n))
            t.advance(s, turn=2, dice=[C["REGROW_CUT"] + 1] * n)
            t.ok(all(b["pile"] == C["PILE_MAX"] - 1 for b in s["line"]), "a pile below the cap grows by the roll")
            dice = [(i % C["REGROW_DIE"]) + 1 for i in range(n)]
            s = t.fresh(line=self._mk([1] * n))
            ev = t.advance(s, turn=2, dice=dice)
            got = {b["name"]: b["pile"] for b in s["line"]}
            want = {f"B{i + 1}": 1 + dice[i] - C["REGROW_CUT"] for i in range(n)}
            t.eq(got, want, "each pile regrows by its own roll minus the cut")
            t.ok(any("roll" in e for e in ev), "the regrowth rolls are shown")

        def r2(t):
            s = t.fresh()
            ids = t.ids(s)
            t.ok("write" in ids and "raise" in ids, "on day 1 a Rule and a raise are both open")
            t.ok("favour" not in ids and "vigil" not in ids, "no favour or vigil on day 1")
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n), hidden__ally=1)
            t.ok(t.offered(s, "write", first="take", then="walk"), "any first and then pair is offered")
            t.ok(not t.offered(s, "write", first="dig", then="walk"), "only the named instructions exist")
            s2, ev = t.step(t.copy(s), "write", {"first": "take", "then": "walk"})
            t.eq(s2["_turn"], 2, "one action ends the day")
            t.eq(s2["stock"], C["START_STOCK"] + C["CYCLES"] * C["TAKE_MAX"] - C["EAT"], "the Rule ran its cycles, then the brothers ate")
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n), hidden__ally=1)
            t.apply(s, "write", {"first": "take", "then": "walk"})
            lifts = [C["PILE_MAX"] - b["pile"] for b in s["line"]]
            t.eq(lifts[:C["CYCLES"]], [C["TAKE_MAX"]] * C["CYCLES"], "the pair repeats on each next bunker")
            t.eq(sum(lifts[C["CYCLES"]:]), 0, "the runner never reaches farther than the Rule goes")
            s = t.fresh(stock=0, line=self._mk([1] * n))
            t.ok(t.ids(s) == ["write"], "with no stock only a Rule is possible")

        def r3(t):
            full = [C["PILE_MAX"]] * n
            s = t.fresh(line=self._mk(full), hidden__ally=1)
            t.apply(s, "write", {"first": "take", "then": "take"})
            t.eq(s["stock"], C["START_STOCK"] + min(C["PILE_MAX"], 2 * C["CYCLES"] * C["TAKE_MAX"]), "take lifts up to TAKE_MAX from the same pile each time")
            s = t.fresh(line=self._mk(full), hidden__ally=1)
            t.apply(s, "write", {"first": "walk", "then": "walk"})
            t.eq(s["stock"], C["START_STOCK"], "walk lifts nothing")
            t.eq([b["pile"] for b in s["line"]], full, "walk leaves every pile alone")
            s = t.fresh(line=self._mk([1, 0] + [C["PILE_MAX"]] * (n - 2)), hidden__ally=1)
            self._hits.clear()
            t.apply(s, "write", {"first": "take", "then": "walk"})
            t.eq(s["stock"], C["START_STOCK"] + 1 + (C["CYCLES"] - 2) * C["TAKE_MAX"], "take lifts only what a small pile holds")
            t.ok("dry" in self._hits, "a take on an empty pile is noted")
            s = t.fresh(line=self._mk(full), hidden__ally=1)
            s["_turn"] = C["MID"] - 1
            t.ok(not t.offered(s, "write", first="sweep", then="take"), "no sweep before its day")
            s["_turn"] = C["MID"]
            t.ok(t.offered(s, "write", first="sweep", then="take"), "sweep is offered from its day")
            t.apply(s, "write", {"first": "sweep", "then": "sweep"})
            reach = min(n, 2 * C["CYCLES"])
            t.eq(s["stock"], C["START_STOCK"] + reach * C["SWEEP_MAX"], "sweep lifts SWEEP_MAX here and steps on")
            t.eq([C["PILE_MAX"] - b["pile"] for b in s["line"]], [C["SWEEP_MAX"]] * reach + [0] * (n - reach), "one sweep per bunker down the line")
            s = t.fresh(line=self._mk(full)[:2], hidden__ally=1)
            s["_turn"] = C["MID"]
            self._hits.clear()
            t.apply(s, "write", {"first": "sweep", "then": "sweep"})
            t.eq(s["stock"], C["START_STOCK"] + 2 * C["CYCLES"] * C["SWEEP_MAX"], "at the end of the line the runner stays and keeps lifting")
            t.eq(s["line"][0]["pile"], C["PILE_MAX"] - C["SWEEP_MAX"], "the first bunker was swept once")
            t.ok("end_of_line" in self._hits, "reaching the end of the line is noted")
            s = t.fresh(line=self._mk(full), hidden__ally=1)
            s["line"][0]["tier"] = 1
            t.apply(s, "write", {"first": "take", "then": "walk"})
            t.eq(s["line"][0]["pile"], C["PILE_MAX"] - C["TAKE_MAX"], "a raised bunker is lifted from like any other")

        def r4(t):
            s = t.fresh(stock=C["RAISE_BASE"], line=self._mk([3] * n))
            t.ok(t.offered(s, "raise", bunker="B1"), "exactly enough stock is enough")
            s = t.fresh(stock=C["RAISE_BASE"] - 1, line=self._mk([3] * n))
            t.ok(not t.offered(s, "raise", bunker="B1"), "one stock short is not enough")
            s = t.fresh(stock=40, line=self._mk([3] * n), hidden__ally=1)
            self._hits.clear()
            s2, ev = t.step(t.copy(s), "raise", {"bunker": "B2"})
            t.eq({b["name"]: b["tier"] for b in s2["line"]}["B2"], 1, "the bunker gains a tier")
            t.eq(s2["stock"], 40 - C["RAISE_BASE"] - C["EAT"], "the first tier costs RAISE_BASE")
            t.eq(s2["_turn"], 2, "a raise takes the day")
            t.eq(s2["lifted"], [], "a raise day sends no runner")
            t.apply(s, "raise", {"bunker": "B2"})
            t.eq(s["stock"], 40 - C["RAISE_BASE"], "apply pays the cost")
            t.ok("raise" in self._hits, "a raise is noted")
            s["stock"] = 2 * C["RAISE_BASE"]
            t.ok(t.offered(s, "raise", bunker="B2"), "the second tier costs twice the base, and exactly that is enough")
            s["stock"] = 2 * C["RAISE_BASE"] - 1
            t.ok(not t.offered(s, "raise", bunker="B2"), "one short of the second tier is not enough")
            t.ok(t.offered(s, "raise", bunker="B1"), "another bunker still costs only the base")
            s["stock"] = 2 * C["RAISE_BASE"]
            t.apply(s, "raise", {"bunker": "B2"})
            t.eq((s["line"][1]["tier"], s["stock"]), (2, 0), "the second tier costs RAISE_BASE times 2")
            s = t.fresh(stock=100, line=self._mk([3] * n, tiers=[0, C["TIERS"] - 1] + [0] * (n - 2)))
            t.ok(not t.offered(s, "raise", bunker="B2"), "the last tier is not a plain raise")
            t.ok(t.offered(s, "raise", bunker="B1"), "other bunkers can still be raised")
            s = t.fresh(line=self._mk([3] * n, tiers=[0, 2] + [0] * (n - 2)))
            t.advance(s, turn=2, dice=[C["REGROW_CUT"] + 1] * n)
            piles = {b["name"]: b["pile"] for b in s["line"]}
            t.eq(piles["B1"], 3 + 1, "an unraised bunker regrows by the roll alone")
            t.eq(piles["B2"], 3 + 1 + 2 * C["TIER_REGROW"], "a raised bunker regrows TIER_REGROW more per tier")
            s = t.fresh(line=self._mk([3] * n, tiers=[0, 1] + [0] * (n - 2)))
            s["lifted"] = [["B1", 1], ["B2", 5]]
            t.advance(s, turn=2, dice=[1] * n)
            camped = sorted(b["name"] for b in s["line"] if b["camp"])
            t.eq(camped, ["B1"], "the Gleaners cannot camp a raised bunker")

        def r5(t):
            cost = C["RAISE_BASE"] * C["TIERS"]
            top = C["TIERS"] - 1
            tiers = [0, top] + [0] * (n - 2)
            s = t.fresh(stock=cost, line=self._mk([3] * n, tiers=tiers))
            t.ok(t.offered(s, "vigil", bunker="B2", offering=0), "exactly enough stock allows a vigil")
            t.ok(not t.offered(s, "vigil", bunker="B1", offering=0), "only a bunker one step from the top may keep a vigil")
            t.ok(not t.offered(s, "vigil", bunker="B2", offering=1), "no stock beyond the cost, nothing to add")
            s = t.fresh(stock=cost - 1, line=self._mk([3] * n, tiers=tiers))
            t.ok("vigil" not in t.ids(s), "one stock short of the cost, no vigil")
            s = t.fresh(stock=cost + 1, line=self._mk([3] * n, tiers=tiers))
            t.ok(t.offered(s, "vigil", bunker="B2", offering=1) and not t.offered(s, "vigil", bunker="B2", offering=2), "you can add only what you hold above the cost")
            s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
            t.ok(t.offered(s, "vigil", bunker="B2", offering=C["FINAL_OFFER"]), "you can add up to FINAL_OFFER")
            t.ok(not t.offered(s, "vigil", bunker="B2", offering=C["FINAL_OFFER"] + 1), "not more than FINAL_OFFER")
            self._hits.clear()
            t.apply(s, "vigil", {"bunker": "B2", "offering": 0}, dice=[C["FINAL_NEED"]])
            t.eq(s["stock"], 50, "a hit pays the cost")
            t.eq(s["line"][1]["tier"], C["TIERS"], "a hit lifts the last tier")
            t.ok("tier_max" in self._hits, "the top tier is noted")
            t.eq(self.check_end(s)["result"], "win", "the last tier wins")
            s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
            self._hits.clear()
            t.apply(s, "vigil", {"bunker": "B2", "offering": 0}, dice=[C["FINAL_NEED"] - 1])
            t.eq((s["stock"], s["line"][1]["tier"]), (cost + 50, top), "a miss with nothing added costs nothing")
            t.ok("vigil_miss" in self._hits, "a miss is noted")
            t.eq(s["lifted"], [], "a vigil day sends no runner")
            for k in range(1, C["FINAL_OFFER"] + 1):
                s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
                t.apply(s, "vigil", {"bunker": "B2", "offering": k}, dice=[C["FINAL_NEED"] - k])
                t.eq((s["stock"], s["line"][1]["tier"]), (50 - k, C["TIERS"]), "each stock added lowers the need by one, and a hit pays the cost")
                s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
                t.apply(s, "vigil", {"bunker": "B2", "offering": k}, dice=[C["FINAL_NEED"] - k - 1])
                t.eq((s["stock"], s["line"][1]["tier"]), (cost + 50 - k, top), "a miss loses only what was added")
            s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
            s2, ev = t.step(t.copy(s), "vigil", {"bunker": "B2", "offering": 0})
            t.ok(s2["_ended"] is not None or s2["_turn"] == 2, "a vigil takes the day")
            t.ok(any("roll" in e and "need" in e for e in ev), "the vigil roll is shown")
            wins = 0
            for sd in range(1, 301):
                s = t.fresh(stock=cost + 50, line=self._mk([3] * n, tiers=tiers))
                t.apply(s, "vigil", {"bunker": "B2", "offering": 0}, seed=sd)
                wins += s["line"][1]["tier"] == C["TIERS"]
            want = (6 - C["FINAL_NEED"] + 1) / 6
            t.ok(abs(wins / 300 - want) < 0.08, f"an unaided vigil should hit about {want:.0%} of the time, got {wins / 300:.0%}")

        def r6(t):
            base = self._mk([5] * n)
            s = t.fresh(line=t.copy(base))
            s["lifted"] = [["B1", 2], ["B3", 4], ["B4", 4]]
            self._hits.clear()
            t.advance(s, turn=C["MID"] - 1, dice=[1] * n)
            t.eq(sorted(b["name"] for b in s["line"] if b["camp"]), ["B3"], "one camp a dusk, on the most lifted, earlier bunker on a tie")
            t.ok("camp" in self._hits and "second_camp" not in self._hits, "the first camp is noted, not the second")
            s = t.fresh(line=t.copy(base))
            s["lifted"] = [["B1", 2], ["B3", 4], ["B4", 4]]
            self._hits.clear()
            t.advance(s, turn=C["MID"], dice=[1] * n)
            t.eq(sorted(b["name"] for b in s["line"] if b["camp"]), ["B3", "B4"], "from MID the Gleaners camp two")
            t.ok("second_camp" in self._hits and "unlock" in self._hits, "the midpoint is noted")
            s = t.fresh(line=t.copy(base))
            s["lifted"] = [["B1", 2]]
            t.advance(s, turn=C["MID"], dice=[1] * n)
            t.eq(sorted(b["name"] for b in s["line"] if b["camp"]), ["B1"], "they camp only what was lifted")
            s = t.fresh(line=t.copy(base))
            s["line"][1]["camp"] = True
            s["lifted"] = []
            self._hits.clear()
            t.advance(s, turn=2, dice=[1] * n)
            t.eq([b["camp"] for b in s["line"]], [False] * n, "a camp lasts one day, and no run leaves no trail")
            t.ok("no_trail" in self._hits, "no trail is noted")
            s = t.fresh(line=t.copy(base), hidden__ally=1)
            s["line"][0]["camp"] = True
            self._hits.clear()
            t.apply(s, "write", {"first": "take", "then": "take"})
            t.eq(s["stock"], C["START_STOCK"], "a camped bunker yields nothing")
            t.eq(s["line"][0]["pile"], 5, "and loses nothing")
            t.eq(s["lifted"], [], "nothing lifted, nothing to follow")
            t.ok("blocked" in self._hits, "a blocked lift is noted")
            s = t.fresh(line=t.copy(base), hidden__ally=1)
            s["lifted"] = []
            t.apply(s, "write", {"first": "take", "then": "walk"})
            t.eq(s["lifted"], [["B1", C["TAKE_MAX"]], ["B2", C["TAKE_MAX"]], ["B3", C["TAKE_MAX"]]][:C["CYCLES"]], "the lifts are recorded for the Gleaners")

        def r7(t):
            facs = [0, 1, 2, 0, 1, 2]
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n, facs=facs), hidden__ally=1)
            self._hits.clear()
            ev = t.apply(s, "write", {"first": "take", "then": "walk"})
            t.eq(s["stock"], C["START_STOCK"] + C["CYCLES"] * C["TAKE_MAX"] + C["ALLY_EXTRA"], "the ally's keeper adds ALLY_EXTRA to the one lift there")
            t.eq(s["known"]["ally"], 1, "a bonus names the ally")
            t.ok("ally_found" in self._hits and "bonus" in self._hits, "the find is noted")
            s = t.fresh(line=self._mk([0] + [C["PILE_MAX"]] * (n - 1), facs=[1, 0, 0, 0, 0, 0]), hidden__ally=1)
            t.apply(s, "write", {"first": "take", "then": "take"})
            t.eq(s["stock"], C["START_STOCK"], "a lift that finds nothing gets no bonus")
            t.eq(s["known"]["ally"], None, "and teaches nothing")
            t.eq(s["known"]["cleared"], [], "an empty lift clears no one")
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n, facs=[0, 1, 0, 1, 2, 2]), hidden__ally=2)
            self._hits.clear()
            t.apply(s, "write", {"first": "take", "then": "walk"})
            t.eq(s["stock"], C["START_STOCK"] + C["CYCLES"] * C["TAKE_MAX"], "no ally lifted, no bonus yet")
            t.eq(sorted(s["known"]["cleared"]), [0, 1], "factions lifted from with no bonus are cleared")
            t.eq(s["known"]["ally"], 2, "two cleared factions leave the last one as the ally")
            t.ok("elimination" in self._hits and "ally_found" not in self._hits, "elimination is noted when it happens")
            s = t.fresh(line=self._mk([C["PILE_MAX"]] * n, facs=[0, 0, 0, 1, 1, 1]), hidden__ally=2)
            t.apply(s, "write", {"first": "take", "then": "take"})
            t.eq(s["known"]["cleared"], [0], "the same faction is cleared once")
            t.eq(s["known"]["ally"], None, "one cleared faction is not enough")
            s = t.fresh(hidden__ally=2)
            s["known"]["cleared"] = [0]
            rng = t.rng(seed=3, choices=[1])
            self.resample_hidden(s, rng)
            t.eq(s["hidden"]["ally"], 1, "a redraw avoids cleared factions")
            s["known"]["ally"] = 2
            self.resample_hidden(s, t.rng(seed=3, choices=[1]))
            t.eq(s["hidden"]["ally"], 2, "a redraw keeps a known ally")
            s = t.fresh()
            s["known"]["ally"] = 1
            s["_turn"] = C["LEVER"] - 1
            t.ok(not t.offered(s, "favour"), "no favour before its day")
            s["_turn"] = C["LEVER"]
            t.ok(t.offered(s, "favour"), "a known ally can send a favour from its day")
            s["known"]["ally"] = None
            t.ok(not t.offered(s, "favour"), "an unknown ally sends nothing")
            s["known"]["ally"] = 1
            self._hits.clear()
            s2, ev = t.step(t.copy(s), "favour")
            t.eq(s2["stock"], C["START_STOCK"] + C["FAVOUR"] - C["EAT"], "the favour brings FAVOUR stock")
            t.eq(s2["_turn"], C["LEVER"] + 1, "the favour takes the day")
            t.ok("favour" in self._hits, "the favour is noted")
            t.ok(not t.offered(s2, "favour"), "the favour comes once")
            t.eq(s2["lifted"], [], "a favour day leaves no trail")

        def r8(t):
            s = t.fresh()
            t.eq(s["stock"], C["START_STOCK"], "start stock")
            t.eq(self.turns, C["TURNS"], "the budget is TURNS days")
            s = t.fresh(line=self._mk([3] * n, tiers=[C["TIERS"]] + [0] * (n - 1)))
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "a bunker at the top tier wins")
            s = t.fresh(line=self._mk([3] * n, tiers=[C["TIERS"] - 1] + [0] * (n - 1)))
            s["_turn"] = C["TURNS"]
            t.eq(self.check_end(s), None, "the last day is still played")
            s["_turn"] = C["TURNS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "short of the top tier after the last day is a loss")
            s = t.fresh(stock=C["EAT"])
            t.advance(s, turn=2, dice=[2] * n)
            t.eq(s["stock"], 0, "the brothers eat EAT stock")
            t.eq(self.check_end(s), None, "exactly zero stock is still alive")
            s = t.fresh(stock=C["EAT"] - 1)
            self._hits.clear()
            t.advance(s, turn=2, dice=[2] * n)
            t.eq(s["stock"], -1, "one short of the meal")
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "stock below zero is a loss")
            t.ok("starve" in self._hits, "starvation is noted")

        return [
            (1, "the line", r1), (2, "one action a day", r2), (3, "instructions", r3), (4, "raise", r4),
            (5, "vigil", r5), (6, "the Gleaners", r6), (7, "the secret ally", r7), (8, "goal and meals", r8),
        ]

    # ------------------------------------------------------------ the game

    def resample_hidden(self, s, rng):
        """The ally is hidden until a bonus or elimination names it; before that, redraw among factions not yet cleared."""
        k = s["known"]
        if k["ally"] is not None:
            s["hidden"]["ally"] = k["ally"]
            return
        cand = [f for f in range(len(FACS)) if f not in k["cleared"]]
        s["hidden"]["ally"] = rng.choice(cand)

    def init_state(self, rng):
        C = self.C
        names = rng.shuffle(list(NAMES))
        facs = rng.shuffle([i % len(FACS) for i in range(C["LINE"])])
        span = C["_PILE_HI"] - C["_PILE_LO"] + 1
        line = []
        for i in range(C["LINE"]):
            line.append({"name": names[i], "fac": facs[i], "pile": C["_PILE_LO"] - 1 + rng.d(span), "tier": 0, "camp": False})
        return {
            "stock": C["START_STOCK"],
            "line": line,
            "known": {"ally": None, "cleared": []},
            "favour_used": False,
            "lifted": [],
            "hidden": {"ally": rng.d(len(FACS)) - 1},
        }

    def options(self, s):
        C = self.C
        kinds = self._kinds(s)
        o = [{
            "id": "write",
            "label": f"Write a Rule: a first and a then instruction ({', '.join(kinds)}), run {plural(C['CYCLES'], 'time')} by the runner",
            "args": {},
            "params": {"first": {"choices": list(kinds)}, "then": {"choices": list(kinds)}},
        }]
        ok = self._raise_choices(s)
        if ok:
            o.append({
                "id": "raise",
                "label": f"Raise a bunker one tier (pay {C['RAISE_BASE']} stock times its new tier; no run today)",
                "args": {},
                "params": {"bunker": {"choices": ok}},
            })
        vg = self._vigil_choices(s)
        if vg:
            cost = C["RAISE_BASE"] * C["TIERS"]
            top = min(C["FINAL_OFFER"], s["stock"] - cost)
            o.append({
                "id": "vigil",
                "label": f"Keep the vigil for the last tier (roll {C['FINAL_NEED']}+, add stock to lower the need; a hit pays {cost}; no run today)",
                "args": {},
                "params": {"bunker": {"choices": vg}, "offering": {"min": 0, "max": top}},
            })
        if self._favour_ready(s):
            o.append({
                "id": "favour",
                "label": f"Call the favour: {C['FAVOUR']} stock from your ally, once (no run today)",
                "args": {},
            })
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "write":
            first, then = args["first"], args["then"]
            ev.append(f"Rule written: {first}, then {then}, run {plural(C['CYCLES'], 'time')}. The runner goes out alone.")
            log = []
            res = self._run(s["line"], first, then, s["hidden"]["ally"], log)
            for e in log:
                ev.append(self._step_text(e))
                if e["why"] == "camp":
                    self.hit("blocked")
                elif e["why"] == "dry":
                    self.hit("dry")
                if e["bonus"]:
                    self.hit("bonus")
                if e["end"]:
                    self.hit("end_of_line")
            s["stock"] += res["gain"]
            s["lifted"] = res["lifted"]
            ev.append(f"The runner comes home with {res['gain']} stock.")
            self._learn(s, res["seen"], ev)
        elif a == "raise":
            b = next(x for x in s["line"] if x["name"] == args["bunker"])
            cost = self._raise_cost(b)
            s["stock"] -= cost
            b["tier"] += 1
            s["lifted"] = []
            self.hit("raise")
            ev.append(f"{b['name']} is raised to tier {b['tier']} for {cost} stock.")
        elif a == "vigil":
            b = next(x for x in s["line"] if x["name"] == args["bunker"])
            cost = self._raise_cost(b)
            add = args["offering"]
            s["stock"] -= add
            s["lifted"] = []
            ok, text = rng.check(C["FINAL_NEED"] - add, 6, "vigil")
            if ok:
                s["stock"] -= cost
                b["tier"] += 1
                self.hit("tier_max")
                ev.append(f"Vigil at {b['name']}, {add} added: {text}. The last tier is raised for {cost} stock.")
            else:
                self.hit("vigil_miss")
                ev.append(f"Vigil at {b['name']}, {add} added: {text}. The added stock is lost.")
        elif a == "favour":
            s["favour_used"] = True
            s["stock"] += C["FAVOUR"]
            s["lifted"] = []
            self.hit("favour")
            ev.append(f"The {FACS[s['known']['ally']]} send a favour: {C['FAVOUR']} stock.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        line = s["line"]
        s["stock"] -= C["EAT"]
        ev.append(f"Dusk: the brothers eat {C['EAT']} stock.")
        if s["stock"] < 0:
            self.hit("starve")
            ev.append("The larder is empty. The cloister starves.")
        # the Gleaners follow the runner's trail
        for b in line:
            b["camp"] = False
        slots = C["CAMP_LATE"] if s["_turn"] >= C["MID"] else C["CAMP_EARLY"]
        where = {b["name"]: i for i, b in enumerate(line)}
        trail = sorted((-amt, where[name]) for name, amt in s["lifted"] if amt > 0 and line[where[name]]["tier"] == 0)
        chosen = [i for _, i in trail[:slots]]
        for i in chosen:
            line[i]["camp"] = True
            self.hit("camp")
            ev.append(f"The Gleaners camp {line[i]['name']}; it will yield nothing tomorrow.")
        if len(chosen) > C["CAMP_EARLY"]:
            self.hit("second_camp")
        if not chosen:
            self.hit("no_trail")
            ev.append("The Gleaners find no trail to follow.")
        # regrowth
        parts = []
        for b in line:
            d = rng.d(C["REGROW_DIE"])
            grown = min(C["PILE_MAX"], b["pile"] + d - C["REGROW_CUT"] + C["TIER_REGROW"] * b["tier"])
            parts.append(f"{b['name']} roll {d} (+{grown - b['pile']})")
            b["pile"] = grown
        ev.append("Piles regrow: " + ", ".join(parts) + ".")
        # the line slides
        head = line.pop(0)
        line.append(head)
        ev.append(f"The line slides: {head['name']} goes to the back.")
        s["lifted"] = []
        if s["_turn"] == C["MID"]:
            self.hit("unlock")
            ev.append(f"Day {C['MID']}: the deep hatch opens, so sweep joins your instructions, and a second Gleaner crew arrives.")
        return ev

    def status_line(self, s):
        top = max(b["tier"] for b in s["line"])
        piles = " ".join((f"[{b['pile']}]" if b["camp"] else str(b["pile"])) for b in s["line"])
        return f"Stock {s['stock']} | Tier {top}/{self.C['TIERS']} | Line {piles}"

    def visible(self, s):
        k = s["known"]
        return {
            "stock": s["stock"],
            "line": [
                {"pos": i + 1, "name": b["name"], "faction": FACS[b["fac"]], "pile": b["pile"], "tier": b["tier"], "camped": b["camp"]}
                for i, b in enumerate(s["line"])
            ],
            "ally": None if k["ally"] is None else FACS[k["ally"]],
            "cleared": [FACS[f] for f in k["cleared"]],
            "favour_used": s["favour_used"],
        }

    def check_end(self, s):
        C = self.C
        for b in s["line"]:
            if b["tier"] >= C["TIERS"]:
                return {"result": "win", "reason": f"{b['name']} stands at tier {b['tier']}"}
        if s["stock"] < 0:
            return {"result": "loss", "reason": "the larder ran dry and the cloister starved"}
        if s["_turn"] > self.turns:
            return {"result": "loss", "reason": f"the days ran out with no bunker at tier {C['TIERS']}"}
        return None

    def _best_rule(self, s):
        """The Rule that brings the most stock home on today's line, as far as the player can tell."""
        ally = s["known"]["ally"]
        kinds = self._kinds(s)
        best = None
        for f in kinds:
            for th in kinds:
                line = [dict(b) for b in s["line"]]
                res = self._run(line, f, th, ally)
                if best is None or res["gain"] > best[0]:
                    best = (res["gain"], f, th)
        return best

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        if "vigil" in ids:
            o = next(x for x in options if x["id"] == "vigil")
            return {"id": "vigil", "args": {"bunker": o["params"]["bunker"]["choices"][0], "offering": o["params"]["offering"]["max"]}}
        gain, first, then = self._best_rule(s)
        if "favour" in ids and gain <= C["FAVOUR"] - C["_FAVOUR_EDGE"]:
            return "favour"
        if "raise" in ids:
            names = next(o for o in options if o["id"] == "raise")["params"]["bunker"]["choices"]
            top = max(b["tier"] for b in s["line"])
            ally = s["known"]["ally"]
            pick = None
            if top > 0:
                tgt = max(s["line"], key=lambda b: b["tier"])
                if tgt["name"] in names:
                    pick = tgt
            else:
                cands = [b for b in s["line"] if b["name"] in names and (ally is None or b["fac"] == ally)]
                if cands:
                    pick = max(cands, key=lambda b: b["pile"])
            if pick is not None:
                days_left = self.turns - s["_turn"] + 1
                need = C["TIERS"] - top
                safe = s["stock"] - self._raise_cost(pick) >= C["EAT"] * C["_RESERVE"]
                if days_left <= need + C["_SLACK"] or (safe and (ally is not None or s["_turn"] >= C["_RAISE_DAY"])):
                    return {"id": "raise", "args": {"bunker": pick["name"]}}
        return {"id": "write", "args": {"first": first, "then": then}}


if __name__ == "__main__":
    run(G)
