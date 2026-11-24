"""The Bee Tithe: a mythic trading run over a farming valley under a slow front.

You are the last Beekeeper of Orrin Vale. Your bees store sunlight. You carry it from steading to
steading, paying the tithe that keeps six families calm, while a storm front hunts the sunny fields.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, run  # noqa: E402


class G(Game):
    name = "The Bee Tithe"

    CONSTANTS = {
        "TURNS": 16,
        "RING": 6,
        "STEADINGS": "Orchard, Barley, Mill, Vine, Fen, Hearth",
        "WALK": 1,
        "START_LIGHT": 8,
        "LIGHT_CAP": 14,
        "SUN_MAX": 4,
        "GATHER_MIN": 1,
        "GIFT_MIN": 1,
        "GIFT_MAX": 3,
        "MOOD_MAX": 8,
        "BRIGHT_AT": 3,
        "DARK_AT": 0,
        "RATE_BRIGHT": 1,
        "RATE_DIM": 2,
        "RATE_DARK": 3,
        "BLESS_START": 4,
        "BLESS_STEP": 2,
        "BLESS_EVERY": 4,
        "GOLDEN_FROM": 15,
        "GOLDEN_MULT": 2,
        "UNREST_SUN": 0,
        "UNREST_LOSS": 1,
        "RIOT_AT": 3,
        "FRONT_DROP": 2,
        "RECENT": 3,
        "STORM_TURN": 9,
        "FAVOR_TURN": 8,
        "FAVOR_AT": 4,
        "FAVOR_COST": 2,
        "FAVOR_GAIN": 8,
        "START_MOOD": 1,
        "GOAL": 40,
        "_START_AT": 5,
        "_LW": 0.8,
        "_MW0": 0.8,
        "_DRIFT_UP": 0.6,
        "_DRIFT_DOWN": 0.2,
    }

    RULES = """
