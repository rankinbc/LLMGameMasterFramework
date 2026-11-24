"""Audit of Reeds: a /play engine (v3 contract).

You are the Bureau of Sleep's siege engineer. A dreamer's river delta is being audited, and the Ferryman's barge is
carrying the dream's last secret down to the sea. Sound the reaches, drill your sappers, break each guard, and chart
the whole delta before the dream wakes.

Rulesheet: run `python engine.py rules`. It is built from CONSTANTS and RULES below.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, plural, run  # noqa: E402

HOUSES = ["Heron", "Eel", "Moth"]
SIDES = ["East", "West"]
PARENT = [-1, 0, 0, 1, 1, 2, 2]  # the delta: reach 1 is the Source, 2 and 3 the forks, 4 to 7 the mouths


def kids(i):
    """The reaches directly under reach i (0-based)."""
    return [j for j, p in enumerate(PARENT) if p == i]


def below(i):
    """Reach i and every reach under it."""
    out = [i]
    for k in kids(i):
        out += below(k)
    return out


def joined(idx):
    """'4', '4 and 5' or '2, 4 and 5' from 0-based reach indexes, shown 1-based."""
    names = [str(i + 1) for i in idx]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


class G(Game):
    name = "Audit of Reeds"

    CONSTANTS = {
        "REACHES": 7,
        "TURNS": 18,
        "DIE": 6,
        "START_SOUNDINGS": 4,
        "START_DRILL": 0,
        "SOUND_GAIN": 2,
        "SOUND_LATE": 1,
        "SOUND_REPEAT": 1,
        "TRAIN_COST": 2,
        "DRILL_MAX": 3,
        "DRILL_LOSS": 1,
        "PUSH_MAX": 3,
        "GUARD_LO": 4,
        "GUARD_HI": 7,
        "CHART_PAY": 1,
        "PACE": 6,
        "WARD": 3,
        "EASE": 1,
        "FRIEND_NOTE": 1,
        "STIR_TURN": 10,
        "STIR": 1,
        "BREACH_COST": 2,
        "BREACH_MIN": 2,
        "WRIT_TURN": 13,
        "WRIT_COST": 5,
    }

    RULES = """
