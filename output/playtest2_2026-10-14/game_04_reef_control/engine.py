"""Reef Control: a /play engine.

Rolls: FORM=7 build order, SET=9 shipwreck atoll, ROLE=35 air traffic controller,
LOOP=34 visit one district / spend / poll, CLOCK=1 food runs out, TWIST=39 rules change
on a published schedule, WIN=14 keep a settlement above a threshold, MAP=3 5x5 grid with fog,
TONE=8 cozy with teeth.

Rulesheet (8 lines):
1. Each day pick one: forage a tile, or build one thing with food (labor). Camp is C3. At dawn the camp eats 1 food per 3 souls (rounded up).
2. Forage: roll d6, need 4+ for the tile's full yield, else half. Every visit, yours or Dekker's, lowers that tile's yield by 1 (min 2).
3. The inner ring is on foot; the outer ring needs the Raft. The Wreck is somewhere on the outer ring; visiting it unlocks Storehouse and Tower.
4. Builds (food): Trap 4 (water rolls +1), Raft 6, Smokehouse 6 (all rolls +1), Storehouse 7, Palisade 7, Tower 9 (day 10+).
5. Tide table: days 5, 10, 15, 20 are king tides: reef and Wreck closed, lagoon yield doubled. Dawn of day 12 a storm takes half your food unless Storehouse.
6. Dekker's crew (3 who split off) strips one tile a day near his corner. From day 10 they raid 3 food a night unless Palisade.
7. After the dawn meal: food at 0, one soul walks to Dekker; food 20+, one of Dekker's walks to you. Fewer than 6 souls and the camp is done. Two bad forage rolls in a row: Dekker offers 8 food for one soul.
8. Tower lit at dawn on days 13 and 17: roll d6, 3+ for a 12-food airdrop. Win: 8+ souls when the ship comes after day 20.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

COLS = "ABCDE"
TERRAIN_NAME = {"J": "jungle", "L": "lagoon", "R": "reef", "W": "wreck", "D": "Dekker's camp", "C": "camp"}
BUILDS = {
    "build_trap": ("Trap", 4),
    "build_raft": ("Raft", 6),
    "build_smoke": ("Smokehouse", 6),
    "build_store": ("Storehouse", 7),
    "build_wall": ("Palisade", 7),
    "build_tower": ("Tower", 9),
}
KING_TIDES = (5, 10, 15, 20)
STORM_DAY = 12
PLANE_DAYS = (13, 17)
WIN_SOULS = 8
RAID = 3
INNER_Y = {"J": 5, "L": 5, "R": 6}
OUTER_Y = {"J": 6, "L": 6, "R": 7}
WRECK_Y = 8
MIN_SOULS = 6


def key(r, c):
    return f"{COLS[c]}{r + 1}"


def rc(k):
    return int(k[1]) - 1, COLS.index(k[0])


def ring(r, c):
    return max(abs(r - 2), abs(c - 2))


def upkeep(s):
    return (s["souls"] + 2) // 3


def side_of(r, c, rng):
    sides = []
    if r == 0:
        sides.append("north")
    if r == 4:
        sides.append("south")
    if c == 0:
        sides.append("west")
    if c == 4:
        sides.append("east")
    return rng.choice(sides)


class G(Game):
    name = "Reef Control"
    turns = 20

    # ------------------------------------------------------------ setup
    def init_state(self, rng):
        tiles = {}
        inner = [(r, c) for r in range(5) for c in range(5) if ring(r, c) == 1]
        outer = [(r, c) for r in range(5) for c in range(5) if ring(r, c) == 2]
        # inner ring: guarantee 2 jungle and 1 lagoon so a king tide never empties the options
        inner_terr = ["J", "J", "L"] + [rng.choice("JLR") for _ in range(5)]
        rng.shuffle(inner_terr)
        for (r, c), t in zip(inner, inner_terr):
            base = INNER_Y[t] + rng.d(2) - 1
            tiles[key(r, c)] = {"t": t, "y": base, "seen": True, "visited": False}
        dek = rng.choice([(0, 0), (0, 4), (4, 0), (4, 4)])
        wreck_choices = [p for p in outer if p != dek and max(abs(p[0] - dek[0]), abs(p[1] - dek[1])) > 1]
        wreck = rng.choice(wreck_choices)
        for (r, c) in outer:
            if (r, c) == dek:
                tiles[key(r, c)] = {"t": "D", "y": 0, "seen": False, "visited": False}
            elif (r, c) == wreck:
                tiles[key(r, c)] = {"t": "W", "y": WRECK_Y, "seen": False, "visited": False}
            else:
                t = rng.choice("JLRR")
                base = OUTER_Y[t] + rng.d(2) - 1
                tiles[key(r, c)] = {"t": t, "y": base, "seen": False, "visited": False}
        tiles["C3"] = {"t": "C", "y": 0, "seen": True, "visited": True}
        return {
            "food": 10,
            "souls": 10,
            "built": [],
            "wreck_found": False,
            "streak": 0,
            "tiles": tiles,
            "hint": f"Debris keeps washing up on the {side_of(wreck[0], wreck[1], rng)} shore.",
            "hidden": {"dekker": key(*dek), "wreck": key(*wreck), "dekker_crew": 3, "dek_pos": [dek[0], dek[1]]},
        }

    # ------------------------------------------------------------ helpers
    def king(self, s):
        return s["_turn"] in KING_TIDES

    def need(self, s, t):
        n = 4
        if "Smokehouse" in s["built"]:
            n -= 1
        if t in ("L", "R", "W") and "Trap" in s["built"]:
            n -= 1
        return max(2, n)

    def eff_yield(self, s, k):
        tile = s["tiles"][k]
        y = tile["y"]
        if tile["t"] == "L" and self.king(s):
            y *= 2
        return y

    def reachable(self, s, k):
        tile = s["tiles"][k]
        if not tile["seen"] or tile["t"] in ("C", "D"):
            return False
        r, c = rc(k)
        if ring(r, c) == 2 and "Raft" not in s["built"]:
            return False
        if self.king(s) and tile["t"] in ("R", "W"):
            return False
        return True

    def frontier(self, s, k):
        r, c = rc(k)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < 5 and 0 <= cc < 5 and not s["tiles"][key(rr, cc)]["seen"]:
                    return True
        return False

    def reveal_around(self, s, k):
        r, c = rc(k)
        new = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < 5 and 0 <= cc < 5:
                    kk = key(rr, cc)
                    if not s["tiles"][kk]["seen"]:
                        s["tiles"][kk]["seen"] = True
                        new.append(kk)
        return new

    def tile_desc(self, s, k):
        t = s["tiles"][k]
        name = TERRAIN_NAME[t["t"]]
        if t["t"] in "JLRW":
            return f"{k} {name} {t['y']}"
        return f"{k} {name}"

    def map_rows(self, s):
        rows = []
        for r in range(5):
            cells = []
            for c in range(5):
                t = s["tiles"][key(r, c)]
                if not t["seen"]:
                    cells.append("??")
                elif t["t"] in ("C", "D"):
                    cells.append(t["t"] + t["t"])
                else:
                    cells.append(f"{t['t']}{t['y']}")
            rows.append(f"{r + 1} " + " ".join(cells))
        return ["  A  B  C  D  E"] + rows

    # ------------------------------------------------------------ contract
    def options(self, s):
        o = []
        forage = []
        for k in s["tiles"]:
            if self.reachable(s, k):
                tile = s["tiles"][k]
                ey = self.eff_yield(s, k)
                need = self.need(s, tile["t"])
                exp = ey * ((7 - need) / 6) + (ey // 2) * ((need - 1) / 6)
                forage.append((k, tile, ey, need, exp))
        forage.sort(key=lambda f: (-f[4], f[0]))
        picks = forage[:3]
        fr = [f for f in forage if self.frontier(s, f[0])]
        if fr and not any(self.frontier(s, f[0]) for f in picks):
            picks = picks[:2] + [fr[0]]
        wk = [f for f in forage if f[1]["t"] == "W" and not s["wreck_found"]]
        if wk and wk[0] not in picks:
            picks = picks[:2] + [wk[0]]
        for k, tile, ey, need, exp in picks:
            name = TERRAIN_NAME[tile["t"]]
            tag = ""
            if tile["t"] == "L" and self.king(s):
                tag = " king tide x2"
            if self.frontier(s, k):
                tag += ", reveals fog"
            o.append({"id": f"forage_{k}", "label": f"Forage {k} {name} (yield {ey}{tag}, need {need}+)",
                      "args": {"ey": ey, "need": need, "wreck": int(tile["t"] == "W" and not s["wreck_found"]),
                               "frontier": int(self.frontier(s, k))}})
        builds = []
        for bid, (name, cost) in BUILDS.items():
            if name in s["built"] or s["food"] < cost:
                continue
            if name in ("Storehouse", "Tower") and not s["wreck_found"]:
                continue
            if name == "Tower" and s["_turn"] < 10:
                continue
            builds.append({"id": bid, "label": f"Build {name} (-{cost} food)", "args": {}})
        lever = s["streak"] >= 2 and s["souls"] > MIN_SOULS
        o += builds[: (1 if lever else 2)]
        if lever:
            o.append({"id": "bargain", "label": "Dekker's bargain: one soul for 8 food", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        ev = []
        if a.startswith("forage_"):
            k = a[7:]
            tile = s["tiles"][k]
            ey = self.eff_yield(s, k)
            need = self.need(s, tile["t"])
            ok, txt = rng.check(need, label="forage")
            got = ey if ok else ey // 2
            s["food"] += got
            tile["y"] = max(2, tile["y"] - 1)
            tile["visited"] = True
            kind = "full" if ok else "half"
            ev.append(f"{txt}. {k} {TERRAIN_NAME[tile['t']]} gave {got} food ({kind} yield). Tile yield now {tile['y']}.")
            s["streak"] = 0 if ok else s["streak"] + 1
            new = self.reveal_around(s, k)
            if new:
                ev.append("Revealed: " + ", ".join(self.tile_desc(s, n) for n in new) + ".")
            if tile["t"] == "W" and not s["wreck_found"]:
                s["wreck_found"] = True
                ev.append("The Wreck is yours to strip: Storehouse and Tower can now be built.")
        elif a in BUILDS:
            name, cost = BUILDS[a]
            s["food"] -= cost
            s["built"].append(name)
            ev.append(f"Built {name} for {cost} food.")
        elif a == "bargain":
            s["food"] += 8
            s["souls"] -= 1
            s["hidden"]["dekker_crew"] += 1
            s["streak"] = 0
            ev.append("One soul walks to Dekker's side with a goodbye. Food +8, souls -1.")
        return ev

    def advance(self, s, rng):
        ev = []
        t = s["_turn"]
        if t > self.turns:
            return ev
        # Dekker strips a tile near his corner
        dr, dc = s["hidden"]["dek_pos"]
        cand = []
        for r in range(5):
            for c in range(5):
                k = key(r, c)
                tile = s["tiles"][k]
                if tile["t"] in ("J", "L", "R", "W") and max(abs(r - dr), abs(c - dc)) <= 2 and tile["y"] > 2:
                    cand.append((tile["y"], k))
        if cand:
            cand.sort(key=lambda x: (-x[0], x[1]))
            y, k = cand[0]
            tile = s["tiles"][k]
            tile["y"] -= 1
            tile["seen"] = True
            ev.append(f"Dekker's crew worked {k} {TERRAIN_NAME[tile['t']]} (yield now {tile['y']}).")
        else:
            ev.append("Dekker's corner is picked clean; his crew sat idle.")
        # night raid
        if t >= 11:
            if "Palisade" in s["built"]:
                ev.append("Dekker's raiders tested the Palisade and went home empty.")
            else:
                s["food"] = max(0, s["food"] - RAID)
                ev.append(f"Dekker's raiders took {RAID} food in the night.")
        # storm
        if t == STORM_DAY:
            if "Storehouse" in s["built"]:
                ev.append("Dawn of day 12: the storm hit. The Storehouse held; nothing lost.")
            else:
                lost = s["food"] // 2
                s["food"] -= lost
                ev.append(f"Dawn of day 12: the storm hit and swept away {lost} food.")
        # planes
        if t in PLANE_DAYS:
            if "Tower" in s["built"]:
                ok, txt = rng.check(3, label="airdrop")
                if ok:
                    s["food"] += 12
                    ev.append(f"Plane overhead, Tower lit. {txt}. Airdrop: food +12.")
                else:
                    ev.append(f"Plane overhead, Tower lit. {txt}. It did not see you.")
            else:
                ev.append("A plane passed high over the atoll. Nothing on the ground to see.")
        # dawn meal
        up = upkeep(s)
        s["food"] -= up
        ev.append(f"Dawn meal: {up} food.")
        if s["food"] <= 0:
            s["food"] = 0
            s["souls"] -= 1
            s["hidden"]["dekker_crew"] += 1
            ev.append("Food at 0. One soul walked to Dekker. Souls -1.")
        elif s["food"] >= 20 and s["hidden"]["dekker_crew"] > 0:
            s["souls"] += 1
            s["hidden"]["dekker_crew"] -= 1
            ev.append("Food 20+. One of Dekker's people walked over to your fire. Souls +1.")
        if t == 10:
            ev.append("Day 10: Dekker's raids start tonight. The Tower can be built now.")
        if t in KING_TIDES:
            ev.append("King tide today: reef and Wreck closed, lagoon yields doubled.")
        return ev

    def status_line(self, s):
        b = ",".join(s["built"]) if s["built"] else "-"
        t = s["_turn"]
        if t in KING_TIDES:
            tide = "KING"
        else:
            nxt = next((k for k in KING_TIDES if k > t), None)
            tide = f"low (king {nxt})" if nxt else "low"
        return f"Food {s['food']} | Souls {s['souls']} | Built {b} | Tide {tide}"

    def check_end(self, s):
        if s["souls"] < MIN_SOULS:
            return {"result": "loss", "reason": f"souls {s['souls']}, the camp broke up"}
        if s["_turn"] > self.turns:
            if s["souls"] >= WIN_SOULS:
                return {"result": "win", "reason": f"ship came for {s['souls']} souls"}
            return {"result": "loss", "reason": f"ship came for {s['souls']} souls, needed {WIN_SOULS}"}
        return None

    def visible(self, s):
        v = {k: v for k, v in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "tiles", "_seed")}
        v["map"] = self.map_rows(s)
        v["upkeep"] = upkeep(s)
        v["schedule"] = "king tides 5/10/15/20; raids and Tower from 10; storm dawn 12; planes 13 and 17; ship after 20"
        return v

    # ------------------------------------------------------------ heuristic
    def heuristic(self, s, options, rng):
        ids = {o["id"]: o for o in options}
        up = upkeep(s)
        food = s["food"]
        t = s["_turn"]
        if "bargain" in ids and food < up and s["souls"] >= 9:
            return "bargain"
        # build plan with deadlines: trap first, raft by day 6, store before the storm, wall before the raids, tower before plane 13
        plan = [
            ("build_trap", 1, 20),
            ("build_raft", 1, 12),
            ("build_store", 1, STORM_DAY - 1),
            ("build_wall", 6, 14),
            ("build_tower", 10, 16),
            ("build_smoke", 1, 15),
        ]
        for b, lo, hi in plan:
            if b not in ids or t < lo or t > hi:
                continue
            cost = BUILDS[b][1]
            if food - cost >= up:
                return b
        forages = [o for o in options if o["id"].startswith("forage_")]
        if forages:
            best = max(forages, key=lambda o: (o["args"]["wreck"], o["args"]["ey"] * (7 - o["args"]["need"]), o["args"]["frontier"]))
            return best["id"]
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
