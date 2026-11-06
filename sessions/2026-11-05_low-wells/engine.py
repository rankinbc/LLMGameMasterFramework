"""Low Wells: a mercenary company escapes across three drying islands, one site a day, with a colonel who
answers whatever you did yesterday.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import functools
import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, plural, run  # noqa: E402

ISLES = ["Hollin", "Brae", "Saltmarch"]
POS = ["North", "West", "East", "South"]
N = len(POS)            # sites on each island
TOTAL = len(ISLES) * N  # sites on the map
CAMP = 1                # Hollin West
HARBOR = 2 * N + 2      # Saltmarch East
KIND = {"march": "march", "sail": "sail", "question": "hide", "lie": "hide", "hire": "hide"}
KIND_WORD = {"march": "march", "sail": "sail"}
AGAIN = {"march": "march again", "sail": "sail again"}


def name(i):
    if i == CAMP:
        return "Hollin camp"
    if i == HARBOR:
        return "Saltmarch harbor"
    return f"{ISLES[i // N]} {POS[i % N]}"


@functools.lru_cache(maxsize=4096)  # lit-ok: cache size
def _winnable(g, key):
    sites, consts = key
    C = dict(consts)

    @functools.lru_cache(maxsize=None)
    def go(turn, at, done, m0, s0, ready, hands):
        if turn > C["DAYS"]:
            return False
        isl = at // N
        left = sum(1 for j in range(isl * N, TOTAL) if sites[j] == "village" and not (done >> j & 1))  # lit-ok
        if m0 + left * C["RECRUIT"] + (0 if hands else C["HANDS"]) < C["GOAL"]:
            return False
        moves = [("march", isl * N + j) for j in range(N) if isl * N + j != at]
        if isl < len(ISLES) - 1 and s0 >= 1:
            moves += [("sail", (isl + 1) * N + j) for j in range(N)]
        moves.append(("lie", None))
        if at == HARBOR and not hands:
            moves.append(("hire", None))
        for a, i in moves:
            m, st, d, h, pos = m0, s0, done, hands, at
            kind = KIND[a]
            if kind == ready:
                if a == "sail":
                    st -= min(C["GUN"], st)
                else:
                    m -= C["RIDERS"]
            if a == "sail":
                m = min(m, st)
            if m <= 0:
                continue
            if a in ("march", "sail"):
                pos = i
                if i not in (CAMP, HARBOR) and not (d >> i & 1):  # lit-ok: bit mask of taken sites
                    d |= 1 << i  # lit-ok
                    c = sites[i]
                    if c == "boats":
                        st += C["BOAT"]
                    elif c == "village":
                        m += C["RECRUIT"]
                    else:
                        m -= C["MIL_WIN_LOSS"]
                        st += C["MIL_SEATS"]
            if a == "hire":
                m += C["HANDS"]
                h = True
            if m <= 0:
                continue
            if pos == HARBOR and m >= C["GOAL"]:
                return True
            dry = [C["HOLLIN_DRY"], C["BRAE_DRY"], None][pos // N]
            if dry is not None and turn >= dry:
                m -= C["THIRST"]
                if m <= 0:
                    continue
            nxt = None if kind == "hide" or (kind == "sail" and pos // N == len(ISLES) - 1) else kind
            if go(turn + 1, pos, d, m, st, nxt, h):
                return True
        return False

    return go(1, CAMP, 1 << CAMP, C["START_MEN"], C["START_SEATS"], None, False)  # lit-ok


def men(n):
    return plural(n, "man", "men")


class G(Game):
    name = "Low Wells"

    CONSTANTS = {
        "DAYS": 12,
        "START_MEN": 16,
        "START_SEATS": 12,
        "BOAT": 6,
        "RECRUIT": 5,
        "DIE": 6,
        "FIGHT_NEED": 4,
        "FIGHT_SCOUTED": 3,
        "MIL_WIN_LOSS": 1,
        "MIL_SEATS": 4,
        "MIL_LOSS": 4,
        "RIDERS": 3,
        "GUN": 4,
        "HOLLIN_DRY": 4,
        "BRAE_DRY": 8,
        "THIRST": 2,
        "HANDS": 4,
        "GOAL": 32,
        "_BOATS": 3,
        "_VILLAGES": 4,
        "_MILITIA": 3,
        "_DEALS": 60,
    }

    RULES = """
