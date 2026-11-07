"""Belt Claim: the v4 reference engine for /play (a game that grows).

A hand-made example, not a roll result. It shows the v4 shape, not the content: an ECONOMY with an income (tons dug
per ship per turn), a stock (ore, then credits) and sinks (ships, the refinery); a GROWTH number (the fleet) that
sensible play doubles; a LADDER (two sloops, a third ship that opens raiding, the refinery that doubles the price);
two PATHS to the win (haul: dig and sell; raid: take Kessler's barges); a PRESSURE that scales (Kessler's fleet grows
on a schedule and sits on the richest rocks, and the rocks run out); a visible rival on the board; two gambits that
act on the rival; a cast the engine owns; a cliff finish (the survey closes on the last turn).

Copy the structure. Change the nouns, the economy, the ladder and the win. Do not copy the belt, Kessler or the
refinery into the next game.

Known warning, accepted: GROWTH says the fleet stops growing in the last third. That is the design: by then the
belt is nearly worked out and the last turns are spent raiding Kessler's barges and jumping his claims, which
trades ships for his ships. The finish is the survey cliff, not a plateau.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gm_base import Game, plural, run  # noqa: E402
from gm_cast import fall, fallen_text, roster  # noqa: E402

DOCK = 0  # lit-ok: the station's index; rocks are 1..ROCKS


class G(Game):
    name = "Belt Claim"

    CONSTANTS = {
        "TURNS": 32,
        "ROCKS": 8,
        "START_SHIPS": 2,
        "START_CREDITS": 20,
        "START_KESSLER": 3,
        "PRICE": 2,
        "GLUT": 20,
        "SHIP_COST": 50,
        "FLEET_MAX": 8,
        "REFINERY_COST": 90,
        "RIVAL_EVERY": 4,
        "MID": 16,
        "RAID_NEED": 4,
        "RAID_NEED_ESCORT": 3,
        "ESCORT_FLEET": 4,
        "RAID_ORE": 8,
        "JUMP_NEED": 4,
        "JUMP_NEED_BIG": 3,
        "JUMP_BAN": 2,
        "_GRADE_MIN": 2,
        "_GRADE_MAX": 5,
        "_RESERVE_MIN": 60,
        "_RESERVE_MAX": 120,
        "_SELL_AT": 15,
    }

    RULES = """
