"""Brass Ring: a /play engine.

You run the two cabs of a cab guild in a clockwork city. Eight guild quarters ring the Clock Tower. A masked saboteur,
the Gearwright, unwinds one quarter's mainspring a night, and the Tribunal that sits on the last night will hang the
cabmaster unless the cabs have caught him in the act often enough. Heat is how closely the Watch is looking at you.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

TOWER = 0  # lit-ok: the hub's index; quarters are 1..QUARTERS
CABS = ("Red", "Black")


class G(Game):
    name = "Brass Ring"

    CONSTANTS = {
        "NIGHTS": 16,
        "QUARTERS": 8,
        "HEAT_START": 3,
        "HEAT_MAX": 10,
        "MOVE_HEAT": 1,
        "LIE_LOW": 2,
        "MAX_DOORS": 2,
        "MID_NIGHT": 9,
        "CATCH_PROOF": 1,
        "CATCH_HEAT": 2,
        "BAIT_HEAT": 1,
        "BAIT_NEED": 4,
        "BAIT_NEED_KNOWN": 3,
        "BAIT_FAIL_HEAT": 2,
        "TOWER_PROOF": 2,
        "RAID_UNLOCK": 2,
        "RAID_NEED": 4,
        "RAID_NEED_THERE": 3,
        "RAID_PROOF": 3,
        "RAID_FAIL_HEAT": 4,
        "TRIBUNAL_NEED": 11,
        "DIE": 6,
    }

    RULES = """
