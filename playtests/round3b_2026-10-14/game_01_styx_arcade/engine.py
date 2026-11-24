"""Styx Arcade: a deduction game in a 1980s arcade where the cabinets are fed with the coins of the dead.

You are a smuggler in the Ferryman's debt. One of the regulars is skimming the Owner's takings. Run convoys down
the aisles for Hearsay and witness reports, swap Hearsay for Proof at the Pawnbroker's drifting rate and stamp it on
one regular's file, and accuse the Skimmer with Proof in hand before the Owner's audit. A magpie of a rival lifts
Proof from any file that grows too fat.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

GAMES = ["Hydra", "Sphinx", "Minotaur"]
COATS = ["ash", "crimson", "saffron"]
SHIFTS = ["early", "late"]
TOPICS = ["game", "coat", "shift"]
NAMES = ["Argus", "Circe", "Midas", "Pandora", "Atlas", "Ixion", "Hecate", "Orpheus"]


def phrase(topic, val):
    """How a witness says one fact about the Skimmer."""
    if topic == "game":
        return f"plays {val}"
    if topic == "coat":
        return f"wears the {val} coat"
    return f"works the {val} shift"


def topic_words(topics):
    return " and ".join(topics)


class G(Game):
    name = "Styx Arcade"

    CONSTANTS = {
        "NIGHTS": 12,
        "REGULARS": 6,
        "START_HEARSAY": 2,
        "AISLES": 3,
        "HAZ_MAX": 4,
        "BRIBE_MAX": 3,
        "WITNESS_P": 0.5,
        "HAUL_BASE": 2,
        "DIE": 6,
        "SEIZE": 1,
        "RATE_MIN": 6,
        "RATE_MAX": 9,
        "PROOF_NEED": 3,
        "LIFT": 1,
        "THEFT_AT": 3,
        "THEFT_MID": 2,
        "MID_NIGHT": 6,
        "LEDGER_NIGHT": 8,
        "LEDGER_COST": 3,
        "_START_RATE": 7,
    }

    RULES = """
