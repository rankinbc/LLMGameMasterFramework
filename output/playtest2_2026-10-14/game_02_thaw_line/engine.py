"""Thaw Line: a /play engine.

Rolls: FORM=10 heist (plan with limited intel, then execute), SET=10 arctic research station,
ROLE=39 hotel manager who can see ghosts, LOOP=31 place one tile; adjacency and chains score,
CLOCK=12 the map floods tile by tile, TWIST=24 huge advantage that decays, WIN=19 one specimen
with all three traits, MAP=10 no map, a deck of encounters, TONE=2 dry humor.

Premise: You manage Kelvin Station, an Arctic research station that pays its bills as a hotel
for visiting scientists. The 1971 crew froze here and still haunt the modules; only you can see
them. Boreas Holdings wants the Specimen (a worm thawed from Core 7) proven ALIVE, STABLE and
SEQUENCED and flown out before the shelf (the ghosts call it Gunnar) breaks up under you.

Rulesheet (8 lines):
1. The station is a line of 12 slots; slots 1-3 hold a Freezer, a Bunk and a Generator. Each turn place one of your 3 drawn modules in the next empty slot, or do one other thing (hunkering down redraws the hand and saves 1 fuel).
2. A module is powered if a Generator stands within two slots of it, water or not. Each turn burns 2 fuel plus 1 per Generator; each powered Bunk pays 3 back. Fuel starts at 52 and only guests refill it.
3. Trials (3 fuel, need a powered Lab) prove one trait each: roll d6, need 5 minus powered Labs (min 3). SEQUENCED any time; ALIVE and STABLE only after the thaw on turn 10.
4. After turn 9 the shelf calves: one slot drowns at the end of each of turns 10 to 17 in a hidden order, and the ice groans under the next one a turn early. Before the calving, ask the ghosts (2 fuel) to learn when the two lowest unrevealed slots drown.
5. The Specimen lives in your Freezers: with no powered Freezer standing you cannot run trials or board the plane.
6. Swap (2 fuel): trade the groaning module with its ridge-side neighbour (sea-side if there is none) before the sea takes the slot.
7. Two failed trials in a row open a Seance (2 fuel): your next trial needs only 2+.
8. Win: three traits, then Call the plane (2 fuel): roll d6, need 4 minus powered Radios (min 2). Lose: fuel 0, nothing standing, or the end of turn 18 (the plane lands then anyway: win only with 3 traits and a powered Freezer).
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

TILES = {"G": "Generator", "L": "Lab", "F": "Freezer", "B": "Bunk", "R": "Radio"}
TILE_ORDER = "GLFRB"
TRAITS = ["SEQ", "ALIVE", "STABLE"]
N_SLOTS = 12
THAW = 10
START_FUEL = 52
DROWNINGS = 8  # at the end of turns 10..17
TRIAL_BASE = 5
TRIAL_MIN = 3
DECK = "GGGG" + "LLLLLL" + "FFFF" + "BBBB" + "RRRR"
TRIAL_COST = 3
BUNK_PAY = 3
START = ["F", "B", "G"]


def standing(x):
    return x is not None and x != "~"


def runs(slots):
    out, cur = [], []
    for i, x in enumerate(slots):
        if standing(x):
            cur.append(i)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def powered_idx(slots):
    """A standing module is powered if a Generator stands within two slots of it, water or not."""
    p = []
    n = len(slots)
    for i, x in enumerate(slots):
        if not standing(x):
            continue
        if any(slots[j] == "G" for j in range(max(0, i - 2), min(n, i + 3))):
            p.append(i)
    return p


def count_powered(slots, letter):
    p = powered_idx(slots)
    return sum(1 for i in p if slots[i] == letter)


def count_standing(slots, letter):
    return sum(1 for x in slots if x == letter)


def ordinal(n):
    return f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'}"


class G(Game):
    name = "Thaw Line"
    turns = 18

    # ------------------------------------------------------------ state
    def init_state(self, rng):
        deck = list(DECK)
        rng.shuffle(deck)
        hand = [deck.pop() for _ in range(3)]
        cracks = list(range(1, N_SLOTS + 1))
        rng.shuffle(cracks)
        events = ["storm"] * 4 + ["charter"] * 3 + ["supply"] * 2 + ["sighting"] * 3 + ["quiet"] * 6
        rng.shuffle(events)
        return {
            "fuel": START_FUEL,
            "slots": list(START) + [None] * (N_SLOTS - 3),
            "hand": hand,
            "traits": [],
            "known": {},
            "groan": None,
            "streak": 0,
            "seance": False,
            "hunker": False,
            "escaped": False,
            "hidden": {"deck": deck, "cracks": cracks, "events": events},
        }

    # ------------------------------------------------------------ helpers
    def next_empty(self, s):
        for i, x in enumerate(s["slots"]):
            if x is None:
                return i
        return None

    def trial_need(self, s):
        if s["seance"]:
            return 2
        return max(TRIAL_MIN, TRIAL_BASE - count_powered(s["slots"], "L"))

    def swap_target(self, s):
        """Return (groan_idx, neighbour_idx) or None."""
        g = s["groan"]
        if not g:
            return None
        gi = g - 1
        sl = s["slots"]
        if not standing(sl[gi]):
            return None
        if gi + 1 < N_SLOTS and standing(sl[gi + 1]):
            return gi, gi + 1
        if gi - 1 >= 0 and standing(sl[gi - 1]):
            return gi, gi - 1
        return None

    def unrevealed(self, s):
        return [i + 1 for i, x in enumerate(s["slots"]) if x != "~" and str(i + 1) not in s["known"]]

    def rank_text(self, slot, rank):
        if rank > DROWNINGS:
            return f"slot {slot} outlasts the plane"
        return f"slot {slot} goes under at the end of turn {THAW + rank - 1} ({ordinal(rank)} to drown)"

    def hand_text(self, s):
        return ", ".join(TILES[x] for x in s["hand"]) or "empty"

    # ------------------------------------------------------------ options
    def options(self, s):
        o = []
        t, f = s["_turn"], s["fuel"]
        sl = s["slots"]
        nxt = self.next_empty(s)
        if nxt is not None:
            for tile in sorted(list(dict.fromkeys(s["hand"])), key=TILE_ORDER.index):
                o.append({"id": f"place_{tile}", "label": f"Place a {TILES[tile]} in slot {nxt + 1}"})
        pl = count_powered(sl, "L")
        pf = count_powered(sl, "F")
        if f >= TRIAL_COST and pl >= 1 and pf >= 1:
            need = self.trial_need(s)
            for tr in TRAITS:
                if tr in s["traits"]:
                    continue
                if tr != "SEQ" and t < THAW:
                    continue
                o.append({"id": f"trial_{tr.lower()}", "label": f"Run the {tr} trial ({TRIAL_COST} fuel, roll d6 need {need}+)"})
        if f >= 2 and t < THAW and self.unrevealed(s):
            o.append({"id": "ask", "label": "Ask the ghosts about the next two unrevealed slots (2 fuel)"})
        st = self.swap_target(s)
        if st and f >= 2:
            gi, ni = st
            o.append({"id": "swap", "label": f"Swap the {TILES[sl[gi]]} in slot {gi + 1} with the {TILES[sl[ni]]} in slot {ni + 1} (2 fuel)"})
        if s["streak"] >= 2 and not s["seance"] and f >= 2 and len(s["traits"]) < 3:
            o.append({"id": "seance", "label": "Hold a seance: the 1971 crew run the next trial (2 fuel, next trial needs 2+)"})
        pr = count_powered(sl, "R")
        if len(s["traits"]) == 3 and f >= 2 and t >= THAW:
            o.append({"id": "call", "label": f"Call the plane (2 fuel, roll d6 need {max(2, 4 - pr)}+)"})
        o.append({"id": "hold", "label": "Hunker down (burn 1 less fuel tonight; redraw the hand)"})
        return o

    # ------------------------------------------------------------ apply
    def apply(self, s, a, args, rng):
        ev = []
        sl = s["slots"]
        h = s["hidden"]
        if a.startswith("place_"):
            tile = a[-1]
            nxt = self.next_empty(s)
            sl[nxt] = tile
            s["hand"].remove(tile)
            if h["deck"]:
                s["hand"].append(h["deck"].pop())
            pw = "powered" if nxt in powered_idx(sl) else "unpowered"
            ev.append(f"{TILES[tile]} bolted into slot {nxt + 1} ({pw}).")
            if tile == "L":
                ev.append(f"Powered Labs now {count_powered(sl, 'L')}: trial need {self.trial_need(s)}+.")
            elif tile == "B":
                ev.append(f"Powered Bunks now {count_powered(sl, 'B')}: guests pay {BUNK_PAY * count_powered(sl, 'B')} a night.")
            elif tile == "G":
                ev.append(f"Generators now {count_standing(sl, 'G')}: burn {2 + count_standing(sl, 'G')} a night.")
            ev.append(f"Hand: {self.hand_text(s)}.")
        elif a.startswith("trial_"):
            tr = a[6:].upper()
            s["fuel"] -= TRIAL_COST
            need = self.trial_need(s)
            ok, txt = rng.check(need, label=tr)
            s["seance"] = False
            if ok:
                s["traits"].append(tr)
                s["streak"] = 0
                ev.append(f"{txt}. {tr} confirmed. Traits {len(s['traits'])}/3.")
            else:
                s["streak"] += 1
                ev.append(f"{txt}. The bench is inconclusive. Failed trials in a row: {s['streak']}.")
        elif a == "ask":
            s["fuel"] -= 2
            got = self.unrevealed(s)[:2]
            parts = []
            for slot in got:
                rank = h["cracks"].index(slot) + 1
                s["known"][str(slot)] = rank
                parts.append(self.rank_text(slot, rank))
            ev.append("The crew of '71 confer: " + "; ".join(parts) + ".")
        elif a == "swap":
            s["fuel"] -= 2
            gi, ni = self.swap_target(s)
            sl[gi], sl[ni] = sl[ni], sl[gi]
            ev.append(f"Dragged the {TILES[sl[ni]]} to slot {ni + 1}; the {TILES[sl[gi]]} now sits in groaning slot {gi + 1}.")
        elif a == "seance":
            s["fuel"] -= 2
            s["seance"] = True
            ev.append("The 1971 crew take the bench. Next trial needs 2+.")
        elif a == "call":
            s["fuel"] -= 2
            pr = count_powered(sl, "R")
            need = max(2, 4 - pr)
            ok, txt = rng.check(need, label="plane")
            if ok:
                s["escaped"] = True
                ev.append(f"{txt}. The Twin Otter lands on the last firm ice. Specimen aboard.")
            else:
                ev.append(f"{txt}. The pilot turns back in the whiteout. Try again tomorrow.")
        elif a == "hold":
            s["hunker"] = True
            ev.append("You turn the thermostats down and do the brochure copy.")
            if self.next_empty(s) is not None and h["deck"]:
                old = s["hand"]
                s["hand"] = []
                while len(s["hand"]) < 3 and h["deck"]:
                    s["hand"].append(h["deck"].pop())
                h["deck"] = old + h["deck"]
                ev.append(f"The supply sled brings new crates. Hand: {self.hand_text(s)}.")
        return ev

    # ------------------------------------------------------------ advance
    def advance(self, s, rng):
        ev = []
        t = s["_turn"]
        sl = s["slots"]
        h = s["hidden"]
        # the shelf (rival)
        if t == THAW:
            ev.append("Gunnar calves with a sound like furniture. The core bay thaws: the Specimen is awake. ALIVE and STABLE trials are open.")
            s["groan"] = h["cracks"][0]
            ev.append(self.groan_text(s))
        elif THAW < t <= THAW + DROWNINGS:
            g = s["groan"]
            was = sl[g - 1]
            sl[g - 1] = "~"
            ev.append(f"Slot {g} ({TILES[was] if standing(was) else 'empty'}) goes under.")
            idx = t - THAW
            if idx < DROWNINGS:
                s["groan"] = h["cracks"][idx]
                ev.append(self.groan_text(s))
            else:
                s["groan"] = None
                ev.append("The ice is quiet. Nothing more drowns before the plane.")
        elif t < THAW:
            ev.append(f"Gunnar is quiet. The calving comes at the end of turn {THAW - 1}.")
        # fuel
        gens = count_standing(sl, "G")
        burn = 2 + gens - (1 if s["hunker"] else 0)
        s["hunker"] = False
        income = BUNK_PAY * count_powered(sl, "B")
        s["fuel"] += income - burn
        ev.append(f"Burned {burn} fuel, guests paid {income}. Fuel {s['fuel']}.")
        # encounter deck
        e = h["events"].pop(0) if h["events"] else "quiet"
        if e == "storm":
            s["fuel"] -= 3
            ev.append(f"Storm: the heaters run all night. Fuel -3 ({s['fuel']}).")
        elif e == "charter":
            pb = count_powered(sl, "B")
            s["fuel"] += BUNK_PAY * pb
            ev.append(f"A charter of glaciologists checks in and pays in diesel: +{BUNK_PAY * pb} fuel ({s['fuel']}).")
        elif e == "supply":
            s["fuel"] += 5
            ev.append(f"Supply drop: 5 drums land on the ice ({s['fuel']}).")
        elif e == "sighting":
            un = self.unrevealed(s)
            if un:
                slot = un[0]
                rank = h["cracks"].index(slot) + 1
                s["known"][str(slot)] = rank
                ev.append(f"Dr. Vang drifts through the wall and mentions that {self.rank_text(slot, rank)}.")
            else:
                ev.append("Dr. Vang drifts through the wall. She has nothing new to say.")
        else:
            ev.append("A quiet night. The ghosts play cards.")
        # specimen
        if t > THAW and count_powered(sl, "F") == 0:
            ev.append("No powered Freezer stands. The Specimen sits in a cooler of snow: no trials, no flight, until you fix that.")
        ev.append(f"Powered: {count_powered(sl, 'L')} Lab, {count_powered(sl, 'F')} Freezer, {count_powered(sl, 'R')} Radio, {count_powered(sl, 'B')} Bunk.")
        return ev

    def groan_text(self, s):
        g = s["groan"]
        x = s["slots"][g - 1]
        what = TILES[x] if standing(x) else "nothing"
        return f"The ice groans under slot {g} ({what}). It goes at the end of this turn."

    # ------------------------------------------------------------ status
    def status_line(self, s):
        sl = s["slots"]
        p = powered_idx(sl)
        cells = []
        for i, x in enumerate(sl):
            if x is None:
                c = "."
            elif x == "~":
                c = "~"
            elif i in p:
                c = x
            else:
                c = x.lower()
            if s["groan"] == i + 1:
                c += "!"
            cells.append(c)
        tr = "/".join(s["traits"]) if s["traits"] else "none"
        return f"Fuel {s['fuel']} | Traits {len(s['traits'])}/3 {tr} | Line {' '.join(cells)} | Labs on {count_powered(sl, 'L')}"

    def check_end(self, s):
        if s["escaped"]:
            return {"result": "win", "reason": f"flew out with 3 traits on turn {s['_turn']}, fuel {s['fuel']}"}
        if s["fuel"] <= 0:
            return {"result": "loss", "reason": "fuel ran out; the station froze"}
        if not any(standing(x) for x in s["slots"]):
            return {"result": "loss", "reason": "nothing left standing"}
        if s["_turn"] > self.turns:
            if len(s["traits"]) == 3 and count_powered(s["slots"], "F") >= 1:
                return {"result": "win", "reason": "the plane found you on the last floe with the Specimen intact"}
            return {"result": "loss", "reason": f"the plane came and went; traits {len(s['traits'])}/3"}
        return None

    # ------------------------------------------------------------ heuristic
    def heuristic(self, s, options, rng):
        ids = [o["id"] for o in options]
        t, f = s["_turn"], s["fuel"]
        sl = s["slots"]
        if "call" in ids:
            return "call"
        if "seance" in ids:
            return "seance"
        if "swap" in ids and f >= 8:
            gi, ni = self.swap_target(s)
            val = {"G": 5, "F": 4, "R": 3, "L": 2, "B": 1}
            if sl[gi] == "F" and count_powered(sl, "F") > 1:
                val["F"] = 1
            if sl[gi] == "R" and count_powered(sl, "R") > 1:
                val["R"] = 1
            if val[sl[gi]] > val[sl[ni]]:
                return "swap"
        trials = [i for i in ids if i.startswith("trial_")]
        if t >= THAW:
            if trials and f >= TRIAL_COST:
                return trials[0]
            places = [i for i in ids if i.startswith("place_")]
            for want in ("G", "F", "L"):
                if f"place_{want}" in places:
                    return f"place_{want}"
            return "hold"
        # phase 1
        if "ask" in ids and t == 1 and f >= 30:
            return "ask"
        nxt = self.next_empty(s)
        remaining = N_SLOTS - nxt if nxt is not None else 0
        turns_left = THAW - t  # placement turns left in phase 1 including this one
        need = self.trial_need(s)
        if "trial_seq" in ids and f >= 16 and (need <= 3 or (need <= 4 and remaining < turns_left)):
            return "trial_seq"
        places = [i for i in ids if i.startswith("place_")]
        if places:
            known_rank = s["known"].get(str(nxt + 1))
            cG, cL, cF, cR, cB = (count_standing(sl, x) for x in "GLFRB")
            burn = 2 + cG
            income = BUNK_PAY * count_powered(sl, "B")
            in_range = any(sl[j] == "G" for j in range(max(0, nxt - 2), min(N_SLOTS, nxt + 3)))
            desire = {}
            desire["R"] = 10 if (cR == 0 and remaining <= 4) else (7 if cR == 0 else 1)
            desire["G"] = 7 if cG < 2 else (0 if cG < 3 else -5)
            if cG < 2 and s["known"].get("3", 99) <= 3:
                desire["G"] = 9
            desire["L"] = 8 if cL < 3 else (5 if cL < 4 else 2)
            desire["F"] = 9 if (cF < 2 and remaining <= 2) else (6 if cF < 2 else 0)
            desire["B"] = 6 if income < burn + 2 else 3
            if not in_range and cG < 3:
                desire["G"] = 11
                for k in "LFRB":
                    desire[k] -= 4
            if known_rank is not None and known_rank <= 3:
                desire["B"] = 9
                for k in "GLFR":
                    desire[k] -= 3
            best = max(places, key=lambda p: desire[p[-1]])
            can_mulligan = len(s["hidden"]["deck"]) >= 3 and t <= 7
            if can_mulligan and (desire[best[-1]] <= 2 or (not in_range and cG < 3 and "place_G" not in places)
                                 or (cR == 0 and remaining <= 3 and "place_R" not in places)):
                return "hold"
            return best
        if "trial_seq" in ids and f >= 12:
            return "trial_seq"
        return "hold"


if __name__ == "__main__":
    run(G)