1. Eight quarters, 1 to {QUARTERS} clockwise, ring the Tower. Your cabs are Red and Black. Each night move one cab one step: to a neighbor quarter, or to or from the Tower.
2. The Gearwright unwinds one quarter a night. At dusk the Watch reports where he bought grease; he strikes 1 to {MAX_DOORS} quarters from there, always the same count and direction (his habit) until night {MID_NIGHT}, when it changes.
3. A lit cab in the struck quarter catches him: Proof +{CATCH_PROOF}, but the Watch finds it there: Heat +{CATCH_HEAT}. A cab next door hears the spring snap and learns where he struck. A Tower cab sees only the Tower.
4. A move costs Heat +{MOVE_HEAT}. Lie low, lanterns out, cabs where they stand: Heat -{LIE_LOW} (never below 0), but they catch nothing that night, though they still hear. Start at Heat {HEAT_START}; at {HEAT_MAX} you are arrested and lose.
5. Leak that the Tower guard stands down tomorrow (Heat +{BAIT_HEAT}): roll {BAIT_NEED}+, or {BAIT_NEED_KNOWN}+ once you know his habit, and tomorrow night he strikes the Tower, not the ring. A miss is traced to you: Heat +{BAIT_FAIL_HEAT}.
6. The leak can be tried once before night {MID_NIGHT} and once after, never on night {NIGHTS}. Caught at the Tower by a lit cab there, with the Tower guard as witness: Proof +{TOWER_PROOF} and no Heat.
7. At Proof {RAID_UNLOCK}, and {RAID_UNLOCK} Proof after each raid, his address turns up and a raid is offered: roll {RAID_NEED}+, or {RAID_NEED_THERE}+ with a cab in that quarter, for Proof +{RAID_PROOF}; a miss costs Heat +{RAID_FAIL_HEAT}. He moves house.
8. After night {NIGHTS} the Tribunal sits. Roll a d{DIE} and add your Proof: {TRIBUNAL_NEED} or more exposes the Gearwright and you win. Less, and you are convicted in his place.
"""

    ACTIONS = ["move", "lie_low", "bait", "raid"]
    TAGS = ["catch", "heard", "silent", "habit_learned", "habit_change", "bait", "bait_miss", "tower_catch", "tower_missed",
            "lodging", "raid", "raid_miss", "tribunal", "arrested"]
    GAMBITS = {"bait": {"rival": True}, "raid": {}}
    RIVAL_KEYS = ["tell", "bait"]
    TRACKED = ["heat", "proof", "cabs"]

    BOUNDS = {"heat": (0, 30), "proof": (0, 30), "tell": (1, 8), "bait": (0, 2), "receipt_at": (0, 40)}
    REACH = {"heat": "HEAT_MAX", "proof": "RAID_UNLOCK"}
    GATES = {
        "move": {"_if": lambda g, s: True},
        "lie_low": {"_if": lambda g, s: True},
        "bait": {"!baited": 1, "!bait": 1, "_if": lambda g, s: s["_turn"] < g.C["NIGHTS"]},
        "raid": {"_if": lambda g, s: s["lodging"] is not None},
    }

    @property
    def turns(self):
        return self.C["NIGHTS"]

    # ------------------------------------------------------------ geometry

    def wrap(self, q):
        n = self.C["QUARTERS"]
        return (q - 1) % n + 1

    def offsets(self):
        m = self.C["MAX_DOORS"]
        return [-d for d in range(m, 0, -1)] + list(range(1, m + 1))

    def neighbors(self, q):
        return [self.wrap(q - 1), self.wrap(q + 1)]

    def place(self, q):
        return "the Tower" if q == TOWER else f"Quarter {q}"

    def doors(self, off):
        way = "clockwise" if off > 0 else "counterclockwise"
        return f"{plural(abs(off), 'quarter')} {way}"

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C

        def r1(t):
            s = t.fresh()
            t.eq(s["cabs"], {"Red": TOWER, "Black": TOWER}, "both cabs start in the Tower yard")
            for q in range(1, C["QUARTERS"] + 1):
                t.ok(t.offered(s, "move", cab="Red", to=q), f"a Tower cab can reach Quarter {q}")
            t.ok(not t.offered(s, "move", cab="Red", to=0) and not t.offered(s, "move", cab="Red", to="Tower"), "a Tower cab cannot move to the Tower")
            t.eq(t.label(s, "move", cab="Red"), f"Send the Red cab out from the Tower to any quarter (Heat +{C['MOVE_HEAT']})")
            s = t.fresh(cabs={"Red": 3, "Black": TOWER})
            t.eq(t.label(s, "move", cab="Red"), f"Send the Red cab from Quarter 3 to 2, 4 or the Tower (Heat +{C['MOVE_HEAT']})")
            for to in (2, 4, "Tower"):
                t.ok(t.offered(s, "move", cab="Red", to=to), f"a ring cab can step to {to}")
            for to in (1, 5, 6, 7, 8):
                t.ok(not t.offered(s, "move", cab="Red", to=to), f"a ring cab cannot jump to {to}")
            s = t.fresh(cabs={"Red": 8, "Black": 1})
            t.ok(t.offered(s, "move", cab="Red", to=1), "the ring closes: 8 touches 1")
            t.ok(t.offered(s, "move", cab="Black", to=8), "the ring closes: 1 touches 8")
            t.eq(t.label(s, "move", cab="Red"), f"Send the Red cab from Quarter 8 to 7, 1 or the Tower (Heat +{C['MOVE_HEAT']})")
            s = t.fresh(cabs={"Red": 3, "Black": TOWER})
            events = t.apply(s, "move", {"cab": "Red", "to": "Tower"})
            t.eq(s["cabs"]["Red"], TOWER, "the cab arrives")
            t.has(events, f"The Red cab rolls from Quarter 3 to the Tower. Heat +{C['MOVE_HEAT']}.")
            s = t.fresh(cabs={"Red": 3, "Black": TOWER})
            t.apply(s, "move", {"cab": "Black", "to": 7})
            t.eq(s["cabs"], {"Red": 3, "Black": 7}, "only the sent cab moves")
            s = t.fresh(cabs={"Red": 3, "Black": TOWER}, tell=5)
            s, _ = t.step(s, "move", {"cab": "Black", "to": 7})
            t.eq(s["_turn"], 2, "one action ends the night")
            t.eq(t.status(t.fresh(cabs={"Red": 3, "Black": TOWER}, tell=5, heat=4, proof=1)),
                 "Heat 4 | Proof 1 | Cabs: Red Q3, Black Tower | Gearwright: grease at Q5, habit unknown", "the status line")
            t.eq(t.status(t.fresh(cabs={"Red": 3, "Black": 6}, tell=5, habit=-2)),
                 f"Heat {C['HEAT_START']} | Proof 0 | Cabs: Red Q3, Black Q6 | Gearwright: grease at Q5, strikes 2 quarters counterclockwise")
            t.eq(self.turns, C["NIGHTS"], "the budget is NIGHTS")

        def r2(t):
            tells, offs = set(), set()
            for sd in range(1, 60):
                s = t.fresh(seed=sd)
                tells.add(s["tell"])
                offs.add(s["hidden"]["offset"])
            t.eq(tells, set(range(1, C["QUARTERS"] + 1)), "the first grease report can be any quarter")
            want = set(range(-C["MAX_DOORS"], 0)) | set(range(1, C["MAX_DOORS"] + 1))
            t.eq(offs, want, "the habit is 1 to MAX_DOORS quarters, either way, never 0")
            t.eq(set(self.offsets()), want, "the engine's list of habits agrees")
            s = t.fresh(tell=3, hidden__offset=2, cabs={"Red": 5, "Black": TOWER})
            events = t.advance(s, turn=2)
            t.has(events, "unwinds Quarter 5", "the strike lands tell plus offset")
            s = t.fresh(tell=1, hidden__offset=-2, cabs={"Red": 7, "Black": TOWER})
            events = t.advance(s, turn=2)
            t.has(events, "unwinds Quarter 7", "the ring wraps counterclockwise")
            s = t.fresh(tell=8, hidden__offset=1, cabs={"Red": 1, "Black": TOWER})
            events = t.advance(s, turn=2)
            t.has(events, "unwinds Quarter 1", "the ring wraps clockwise")
            # tomorrow's grease report
            s = t.fresh(tell=3, cabs={"Red": TOWER, "Black": TOWER})
            events = t.advance(s, turn=2, dice=[6])
            t.eq(s["tell"], 6, "the dusk report sets tomorrow's grease quarter")
            t.has(events, "Dusk report: gear-grease bought in Quarter 6.")
            # the habit changes on MID_NIGHT: redrawn at the dusk before it
            s = t.fresh(tell=3, hidden__offset=2, habit=2, ruled_out=[-1], cabs={"Red": TOWER, "Black": TOWER})
            self._hits.clear()
            events = t.advance(s, turn=C["MID_NIGHT"] - 1, choices=[-1], dice=[4])
            t.eq(s["hidden"]["offset"], -1, "a new habit is drawn")
            t.ok(s["habit"] is None and s["ruled_out"] == [2], "the habit is gone, and the old one is the one way he will not walk")
            s3 = t.fresh(tell=3, hidden__offset=2, habit=None, ruled_out=[-1], cabs={"Red": TOWER, "Black": TOWER})
            t.advance(s3, turn=C["MID_NIGHT"] - 1, choices=[-1], dice=[4])
            t.eq(s3["ruled_out"], [], "a habit never learned rules nothing out after the change")
            t.has(events, f"Night {C['MID_NIGHT']}: he has seen your cabs. His habit changes.")
            t.ok("habit_change" in self._hits, "the change is noted")
            t.in_order(events, ["His habit changes", "Dusk report"], "the change is announced before tomorrow's report")
            s = t.fresh(tell=3, hidden__offset=2, habit=2, cabs={"Red": TOWER, "Black": TOWER})
            self._hits.clear()
            t.advance(s, turn=C["MID_NIGHT"] - 2, dice=[4])
            t.ok(s["hidden"]["offset"] == 2 and s["habit"] == 2 and "habit_change" not in self._hits, "no change on other nights")
            s = t.fresh(tell=3, hidden__offset=2, habit=2, cabs={"Red": TOWER, "Black": TOWER})
            t.advance(s, turn=C["MID_NIGHT"], dice=[4])
            t.ok(s["hidden"]["offset"] == 2, "the habit changes once")
            for sd in range(1, 40):
                s = t.fresh(seed=sd, tell=3, hidden__offset=2, cabs={"Red": TOWER, "Black": TOWER})
                t.advance(s, turn=C["MID_NIGHT"] - 1, seed=sd)
                t.ok(s["hidden"]["offset"] != 2 and s["hidden"]["offset"] in self.offsets(), "the new habit differs from the old")

        def r3(t):
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": TOWER}, heat=3, proof=0)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.eq(s["proof"], C["CATCH_PROOF"], "a cab in the struck quarter takes proof")
            t.eq(s["heat"], 3 + C["CATCH_HEAT"], "and the Watch finds it there")
            t.has(events, f"The Gearwright unwinds Quarter 4 under the Red cab's lantern: a mask, a brass key, a face. Proof +{C['CATCH_PROOF']}.")
            t.has(events, f"The Watch finds your cab at the scene. Heat +{C['CATCH_HEAT']}.")
            t.in_order(events, ["unwinds Quarter 4", "Heat +", "Dusk report"])
            t.eq(s["habit"], 1, "seeing the strike teaches the habit")
            t.has(events, "He struck 1 quarter clockwise of the grease. Now you know his habit.")
            t.ok({"catch", "habit_learned"} <= self._hits)
            t.eq(s["last_strike"], 4, "the struck quarter is known")
            # both cabs there: one catch, one heat
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": 4}, heat=3)
            t.advance(s, turn=2)
            t.ok(s["proof"] == C["CATCH_PROOF"] and s["heat"] == 3 + C["CATCH_HEAT"], "two cabs at the scene count once")
            events = t.advance(t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": 4}, heat=3), turn=2)
            t.has(events, "under the Red and Black cabs' lanterns")
            t.has(events, f"The Watch finds your cabs at the scene. Heat +{C['CATCH_HEAT']}.")
            events = t.advance(t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": 4}, heat=3, dark=True), turn=2)
            t.has(events, "The Red and Black cabs sit dark in Quarter 4 as the mainspring snaps beside them: he unwinds Quarter 4. No lantern, no face.")
            # next door hears
            s = t.fresh(tell=3, hidden__offset=2, cabs={"Red": 4, "Black": TOWER}, heat=3)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.ok(s["proof"] == 0 and s["heat"] == 3, "hearing is not proof and costs nothing")
            t.has(events, "From Quarter 4 the Red cab hears a mainspring snap next door: he unwinds Quarter 5.")
            t.eq(s["habit"], 2, "hearing teaches the habit")
            t.has(events, "He struck 2 quarters clockwise of the grease. Now you know his habit.")
            t.ok("heard" in self._hits)
            s = t.fresh(tell=3, hidden__offset=-2, cabs={"Red": 8, "Black": TOWER}, heat=3)
            events = t.advance(s, turn=2)
            t.has(events, "From Quarter 8 the Red cab hears a mainspring snap next door: he unwinds Quarter 1.", "hearing wraps the ring")
            # nothing nearby: silence, and what the silence rules out
            s = t.fresh(tell=3, hidden__offset=-2, cabs={"Red": 4, "Black": TOWER}, heat=3)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.has(events, "A mainspring snaps somewhere on the ring. No guild admits which.")
            t.ok(s["habit"] is None and s["last_strike"] is None, "nothing learned outright")
            t.eq(s["ruled_out"], [1, 2], "the quiet around the Red cab rules out the quarters it covered")
            t.has(events, "A mainspring snaps somewhere on the ring. No guild admits which. Nothing within earshot of your cabs, so not 1 quarter clockwise or 2 quarters clockwise.")
            # a second quiet night on the other side leaves one way, and that is his habit
            s["tell"], s["cabs"]["Red"] = 3, 3  # covers 2, 3, 4: quiet again rules out 1 counterclockwise
            self._hits.clear()
            events = t.advance(s, turn=3)
            t.eq(s["habit"], -2, "three ways ruled out leaves the fourth")
            t.eq(s["ruled_out"], [], "the list is cleared once the habit is known")
            t.has(events, "Only one way is left: he strikes 2 quarters counterclockwise of the grease. Now you know his habit.")
            t.ok("habit_learned" in self._hits)
            # learning clears a non-empty list
            s = t.fresh(tell=3, hidden__offset=1, ruled_out=[-1], cabs={"Red": 4, "Black": TOWER}, heat=3)
            t.advance(s, turn=2)
            t.ok(s["habit"] == 1 and s["ruled_out"] == [], "a catch wipes the ruled-out list")
            # a dark cab next door still hears
            s = t.fresh(tell=3, hidden__offset=2, cabs={"Red": 4, "Black": TOWER}, heat=3, dark=True)
            events = t.advance(s, turn=2)
            t.ok(s["habit"] == 2 and s["proof"] == 0, "lanterns out, ears open")
            t.has(events, "From Quarter 4 the Red cab hears a mainspring snap next door: he unwinds Quarter 5.")
            t.ok("silent" in self._hits)
            # a known habit: silence rules out nothing more
            s = t.fresh(tell=3, hidden__offset=-2, habit=-2, cabs={"Red": 4, "Black": TOWER}, heat=3)
            t.advance(s, turn=2)
            t.eq(s["ruled_out"], [], "once the habit is known the list of ruled-out doors stays empty")
            # the Tower sees nothing
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": TOWER, "Black": TOWER}, heat=3)
            events = t.advance(s, turn=2)
            t.ok(s["habit"] is None and s["ruled_out"] == [] and s["proof"] == 0, "Tower cabs see and hear nothing")
            t.has(events, "No guild admits which")
            # a known habit is not announced twice
            s = t.fresh(tell=3, hidden__offset=1, habit=1, cabs={"Red": 4, "Black": TOWER}, heat=3)
            events = t.advance(s, turn=2)
            t.ok(not any("Now you know" in e for e in events), "no second lesson")

        def r4(t):
            s = t.fresh()
            t.eq(s["heat"], C["HEAT_START"], "starting heat")
            s = t.fresh(cabs={"Red": 3, "Black": TOWER}, heat=4)
            t.apply(s, "move", {"cab": "Red", "to": 4})
            t.eq(s["heat"], 4 + C["MOVE_HEAT"], "a move costs heat")
            t.eq(set(t.ids(s)), {"move", "lie_low", "bait"}, "only the sheet's moves are on the table before the raid")
            s = t.fresh(cabs={"Red": 3, "Black": 6}, heat=5)
            t.eq(t.label(s, "lie_low"), f"Lie low with the lanterns out (Heat -{C['LIE_LOW']}, no catch tonight)")
            t.eq(t.label(t.fresh(heat=C["LIE_LOW"]), "lie_low"), f"Lie low with the lanterns out (Heat -{C['LIE_LOW']}, no catch tonight)", "exactly LIE_LOW still shows the full drop")
            events = t.apply(s, "lie_low")
            t.eq(s["heat"], 5 - C["LIE_LOW"], "lying low cools the Watch")
            t.eq(s["cabs"], {"Red": 3, "Black": 6}, "nobody moves")
            t.ok(s["dark"], "the lanterns are out")
            t.has(events, f"The lanterns go out and the cabs sit still. Heat -{C['LIE_LOW']}.")
            s = t.fresh(heat=1)
            t.eq(t.label(s, "lie_low"), "Lie low with the lanterns out (Heat to 0, no catch tonight)")
            events = t.apply(s, "lie_low")
            t.eq(s["heat"], 0, "heat does not go below 0")
            t.has(events, "The lanterns go out and the cabs sit still. Heat -1.")
            s = t.fresh(heat=0)
            t.eq(t.label(s, "lie_low"), "Lie low with the lanterns out (Heat is already 0, no catch tonight)")
            events = t.apply(s, "lie_low")
            t.has(events, "The lanterns go out and the cabs sit still. Heat stays at 0.")
            # dark cabs catch nothing, but a cab beside the snap still learns where
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": TOWER}, heat=3, dark=True)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.ok(s["proof"] == 0 and s["heat"] == 3, "a dark cab at the scene takes no proof and draws no Watch")
            t.has(events, "The Red cab sits dark in Quarter 4 as the mainspring snaps beside it: he unwinds Quarter 4. No lantern, no face.")
            t.ok(s["habit"] == 1 and s["last_strike"] == 4 and "heard" in self._hits, "it still learns his habit")
            t.ok(not s["dark"], "the lanterns are lit again at dusk")
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": TOWER}, heat=3, dark=False)
            t.advance(s, turn=2)
            t.eq(s["proof"], C["CATCH_PROOF"], "with lanterns lit the same cab catches him")
            # arrest: in the yard, and at the scene
            s = t.fresh(cabs={"Red": 3, "Black": TOWER}, heat=C["HEAT_MAX"] - 1)
            self._hits.clear()
            events = t.apply(s, "move", {"cab": "Red", "to": 4})
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "a move that reaches HEAT_MAX ends the game")
            t.eq(s["_ended"]["reason"], f"arrested: Heat reached {C['HEAT_MAX']}")
            t.has(events, "The Watch is waiting at the yard gate with a warrant.")
            t.ok("arrested" in self._hits)
            s = t.fresh(cabs={"Red": 3, "Black": TOWER}, heat=C["HEAT_MAX"] - 2)
            t.apply(s, "move", {"cab": "Red", "to": 4})
            t.ok(not s["_ended"] and self.check_end(s) is None, "one under the warrant is still free")
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": TOWER}, heat=C["HEAT_MAX"] - C["CATCH_HEAT"])
            events = t.advance(s, turn=2)
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "found at the scene with Heat at the limit: arrested at dusk")
            t.ok(s["proof"] == C["CATCH_PROOF"], "the proof is taken before the arrest")
            t.ok(not any("Dusk report" in e for e in events), "no report for a tomorrow that will not come")
            t.ok(s["tell"] == 3, "no new grease quarter after the arrest")
            s = t.fresh(tell=3, hidden__offset=1, cabs={"Red": 4, "Black": TOWER}, heat=C["HEAT_MAX"] - C["CATCH_HEAT"], proof=C["RAID_UNLOCK"] - 1)
            events = t.advance(s, turn=2)
            t.ok(s["_ended"] and s["lodging"] is None and not any("receipt" in e for e in events), "an arrest at dusk comes before the receipt")

        def r5(t):
            s = t.fresh(cabs={"Red": 3, "Black": 6}, heat=4)
            t.eq(t.label(s, "bait"), f"Leak that the Tower guard stands down tomorrow night (Heat +{C['BAIT_HEAT']}; roll {C['BAIT_NEED']}+ and he strikes the Tower tomorrow, miss: Heat +{C['BAIT_FAIL_HEAT']})")
            s2 = t.fresh(cabs={"Red": TOWER, "Black": 6}, heat=4, habit=1)
            t.eq(t.label(s2, "bait"), f"Leak that the Tower guard stands down tomorrow night (Heat +{C['BAIT_HEAT']}; roll {C['BAIT_NEED_KNOWN']}+ since you know his habit and he strikes the Tower tomorrow, miss: Heat +{C['BAIT_FAIL_HEAT']})")
            self._hits.clear()
            events = t.apply(s, "bait", dice=[C["BAIT_NEED"]])
            t.eq(s["heat"], 4 + C["BAIT_HEAT"], "the leak costs heat")
            t.ok(s["bait"] == 2 and s["baited"], "he bites, and the rumor is spent")
            t.has(events, f"roll {C['BAIT_NEED']} (need {C['BAIT_NEED']}+) bait success. The rumor takes. He has heard the Tower guard stands down.")
            t.ok("bait" in self._hits)
            t.ok(not t.offered(s, "bait"), "once only")
            # tonight he still works the ring; the report at dusk says where he goes tomorrow
            s["tell"], s["hidden"]["offset"], s["cabs"] = 3, 1, {"Red": 7, "Black": 6}
            events = t.advance(s, turn=2, dice=[5])
            t.has(events, "A mainspring snaps somewhere on the ring", "the ring is struck tonight as usual")
            t.eq(s["bait"], 1, "tomorrow is the Tower night")
            t.has(events, "Dusk report: word that the Tower guard stands down is in every tavern. He comes for the Tower tomorrow night.")
            t.ok(not any("gear-grease" in e for e in events), "no grease report on a Tower night")
            t.eq(s["tell"], 3, "no new grease quarter is drawn for a Tower night")
            t.eq(t.status(s), "Heat 5 | Proof 0 | Cabs: Red Q7, Black Q6 | Gearwright: coming for the Tower, habit unknown")
            # the miss
            s = t.fresh(cabs={"Red": 3, "Black": 6}, heat=4)
            self._hits.clear()
            events = t.apply(s, "bait", dice=[C["BAIT_NEED"] - 1])
            t.eq(s["heat"], 4 + C["BAIT_HEAT"] + C["BAIT_FAIL_HEAT"], "a miss is traced back to you")
            t.ok(s["bait"] == 0 and s["baited"], "he does not bite, and will not hear the rumor again")
            t.has(events, f"roll {C['BAIT_NEED'] - 1} (need {C['BAIT_NEED']}+) bait fail. The rumor falls flat and the Watch asks who started it. Heat +{C['BAIT_FAIL_HEAT']}.")
            t.ok("bait_miss" in self._hits)
            t.ok(not t.offered(s, "bait"), "a miss is also once")
            s = t.fresh(cabs={"Red": TOWER, "Black": 6}, heat=4, habit=-2)
            t.apply(s, "bait", dice=[C["BAIT_NEED_KNOWN"]])
            t.ok(s["bait"] == 2, "knowing his habit lowers the need")
            s = t.fresh(cabs={"Red": TOWER, "Black": 6}, heat=4)
            t.apply(s, "bait", dice=[C["BAIT_NEED_KNOWN"]])
            t.ok(s["bait"] == 0, "without it the lower roll is a miss")
            s = t.fresh(cabs={"Red": 3, "Black": 6}, heat=C["HEAT_MAX"] - C["BAIT_HEAT"] - C["BAIT_FAIL_HEAT"])
            t.apply(s, "bait", dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "a traced rumor can be the last entry in the book")
            s = t.fresh(cabs={"Red": 3, "Black": 6})
            s["_turn"] = C["NIGHTS"]
            t.ok(not t.offered(s, "bait"), "no leak on the last night: tomorrow never comes")
            s["_turn"] = C["NIGHTS"] - 1
            t.ok(t.offered(s, "bait"), "the night before is the last chance")
            # the Tower night: the ring is spared
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, tell=3, hidden__offset=1, bait=1, baited=True, heat=4)
            events = t.advance(s, turn=2)
            t.ok(not any("Quarter 4" in e and "unwinds" in e for e in events), "the ring is spared on the Tower night")
            t.ok(s["bait"] == 0, "the bait is used up at dusk")
            t.ok(any("gear-grease" in e for e in events), "the grease report returns afterwards")

        def r6(t):
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, tell=3, hidden__offset=1, bait=1, baited=True, heat=4, proof=1)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.eq(s["proof"], 1 + C["TOWER_PROOF"], "a Tower catch is worth double")
            t.eq(s["heat"], 4, "and costs no heat")
            t.has(events, f"The Gearwright comes for the Tower mainspring and walks into the Red cab's lantern. The guard who never stood down sees everything. Proof +{C['TOWER_PROOF']}.")
            t.ok("tower_catch" in self._hits)
            t.eq(s["last_strike"], TOWER, "the Tower is where he struck")
            t.ok(s["habit"] is None, "a Tower strike says nothing about his habit")
            s = t.fresh(cabs={"Red": TOWER, "Black": TOWER}, bait=1, baited=True, heat=4)
            events = t.advance(s, turn=2)
            t.eq(s["proof"], C["TOWER_PROOF"], "two cabs at the Tower still count once")
            t.has(events, "walks into the Red and Black cabs' lanterns")
            s = t.fresh(cabs={"Red": 3, "Black": 4}, bait=1, baited=True, heat=4)
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.ok(s["proof"] == 0 and s["heat"] == 4, "no cab at the Tower: nothing gained, nothing lost")
            t.has(events, "The Gearwright comes for the Tower mainspring. No cab of yours is there; the guards chase a shadow.")
            t.ok("tower_missed" in self._hits)
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, bait=1, baited=True, heat=4, dark=True)
            events = t.advance(s, turn=2)
            t.ok(s["proof"] == 0, "a dark cab at the Tower catches nothing either")
            t.has(events, "The Gearwright comes for the Tower mainspring and slips past the dark Red cab. The guards chase a shadow.")
            s = t.fresh(cabs={"Red": TOWER, "Black": TOWER}, baited=True, tell=3, hidden__offset=1)
            t.ok(not t.offered(s, "bait"), "the rumor is spent")
            t.advance(s, turn=C["MID_NIGHT"] - 1, dice=[4])
            t.ok(not s["baited"] and t.offered(s, "bait"), "with his new habit he forgets the rumor")
            s = t.fresh(cabs={"Red": TOWER, "Black": TOWER}, baited=True, tell=3, hidden__offset=1)
            t.advance(s, turn=C["MID_NIGHT"] - 2, dice=[4])
            t.ok(s["baited"], "on any other night it stays spent")
            # a rumor already in play cannot be leaked again, even after the night-9 reset
            s = t.fresh(cabs={"Red": TOWER, "Black": TOWER}, baited=True, bait=2, tell=3, hidden__offset=1)
            t.advance(s, turn=C["MID_NIGHT"] - 1, dice=[4])
            t.ok(s["bait"] == 1 and not s["baited"] and not t.offered(s, "bait"), "the pending Tower night is kept and no second leak is offered")
            t.advance(s, turn=C["MID_NIGHT"])
            t.ok(s["bait"] == 0 and s["last_strike"] == TOWER and t.offered(s, "bait"), "he came to the Tower on night 9; the second leak opens after")
            s = t.fresh(cabs={"Red": TOWER, "Black": TOWER}, bait=2, baited=True)
            t.ok(not t.offered(s, "bait"), "no leak while a rumor is spreading")

        def r7(t):
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, tell=3, hidden__offset=1, hidden__lodging=6, proof=C["RAID_UNLOCK"] - 1, heat=2)
            t.ok(not t.offered(s, "raid") and s["lodging"] is None, "no raid before the receipt")
            t.eq(s["receipt_at"], C["RAID_UNLOCK"], "the first receipt comes at RAID_UNLOCK proof")
            self._hits.clear()
            events = t.advance(s, turn=2)
            t.eq(s["proof"], C["RAID_UNLOCK"], "the catch brings proof to the receipt")
            t.eq(s["lodging"], 6, "the receipt names his lodging")
            t.has(events, "Among the evidence, a rent receipt with his address: the Gearwright lodges in Quarter 6.")
            t.in_order(events, ["Proof +", "rent receipt", "Dusk report"])
            t.ok("lodging" in self._hits)
            t.ok(t.offered(s, "raid"), "the raid is on the table")
            t.eq(t.label(s, "raid"), f"Raid his lodging in Quarter 6 (roll {C['RAID_NEED']}+ for Proof +{C['RAID_PROOF']}, miss: Heat +{C['RAID_FAIL_HEAT']})")
            s = t.fresh(cabs={"Red": 6, "Black": 4}, lodging=6, hidden__lodging=6, proof=4, heat=2, receipt_at=2)
            t.eq(t.label(s, "raid"), f"Raid his lodging in Quarter 6 (roll {C['RAID_NEED_THERE']}+ with your cab there for Proof +{C['RAID_PROOF']}, miss: Heat +{C['RAID_FAIL_HEAT']})")
            self._hits.clear()
            events = t.apply(s, "raid", dice=[C["RAID_NEED_THERE"]], choices=[2])
            t.eq(s["proof"], 4 + C["RAID_PROOF"], "a good raid fills the strongbox")
            t.eq(s["heat"], 2, "a good raid costs no heat")
            t.has(events, f"roll {C['RAID_NEED_THERE']} (need {C['RAID_NEED_THERE']}+) raid success. His workbench, his masks, his ledger of the guilds. Proof +{C['RAID_PROOF']}. He has moved house.")
            t.ok(s["lodging"] is None and not t.offered(s, "raid"), "he has moved: no raid until the next receipt")
            t.eq(s["hidden"]["lodging"], 2, "his new lodging is drawn")
            t.eq(s["receipt_at"], 4 + C["RAID_PROOF"] + C["RAID_UNLOCK"], "the next receipt comes RAID_UNLOCK proof later")
            t.ok("raid" in self._hits)
            for sd in range(1, 40):
                s2 = t.fresh(seed=sd, cabs={"Red": 6, "Black": 4}, lodging=6, hidden__lodging=6, proof=4, heat=2, receipt_at=2)
                t.apply(s2, "raid", seed=sd)
                t.ok(s2["hidden"]["lodging"] != 6 and 1 <= s2["hidden"]["lodging"] <= C["QUARTERS"], "he never moves back into the same rooms")
            # the next receipt
            s["cabs"], s["tell"], s["hidden"]["offset"] = {"Red": 4, "Black": TOWER}, 3, 1
            t.advance(s, turn=2)
            t.ok(s["lodging"] is None, "one more proof is not yet the next receipt")
            s["cabs"]["Red"], s["tell"] = 4, 3
            t.advance(s, turn=3)
            t.eq(s["lodging"], 2, "two more proof and the next receipt names the new rooms")
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, lodging=6, hidden__lodging=6, proof=4, heat=2, receipt_at=2)
            t.apply(s, "raid", dice=[C["RAID_NEED_THERE"]])
            t.eq(s["proof"], 4, "without a cab there the lower roll is a miss")
            t.eq(s["heat"], 2 + C["RAID_FAIL_HEAT"], "a brawl in a guild quarter")
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, lodging=6, hidden__lodging=6, proof=4, heat=2, receipt_at=2)
            self._hits.clear()
            events = t.apply(s, "raid", dice=[C["RAID_NEED"] - 1])
            t.has(events, f"roll {C['RAID_NEED'] - 1} (need {C['RAID_NEED']}+) raid fail. The rooms are empty and the neighbors call the Watch. Heat +{C['RAID_FAIL_HEAT']}. He has moved house.")
            t.ok(s["lodging"] is None and not t.offered(s, "raid"), "a miss also sends him to new rooms")
            t.eq(s["receipt_at"], 4 + C["RAID_UNLOCK"], "after a miss the next receipt is RAID_UNLOCK proof away")
            t.ok("raid_miss" in self._hits)
            s = t.fresh(cabs={"Red": TOWER, "Black": 4}, lodging=6, hidden__lodging=6, proof=4, heat=C["HEAT_MAX"] - C["RAID_FAIL_HEAT"], receipt_at=2)
            t.apply(s, "raid", dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "a brawl can bring the warrant")
            lodgings = {t.fresh(seed=sd)["hidden"]["lodging"] for sd in range(1, 60)}
            t.eq(lodgings, set(range(1, C["QUARTERS"] + 1)), "he may lodge in any quarter")

        def r8(t):
            P = C["TRIBUNAL_NEED"] - 4  # proof that leaves a 4+ to roll
            s = t.fresh(proof=P, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            s["_turn"] = C["NIGHTS"]
            t.ok(self.check_end(s) is None, "the last night is still played")
            self._hits.clear()
            events = t.advance(s, turn=C["NIGHTS"], dice=[4])
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "roll plus proof at the mark exposes him")
            t.eq(s["_ended"]["reason"], "the Gearwright is exposed before the Tribunal")
            t.has(events, "The Tribunal sits. roll 4 (need 4+) tribunal success. The mask comes off in open court.")
            t.ok("tribunal" in self._hits)
            t.ok(not any("Dusk report" in e for e in events), "no report after the Tribunal")
            s = t.fresh(proof=P, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            events = t.advance(s, turn=C["NIGHTS"], dice=[3])
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "one short is a conviction")
            t.eq(s["_ended"]["reason"], "convicted in the Gearwright's place")
            t.has(events, "roll 3 (need 4+) tribunal fail. The Tribunal finds the cabmaster guilty.")
            s = t.fresh(proof=C["TRIBUNAL_NEED"] - 1, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            events = t.advance(s, turn=C["NIGHTS"], dice=[1])
            t.ok(s["_ended"]["result"] == "win", "proof one under the mark needs only a 1")
            s = t.fresh(proof=C["TRIBUNAL_NEED"] - C["DIE"] - 1, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            events = t.advance(s, turn=C["NIGHTS"], dice=[C["DIE"]])
            t.ok(s["_ended"]["result"] == "loss", "too little proof for any roll")
            t.has(events, "The Tribunal sits. With so little proof it does not even hear you.")
            s = t.fresh(proof=C["TRIBUNAL_NEED"] - C["DIE"], cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            events = t.advance(s, turn=C["NIGHTS"], dice=[C["DIE"]])
            t.ok(s["_ended"]["result"] == "win", "the top of the die is just enough")
            s = t.fresh(proof=C["TRIBUNAL_NEED"] + 1, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            events = t.advance(s, turn=C["NIGHTS"], dice=[1])
            t.ok(s["_ended"]["result"] == "win", "proof past the mark cannot fail")
            t.has(events, "roll 1 (need 1+) tribunal success")
            s = t.fresh(proof=P, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            t.advance(s, turn=C["NIGHTS"] - 1, dice=[6])
            t.ok(not s["_ended"], "the Tribunal does not sit early")
            # the strike of the last night is resolved before the Tribunal
            s = t.fresh(proof=P - C["CATCH_PROOF"], cabs={"Red": 4, "Black": TOWER}, tell=3, hidden__offset=1, heat=2)
            events = t.advance(s, turn=C["NIGHTS"], dice=[4])
            t.ok(s["proof"] == P and s["_ended"]["result"] == "win", "the last catch counts at the Tribunal")
            t.ok(s["habit"] == 1 and not any("Now you know" in e for e in events), "no habit lesson on the last night")
            s = t.fresh(proof=C["RAID_UNLOCK"] - 1, cabs={"Red": 4, "Black": TOWER}, tell=3, hidden__offset=1, heat=2)
            events = t.advance(s, turn=C["NIGHTS"], dice=[6])
            t.ok(s["lodging"] is None and not any("receipt" in e for e in events), "no address turns up on the last night")
            s = t.fresh(proof=C["TRIBUNAL_NEED"], cabs={"Red": 4, "Black": TOWER}, tell=3, hidden__offset=1, heat=C["HEAT_MAX"] - C["CATCH_HEAT"])
            t.advance(s, turn=C["NIGHTS"])
            t.ok(s["_ended"]["result"] == "loss" and "arrested" in s["_ended"]["reason"], "the warrant on the last night beats the Tribunal")
            t.in_order(events, ["unwinds Quarter 4", "The Tribunal sits"])
            s = t.fresh(proof=P, cabs={"Red": TOWER, "Black": TOWER}, tell=3)
            s["_turn"] = C["NIGHTS"]
            s, _ = t.step(s, "lie_low")
            t.ok(s["_ended"] and s["_ended"]["phase"] == "dusk", "the game ends at the dusk of the last night")
            end = self.final_check(t.fresh())
            t.ok(end["result"] == "loss", "the fallback is a loss")

        return [
            (1, "ring and cabs", r1), (2, "the Gearwright's habit", r2), (3, "catch, hear, silence", r3),
            (4, "heat", r4), (5, "bait", r5), (6, "tower catch", r6), (7, "lodging and raid", r7), (8, "tribunal", r8),
        ]

    # ------------------------------------------------------------ state

    def resample_hidden(self, s, rng):
        if s["habit"] is None:
            pool = [o for o in self.offsets() if o not in s["ruled_out"]] or self.offsets()
            s["hidden"]["offset"] = rng.choice(pool)
        if s["lodging"] is None:
            s["hidden"]["lodging"] = rng.d(self.C["QUARTERS"])

    def init_state(self, rng):
        C = self.C
        return {
            "heat": C["HEAT_START"],
            "proof": 0,
            "cabs": {"Red": TOWER, "Black": TOWER},
            "tell": rng.d(C["QUARTERS"]),
            "habit": None,
            "ruled_out": [],
            "last_strike": None,
            "bait": 0,
            "dark": False,
            "baited": False,
            "lodging": None,
            "receipt_at": C["RAID_UNLOCK"],
            "hidden": {"offset": rng.choice(self.offsets()), "lodging": rng.d(C["QUARTERS"])},
        }

    def options(self, s):
        C = self.C
        o = []
        for cab in CABS:
            q = s["cabs"][cab]
            if q == TOWER:
                o.append({"id": "move", "args": {"cab": cab}, "params": {"to": {"choices": list(range(1, C["QUARTERS"] + 1))}},
                          "label": f"Send the {cab} cab out from the Tower to any quarter (Heat +{C['MOVE_HEAT']})"})
            else:
                a, b = self.neighbors(q)
                o.append({"id": "move", "args": {"cab": cab}, "params": {"to": {"choices": [a, b, "Tower"]}},
                          "label": f"Send the {cab} cab from Quarter {q} to {a}, {b} or the Tower (Heat +{C['MOVE_HEAT']})"})
        if s["heat"] == 0:
            cool = "Heat is already 0"
        elif s["heat"] < C["LIE_LOW"]:
            cool = "Heat to 0"
        else:
            cool = f"Heat -{C['LIE_LOW']}"
        o.append({"id": "lie_low", "args": {}, "label": f"Lie low with the lanterns out ({cool}, no catch tonight)"})
        if not s["baited"] and not s["bait"] and s["_turn"] < C["NIGHTS"]:
            need = f"{C['BAIT_NEED_KNOWN']}+ since you know his habit" if s["habit"] is not None else f"{C['BAIT_NEED']}+"
            o.append({"id": "bait", "args": {},
                      "label": f"Leak that the Tower guard stands down tomorrow night (Heat +{C['BAIT_HEAT']}; roll {need} and he strikes the Tower tomorrow, miss: Heat +{C['BAIT_FAIL_HEAT']})"})
        if s["lodging"] is not None:
            there = any(s["cabs"][c] == s["lodging"] for c in CABS)
            need = f"{C['RAID_NEED_THERE']}+ with your cab there" if there else f"{C['RAID_NEED']}+"
            o.append({"id": "raid", "args": {},
                      "label": f"Raid his lodging in Quarter {s['lodging']} (roll {need} for Proof +{C['RAID_PROOF']}, miss: Heat +{C['RAID_FAIL_HEAT']})"})
        return o

    def _warrant(self, s, ev):
        """True when Heat has reached the limit: the game ends here."""
        if s["heat"] >= self.C["HEAT_MAX"]:
            self.hit("arrested")
            ev.append("The Watch is waiting at the yard gate with a warrant.")
            self.finish(s, "loss", f"arrested: Heat reached {self.C['HEAT_MAX']}")
            return True
        return False

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "move":
            cab, to = args["cab"], args["to"]
            dest = TOWER if to == "Tower" else int(to)
            ev.append(f"The {cab} cab rolls from {self.place(s['cabs'][cab])} to {self.place(dest)}. Heat +{C['MOVE_HEAT']}.")
            s["cabs"][cab] = dest
            s["heat"] += C["MOVE_HEAT"]
            self._warrant(s, ev)
        elif a == "lie_low":
            drop = min(s["heat"], C["LIE_LOW"])
            s["heat"] -= drop
            s["dark"] = True
            ev.append("The lanterns go out and the cabs sit still. " + (f"Heat -{drop}." if drop else "Heat stays at 0."))
        elif a == "bait":
            s["heat"] += C["BAIT_HEAT"]
            s["baited"] = True
            ok, txt = rng.check(C["BAIT_NEED_KNOWN"] if s["habit"] is not None else C["BAIT_NEED"], C["DIE"], "bait")
            if ok:
                s["bait"] = 2  # lit-ok: the rumor needs tonight to travel; he comes at the next dusk
                self.hit("bait")
                ev.append(f"{txt}. The rumor takes. He has heard the Tower guard stands down.")
            else:
                s["heat"] += C["BAIT_FAIL_HEAT"]
                self.hit("bait_miss")
                ev.append(f"{txt}. The rumor falls flat and the Watch asks who started it. Heat +{C['BAIT_FAIL_HEAT']}.")
            self._warrant(s, ev)
        elif a == "raid":
            there = any(s["cabs"][c] == s["lodging"] for c in CABS)
            ok, txt = rng.check(C["RAID_NEED_THERE"] if there else C["RAID_NEED"], C["DIE"], "raid")
            old = s["lodging"]
            s["lodging"] = None
            s["hidden"]["lodging"] = rng.choice([q for q in range(1, C["QUARTERS"] + 1) if q != old])
            if ok:
                s["proof"] += C["RAID_PROOF"]
                self.hit("raid")
                ev.append(f"{txt}. His workbench, his masks, his ledger of the guilds. Proof +{C['RAID_PROOF']}. He has moved house.")
            else:
                s["heat"] += C["RAID_FAIL_HEAT"]
                self.hit("raid_miss")
                ev.append(f"{txt}. The rooms are empty and the neighbors call the Watch. Heat +{C['RAID_FAIL_HEAT']}. He has moved house.")
            s["receipt_at"] = s["proof"] + C["RAID_UNLOCK"]
            if not ok:
                self._warrant(s, ev)
        return ev

    def _lanterns(self, cabs_here, dark=False):
        names = " and ".join(cabs_here)
        if dark:
            return f"the dark {names} {plural(len(cabs_here), 'cab')[2:]}"
        if len(cabs_here) == 1:
            return f"the {names} cab's lantern"
        return f"the {names} cabs' lanterns"

    def advance(self, s, rng):
        C = self.C
        ev = []
        h = s["hidden"]
        # the Gearwright's strike (decided by his habit and the grease report, or by the bait)
        if s["bait"] == 1:
            s["bait"] = 0
            here = [c for c in CABS if s["cabs"][c] == TOWER]
            s["last_strike"] = TOWER
            if here and s["dark"]:
                self.hit("tower_missed")
                ev.append(f"The Gearwright comes for the Tower mainspring and slips past {self._lanterns(here, dark=True)}. "
                          "The guards chase a shadow.")
            elif here:
                s["proof"] += C["TOWER_PROOF"]
                self.hit("tower_catch")
                ev.append(f"The Gearwright comes for the Tower mainspring and walks into {self._lanterns(here)}. "
                          f"The guard who never stood down sees everything. Proof +{C['TOWER_PROOF']}.")
            else:
                self.hit("tower_missed")
                ev.append("The Gearwright comes for the Tower mainspring. No cab of yours is there; the guards chase a shadow.")
        else:
            target = self.wrap(s["tell"] + h["offset"])
            here = [c for c in CABS if s["cabs"][c] == target]
            near = [c for c in CABS if s["cabs"][c] != TOWER and target in self.neighbors(s["cabs"][c])]
            if here and s["dark"]:
                s["last_strike"] = target
                self.hit("heard")
                who = f"The {here[0]} cab sits" if len(here) == 1 else f"The {' and '.join(here)} cabs sit"
                them = "it" if len(here) == 1 else "them"
                ev.append(f"{who} dark in Quarter {target} as the mainspring snaps beside {them}: he unwinds Quarter {target}. No lantern, no face.")
            elif here:
                s["proof"] += C["CATCH_PROOF"]
                s["heat"] += C["CATCH_HEAT"]
                s["last_strike"] = target
                self.hit("catch")
                ev.append(f"The Gearwright unwinds Quarter {target} under {self._lanterns(here)}: a mask, a brass key, a face. "
                          f"Proof +{C['CATCH_PROOF']}.")
                ev.append(f"The Watch finds your {plural(len(here), 'cab')[2:]} at the scene. Heat +{C['CATCH_HEAT']}.")
            elif near:
                s["last_strike"] = target
                self.hit("heard")
                cab = near[0]
                ev.append(f"From Quarter {s['cabs'][cab]} the {cab} cab hears a mainspring snap next door: he unwinds Quarter {target}.")
            else:
                s["last_strike"] = None
                self.hit("silent")
                covered = set()
                for c in CABS:
                    q = s["cabs"][c]
                    if q != TOWER:
                        covered |= {q, *self.neighbors(q)}
                new_out = [off for off in self.offsets()
                           if s["habit"] is None and self.wrap(s["tell"] + off) in covered and off not in s["ruled_out"]]
                s["ruled_out"] += new_out
                left = [off for off in self.offsets() if off not in s["ruled_out"]]
                tail = ""
                if new_out:
                    tail = " Nothing within earshot of your cabs, so not " + " or ".join(self.doors(o) for o in new_out) + "."
                ev.append("A mainspring snaps somewhere on the ring. No guild admits which." + tail)
                if s["habit"] is None and len(left) == 1:
                    s["habit"] = left[0]
                    s["ruled_out"] = []
                    self.hit("habit_learned")
                    if s["_turn"] < C["NIGHTS"]:
                        ev.append(f"Only one way is left: he strikes {self.doors(s['habit'])} of the grease. Now you know his habit.")
            if (here or near) and s["habit"] is None:
                s["habit"] = h["offset"]
                s["ruled_out"] = []
                self.hit("habit_learned")
                if s["_turn"] < C["NIGHTS"]:
                    ev.append(f"He struck {self.doors(h['offset'])} of the grease. Now you know his habit.")
        s["dark"] = False
        if self._warrant(s, ev):
            return ev
        if s["lodging"] is None and s["proof"] >= s["receipt_at"] and s["_turn"] < C["NIGHTS"]:
            s["lodging"] = h["lodging"]
            self.hit("lodging")
            ev.append(f"Among the evidence, a rent receipt with his address: the Gearwright lodges in Quarter {s['lodging']}.")
        if s["_turn"] >= C["NIGHTS"]:
            self.hit("tribunal")
            need = C["TRIBUNAL_NEED"] - s["proof"]
            if need > C["DIE"]:
                ev.append("The Tribunal sits. With so little proof it does not even hear you.")
                self.finish(s, "loss", "convicted in the Gearwright's place")
                return ev
            ok, txt = rng.check(need, C["DIE"], "tribunal")
            if ok:
                ev.append(f"The Tribunal sits. {txt}. The mask comes off in open court.")
                self.finish(s, "win", "the Gearwright is exposed before the Tribunal")
            else:
                ev.append(f"The Tribunal sits. {txt}. The Tribunal finds the cabmaster guilty.")
                self.finish(s, "loss", "convicted in the Gearwright's place")
            return ev
        tomorrow = s["_turn"] + 1
        if s["bait"] == 2:
            s["bait"] = 1
        if tomorrow == C["MID_NIGHT"]:
            old = h["offset"]
            h["offset"] = rng.choice([o for o in self.offsets() if o != old])
            s["ruled_out"] = [old] if s["habit"] is not None else []  # a habit you knew is the one he will not keep
            s["habit"] = None
            s["baited"] = False  # a new habit, and he has forgotten the Tower rumor
            self.hit("habit_change")
            ev.append(f"Night {C['MID_NIGHT']}: he has seen your cabs. His habit changes.")
        if s["bait"] != 1:
            s["tell"] = rng.d(C["QUARTERS"])
        if s["bait"] == 1:
            ev.append("Dusk report: word that the Tower guard stands down is in every tavern. He comes for the Tower tomorrow night.")
        else:
            ev.append(f"Dusk report: gear-grease bought in Quarter {s['tell']}.")
        return ev

    def status_line(self, s):
        cabs = ", ".join(f"{c} {'Tower' if s['cabs'][c] == TOWER else 'Q' + str(s['cabs'][c])}" for c in CABS)
        habit = "habit unknown" if s["habit"] is None else f"strikes {self.doors(s['habit'])}"
        where = "coming for the Tower" if s["bait"] == 1 else f"grease at Q{s['tell']}"
        return f"Heat {s['heat']} | Proof {s['proof']} | Cabs: {cabs} | Gearwright: {where}, {habit}"

    def check_end(self, s):
        if s["heat"] >= self.C["HEAT_MAX"]:
            return {"result": "loss", "reason": f"arrested: Heat reached {self.C['HEAT_MAX']}"}
        return None

    def final_check(self, s):
        return {"result": "loss", "reason": "the Tribunal never sat"}

    # ------------------------------------------------------------ policy

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        heat, cabs, tell, habit = s["heat"], s["cabs"], s["tell"], s["habit"]
        room = C["HEAT_MAX"] - heat  # how many entries the sergeant's book has left
        tower = [c for c in CABS if cabs[c] == TOWER]
        ring = [c for c in CABS if cabs[c] != TOWER]

        def move(cab, to):
            return {"id": "move", "args": {"cab": cab, "to": "Tower" if to == TOWER else to}}

        if "raid" in ids and room > C["RAID_FAIL_HEAT"] and (any(cabs[c] == s["lodging"] for c in CABS) or room > C["RAID_FAIL_HEAT"] + 1):
            return "raid"  # never a raid whose miss is the warrant
        if s["bait"] == 1:
            # he comes for the Tower tonight: a lit cab must be waiting there, so somebody moves
            if room > C["MOVE_HEAT"] + 1:
                if not tower:
                    return move(ring[0], TOWER)
                if ring:
                    return move(ring[0], TOWER)
                return move(tower[0], self.wrap(tell + 1))
            return "lie_low"
        if "bait" in ids and tower and room > C["BAIT_HEAT"] + C["BAIT_FAIL_HEAT"] + 1 and (habit is not None or s["_turn"] <= 2):  # lit-ok: the opening nights
            return "bait"
        if habit is not None:
            target = self.wrap(tell + habit)
            waiting = [c for c in CABS if cabs[c] == target]
            if waiting and room > C["MOVE_HEAT"] + C["CATCH_HEAT"]:
                others = [c for c in CABS if c not in waiting]
                other = others[0] if others else waiting[-1]  # both waiting: one is enough, send the other to the hub
                if cabs[other] == TOWER:
                    return move(other, s["lodging"] if s["lodging"] else self.wrap(target + 4))  # lit-ok: across the ring
                return move(other, TOWER)
            if waiting:
                return "lie_low"
            if room > C["MOVE_HEAT"] + C["CATCH_HEAT"]:
                if tower:
                    return move(tower[0], target)
                for c in ring:
                    if target in self.neighbors(cabs[c]):
                        return move(c, target)
            if not tower and room > C["MOVE_HEAT"] + 3:
                return move(ring[0], TOWER)
            return "lie_low"
        # habit unknown: bait him to the Tower, or learn the habit by flanking the grease quarter
        flank = [self.wrap(tell + 1), self.wrap(tell - 1)]
        if any(cabs[c] in flank for c in CABS):
            return "lie_low"  # a cab is already listening
        if room > C["MOVE_HEAT"] + C["CATCH_HEAT"] + 1:
            if tower:
                return move(tower[0], flank[0])
            for c in ring:
                for f in flank:
                    if f in self.neighbors(cabs[c]):
                        return move(c, f)
            if room > C["MOVE_HEAT"] + 3:
                return move(ring[0], TOWER)
        return "lie_low"


if __name__ == "__main__":
    run(G)