1. {REGULARS} regulars work the floor and one is the Skimmer. Each plays one game, wears one coat and works one shift, all posted on the roster. You start with {START_HEARSAY} Hearsay and no Proof.
2. Each night the deck deals {AISLES} aisle cards (hazard up to {HAZ_MAX}, haul of hazard plus {HAUL_BASE} Hearsay). On {WITNESS_P:.0%} of nights one card has a witness who knows the Skimmer's game, coat or shift.
3. Run one aisle, bribing up to {BRIBE_MAX} Hearsay, and roll a d{DIE}: caught on a roll up to hazard minus bribes. Safe: take the haul and hear the witness. Caught: no haul, no report, and the Walker confiscates {SEIZE} Proof.
4. Instead of running, swap Hearsay for Proof at the Pawnbroker's rate, stamped on one regular in doubt; stamping another voids the old file. The rate drifts a step each dusk, {RATE_MIN} to {RATE_MAX} Hearsay per Proof.
5. Instead of running, accuse the regular on a file holding {PROOF_NEED} Proof: right wins, wrong loses. A report clearing the file's regular voids it. No accusation by the end of night {NIGHTS}: the audit calls your debt.
6. Each dusk the Magpie lifts {LIFT} Proof from your file if it holds {THEFT_AT} or more, so buy extra to cover him before the night you accuse.
7. From night {MID_NIGHT} the Back Booth opens as a fourth aisle (hazard {HAZ_MAX}, two topics), and the Magpie lifts from a file of {THEFT_MID} Proof or more.
8. From night {LEDGER_NIGHT} you may read the Owner's ledger for {LEDGER_COST} Hearsay instead of running: you learn one topic of your choice for sure, no roll.
"""

    ACTIONS = ["run", "exchange", "accuse", "ledger"]
    TAGS = ["caught", "seized", "magpie", "booth", "ledger", "rate_low", "rate_high", "voided"]
    TRACKED = ["hearsay", "proof"]

    BOUNDS = {
        "hearsay": (0, 200),
        "proof": (0, 20),
        "rate": (CONSTANTS["RATE_MIN"], CONSTANTS["RATE_MAX"]),
        "suspects": (1, CONSTANTS["REGULARS"]),
    }
    DERIVED = {
        "suspects": lambda g, s: len(g._cands(s)),
        "rate_flip": lambda g, s: g.C["RATE_MIN"] + g.C["RATE_MAX"] - s["rate"],
    }
    REACH = {
        "proof": CONSTANTS["PROOF_NEED"],
        "rate": CONSTANTS["RATE_MAX"],
        "rate_flip": CONSTANTS["RATE_MAX"],
        "hearsay": CONSTANTS["LEDGER_COST"],
    }
    GATES = {
        "exchange": {"_if": lambda g, s: s["hearsay"] >= s["rate"]},
        "accuse": {"proof": "PROOF_NEED"},
        "ledger": {
            "hearsay": "LEDGER_COST",
            "_turn": "LEDGER_NIGHT",
            "_if": lambda g, s: any(t not in s["known"] for t in TOPICS),
        },
    }

    @property
    def turns(self):
        return self.C["NIGHTS"]

    # ------------------------------------------------------------------ helpers

    def _cands(self, s):
        """Indexes of the regulars that fit every fact the player has learned."""
        return [i for i, r in enumerate(s["roster"]) if all(r[t] == v for t, v in s["known"].items())]

    def _names(self, s):
        return [s["roster"][i]["name"] for i in self._cands(s)]

    def _limit(self, night):
        """The size of file at which the Magpie lifts at the dusk of this night."""
        C = self.C
        return C["THEFT_MID"] if night >= C["MID_NIGHT"] else C["THEFT_AT"]

    def _deal(self, night, rng):
        """The deck's aisle cards for one night. One of them carries a witness. From MID_NIGHT a fourth card, the
        Back Booth, is added with two witnesses."""
        C = self.C
        cards = []
        for _ in range(C["AISLES"]):
            h = rng.d(C["HAZ_MAX"])
            cards.append({"attrs": [], "hazard": h, "haul": h + C["HAUL_BASE"], "booth": False})
        if rng.chance(C["WITNESS_P"]):
            witness = rng.d(C["AISLES"]) - 1
            cards[witness]["attrs"] = [rng.choice(TOPICS)]
        if night >= C["MID_NIGHT"]:
            first = rng.choice(TOPICS)
            second = rng.choice([t for t in TOPICS if t != first])
            cards.append({"attrs": [first, second], "hazard": C["HAZ_MAX"], "haul": C["HAZ_MAX"] + C["HAUL_BASE"], "booth": True})
        return cards

    def _reveal(self, s, topic):
        """The witness tells the Skimmer's value for a topic. It becomes a known fact."""
        val = s["roster"][s["hidden"]["culprit"]][topic]
        again = topic in s["known"]
        s["known"][topic] = val
        if again:
            return f"The witness repeats what you know: the Skimmer {phrase(topic, val)}."
        return f"The witness says the Skimmer {phrase(topic, val)}."

    def _void_if_cleared(self, s):
        """A report that clears the regular on the file voids the file."""
        if s["case"] is not None and s["case"] not in self._names(s):
            ev = [f"The report clears {s['case']}: the Owner voids your file ({s['proof']} Proof lost)."]
            s["proof"] = 0
            s["case"] = None
            self.hit("voided")
            return ev
        return []

    def _info(self, s, cands, topics):
        """Expected number of regulars cleared by learning these topics (used by the heuristic)."""
        fresh = [t for t in topics if t not in s["known"]]
        if not fresh or len(cands) < 2:
            return 0.0
        groups = {}
        for i in cands:
            key = tuple(s["roster"][i][t] for t in fresh)
            groups[key] = groups.get(key, 0) + 1
        return len(cands) - sum(n * n for n in groups.values()) / len(cands)

    # ------------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C

        def roster():
            rows = [
                ("Argus", "Hydra", "ash", "early"), ("Circe", "Hydra", "crimson", "late"),
                ("Midas", "Sphinx", "ash", "late"), ("Pandora", "Sphinx", "saffron", "early"),
                ("Atlas", "Minotaur", "crimson", "early"), ("Ixion", "Minotaur", "saffron", "late"),
            ]
            return [{"name": n, "game": g, "coat": c, "shift": h} for n, g, c, h in rows][: C["REGULARS"]]

        def card(topic="coat", hazard=3, booth=False, attrs=None):
            return {"attrs": attrs or [topic], "hazard": hazard, "haul": hazard + C["HAUL_BASE"], "booth": booth}

        def base(t, **over):
            kw = dict(roster=roster(), hidden__culprit=2, known={}, cards=[card(), card(hazard=1), card(hazard=4)],
                      hearsay=10, proof=0, case=None, rate=C["RATE_MIN"] + 1)
            kw.update(over)
            return t.fresh(**kw)

        def run_cap(t, s, i):
            opts = [o for o in self.options(s) if o["id"] == "run" and o["args"]["aisle"] == i]
            t.eq(len(opts), 1, "one run option per aisle")
            return opts[0].get("params", {}).get("bribe", {}).get("max", 0)

        def r1(t):
            s = t.fresh(seed=3)
            t.eq(len(s["roster"]), C["REGULARS"], "the roster size")
            t.eq(len({r["name"] for r in s["roster"]}), C["REGULARS"], "regulars have different names")
            looks = {(r["game"], r["coat"], r["shift"]) for r in s["roster"]}
            t.eq(len(looks), C["REGULARS"], "no two regulars look alike")
            for r in s["roster"]:
                t.ok(r["game"] in GAMES and r["coat"] in COATS and r["shift"] in SHIFTS, "each regular has a game, a coat and a shift")
            t.ok(0 <= s["hidden"]["culprit"] < C["REGULARS"], "one regular is the Skimmer")
            t.eq((s["hearsay"], s["proof"], s["case"], s["known"], s["verdict"]), (C["START_HEARSAY"], 0, None, {}, None), "a fresh game starts clean")
            t.eq(s["rate"], C["_START_RATE"], "the starting rate")
            culprits = {t.fresh(seed=sd)["hidden"]["culprit"] for sd in range(1, 80)}
            t.eq(sorted(culprits), list(range(C["REGULARS"])), "any regular can be the Skimmer, and no one else")
            s2, ev = t.step(t.fresh(seed=2), "run", {"aisle": 0, "bribe": 0})
            t.eq(s2["_turn"], 2, "one action ends the night")
            t.eq(self.status_line(t.fresh(seed=2)).split(" | ")[0], f"Hearsay {C['START_HEARSAY']}", "the status line leads with Hearsay")

        def r2(t):
            s = t.fresh(seed=4)
            t.eq(len(s["cards"]), C["AISLES"], "the deck deals AISLES cards on night 1")
            s = base(t)
            t.advance(s, turn=2, dice=[2, 3, 1, C["HAZ_MAX"], 2], chances=[C["WITNESS_P"] - 0.01], choices=["coat"])
            t.eq(len(s["cards"]), C["AISLES"], "AISLES cards each night")
            t.eq([c["hazard"] for c in s["cards"]], [3, 1, C["HAZ_MAX"]], "hazard is the die")
            t.eq([c["haul"] for c in s["cards"]], [3 + C["HAUL_BASE"], 1 + C["HAUL_BASE"], C["HAZ_MAX"] + C["HAUL_BASE"]], "haul is hazard plus HAUL_BASE")
            t.eq([c["attrs"] for c in s["cards"]], [[], ["coat"], []], "a witness night: exactly one card has a witness, here the second")
            labels = [o["label"] for o in self.options(s) if o["id"] == "run"]
            t.has(labels, "no witness", "a card without a witness says so")
            t.has(labels, "coat witness", "the witness card names its topic")
            s = base(t)
            t.advance(s, turn=2, dice=[2, 3, 1, C["HAZ_MAX"], 2], chances=[C["WITNESS_P"]], choices=["coat"])
            t.eq([c["attrs"] for c in s["cards"]], [[], [], []], "a quiet night: no card has a witness")
            seen, topics, spots, nights = set(), set(), set(), 0
            for sd in range(1, 300):
                s = t.fresh(seed=sd)
                n = sum(1 for c in s["cards"] if c["attrs"])
                t.ok(n <= 1, "at most one witness a night")
                nights += n
                for i, c in enumerate(s["cards"]):
                    seen.add(c["hazard"])
                    topics.update(c["attrs"])
                    if c["attrs"]:
                        spots.add(i)
            t.ok(abs(nights / 299 - C["WITNESS_P"]) < 0.1, f"a witness turns up on about {C['WITNESS_P']:.0%} of nights, got {nights / 299:.0%}")
            t.eq(sorted(seen), list(range(1, C["HAZ_MAX"] + 1)), "hazards run from 1 to HAZ_MAX")
            t.eq(sorted(topics), sorted(TOPICS), "all three topics come up")
            t.eq(sorted(spots), list(range(C["AISLES"])), "the witness can be on any card")
            # run offers one option per aisle, with a bribe up to the cap, the hazard and the purse
            s = base(t, cards=[card(hazard=4), card(hazard=2), card(hazard=1)], hearsay=10)
            t.eq([run_cap(t, s, 0), run_cap(t, s, 1), run_cap(t, s, 2)], [min(C["BRIBE_MAX"], 4), min(C["BRIBE_MAX"], 2), 1], "bribe up to BRIBE_MAX and the hazard")
            s = base(t, cards=[card(hazard=4), card(hazard=2), card(hazard=1)], hearsay=1)
            t.eq([run_cap(t, s, 0), run_cap(t, s, 1), run_cap(t, s, 2)], [1, 1, 1], "a bribe cannot exceed the purse")
            s = base(t, cards=[card(hazard=4), card(hazard=2), card(hazard=1)], hearsay=2)
            t.eq([run_cap(t, s, 0), run_cap(t, s, 1), run_cap(t, s, 2)], [2, 2, 1], "a purse of two")
            # apply trusts nothing: a bribe the call asks for is cut to what the rules allow
            s = base(t, hearsay=10, cards=[card(hazard=4)])
            self.apply(s, "run", {"aisle": 0}, t.rng(dice=[C["DIE"]]))
            t.eq(s["hearsay"], 10 + 4 + C["HAUL_BASE"], "a run with no bribe named is a run with no bribe")
            s = base(t, hearsay=0)
            self.apply(s, "run", {"aisle": 0, "bribe": 2}, t.rng(dice=[C["DIE"]]))
            t.ok(s["hearsay"] >= 0, "an empty purse cannot pay a bribe, whatever the call says")
            s = base(t, hearsay=1, cards=[card(hazard=4)])
            self.apply(s, "run", {"aisle": 0, "bribe": 3}, t.rng(dice=[C["DIE"]]))
            t.eq(s["hearsay"], (4 + C["HAUL_BASE"]), "a bribe above the purse is cut to the purse")
            s = base(t, hearsay=10, cards=[card(hazard=2)])
            self.apply(s, "run", {"aisle": 0, "bribe": 3}, t.rng(dice=[C["DIE"]]))
            t.eq(s["hearsay"], 10 - 2 + (2 + C["HAUL_BASE"]), "a bribe above the hazard is cut to the hazard")
            s = base(t, hearsay=10, cards=[card(hazard=4)])
            self.apply(s, "run", {"aisle": 0, "bribe": 9}, t.rng(dice=[C["DIE"]]))
            t.eq(s["hearsay"], 10 - C["BRIBE_MAX"] + (4 + C["HAUL_BASE"]), "a bribe above BRIBE_MAX is cut to BRIBE_MAX")
            s = base(t, hearsay=10, cards=[card(hazard=4)])
            self.apply(s, "run", {"aisle": 0, "bribe": -2}, t.rng(dice=[C["DIE"]]))
            t.eq(s["hearsay"], 10 + (4 + C["HAUL_BASE"]), "a negative bribe is no bribe")
            s = base(t, hearsay=0)
            runs = [o for o in self.options(s) if o["id"] == "run"]
            t.eq(len(runs), 3, "every aisle can be run")
            t.ok(all("params" not in o for o in runs), "with an empty purse there is nothing to bribe with")
            t.ok(not t.offered(s, "exchange"), "no swap with an empty purse")

        def r3(t):
            # caught on a roll up to hazard minus bribes
            s = base(t, cards=[card(hazard=3)])
            t.apply(s, "run", {"aisle": 0, "bribe": 1}, dice=[2])
            t.eq(s["hearsay"], 10 - 1, "caught: the bribe is gone and there is no haul")
            t.eq(s["known"], {}, "caught: no report")
            s = base(t, cards=[card(hazard=3)])
            ev = t.apply(s, "run", {"aisle": 0, "bribe": 1}, dice=[3])
            t.eq(s["hearsay"], 10 - 1 + (3 + C["HAUL_BASE"]), "safe: the haul comes in and the bribe is gone")
            t.eq(s["known"], {"coat": "ash"}, "safe: the witness names the Skimmer's coat")
            t.has(ev, "need 3+", "the roll shows its target")
            t.has(ev, "wears the ash coat", "the report is told")
            s = base(t, cards=[card(hazard=3)])
            t.apply(s, "run", {"aisle": 0, "bribe": 0}, dice=[3])
            t.eq(s["known"], {}, "no bribe, hazard 3: a roll of 3 is caught")
            s = base(t, cards=[card(hazard=3)])
            t.apply(s, "run", {"aisle": 0, "bribe": 0}, dice=[4])
            t.eq(s["hearsay"], 10 + (3 + C["HAUL_BASE"]), "no bribe, hazard 3: a roll of 4 is safe")
            s = base(t, cards=[card(hazard=3)])
            t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[1])
            t.eq(s["known"], {"coat": "ash"}, "a bribe equal to the hazard is always safe")
            t.eq(s["hearsay"], 10 - 3 + (3 + C["HAUL_BASE"]), "the bribe is spent even when safe")
            # caught: the Walker confiscates SEIZE Proof from the file, never more than it holds
            s = base(t, cards=[card(hazard=4)], proof=3, case="Midas")
            self._hits.clear()
            t.apply(s, "run", {"aisle": 0, "bribe": 0}, dice=[1])
            t.eq((s["proof"], s["case"]), (3 - C["SEIZE"], "Midas"), "caught: the Walker confiscates Proof")
            t.ok("caught" in self._hits and "seized" in self._hits, "caught and seized are noted")
            s = base(t, cards=[card(hazard=4)], proof=0)
            self._hits.clear()
            t.apply(s, "run", {"aisle": 0, "bribe": 0}, dice=[1])
            t.eq(s["proof"], 0, "no Proof to confiscate")
            t.ok("caught" in self._hits and "seized" not in self._hits, "caught without a seizure")
            s = base(t, cards=[card(hazard=4)], proof=C["SEIZE"], case="Midas")
            t.apply(s, "run", {"aisle": 0, "bribe": 0}, dice=[1])
            t.eq((s["proof"], s["case"]), (0, None), "an emptied file is closed")
            s = base(t, cards=[card(hazard=4)], proof=3, case="Midas")
            t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[4])
            t.eq(s["proof"], 3, "safe: the Walker takes nothing")
            # the witness tells the truth, a repeat adds nothing
            s = base(t, cards=[card(topic="game")], hidden__culprit=4)
            t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[6])
            t.eq(s["known"], {"game": "Minotaur"}, "the game of the Skimmer")
            s = base(t, cards=[card(topic="shift")], hidden__culprit=0)
            t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[6])
            t.eq(s["known"], {"shift": "early"}, "the shift of the Skimmer")
            s = base(t, cards=[card(topic="coat")], known={"coat": "ash"})
            ev = t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[6])
            t.eq(s["known"], {"coat": "ash"}, "a repeated report adds nothing")
            t.has(ev, "repeats", "a repeat is called a repeat")
            # unscripted: safe about (DIE - hazard) / DIE of the time
            wins = 0
            for sd in range(1, 301):
                s = base(t, cards=[card(hazard=2)])
                t.apply(s, "run", {"aisle": 0, "bribe": 0}, seed=sd)
                wins += s["known"] != {}
            want = (C["DIE"] - 2) / C["DIE"]
            t.ok(abs(wins / 300 - want) < 0.08, f"a hazard 2 run is safe about {want:.0%}, got {wins / 300:.0%}")

        def r4(t):
            rate = C["RATE_MIN"] + 1
            s = base(t, hearsay=2 * rate + 1, rate=rate)
            t.ok(t.offered(s, "exchange", who="Midas", proof=2) and not t.offered(s, "exchange", who="Midas", proof=3), "swap as many as you can pay for")
            t.ok(not t.offered(s, "exchange", who="Midas", proof=0), "swap at least one")
            ev = t.apply(s, "exchange", {"who": "Midas", "proof": 2})
            t.eq((s["hearsay"], s["proof"], s["case"]), (1, 2, "Midas"), "Hearsay per Proof at the rate, stamped on Midas")
            t.has(ev, f"stamps 2 Proof for {2 * rate} Hearsay on Midas", "the swap is told")
            s = base(t, hearsay=rate - 1, rate=rate)
            t.ok("exchange" not in t.ids(s), "short of one Proof's price: no swap")
            s = base(t, hearsay=rate, rate=rate)
            t.ok(t.offered(s, "exchange", who="Argus", proof=1) and not t.offered(s, "exchange", who="Argus", proof=2), "exactly one Proof's price buys one")
            # only regulars still in doubt can be stamped
            s = base(t, known={"coat": "ash"})
            t.ok(t.offered(s, "exchange", who="Argus", proof=1) and t.offered(s, "exchange", who="Midas", proof=1), "the regulars in doubt can be stamped")
            t.ok(not t.offered(s, "exchange", who="Circe", proof=1) and not t.offered(s, "exchange", who="Ixion", proof=1), "a cleared regular cannot be stamped")
            # a file holds Proof against one regular only
            s = base(t, proof=1, case="Argus", hearsay=20)
            self._hits.clear()
            ev = t.apply(s, "exchange", {"who": "Midas", "proof": 1})
            t.eq((s["proof"], s["case"]), (1, "Midas"), "stamping another regular voids the old file")
            t.has(ev, "voids your file on Argus", "the old file is voided out loud")
            t.ok("voided" in self._hits, "a voided file is noted")
            s = base(t, proof=1, case="Midas", hearsay=20)
            self._hits.clear()
            ev = t.apply(s, "exchange", {"who": "Midas", "proof": 1})
            t.eq((s["proof"], s["case"]), (2, "Midas"), "stamping the same regular adds to the file")
            t.ok("voided" not in self._hits and not any("voids" in e for e in ev), "nothing is voided")
            # the rate drifts one step at dusk, inside its bounds
            lo, hi = C["RATE_MIN"], C["RATE_MAX"]
            for start, die, want in [(lo + 1, 1, lo), (lo + 1, 2, lo + 1), (lo + 1, 3, lo + 2), (lo, 1, lo), (hi, 3, hi), (hi, 1, hi - 1), (lo, 3, lo + 1)]:
                s = base(t, rate=start)
                ev = t.advance(s, turn=3, dice=[die, 1, 1, 1])
                t.eq(s["rate"], want, f"rate {start} with die {die}")
                t.has(ev, f"reads {want} Hearsay per Proof", "the board is read out")
            s = base(t, rate=hi - 1)
            self._hits.clear()
            t.advance(s, turn=3, dice=[3, 1, 1, 1])
            t.ok("rate_high" in self._hits and "rate_low" not in self._hits, "a rate at the ceiling is noted")
            s = base(t, rate=lo + 1)
            self._hits.clear()
            t.advance(s, turn=3, dice=[1, 1, 1, 1])
            t.ok("rate_low" in self._hits and "rate_high" not in self._hits, "a rate at the floor is noted")
            moved = {}
            for sd in range(1, 241):
                s = base(t, rate=lo + 1)
                t.advance(s, turn=3, seed=sd)
                moved[s["rate"]] = moved.get(s["rate"], 0) + 1
            t.eq(sorted(moved), [lo, lo + 1, lo + 2], "from inside the band the rate can fall, hold or rise")
            t.ok(all(abs(n / 240 - 1 / 3) < 0.1 for n in moved.values()), f"a fall, a hold and a rise are about equally likely, got {moved}")
            # the countdown at dusk
            s = base(t)
            ev = t.advance(s, turn=2, dice=[2, 1, 1, 1])
            t.has(ev, f"{C['NIGHTS'] - 1} nights left before the audit", "the countdown is told")
            s = base(t)
            ev = t.advance(s, turn=C["NIGHTS"], dice=[2, 1, 1, 1])
            t.has(ev, "1 night left before the audit", "one night left is singular")
            s = base(t)
            ev = t.advance(s, turn=C["NIGHTS"] + 1, dice=[2, 1, 1, 1])
            t.ok(not any("left before the audit" in e for e in ev), "no countdown once the audit has come")

        def r5(t):
            s = base(t, proof=C["PROOF_NEED"] - 1, case="Midas")
            t.ok("accuse" not in t.ids(s), "one Proof short: no accusation")
            s = base(t, proof=C["PROOF_NEED"], case="Midas")
            t.ok(t.offered(s, "accuse"), "a full file can accuse")
            t.ok(t.offered(s, "accuse", who="Midas") and not t.offered(s, "accuse", who="Argus"), "only the regular on the file can be accused")
            t.has([o["label"] for o in self.options(s) if o["id"] == "accuse"], "Midas", "the accusation names the file's regular")
            s2, ev = t.step(t.copy(s), "accuse")
            end = self.check_end(s2)
            t.ok(end and end["result"] == "win" and s2["_ended"] == end, "the right name wins")
            t.has(ev, "Midas", "the accusation is told")
            s = base(t, proof=C["PROOF_NEED"], case="Argus")
            s2, ev = t.step(s, "accuse")
            end = self.check_end(s2)
            t.ok(end and end["result"] == "loss" and s2["_ended"] == end, "a wrong name loses")
            t.has(ev, "was Midas", "the real Skimmer is named at the end")
            s = base(t, proof=C["PROOF_NEED"] + 2, case="Midas")
            t.ok(t.offered(s, "accuse"), "more Proof than needed still accuses")
            # a report that clears the file's regular voids the file
            s = base(t, proof=C["PROOF_NEED"], case="Circe", cards=[card(topic="coat")])
            self._hits.clear()
            ev = t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[6])
            t.eq((s["proof"], s["case"]), (0, None), "the Skimmer's coat is ash, so Circe is cleared and the file is void")
            t.has(ev, "voids your file", "the void is told")
            t.ok("voided" in self._hits, "the void is noted")
            s = base(t, proof=C["PROOF_NEED"], case="Argus", cards=[card(topic="coat")])
            self._hits.clear()
            t.apply(s, "run", {"aisle": 0, "bribe": 3}, dice=[6])
            t.eq((s["proof"], s["case"]), (C["PROOF_NEED"], "Argus"), "Argus still fits the report, so the file stands")
            t.ok("voided" not in self._hits, "no void")
            s = base(t, proof=C["PROOF_NEED"], case="Midas", hearsay=C["LEDGER_COST"] + 1, _turn=C["LEDGER_NIGHT"], known={"game": "Sphinx"})
            t.apply(s, "ledger", {"topic": "coat"})
            t.eq(s["known"], {"game": "Sphinx", "coat": "ash"}, "the ledger tells the coat")
            t.eq((s["proof"], s["case"]), (C["PROOF_NEED"], "Midas"), "a ledger entry that fits keeps the file")
            s = base(t, proof=C["PROOF_NEED"], case="Pandora", hearsay=C["LEDGER_COST"] + 1, _turn=C["LEDGER_NIGHT"], known={"game": "Sphinx"})
            ev = t.apply(s, "ledger", {"topic": "coat"})
            t.eq((s["proof"], s["case"]), (0, None), "a ledger entry that clears the file's regular voids the file")
            t.has(ev, "voids your file", "the void is told")
            # the audit
            s = base(t)
            s["_turn"] = C["NIGHTS"]
            t.ok(self.check_end(s) is None, "the last night is still played")
            s2, _ = t.step(base(t, proof=C["PROOF_NEED"], case="Midas", _turn=C["NIGHTS"]), "accuse")
            t.eq(s2["_ended"]["result"], "win", "the last night's accusation counts")
            s["_turn"] = C["NIGHTS"] + 1
            end = self.check_end(s)
            t.ok(end and end["result"] == "loss", "no accusation by the end of the last night is a loss")
            t.eq(self.turns, C["NIGHTS"], "the budget is NIGHTS")
            s = base(t)
            s["_turn"] = C["NIGHTS"]
            s2, _ = t.step(s, "run", {"aisle": 0, "bribe": 0})
            t.ok(s2["_ended"] is not None and s2["_ended"]["result"] == "loss", "running on the last night ends in the audit")
            ok = 0
            for sd in range(1, 40):
                s = t.fresh(seed=sd, proof=C["PROOF_NEED"])
                s["case"] = s["roster"][s["hidden"]["culprit"]]["name"]
                s2, _ = t.step(s, "accuse")
                ok += s2["_ended"]["result"] == "win"
            t.eq(ok, 39, "accusing the real Skimmer always wins")

        def r6(t):
            for held, left in [(C["THEFT_AT"], C["THEFT_AT"] - C["LIFT"]), (C["THEFT_AT"] + 2, C["THEFT_AT"] + 2 - C["LIFT"]),
                               (C["THEFT_AT"] - 1, C["THEFT_AT"] - 1), (0, 0)]:
                s = base(t, proof=held, case="Midas" if held else None)
                self._hits.clear()
                ev = t.advance(s, turn=3, dice=[2, 1, 1, 1])
                t.eq(s["proof"], left, f"holding {held} at dusk")
                if left < held:
                    t.has(ev, "Magpie", "the lift is told")
                    t.ok("magpie" in self._hits, "the Magpie is noted")
                else:
                    t.ok("magpie" not in self._hits and not any("Magpie" in e for e in ev), "no lift, no tell")
            s = base(t, proof=5, case="Midas")
            t.advance(s, turn=4, dice=[2, 1, 1, 1])
            t.eq((s["proof"], s["case"]), (5 - C["LIFT"], "Midas"), "he lifts LIFT, not the whole file")
            # buying extra covers him: the need plus the lift, then accuse the next night
            s = base(t, hearsay=40, rate=C["RATE_MIN"])
            s, _ = t.step(s, "exchange", {"who": "Midas", "proof": C["PROOF_NEED"] + C["LIFT"]})
            t.ok(s["proof"] >= C["PROOF_NEED"] and s["case"] == "Midas", "buying need plus lift leaves enough after the Magpie")

        def r7(t):
            s = base(t)
            self._hits.clear()
            t.advance(s, turn=C["MID_NIGHT"] - 1, dice=[2, 1, 1, 1])
            t.eq(len(s["cards"]), C["AISLES"], "no Back Booth before the middle night")
            t.ok("booth" not in self._hits, "no booth yet")
            s = base(t)
            self._hits.clear()
            ev = t.advance(s, turn=C["MID_NIGHT"], dice=[2, 1, 2, 3, 1], chances=[0.0], choices=["game", "shift", "coat"])
            t.eq(len(s["cards"]), C["AISLES"] + 1, "the Back Booth is a fourth aisle")
            booth = s["cards"][-1]
            t.eq((booth["hazard"], booth["haul"], booth["booth"]), (C["HAZ_MAX"], C["HAZ_MAX"] + C["HAUL_BASE"], True), "booth hazard and haul")
            t.eq(booth["attrs"], ["shift", "coat"], "two topics, two different ones")
            t.eq(s["cards"][0]["attrs"], ["game"], "the three plain cards keep their one witness")
            t.ok(not any(c["booth"] for c in s["cards"][:-1]), "only the fourth card is the booth")
            t.ok("booth" in self._hits, "the booth is noted")
            t.has(ev, "Back Booth", "the booth is announced")
            for sd in range(1, 60):
                s = base(t)
                t.advance(s, turn=C["MID_NIGHT"] + 2, seed=sd)
                t.ok(len(s["cards"]) == C["AISLES"] + 1 and len(set(s["cards"][-1]["attrs"])) == 2, "the booth never repeats a topic")
            s = base(t, cards=[card(), card(), card(), card(hazard=C["HAZ_MAX"], booth=True, attrs=["game", "shift"])], hidden__culprit=2)
            t.eq(run_cap(t, s, 3), C["BRIBE_MAX"], "the booth can be bribed too")
            t.apply(s, "run", {"aisle": 3, "bribe": C["BRIBE_MAX"]}, dice=[C["DIE"]])
            t.eq(s["known"], {"game": "Sphinx", "shift": "late"}, "the booth reports two topics")
            # the Magpie lifts from smaller files from the middle night
            small = C["THEFT_MID"]
            s = base(t, proof=small, case="Midas")
            t.advance(s, turn=C["MID_NIGHT"], dice=[2, 1, 1, 1, 1])
            t.eq(s["proof"], small, "before the middle night a file of THEFT_MID is safe")
            s = base(t, proof=small, case="Midas")
            self._hits.clear()
            ev = t.advance(s, turn=C["MID_NIGHT"] + 1, dice=[2, 1, 1, 1, 1])
            t.eq(s["proof"], small - C["LIFT"], "from the middle night THEFT_MID is enough")
            t.eq(s["case"], "Midas" if small > C["LIFT"] else None, "the file stays while it holds Proof")
            t.has(ev, "Magpie", "the lift is told")
            # a lift that empties the file closes it
            old_lift = C["LIFT"]
            try:
                C["LIFT"] = small + 1
                s = base(t, proof=small, case="Midas")
                t.advance(s, turn=C["MID_NIGHT"] + 1, dice=[2, 1, 1, 1, 1])
                t.eq((s["proof"], s["case"]), (0, None), "a lift that empties the file closes it")
            finally:
                C["LIFT"] = old_lift
            s = base(t, proof=small - 1)
            t.advance(s, turn=C["MID_NIGHT"] + 1, dice=[2, 1, 1, 1, 1])
            t.eq(s["proof"], small - 1, "below THEFT_MID nothing is lifted")

        def r8(t):
            ledger_night = C["LEDGER_NIGHT"]
            s = base(t, hearsay=C["LEDGER_COST"], _turn=ledger_night - 1)
            t.ok("ledger" not in t.ids(s), "no ledger before its night")
            s = base(t, hearsay=C["LEDGER_COST"], _turn=ledger_night)
            t.ok(all(t.offered(s, "ledger", topic=x) for x in TOPICS), "the ledger offers every unknown topic")
            s = base(t, hearsay=C["LEDGER_COST"] - 1, _turn=ledger_night)
            t.ok("ledger" not in t.ids(s), "not enough Hearsay for the ledger")
            s = base(t, hearsay=C["LEDGER_COST"] + 4, _turn=ledger_night + 2, known={"game": "Sphinx"})
            t.ok(not t.offered(s, "ledger", topic="game") and t.offered(s, "ledger", topic="coat"), "a known topic is not offered")
            self._hits.clear()
            ev = t.apply(s, "ledger", {"topic": "coat"})
            t.eq(s["hearsay"], 4, "the ledger costs LEDGER_COST")
            t.eq(s["known"], {"game": "Sphinx", "coat": "ash"}, "the ledger tells the Skimmer's coat for sure")
            t.ok("ledger" in self._hits, "the ledger is noted")
            t.has(ev, "ash", "the ledger entry is told")
            s = base(t, hearsay=9, _turn=ledger_night, known={"game": "Sphinx", "coat": "ash", "shift": "late"})
            t.ok("ledger" not in t.ids(s), "nothing left to learn")
            s = base(t, hearsay=9, _turn=ledger_night, hidden__culprit=5)
            t.apply(s, "ledger", {"topic": "shift"})
            t.eq(s["known"], {"shift": "late"}, "a different Skimmer, a different entry")
            s2, _ = t.step(s, "ledger", {"topic": "game"})
            t.eq(s2["_turn"], ledger_night + 1, "reading the ledger takes the night")

        return [
            (1, "roster and start", r1), (2, "aisle cards", r2), (3, "the roll", r3), (4, "swap, file and rate", r4),
            (5, "accuse, voids and audit", r5), (6, "the Magpie", r6), (7, "booth and bolder Magpie", r7), (8, "the ledger", r8),
        ]

    def resample_hidden(self, s, rng):
        """The Skimmer is hidden. Any regular who fits every fact learned so far could be the one."""
        cands = self._cands(s) or list(range(len(s["roster"])))
        s["hidden"]["culprit"] = cands[rng.d(len(cands)) - 1]

    # ------------------------------------------------------------------ engine contract

    def init_state(self, rng):
        C = self.C
        looks = [(g, c, h) for g in GAMES for c in COATS for h in SHIFTS]
        rng.shuffle(looks)
        names = list(NAMES)
        rng.shuffle(names)
        n = C["REGULARS"]
        roster = [{"name": names[i], "game": looks[i][0], "coat": looks[i][1], "shift": looks[i][2]} for i in range(n)]
        culprit = rng.d(n) - 1
        return {
            "hearsay": C["START_HEARSAY"],
            "proof": 0,
            "case": None,
            "rate": C["_START_RATE"],
            "roster": roster,
            "known": {},
            "cards": self._deal(1, rng),
            "verdict": None,
            "hidden": {"culprit": culprit},
        }

    def options(self, s):
        C = self.C
        o = []
        for i, card in enumerate(s["cards"]):
            top = min(C["BRIBE_MAX"], s["hearsay"], card["hazard"])
            what = "the Back Booth" if card["booth"] else f"aisle {i + 1}"
            who = f"{topic_words(card['attrs'])} witness" if card["attrs"] else "no witness"
            label = f"Run {what}: {who}, hazard {card['hazard']}, haul {card['haul']}"
            opt = {"id": "run", "label": label, "args": {"aisle": i}, "group": "Run a convoy"}
            if top >= 1:
                opt["params"] = {"bribe": {"min": 0, "max": top, "step": 1}}
            o.append(opt)
        rate = max(1, s["rate"])
        if s["hearsay"] >= rate:
            n = s["hearsay"] // rate
            o.append({"id": "exchange", "label": f"Swap Hearsay for Proof at {rate} Hearsay each (you can afford {n}), stamped on one regular",
                      "args": {}, "params": {"who": {"choices": self._names(s)}, "proof": {"min": 1, "max": n, "step": 1}}})
        if s["proof"] >= C["PROOF_NEED"] and s["case"] is not None:
            o.append({"id": "accuse", "label": f"Accuse {s['case']} before the Owner ({s['proof']} Proof on the file)", "args": {"who": s["case"]}})
        unknown = [t for t in TOPICS if t not in s["known"]]
        if s["_turn"] >= C["LEDGER_NIGHT"] and s["hearsay"] >= C["LEDGER_COST"] and unknown:
            o.append({"id": "ledger", "label": f"Read the Owner's ledger (-{C['LEDGER_COST']} Hearsay): learn one topic for sure",
                      "args": {}, "params": {"topic": {"choices": unknown}}})
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "run":
            card = s["cards"][args["aisle"]]
            bribe = max(0, min(int(args.get("bribe", 0)), C["BRIBE_MAX"], s["hearsay"], card["hazard"]))
            s["hearsay"] -= bribe
            ok, txt = rng.check(max(1, card["hazard"] - bribe + 1), C["DIE"], "convoy")
            if ok:
                s["hearsay"] += card["haul"]
                ev.append(f"{txt}. The convoy slips past the Walker: haul +{card['haul']} Hearsay.")
                for topic in card["attrs"]:
                    ev.append(self._reveal(s, topic))
                ev += self._void_if_cleared(s)
            else:
                self.hit("caught")
                ev.append(f"{txt}. The Floor Walker catches the convoy: no haul, no report.")
                lost = min(C["SEIZE"], s["proof"])
                if lost > 0:
                    s["proof"] -= lost
                    self.hit("seized")
                    ev.append(f"The Walker confiscates {lost} Proof from your file.")
                    if s["proof"] == 0:
                        s["case"] = None
        elif a == "exchange":
            who = args["who"]
            n = int(args["proof"])
            cost = n * s["rate"]
            if s["case"] is not None and s["case"] != who:
                self.hit("voided")
                ev.append(f"The Owner voids your file on {s['case']} ({s['proof']} Proof lost).")
                s["proof"] = 0
            s["hearsay"] -= cost
            s["proof"] += n
            s["case"] = who
            ev.append(f"The Pawnbroker stamps {n} Proof for {cost} Hearsay on {who}.")
        elif a == "accuse":
            who = s["case"]
            culprit = s["roster"][s["hidden"]["culprit"]]["name"]
            if who == culprit:
                s["verdict"] = "right"
                ev.append(f"You name {who} with {s['proof']} Proof on the file. The Owner nods: {who} was the Skimmer.")
            else:
                s["verdict"] = "wrong"
                ev.append(f"You name {who}, but the Skimmer was {culprit}. The Owner is not amused.")
        elif a == "ledger":
            s["hearsay"] -= C["LEDGER_COST"]
            self.hit("ledger")
            ev.append(f"You pay {C['LEDGER_COST']} Hearsay for a page of the ledger.")
            ev.append(self._reveal(s, args["topic"]))
            ev += self._void_if_cleared(s)
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        night = s["_turn"] - 1  # the night that just ended
        if s["proof"] >= self._limit(night):
            took = min(C["LIFT"], s["proof"])
            s["proof"] -= took
            if s["proof"] == 0:
                s["case"] = None
            self.hit("magpie")
            ev.append(f"At dusk the Magpie lifts {took} Proof from your file.")
        die = rng.d(3)
        if die == 1:
            s["rate"] = max(C["RATE_MIN"], s["rate"] - 1)
        elif die == 3:
            s["rate"] = min(C["RATE_MAX"], s["rate"] + 1)
        if s["rate"] == C["RATE_MIN"]:
            self.hit("rate_low")
        if s["rate"] == C["RATE_MAX"]:
            self.hit("rate_high")
        ev.append(f"The Pawnbroker's board now reads {s['rate']} Hearsay per Proof.")
        if s["_turn"] == C["MID_NIGHT"]:
            self.hit("booth")
            ev.append(f"Night {s['_turn']}: the Back Booth opens as a fourth aisle, and the Magpie will lift from any file of {C['THEFT_MID']} Proof or more.")
        s["cards"] = self._deal(s["_turn"], rng)
        left = C["NIGHTS"] - s["_turn"] + 1
        if left >= 1:
            ev.append(f"{plural(left, 'night')} left before the audit.")
        return ev

    def status_line(self, s):
        proof = f"Proof {s['proof']}" + (f" on {s['case']}" if s["case"] else "")
        return f"Hearsay {s['hearsay']} | {proof} | Rate {s['rate']} | Suspects {len(self._cands(s))}"

    def check_end(self, s):
        if s["verdict"] == "right":
            return {"result": "win", "reason": "the Skimmer was named with Proof on the file"}
        if s["verdict"] == "wrong":
            return {"result": "loss", "reason": "the wrong regular was named"}
        if s["_turn"] > self.turns:
            return {"result": "loss", "reason": "the Owner's audit arrived with no accusation"}
        return None

    def visible(self, s):
        v = Game.visible(self, s)
        v["candidates"] = self._names(s)
        return v

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        cands = self._cands(s)
        names = self._names(s)
        night = s["_turn"]
        nights_left = C["NIGHTS"] - night
        if "accuse" in ids:
            return {"id": "accuse", "args": {}}
        # buy enough Proof to survive the Magpie, once the answer is near or time is short
        target = s["case"] if s["case"] in names else rng.choice(names)
        have = s["proof"] if s["case"] == target else 0
        total = C["PROOF_NEED"] if C["PROOF_NEED"] < self._limit(night) else C["PROOF_NEED"] + C["LIFT"]
        want = max(1, total - have)
        ready = len(cands) == 1 or (len(cands) <= 2 and nights_left <= 3) or nights_left <= 1
        cheap = C["RATE_MIN"] + 1
        afford = s["hearsay"] // max(1, s["rate"])
        if "exchange" in ids:
            if ready and afford >= want and (s["rate"] <= cheap or nights_left <= 3):
                return {"id": "exchange", "args": {"who": target, "proof": want}}
        if "ledger" in ids and len(cands) > 1 and nights_left <= 5:
            ledger = next(o for o in options if o["id"] == "ledger")
            topics = ledger["params"]["topic"]["choices"]
            pick = max(topics, key=lambda t: self._info(s, cands, [t]))
            return {"id": "ledger", "args": {"topic": pick}}
        best, best_val = None, None
        weight = 2.0 if len(cands) > 1 else 0.0
        for o in options:
            if o["id"] != "run":
                continue
            card = s["cards"][o["args"]["aisle"]]
            top = o["params"]["bribe"]["max"] if o.get("params") else 0
            info = self._info(s, cands, card["attrs"])
            for b in range(top + 1):
                p_safe = (C["DIE"] - max(0, card["hazard"] - b)) / C["DIE"]
                val = p_safe * (card["haul"] + weight * info) - b - (1 - p_safe) * s["proof"] * 2
                if best_val is None or val > best_val:
                    best, best_val = {"id": "run", "args": {"aisle": o["args"]["aisle"], "bribe": b}}, val
        return best


if __name__ == "__main__":
    run(G)