1. {RING} steadings ring the valley: {STEADINGS}. Each turn you walk to one (cost {WALK} light per step round the ring) and do one thing there. You start at Hearth with {START_LIGHT} light, and you can hold {LIGHT_CAP}.
2. Gather: your bees there make light equal to its sun, but never less than {GATHER_MIN}. Every steading has a sun from 0 to {SUN_MAX}, shown on the status line.
3. Gift {GIFT_MIN} to {GIFT_MAX} light: that steading's mood rises by gifts x rate. The rate is {RATE_BRIGHT} at sun {BRIGHT_AT} or more, {RATE_DARK} at sun {DARK_AT}, otherwise {RATE_DIM}. Mood tops out at {MOOD_MAX}.
4. Your blessing adds +{BLESS_START} mood to every gift, losing {BLESS_STEP} every {BLESS_EVERY} turns. From turn {GOLDEN_FROM} (the Golden Hour) every gift counts x{GOLDEN_MULT}.
5. At dusk, a steading you did not visit loses {UNREST_LOSS} mood if its sun is {UNREST_SUN} or less. Any mood at -{RIOT_AT} or lower is a riot: you lose.
6. Each dusk the front cuts the sun of one steading by {FRONT_DROP} (two steadings from turn {STORM_TURN}) and you see where it fell only afterward. It hunts either the sunniest steading or the one you visited most in the last {RECENT} turns, and you are not told which. Other suns drift.
7. From turn {FAVOR_TURN}, a steading at mood {FAVOR_AT} or more will pay a favor, once: its mood falls {FAVOR_COST} and you gain {FAVOR_GAIN} light.
8. Every steading starts at mood {START_MOOD}. The Harvest Count comes right after your action on turn {TURNS}: total mood (approval) of {GOAL} or more wins, anything less loses.
"""

    ACTIONS = ["gather", "gift", "favor"]
    TAGS = ["front_sunny", "front_crowd", "storm", "favor", "golden", "overflow", "unrest",
            "dark_gift", "bless_fade", "near_riot", "ceiling"]

    @property
    def BOUNDS(self):
        C = self.C
        return {
            "light": (0, C["LIGHT_CAP"]),
            "approval": (C["RING"] * -(C["RIOT_AT"] + C["UNREST_LOSS"]), C["RING"] * C["MOOD_MAX"]),
            "low": (-(C["RIOT_AT"] + C["UNREST_LOSS"]), C["MOOD_MAX"]),
            "at": (0, C["RING"] - 1),
            "visited": (-1, C["RING"] - 1),
            "favors": (0, C["RING"]),
        }

    @property
    def REACH(self):
        C = self.C
        return {
            "approval": C["GOAL"],
            "low": ("<=", -C["RIOT_AT"]),
            "light": C["LIGHT_CAP"],
            "favors": 1,
        }

    GATES = {
        "gift": {"light": "GIFT_MIN"},
        "favor": {"_turn": "FAVOR_TURN", "_if": lambda g, s: g._favor_targets(s) != []},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    @property
    def names(self):
        return self.C["STEADINGS"].split(", ")

    def dist(self, a, b):
        n = self.C["RING"]
        d = abs(a - b)
        return min(d, n - d)

    def rate(self, sun):
        C = self.C
        if sun >= C["BRIGHT_AT"]:
            return C["RATE_BRIGHT"]
        if sun <= C["DARK_AT"]:
            return C["RATE_DARK"]
        return C["RATE_DIM"]

    def yield_at(self, sun):
        return max(self.C["GATHER_MIN"], sun)

    def blessing(self, turn):
        C = self.C
        return max(0, C["BLESS_START"] - C["BLESS_STEP"] * ((turn - 1) // C["BLESS_EVERY"]))

    def gift_gain(self, s, d, n, turn=None):
        C = self.C
        t = s["_turn"] if turn is None else turn
        gain = n * self.rate(s["sun"][d]) + self.blessing(t)
        if t >= C["GOLDEN_FROM"]:
            gain *= C["GOLDEN_MULT"]
        return gain

    def gift_eff(self, s, d, n):
        """What the gift really adds, after the mood ceiling."""
        return min(self.gift_gain(s, d, n), self.C["MOOD_MAX"] - s["mood"][d])

    def _sync(self, s):
        s["approval"] = sum(s["mood"])
        s["low"] = min(s["mood"])

    def _favor_targets(self, s):
        C = self.C
        if s["_turn"] < C["FAVOR_TURN"]:
            return []
        out = []
        for d in range(C["RING"]):
            if s["mood"][d] >= C["FAVOR_AT"] and not s["favored"][d] and s["light"] >= self.dist(s["at"], d) * C["WALK"]:
                out.append(d)
        return out

    def has_option(self, s, aid, **args):
        """Exact membership test (the harness's t.offered returns True for a lone same-id option whatever its args)."""
        return any(o["id"] == aid and all(o["args"].get(k) == v for k, v in args.items()) for o in self.options(s))

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        names = self.names

        def r1(t):
            s = t.fresh()
            t.eq(s["at"], 5, "you start at Hearth")
            t.eq(names[s["at"]], "Hearth", "the last steading is Hearth")
            t.eq(s["light"], C["START_LIGHT"], "start light")
            t.eq(len(s["mood"]), C["RING"], "one mood per steading")
            s = t.fresh(light=10, at=5)
            far = max(range(C["RING"]), key=lambda d: self.dist(5, d))
            w = self.dist(5, far) * C["WALK"]
            t.ok(w >= 1, "some steading is a walk away")
            s["sun"][far] = 2
            t.apply(s, "gather", {"d": far})
            t.eq(s["light"], 10 - w + 2, "the walk is paid in light")
            t.eq(s["at"], far, "you end the walk at the steading")
            s = t.fresh(light=w - 1, at=5)
            t.ok(not self.has_option(s, "gather", d=far), "a walk you cannot pay is not offered")
            s = t.fresh(light=10, at=5)
            s2, _ = t.step(s, "gather", {"d": 5})
            t.eq(s2["_turn"], 2, "one action ends the turn")

        def r2(t):
            s = t.fresh(light=3, at=0, sun=[4, 1, 1, 1, 1, 1])
            t.apply(s, "gather", {"d": 0})
            t.eq(s["light"], 3 + 4, "gather makes light equal to the sun")
            s = t.fresh(light=C["LIGHT_CAP"] - 1, at=0, sun=[4, 1, 1, 1, 1, 1])
            t.apply(s, "gather", {"d": 0})
            t.eq(s["light"], C["LIGHT_CAP"], "light stops at the cap")
            s = t.fresh(light=3, at=0, sun=[0, 1, 1, 1, 1, 1])
            t.apply(s, "gather", {"d": 0})
            t.eq(s["light"], 3 + C["GATHER_MIN"], "sun 0 still gives the minimum")

        def r3(t):
            for sun, want in ((C["SUN_MAX"], C["RATE_BRIGHT"]), (C["BRIGHT_AT"], C["RATE_BRIGHT"]),
                              (C["BRIGHT_AT"] - 1, C["RATE_DIM"]), (C["DARK_AT"] + 1, C["RATE_DIM"]),
                              (C["DARK_AT"], C["RATE_DARK"])):
                s = t.fresh(light=10, at=2, sun=[sun] * C["RING"])
                s["_turn"] = 2 * C["BLESS_EVERY"] + 1  # blessing gone, not golden
                m0 = s["mood"][2]
                t.apply(s, "gift", {"d": 2, "n": 2})
                t.eq(s["mood"][2] - m0, 2 * want, f"rate at sun {sun}")
                t.eq(s["light"], 10 - 2, "the gift costs its light")
            s = t.fresh(light=10, at=2, sun=[C["DARK_AT"]] * C["RING"], mood=[C["MOOD_MAX"] - 1] * C["RING"])
            s["_turn"] = 2 * C["BLESS_EVERY"] + 1
            t.apply(s, "gift", {"d": 2, "n": 2})
            t.eq(s["mood"][2], C["MOOD_MAX"], "mood tops out at the ceiling")
            s = t.fresh(light=C["GIFT_MAX"], at=2)
            t.ok(self.has_option(s, "gift", d=2, n=C["GIFT_MAX"]), "the largest gift is offered")
            t.ok(not self.has_option(s, "gift", d=2, n=C["GIFT_MAX"] + 1), "nothing above the largest gift")
            s = t.fresh(light=0, at=2)
            t.ok(not self.has_option(s, "gift", d=2, n=1), "no light, no gift")

        def r4(t):
            def gain_at(turn):
                s = t.fresh(light=10, at=0, sun=[C["SUN_MAX"]] * C["RING"])
                s["_turn"] = turn
                m0 = s["mood"][0]
                t.apply(s, "gift", {"d": 0, "n": 1})
                return s["mood"][0] - m0
            e = C["BLESS_EVERY"]
            t.eq(gain_at(1), C["RATE_BRIGHT"] + C["BLESS_START"], "blessing at the start")
            t.eq(gain_at(e), C["RATE_BRIGHT"] + C["BLESS_START"], "blessing holds to the end of its first span")
            t.eq(gain_at(e + 1), C["RATE_BRIGHT"] + C["BLESS_START"] - C["BLESS_STEP"], "blessing fades by one step")
            t.eq(gain_at(2 * e + 1), C["RATE_BRIGHT"] + max(0, C["BLESS_START"] - 2 * C["BLESS_STEP"]), "and again")
            g = C["GOLDEN_FROM"]
            t.eq(gain_at(g - 1), C["RATE_BRIGHT"] + self.blessing(g - 1), "no doubling before the Golden Hour")
            t.eq(gain_at(g), (C["RATE_BRIGHT"] + self.blessing(g)) * C["GOLDEN_MULT"], "the Golden Hour doubles gifts")
            t.eq(gain_at(C["TURNS"]), (C["RATE_BRIGHT"] + self.blessing(C["TURNS"])) * C["GOLDEN_MULT"], "and holds to the last turn")

        def r5(t):
            sun = [C["UNREST_SUN"], C["UNREST_SUN"] + 1, C["UNREST_SUN"], C["SUN_MAX"], 0, C["UNREST_SUN"]]
            s = t.fresh(sun=sun, visited=2, mood=[0] * C["RING"])
            t.advance(s, turn=3)
            t.eq(s["mood"][0], -C["UNREST_LOSS"], "an ignored dim steading loses mood")
            t.eq(s["mood"][1], 0, "a bright enough steading does not")
            t.eq(s["mood"][2], 0, "a visited dim steading does not")
            t.eq(s["mood"][3], 0, "a sunny steading does not")
            t.eq(s["mood"][4], -C["UNREST_LOSS"], "sun 0 is below the line")
            t.eq(s["approval"], sum(s["mood"]), "approval follows the moods")
            s = t.fresh(mood=[C["START_MOOD"]] * C["RING"])
            s["mood"][3] = -C["RIOT_AT"] + 1
            self._sync(s)
            t.ok(self.check_end(s) is None, "one above the riot line is still alive")
            s["mood"][3] = -C["RIOT_AT"]
            self._sync(s)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "mood at the riot line is a loss")
            s = t.fresh(sun=[C["UNREST_SUN"]] * C["RING"], visited=0, mood=[-C["RIOT_AT"] + C["UNREST_LOSS"]] * C["RING"])
            t.advance(s, turn=3)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "dusk unrest can tip a steading into riot")

        def r6(t):
            ring = C["RING"]
            s = t.fresh(sun=[1, 4, 2, 4, 0, 3], visited=0, hidden__temper=0, recent=[0, 0, 0])
            ev = t.advance(s, turn=3)
            t.eq(s["sun"][1], 4 - C["FRONT_DROP"], "the front cuts the sunniest, first in ring order on a tie")
            t.has(ev, "fell on", "the strike is shown")
            s = t.fresh(sun=[1, 4, 2, 4, 0, 3], visited=0, hidden__temper=0, recent=[0, 0, 0])
            before = s["sun"][3]
            t.advance(s, turn=C["STORM_TURN"])
            t.ok(abs(s["sun"][3] - before) < C["FRONT_DROP"], "before the storm only one steading is struck")
            s = t.fresh(sun=[1, 4, 2, 4, 0, 3], visited=0, hidden__temper=0, recent=[0, 0, 0])
            t.advance(s, turn=C["STORM_TURN"] + 1)
            t.eq(s["sun"][1], 4 - C["FRONT_DROP"], "from the storm turn: first strike")
            t.eq(s["sun"][3], 4 - C["FRONT_DROP"], "from the storm turn: a second strike")
            s = t.fresh(sun=[1, 4, 2, 4, 0, 3], visited=3, hidden__temper=1, recent=[3, 3, 1])
            t.advance(s, turn=3)
            t.eq(s["sun"][3], 4 - C["FRONT_DROP"], "temper 2 hunts the steading visited most lately")
            s = t.fresh(sun=[1, 1, 2, 0, 0, 3], visited=3, hidden__temper=1, recent=[3, 3, 1])
            t.advance(s, turn=3)
            t.eq(s["sun"][3], 0, "a strike cannot take the sun below zero")
            s = t.fresh(sun=[1, 4, 2, 4, 0, 3], hidden__temper=0)
            s2, _ = t.step(s, "gather", {"d": 5})
            t.eq(len(s2["recent"]), 1, "visits are remembered")
            for _ in range(C["RECENT"] + 2):
                s2["_ended"] = None
                s2, _ = t.step(s2, "gather", {"d": s2["at"]})
            t.eq(len(s2["recent"]), C["RECENT"], "only the last few turns are remembered")
            s = t.fresh(sun=[2] * ring, visited=0, hidden__temper=0, recent=[0])
            ev = t.advance(s, turn=3)
            t.ok(all(0 <= x <= C["SUN_MAX"] for x in s["sun"]), "suns stay in range after drift")

        def r7(t):
            s = t.fresh(light=3, at=0, mood=[C["FAVOR_AT"]] + [0] * (C["RING"] - 1))
            self._sync(s)
            s["_turn"] = C["FAVOR_TURN"] - 1
            t.ok(not self.has_option(s, "favor", d=0), "no favor before its turn")
            s["_turn"] = C["FAVOR_TURN"]
            t.ok(self.has_option(s, "favor", d=0), "favor offered from its turn")
            t.ok(not self.has_option(s, "favor", d=1), "a low-mood steading owes nothing")
            t.apply(s, "favor", {"d": 0})
            t.eq(s["mood"][0], C["FAVOR_AT"] - C["FAVOR_COST"], "the favor costs mood")
            t.eq(s["light"], 3 + C["FAVOR_GAIN"], "the favor pays light")
            t.ok(not self.has_option(s, "favor", d=0), "once only")
            s = t.fresh(light=C["LIGHT_CAP"] - 1, at=0, mood=[C["FAVOR_AT"]] + [0] * (C["RING"] - 1))
            s["_turn"] = C["FAVOR_TURN"]
            t.apply(s, "favor", {"d": 0})
            t.eq(s["light"], C["LIGHT_CAP"], "favor light stops at the cap")
            s = t.fresh(light=C["FAVOR_COST"], at=0, mood=[0] * C["RING"])
            s["mood"][3] = C["FAVOR_AT"]
            s["_turn"] = C["FAVOR_TURN"]
            far = self.dist(0, 3) * C["WALK"]
            s["light"] = far - 1
            t.ok(not self.has_option(s, "favor", d=3), "a favor you cannot walk to is not offered")

        def r8(t):
            s = t.fresh()
            t.eq(s["mood"], [C["START_MOOD"]] * C["RING"], "start moods")
            t.eq(s["approval"], C["START_MOOD"] * C["RING"], "start approval")
            s = t.fresh(mood=[0] * C["RING"])
            s["mood"][0] = C["GOAL"]
            s["_turn"] = C["TURNS"] - 1
            s["visited"] = 0
            self._sync(s)
            t.ok(self.check_end(s) is None, "reaching the goal early does not win; only the count does")
            s["_turn"] = C["TURNS"]
            s["visited"] = -1
            t.ok(self.check_end(s) is None, "the count is not taken before the last action (dusk of the turn before)")
            s["visited"] = 0
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "the count at the goal wins")
            s["mood"][0] = C["GOAL"] - 1
            self._sync(s)
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "one short of the goal at the count loses")
            s2, _ = t.step(t.fresh(light=5, at=5, mood=[C["GOAL"]] + [0] * (C["RING"] - 1)), "gather", {"d": 5})
            t.ok(s2["_ended"] is None, "the count waits for the last turn")
            s = t.fresh(light=5, at=5, mood=[7] * C["RING"])
            self._sync(s)
            s["_turn"] = C["TURNS"] - 1
            s2, _ = t.step(s, "gather", {"d": 5})
            t.eq(s2["_turn"], C["TURNS"], "the last turn is played")
            t.ok(s2["_ended"] is None, "the game is still live at the start of the last turn")
            t.ok(len(self.options(s2)) > 0, "the last turn offers actions")
            s3, _ = t.step(s2, "gather", {"d": 5})
            t.ok(s3["_ended"] is not None, "the count comes right after the action on the last turn")
            t.eq(s3["_turn"], C["TURNS"], "and no dusk follows it")
            t.eq(self.turns, C["TURNS"], "the turn budget is TURNS")

        return [
            (1, "ring and walk", r1), (2, "gather", r2), (3, "gift rates", r3), (4, "blessing and golden hour", r4),
            (5, "unrest and riot", r5), (6, "the front", r6), (7, "favors", r7), (8, "start and goal", r8),
        ]

    # ------------------------------------------------------------ engine

    def init_state(self, rng):
        C = self.C
        sun = [rng.d(C["SUN_MAX"]) for _ in range(C["RING"])]
        temper = rng.d(2) - 1
        s = {
            "light": C["START_LIGHT"],
            "approval": 0,
            "low": 0,
            "favors": 0,
            "at": C["_START_AT"],
            "visited": -1,
            "mood": [C["START_MOOD"]] * C["RING"],
            "sun": sun,
            "favored": [0] * C["RING"],
            "recent": [],
            "hidden": {"temper": temper},
        }
        self._sync(s)
        return s

    def options(self, s):
        C = self.C
        names = self.names
        o = []
        for d in range(C["RING"]):
            w = self.dist(s["at"], d) * C["WALK"]
            walk = f", walk -{w}" if w else ""
            if s["light"] >= w:
                y = self.yield_at(s["sun"][d])
                room = C["LIGHT_CAP"] - (s["light"] - w)
                full = f", baskets full at +{room}" if y > room else ""
                o.append({"id": "gather", "label": f"Gather at {names[d]} (sun {s['sun'][d]}: +{y} light{full}{walk})",
                          "args": {"d": d}, "group": "Gather light"})
            for n in range(C["GIFT_MIN"], C["GIFT_MAX"] + 1):
                if s["light"] >= w + n:
                    gain = self.gift_eff(s, d, n)
                    o.append({"id": "gift", "label": f"Gift {n} light to {names[d]} (sun {s['sun'][d]}: mood +{gain}{walk})",
                              "args": {"d": d, "n": n}, "group": "Gift light"})
        for d in self._favor_targets(s):
            w = self.dist(s["at"], d) * C["WALK"]
            walk = f", walk -{w}" if w else ""
            o.append({"id": "favor", "label": f"Call a favor at {names[d]} (mood -{C['FAVOR_COST']}, light +{C['FAVOR_GAIN']}{walk})",
                      "args": {"d": d}, "group": "Call a favor"})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        names = self.names
        d = args["d"]
        ev = []
        w = self.dist(s["at"], d) * C["WALK"]
        if w:
            s["light"] -= w
            ev.append(f"You walk to {names[d]} (light -{w}).")
        else:
            ev.append(f"You stay at {names[d]}.")
        s["at"] = d
        s["visited"] = d
        s["recent"] = (s["recent"] + [d])[-C["RECENT"]:]
        if a == "gather":
            y = self.yield_at(s["sun"][d])
            room = C["LIGHT_CAP"] - s["light"]
            got = min(y, room)
            s["light"] += got
            if got < y:
                self.hit("overflow")
                ev.append(f"The bees at {names[d]} make {y} light. Only {got} fits in your baskets.")
            else:
                ev.append(f"The bees at {names[d]} make {y} light.")
        elif a == "gift":
            n = args["n"]
            raw = self.gift_gain(s, d, n)
            gain = self.gift_eff(s, d, n)
            sun = s["sun"][d]
            s["light"] -= n
            s["mood"][d] += gain
            bonus = self.blessing(s["_turn"])
            ceiling = f" Mood tops out at {C['MOOD_MAX']}; {raw - gain} wasted." if gain < raw else ""
            ev.append(f"{names[d]} takes {n} light (sun {sun}, rate {self.rate(sun)}, blessing +{bonus}"
                      f"{', Golden Hour x' + str(C['GOLDEN_MULT']) if s['_turn'] >= C['GOLDEN_FROM'] else ''}). "
                      f"Mood +{gain} to {s['mood'][d]}.{ceiling}")
            if gain < raw:
                self.hit("ceiling")
            if sun <= C["DARK_AT"]:
                self.hit("dark_gift")
            if s["_turn"] >= C["GOLDEN_FROM"]:
                self.hit("golden")
        elif a == "favor":
            s["mood"][d] -= C["FAVOR_COST"]
            room = C["LIGHT_CAP"] - s["light"]
            got = min(C["FAVOR_GAIN"], room)
            s["light"] += got
            s["favored"][d] = 1
            s["favors"] += 1
            self.hit("favor")
            ev.append(f"{names[d]} pays its favor: mood -{C['FAVOR_COST']} to {s['mood'][d]}, light +{got}.")
        self._sync(s)
        return ev

    def advance(self, s, rng):
        C = self.C
        names = self.names
        ring = C["RING"]
        ev = []
        dusk = s["_turn"] - 1  # the turn that just ended
        # unrest: steadings left alone under dim skies
        upset = []
        for i in range(ring):
            if i != s["visited"] and s["sun"][i] <= C["UNREST_SUN"]:
                s["mood"][i] -= C["UNREST_LOSS"]
                upset.append(f"{names[i]} -{C['UNREST_LOSS']} to {s['mood'][i]}")
                self.hit("unrest")
                if s["mood"][i] <= -C["RIOT_AT"] + 1:
                    self.hit("near_riot")
        if upset:
            ev.append("Unrest at dusk: " + ", ".join(upset) + ".")
        # the front
        temper = s["hidden"]["temper"]
        count = 2 if dusk >= C["STORM_TURN"] else 1
        if dusk == C["STORM_TURN"]:
            self.hit("storm")
            ev.append("The long night begins: the front now falls on two steadings.")
        if temper == 0:
            order = sorted(range(ring), key=lambda i: (-s["sun"][i], i))
        else:
            order = sorted(range(ring), key=lambda i: (-s["recent"].count(i), -s["sun"][i], i))
        struck = order[:count]
        self.hit("front_sunny" if temper == 0 else "front_crowd")
        for i in struck:
            old = s["sun"][i]
            s["sun"][i] = max(0, old - C["FRONT_DROP"])
            if old == s["sun"][i]:
                ev.append(f"The front fell on {names[i]}, which had no sun left to lose.")
            else:
                ev.append(f"The front fell on {names[i]}: sun {old} to {s['sun'][i]}.")
        # drift elsewhere
        moved = []
        for i in range(ring):
            if i in struck:
                continue
            new = rng.drift(s["sun"][i], 0, C["SUN_MAX"], 1, C["_DRIFT_UP"], C["_DRIFT_DOWN"])
            if new != s["sun"][i]:
                moved.append(f"{names[i]} {new - s['sun'][i]:+d}")
            s["sun"][i] = new
        if moved:
            ev.append("Sun drifts: " + ", ".join(moved) + ".")
        s["visited"] = -1
        # announcements for what the next turn changes
        nxt = s["_turn"]
        if nxt <= C["TURNS"]:
            if self.blessing(nxt) < self.blessing(nxt - 1):
                self.hit("bless_fade")
                ev.append(f"Your blessing fades: gifts now carry +{self.blessing(nxt)}.")
            if nxt == C["FAVOR_TURN"]:
                ev.append("The valley remembers your kindness: steadings at high mood will now pay favors.")
            if nxt == C["GOLDEN_FROM"]:
                ev.append(f"The Golden Hour: every gift now counts x{C['GOLDEN_MULT']}.")
        self._sync(s)
        return ev

    def status_line(self, s):
        names = self.names
        mood = " ".join(f"{names[i][0]}{s['mood'][i]}" for i in range(self.C["RING"]))
        sun = " ".join(f"{names[i][0]}{s['sun'][i]}" + ("@" if i == s["at"] else "") for i in range(self.C["RING"]))
        return f"Light {s['light']}/{self.C['LIGHT_CAP']} | Approval {s['approval']}/{self.C['GOAL']} | Mood {mood} | Sun {sun}"

    def check_end(self, s):
        C = self.C
        names = self.names
        if s["low"] <= -C["RIOT_AT"]:
            i = s["mood"].index(s["low"])
            return {"result": "loss", "reason": f"{names[i]} rose against you at mood {s['low']}"}
        # check_end runs twice a turn: after the action (s["_turn"] is this turn, s["visited"] is set) and after dusk
        # (s["_turn"] is already the next turn, s["visited"] is cleared). The count belongs to the first moment on the last turn.
        if s["_turn"] > self.turns or (s["_turn"] == self.turns and s["visited"] >= 0):
            if s["approval"] >= C["GOAL"]:
                return {"result": "win", "reason": f"the Harvest Count found approval {s['approval']}"}
            return {"result": "loss", "reason": f"the Harvest Count found approval {s['approval']}, needed {C['GOAL']}"}
        return None

    def heuristic(self, s, options, rng):
        C = self.C
        t = s["_turn"]
        mw = C["_MW0"] + (1 - C["_MW0"]) * (t - 1) / max(1, C["TURNS"] - 1)  # mood banked late survives to the count
        if t >= C["TURNS"]:
            lw = 0.0
        elif t >= C["GOLDEN_FROM"] - 1:
            lw = C["_LW"] * 1.2
        else:
            lw = C["_LW"]
        best, best_score = None, None
        for o in options:
            d = o["args"]["d"]
            w = self.dist(s["at"], d) * C["WALK"]
            sc = 0.0
            # visiting protects a dim steading from dusk unrest
            if s["sun"][d] <= C["UNREST_SUN"]:
                sc += mw * C["UNREST_LOSS"]
                if s["mood"][d] - C["UNREST_LOSS"] <= -C["RIOT_AT"]:
                    sc += 100
            if o["id"] == "gather":
                got = min(self.yield_at(s["sun"][d]), C["LIGHT_CAP"] - s["light"] + w)
                sc += lw * (got - w)
            elif o["id"] == "gift":
                n = o["args"]["n"]
                sc += mw * self.gift_eff(s, d, n) - lw * (n + w)
            else:
                got = min(C["FAVOR_GAIN"], C["LIGHT_CAP"] - s["light"] + w)
                sc += lw * (got - w) - mw * C["FAVOR_COST"]
            if best_score is None or sc > best_score + 1e-9:
                best, best_score = o, sc
        return best


if __name__ == "__main__":
    run(G)
