"""The Coral Galley: a /play engine.

Rolls: FORM=15 programming (write orders, watch them run), SET=24 restaurant kitchen on a Friday
night, ROLE=30 a reef (the kitchen line is "the Reef"), LOOP=7 hold a line against waves and repair
between, CLOCK=21 runway with investors watching, TWIST=13 bank one action, WIN=3 survive the clock,
MAP=12 league table, TONE=3 pulp adventure.

Rulesheet (8 lines):
1. The Reef runs your last three orders in sequence every wave. Each wave you shout one new order; the oldest is forgotten.
2. FIRE serves 4 covers at 3 cash each. PUSH serves 3 at 5 each on a roll of 3+ (Line 12+ needs 2+, Line 5 or less needs 5+); a miss serves none and Line -1.
3. FIX costs 6 cash, Line +6 (max 24), and halves this wave's damage. Every unserved cover hits the Line for 1. Line 0 collapses the kitchen.
4. Upkeep each wave is 8 plus the wave number. If you cannot pay, the Syndicate covers it and your Buzz drops 2.
5. Serve the whole wave: Buzz +1. Leave 3+ unserved: Buzz -1 (6+: -2) and Rourke's Chop House poaches +2 Buzz. Rank is your Buzz against five rival clubs.
6. Instead of an order you may BANK (the Reef repeats itself; you hold one token). SPEND the token to run your three orders twice in one wave.
7. Wave 8: the Syndicate reviews the League. Rank 3 or better: +30 cash. Worse: upkeep +6 a wave. PLATTER unlocks: -10 cash, serves 2, Buzz +2, needs Line 8+. Every rival climbs +2 a wave after the review, Rourke +4.
8. Two failed waves in a row, with no token held, let you SHANGHAI a dock crew (-15 cash: every cover served, Line +2). Win: still open after wave 16 and in the League's top three.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

# tuning knobs
CASH0 = 60
LINE_MAX = 24
WAVE_BASE = (4, 7, 12)  # waves 1-7, 8-12, 13-16
FIRE_N, FIRE_PAY = 4, 3
PUSH_N, PUSH_PAY = 3, 5
FIX_COST, FIX_GAIN = 6, 6
PLATTER_N, PLATTER_COST, PLATTER_BUZZ, PLATTER_MIN = 2, 10, 2, 8
UPKEEP_BASE, UPKEEP_CUT, REVIEW_BONUS = 8, 6, 30  # upkeep = base + wave number (+cut after a bad review)
SHANGHAI_COST = 15
SHORTFALL_BUZZ = 2  # buzz lost when upkeep cannot be paid
WIN_RANK = 3  # finish at this rank or better
RIVAL_UP, RIVAL_DOWN = 0.5, 0.25  # rival buzz drift odds
ROURKE_CLIMB = 2  # Rourke gains this every wave after the review
RIVAL_CLIMB = 2  # every rival gains this every wave after the review

RIVALS = ["Rourke's Chop House", "The Brass Lantern", "Madame Oyster's", "The Sunken Ballroom", "Pier Nine"]
TYPES = {
    "normal": "a normal seating",
    "light": "a light seating (-3 covers)",
    "rush": "a rush (+3 covers)",
    "critic": "the Tribune's columnist (serve all: Buzz +3; leave 3+: Buzz -3)",
    "sailors": "sea-wolves off the trawlers (Line damage doubled)",
}
ORDER_NAMES = {"fire": "FIRE", "push": "PUSH", "fix": "FIX", "platter": "PLATTER"}


class G(Game):
    name = "The Coral Galley"
    turns = 16

    def init_state(self, rng):
        deck = ["normal"] * 5 + ["light"] * 3 + ["rush"] * 3 + ["critic"] * 2 + ["sailors"] * 2
        rng.shuffle(deck)
        deck = ["normal"] + deck  # wave 1 is always a normal seating
        rivals = {name: 7 + rng.d(6) for name in RIVALS}
        return {
            "cash": CASH0,
            "line": LINE_MAX,
            "buzz": 10,
            "orders": ["fire", "fire", "fire"],
            "token": 0,
            "upkeep": 0,
            "streak": 0,
            "rivals": rivals,
            "next_wave": "normal",
            "hidden": {"deck": deck, "reviewed": False},
        }

    # ------------------------------------------------------------ helpers
    def rank(self, s):
        return 1 + sum(1 for v in s["rivals"].values() if v > s["buzz"])

    def wave_base(self, turn):
        if turn <= 7:
            return WAVE_BASE[0]
        if turn <= 12:
            return WAVE_BASE[1]
        return WAVE_BASE[2]

    def upkeep_due(self, s, wave):
        return UPKEEP_BASE + wave + s["upkeep"]

    def program_text(self, s):
        return ">".join(ORDER_NAMES[o] for o in s["orders"])

    # ------------------------------------------------------------ contract
    def options(self, s):
        o = [
            {"id": "fire", "label": f"Shout FIRE (serve {FIRE_N} at {FIRE_PAY} each)"},
            {"id": "push", "label": f"Shout PUSH (serve {PUSH_N} at {PUSH_PAY} each on a roll)"},
            {"id": "fix", "label": f"Shout FIX (-{FIX_COST} cash, Line +{FIX_GAIN}, halve damage)"},
        ]
        if s["_turn"] >= 8 and s["line"] >= PLATTER_MIN:
            o.append({"id": "platter", "label": f"Shout PLATTER (-{PLATTER_COST} cash, serve {PLATTER_N}, Buzz +{PLATTER_BUZZ})"})
        if s["streak"] >= 2 and s["cash"] >= SHANGHAI_COST and not s["token"]:
            o.append({"id": "shanghai", "label": f"Shanghai a dock crew (-{SHANGHAI_COST} cash: all served, Line +2)"})
        elif s["token"]:
            o.append({"id": "spend", "label": "SPEND the token: run the three orders twice"})
        else:
            o.append({"id": "bank", "label": "BANK: shout nothing, hold a token"})
        return o

    def run_program(self, s, remaining, rng, ev, twice=False):
        fixed = False
        passes = 2 if twice else 1
        for p in range(passes):
            for o in s["orders"]:
                if o == "fire":
                    n = min(FIRE_N, remaining)
                    s["cash"] += FIRE_PAY * n
                    remaining -= n
                    ev.append(f"FIRE: served {n} for {FIRE_PAY * n} cash.")
                elif o == "push":
                    need = 2 if s["line"] >= 12 else (5 if s["line"] <= 5 else 3)
                    ok, txt = rng.check(need, label="upsell")
                    if ok:
                        n = min(PUSH_N, remaining)
                        s["cash"] += PUSH_PAY * n
                        remaining -= n
                        ev.append(f"PUSH: {txt}. Served {n} for {PUSH_PAY * n} cash.")
                    else:
                        s["line"] -= 1
                        ev.append(f"PUSH: {txt}. Served none, Line -1.")
                elif o == "fix":
                    if s["cash"] >= FIX_COST:
                        s["cash"] -= FIX_COST
                        s["line"] = min(LINE_MAX, s["line"] + FIX_GAIN)
                        fixed = True
                        ev.append(f"FIX: -{FIX_COST} cash, Line +{FIX_GAIN}, damage halved this wave.")
                    else:
                        ev.append("FIX: no cash for parts, skipped.")
                elif o == "platter":
                    if s["line"] < PLATTER_MIN:
                        ev.append(f"PLATTER: Line under {PLATTER_MIN}, the Reef cannot plate it.")
                    elif s["cash"] < PLATTER_COST:
                        ev.append("PLATTER: no cash for lobster, skipped.")
                    else:
                        n = min(PLATTER_N, remaining)
                        s["cash"] -= PLATTER_COST
                        remaining -= n
                        s["buzz"] += PLATTER_BUZZ
                        ev.append(f"PLATTER: -{PLATTER_COST} cash, served {n}, Buzz +{PLATTER_BUZZ}.")
        return remaining, fixed

    def apply(self, s, a, args, rng):
        ev = []
        twice = False
        shanghai = False
        if a in ORDER_NAMES:
            s["orders"] = s["orders"][1:] + [a]
            ev.append(f"Orders now {self.program_text(s)}.")
        elif a == "bank":
            s["token"] = 1
            ev.append("You bank the turn. Token held. The Reef repeats itself.")
        elif a == "spend":
            s["token"] = 0
            twice = True
            ev.append("Token spent: the Reef runs its orders twice.")
        elif a == "shanghai":
            s["cash"] -= SHANGHAI_COST
            shanghai = True
            ev.append(f"You pay {SHANGHAI_COST} and shanghai a dock crew.")

        wtype = s["next_wave"]
        roll = rng.d(6)
        base = self.wave_base(s["_turn"])
        covers = base + roll
        mod = ""
        if wtype == "light":
            covers -= 3
            mod = " -3 light"
        elif wtype == "rush":
            covers += 3
            mod = " +3 rush"
        covers = max(1, covers)
        ev.append(f"Wave {s['_turn']}: {covers} covers ({base} + roll {roll}{mod}), {TYPES[wtype]}.")

        remaining, fixed = self.run_program(s, covers, rng, ev, twice=twice)
        if shanghai:
            if remaining:
                ev.append(f"The dock crew serves the last {remaining} for tips.")
            remaining = 0
            s["line"] = min(LINE_MAX, s["line"] + 2)
            ev.append("Line +2.")

        dmg = remaining * (2 if wtype == "sailors" else 1)
        if fixed:
            dmg = dmg // 2
        if dmg:
            s["line"] -= dmg
            tags = ""
            if wtype == "sailors":
                tags += " (sea-wolves, doubled)"
            if fixed:
                tags += ", halved by FIX"
            ev.append(f"{remaining} unserved{tags}: Line -{dmg}.")

        if remaining == 0:
            s["buzz"] += 1
            s["streak"] = 0
            ev.append("Wave held. Buzz +1.")
            if wtype == "critic":
                s["buzz"] += 3
                ev.append("The columnist ate everything. Buzz +3.")
        else:
            s["streak"] += 1
            if remaining >= 3:
                loss = 2 if remaining >= 6 else 1
                s["buzz"] -= loss
                s["rivals"]["Rourke's Chop House"] += 2
                ev.append(f"{remaining} walked out. Buzz -{loss}. Rourke's doorman waves them in: Rourke +2.")
                if wtype == "critic":
                    s["buzz"] -= 3
                    ev.append("The columnist left hungry. Buzz -3.")
            else:
                ev.append(f"{remaining} left unserved. Wave not held.")
        return ev

    def advance(self, s, rng):
        ev = []
        due = self.upkeep_due(s, s["_turn"] - 1)
        s["cash"] -= due
        ev.append(f"Upkeep {due}.")
        if s["cash"] < 0:
            s["cash"] = 0
            s["buzz"] -= SHORTFALL_BUZZ
            ev.append(f"You cannot pay. The Syndicate covers it and word gets around. Cash 0, Buzz -{SHORTFALL_BUZZ}.")
        if s["_turn"] == 8 and not s["hidden"]["reviewed"]:
            s["hidden"]["reviewed"] = True
            r = self.rank(s)
            if r <= 3:
                s["cash"] += REVIEW_BONUS
                ev.append(f"Wave 8: the Syndicate reviews the League. Rank {r}: they wire {REVIEW_BONUS} cash.")
            else:
                s["upkeep"] = UPKEEP_CUT
                ev.append(f"Wave 8: the Syndicate reviews the League. Rank {r}: upkeep rises by {UPKEEP_CUT} a wave.")
            ev.append(f"Bigger seatings from here. PLATTER is on the menu (Line {PLATTER_MIN}+).")
        if s["_turn"] == 13:
            ev.append("Wave 13: the late crowd. Seatings grow again.")
        for name in s["rivals"]:
            s["rivals"][name] = rng.drift(s["rivals"][name], 3, 99, p_up=RIVAL_UP, p_down=RIVAL_DOWN)
        if s["_turn"] > 8:
            for name in s["rivals"]:
                s["rivals"][name] += RIVAL_CLIMB
            s["rivals"]["Rourke's Chop House"] += ROURKE_CLIMB
        deck = s["hidden"]["deck"]
        idx = s["_turn"] - 1
        s["next_wave"] = deck[idx] if idx < len(deck) else "normal"
        rk = s["rivals"]["Rourke's Chop House"]
        ev.append(f"Rourke's Chop House sits at Buzz {rk}. Next: {TYPES[s['next_wave']]}.")
        return ev

    def status_line(self, s):
        tok = " +token" if s["token"] else ""
        return f"Cash {s['cash']} | Line {s['line']} | Buzz {s['buzz']} #{self.rank(s)}/6 | {self.program_text(s)}{tok}"

    def check_end(self, s):
        if s["line"] <= 0:
            return {"result": "loss", "reason": "the Reef collapsed: Line 0"}
        if s["_turn"] > self.turns:
            r = self.rank(s)
            if r <= WIN_RANK:
                return {"result": "win", "reason": f"open after wave 16 at rank {r}, cash {s['cash']}, line {s['line']}"}
            return {"result": "loss", "reason": f"rank {r}: the Syndicate keeps only the top three"}
        return None

    def visible(self, s):
        v = {k: val for k, val in s.items() if k not in ("hidden", "_rng", "_turn", "_ended")}
        v["rank"] = self.rank(s)
        v["next_wave"] = TYPES[s["next_wave"]]
        return v

    def heuristic(self, s, options, rng):
        ids = {o["id"] for o in options}
        fires = s["orders"].count("fire")
        has_fix = "fix" in s["orders"]
        nxt = s["next_wave"]
        if "shanghai" in ids and s["cash"] >= SHANGHAI_COST + 10:
            return "shanghai"
        if "spend" in ids and (nxt in ("critic", "rush", "sailors") or s["line"] <= 8 or s["_turn"] >= 13):
            return "spend"
        if s["line"] <= 7 and s["cash"] >= FIX_COST + 5:
            return "fix"
        if s["line"] <= 12 and not has_fix and s["cash"] >= FIX_COST + 5:
            return "fix"
        if s["cash"] < 15:
            return "fire"
        if "platter" in ids and "platter" not in s["orders"] and s["cash"] >= 40 and s["line"] >= 10:
            return "platter"
        if "platter" in ids and s["orders"].count("platter") < 2 and s["cash"] >= 80 and s["line"] >= 12:
            return "platter"
        if fires < 2:
            return "fire"
        if s["line"] >= 12 and "push" not in s["orders"]:
            return "push"
        if "bank" in ids and s["line"] >= 10 and s["cash"] >= 25:
            return "bank"
        if s["line"] <= 15 and not has_fix and s["cash"] >= 30:
            return "fix"
        return "fire"


if __name__ == "__main__":
    run(G)