1. Chart all {REACHES} reaches within {TURNS} turns or the dream wakes. Reach 1 is the Source; forks 2 (East) and 3 (West) carry mouths 4 and 5, and 6 and 7. A fork and its mouths form a branch.
2. Sound any reach to learn its guard (a base of {GUARD_LO} to {GUARD_HI}) and gain Soundings +{SOUND_GAIN} (only +{SOUND_LATE} from turn {STIR_TURN}), or +{SOUND_REPEAT} if you know the guard already. You start with Soundings {START_SOUNDINGS} and Drill {START_DRILL}.
3. Train the sappers for {TRAIN_COST} soundings: Drill rises one level, up to Drill {DRILL_MAX}. Each reach you chart, by any means, pays Soundings +{CHART_PAY}.
4. Deploy the sappers at an uncharted reach, pushing up to {PUSH_MAX} soundings. Roll d{DIE} plus Drill plus push: meeting its guard charts it. Win or lose, the push is spent and the guard learned; a failure costs {DRILL_LOSS} Drill.
5. The Ferryman's barge starts at reach 1. At dusk every {PACE} turns it drops to the less charted branch, then the less charted mouth under its fork (ties go low). An uncharted reach it holds has guard +{WARD}.
6. Three houses hold the reaches: Heron, Eel and Moth. One is secretly your friend: its reaches have guard -{EASE} and pay +{FRIEND_NOTE} when sounded. You learn which when you act at its reaches, or rule out the other two.
7. From turn {STIR_TURN} the dream stirs: guards +{STIR}. Once, breach a branch with {BREACH_MIN} or more uncharted reaches for {BREACH_COST} soundings: one pushed roll against their highest guard, all shown, charts them all (failure costs Drill and the breach).
8. From turn {WRIT_TURN}, once, spend {WRIT_COST} soundings on the Bureau's writ to chart any one reach with no roll.
"""

    ACTIONS = ["sound", "train", "deploy", "breach", "writ"]
    TAGS = [
        "friend", "elimination", "ward", "stir", "writ_ready", "fork_east", "fork_west", "mouth",
        "breach", "writ", "drill_max", "drill_lost",
    ]
    TRACKED = ["soundings", "drill", "charted"]
    BOUNDS = {"soundings": (0, 80), "drill": (0, 3), "barge": (0, 6), "charted_n": (0, 7)}
    REACH = {"charted_n": 7, "drill": 3, "barge": 3, "soundings": 5}
    DERIVED = {"charted_n": lambda g, s: sum(1 for c in s["charted"] if c)}
    GATES = {
        "train": {"soundings": "TRAIN_COST", "_if": lambda g, s: s["drill"] < g.C["DRILL_MAX"]},
        "deploy": {"_if": lambda g, s: not all(s["charted"])},
        "breach": {
            "soundings": "BREACH_COST", "_turn": "STIR_TURN", "!breach_used": 1,
            "_if": lambda g, s: any(sum(1 for m in below(f) if not s["charted"][m]) >= g.C["BREACH_MIN"] for f in kids(0)),
        },
        "writ": {"soundings": "WRIT_COST", "_turn": "WRIT_TURN", "!writ_used": 1},
    }

    @property
    def turns(self):
        return self.C["TURNS"]

    # ------------------------------------------------------------------ helpers

    def eff(self, s, i):
        """The guard of reach i right now: base, plus the stir, plus the barge's ward (an uncharted reach only), minus the friend's ease."""
        C = self.C
        g = s["hidden"]["guard"][i]
        if s["_turn"] >= C["STIR_TURN"]:
            g += C["STIR"]
        if s["barge"] == i and not s["charted"][i]:
            g += C["WARD"]
        if s["houses"][i] == s["hidden"]["friend"]:
            g -= C["EASE"]
        return g

    def shown(self, s, i):
        """The guard the player knows, or None."""
        return self.eff(s, i) if s["known"][i] else None

    def p_win(self, need):
        """Chance that one die meets `need`."""
        d = self.C["DIE"]
        return max(0.0, min(1.0, (d - need + 1) / d))

    def roll_word(self, need, top):
        """What the player needs on the die before any push; top is the most they can push."""
        if need <= 1:
            return "any roll wins"
        if need - top > self.C["DIE"]:
            return "no roll can win"
        if need > self.C["DIE"]:
            return "no roll wins without a push"
        return f"roll {need}+ before any push"

    def roll(self, rng, need):
        """One die against `need`. A need of 1 or less is a sure thing and reads 1+."""
        return rng.check(max(1, need), self.C["DIE"])

    def tag(self, s, i):
        return HOUSES[s["houses"][i]] + (", barge here" if s["barge"] == i else "")

    def meet(self, s, i):
        """Contact with reach i: the friend shows itself, or its house is ruled out."""
        ev = []
        h = s["houses"][i]
        if s["friend"] != -1 or h in s["cleared"]:
            return ev
        if h == s["hidden"]["friend"]:
            s["friend"] = h
            self.hit("friend")
            ev.append(f"The {HOUSES[h]} keepers slip you a note: House {HOUSES[h]} is on your side.")
            return ev
        s["cleared"].append(h)
        ev.append(f"The {HOUSES[h]} keepers give you nothing: House {HOUSES[h]} is not your friend.")
        if len(s["cleared"]) == len(HOUSES) - 1:
            rest = [x for x in range(len(HOUSES)) if x not in s["cleared"]][0]
            s["friend"] = rest
            self.hit("elimination")
            ev.append(f"That leaves House {HOUSES[rest]}: it is on your side.")
        return ev

    def chart(self, s, idx):
        """Chart the reaches in idx. Each pays CHART_PAY soundings. Returns the pay."""
        for m in idx:
            s["charted"][m] = True
            s["known"][m] = True
        pay = self.C["CHART_PAY"] * len(idx)
        s["soundings"] += pay
        return pay

    def spent(self, s, cost):
        s["soundings"] -= cost

    def fail(self, s, ev, txt):
        """The sappers are driven off."""
        before = s["drill"]
        s["drill"] = max(0, s["drill"] - self.C["DRILL_LOSS"])
        if s["drill"] < before:
            self.hit("drill_lost")
            ev.append(f"{txt}. The sappers are driven off and Drill falls to {s['drill']}.")
        else:
            ev.append(f"{txt}. The sappers are driven off.")

    # ------------------------------------------------------------------ the contract

    def init_state(self, rng):
        C = self.C
        n = C["REACHES"]
        big = rng.d(len(HOUSES)) - 1
        houses = [(i + big) % len(HOUSES) for i in range(n)]
        rng.shuffle(houses)
        span = C["GUARD_HI"] - C["GUARD_LO"] + 1
        guard = [C["GUARD_LO"] + rng.d(span) - 1 for _ in range(n)]
        friend = rng.choice(list(range(len(HOUSES))))
        return {
            "soundings": C["START_SOUNDINGS"],
            "drill": C["START_DRILL"],
            "charted": [False] * n,
            "known": [False] * n,
            "houses": houses,
            "barge": 0,
            "friend": -1,
            "cleared": [],
            "writ_used": False,
            "breach_used": False,
            "hidden": {"guard": guard, "friend": friend},
        }

    def resample_hidden(self, s, rng):
        """Guards the player has not learned, and the friend if it has not shown itself, are redrawn."""
        C = self.C
        span = C["GUARD_HI"] - C["GUARD_LO"] + 1
        for i in range(C["REACHES"]):
            if not s["known"][i]:
                s["hidden"]["guard"][i] = C["GUARD_LO"] + rng.d(span) - 1
        if s["friend"] == -1:
            pool = [h for h in range(len(HOUSES)) if h not in s["cleared"]]
            s["hidden"]["friend"] = rng.choice(pool)

    def options(self, s):
        C = self.C
        o = []
        late = s["_turn"] >= C["STIR_TURN"]
        for i in range(C["REACHES"]):
            if s["known"][i]:
                gain = C["SOUND_REPEAT"]
                info = f"{self.tag(s, i)}, guard {self.shown(s, i)}"
            else:
                gain = C["SOUND_LATE"] if late else C["SOUND_GAIN"]
                info = f"{self.tag(s, i)}, guard unknown"
            maybe = ""
            if s["friend"] == s["houses"][i]:
                gain += C["FRIEND_NOTE"]
            elif s["friend"] == -1 and s["houses"][i] not in s["cleared"]:
                maybe = f" (+{C['FRIEND_NOTE']} more if House {HOUSES[s['houses'][i]]} is your friend)"
            o.append({
                "id": "sound", "label": f"Sound reach {i + 1} ({info}): +{plural(gain, 'sounding')}{maybe}",
                "args": {"reach": i + 1}, "group": "Sound a reach",
            })
        if s["drill"] < C["DRILL_MAX"] and s["soundings"] >= C["TRAIN_COST"]:
            o.append({
                "id": "train", "label": f"Train the sappers: Drill {s['drill']} to {s['drill'] + 1} (-{plural(C['TRAIN_COST'], 'sounding')})",
                "args": {},
            })
        top = min(C["PUSH_MAX"], s["soundings"])
        for i in range(C["REACHES"]):
            if s["charted"][i]:
                continue
            g = self.shown(s, i)
            if g is None:
                info = f"{self.tag(s, i)}, guard unknown)"
            else:
                info = f"{self.tag(s, i)}, guard {g}): {self.roll_word(g - s['drill'], top)}"
            o.append({
                "id": "deploy", "label": f"Deploy the sappers at reach {i + 1} ({info}",
                "args": {"reach": i + 1}, "group": "Deploy the sappers",
                "params": {"push": {"min": 0, "max": top}},
            })
        if late and not s["breach_used"]:
            for f in kids(0):
                rest = [m for m in below(f) if not s["charted"][m]]
                if len(rest) < C["BREACH_MIN"] or s["soundings"] < C["BREACH_COST"]:
                    continue
                known = [self.shown(s, m) for m in rest]
                if None in known:
                    info = "highest guard unknown"
                else:
                    info = f"highest guard {max(known)}"
                o.append({
                    "id": "breach",
                    "label": f"Breach the {SIDES[f - 1]} branch (reaches {joined(rest)}; {info}; -{plural(C['BREACH_COST'], 'sounding')})",
                    "args": {"fork": f + 1}, "group": "Breach a branch",
                    "params": {"push": {"min": 0, "max": min(C["PUSH_MAX"], s["soundings"] - C["BREACH_COST"])}},
                })
        if s["_turn"] >= C["WRIT_TURN"] and not s["writ_used"] and s["soundings"] >= C["WRIT_COST"]:
            for i in range(C["REACHES"]):
                if not s["charted"][i]:
                    o.append({
                        "id": "writ",
                        "label": f"Spend the writ on reach {i + 1} ({self.tag(s, i)}): charted with no roll (-{plural(C['WRIT_COST'], 'sounding')})",
                        "args": {"reach": i + 1}, "group": "Use the writ",
                    })
        return o

    def apply(self, s, a, args, rng):
        C = self.C
        ev = []
        if a == "sound":
            i = int(args["reach"]) - 1
            house = HOUSES[s["houses"][i]]
            fresh = not s["known"][i]
            if fresh:
                gain = C["SOUND_LATE"] if s["_turn"] >= C["STIR_TURN"] else C["SOUND_GAIN"]
            else:
                gain = C["SOUND_REPEAT"]
            ev += self.meet(s, i)
            s["known"][i] = True
            again = "" if fresh else " again"
            ev.append(f"You sound reach {i + 1} ({house}){again}: guard {self.eff(s, i)}.")
            if s["houses"][i] == s["hidden"]["friend"]:
                gain += C["FRIEND_NOTE"]
                ev.append(f"Soundings +{gain} ({C['FRIEND_NOTE']} from the {house} keepers).")
            else:
                ev.append(f"Soundings +{gain}.")
            s["soundings"] += gain
        elif a == "train":
            self.spent(s, C["TRAIN_COST"])
            s["drill"] += 1
            if s["drill"] == C["DRILL_MAX"]:
                self.hit("drill_max")
            ev.append(f"The sappers drill through the night. Drill is now {s['drill']}.")
        elif a == "deploy":
            i, push = int(args["reach"]) - 1, args["push"]
            self.spent(s, push)
            ev += self.meet(s, i)
            s["known"][i] = True
            g = self.eff(s, i)
            if s["barge"] == i:
                self.hit("ward")
            ev.append(f"The sappers go in at reach {i + 1} ({self.tag(s, i)}): guard {g}, Drill {s['drill']}, push {push}.")
            ok, txt = self.roll(rng, g - s["drill"] - push)
            if ok:
                pay = self.chart(s, [i])
                ev.append(f"{txt}. Reach {i + 1} is charted: Soundings +{pay}.")
            else:
                self.fail(s, ev, txt)
        elif a == "breach":
            f, push = int(args["fork"]) - 1, args["push"]
            s["breach_used"] = True
            self.hit("breach")
            self.spent(s, C["BREACH_COST"] + push)
            rest = [m for m in below(f) if not s["charted"][m]]
            for m in rest:
                ev += self.meet(s, m)
                s["known"][m] = True
            g = max(self.eff(s, m) for m in rest)
            ev.append(
                f"The sappers burrow under the {SIDES[f - 1]} branch (reaches {joined(rest)}): "
                f"highest guard {g}, Drill {s['drill']}, push {push}."
            )
            ok, txt = self.roll(rng, g - s["drill"] - push)
            if ok:
                pay = self.chart(s, rest)
                ev.append(f"{txt}. Reaches {joined(rest)} are charted: Soundings +{pay}.")
            else:
                self.fail(s, ev, txt)
        elif a == "writ":
            i = int(args["reach"]) - 1
            self.hit("writ")
            self.spent(s, C["WRIT_COST"])
            s["writ_used"] = True
            ev += self.meet(s, i)
            pay = self.chart(s, [i])
            ev.append(f"The writ opens reach {i + 1} ({HOUSES[s['houses'][i]]}): charted, no roll. Soundings +{pay}.")
        return ev

    def advance(self, s, rng):
        C = self.C
        ev = []
        t = s["_turn"]
        if t + 1 == C["STIR_TURN"]:
            self.hit("stir")
            ev.append(
                f"The dream stirs. From turn {C['STIR_TURN']} every guard is {C['STIR']} higher, "
                f"a first sounding pays only {C['SOUND_LATE']}, and the sappers may breach a branch, once."
            )
        if t + 1 == C["WRIT_TURN"]:
            self.hit("writ_ready")
            ev.append("A courier from the Bureau arrives. The writ is yours to spend, once.")
        low = kids(s["barge"])
        if low and t % C["PACE"] == 0:
            counts = [len([m for m in below(k) if s["charted"][m]]) for k in low]
            pick = counts.index(min(counts))
            s["barge"] = low[pick]
            n = s["barge"] + 1
            level = counts.count(min(counts)) > 1
            if PARENT[s["barge"]] == 0:
                self.hit("fork_east" if s["barge"] == kids(0)[0] else "fork_west")
                where = SIDES[s["barge"] - 1]
                if level:
                    ev.append(f"At dusk the barge drops to reach {n}: the branches stand level, so it keeps to the {where}.")
                else:
                    ev.append(f"At dusk the barge drops to reach {n} and takes the {where} branch, the one you have charted less.")
            else:
                self.hit("mouth")
                if level:
                    ev.append(f"At dusk the barge drops to reach {n}: the mouths stand level, so it takes the lower.")
                else:
                    ev.append(f"At dusk the barge drops to reach {n}, the mouth you have not charted.")
        n = s["barge"] + 1
        if t >= C["TURNS"]:
            return ev
        if kids(s["barge"]):
            ev.append(f"The barge lies at reach {n} and will drop after turn {t + C['PACE'] - t % C['PACE']}.")
        else:
            ev.append(f"The barge lies at reach {n} and will slip out to sea after turn {C['TURNS']}.")
        return ev

    def status_line(self, s):
        n = sum(1 for c in s["charted"] if c)
        return f"Soundings {s['soundings']} | Drill {s['drill']} | Charted {n}/{self.C['REACHES']} | Barge {s['barge'] + 1}"

    def visible(self, s):
        return {
            "soundings": s["soundings"],
            "drill": s["drill"],
            "reaches": [
                {
                    "reach": i + 1, "house": HOUSES[s["houses"][i]], "charted": s["charted"][i],
                    "guard": self.shown(s, i), "barge": s["barge"] == i,
                }
                for i in range(self.C["REACHES"])
            ],
            "barge_reach": s["barge"] + 1,
            "barge_drops_after_turn": (s["_turn"] + (-s["_turn"]) % self.C["PACE"]) if kids(s["barge"]) else None,
            "friend": HOUSES[s["friend"]] if s["friend"] != -1 else None,
            "not_friends": [HOUSES[h] for h in range(len(HOUSES)) if h != s["friend"]] if s["friend"] != -1 else [HOUSES[h] for h in s["cleared"]],
            "writ_used": s["writ_used"],
            "breach_used": s["breach_used"],
        }

    def check_end(self, s):
        if all(s["charted"]):
            return {"result": "win", "reason": f"all {self.C['REACHES']} reaches are charted and the dream's secret is out"}
        return None

    def final_check(self, s):
        left = sum(1 for c in s["charted"] if not c)
        return {"result": "loss", "reason": f"the barge slipped out to sea and the dream woke with {plural(left, 'reach')} uncharted"}

    def heuristic(self, s, options, rng):
        C = self.C
        R = C["REACHES"]
        unch = [i for i in range(R) if not s["charted"][i]]
        left = self.turns - s["_turn"] + 1
        pressed = left <= len(unch) + 1
        mid = (C["GUARD_LO"] + C["GUARD_HI"]) / 2
        ids = {o["id"] for o in options}

        def est(i):
            g = self.shown(s, i)
            if g is not None:
                return g
            g = mid
            if s["_turn"] >= C["STIR_TURN"]:
                g += C["STIR"]
            if s["barge"] == i:
                g += C["WARD"]
            if s["houses"][i] == s["friend"]:
                g -= C["EASE"]
            return g

        def best_push(g, cap):
            for p in range(cap + 1):
                if self.p_win(g - s["drill"] - p) >= 0.75:
                    return p
            return cap

        if "writ" in ids:
            tgt = max(unch, key=est)
            cap = min(C["PUSH_MAX"], s["soundings"])
            if pressed or self.p_win(est(tgt) - s["drill"] - cap) < 0.6:
                return {"id": "writ", "args": {"reach": tgt + 1}}
        best = None
        for o in options:
            if o["id"] != "breach":
                continue
            rest = [m for m in below(o["args"]["fork"] - 1) if not s["charted"][m]]
            g = max(est(m) for m in rest)
            cap = o["params"]["push"]["max"]
            push = best_push(g, cap)
            p = self.p_win(g - s["drill"] - push)
            if p >= 0.6 and (best is None or len(rest) * p > best[0]):
                best = (len(rest) * p, {"id": "breach", "args": {"fork": o["args"]["fork"], "push": push}})
        if best:
            return best[1]
        pick = None
        for o in options:
            if o["id"] != "deploy":
                continue
            i = o["args"]["reach"] - 1
            if not s["known"][i] and not pressed:
                continue
            g = est(i)
            push = best_push(g, o["params"]["push"]["max"])
            p = self.p_win(g - s["drill"] - push)
            if pick is None or p > pick[0]:
                pick = (p, {"id": "deploy", "args": {"reach": i + 1, "push": push}})
        if pick and (pick[0] >= 0.65 or pressed):
            return pick[1]
        if "train" in ids and left > len(unch) + 3:
            return "train"
        for want in (lambda i: not s["known"][i] and not s["charted"][i], lambda i: not s["known"][i], lambda i: not s["charted"][i]):
            for i in range(R):
                if want(i):
                    return {"id": "sound", "args": {"reach": i + 1}}
        return {"id": "sound", "args": {"reach": 1}}

    def rule_tests(self):
        """One test per rule line, written from the sheet's sentences."""
        C = self.C
        R = C["REACHES"]

        def st(t, **over):
            """A calm test state: houses Heron Eel Moth Heron Eel Moth Heron, every base guard 5, Moth is the friend."""
            base = {"houses": [0, 1, 2, 0, 1, 2, 0], "hidden__guard": [5] * R, "hidden__friend": 2, "soundings": 10}
            base.update(over)
            return t.fresh(**base)

        def r1(t):
            t.eq(len(PARENT), R, "one parent per reach")
            t.eq(kids(0), [1, 2], "the Source feeds the two forks")
            t.eq(kids(1), [3, 4], "reaches 4 and 5 lie under 2")
            t.eq(kids(2), [5, 6], "reaches 6 and 7 lie under 3")
            t.eq(kids(3), [], "a mouth has nothing under it")
            t.eq(below(1), [1, 3, 4], "the East fork and its mouths")
            t.eq(below(2), [2, 5, 6], "the West fork and its mouths")
            t.eq(len(below(0)), R, "every reach lies under the Source")
            t.eq(joined([0]), "1", "one reach")
            t.eq(joined([3, 4]), "4 and 5", "two reaches")
            t.eq(joined([1, 3, 4]), "2, 4 and 5", "three reaches")
            t.eq(self.turns, C["TURNS"], "the budget is TURNS")
            s0 = t.fresh()
            t.eq(s0["charted"], [False] * R, "nothing is charted at the start")
            t.eq(s0["known"], [False] * R, "no guard is known at the start")
            t.eq(t.status(s0), f"Soundings {C['START_SOUNDINGS']} | Drill {C['START_DRILL']} | Charted 0/{R} | Barge 1", "the status line")
            t.eq(self.check_end(s0), None, "a fresh game is live")
            s = t.fresh(charted=[True] * R)
            end = self.check_end(s)
            t.ok(end and end["result"] == "win", "every reach charted is a win")
            t.has([end["reason"]], f"all {R} reaches are charted", "the win reason")
            t.eq(t.status(s), f"Soundings {C['START_SOUNDINGS']} | Drill {C['START_DRILL']} | Charted {R}/{R} | Barge 1", "the count of charted reaches")
            s = t.fresh(charted=[True] * (R - 1) + [False])
            t.eq(self.check_end(s), None, "one reach short is not a win")
            s["_turn"] = C["TURNS"]
            t.eq(self.check_end(s), None, "the last turn is still played")
            end = self.final_check(s)
            t.ok(end["result"] == "loss" and "dream woke with 1 reach uncharted" in end["reason"], "one reach short at dawn is a loss")
            s = t.fresh(charted=[True] * (R - 2) + [False] * 2)
            t.has([self.final_check(s)["reason"]], "dream woke with 2 reaches uncharted", "two reaches short")
            s = st(t, charted=[False] * R)
            s["_turn"] = C["TURNS"]
            s, _ = t.step(s, "sound", {"reach": 1})
            t.ok(s["_ended"] and s["_ended"]["phase"] == "budget" and s["_turn"] == C["TURNS"] + 1, "the budget ends the game after the last dusk")
            t.eq(s["_ended"]["result"], "loss", "an unfinished delta is a loss")
            s = st(t, charted=[True] * 3 + [False] + [True] * 3, drill=C["DRILL_MAX"], soundings=C["PUSH_MAX"], barge=0)
            s["_turn"] = C["TURNS"]
            s["hidden"]["guard"][3] = C["GUARD_LO"]
            s, _ = t.step(s, "deploy", {"reach": 4, "push": C["PUSH_MAX"]})
            t.ok(s["_ended"] and s["_ended"]["result"] == "win" and s["_ended"]["phase"] == "action", "charting the last reach on the last turn wins")
            houses_seen, guards_seen, friends, bigs = set(), set(), set(), set()
            for sd in range(1, 80):
                s = t.fresh(seed=sd)
                t.eq(sorted(s["houses"].count(h) for h in range(len(HOUSES))), [R // len(HOUSES), R // len(HOUSES), R // len(HOUSES) + 1], "three houses hold 3, 2 and 2 reaches")
                guards_seen.update(s["hidden"]["guard"])
                friends.add(s["hidden"]["friend"])
                houses_seen.add(tuple(s["houses"]))
                bigs.add(max(range(len(HOUSES)), key=lambda h: s["houses"].count(h)))
                t.eq((s["friend"], s["cleared"], s["barge"], s["writ_used"]), (-1, [], 0, False), "nobody is known yet")
            t.eq(guards_seen, set(range(C["GUARD_LO"], C["GUARD_HI"] + 1)), "guards run from GUARD_LO to GUARD_HI")
            t.eq(friends, set(range(len(HOUSES))), "any house can be the friend")
            t.eq(bigs, set(range(len(HOUSES))), "any house can hold the three reaches")
            s = self.init_state(t.rng(dice=[2, 1, 2, 3, 4, 1, 2, 3]))
            t.eq([s["houses"].count(h) for h in range(len(HOUSES))], [2, 3, 2], "a draw of 2 gives House Eel the three reaches")
            s = self.init_state(t.rng(dice=[3, 1, 2, 3, 4, 1, 2, 3]))
            t.eq([s["houses"].count(h) for h in range(len(HOUSES))], [2, 2, 3], "a draw of 3 gives House Moth the three reaches")
            s = self.init_state(t.rng(dice=[1, 1, 2, 3, 4, 1, 2, 3]))
            t.eq([s["houses"].count(h) for h in range(len(HOUSES))], [3, 2, 2], "a draw of 1 gives House Heron the three reaches")
            g = C["GUARD_LO"]
            t.eq(s["hidden"]["guard"], [g, g + 1, g + 2, g + 3, g, g + 1, g + 2], "each guard is GUARD_LO plus a die minus one")
            t.ok(len(houses_seen) > 10, "the layout changes with the seed")
            s = st(t, charted=[True, True, False, True, True, False, False], soundings=10, drill=C["DRILL_MAX"], hidden__guard=[1] * R)
            s["_turn"] = C["TURNS"]
            s, _ = t.step(s, "breach", {"fork": 3, "push": 0})
            t.ok(s["_ended"] and s["_ended"]["result"] == "win" and s["_ended"]["phase"] == "action", "a breach that charts the last reaches on the last turn wins")
            s = st(t, charted=[True] * 3 + [False] + [True] * 3, soundings=C["WRIT_COST"])
            s["_turn"] = C["TURNS"]
            s, _ = t.step(s, "writ", {"reach": 4})
            t.ok(s["_ended"] and s["_ended"]["result"] == "win" and s["_ended"]["phase"] == "action", "a writ that charts the last reach on the last turn wins")
            v = self.visible(st(t, known=[False] * 3 + [True] + [False] * 3))
            t.eq(v["reaches"][3], {"reach": 4, "house": "Heron", "charted": False, "guard": 5, "barge": False}, "the board shows a known guard")
            t.eq(v["reaches"][4]["guard"], None, "an unknown guard is not shown")
            t.eq((v["friend"], v["not_friends"], "hidden" in v), (None, [], False), "the friend and the hidden section stay hidden")
            for turn, due in ((1, C["PACE"]), (C["PACE"], C["PACE"]), (C["PACE"] + 1, 2 * C["PACE"])):
                t.eq(self.visible(st(t, _turn=turn))["barge_drops_after_turn"], due, f"the barge's next drop seen on turn {turn}")
            for turn in range(C["PACE"] + 1, 2 * C["PACE"] + 1):
                t.eq(self.visible(st(t, _turn=turn, barge=1))["barge_drops_after_turn"], 2 * C["PACE"], f"the fork's drop seen on turn {turn}")
            t.eq(self.visible(st(t, barge=3, _turn=2 * C["PACE"] + 1))["barge_drops_after_turn"], None, "a barge at a mouth has no drop left")
            t.eq(self.visible(st(t, barge=2))["barge_reach"], 3, "the barge's reach is shown from 1")

        def r2(t):
            s = st(t, soundings=0)
            ev = t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_GAIN"], "a fresh sounding pays SOUND_GAIN")
            t.ok(s["known"][3], "sounding teaches the guard")
            t.has(ev, "You sound reach 4 (Heron): guard 5.", "the sounding teaches the guard")
            t.has(ev, f"Soundings +{C['SOUND_GAIN']}.", "the gain is stated")
            ev = t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_GAIN"] + C["SOUND_REPEAT"], "a known reach pays SOUND_REPEAT")
            t.has(ev, "You sound reach 4 (Heron) again: guard 5.", "the repeat wording")
            t.has(ev, f"Soundings +{C['SOUND_REPEAT']}.", "the repeat gain")
            s = st(t, soundings=0, _turn=C["STIR_TURN"] - 1)
            t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_GAIN"], "the turn before the stir still pays SOUND_GAIN")
            s = st(t, soundings=0, _turn=C["STIR_TURN"])
            t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_LATE"], "from the stir a fresh sounding pays SOUND_LATE")
            s = st(t, soundings=0, _turn=C["STIR_TURN"], known=[False] * 3 + [True] + [False] * 3)
            t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_REPEAT"], "a repeat pays SOUND_REPEAT after the stir too")
            s = st(t, soundings=0, charted=[False] * 3 + [True] + [False] * 3)
            t.ok(t.offered(s, "sound", reach=4), "a charted reach can still be sounded")
            s = st(t)
            t.eq(len([o for o in self.options(s) if o["id"] == "sound"]), R, "every reach can be sounded")
            t.eq(t.label(s, "sound", reach=4), f"Sound reach 4 (Heron, guard unknown): +{plural(C['SOUND_GAIN'], 'sounding')} (+{C['FRIEND_NOTE']} more if House Heron is your friend)", "the label before sounding: the friend's note is a maybe")
            s2 = st(t, _turn=C["STIR_TURN"])
            t.eq(t.label(s2, "sound", reach=4), f"Sound reach 4 (Heron, guard unknown): +{plural(C['SOUND_LATE'], 'sounding')} (+{C['FRIEND_NOTE']} more if House Heron is your friend)", "the label after the stir")
            s3 = st(t, known=[False] * 3 + [True] + [False] * 3)
            t.eq(t.label(s3, "sound", reach=4), f"Sound reach 4 (Heron, guard 5): +{plural(C['SOUND_REPEAT'], 'sounding')} (+{C['FRIEND_NOTE']} more if House Heron is your friend)", "the label of a known reach")
            s4 = st(t, cleared=[0])
            t.eq(t.label(s4, "sound", reach=4), f"Sound reach 4 (Heron, guard unknown): +{plural(C['SOUND_GAIN'], 'sounding')}", "a ruled-out house cannot be the friend, so no maybe")
            s5 = st(t, friend=2)
            t.eq(t.label(s5, "sound", reach=4), f"Sound reach 4 (Heron, guard unknown): +{plural(C['SOUND_GAIN'], 'sounding')}", "once the friend is known, other houses show no maybe")
            t.eq(t.label(s5, "sound", reach=3), f"Sound reach 3 (Moth, guard unknown): +{plural(C['SOUND_GAIN'] + C['FRIEND_NOTE'], 'sounding')}", "and the friend's own reaches show the extra")
            s6 = st(t, soundings=0, charted=[False] * 3 + [True] + [False] * 3, known=[False] * 3 + [True] + [False] * 3)
            t.apply(s6, "sound", {"reach": 4})
            t.eq(s6["soundings"], C["SOUND_REPEAT"], "a charted reach pays SOUND_REPEAT")
            s7 = st(t, soundings=0)
            t.apply(s7, "sound", {"reach": 4.0})
            t.ok(s7["known"][3], "a whole-number float names the same reach")
            s0 = t.fresh()
            t.eq((s0["soundings"], s0["drill"]), (C["START_SOUNDINGS"], C["START_DRILL"]), "the starting stock")

        def r3(t):
            s = st(t, soundings=C["TRAIN_COST"], drill=0)
            t.ok(t.offered(s, "train"), "exactly the cost is enough")
            t.eq(t.label(s, "train"), f"Train the sappers: Drill 0 to 1 (-{plural(C['TRAIN_COST'], 'sounding')})", "the train label")
            ev = t.apply(s, "train")
            t.eq((s["soundings"], s["drill"]), (0, 1), "training costs TRAIN_COST for one Drill")
            t.has(ev, "The sappers drill through the night. Drill is now 1.", "the training event")
            t.ok(not t.offered(st(t, soundings=C["TRAIN_COST"] - 1), "train"), "one sounding short cannot train")
            t.ok(not t.offered(st(t, soundings=30, drill=C["DRILL_MAX"]), "train"), "Drill stops at DRILL_MAX")
            s = st(t, soundings=30, drill=C["DRILL_MAX"] - 1)
            t.ok(t.offered(s, "train"), "one below the cap can train")
            self._hits.clear()
            ev = t.apply(s, "train")
            t.eq(s["drill"], C["DRILL_MAX"], "training reaches the cap")
            t.ok("drill_max" in self._hits, "the cap is noted")
            s = st(t, soundings=30, drill=0)
            self._hits.clear()
            t.apply(s, "train")
            t.ok("drill_max" not in self._hits, "Drill 1 is not the cap")
            s = st(t, soundings=0, drill=0)
            t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[C["GUARD_HI"]])
            t.eq(s["soundings"], C["CHART_PAY"], "a charted reach pays CHART_PAY")
            s = st(t, soundings=0, drill=0, hidden__guard=[C["GUARD_HI"]] * R)
            t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[1])
            t.eq(s["soundings"], 0, "a failure pays nothing")
            s = st(t, soundings=C["BREACH_COST"], drill=0, _turn=C["STIR_TURN"], hidden__guard=[1] * R)
            t.apply(s, "breach", {"fork": 3, "push": 0}, dice=[C["DIE"]])
            t.eq(s["soundings"], 3 * C["CHART_PAY"], "three reaches charted by a breach pay three times")
            s = st(t, soundings=C["WRIT_COST"], _turn=C["WRIT_TURN"])
            t.apply(s, "writ", {"reach": 4})
            t.eq(s["soundings"], C["CHART_PAY"], "a writ pays too")

        def r4(t):
            known = [False] * 3 + [True] + [False] * 3
            s = st(t, known=known, drill=2)
            t.eq(t.label(s, "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 5): roll 3+ before any push", "the known label")
            t.eq(t.label(s, "deploy", reach=5, push=0), "Deploy the sappers at reach 5 (Eel, guard unknown)", "the unknown label")
            t.eq(t.label(st(t, known=known, drill=3), "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 5): roll 2+ before any push", "a roll of 2 is not a sure thing")
            t.eq(t.label(st(t, known=known, drill=4), "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 5): any roll wins", "a sure thing")
            t.eq(t.label(st(t, known=known, drill=5), "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 5): any roll wins", "a sure thing, well over")
            hard = st(t, known=known, drill=2, hidden__guard=[5, 5, 5, 8, 5, 5, 5])
            t.eq(t.label(hard, "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 8): roll 6+ before any push", "the top of the die")
            hard = st(t, known=known, drill=2, hidden__guard=[5, 5, 5, 9, 5, 5, 5])
            t.eq(t.label(hard, "deploy", reach=4, push=0), "Deploy the sappers at reach 4 (Heron, guard 9): no roll wins without a push", "past the die, but a push can still win")
            edge = st(t, known=known, drill=2, soundings=C["PUSH_MAX"], hidden__guard=[5, 5, 5, 2 + C["DIE"] + C["PUSH_MAX"], 5, 5, 5])
            t.eq(t.label(edge, "deploy", reach=4, push=0), f"Deploy the sappers at reach 4 (Heron, guard {2 + C['DIE'] + C['PUSH_MAX']}): no roll wins without a push", "a full push lands exactly on the top of the die")
            edge = st(t, known=known, drill=2, soundings=C["PUSH_MAX"], hidden__guard=[5, 5, 5, 3 + C["DIE"] + C["PUSH_MAX"], 5, 5, 5])
            t.eq(t.label(edge, "deploy", reach=4, push=0), f"Deploy the sappers at reach 4 (Heron, guard {3 + C['DIE'] + C['PUSH_MAX']}): no roll can win", "one past the best push")
            edge = st(t, known=known, drill=2, soundings=0, hidden__guard=[5, 5, 5, 3 + C["DIE"], 5, 5, 5])
            t.eq(t.label(edge, "deploy", reach=4, push=0), f"Deploy the sappers at reach 4 (Heron, guard {3 + C['DIE']}): no roll can win", "with nothing to push, past the die cannot win")
            edge = st(t, known=known, drill=2, soundings=0, hidden__guard=[5, 5, 5, 2 + C["DIE"], 5, 5, 5])
            t.eq(t.label(edge, "deploy", reach=4, push=0), f"Deploy the sappers at reach 4 (Heron, guard {2 + C['DIE']}): roll {C['DIE']}+ before any push", "with nothing to push, the top of the die still wins")
            t.eq(self.p_win(1), 1.0, "any roll wins at need 1")
            t.eq(self.p_win(0), 1.0, "never above one")
            t.eq(self.p_win(C["DIE"]), 1 / C["DIE"], "a six needs a six")
            t.eq(self.p_win(C["DIE"] + 1), 0.0, "never below zero")
            for soundings, top in ((0, 0), (1, 1), (C["PUSH_MAX"], C["PUSH_MAX"]), (C["PUSH_MAX"] + 5, C["PUSH_MAX"])):
                o = [x for x in self.options(st(t, soundings=soundings)) if x["id"] == "deploy"][0]
                t.eq(o["params"], {"push": {"min": 0, "max": top}}, "the push is up to PUSH_MAX and never more than you hold")
            s = st(t, soundings=10, drill=2, known=known)
            ev = t.apply(s, "deploy", {"reach": 4, "push": 1}, dice=[2])
            t.ok(s["charted"][3], "a roll that meets the guard charts the reach")
            t.eq((s["soundings"], s["drill"]), (9 + C["CHART_PAY"], 2), "the push is spent, the chart pays and Drill stays after a success")
            t.has(ev, "The sappers go in at reach 4 (Heron): guard 5, Drill 2, push 1.", "the approach")
            t.has(ev, f"roll 2 (need 2+) success. Reach 4 is charted: Soundings +{C['CHART_PAY']}.", "the success wording")
            s = st(t, soundings=10, drill=5, known=known)
            ev = t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[1])
            t.ok(s["charted"][3], "a sure thing succeeds even on a 1")
            t.has(ev, "roll 1 (need 1+) success.", "a need of zero or less reads 1+")
            s = st(t, soundings=10, drill=4, known=known)
            ev = t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[1])
            t.has(ev, "roll 1 (need 1+) success.", "a need of exactly 1 reads 1+")
            s = st(t, soundings=10, drill=3, known=known)
            ev = t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[1])
            t.ok(not s["charted"][3], "a need of 2 is not a sure thing")
            t.has(ev, "roll 1 (need 2+) fail.", "a need of 2 reads 2+")
            s = st(t, soundings=10, drill=2, known=known)
            self._hits.clear()
            ev = t.apply(s, "deploy", {"reach": 4, "push": 1}, dice=[1])
            t.ok(not s["charted"][3], "a roll one short fails")
            t.eq((s["soundings"], s["drill"]), (9, 2 - C["DRILL_LOSS"]), "a failure spends the push and costs Drill")
            t.has(ev, f"roll 1 (need 2+) fail. The sappers are driven off and Drill falls to {2 - C['DRILL_LOSS']}.", "the failure wording")
            t.ok("drill_lost" in self._hits, "lost Drill is noted")
            t.ok(s["known"][3], "a failed attempt still teaches the guard")
            s = st(t, soundings=10, drill=0)
            self._hits.clear()
            ev = t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[4])
            t.eq(s["drill"], 0, "Drill never goes below zero")
            t.ok(any(e.endswith("fail. The sappers are driven off.") for e in ev), "no Drill to lose, no mention of it")
            t.ok("drill_lost" not in self._hits, "nothing was lost")
            s = st(t, soundings=10, drill=0)
            t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[5])
            t.ok(s["charted"][3], "a bare roll of exactly the guard charts the reach")
            s = st(t, charted=[False] * 3 + [True] + [False] * 3)
            t.ok(not t.offered(s, "deploy", reach=4, push=0), "a charted reach is not deployed at again")
            t.ok(t.offered(s, "deploy", reach=5, push=0), "an uncharted reach can be")
            wins = 0
            for sd in range(1, 301):
                s = st(t, soundings=10, drill=1)
                t.apply(s, "deploy", {"reach": 4, "push": 1}, seed=sd)
                wins += s["charted"][3]
            want = (C["DIE"] - (5 - 1 - 1) + 1) / C["DIE"]
            t.ok(abs(wins / 300 - want) < 0.09, f"guard 5, Drill 1, push 1 should succeed about {want:.0%}, got {wins / 300:.0%}")

        def r5(t):
            t.eq(t.fresh()["barge"], 0, "the barge starts at reach 1")
            s = st(t)
            ev = t.advance(s, turn=C["PACE"] - 1)
            t.eq(s["barge"], 0, "no drop before the pace")
            t.has(ev, f"The barge lies at reach 1 and will drop after turn {C['PACE']}.", "the tell before a drop")
            ev = t.advance(s, turn=1)
            t.has(ev, f"will drop after turn {C['PACE']}.", "the first turn shows the same drop")
            s = st(t)
            self._hits.clear()
            ev = t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 1, "it drops one reach after turn PACE, to the East fork on a tie")
            t.has(ev, "At dusk the barge drops to reach 2: the branches stand level, so it keeps to the East.", "the tie wording")
            t.has(ev, f"The barge lies at reach 2 and will drop after turn {2 * C['PACE']}.", "the next drop")
            t.ok("fork_east" in self._hits and "fork_west" not in self._hits, "the East fork is noted")
            t.ok(t.status(s).endswith("Barge 2"), "the status shows the barge")
            s = st(t)
            t.advance(s, turn=C["PACE"] + 1)
            t.eq(s["barge"], 0, "no drop the turn after the pace")
            s = st(t, charted=[False, True, False, False, False, False, False])
            self._hits.clear()
            ev = t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 2, "East charted more: the barge takes the West fork")
            t.has(ev, "drops to reach 3 and takes the West branch, the one you have charted less.", "the West wording")
            t.ok("fork_west" in self._hits, "the West fork is noted")
            s = st(t, charted=[False, False, True, False, False, False, False])
            t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 1, "West charted more: the barge takes the East fork")
            s = st(t, charted=[True, False, False, False, False, False, False])
            t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 1, "the Source is on neither branch")
            s = st(t, charted=[False, False, False, True, True, False, False])
            t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 2, "a branch counts all its reaches: East has two charted")
            s = st(t, charted=[False, False, True, False, False, True, False])
            t.advance(s, turn=C["PACE"])
            t.eq(s["barge"], 1, "two against one: West has more")
            s = st(t, barge=1)
            self._hits.clear()
            ev = t.advance(s, turn=2 * C["PACE"])
            t.eq(s["barge"], 3, "a level pair of mouths: the lower number")
            t.has(ev, "At dusk the barge drops to reach 4: the mouths stand level, so it takes the lower.", "the level mouth wording")
            t.ok("mouth" in self._hits, "the mouth is noted")
            t.has(ev, f"The barge lies at reach 4 and will slip out to sea after turn {C['TURNS']}.", "the last tell")
            s = st(t, barge=1, charted=[False, False, False, True, False, False, False])
            ev = t.advance(s, turn=2 * C["PACE"])
            t.eq(s["barge"], 4, "the uncharted mouth")
            t.has(ev, "drops to reach 5, the mouth you have not charted.", "the uncharted mouth wording")
            s = st(t, barge=1, charted=[False, False, False, False, True, False, False])
            t.advance(s, turn=2 * C["PACE"])
            t.eq(s["barge"], 3, "the other uncharted mouth")
            s = st(t, barge=1, charted=[False, False, False, True, True, False, False])
            t.advance(s, turn=2 * C["PACE"])
            t.eq(s["barge"], 3, "two charted mouths: the lower")
            s = st(t, barge=2, charted=[False, False, False, False, False, True, False])
            ev = t.advance(s, turn=2 * C["PACE"])
            t.eq(s["barge"], 6, "under the West fork, the uncharted mouth is reach 7")
            t.has(ev, "drops to reach 7, the mouth you have not charted.", "reach 7")
            s = st(t, barge=1)
            t.advance(s, turn=2 * C["PACE"] - 1)
            t.eq(s["barge"], 1, "no drop a turn early")
            s = st(t, barge=3)
            ev = t.advance(s, turn=3 * C["PACE"])
            t.eq(s["barge"], 3, "the barge waits at a mouth")
            t.ok(not any("drops to" in e for e in ev), "no drop from a mouth")
            s = st(t, soundings=10, drill=C["DRILL_MAX"], _turn=C["PACE"], hidden__guard=[1] * R)
            s, ev = t.step(s, "deploy", {"reach": 1, "push": 0})
            go = [k for k, e in enumerate(ev) if "The sappers go in at reach 1 (Heron, barge here)" in e]
            drop = [k for k, e in enumerate(ev) if "At dusk the barge drops to reach 2" in e]
            t.ok(go and drop and go[0] < drop[0], "the action meets the barge where it stands, then dusk moves it")
            t.eq((s["barge"], s["_turn"]), (1, C["PACE"] + 1), "dusk moved the barge and the turn counter went up")
            s = st(t, barge=3)
            ev = t.advance(s, turn=C["TURNS"] - 1)
            t.has(ev, f"The barge lies at reach 4 and will slip out to sea after turn {C['TURNS']}.", "the tell the turn before dawn")
            ev = t.advance(st(t, barge=3), turn=C["TURNS"])
            t.ok(not any("The barge lies" in e for e in ev), "the last dusk has no tell: the end reason says it")
            s = st(t, barge=3, charted=[False, False, False, True, False, False, False])
            t.eq(self.eff(s, 3), 5, "a charted reach has no ward to pay")
            t.eq(self.eff(s, 4), 5, "and no other reach does")
            t.eq(self.visible(s)["reaches"][3]["barge"], True, "the barge is still shown on it")
            s["known"][3] = True
            t.eq(t.label(s, "sound", reach=4), f"Sound reach 4 (Heron, barge here, guard 5): +{plural(C['SOUND_REPEAT'], 'sounding')} (+{C['FRIEND_NOTE']} more if House Heron is your friend)", "a charted barge reach shows its plain guard")
            s = st(t, barge=3)
            t.eq(self.eff(s, 3), 5 + C["WARD"], "the reach holding the barge has guard +WARD")
            t.eq(self.eff(s, 4), 5, "other reaches are untouched")
            s = st(t, barge=4)
            t.eq((self.eff(s, 3), self.eff(s, 4)), (5, 5 + C["WARD"]), "the ward moves with the barge")
            s = st(t, barge=3, soundings=0)
            ev = t.apply(s, "sound", {"reach": 4})
            t.has(ev, f"guard {5 + C['WARD']}.", "sounding shows the ward")
            s = st(t, barge=3, drill=2, soundings=10)
            self._hits.clear()
            ev = t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[5 + C["WARD"] - 2])
            t.has(ev, f"The sappers go in at reach 4 (Heron, barge here): guard {5 + C['WARD']}, Drill 2, push 0.", "the ward wording")
            t.ok(s["charted"][3] and "ward" in self._hits, "a roll that meets the warded guard charts it")
            s = st(t, barge=3, drill=2, soundings=10)
            t.apply(s, "deploy", {"reach": 4, "push": 0}, dice=[5 + C["WARD"] - 3])
            t.ok(not s["charted"][3], "one short of the warded guard fails")
            s = st(t, barge=3)
            t.eq(t.label(s, "sound", reach=4), f"Sound reach 4 (Heron, barge here, guard unknown): +{plural(C['SOUND_GAIN'], 'sounding')} (+{C['FRIEND_NOTE']} more if House Heron is your friend)", "the label shows the barge")

        def r6(t):
            s = st(t)
            t.eq((self.eff(s, 2), self.eff(s, 5)), (5 - C["EASE"], 5 - C["EASE"]), "the friend's reaches have guard -EASE")
            t.eq((self.eff(s, 1), self.eff(s, 3)), (5, 5), "the other houses are untouched")
            s = st(t, soundings=0)
            self._hits.clear()
            ev = t.apply(s, "sound", {"reach": 6})
            t.eq(s["friend"], 2, "meeting the friend shows it")
            t.eq(s["soundings"], C["SOUND_GAIN"] + C["FRIEND_NOTE"], "the friend pays extra")
            t.has(ev, "The Moth keepers slip you a note: House Moth is on your side.", "the reveal")
            t.has(ev, f"Soundings +{C['SOUND_GAIN'] + C['FRIEND_NOTE']} ({C['FRIEND_NOTE']} from the Moth keepers).", "the extra is explained")
            t.has(ev, f"You sound reach 6 (Moth): guard {5 - C['EASE']}.", "the eased guard")
            t.ok("friend" in self._hits, "the friend is noted")
            t.eq(self.visible(s)["friend"], "Moth", "the friend is shown once known")
            t.eq(t.label(s, "sound", reach=3), f"Sound reach 3 (Moth, guard unknown): +{plural(C['SOUND_GAIN'] + C['FRIEND_NOTE'], 'sounding')}", "the label shows the friend's extra once known")
            ev = t.apply(s, "sound", {"reach": 3})
            t.eq(s["soundings"], 2 * C["SOUND_GAIN"] + 2 * C["FRIEND_NOTE"], "the extra comes every time")
            t.ok(not any("keepers slip you a note" in e for e in ev), "the reveal happens once")
            s = st(t, soundings=0, known=[False, False, True, False, False, False, False], friend=2)
            t.apply(s, "sound", {"reach": 3})
            t.eq(s["soundings"], C["SOUND_REPEAT"] + C["FRIEND_NOTE"], "the friend pays extra on a repeat too")
            s = st(t, soundings=0)
            self._hits.clear()
            ev = t.apply(s, "sound", {"reach": 4})
            t.eq(s["soundings"], C["SOUND_GAIN"], "another house pays no extra")
            t.eq((s["friend"], s["cleared"]), (-1, [0]), "the house is ruled out")
            t.has(ev, "The Heron keepers give you nothing: House Heron is not your friend.", "the ruling out")
            t.ok("friend" not in self._hits and "elimination" not in self._hits, "nothing revealed yet")
            ev = t.apply(s, "sound", {"reach": 7})
            t.eq(s["cleared"], [0], "a house is ruled out once")
            t.ok(not any("keepers" in e for e in ev), "no second ruling")
            t.eq(self.visible(s)["not_friends"], ["Heron"], "the ruled-out house is shown")
            ev = t.apply(s, "sound", {"reach": 5})
            t.eq((s["cleared"], s["friend"]), ([0, 1], 2), "two houses ruled out leave the friend")
            t.has(ev, "The Eel keepers give you nothing: House Eel is not your friend.", "the second ruling")
            t.has(ev, "That leaves House Moth: it is on your side.", "the elimination")
            t.ok("elimination" in self._hits, "the elimination is noted")
            s = st(t, soundings=0)
            t.apply(s, "sound", {"reach": 5})
            t.eq(s["soundings"], C["SOUND_GAIN"], "no extra from a house that is not the friend")
            s = st(t, soundings=0, cleared=[0])
            t.apply(s, "sound", {"reach": 6})
            t.eq((self.visible(s)["friend"], self.visible(s)["not_friends"]), ("Moth", ["Heron", "Eel"]), "once the friend is found, every other house is shown as not the friend")
            s = st(t, soundings=0)
            t.eq(self.visible(s)["not_friends"], [], "nobody is ruled out yet")
            t.apply(s, "sound", {"reach": 4})
            t.eq(self.visible(s)["not_friends"], ["Heron"], "a house ruled out is listed before the friend is known")
            base = st(t, known=[False] * 3 + [True] + [False] * 3, cleared=[0], hidden__guard=[5, 5, 5, 6, 5, 5, 5])
            mates, seen_guards = set(), set()
            for sd in range(1, 40):
                s = t.copy(base)
                self.resample_hidden(s, t.rng(sd))
                t.eq(s["hidden"]["guard"][3], 6, "a known guard is not redrawn")
                t.ok(s["hidden"]["friend"] != 0, "a ruled-out house is not redrawn as the friend")
                mates.add(s["hidden"]["friend"])
                seen_guards.update(s["hidden"]["guard"][:3] + s["hidden"]["guard"][4:])
            t.eq(mates, {1, 2}, "the friend is redrawn among the houses not ruled out")
            t.eq(seen_guards, set(range(C["GUARD_LO"], C["GUARD_HI"] + 1)), "unknown guards are redrawn over the whole range")
            s = t.copy(base)
            s["friend"], s["hidden"]["friend"] = 2, 2
            self.resample_hidden(s, t.rng(3))
            t.eq(s["hidden"]["friend"], 2, "a revealed friend stays")
            s = st(t, soundings=10, drill=2)
            ev = t.apply(s, "deploy", {"reach": 3, "push": 0}, dice=[1])
            t.eq(s["friend"], 2, "a deploy meets the house too")
            t.has(ev, f"The sappers go in at reach 3 (Moth): guard {5 - C['EASE']}, Drill 2, push 0.", "the eased guard in a deploy")
            s = st(t, soundings=10, drill=2, _turn=C["WRIT_TURN"])
            t.apply(s, "writ", {"reach": 3})
            t.eq(s["friend"], 2, "the writ meets the house too")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"])
            t.apply(s, "breach", {"fork": 3, "push": 0}, dice=[1])
            t.eq(s["friend"], 2, "a breach meets every house under the fork")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"])
            ev = t.apply(s, "breach", {"fork": 2, "push": 0}, dice=[1])
            t.eq((s["cleared"], s["friend"]), ([1, 0], 2), "a breach under the East fork rules out Eel and Heron, which leaves Moth")
            t.has(ev, "That leaves House Moth: it is on your side.", "the elimination after a breach")
            t.eq(self.shown(st(t), 2), None, "an unknown guard is not shown")

        def r7(t):
            s = st(t, _turn=C["STIR_TURN"] - 1)
            t.eq(self.eff(s, 3), 5, "before the stir the guard is as drawn")
            s["_turn"] = C["STIR_TURN"]
            t.eq(self.eff(s, 3), 5 + C["STIR"], "from the stir every guard is +STIR")
            t.eq(self.eff(s, 2), 5 + C["STIR"] - C["EASE"], "the stir, the friend's ease and the ward all add up")
            s["barge"] = 3
            t.eq(self.eff(s, 3), 5 + C["STIR"] + C["WARD"], "the stir and the ward add up")
            self._hits.clear()
            ev = t.advance(st(t), turn=C["STIR_TURN"] - 1)
            t.has(ev, f"The dream stirs. From turn {C['STIR_TURN']} every guard is {C['STIR']} higher, a first sounding pays only {C['SOUND_LATE']}, and the sappers may breach a branch, once.", "the stir announcement")
            t.ok("stir" in self._hits, "the stir is noted")
            ev = t.advance(st(t), turn=C["STIR_TURN"])
            t.ok(not any("The dream stirs" in e for e in ev), "the stir is announced once")
            ev = t.advance(st(t), turn=C["STIR_TURN"] - 2)
            t.ok(not any("The dream stirs" in e for e in ev), "not two turns early")
            s = st(t, soundings=20, _turn=C["STIR_TURN"] - 1)
            t.ok(not any(o["id"] == "breach" for o in self.options(s)), "no breach before the stir")
            s["_turn"] = C["STIR_TURN"]
            t.ok(t.offered(s, "breach", fork=2, push=0) and t.offered(s, "breach", fork=3, push=0), "both forks can be breached from the stir")
            t.eq(t.label(s, "breach", fork=2, push=0), f"Breach the East branch (reaches 2, 4 and 5; highest guard unknown; -{plural(C['BREACH_COST'], 'sounding')})", "the East label")
            t.eq(t.label(s, "breach", fork=3, push=0), f"Breach the West branch (reaches 3, 6 and 7; highest guard unknown; -{plural(C['BREACH_COST'], 'sounding')})", "the West label")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], known=[True] * R, hidden__guard=[5, 5, 6, 6, 4, 5, 5])
            t.eq(t.label(s, "breach", fork=2, push=0), f"Breach the East branch (reaches 2, 4 and 5; highest guard {6 + C['STIR']}; -{plural(C['BREACH_COST'], 'sounding')})", "the highest known guard")
            t.eq(t.label(s, "breach", fork=3, push=0), f"Breach the West branch (reaches 3, 6 and 7; highest guard {6 + C['STIR'] - C['EASE']}; -{plural(C['BREACH_COST'], 'sounding')})", "the friend's ease inside a branch")
            s = st(t, soundings=C["BREACH_COST"], _turn=C["STIR_TURN"])
            t.ok(t.offered(s, "breach", fork=2, push=0), "exactly the cost is enough")
            o = [x for x in self.options(s) if x["id"] == "breach"][0]
            t.eq(o["params"], {"push": {"min": 0, "max": 0}}, "nothing left to push")
            s = st(t, soundings=C["BREACH_COST"] + 1, _turn=C["STIR_TURN"])
            o = [x for x in self.options(s) if x["id"] == "breach"][0]
            t.eq(o["params"], {"push": {"min": 0, "max": 1}}, "the push comes after the cost")
            s = st(t, soundings=C["BREACH_COST"] + 20, _turn=C["STIR_TURN"])
            o = [x for x in self.options(s) if x["id"] == "breach"][0]
            t.eq(o["params"], {"push": {"min": 0, "max": C["PUSH_MAX"]}}, "the push is capped")
            t.ok(not t.offered(st(t, soundings=C["BREACH_COST"] - 1, _turn=C["STIR_TURN"]), "breach", fork=2, push=0), "one sounding short cannot breach")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], charted=[False, False, False, True, True, False, False])
            t.ok(not t.offered(s, "breach", fork=2, push=0), "a fork with one reach left is a plain deploy")
            t.ok(t.offered(s, "breach", fork=3, push=0), "the other fork is still open")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], charted=[False, True, False, True, False, False, False])
            t.ok(not t.offered(s, "breach", fork=2, push=0), "a fork with one reach left is a plain deploy, charted fork or not")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], charted=[False, True, False, False, False, False, False])
            t.eq(t.label(s, "breach", fork=2, push=0), f"Breach the East branch (reaches 4 and 5; highest guard unknown; -{plural(C['BREACH_COST'], 'sounding')})", "two reaches left")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], charted=[False, False, True, False, False, True, True])
            t.ok(not t.offered(s, "breach", fork=3, push=0), "a finished West branch cannot be breached")
            s = st(t, soundings=20, _turn=C["STIR_TURN"], barge=1, known=[True] * R, charted=[False, True, False, False, False, False, False])
            t.eq(t.label(s, "breach", fork=2, push=0), f"Breach the East branch (reaches 4 and 5; highest guard {5 + C['STIR']}; -{plural(C['BREACH_COST'], 'sounding')})", "a charted, warded fork does not raise the breach")
            hard = [5, 5, 5, 6, 4, 5, 5]
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], hidden__guard=hard)
            self._hits.clear()
            ev = t.apply(s, "breach", {"fork": 2, "push": 1}, dice=[4])
            t.ok(s["charted"][1] and s["charted"][3] and s["charted"][4], "one roll charts the fork and its mouths")
            t.eq((s["soundings"], s["drill"]), (10 - C["BREACH_COST"] - 1 + 3 * C["CHART_PAY"], 2), "the cost and the push are spent, and three reaches pay")
            t.ok(all(s["known"][m] for m in (1, 3, 4)), "a breach teaches every guard under it")
            t.has(ev, f"The sappers burrow under the East branch (reaches 2, 4 and 5): highest guard {6 + C['STIR']}, Drill 2, push 1.", "the burrow wording")
            t.has(ev, f"roll 4 (need {6 + C['STIR'] - 2 - 1}+) success. Reaches 2, 4 and 5 are charted: Soundings +{3 * C['CHART_PAY']}.", "the success wording")
            t.ok("breach" in self._hits, "the breach is noted")
            t.ok(s["breach_used"], "the breach is spent")
            s["soundings"] = 30
            t.ok(not any(o["id"] == "breach" for o in self.options(s)), "once only, after a success")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], hidden__guard=hard)
            t.ok(not s["breach_used"], "a fresh game has its breach")
            ev = t.apply(s, "breach", {"fork": 2, "push": 1}, dice=[3])
            t.ok(s["breach_used"], "a failed breach is spent too")
            s["soundings"] = 30
            t.ok(not any(o["id"] == "breach" for o in self.options(s)), "once only, after a failure")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], hidden__guard=hard)
            ev = t.apply(s, "breach", {"fork": 2, "push": 1}, dice=[3])
            t.ok(not any(s["charted"][m] for m in (1, 3, 4)), "a roll one short charts nothing")
            t.eq((s["soundings"], s["drill"]), (10 - C["BREACH_COST"] - 1, 2 - C["DRILL_LOSS"]), "a failed breach costs Drill as usual")
            t.has(ev, f"roll 3 (need 4+) fail. The sappers are driven off and Drill falls to {2 - C['DRILL_LOSS']}.", "the failure wording")
            t.ok(all(s["known"][m] for m in (1, 3, 4)), "a failed breach still teaches every guard under it")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], hidden__guard=[5, 5, 5, 9, 4, 5, 5], charted=[False, False, False, True, False, False, False])
            ev = t.apply(s, "breach", {"fork": 2, "push": 0}, dice=[5 + C["STIR"] - 2])
            t.ok(s["charted"][1] and s["charted"][4], "a charted reach does not raise the roll")
            t.has(ev, "(reaches 2 and 5)", "only the uncharted reaches are listed")
            t.has(ev, f"Reaches 2 and 5 are charted: Soundings +{2 * C['CHART_PAY']}.", "two reaches charted")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], hidden__guard=[5, 5, 5, 5, 5, 8, 5])
            ev = t.apply(s, "breach", {"fork": 3, "push": 0}, dice=[8 + C["STIR"] - C["EASE"] - 2])
            t.has(ev, f"burrow under the West branch (reaches 3, 6 and 7): highest guard {8 + C['STIR'] - C['EASE']}", "the West wording")
            t.ok(s["charted"][2] and s["charted"][5] and s["charted"][6], "the friend's eased guard counts in the maximum")
            s = st(t, soundings=10, drill=C["DRILL_MAX"], _turn=C["STIR_TURN"], hidden__guard=[1] * R)
            ev = t.apply(s, "breach", {"fork": 2, "push": 0}, dice=[1])
            t.has(ev, "roll 1 (need 1+) success.", "a breach that needs nothing reads 1+")
            s = st(t, soundings=10, drill=2, _turn=C["STIR_TURN"], barge=1)
            ev = t.apply(s, "breach", {"fork": 2, "push": 0}, dice=[6])
            t.has(ev, f"highest guard {5 + C['STIR'] + C['WARD']}", "the barge's ward counts in a breach")

        def r8(t):
            s = st(t, soundings=30, _turn=C["WRIT_TURN"] - 1)
            t.ok(not any(o["id"] == "writ" for o in self.options(s)), "no writ before its turn")
            s["_turn"] = C["WRIT_TURN"]
            t.eq(len([o for o in self.options(s) if o["id"] == "writ"]), R, "a writ can open any uncharted reach")
            t.eq(t.label(s, "writ", reach=4), f"Spend the writ on reach 4 (Heron): charted with no roll (-{plural(C['WRIT_COST'], 'sounding')})", "the writ label")
            t.ok(t.offered(st(t, soundings=C["WRIT_COST"], _turn=C["WRIT_TURN"]), "writ", reach=1), "exactly the cost is enough")
            t.ok(not t.offered(st(t, soundings=C["WRIT_COST"] - 1, _turn=C["WRIT_TURN"]), "writ", reach=1), "one sounding short")
            s = st(t, soundings=C["WRIT_COST"], _turn=C["WRIT_TURN"], hidden__guard=[99] * R, charted=[False, False, False, False, True, False, False])
            t.ok(not t.offered(s, "writ", reach=5), "a charted reach needs no writ")
            self._hits.clear()
            ev = t.apply(s, "writ", {"reach": 4})
            t.ok(s["charted"][3] and s["writ_used"], "the writ charts the reach without a roll, whatever its guard")
            t.ok(s["known"][3], "a charted reach is a known reach")
            t.eq(s["soundings"], C["CHART_PAY"], "the writ costs WRIT_COST and the chart pays")
            t.has(ev, f"The writ opens reach 4 (Heron): charted, no roll. Soundings +{C['CHART_PAY']}.", "the writ wording")
            t.ok("writ" in self._hits, "the writ is noted")
            s["soundings"] = 30
            t.ok(not any(o["id"] == "writ" for o in self.options(s)), "once only")
            s = st(t, soundings=30, _turn=C["WRIT_TURN"], barge=3, hidden__guard=[99] * R)
            t.apply(s, "writ", {"reach": 4})
            t.ok(s["charted"][3], "the ward does not stop a writ")
            self._hits.clear()
            ev = t.advance(st(t), turn=C["WRIT_TURN"] - 1)
            t.has(ev, "A courier from the Bureau arrives. The writ is yours to spend, once.", "the courier")
            t.ok("writ_ready" in self._hits, "the courier is noted")
            ev = t.advance(st(t), turn=C["WRIT_TURN"])
            t.ok(not any("courier" in e for e in ev), "the courier comes once")
            ev = t.advance(st(t), turn=C["WRIT_TURN"] - 2)
            t.ok(not any("courier" in e for e in ev), "not two turns early")

        return [
            (1, "delta, goal and dawn", r1), (2, "sounding", r2), (3, "training", r3), (4, "deploying", r4),
            (5, "the barge", r5), (6, "the friend", r6), (7, "stir and breach", r7), (8, "the writ", r8),
        ]


if __name__ == "__main__":
    run(G)