1. You start at Hollin camp with {START_MEN} men and boats for {START_SEATS}. Each day, one move: march to another site on your island, sail to any site on the next island east (your boats go with you), question the fishermen, or lie low.
2. Sailing needs a seat per man; men without one are left on the beach for good. Every site except your camp and the harbor holds one thing, taken at your first visit: fishing boats (Seats +{BOAT}), a village (Men +{RECRUIT}), or militia.
3. Militia fight when you arrive: roll {FIGHT_NEED}+ on a d{DIE}, or {FIGHT_SCOUTED}+ if the fishermen told you they were there. Win: Men -{MIL_WIN_LOSS}, Seats +{MIL_SEATS} from their boats. Lose: Men -{MIL_LOSS}. Either way they leave.
4. Questioning the fishermen, from any site, shows what every site on your island and the next one holds. Questioning and lying low keep the company hidden: Vass never strikes them, and he loses your trail.
5. Colonel Vass reads your tracks. March the day after a march, or sail the day after a sail, and he lies in wait: riders ambush the march (Men -{RIDERS}); a gunboat sinks boats before the sail (Seats -{GUN}).
6. The water table is dropping: Hollin's wells are dry from day {HOLLIN_DRY}, Brae's from day {BRAE_DRY}. From that day's night on, every night on a dry island costs Men -{THIRST}, whatever your move. Saltmarch has a cistern.
7. Once, as your move at Saltmarch harbor, sign on dockhands from the town: Men +{HANDS}. Like lying low, Vass cannot strike it and loses your trail.
8. Your new mainland contract is for {GOAL} men. The Merrow waits at Saltmarch harbor until dusk of day {DAYS}; the moment the company stands there {GOAL} strong, it boards and you win. Every map is winnable if your fights go well.
"""

    ACTIONS = ["march", "sail", "question", "lie", "hire"]
    TAGS = ["boats", "village", "militia_win", "militia_loss", "left_behind", "riders", "gunboat", "thirst",
            "brae_dry", "hire", "board"]
    TRACKED = ["men", "seats"]

    BOUNDS = {"men": (0, 60), "seats": (0, 70)}
    REACH = {"men": "GOAL"}
    GATES = {
        "hire": {"!hands_used": 1, "_if": lambda g, s: s["at"] == HARBOR},
        "sail": {"seats": 1, "_if": lambda g, s: s["at"] // N < 2},
    }

    @property
    def turns(self):
        return self.C["DAYS"]

    # ------------------------------------------------------------ state

    def init_state(self, rng):
        C = self.C
        deck = ["boats"] * C["_BOATS"] + ["village"] * C["_VILLAGES"] + ["militia"] * C["_MILITIA"]
        sites = None
        for _ in range(C["_DEALS"]):  # deal again until the map can be won
            rng.shuffle(deck)
            pool = list(deck)
            sites = ["camp" if i == CAMP else "harbor" if i == HARBOR else pool.pop() for i in range(TOTAL)]
            if self.ceiling(sites) >= C["GOAL"] and self.winnable(sites):
                break
        known = [None] * TOTAL  # lit-ok
        known[CAMP] = "camp"
        known[HARBOR] = "harbor"
        done = [False] * TOTAL  # lit-ok
        done[CAMP] = True
        return {
            "men": C["START_MEN"],
            "seats": C["START_SEATS"],
            "at": CAMP,
            "known": known,
            "done": done,
            "last": None,
            "ready": [],
            "hands_used": False,
            "hidden": {"sites": sites},
        }

    def resample_hidden(self, s, rng):
        idx = [i for i in range(TOTAL) if s["known"][i] is None]  # lit-ok
        pool = [s["hidden"]["sites"][i] for i in idx]
        for _ in range(self.C["_DEALS"]):
            rng.shuffle(pool)
            trial = list(s["hidden"]["sites"])
            for i, c in zip(idx, pool):
                trial[i] = c
            if self.ceiling(trial) >= self.C["GOAL"] and self.winnable(trial):
                break
        s["hidden"]["sites"] = trial

    def winnable(self, sites):
        """True if a perfect player who wins every militia fight can stand at the harbor GOAL strong in time:
        every rule applied (Vass, thirst, seats, the clock). The deal uses it so every map can be won."""
        key = (tuple(sites), tuple(sorted((k, v) for k, v in self.C.items())))
        return _winnable(self, key)

    def ceiling(self, sites):
        """The most men a map can ever bring to the harbor: every militia beaten, no Vass, no thirst, no clock."""
        C = self.C
        states = {(C["START_MEN"], C["START_SEATS"])}
        for isl in range(len(ISLES)):
            spots = [sites[j] for j in range(isl * N, isl * N + N) if j not in (CAMP, HARBOR)]
            nxt = set()
            for m0, s0 in states:
                for mask in range(1 << len(spots)):  # lit-ok: every subset of the island's sites
                    m, st = m0, s0
                    for k, c in enumerate(spots):
                        if mask >> k & 1:  # lit-ok
                            if c == "boats":
                                st += C["BOAT"]
                            elif c == "village":
                                m += C["RECRUIT"]
                            else:
                                m -= C["MIL_WIN_LOSS"]
                                st += C["MIL_SEATS"]
                    if isl < len(ISLES) - 1:
                        m = min(m, st)
                    nxt.add((m, st))
            states = nxt
        return max(m for m, _ in states) + C["HANDS"]

    # ------------------------------------------------------------ helpers

    def info(self, s, i):
        C = self.C
        if i == CAMP:
            return "your old camp"
        if i == HARBOR:
            return "the harbor"
        k = s["known"][i]
        if k is None:
            return "unknown"
        if s["done"][i]:
            return "already searched"
        if k == "boats":
            if i // N == 2:
                return "fishing boats, no use on the last island"
            return f"fishing boats, Seats +{C['BOAT']}"
        if k == "village":
            return f"a village, Men +{C['RECRUIT']}"
        if i // N == 2:
            return f"militia, fight needs {C['FIGHT_SCOUTED']}+, their boats no use on the last island"
        return f"militia, fight needs {C['FIGHT_SCOUTED']}+"

    def unknown_near(self, s):
        isl = s["at"] // N
        rng_ = range(isl * N, min(TOTAL, isl * N + 2 * N))  # lit-ok: this island and the next
        return [i for i in rng_ if s["known"][i] is None]

    def warn(self, s, kind):
        C = self.C
        if kind not in s["ready"]:
            return ""
        if kind == "sail":
            return f"; Vass is ready: Seats -{C['GUN']}"
        return f"; Vass is ready: Men -{C['RIDERS']}"

    def dry_day(self, isl):
        return [self.C["HOLLIN_DRY"], self.C["BRAE_DRY"], None][isl]

    # ------------------------------------------------------------ options

    def options(self, s):
        C = self.C
        o = []
        at = s["at"]
        isl = at // N
        for j in range(N):  # lit-ok
            i = isl * N + j
            if i != at:
                o.append({"id": "march", "label": f"March to {name(i)} ({self.info(s, i)}){self.warn(s, 'march')}",
                          "args": {"site": i}, "group": f"March to another site on {ISLES[isl]}"})
        if isl < 2 and s["seats"] >= 1:
            after = max(0, s["seats"] - C["GUN"]) if "sail" in s["ready"] else s["seats"]
            left = max(0, s["men"] - after)
            note = f"; {men(left)} left on the beach" if left else ""
            for j in range(N):  # lit-ok
                i = (isl + 1) * N + j
                o.append({"id": "sail", "label": f"Sail to {name(i)} ({self.info(s, i)}){self.warn(s, 'sail')}{note}",
                          "args": {"site": i}, "group": f"Sail to {ISLES[isl + 1]}"})
        near = self.unknown_near(s)
        if near:
            isles = sorted({i // N for i in near})
            o.append({"id": "question", "label": f"Question the fishermen about {' and '.join(ISLES[k] for k in isles)}",
                      "args": {}})
        o.append({"id": "lie", "label": "Lie low in the hills for the day (Vass loses your trail)", "args": {}})
        if at == HARBOR and not s["hands_used"]:
            o.append({"id": "hire", "label": f"Sign on dockhands in the harbor town (Men +{C['HANDS']}, once; Vass loses your trail)",
                      "args": {}})
        return o

    # ------------------------------------------------------------ apply

    def arrive(self, s, i, rng):
        C = self.C
        ev = []
        if i == HARBOR:
            short = C["GOAL"] - s["men"]
            if short > 0:
                ev.append(f"The Merrow rides at anchor. Your mainland contract is for {C['GOAL']} men: you are {short} short.")
            return ev
        if i == CAMP:
            ev.append("Your old camp is empty.")
            return ev
        if s["done"][i]:
            ev.append(f"{name(i)} has nothing left to take.")
            return ev
        content = s["hidden"]["sites"][i]
        knew = s["known"][i] is not None
        s["known"][i] = content
        s["done"][i] = True
        if content == "boats":
            s["seats"] += C["BOAT"]
            self.hit("boats")
            ev.append(f"Fishing boats on the beach. Seats +{C['BOAT']}.")
        elif content == "village":
            s["men"] += C["RECRUIT"]
            self.hit("village")
            ev.append(f"Men from the village sign on for passage off the islands. Men +{C['RECRUIT']}.")
        else:
            need = C["FIGHT_SCOUTED"] if knew else C["FIGHT_NEED"]
            ok, txt = rng.check(need, C["DIE"])
            if ok:
                lost = self.lose(s, C["MIL_WIN_LOSS"])
                s["seats"] += C["MIL_SEATS"]
                self.hit("militia_win")
                ev.append(f"Militia hold {name(i)}. You attack: {txt}. They break and run. Men -{lost}, Seats +{C['MIL_SEATS']} from their boats.")
            else:
                lost = self.lose(s, C["MIL_LOSS"])
                self.hit("militia_loss")
                ev.append(f"Militia hold {name(i)}. You attack: {txt}. They hold the beach until dark, then slip away. Men -{lost}.")
        return ev

    def lose(self, s, n):
        """Take up to n men; never below zero. Returns how many were lost."""
        lost = min(n, s["men"])
        s["men"] -= lost
        return lost

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        kind = KIND[a]
        if kind in s["ready"]:
            if kind == "sail":
                lost = min(C["GUN"], s["seats"])
                s["seats"] -= lost
                self.hit("gunboat")
                ev.append(f"Vass's gunboat was waiting in the strait. Seats -{lost}.")
            else:
                lost = self.lose(s, C["RIDERS"])
                self.hit("riders")
                ev.append(f"Vass was ready for you: his riders hit the company. Men -{lost}.")
                if s["men"] <= 0:
                    self.finish(s, "loss", "Vass's riders destroyed the company")
                    return ev
        s["last"] = None if kind == "hide" else kind
        if a == "march":
            i = args["site"]
            s["at"] = i
            ev.append(f"The company marches to {name(i)}.")
            ev += self.arrive(s, i, rng)
        elif a == "sail":
            i = args["site"]
            if s["men"] > s["seats"]:
                left = s["men"] - s["seats"]
                s["men"] = s["seats"]
                self.hit("left_behind")
                ev.append(f"Not enough seats: {men(left)} left on the beach for good.")
                if s["men"] <= 0:
                    self.finish(s, "loss", "the whole company was left on the beach")
                    return ev
            s["at"] = i
            ev.append(f"The boats cross to {name(i)}.")
            ev += self.arrive(s, i, rng)
        elif a == "question":
            found = []
            for i in self.unknown_near(s):
                s["known"][i] = s["hidden"]["sites"][i]
                found.append(f"{name(i)}: {self.info(s, i)}")
            ev.append("The fishermen talk. " + "; ".join(found) + ".")
        elif a == "lie":
            ev.append("The company lies low in the hills. Vass's scouts lose the trail.")
        elif a == "hire":
            s["men"] += C["HANDS"]
            s["hands_used"] = True
            self.hit("hire")
            ev.append(f"Dockhands from the harbor town sign on for the mainland. Men +{C['HANDS']}.")
        if s["men"] <= 0:
            self.finish(s, "loss", "the company was destroyed")
        elif s["at"] == HARBOR and s["men"] >= C["GOAL"]:
            self.hit("board")
            ev.append(f"The company boards the Merrow, {men(s['men'])} strong.")
            self.finish(s, "win", f"the Merrow sailed with {men(s['men'])} aboard")
        return ev

    # ------------------------------------------------------------ dusk

    def advance(self, s, rng):
        C = self.C
        ev = []
        isl = s["at"] // N
        dry = self.dry_day(isl)
        if dry is not None and s["_turn"] >= dry:
            lost = self.lose(s, C["THIRST"])
            self.hit("thirst")
            ev.append(f"Dusk on {ISLES[isl]}: the wells are dry. Men -{lost} to thirst and desertion.")
            if s["men"] <= 0:
                self.finish(s, "loss", "thirst finished the company")
                return ev
        tomorrow = s["_turn"] + 1
        if tomorrow > C["DAYS"]:
            return ev
        if s["last"] == "sail" and isl == len(ISLES) - 1:
            s["last"] = None  # no sail is left to make, so there is nothing for him to wait for
        s["ready"] = [s["last"]] if s["last"] else []
        if s["last"]:
            ev.append(f"Vass's scouts read your tracks. Tomorrow he is ready if you {AGAIN[s['last']]}.")
        else:
            ev.append("Tomorrow Vass has no read on you.")
        if tomorrow == C["HOLLIN_DRY"] and isl == 0:
            ev.append("Hollin's wells give out tomorrow.")
        if tomorrow == C["BRAE_DRY"] and isl == 1:
            self.hit("brae_dry")
            ev.append("Brae's wells give out tomorrow.")
        return ev

    def status_line(self, s):
        r = s["ready"]
        vass = f"ready for {KIND_WORD[r[0]]}" if r else "no read on you"
        return f"Men {s['men']}/{self.C['GOAL']} | Seats {s['seats']} | At: {name(s['at'])} | Vass: {vass}"

    def check_end(self, s):
        if s["men"] <= 0:
            return {"result": "loss", "reason": "the company was destroyed"}
        return None

    def final_check(self, s):
        if s["at"] == HARBOR:
            return {"result": "loss", "reason": f"the Merrow sailed without you: {men(s['men'])} at the harbor, the contract needed {self.C['GOAL']}"}
        return {"result": "loss", "reason": f"the Merrow sailed without you; the company was still at {name(s['at'])}"}

    # ------------------------------------------------------------ heuristic

    def heuristic(self, s, options, rng):
        C = self.C
        ids = {o["id"] for o in options}
        turn = s["_turn"]
        at = s["at"]
        isl = at // N
        m, st = s["men"], s["seats"]
        ready = s["ready"]
        dry = self.dry_day(isl)
        days_left = C["DAYS"] - turn

        def untaken(k_isl):
            return [j for j in range(k_isl * N, k_isl * N + N) if not s["done"][j] and j not in (CAMP, HARBOR)]  # lit-ok

        def carry(k_isl):
            """Seats the company can count on at its next crossing from island k_isl."""
            extra = sum(C["BOAT"] for j in untaken(k_isl) if s["known"][j] == "boats")
            return st + extra

        def villages_ahead():
            return sum(1 for k_isl in (isl, isl + 1) if k_isl <= 2 for j in untaken(k_isl) if s["known"][j] == "village")

        def site_value(i):
            if i == HARBOR:
                if m >= C["GOAL"]:
                    return 8
                if not s["hands_used"] and m + C["HANDS"] >= C["GOAL"]:
                    return 6
                return 2 if days_left <= 1 else -0.5
            if s["done"][i] or i == CAMP:
                return -1
            k = s["known"][i]
            k_isl = i // N
            last = k_isl == 2
            if k is None:
                return 1.0 if last else 1.5
            if k == "boats":
                if last:
                    return -0.2
                return 3 if st < m + C["RECRUIT"] * max(1, villages_ahead()) else 0.8
            if k == "village":
                if last:
                    return 4.5
                room = max(0, carry(k_isl) - m)
                return 0.9 * min(C["RECRUIT"], room) + 0.3
            if last:
                return -1
            return 1.2 if st < m else 0.2

        worth_here = [j for j in untaken(isl) if j != at and site_value(j) >= 1.5]

        def score(o):
            a = o["id"]
            kind = KIND.get(a)
            v = 0.0
            if a == "march":
                v = site_value(o["args"]["site"])
            elif a == "sail":
                i = o["args"]["site"]
                v = site_value(i) + 0.5
                after = max(0, st - C["GUN"]) if "sail" in ready else st
                left = max(0, m - after)
                v -= 1.0 * left
                if not worth_here:
                    v += 2.5
                if dry is not None and turn >= dry:
                    v += 3
                if days_left <= 2 + (1 - isl):
                    v += 3
            elif a == "question":
                v = 2.6 if any(s["known"][j] is None for j in untaken(isl)) else 1.4
            elif a == "lie":
                v = 0.4 if ready and turn <= 3 else -0.6
            elif a == "hire":
                v = 7 if m < C["GOAL"] else 0.2
            if kind and kind in ready:
                v -= 3 if kind != "sail" else 1.5
            if a != "sail" and dry is not None and turn >= dry:
                v -= 1.5
            return v

        best = max(score(o) for o in options)
        top = [o for o in options if score(o) == best]
        return rng.choice(top)

    # ------------------------------------------------------------ rule tests

    def rule_tests(self):
        C = self.C
        # a fixed map: Hollin N, camp, E, S | Brae N, W, E, S | Saltmarch N, W, harbor, S
        S = ["village", "camp", "boats", "village", "militia", "boats", "village", "militia",
             "boats", "village", "harbor", "militia"]

        def r1(t):
            s = t.fresh()
            t.eq((s["men"], s["seats"], s["at"]), (C["START_MEN"], C["START_SEATS"], CAMP), "the start")
            t.eq(t.status(s), f"Men {C['START_MEN']}/{C['GOAL']} | Seats {C['START_SEATS']} | At: Hollin camp | Vass: no read on you", "status line")
            t.eq(set(t.ids(s)), {"march", "sail", "question", "lie"}, "the four moves on day 1")
            t.ok(all(t.offered(s, "march", site=i) for i in (0, 2, 3)), "march to any other Hollin site")  # lit-ok
            t.ok(not t.offered(s, "march", site=CAMP), "not to where you stand")
            t.ok(not t.offered(s, "march", site=4), "marching stays on the island")  # lit-ok
            t.ok(all(t.offered(s, "sail", site=i) for i in (4, 5, 6, 7)), "sail to any Brae site")  # lit-ok
            t.ok(not t.offered(s, "sail", site=8), "not past the next island")  # lit-ok
            s2, _ = t.step(s, "lie")
            t.eq(s2["_turn"], 2, "one move ends the day")
            s = t.fresh(at=HARBOR)
            t.ok("sail" not in t.ids(s), "no island east of Saltmarch")
            t.eq(t.label(t.fresh(), "march", site=0), "March to Hollin North (unknown)", "march label, unknown site")
            t.eq(t.label(t.fresh(), "sail", site=5), f"Sail to Brae West (unknown); {men(C['START_MEN'] - C['START_SEATS'])} left on the beach", "sail label")  # lit-ok
            s0 = t.fresh()
            t.eq(sorted(s0["hidden"]["sites"]), sorted(S), "the map holds 3 boats, 4 villages, 3 militia")

        def r2(t):
            s = t.fresh(men=20, seats=14, hidden__sites=S)
            t.ok(t.label(s, "sail", site=6).endswith("; 6 men left on the beach"), "the label warns who stays behind")  # lit-ok
            ev = t.apply(s, "sail", {"site": 6})  # lit-ok
            t.has(ev, "Not enough seats: 6 men left on the beach for good.")
            t.in_order(ev, ["left on the beach", "The boats cross to Brae East", "Men from the village"], "cause before effect")
            t.eq(s["men"], 14 + C["RECRUIT"], "only seated men cross; then the village joins")
            s = t.fresh(men=14, seats=14, hidden__sites=S)
            ev = t.apply(s, "sail", {"site": 6})  # lit-ok
            t.ok(not any("left on the beach" in e for e in ev), "exactly enough seats leaves nobody")
            t.eq(s["men"], 14 + C["RECRUIT"], "a full crossing")
            s = t.fresh(men=15, seats=10, hidden__sites=S)
            ev = t.apply(s, "march", {"site": 2})
            t.eq(s["seats"], 10 + C["BOAT"], "fishing boats add seats")
            t.has(ev, f"Fishing boats on the beach. Seats +{C['BOAT']}.")
            t.apply(s, "march", {"site": 0})
            t.eq(s["men"], 15 + C["RECRUIT"], "a village adds men")
            ev = t.apply(s, "march", {"site": 2})
            t.eq(s["seats"], 10 + C["BOAT"], "a site is taken once")
            t.has(ev, "Hollin East has nothing left to take.")
            t.eq(t.label(s, "march", site=0), "March to Hollin North (already searched)", "a taken site says so")
            t.eq(t.label(s, "march", site=CAMP), "March to Hollin camp (your old camp)", "the camp")
            s = t.fresh(at=9, hidden__sites=S, known=S)  # lit-ok
            t.eq(t.label(s, "march", site=8), "March to Saltmarch North (fishing boats, no use on the last island)", "boats past the last crossing say so")  # lit-ok
            s = t.fresh(men=1, seats=1)
            t.ok(t.offered(s, "sail", site=4), "one seat is enough to sail")  # lit-ok
            s = t.fresh(seats=0)
            t.ok("sail" not in t.ids(s), "no boats, no sailing")

        def r3(t):
            M = ["militia"] + S[1:]
            s = t.fresh(men=16, seats=10, hidden__sites=M)
            ev = t.apply(s, "march", {"site": 0}, dice=[C["FIGHT_NEED"]])
            t.has(ev, f"Militia hold Hollin North. You attack: roll {C['FIGHT_NEED']} (need {C['FIGHT_NEED']}+) success. They break and run.")
            t.eq((s["men"], s["seats"]), (16 - C["MIL_WIN_LOSS"], 10 + C["MIL_SEATS"]), "a won fight")
            s = t.fresh(men=16, seats=10, hidden__sites=M)
            ev = t.apply(s, "march", {"site": 0}, dice=[C["FIGHT_NEED"] - 1])
            t.has(ev, "fail. They hold the beach until dark, then slip away.")
            t.eq((s["men"], s["seats"]), (16 - C["MIL_LOSS"], 10), "a lost fight")
            t.ok(s["done"][0], "the militia are gone either way")
            s = t.fresh(men=16, seats=10, hidden__sites=M)
            t.apply(s, "question")
            t.eq(t.label(s, "march", site=0), f"March to Hollin North (militia, fight needs {C['FIGHT_SCOUTED']}+)", "odds in the label")
            ev = t.apply(s, "march", {"site": 0}, dice=[C["FIGHT_SCOUTED"]])
            t.has(ev, f"(need {C['FIGHT_SCOUTED']}+) success", "a fight you knew of is easier")
            s = t.fresh(men=16, seats=10, hidden__sites=M)
            t.apply(s, "question")
            t.apply(s, "march", {"site": 0}, dice=[C["FIGHT_SCOUTED"] - 1])
            t.eq(s["men"], 16 - C["MIL_LOSS"], "and still losable")
            s = t.fresh(men=10, seats=10, hidden__sites=S)
            ev = t.apply(s, "sail", {"site": 4}, dice=[C["FIGHT_NEED"] - 1])  # lit-ok: Brae North holds militia
            t.has(ev, f"(need {C['FIGHT_NEED']}+) fail", "landing on militia fights too")
            t.eq(s["men"], 10 - C["MIL_LOSS"], "a lost landing")
            s = t.fresh(men=10, seats=10, hidden__sites=S)
            t.apply(s, "question")
            ev = t.apply(s, "sail", {"site": 4}, dice=[C["FIGHT_SCOUTED"]])  # lit-ok
            t.has(ev, f"(need {C['FIGHT_SCOUTED']}+) success", "a scouted landing is easier too")
            s = t.fresh(men=C["MIL_LOSS"], seats=10, hidden__sites=M)
            t.apply(s, "march", {"site": 0}, dice=[1])
            t.ok(s["_ended"] and s["_ended"]["result"] == "loss", "a lost fight can wipe out the company")
            s = t.fresh(at=9, hidden__sites=S, known=S)  # lit-ok
            t.eq(t.label(s, "march", site=11), f"March to Saltmarch South (militia, fight needs {C['FIGHT_SCOUTED']}+, their boats no use on the last island)", "the last island's militia say so")  # lit-ok
            s = t.fresh(at=2, hidden__sites=S)
            ev = t.apply(s, "march", {"site": CAMP})
            t.eq((s["men"], s["seats"]), (C["START_MEN"], C["START_SEATS"]), "the camp holds nothing")
            t.has(ev, "Your old camp is empty.")

        def r4(t):
            s = t.fresh(hidden__sites=S)
            t.eq(t.label(s, "question"), "Question the fishermen about Hollin and Brae", "label")
            ev = t.apply(s, "question")
            t.eq(s["known"][:2 * N], S[:2 * N], "your island and the next")
            t.eq(s["known"][2 * N], None, "not two islands away")
            t.has(ev, f"Hollin South: a village, Men +{C['RECRUIT']}")
            t.has(ev, f"Brae North: militia, fight needs {C['FIGHT_SCOUTED']}+")
            s = t.fresh(hidden__sites=S, at=5)  # lit-ok
            t.eq(t.label(s, "question"), "Question the fishermen about Brae and Saltmarch", "from Brae")
            t.apply(s, "question")
            t.eq(s["known"][N:], S[N:], "Brae and Saltmarch")
            t.eq(s["known"][0], None, "not Hollin behind you")
            t.ok("question" not in t.ids(s), "nothing left to learn nearby")
            s = t.fresh(hidden__sites=S, at=8)  # lit-ok
            t.eq(t.label(s, "question"), "Question the fishermen about Saltmarch", "on the last island only it")
            t.apply(s, "question")
            t.eq((s["men"], s["seats"]), (C["START_MEN"], C["START_SEATS"]), "questioning is free")
            s = t.fresh(hidden__sites=S, ready=["march"], last="march")
            t.eq(t.label(s, "lie"), "Lie low in the hills for the day (Vass loses your trail)", "lie label, no warning")
            ev = t.apply(s, "lie")
            t.eq(s["men"], C["START_MEN"], "Vass cannot strike a hidden company, even when ready")
            t.has(ev, "The company lies low in the hills. Vass's scouts lose the trail.")
            t.eq(s["last"], None, "no move for him to read")
            ev = t.advance(s, turn=1)
            t.eq(s["ready"], [], "tomorrow he has no read")
            t.has(ev, "Tomorrow Vass has no read on you.")
            t.ok(t.status(s).endswith("Vass: no read on you"), "status")
            for kind_move, args in (("march", {"site": 2}), ("question", {}), ("lie", {})):
                s2 = t.copy(s)
                t.apply(s2, kind_move, args)
                t.eq(s2["men"], C["START_MEN"], f"{kind_move} is safe the day after lying low")
            s = t.fresh(hidden__sites=S, ready=["sail"], men=12, seats=12)
            t.apply(s, "lie")
            t.eq(s["seats"], 12, "lying low never costs boats")

        def r5(t):
            s = t.fresh(hidden__sites=S)
            t.apply(s, "march", {"site": 2})
            ev = t.advance(s, turn=1)
            t.eq(s["ready"], ["march"], "he reads a march")
            t.has(ev, "Tomorrow he is ready if you march again.")
            t.ok(t.status(s).endswith("Vass: ready for march"), "the status line shows it")
            t.ok(t.label(s, "march", site=0).endswith(f"; Vass is ready: Men -{C['RIDERS']}"), "the label warns")
            t.ok("Vass" not in t.label(s, "question"), "no warning on questioning")
            t.ok("Vass" not in t.label(s, "sail", site=4), "no warning on a sail")  # lit-ok
            s["_turn"] = 2
            m0 = s["men"]
            ev = t.apply(s, "march", {"site": 0})
            t.eq(s["men"], m0 - C["RIDERS"] + C["RECRUIT"], "a second march costs men")
            t.has(ev, f"Vass was ready for you: his riders hit the company. Men -{C['RIDERS']}.")
            t.in_order(ev, ["riders", "marches to Hollin North"], "the ambush comes first")
            s = t.fresh(hidden__sites=S, ready=["march"])
            m0 = s["men"]
            t.apply(s, "question")
            t.eq(s["men"], m0, "questioning is never struck")
            t.eq(s["last"], None, "questioning hides your trail")
            s = t.fresh(hidden__sites=S, ready=["march"], men=12, seats=14)
            t.apply(s, "sail", {"site": 5})  # lit-ok
            t.eq(s["seats"], 14 + C["BOAT"], "a sail the day after a march is safe")  # lit-ok
            s = t.fresh(hidden__sites=S, ready=["march"], men=2)
            ev = t.apply(s, "march", {"site": 2})
            t.eq(s["men"], 0, "never below zero")
            t.has(ev, "Men -2.")
            s = t.fresh(hidden__sites=S, ready=["sail"], seats=C["GUN"] + 2, men=C["GUN"] + 2, at=4)  # lit-ok
            t.apply(s, "sail", {"site": 8})  # lit-ok
            ev = t.advance(s, turn=3)  # lit-ok
            t.eq(s["ready"], [], "a sail onto the last island leaves him nothing to wait for")
            t.has(ev, "Tomorrow Vass has no read on you.")
            s = t.fresh(hidden__sites=S, ready=["sail"])
            t.apply(s, "march", {"site": 2})
            t.eq(s["men"], C["START_MEN"], "a different kind of move is safe")
            t.eq(s["last"], "march", "and becomes the move he reads")
            s = t.fresh(hidden__sites=S, ready=["march"])
            t.apply(s, "march", {"site": 2})
            t.eq(s["men"], C["START_MEN"] - C["RIDERS"], "march after march costs men")
            s = t.fresh(hidden__sites=S, ready=["sail"], men=12, seats=14)
            left = 12 - (14 - C["GUN"])
            t.ok(t.label(s, "sail", site=6).endswith(f"; Vass is ready: Seats -{C['GUN']}; {men(left)} left on the beach"), "the sail label counts the gunboat")  # lit-ok
            ev = t.apply(s, "sail", {"site": 6})  # lit-ok
            t.eq(s["seats"], 14 - C["GUN"], "the gunboat sinks seats")
            t.eq(s["men"], (14 - C["GUN"]) + C["RECRUIT"], "before the crossing: the extra men stay, then the village")
            t.in_order(ev, [f"Vass's gunboat was waiting in the strait. Seats -{C['GUN']}.", "left on the beach", "cross"], "gunboat first")
            s = t.fresh(hidden__sites=S, ready=["sail"], seats=C["GUN"] - 1)
            t.apply(s, "sail", {"site": 5})  # lit-ok
            t.eq(s["seats"], 0, "seats never go below zero")
            t.ok(s["_ended"] and s["_ended"]["reason"] == "the whole company was left on the beach", "nobody can cross")
            s = t.fresh(hidden__sites=S, ready=["march"], men=C["RIDERS"])
            t.apply(s, "march", {"site": 2})
            t.ok(s["_ended"] and s["_ended"]["reason"] == "Vass's riders destroyed the company", "riders can finish the company")
            s = t.fresh(hidden__sites=S, ready=["march"], men=C["RIDERS"] + 1)
            t.apply(s, "march", {"site": 2})
            t.ok(not s["_ended"], "one man left marches on")

        def r6(t):
            s = t.fresh()
            t.advance(s, turn=C["HOLLIN_DRY"] - 1)
            t.eq(s["men"], C["START_MEN"], "Hollin's wells hold before their day")
            ev = t.advance(s, turn=C["HOLLIN_DRY"])
            t.eq(s["men"], C["START_MEN"] - C["THIRST"], "a dusk on dry Hollin")
            t.has(ev, f"Dusk on Hollin: the wells are dry. Men -{C['THIRST']} to thirst and desertion.")
            s = t.fresh(at=5)  # lit-ok
            t.advance(s, turn=C["BRAE_DRY"] - 1)
            t.eq(s["men"], C["START_MEN"], "Brae holds before its day")
            ev = t.advance(s, turn=C["BRAE_DRY"])
            t.eq(s["men"], C["START_MEN"] - C["THIRST"], "Brae dry")
            t.has(ev, "Dusk on Brae: the wells are dry.")
            s = t.fresh(at=9)  # lit-ok
            t.advance(s, turn=C["DAYS"])
            t.eq(s["men"], C["START_MEN"], "Saltmarch never dries")
            s = t.fresh(last="march")
            ev = t.advance(s, turn=C["HOLLIN_DRY"] - 1)
            t.has(ev, "Hollin's wells give out tomorrow.")
            s = t.fresh(at=5, last="march")  # lit-ok
            ev = t.advance(s, turn=C["BRAE_DRY"] - 1)
            t.has(ev, "Brae's wells give out tomorrow.")
            s = t.fresh(at=9, last="march")  # lit-ok
            ev = t.advance(s, turn=C["BRAE_DRY"] - 1)
            t.ok(not any("wells" in e for e in ev), "no warning for an island left behind")
            s = t.fresh(at=5, last="march")  # lit-ok
            ev = t.advance(s, turn=C["HOLLIN_DRY"] - 1)
            t.ok(not any("Hollin" in e for e in ev), "no Hollin warning from Brae")
            s = t.fresh(men=C["THIRST"], last="march")
            ev = t.advance(s, turn=C["HOLLIN_DRY"])
            t.ok(s["_ended"] and s["_ended"]["reason"] == "thirst finished the company", "thirst can end it")
            t.ok(not any("Tomorrow" in e for e in ev), "no tell after the end")
            s = t.fresh(men=C["THIRST"] + 1, last="march")
            t.advance(s, turn=C["HOLLIN_DRY"])
            t.ok(not s["_ended"], "one man left still marches on")

        def r7(t):
            s = t.fresh(hidden__sites=S, at=9)  # lit-ok
            t.ok("hire" not in t.ids(s), "only at the harbor")
            s = t.fresh(hidden__sites=S, at=HARBOR, men=10)
            t.ok(t.offered(s, "hire"), "dockhands at the harbor")
            t.eq(t.label(s, "hire"), f"Sign on dockhands in the harbor town (Men +{C['HANDS']}, once; Vass loses your trail)", "label")
            ev = t.apply(s, "hire")
            t.eq(s["men"], 10 + C["HANDS"], "dockhands join")
            t.has(ev, f"Dockhands from the harbor town sign on for the mainland. Men +{C['HANDS']}.")
            t.eq(s["last"], None, "Vass loses your trail")
            t.ok("hire" not in t.ids(s), "once only")
            for r in (["march"], ["sail"]):
                s = t.fresh(hidden__sites=S, at=HARBOR, men=10, ready=r)
                t.apply(s, "hire")
                t.eq(s["men"], 10 + C["HANDS"], f"Vass cannot strike in the town (ready for {r[0]})")

        def r8(t):
            s = t.fresh(at=9, men=C["GOAL"], hidden__sites=S)  # lit-ok
            ev = t.apply(s, "march", {"site": HARBOR})
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "arriving at the harbor with the goal wins at once")
            t.eq(s["_ended"]["reason"], f"the Merrow sailed with {C['GOAL']} men aboard", "the reason")
            t.in_order(ev, ["The company marches to Saltmarch harbor.", f"The company boards the Merrow, {C['GOAL']} men strong."], "arrive, then board")
            s = t.fresh(men=C["GOAL"] + 5, seats=C["GOAL"] + 5, at=5, hidden__sites=S)  # lit-ok
            t.apply(s, "sail", {"site": HARBOR})
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "sailing straight into the harbor works too")
            s = t.fresh(at=9, men=C["GOAL"] - 2, hidden__sites=S)  # lit-ok
            ev = t.apply(s, "march", {"site": HARBOR})
            t.ok(not s["_ended"], "short of the goal, no boarding")
            t.has(ev, f"The Merrow rides at anchor. Your mainland contract is for {C['GOAL']} men: you are 2 short.")
            s = t.fresh(at=HARBOR, men=C["GOAL"] - C["HANDS"], hidden__sites=S)
            ev = t.apply(s, "hire")
            t.ok(s["_ended"] and s["_ended"]["result"] == "win", "the dockhands can bring the company up to strength")
            t.in_order(ev, ["Dockhands", "boards the Merrow"], "hire, then board")
            s = t.fresh(at=9, men=C["GOAL"])  # lit-ok
            t.ok(self.check_end(s) is None, "only at the harbor")
            s = t.fresh(at=HARBOR, men=C["GOAL"] - 1, last="march")
            s["_turn"] = C["DAYS"]
            t.ok(self.check_end(s) is None, "the last day is played")
            s2, ev = t.step(s, "march", {"site": 9})  # lit-ok
            t.ok(s2["_ended"]["result"] == "loss" and s2["_ended"]["phase"] == "budget", "she sails at dusk of the last day")
            t.eq(s2["_ended"]["reason"], "the Merrow sailed without you; the company was still at Saltmarch West", "the reason")
            t.ok(not any("Tomorrow" in e for e in ev), "no tell for a day that will not come")
            s = t.fresh(at=HARBOR, men=C["GOAL"] - 1, last="march")
            s["_turn"] = C["DAYS"]
            s2, ev = t.step(s, "lie")
            t.eq(s2["_ended"]["reason"], f"the Merrow sailed without you: {C['GOAL'] - 1} men at the harbor, the contract needed {C['GOAL']}", "short at the harbor")
            s = t.fresh(at=9, men=C["GOAL"], last="march", hidden__sites=S)  # lit-ok
            s["_turn"] = C["DAYS"]
            s2, ev = t.step(s, "march", {"site": HARBOR})
            t.ok(s2["_ended"]["result"] == "win", "reaching the harbor on the last day still makes it")
            t.eq(self.turns, C["DAYS"], "the budget")
            s = t.fresh(at=9, last="march", ready=[])  # lit-ok
            ev = t.advance(s, turn=C["DAYS"])
            t.eq(s["ready"], [], "no read for a day that will not come")
            s = t.fresh(at=9, last="march")  # lit-ok
            ev = t.advance(s, turn=C["DAYS"] - 1)
            t.eq(s["ready"], ["march"], "the last day still has a read")
            for seed in range(1, 41):
                sites = t.fresh(seed=seed)["hidden"]["sites"]
                t.ok(self.winnable(sites), f"seed {seed}: every map can be won")
            t.ok(not self.winnable(["village", "camp", "village", "village", "boats", "village", "militia", "militia", "boats", "militia", "harbor", "boats"]), "a Hollin of villages cannot be won")
            t.eq(self.ceiling(["village", "camp", "village", "village", "boats", "village", "militia", "militia", "boats", "militia", "harbor", "boats"]),
                 C["START_SEATS"] + C["RECRUIT"] + C["HANDS"], "a Hollin of villages caps the company at its seats")

        return [
            (1, "start and moves", r1), (2, "seats and sites", r2), (3, "militia", r3), (4, "questioning", r4),
            (5, "Vass", r5), (6, "wells", r6), (7, "dockhands", r7), (8, "the Merrow", r8),
        ]


if __name__ == "__main__":
    run(G)