1. {ROCKS} rocks ring the station, each with a grade (tons a ship digs a turn) and a reserve. Start: {START_SHIPS} sloops, {START_CREDITS} credits. A move takes a ship from the station first, else from your poorest rock.
2. At dusk each ship digs its rock's grade in tons, down to what is left; the reserve drops by that. A rock at 0 is worked out. Ore piles up at the station.
3. Sell turns all ore into credits at the price. The price starts at {PRICE} a ton, falls 1 for every {GLUT} tons you sell in one go, and recovers 1 a turn.
4. A ship costs {SHIP_COST} credits, fleet cap {FLEET_MAX}. Your third ship opens raiding. The refinery costs {REFINERY_COST}, needs three ships, and doubles the price you get from then on.
5. Kessler runs the rival outfit with {START_KESSLER} barges: they sit on the richest rocks left, dig like yours, and it adds a barge every {RIVAL_EVERY} turns and one extra on turn {MID}. Its fleet is on the board.
6. Raid a Kessler barge: roll {RAID_NEED}+, or {RAID_NEED_ESCORT}+ with {ESCORT_FLEET} ships or more: Kessler loses a ship and you take {RAID_ORE} tons. A miss loses the raiding ship and its crew.
7. Jump a claim Kessler holds: roll {JUMP_NEED}+, or {JUMP_NEED_BIG}+ with the bigger fleet: its ship falls back to its dock for {JUMP_BAN|turn} and yours takes the rock. A miss sends your ship home.
8. The survey closes after turn {TURNS}: you win with the refinery built and more ships than Kessler. You lose at once with no ships left, or at the close without both.
"""

    ACTIONS = ["move", "sell", "buy_ship", "refinery", "raid", "jump"]
    TAGS = ["worked_out", "glut", "third_ship", "refinery", "kessler_ship", "mid_ship", "raid", "raid_miss",
            "jump", "jump_miss", "fleet_lost", "survey", "contested"]
    GAMBITS = {"raid": {"rival": True}, "jump": {"rival": True}}
    RIVAL_KEYS = ["k_fleet", "k_ships"]
    TRACKED = ["fleet", "credits", "ore", "price"]
    GROWTH = "fleet"
    ECONOMY = {"income": ["dig"], "stock": ["ore", "credits"], "sinks": ["buy_ship", "refinery"]}
    LADDER = {"key": "tier", "tiers": ["two sloops", "a third ship", "the refinery"], "unlocks": {2: ["raid"], 3: []}}
    PATHS = {"haul": ["move", "sell"], "raid": ["raid", "jump"]}

    BOUNDS = {"fleet": (0, 8), "k_fleet": (0, 14), "credits": (0, 3000), "ore": (0, 500), "price": (0, 3), "tier": (1, 3), "dig": (0, 60)}
    REACH = {"fleet": 4, "tier": 3, "price": ("<=", 1), "k_fleet": 4, "credits": "REFINERY_COST"}
    DERIVED = {"dig": lambda g, s: g.dig_rate(s)}
    GATES = {
        "move": {"_if": lambda g, s: g.fleet(s) > 0 and (DOCK not in s["ships"] or len(g.live_rocks(s)) > 0)},
        "sell": {"ore": 1},
        "buy_ship": {"credits": "SHIP_COST", "_if": lambda g, s: g.fleet(s) < g.C["FLEET_MAX"]},
        "refinery": {"credits": "REFINERY_COST", "tier": 2, "!refinery": 1},
        "raid": {"tier": 2, "_if": lambda g, s: s["k_fleet"] > 0 and g.fleet(s) >= 2},  # lit-ok: keep one ship digging
        "jump": {"_if": lambda g, s: any(k["pos"] != DOCK for k in s["k_ships"]) and g.fleet(s) > 0},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------ helpers

    def fleet(self, s):
        return len(s["ships"])

    def dig_rate(self, s):
        """Tons the fleet would dig this dusk: the income."""
        return sum(min(s["rocks"][p - 1]["grade"], s["rocks"][p - 1]["reserve"]) for p in s["ships"] if p != DOCK)

    def live_rocks(self, s):
        return [i + 1 for i, r in enumerate(s["rocks"]) if r["reserve"] > 0]

    def kessler_rocks(self, s):
        return sorted({k["pos"] for k in s["k_ships"] if k["pos"] != DOCK})

    def price_now(self, s):
        return s["price"] * (2 if s["refinery"] else 1)  # lit-ok: "doubles" is the refinery by definition

    def mover(self, s):
        """The ship a move or a jump takes: one at the station first, else one from the poorest rock."""
        if DOCK in s["ships"]:
            return DOCK
        return min(set(s["ships"]), key=lambda p: (min(s["rocks"][p - 1]["grade"], s["rocks"][p - 1]["reserve"]), p))

    def place(self, p):
        return "the station" if p == DOCK else f"Rock {p}"

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C

        def rocks(**over):
            base = [{"grade": 3, "reserve": 20} for _ in range(C["ROCKS"])]
            for k, v in over.items():
                base[int(k[1:]) - 1] = v
            return base

        def r1(t):
            s = t.fresh()
            t.eq(len(s["rocks"]), C["ROCKS"], "eight rocks")
            t.eq(len(s["ships"]), C["START_SHIPS"], "two sloops to start")
            t.ok(all(p == DOCK for p in s["ships"]), "the ships start at the station")
            t.ok(all(C["_GRADE_MIN"] <= r["grade"] <= C["_GRADE_MAX"] and C["_RESERVE_MIN"] <= r["reserve"] <= C["_RESERVE_MAX"] for r in s["rocks"]), "grades and reserves in range")
            s2 = t.fresh(ships=[3, 5], rocks=rocks(r3={"grade": 4, "reserve": 10}, r5={"grade": 2, "reserve": 0}), k_ships=[])
            events = t.advance(s2, turn=2)
            t.has(events, "Your ships dig 4 tons: Rock 3 4.")
            t.has(events, "Idle on worked-out Rock 5.")
            s2 = t.fresh(ships=[5], rocks=rocks(r5={"grade": 2, "reserve": 0}), k_ships=[])
            events = t.advance(s2, turn=2)
            t.has(events, "Your ships dig nothing: every rock they sit on is worked out.")
            t.eq(s["credits"], C["START_CREDITS"], "starting credits")
            t.eq(s["tier"], 1, "tier 1")
            t.ok(set(t.ids(s)) >= {"move"}, "a ship can be moved on turn 1")
            t.ok(not t.offered(s, "sell") and not t.offered(s, "raid") and not t.offered(s, "refinery"), "nothing to sell, no raids, no refinery yet")
            t.eq(t.label(s, "move"), "Send a ship from the station to a rock (pick the rock)")
            s = t.fresh(ships=[DOCK, DOCK], rocks=rocks())
            events = t.apply(s, "move", {"to": 3})
            t.eq(s["ships"], [DOCK, 3], "one ship moved")
            t.has(events, "A ship casts off from the station for Rock 3.")
            s, _ = t.step(s, "move", {"to": 4})
            t.eq(s["_turn"], 2, "one action ends the turn")
            t.eq(sorted(s["ships"]), [3, 4], "both ships out")
            t.ok(t.offered(s, "move", to="station"), "a ship can be called back to the station")
            s = t.fresh(ships=[3, 5], rocks=rocks(r3={"grade": 4, "reserve": 20}, r5={"grade": 2, "reserve": 20}))
            t.eq(t.label(s, "move"), "Move a ship from Rock 5 to another rock or the station (pick where)", "the poorest rock gives up its ship")
            t.ok(not t.offered(s, "move", to=5), "a ship does not move to the rock it leaves")
            events = t.apply(s, "move", {"to": "station"})
            t.eq(sorted(s["ships"]), [DOCK, 3])
            t.has(events, "A ship comes in from Rock 5 to the station.")
            s = t.fresh(ships=[3, 5], rocks=rocks(r3={"grade": 4, "reserve": 20}, r5={"grade": 2, "reserve": 20}))
            events = t.apply(s, "move", {"to": 7})
            t.has(events, "A ship shifts from Rock 5 to Rock 7.")
            s = t.fresh(ships=[3], rocks=rocks(r3={"grade": 4, "reserve": 20}, **{f"r{i}": {"grade": 2, "reserve": 0} for i in (1, 2, 4, 5, 6, 7, 8)}))
            t.ok(t.offered(s, "move", to="station") and not t.offered(s, "move", to=3), "the one live rock is the one you are on: only the station is left to go to")
            t.eq(self.live_rocks(s), [3], "one live rock")
            t.ok(not t.offered(t.fresh(ships=[DOCK], rocks=rocks(**{f"r{i}": {"grade": 2, "reserve": 0} for i in range(1, 9)})), "move"), "a ship at the station with every rock worked out has nowhere to go")
            t.eq(self.dig_rate(s), 4, "the income is what the fleet digs at dusk")
            t.eq(self.dig_rate(t.fresh(ships=[DOCK, DOCK])), 0)
            t.eq(t.status(t.fresh(ships=[3, DOCK], credits=20, ore=0, price=3, k_fleet=2)), "Fleet 2 v Kessler 2 | Credits 20 | Ore 0 | Price 3 a ton")

        def r2(t):
            s = t.fresh(ships=[3, 5], rocks=rocks(r3={"grade": 4, "reserve": 10}, r5={"grade": 2, "reserve": 1}), k_ships=[])
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.eq(s["ore"], 4 + 1, "each ship digs its grade, down to what is left")
            t.eq(s["rocks"][2]["reserve"], 6, "the reserve drops by what was dug")
            t.eq(s["rocks"][4]["reserve"], 0, "a rock digs down to zero")
            t.has(events, "Your ships dig 5 tons: Rock 3 4, Rock 5 1.")
            t.has(events, "Rock 5 is worked out.")
            t.ok("worked_out" in self._hits)
            t.in_order(events, ["dig 5 tons", "worked out"])
            s = t.fresh(ships=[DOCK, DOCK], rocks=rocks(), k_ships=[])
            events = t.advance(s, turn=2)
            t.eq(s["ore"], 0, "ships at the station dig nothing")
            t.has(events, "Your ships dig nothing: none is on a rock.")
            s = t.fresh(ships=[3], rocks=rocks(r3={"grade": 4, "reserve": 10}), k_ships=[{"pos": 3, "ban": 0}])
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.eq(s["rocks"][2]["reserve"], 10 - 4 - 4, "Kessler digs the same rock too, at its grade")
            t.has(events, "Kessler digs beside you on Rock 3.")
            t.ok("contested" in self._hits)

        def r3(t):
            s = t.fresh(ore=10, price=C["PRICE"], credits=0, k_ships=[])
            t.eq(t.label(s, "sell"), f"Sell 10 tons of ore at {C['PRICE']} a ton (+{10 * C['PRICE']} credits)")
            events = t.apply(s, "sell")
            t.eq((s["ore"], s["credits"]), (0, 10 * C["PRICE"]), "ore becomes credits at the price")
            t.eq(s["price"], C["PRICE"], "a small sale does not move the price")
            t.has(events, f"You sell 10 tons at {C['PRICE']} a ton. Credits +{10 * C['PRICE']}.")
            s = t.fresh(ore=2 * C["GLUT"] + 5, price=C["PRICE"], credits=0, k_ships=[])
            self._hits.clear()
            events = t.apply(s, "sell")
            t.eq(s["credits"], (2 * C["GLUT"] + 5) * C["PRICE"], "the whole lot sells at today's price")
            t.eq(s["price"], C["PRICE"] - 2, "every GLUT tons sold in one go drops the price by 1")
            t.has(events, f"The glut knocks the price down to {C['PRICE'] - 2}.")
            t.ok("glut" in self._hits)
            events = t.advance(s, turn=2)
            t.eq(s["price"], C["PRICE"] - 1, "the price recovers 1 a turn")
            t.has(events, f"The ore price recovers to {C['PRICE'] - 1}.")
            t.advance(s, turn=3)
            t.advance(s, turn=4)
            t.eq(s["price"], C["PRICE"], "and stops at its start")
            s = t.fresh(ore=10 * C["GLUT"], price=C["PRICE"], credits=0, k_ships=[])
            t.apply(s, "sell")
            t.eq(s["price"], 0, "the price never goes below 0")
            s = t.fresh(ore=0)
            t.ok(not t.offered(s, "sell"), "nothing to sell")

        def r4(t):
            s = t.fresh(credits=C["SHIP_COST"] - 1, ships=[DOCK, DOCK])
            t.ok(not t.offered(s, "buy_ship"), "a ship costs its price")
            s = t.fresh(credits=C["SHIP_COST"], ships=[DOCK, DOCK], tier=1)
            t.eq(t.label(s, "buy_ship"), f"Buy a third ship (-{C['SHIP_COST']} credits)")
            self._hits.clear()
            events = t.apply(s, "buy_ship")
            t.eq((s["credits"], len(s["ships"]), s["fleet"], s["tier"]), (0, 3, 3, 2), "a third ship, tier 2")
            t.has(events, "A third sloop joins the fleet at the station. Raiding is open.")
            t.ok("third_ship" in self._hits)
            t.eq(len(s["cast"]), 5, "the cast is five")
            s = t.fresh(credits=C["SHIP_COST"], ships=[DOCK] * 3, fleet=3, tier=2)
            t.eq(t.label(s, "buy_ship"), f"Buy a fourth ship (-{C['SHIP_COST']} credits)")
            t.apply(s, "buy_ship")
            t.eq(s["tier"], 2, "more ships do not change the tier")
            s = t.fresh(credits=999, ships=[DOCK] * C["FLEET_MAX"], fleet=C["FLEET_MAX"], tier=2)
            t.ok(not t.offered(s, "buy_ship"), "the fleet cap")
            s = t.fresh(credits=C["REFINERY_COST"], ships=[DOCK, DOCK], tier=1)
            t.ok(not t.offered(s, "refinery"), "the refinery needs three ships")
            s = t.fresh(credits=C["REFINERY_COST"] - 1, ships=[DOCK] * 3, fleet=3, tier=2)
            t.ok(not t.offered(s, "refinery"), "the refinery costs its price")
            s = t.fresh(credits=C["REFINERY_COST"], ships=[DOCK] * 3, fleet=3, tier=2, ore=10, price=C["PRICE"])
            t.eq(t.label(s, "refinery"), f"Build the refinery (-{C['REFINERY_COST']} credits; ore sells for double from now on)")
            self._hits.clear()
            events = t.apply(s, "refinery")
            t.ok(s["refinery"] and s["tier"] == 3 and s["credits"] == 0, "refinery built, tier 3")
            t.has(events, "The refinery lights up. Refined ore sells for double.")
            t.ok("refinery" in self._hits)
            t.ok(not t.offered(s, "refinery"), "one refinery")
            t.eq(t.label(s, "sell"), f"Sell 10 tons of ore at {2 * C['PRICE']} a ton, refined (+{10 * 2 * C['PRICE']} credits)")
            t.apply(s, "sell")
            t.eq(s["credits"], 10 * 2 * C["PRICE"], "refined ore sells for double")

        def r5(t):
            s = t.fresh(ships=[DOCK, DOCK], rocks=rocks(r2={"grade": 5, "reserve": 20}, r7={"grade": 4, "reserve": 20}),
                        k_ships=[{"pos": DOCK, "ban": 0}, {"pos": DOCK, "ban": 0}], k_fleet=2)
            events = t.advance(s, turn=2)
            t.eq(sorted(k["pos"] for k in s["k_ships"]), [2, 7], "Kessler takes the two richest rocks")
            t.has(events, "Kessler's ships sit on Rock 2 and Rock 7.")
            s = t.fresh(ships=[DOCK], rocks=rocks(), k_ships=[{"pos": DOCK, "ban": 0} for _ in range(3)], k_fleet=3)
            events = t.advance(s, turn=2)
            t.ok(any(e.startswith("Kessler's ships sit on Rock ") and ", Rock" in e and " and Rock" in e for e in events), "three rocks read as a list")
            t.eq(s["rocks"][1]["reserve"], 20, "Kessler moves at dusk and digs from the next dusk on")
            t.advance(s, turn=3)
            t.eq(s["rocks"][1]["reserve"], 17, "then it digs at its grade")
            s = t.fresh(k_ships=[{"pos": DOCK, "ban": 0}], k_fleet=1, ships=[DOCK, DOCK])
            self._hits.clear()
            events = t.advance(s, turn=C["RIVAL_EVERY"])
            t.eq(s["k_fleet"], 2, "a new Kessler ship every RIVAL_EVERY turns")
            t.eq(len(s["k_ships"]), 2)
            t.has(events, "A new Kessler barge docks. Kessler's fleet is 2.")
            t.ok("kessler_ship" in self._hits)
            s = t.fresh(k_ships=[{"pos": DOCK, "ban": 0}], k_fleet=1, ships=[DOCK, DOCK])
            t.advance(s, turn=C["RIVAL_EVERY"] - 1)
            t.eq(s["k_fleet"], 1, "no new ship on other turns")
            s = t.fresh(k_ships=[{"pos": DOCK, "ban": 0}], k_fleet=1, ships=[DOCK, DOCK])
            self._hits.clear()
            events = t.advance(s, turn=C["MID"])
            t.eq(s["k_fleet"], 2 if C["MID"] % C["RIVAL_EVERY"] else 3, "one extra ship on the midpoint turn")
            t.has(events, f"Turn {C['MID']}: Kessler brings in an extra barge from the inner belt.")
            t.ok("mid_ship" in self._hits)
            # a banned Kessler ship waits at its dock
            s = t.fresh(k_ships=[{"pos": DOCK, "ban": 2}], k_fleet=1, ships=[DOCK, DOCK], rocks=rocks())
            t.advance(s, turn=2)
            t.ok(s["k_ships"][0]["pos"] == DOCK and s["k_ships"][0]["ban"] == 1, "a ship driven off waits out its turns")
            t.advance(s, turn=3)
            t.ok(s["k_ships"][0]["pos"] == DOCK and s["k_ships"][0]["ban"] == 0)
            t.advance(s, turn=4)
            t.ok(s["k_ships"][0]["pos"] != DOCK, "then it comes back out")
            board = self.board(s)
            t.ok(f"Kessler: {plural(s['k_fleet'], 'barge')}" in board and "Rock 1:" in board and "Tier: two sloops" in board and "Ships at the station: 2" in board, f"the rival's fleet, the rocks and the tier are on the board: {board!r}")
            t.ok("Kessler" in board.splitlines()[0] and "20 tons left" in board.splitlines()[0], "a rock line says who sits on it and what is left")

        def r6(t):
            s = t.fresh(ships=[DOCK, DOCK], tier=1, k_fleet=2)
            t.ok(not t.offered(s, "raid"), "no raids before the third ship")
            s = t.fresh(ships=[DOCK, DOCK, 3], fleet=3, tier=2, k_fleet=2, ore=0, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.eq(t.label(s, "raid"), f"Raid a Kessler barge (roll {C['RAID_NEED']}+: Kessler -1 ship, +{C['RAID_ORE']} tons; miss: you lose the ship)")
            self._hits.clear()
            events = t.apply(s, "raid", dice=[C["RAID_NEED"]])
            t.eq((s["k_fleet"], len(s["k_ships"]), s["ore"]), (1, 1, C["RAID_ORE"]), "a hit takes a barge and its ore")
            t.has(events, f"roll {C['RAID_NEED']} (need {C['RAID_NEED']}+) raid success. Your boarders take a Kessler barge and its {C['RAID_ORE']} tons; its crew limps home in the lifeboat. Kessler's fleet is 1.")
            t.ok("raid" in self._hits)
            s = t.fresh(ships=[DOCK, DOCK, 3], fleet=3, tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            self._hits.clear()
            events = t.apply(s, "raid", dice=[C["RAID_NEED"] - 1])
            t.eq((s["fleet"], len(s["ships"]), s["k_fleet"]), (2, 2, 2), "a miss loses the raiding ship")
            t.has(events, f"roll {C['RAID_NEED'] - 1} (need {C['RAID_NEED']}+) raid fail. The barge's escort holes your ship.")
            t.ok(any(e.endswith("fell.") or "fell." in e for e in events), "the loss names who fell")
            t.eq(sum(1 for c in s["cast"] if not c["alive"]), 1, "one of the cast died with the ship")
            t.ok({"raid_miss", "fleet_lost"} <= self._hits)
            s = t.fresh(ships=[DOCK] * C["ESCORT_FLEET"], fleet=C["ESCORT_FLEET"], tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.eq(t.label(s, "raid"), f"Raid a Kessler barge (roll {C['RAID_NEED_ESCORT']}+ with escorts: Kessler -1 ship, +{C['RAID_ORE']} tons; miss: you lose the ship)")
            t.apply(s, "raid", dice=[C["RAID_NEED_ESCORT"]])
            t.eq(s["k_fleet"], 1, "escorts lower the need")
            s = t.fresh(ships=[DOCK] * 3, fleet=3, tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.apply(s, "raid", dice=[C["RAID_NEED_ESCORT"]])
            t.eq(s["k_fleet"], 2, "without escorts the lower roll misses")
            s = t.fresh(ships=[DOCK] * 3, fleet=3, tier=2, k_fleet=0, k_ships=[])
            t.ok(not t.offered(s, "raid"), "nothing to raid when Kessler has no ships")
            s = t.fresh(ships=[DOCK], fleet=1, tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.ok(not t.offered(s, "raid"), "never raid with the last ship")
            # losing the last ship ends the game
            s = t.fresh(ships=[DOCK, DOCK], fleet=2, tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.apply(s, "raid", dice=[1])
            t.eq(s["fleet"], 1, "down to one")
            t.ok(self.check_end(s) is None, "one ship is still a fleet")

        def r7(t):
            s = t.fresh(ships=[DOCK, 3], fleet=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}], rocks=rocks())
            t.ok(t.offered(s, "jump", rock=2) and t.offered(s, "jump", rock=5) and not t.offered(s, "jump", rock=3), "only Kessler's rocks can be jumped")
            t.eq(t.label(s, "jump", rock=2), f"Jump Kessler's claim on Rock 2 (roll {C['JUMP_NEED']}+: its ship falls back for {plural(C['JUMP_BAN'], 'turn')}, yours takes the rock; miss: your ship goes home)")
            self._hits.clear()
            events = t.apply(s, "jump", {"rock": 2}, dice=[C["JUMP_NEED"]])
            t.eq(s["k_ships"][0], {"pos": DOCK, "ban": C["JUMP_BAN"]}, "the Kessler ship falls back to its dock")
            t.ok(2 in s["ships"], "your ship takes the rock")
            t.has(events, f"roll {C['JUMP_NEED']} (need {C['JUMP_NEED']}+) jump success. Your ship cuts across Kessler's bow on Rock 2 and its barge falls back to its dock for {plural(C['JUMP_BAN'], 'turn')}.")
            t.ok("jump" in self._hits)
            s = t.fresh(ships=[DOCK, 3], fleet=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}], rocks=rocks())
            self._hits.clear()
            events = t.apply(s, "jump", {"rock": 2}, dice=[C["JUMP_NEED"] - 1])
            t.eq(s["k_ships"][0], {"pos": 2, "ban": 0}, "a miss leaves Kessler where it was")
            t.eq(sorted(s["ships"]), [DOCK, 3], "and the ship that went (the one at the station) is home again")
            t.has(events, f"roll {C['JUMP_NEED'] - 1} (need {C['JUMP_NEED']}+) jump fail. Kessler's barge holds the rock and your ship goes home to the station.")
            t.ok("jump_miss" in self._hits)
            s = t.fresh(ships=[DOCK, 3, 4], fleet=3, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}], rocks=rocks())
            t.eq(t.label(s, "jump", rock=2), f"Jump Kessler's claim on Rock 2 (roll {C['JUMP_NEED_BIG']}+ with the bigger fleet: its ship falls back for {plural(C['JUMP_BAN'], 'turn')}, yours takes the rock; miss: your ship goes home)")
            t.apply(s, "jump", {"rock": 2}, dice=[C["JUMP_NEED_BIG"]])
            t.eq(s["k_ships"][0]["ban"], C["JUMP_BAN"], "the bigger fleet lowers the need")
            s = t.fresh(ships=[DOCK, 3], fleet=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}], rocks=rocks())
            t.apply(s, "jump", {"rock": 2}, dice=[C["JUMP_NEED_BIG"]])
            t.eq(s["k_ships"][0]["ban"], 0, "an equal fleet needs the full roll")
            s = t.fresh(ships=[3], fleet=1, k_fleet=2, k_ships=[{"pos": DOCK, "ban": 0}, {"pos": DOCK, "ban": 0}])
            t.ok(not t.offered(s, "jump"), "nothing to jump when Kessler holds no rock")
            # the ship that jumps is the one at the station if any, else the one on the poorest rock
            s = t.fresh(ships=[4, 3], fleet=2, k_fleet=1, k_ships=[{"pos": 2, "ban": 0}], rocks=rocks(r3={"grade": 2, "reserve": 20}, r4={"grade": 5, "reserve": 20}))
            t.apply(s, "jump", {"rock": 2}, dice=[6])
            t.eq(sorted(s["ships"]), [2, 4], "the ship on the poorer rock went")
            s = t.fresh(ships=[4, 3], fleet=2, k_fleet=1, k_ships=[{"pos": 2, "ban": 0}], rocks=rocks(r3={"grade": 2, "reserve": 20}, r4={"grade": 5, "reserve": 20}))
            t.apply(s, "jump", {"rock": 2}, dice=[1])
            t.eq(sorted(s["ships"]), [DOCK, 4], "a miss sends that ship to the station")

        def r8(t):
            s = t.fresh(ships=[3, 4, 5], fleet=3, tier=3, refinery=True, k_fleet=1, k_ships=[{"pos": DOCK, "ban": 0}], rocks=rocks())
            s["_turn"] = C["TURNS"]
            t.ok(self.check_end(s) is None, "the last turn is still played")
            self._hits.clear()
            events = t.advance(s, turn=C["TURNS"])
            t.ok(not s["_ended"], "the dusk of the last turn does not end the game by itself")
            end = self.final_check(s)
            t.eq(end, {"result": "win", "reason": "the survey closes: your refinery and 3 ships against Kessler's 2 take the belt charter"})
            s = t.fresh(ships=[3, 4], fleet=2, tier=2, refinery=False, k_fleet=1, k_ships=[])
            end = self.final_check(s)
            t.eq(end, {"result": "loss", "reason": "the survey closes with no refinery; the charter goes to Kessler"})
            s = t.fresh(ships=[3, 4], fleet=2, tier=3, refinery=True, k_fleet=2, k_ships=[])
            end = self.final_check(s)
            t.eq(end, {"result": "loss", "reason": "the survey closes with 2 ships against Kessler's 2; the charter goes to the bigger fleet"})
            s = t.fresh(ships=[], fleet=0, tier=2, k_fleet=2)
            end = self.check_end(s)
            t.eq(end, {"result": "loss", "reason": "no ships left; the outfit is finished"})
            s = t.fresh(ships=[DOCK, DOCK], fleet=2, tier=2, k_fleet=2, k_ships=[{"pos": 2, "ban": 0}, {"pos": 5, "ban": 0}])
            t.apply(s, "raid", dice=[1])
            s["ships"], s["fleet"] = [], 0
            t.ok(self.check_end(s) and self.check_end(s)["result"] == "loss", "the last ship lost is the end")
            s = t.fresh(ships=[3, 4, 5], fleet=3, tier=3, refinery=True, k_fleet=1, k_ships=[{"pos": DOCK, "ban": 0}], rocks=rocks(), ore=5)
            s["_turn"] = C["TURNS"]
            s, _ = t.step(s, "sell")
            t.ok(s["_ended"] and s["_ended"]["phase"] == "budget" and s["_ended"]["result"] == "win", "the budget ends the game after the last dusk")
            s = t.fresh(ships=[3], fleet=1, k_ships=[], rocks=rocks())
            events = t.advance(s, turn=C["TURNS"] - 1)
            t.has(events, f"Turn {C['TURNS']}: the survey ship is in orbit; the charter is decided at its close.")
            t.ok("survey" in self._hits)

        return [
            (1, "rocks and ships", r1), (2, "digging", r2), (3, "selling and the price", r3), (4, "ships and the refinery", r4),
            (5, "Kessler", r5), (6, "raid", r6), (7, "jump a claim", r7), (8, "the survey", r8),
        ]

    # ------------------------------------------------------------ state

    def init_state(self, rng):
        C = self.C
        rocks = [{"grade": rng.d(C["_GRADE_MAX"] - C["_GRADE_MIN"] + 1) + C["_GRADE_MIN"] - 1,
                  "reserve": rng.d(C["_RESERVE_MAX"] - C["_RESERVE_MIN"] + 1) + C["_RESERVE_MIN"] - 1} for _ in range(C["ROCKS"])]
        s = {
            "ships": [DOCK] * C["START_SHIPS"],
            "fleet": C["START_SHIPS"],
            "credits": C["START_CREDITS"],
            "ore": 0,
            "price": C["PRICE"],
            "tier": 1,
            "refinery": False,
            "rocks": rocks,
            "k_ships": [{"pos": DOCK, "ban": 0} for _ in range(C["START_KESSLER"])],
            "k_fleet": C["START_KESSLER"],
            "hidden": {},
        }
        s["cast"] = roster(rng, 5, "scifi", roles=["pilot", "pilot", "engineer", "fixer", "navigator"])  # lit-ok: five named crew
        return s

    def options(self, s):
        C = self.C
        o = []
        live = self.live_rocks(s)
        if s["ships"]:
            frm = self.mover(s)
            dests = [r for r in live if r != frm]
            if frm != DOCK:
                dests.append("station")
            if dests:
                label = ("Send a ship from the station to a rock (pick the rock)" if frm == DOCK
                         else f"Move a ship from Rock {frm} to another rock or the station (pick where)")
                o.append({"id": "move", "args": {}, "params": {"to": {"choices": dests}}, "label": label})
        if s["ore"] >= 1:
            p = self.price_now(s)
            tag = ", refined" if s["refinery"] else ""
            o.append({"id": "sell", "args": {}, "label": f"Sell {plural(s['ore'], 'ton')} of ore at {p} a ton{tag} (+{s['ore'] * p} credits)"})
        if s["credits"] >= C["SHIP_COST"] and self.fleet(s) < C["FLEET_MAX"]:
            nth = ["third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"][max(0, self.fleet(s) - 2)]  # lit-ok: ordinal words
            o.append({"id": "buy_ship", "args": {}, "label": f"Buy a {nth} ship (-{C['SHIP_COST']} credits)"})
        if s["credits"] >= C["REFINERY_COST"] and s["tier"] >= 2 and not s["refinery"]:  # lit-ok: tier 2 is the third ship
            o.append({"id": "refinery", "args": {}, "label": f"Build the refinery (-{C['REFINERY_COST']} credits; ore sells for double from now on)"})
        if s["tier"] >= 2 and s["k_fleet"] > 0 and self.fleet(s) >= 2:  # lit-ok: tier 2 opens raiding; keep one ship
            esc = self.fleet(s) >= C["ESCORT_FLEET"]
            need = f"{C['RAID_NEED_ESCORT']}+ with escorts" if esc else f"{C['RAID_NEED']}+"
            o.append({"id": "raid", "args": {}, "label": f"Raid a Kessler barge (roll {need}: Kessler -1 ship, +{C['RAID_ORE']} tons; miss: you lose the ship)"})
        if self.fleet(s) > 0:
            big = self.fleet(s) > s["k_fleet"]
            need = f"{C['JUMP_NEED_BIG']}+ with the bigger fleet" if big else f"{C['JUMP_NEED']}+"
            for r in self.kessler_rocks(s):
                o.append({"id": "jump", "args": {"rock": r}, "group": "jump",
                          "label": f"Jump Kessler's claim on Rock {r} (roll {need}: its ship falls back for {plural(C['JUMP_BAN'], 'turn')}, yours takes the rock; miss: your ship goes home)"})
        return o

    def _lose_ship(self, s, rng, ev):
        s["ships"].pop(0)
        s["fleet"] = len(s["ships"])
        self.hit("fleet_lost")
        dead = fall(s, rng, 1)
        if dead:
            ev.append(fallen_text(dead))
        if s["fleet"] == 0:
            self.finish(s, "loss", "no ships left; the outfit is finished")

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "move":
            frm, to = self.mover(s), args["to"]
            dest = DOCK if to == "station" else int(to)
            s["ships"][s["ships"].index(frm)] = dest
            s["ships"].sort()
            if frm == DOCK:
                ev.append(f"A ship casts off from the station for Rock {dest}.")
            elif dest == DOCK:
                ev.append(f"A ship comes in from Rock {frm} to the station.")
            else:
                ev.append(f"A ship shifts from Rock {frm} to Rock {dest}.")
        elif a == "sell":
            p = self.price_now(s)
            tons = s["ore"]
            s["credits"] += tons * p
            s["ore"] = 0
            ev.append(f"You sell {plural(tons, 'ton')} at {p} a ton. Credits +{tons * p}.")
            drop = tons // C["GLUT"]
            if drop:
                s["price"] = max(0, s["price"] - drop)
                self.hit("glut")
                ev.append(f"The glut knocks the price down to {s['price']}.")
        elif a == "buy_ship":
            s["credits"] -= C["SHIP_COST"]
            s["ships"].append(DOCK)
            s["ships"].sort()
            s["fleet"] = len(s["ships"])
            if s["tier"] < 2:  # lit-ok: the third ship is tier 2
                s["tier"] = 2
                self.hit("third_ship")
                ev.append("A third sloop joins the fleet at the station. Raiding is open.")
            else:
                ev.append(f"Another sloop joins the fleet at the station. You have {plural(s['fleet'], 'ship')}.")
        elif a == "refinery":
            s["credits"] -= C["REFINERY_COST"]
            s["refinery"] = True
            s["tier"] = 3  # lit-ok: the refinery is tier 3
            self.hit("refinery")
            ev.append("The refinery lights up. Refined ore sells for double.")
        elif a == "raid":
            esc = self.fleet(s) >= C["ESCORT_FLEET"]
            ok, txt = rng.check(C["RAID_NEED_ESCORT"] if esc else C["RAID_NEED"], 6, "raid")  # lit-ok: a d6
            if ok:
                s["k_ships"].pop()
                s["k_fleet"] = len(s["k_ships"])
                s["ore"] += C["RAID_ORE"]
                self.hit("raid")
                ev.append(f"{txt}. Your boarders take a Kessler barge and its {C['RAID_ORE']} tons; its crew limps home in the lifeboat. Kessler's fleet is {s['k_fleet']}.")
            else:
                self.hit("raid_miss")
                ev.append(f"{txt}. The barge's escort holes your ship.")
                self._lose_ship(s, rng, ev)
        elif a == "jump":
            r = args["rock"]
            big = self.fleet(s) > s["k_fleet"]
            ok, txt = rng.check(C["JUMP_NEED_BIG"] if big else C["JUMP_NEED"], 6, "jump")  # lit-ok: a d6
            s["ships"].remove(self.mover(s))
            if ok:
                for k in s["k_ships"]:
                    if k["pos"] == r:
                        k["pos"], k["ban"] = DOCK, C["JUMP_BAN"]
                        break
                s["ships"].append(r)
                self.hit("jump")
                ev.append(f"{txt}. Your ship cuts across Kessler's bow on Rock {r} and its barge falls back to its dock for {plural(C['JUMP_BAN'], 'turn')}.")
            else:
                s["ships"].append(DOCK)
                self.hit("jump_miss")
                ev.append(f"{txt}. Kessler's barge holds the rock and your ship goes home to the station.")
            s["ships"].sort()
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        # your ships dig
        dug, idle = [], []
        total = 0
        for p in sorted(set(s["ships"])):
            if p == DOCK:
                continue
            rock = s["rocks"][p - 1]
            n = s["ships"].count(p)
            got = min(rock["grade"] * n, rock["reserve"])
            rock["reserve"] -= got
            total += got
            (dug if got else idle).append(f"Rock {p} {got}" if got else f"Rock {p}")
        s["ore"] += total
        if dug:
            ev.append(f"Your ships dig {plural(total, 'ton')}: " + ", ".join(dug) + ".")
        elif all(p == DOCK for p in s["ships"]):
            ev.append("Your ships dig nothing: none is on a rock.")
        else:
            ev.append("Your ships dig nothing: every rock they sit on is worked out.")
        if idle and dug:
            ev.append("Idle on worked-out " + " and ".join(idle) + ".")
        # Kessler digs where it sits
        for k in s["k_ships"]:
            if k["pos"] != DOCK:
                rock = s["rocks"][k["pos"] - 1]
                got = min(rock["grade"], rock["reserve"])
                rock["reserve"] -= got
                if k["pos"] in s["ships"]:
                    self.hit("contested")
                    ev.append(f"Kessler digs beside you on Rock {k['pos']}.")
        for i, rock in enumerate(s["rocks"]):
            if rock["reserve"] == 0 and not rock.get("done"):
                rock["done"] = True
                self.hit("worked_out")
                ev.append(f"Rock {i + 1} is worked out.")
        # the price recovers
        if s["price"] < C["PRICE"]:
            s["price"] += 1
            ev.append(f"The ore price recovers to {s['price']}.")
        # Kessler's fleet grows on its schedule
        if s["_turn"] % C["RIVAL_EVERY"] == 0:
            s["k_ships"].append({"pos": DOCK, "ban": 0})
            s["k_fleet"] = len(s["k_ships"])
            self.hit("kessler_ship")
            ev.append(f"A new Kessler barge docks. Kessler's fleet is {s['k_fleet']}.")
        if s["_turn"] == C["MID"]:
            s["k_ships"].append({"pos": DOCK, "ban": 0})
            s["k_fleet"] = len(s["k_ships"])
            self.hit("mid_ship")
            ev.append(f"Turn {C['MID']}: Kessler brings in an extra barge from the inner belt. Kessler's fleet is {s['k_fleet']}.")
        # Kessler moves: each free ship to the richest live rock no Kessler ship holds
        live = self.live_rocks(s)
        taken = set()
        for k in s["k_ships"]:
            if k["ban"] > 0:
                k["ban"] -= 1
                k["pos"] = DOCK
                continue
            free = [r for r in live if r not in taken]
            if not free:
                k["pos"] = DOCK
                continue
            best = max(free, key=lambda r: (s["rocks"][r - 1]["grade"], s["rocks"][r - 1]["reserve"], -r))
            k["pos"] = best
            taken.add(best)
        held = self.kessler_rocks(s)
        if held:
            names = [f"Rock {r}" for r in held]
            where = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
            ev.append(f"Kessler's ships sit on {where}.")
        else:
            ev.append("Kessler's ships are all at their dock.")
        if s["_turn"] + 1 == C["TURNS"]:
            self.hit("survey")
            ev.append(f"Turn {C['TURNS']}: the survey ship is in orbit; the charter is decided at its close.")
        return ev

    def status_line(self, s):
        return f"Fleet {s['fleet']} v Kessler {s['k_fleet']} | Credits {s['credits']} | Ore {s['ore']} | Price {self.price_now(s)} a ton"

    def board(self, s):
        C = self.C
        lines = []
        for i, r in enumerate(s["rocks"]):
            who = []
            mine = s["ships"].count(i + 1)
            if mine:
                who.append(f"{plural(mine, 'ship')} of yours")
            if (i + 1) in self.kessler_rocks(s):
                who.append("Kessler")
            state = "worked out" if r["reserve"] == 0 else f"grade {r['grade']}, {plural(r['reserve'], 'ton')} left"
            lines.append(f"Rock {i + 1}: {state}" + (f"; {' and '.join(who)}" if who else ""))
        lines.append(f"Ships at the station: {s['ships'].count(DOCK)}")
        lines.append(f"Tier: {self.LADDER['tiers'][s['tier'] - 1]}" + (" (refinery built)" if s["refinery"] else ""))
        nxt = C["RIVAL_EVERY"] - (s["_turn"] % C["RIVAL_EVERY"])
        lines.append(f"Kessler: {plural(s['k_fleet'], 'barge')}, next one in {plural(nxt, 'turn')}")
        return "\n".join(lines)

    def check_end(self, s):
        if s["fleet"] <= 0:
            return {"result": "loss", "reason": "no ships left; the outfit is finished"}
        return None

    def final_check(self, s):
        if not s["refinery"]:
            return {"result": "loss", "reason": "the survey closes with no refinery; the charter goes to Kessler"}
        if s["fleet"] <= s["k_fleet"]:
            return {"result": "loss", "reason": f"the survey closes with {plural(s['fleet'], 'ship')} against Kessler's {s['k_fleet']}; the charter goes to the bigger fleet"}
        return {"result": "win", "reason": f"the survey closes: your refinery and {plural(s['fleet'], 'ship')} against Kessler's {s['k_fleet']} take the belt charter"}

    # ------------------------------------------------------------ policy

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        fleet, k = self.fleet(s), s["k_fleet"]
        left = C["TURNS"] - s["_turn"]
        live = self.live_rocks(s)
        held = set(self.kessler_rocks(s))
        # the ladder first: the refinery, then ships while they can still pay for themselves
        if "refinery" in ids:
            return "refinery"
        if "buy_ship" in ids and (left > 6 or fleet <= k):  # lit-ok: a ship pays for itself in about six turns
            return "buy_ship"
        # cash in when the pile is big, the price is good, or a purchase is one sale away
        if "sell" in ids:
            p = self.price_now(s)
            want = C["REFINERY_COST"] if s["tier"] >= 2 and not s["refinery"] else C["SHIP_COST"]
            if s["ore"] >= C["_SELL_AT"] and s["price"] >= C["PRICE"] - 1 or s["credits"] + s["ore"] * p >= want and s["credits"] < want or left <= 1:
                return "sell"
        # the raid path: cut Kessler down when the odds are bought, or when he is pulling ahead
        if "raid" in ids and (fleet >= C["ESCORT_FLEET"] and (k >= fleet - 1 or s["ore"] < C["_SELL_AT"]) or k > fleet >= 3):  # lit-ok: three ships to risk one
            return "raid"
        # idle ships go to the richest free rock
        free = [r for r in live if r not in held]
        def yield_of(r):
            rock = s["rocks"][r - 1]
            return min(rock["grade"], rock["reserve"])

        frm = self.mover(s) if s["ships"] else DOCK
        best_free = max(free, key=lambda r: (yield_of(r), s["rocks"][r - 1]["reserve"])) if free else None
        # the jump path: Kessler sits on something clearly better than your poorest rock, and the odds are bought
        jumps = [o for o in options if o["id"] == "jump"]
        if jumps and fleet > k:
            target = max(jumps, key=lambda o: yield_of(o["args"]["rock"]))
            gain = yield_of(target["args"]["rock"]) - (yield_of(frm) if frm != DOCK else 0)
            if gain >= 2 and (best_free is None or yield_of(target["args"]["rock"]) > yield_of(best_free)):  # lit-ok: worth a roll
                return target
        # a ship at the station, or on a worked-out or contested rock, goes to the richest free rock
        if "move" in ids and best_free is not None and (frm == DOCK or yield_of(frm) == 0 or frm in held) and best_free != frm:
            return {"id": "move", "args": {"to": best_free}}
        if "move" in ids and best_free is not None and frm != DOCK and yield_of(best_free) > yield_of(frm) + 1:
            return {"id": "move", "args": {"to": best_free}}
        if jumps and not free:
            return max(jumps, key=lambda o: yield_of(o["args"]["rock"]))
        if "sell" in ids and s["ore"] > 0:
            return "sell"
        if "move" in ids and frm == DOCK and live:
            return {"id": "move", "args": {"to": max(live, key=yield_of)}}
        return rng.choice(options)


if __name__ == "__main__":
    run(G)
