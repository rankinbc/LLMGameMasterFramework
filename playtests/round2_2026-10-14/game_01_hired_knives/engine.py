"""Hired Knives: a /play engine.

Rolls: FORM=6 pursuit (chase a target that moves by hidden rule), SET=24 restaurant kitchen on a
Friday night, ROLE=12 mercenary captain (a freelance kitchen brigade for hire), LOOP=18 capture and
hold territory nodes (the seven kitchens of High Street), CLOCK=6 rival racing to the same prize
(Rooney's Copper Pans), TWIST=37 information arrives one turn late, WIN=2 reach a location and get
out (be in Volk's Friday kitchen, then walk the crew out paid), MAP=11 weekly calendar grid 7 by 3
(seven days, three services: the week is the board), TONE=2 dry humor.

Rulesheet (8 lines):
1. High Street has 7 kitchens in a row. You hold a kitchen with 2 cooks; a 3rd cook makes it hard to raid and easier to cook in. Rooney's Copper Pans hold kitchens too.
2. 21 services, Saturday lunch to Friday late. One action per service. Each kitchen you hold pays 4 a service, each cook costs 1; if you cannot pay, a cook walks.
3. Volk the critic eats dinner at the loudest kitchen (highest Buzz) she has not tried yet. Ties are her secret, and she has one habit her column hints at.
4. If she eats in your kitchen: d6, need 4+ (3+ with 3 cooks). Success: a star (a 6 is two) and +6 cash. Fail: Buzz -2.
5. News is one service late: the Buzz board, where Volk ate, and Rooney's moves. Your own kitchen's rolls, and raids on you, you see at once. Taking or raiding a kitchen whose holder changed since the board was printed wastes the service.
6. Actions: Take a house kitchen (8 cash, 2 spare cooks), Raid one of Rooney's (2 spare cooks, d6 need 5+, 4+ with 3 spare; a failed raid loses a cook), Push Buzz +2 (4 cash), Reinforce (3rd cook), Hire a cook (6 cash).
7. Friday dinner Volk returns to the kitchen with the most stars (tie: loudest). Hold it and pass the service: 3+ if you earned its star, else 4+. Then walk out paying 2 per cook.
8. Lose if Rooney feeds her Friday or she eats elsewhere. Two failed rolls in a row open Comp the Room. From Wednesday Rooney pushes harder, raids your starred kitchens on Thursday and Friday lunch, and her habit is for sale (6).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
from gm_base import Game, run  # noqa: E402

DAYS = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
SVCS = ["lunch", "dinner", "late"]
N = 7

QUIRKS = {
    "walker": {
        "hint": "Her column: 'I do not take cabs. A kitchen worth finding is a kitchen worth walking to.'",
        "leak": "Volk walks: she only picks a kitchen within two doors of where she ate last night.",
    },
    "hype": {
        "hint": "Her column: 'Nothing sours a room like sudden applause.'",
        "leak": "Volk distrusts hype: any kitchen whose Buzz rose 4 or more since her last dinner is off her list.",
    },
    "noon": {
        "hint": "Her column: 'I book at noon, like a civilised person.'",
        "leak": "Volk books at noon: she judges Buzz as it stood at the end of lunch. Dinner pushes do not reach her.",
    },
}


def day_svc(t):
    t = max(1, min(21, t))
    return DAYS[(t - 1) // 3], SVCS[(t - 1) % 3]


class G(Game):
    name = "Hired Knives"
    turns = 21

    # ------------------------------------------------------------ setup
    def init_state(self, rng):
        ks = []
        for n in range(1, N + 1):
            ks.append({"n": n, "buzz": rng.d(5), "holder": "house", "cooks": 0, "stars": 0,
                       "star_by": None, "visited": False})
        mine = rng.choice([1, 2, 3, 5, 6, 7])
        ks[mine - 1]["holder"] = "you"
        ks[mine - 1]["cooks"] = 2
        ks[8 - mine - 1]["holder"] = "rooney"
        ks[8 - mine - 1]["cooks"] = 2
        pref = rng.shuffle(list(range(1, N + 1)))
        s = {
            "cash": 24,
            "spare": 2,
            "k": ks,
            "streak": 0,
            "comp_bonus": False,
            "leaked": False,
            "contract": None,
            "friday_done": False,
            "out": False,
            "lost": None,
            "news": [],
            "hidden": {
                "quirk": rng.choice(list(QUIRKS)),
                "pref": pref,
                "volk_last": None,
                "lunch_snapshot": {str(k["n"]): k["buzz"] for k in ks},
                "last_decision_buzz": {str(k["n"]): k["buzz"] for k in ks},
            },
        }
        s["seen"] = self._snapshot(s)
        s["pending"] = self._snapshot(s)
        return s

    def _snapshot(self, s):
        return [{"n": k["n"], "buzz": k["buzz"], "holder": k["holder"], "stars": k["stars"],
                 "visited": k["visited"]} for k in s["k"]]

    # ------------------------------------------------------------ helpers
    def _mine(self, s):
        return [k for k in s["k"] if k["holder"] == "you"]

    def _his(self, s):
        return [k for k in s["k"] if k["holder"] == "rooney"]

    def _cooks(self, s):
        return s["spare"] + sum(k["cooks"] for k in self._mine(s))

    def _seen(self, s, n):
        return s["seen"][n - 1]

    def _friday_target(self, s, board, live_buzz=False):
        """Kitchen Volk returns to on Friday: most stars, tie loudest, tie her secret order."""
        pref = s["hidden"]["pref"]

        def key(b):
            buzz = s["k"][b["n"] - 1]["buzz"] if live_buzz else b["buzz"]
            return (b["stars"], buzz, -pref.index(b["n"]))

        return max(board, key=key)["n"]

    def _default_take(self, s):
        house = [b for b in s["seen"] if b["holder"] == "house" and s["k"][b["n"] - 1]["holder"] != "you"]
        if not house:
            return None
        t = s["_turn"]
        if t >= 19:
            ft = self._friday_target(s, s["seen"])
            return ft if any(b["n"] == ft for b in house) else max(house, key=lambda b: (b["stars"], b["buzz"]))["n"]
        unv = [b for b in house if not b["visited"]] or house
        return max(unv, key=lambda b: (b["buzz"], -b["n"]))["n"]

    def _default_raid(self, s):
        his = [b for b in s["seen"] if b["holder"] == "rooney" and s["k"][b["n"] - 1]["holder"] != "you"]
        if not his:
            return None
        if s["_turn"] >= 19:
            return max(his, key=lambda b: (b["stars"], b["buzz"]))["n"]
        unv = [b for b in his if not b["visited"]] or his
        return max(unv, key=lambda b: (b["buzz"], b["stars"]))["n"]

    def _default_push(self, s):
        mine = self._mine(s)
        if s["_turn"] >= 19:
            return max(mine, key=lambda k: (k["stars"], k["buzz"]))["n"]
        unv = [k for k in mine if not k["visited"]] or mine
        return max(unv, key=lambda k: (k["buzz"], -k["n"]))["n"]

    def _default_reinforce(self, s):
        two = [k for k in self._mine(s) if k["cooks"] == 2]
        if s["_turn"] >= 19:
            return max(two, key=lambda k: (k["stars"], k["buzz"]))["n"]
        unv = [k for k in two if not k["visited"]] or two
        return max(unv, key=lambda k: (k["buzz"], -k["n"]))["n"]

    # ------------------------------------------------------------ options
    def options(self, s):
        t = s["_turn"]
        o = []
        if t == 21:
            bonus = 2 * self._cooks(s)
            if s["cash"] >= bonus:
                o.append({"id": "walkout", "label": f"Walk out the back with the contract, pay the crew {bonus} (2 per cook)"})
            o.append({"id": "stiff", "label": "Walk out without paying the crew (d6, need 5+, or they keep the knives and the contract)"})
            return o
        mine = self._mine(s)
        if s["streak"] >= 2 and s["cash"] >= 5 and mine:
            o.append({"id": "comp", "label": "Comp the room (5 cash): +3 Buzz at your loudest kitchen, next roll -1 need"})
        if t >= 11 and not s["leaked"] and s["cash"] >= 6:
            o.append({"id": "leak", "label": "Buy Volk's habit from her sub-editor (6 cash)"})
        # seen board drives what is offered; the live board drives what happens
        house_seen = [b for b in s["seen"] if b["holder"] == "house" and s["k"][b["n"] - 1]["holder"] != "you"]
        his_seen = [b for b in s["seen"] if b["holder"] == "rooney" and s["k"][b["n"] - 1]["holder"] != "you"]
        if house_seen and s["spare"] >= 2 and s["cash"] >= 8:
            n = self._default_take(s)
            o.append({"id": "take", "label": f"Take kitchen {n} from the house (8 cash, 2 spare cooks)", "args": {"k": n}})
        if his_seen and s["spare"] >= 2:
            n = self._default_raid(s)
            need = 4 if s["spare"] >= 3 else 5
            o.append({"id": "raid", "label": f"Raid Rooney's kitchen {n} (2 spare cooks, d6 need {need}+, fail loses a cook)", "args": {"k": n}})
        if mine and s["cash"] >= 4:
            n = self._default_push(s)
            o.append({"id": "push", "label": f"Push Buzz at kitchen {n} (+2, 4 cash)", "args": {"k": n}})
        if s["spare"] >= 1 and any(k["cooks"] == 2 for k in mine):
            n = self._default_reinforce(s)
            o.append({"id": "reinforce", "label": f"Reinforce kitchen {n} with a 3rd cook", "args": {"k": n}})
        if s["cash"] >= 6:
            o.append({"id": "hire", "label": "Hire a cook (6 cash, +1 spare)"})
        if len(o) < 3:
            o.append({"id": "hold", "label": "Hold the line, skim the tip jar (+1 cash)"})
        # cap at five, dropping the least urgent first
        for drop in ("hire", "raid" if t < 19 else "hire"):
            if len(o) > 5:
                o = [x for x in o if x["id"] != drop]
        return o[:5]

    # ------------------------------------------------------------ apply
    def _kitchen_arg(self, s, args, holder=None):
        try:
            n = int(args.get("k"))
        except (TypeError, ValueError):
            raise SystemExit('{"error": "need a kitchen number k from 1 to 7"}')
        if not 1 <= n <= N:
            raise SystemExit('{"error": "kitchen number must be 1 to 7"}')
        k = s["k"][n - 1]
        if holder and k["holder"] != holder:
            raise SystemExit(f'{{"error": "kitchen {n} is held by {k["holder"]}, not {holder}"}}')
        return k

    def apply(self, s, a, args, rng):
        ev = []
        if a == "take":
            k = self._kitchen_arg(s, args)
            if k["holder"] == "you":
                raise SystemExit('{"error": "you already hold that kitchen"}')
            if k["holder"] == "rooney":
                ev.append(f"You pulled up at kitchen {k['n']} to find Copper Pans vans already outside. The board was a service stale. Nothing spent, service wasted.")
                return ev
            s["cash"] -= 8
            s["spare"] -= 2
            k["holder"], k["cooks"] = "you", 2
            ev.append(f"Took kitchen {k['n']} from the house for 8. Two cooks on the line.")
        elif a == "raid":
            k = self._kitchen_arg(s, args)
            if k["holder"] == "you":
                raise SystemExit(f'{{"error": "kitchen {k["n"]} is already yours"}}')
            if k["holder"] == "house":
                ev.append(f"You kicked in the fire door of kitchen {k['n']} and found house staff and no Copper Pans. Nothing spent, service wasted.")
                return ev
            need = 4 if s["spare"] >= 3 else 5
            ok, txt = rng.check(need, label="raid")
            if ok:
                s["spare"] -= 2
                k["holder"], k["cooks"] = "you", 2
                s["streak"] = 0
                ev.append(f"Raid on kitchen {k['n']}: {txt}. The Copper Pans left by the fire door. It is yours.")
            else:
                s["spare"] -= 1
                s["streak"] += 1
                ev.append(f"Raid on kitchen {k['n']}: {txt}. One of your cooks walked off up the street with his knives. Cook -1.")
        elif a == "push":
            k = self._kitchen_arg(s, args, holder="you")
            s["cash"] -= 4
            k["buzz"] = min(9, k["buzz"] + 2)
            ev.append(f"Pushed kitchen {k['n']}: Buzz +2 (now {k['buzz']}; the board shows it next service). Cash -4.")
        elif a == "reinforce":
            k = self._kitchen_arg(s, args, holder="you")
            if k["cooks"] != 2 or s["spare"] < 1:
                raise SystemExit('{"error": "reinforce needs a 2-cook kitchen and a spare cook"}')
            s["spare"] -= 1
            k["cooks"] = 3
            ev.append(f"Kitchen {k['n']} reinforced: 3 cooks. Raids on it need 6, your rolls there need one less.")
        elif a == "hire":
            s["cash"] -= 6
            s["spare"] += 1
            ev.append("Hired a cook for 6. Spare cooks +1.")
        elif a == "hold":
            s["cash"] += 1
            ev.append("You held the line and skimmed the tip jar. Cash +1.")
        elif a == "comp":
            s["cash"] -= 5
            k = max(self._mine(s), key=lambda x: (x["buzz"], -x["n"]))
            k["buzz"] = min(9, k["buzz"] + 3)
            s["comp_bonus"] = True
            s["streak"] = 0
            ev.append(f"Comped the room at kitchen {k['n']}: Buzz +3 (now {k['buzz']}). Next service roll needs one less. Cash -5.")
        elif a == "leak":
            s["cash"] -= 6
            s["leaked"] = True
            ev.append("The sub-editor took 6 and talked. " + QUIRKS[s["hidden"]["quirk"]]["leak"])
        elif a == "walkout":
            bonus = 2 * self._cooks(s)
            s["cash"] -= bonus
            s["out"] = True
            ev.append(f"Paid the crew {bonus} and walked out the back with the Marrow & Co. contract.")
        elif a == "stiff":
            ok, txt = rng.check(5, label="loyalty")
            if ok:
                s["out"] = True
                ev.append(f"{txt}. The crew grumbled and followed you out. Contract in hand.")
            else:
                s["lost"] = "the crew kept the knives and the contract"
                ev.append(f"{txt}. The crew kept the knives, the contract, and the walk-in. You left with a coat.")
        else:
            raise SystemExit(f'{{"error": "unknown action {a}"}}')
        return ev

    # ------------------------------------------------------------ advance
    def advance(self, s, rng):
        ev = []
        cur = s["_turn"] - 1          # the service just played
        day, svc = day_svc(cur)
        # 1. news from the previous service arrives now
        ev += s["news"]
        news = []
        # 2. takings and wages
        held = len(self._mine(s))
        cooks = self._cooks(s)
        take = 4 * held
        s["cash"] += take - cooks
        ev.append(f"{day} {svc}: takings +{take}, wages -{cooks}.")
        if s["cash"] < 0:
            s["cash"] = 0
            ev.append(self._cook_walks(s))
        # 3. buzz drift
        for k in s["k"]:
            v = rng.d(6)
            if v == 1:
                k["buzz"] = max(0, k["buzz"] - 1)
            elif v == 6:
                k["buzz"] = min(9, k["buzz"] + 1)
        # 4. Rooney acts on the same stale board you see
        ev += self._rooney(s, cur, rng, news)
        # 5. Volk
        if svc == "lunch":
            s["hidden"]["lunch_snapshot"] = {str(k["n"]): k["buzz"] for k in s["k"]}
        elif svc == "dinner":
            if cur == 20:
                ev += self._friday(s, rng, news)
            else:
                ev += self._volk(s, rng, news)
        # 6. hints and milestones
        if cur in (3, 9) and not s["leaked"]:
            news.append(QUIRKS[s["hidden"]["quirk"]]["hint"])
        if cur == 11:
            ev.append("Wednesday. Rooney is pushing harder now and will raid a starred kitchen Thursday lunch; his raiders come out of his quietest kitchen, which the house takes back. Volk's sub-editor drinks at the Lamb if you have 6 to spare.")
        if cur == 18:
            ev.append("Friday. Tonight she goes back to the kitchen with the most stars. Whoever holds it at dinner cooks for the contract.")
        # 7. the board the player sees is one service stale
        s["seen"] = s["pending"]
        s["pending"] = self._snapshot(s)
        s["news"] = news
        return ev

    def _cook_walks(self, s):
        if s["spare"] > 0:
            s["spare"] -= 1
            return "Wages unpaid: a spare cook walked. Cook -1."
        mine = self._mine(s)
        if not mine:
            return "Wages unpaid, but there was nobody left to walk."
        k = max(mine, key=lambda x: (x["cooks"], -x["n"]))
        k["cooks"] -= 1
        if k["cooks"] < 2:
            k["holder"], k["cooks"] = "house", 0
            return f"Wages unpaid: a cook walked out of kitchen {k['n']} and the house took it back. Cook -1."
        return f"Wages unpaid: a cook walked out of kitchen {k['n']}. Cook -1."

    def _rooney(self, s, cur, rng, news):
        ev = []
        seen = s["seen"]
        his = self._his(s)
        his_n = {k["n"] for k in his}
        # Friday dinner: he is at the pass, shouting; no push
        if cur == 20:
            if his:
                k = max(his, key=lambda x: (x["stars"], x["buzz"]))
                news.append(f"Rooney spent Friday dinner at the pass in kitchen {k['n']}, shouting.")
            return ev
        # Friday lunch: he goes for the star kitchen
        if cur == 19:
            tgt = self._friday_target(s, seen)
            k = s["k"][tgt - 1]
            if k["holder"] == "house":
                k["holder"], k["cooks"] = "rooney", 2
                news.append(f"Copper Pans vans outside kitchen {tgt}: Rooney took it from the house.")
                return ev
            if k["holder"] == "you":
                return self._rooney_raid(s, k, rng, news)
            k["buzz"] = min(9, k["buzz"] + 2)
            news.append(f"Rooney pushed kitchen {tgt}: Buzz +2.")
            return ev
        # Thursday lunch: raid your best starred kitchen if it matches his best
        if cur == 16:
            his_best = max([k["stars"] for k in his] or [0])
            mine_starred = [k for k in self._mine(s) if k["stars"] >= 1 and k["stars"] >= his_best]
            if mine_starred:
                k = max(mine_starred, key=lambda x: (x["stars"], x["buzz"]))
                return self._rooney_raid(s, k, rng, news)
        # expand along the street
        if len(his) < 3:
            adj = [b for b in seen if b["holder"] == "house" and s["k"][b["n"] - 1]["holder"] == "house"
                   and any(abs(b["n"] - h) == 1 for h in his_n)]
            if adj:
                unv = [b for b in adj if not b["visited"]] or adj
                b = max(unv, key=lambda x: (x["buzz"], x["n"]))
                k = s["k"][b["n"] - 1]
                k["holder"], k["cooks"] = "rooney", 2
                news.append(f"Copper Pans vans outside kitchen {k['n']}: Rooney took it from the house.")
                return ev
        # push: +1 a service, +2 from Wednesday
        if his:
            unv = [k for k in his if not k["visited"]]
            k = max(unv, key=lambda x: (x["buzz"], x["n"])) if (unv and cur < 19) else max(his, key=lambda x: (x["stars"], x["buzz"]))
            amt = 2 if cur >= 11 else 1
            k["buzz"] = min(9, k["buzz"] + amt)
            news.append(f"Rooney pushed kitchen {k['n']}: Buzz +{amt}.")
        return ev

    def _rooney_raid(self, s, k, rng, news):
        need = 6 if k["cooks"] == 3 else 5
        ok, txt = rng.check(need, label="Rooney raid")
        if ok:
            s["spare"] += k["cooks"]
            k["holder"], k["cooks"] = "rooney", 2
            others = [x for x in self._his(s) if x["n"] != k["n"]]
            extra = ""
            if others:
                q = min(others, key=lambda x: (x["stars"], x["buzz"], -x["n"]))
                q["holder"], q["cooks"] = "house", 0
                extra = f" His raiders came from kitchen {q['n']}, which the house has taken back."
            return [f"Copper Pans came through the fire door of kitchen {k['n']}: {txt}. Your cooks are out on the pavement (back in spare).{extra}"]
        return [f"Copper Pans tried the fire door of kitchen {k['n']}: {txt}. They left."]

    def _volk(self, s, rng, news):
        ev = []
        h = s["hidden"]
        q = h["quirk"]
        cands = [k for k in s["k"] if not k["visited"]]
        if q == "walker" and h["volk_last"]:
            near = [k for k in cands if abs(k["n"] - h["volk_last"]) <= 2]
            cands = near or cands
        if q == "hype":
            calm = [k for k in cands if k["buzz"] - h["last_decision_buzz"][str(k["n"])] < 4]
            cands = calm or cands
        pref = h["pref"]

        def val(k):
            return h["lunch_snapshot"][str(k["n"])] if q == "noon" else k["buzz"]

        k = max(cands, key=lambda x: (val(x), -pref.index(x["n"])))
        k["visited"] = True
        h["volk_last"] = k["n"]
        if k["holder"] == "you":
            need = 4 - (1 if k["cooks"] == 3 else 0) - (1 if s["comp_bonus"] else 0)
            need = max(2, need)
            s["comp_bonus"] = False
            ok, txt = rng.check(need, label="service")
            raw = int(txt.split()[1])
            if ok:
                k["stars"] = 2 if raw == 6 else 1
                k["star_by"] = "you"
                s["cash"] += 6
                s["streak"] = 0
                ev.append(f"A woman with a notebook took table 9 at kitchen {k['n']}. {txt}. "
                          f"{'She asked for the chef. Two stars.' if raw == 6 else 'She sent nothing back. One star.'} Cash +6.")
            else:
                k["buzz"] = max(0, k["buzz"] - 2)
                s["streak"] += 1
                ev.append(f"A woman with a notebook took table 9 at kitchen {k['n']}. {txt}. She left before dessert. Buzz -2.")
            news.append(f"Volk's column: she ate at kitchen {k['n']} (yours).")
        elif k["holder"] == "rooney":
            ok, txt = rng.check(5, label="Rooney service")
            if ok:
                k["stars"] = 1
                k["star_by"] = "rooney"
                news.append(f"Volk's column: she ate at kitchen {k['n']} (Rooney's). {txt}. One star. 'Fine. Nobody writes home about fine.'")
            else:
                k["buzz"] = max(0, k["buzz"] - 2)
                news.append(f"Volk's column: she ate at kitchen {k['n']} (Rooney's). {txt}. No star.")
        else:
            ok, txt = rng.check(5, label="house service")
            if ok:
                k["stars"] = 1
                k["star_by"] = "house"
                news.append(f"Volk's column: she ate at kitchen {k['n']} (house staff). {txt}. One star.")
            else:
                k["buzz"] = max(0, k["buzz"] - 2)
                news.append(f"Volk's column: she ate at kitchen {k['n']} (house staff). {txt}. No star.")
        h["last_decision_buzz"] = {str(x["n"]): x["buzz"] for x in s["k"]}
        return ev

    def _friday(self, s, rng, news):
        ev = []
        tgt = self._friday_target(s, self._snapshot(s), live_buzz=True)
        k = s["k"][tgt - 1]
        s["friday_done"] = True
        if k["holder"] == "you":
            need = 4 - (1 if k["star_by"] == "you" else 0) - (1 if k["cooks"] == 3 else 0) - (1 if s["comp_bonus"] else 0)
            need = max(2, need)
            ok, txt = rng.check(need, label="Friday service")
            if ok:
                s["contract"] = "you"
                ev.append(f"Friday dinner. Volk walked into kitchen {tgt}. {txt}. She put the notebook away. The contract is yours if you can get out.")
            else:
                s["contract"] = "none"
                ev.append(f"Friday dinner. Volk walked into kitchen {tgt}. {txt}. She wrote four hundred words about your fish.")
        elif k["holder"] == "rooney":
            ok, txt = rng.check(5, label="Rooney Friday service")
            s["contract"] = "rooney" if ok else "none"
            ev.append(f"Friday dinner. Volk walked into kitchen {tgt}, Rooney's. {txt}.")
        else:
            s["contract"] = "none"
            ev.append(f"Friday dinner. Volk walked into kitchen {tgt} and ate with the house staff.")
        return ev

    # ------------------------------------------------------------ view
    def status_line(self, s):
        day, svc = day_svc(s["_turn"])
        mine = self._mine(s)
        hold = " ".join(f"{k['n']}({k['cooks']}{'*' * k['stars']})" for k in mine) or "none"
        return f"{day} {svc} | Cash {s['cash']} | Cooks {s['spare']} spare of {self._cooks(s)} | Hold {hold}"

    def visible(self, s):
        return {
            "service": " ".join(day_svc(s["_turn"])),
            "cash": s["cash"],
            "spare_cooks": s["spare"],
            "your_kitchens": [{"n": k["n"], "cooks": k["cooks"], "stars": k["stars"], "visited": k["visited"]} for k in self._mine(s)],
            "board_as_of_last_service": [
                f"K{b['n']} buzz {b['buzz']} {b['holder']}{' ' + '*' * b['stars'] if b['stars'] else ''}{' (visited)' if b['visited'] else ''}"
                for b in s["seen"]
            ],
            "streak": s["streak"],
            "habit_known": s["leaked"],
        }

    def check_end(self, s):
        if s.get("lost"):
            return {"result": "loss", "reason": s["lost"]}
        if s.get("out"):
            return {"result": "win", "reason": f"walked out with the contract and {s['cash']} cash"}
        if s.get("friday_done") and s.get("contract") != "you":
            if s["contract"] == "rooney":
                return {"result": "loss", "reason": "Rooney fed Volk on Friday and took the contract"}
            return {"result": "loss", "reason": "Volk went home unimpressed; no contract"}
        return None

    # ------------------------------------------------------------ heuristic
    def heuristic(self, s, options, rng):
        ids = {o["id"]: o for o in options}
        t = s["_turn"]
        if "walkout" in ids:
            return "walkout"
        if "stiff" in ids:
            return "stiff"
        mine = self._mine(s)
        cooks = self._cooks(s)
        reserve = cooks + 2 + (2 * cooks if t >= 16 else 0)
        cash = s["cash"]
        seen = s["seen"]

        def pick(aid, n=None):
            o = ids[aid]
            return {"id": aid, "args": {"k": n} if n else o.get("args", {})}

        if t >= 19:
            tgt = self._friday_target(s, seen)
            k = s["k"][tgt - 1]
            if k["holder"] == "you":
                if k["cooks"] == 2 and "reinforce" in ids:
                    return pick("reinforce", tgt)
                if k["cooks"] == 2 and "hire" in ids and cash - 6 >= 2 * (cooks + 1):
                    return "hire"
                if "push" in ids and cash - 4 >= 2 * cooks:
                    return pick("push", tgt)
            elif seen[tgt - 1]["holder"] == "house" and "take" in ids:
                return pick("take", tgt)
            elif seen[tgt - 1]["holder"] == "rooney" and "raid" in ids:
                return pick("raid", tgt)
            elif "hire" in ids and s["spare"] < 2 and cash >= 16:
                return "hire"
            if "push" in ids and mine and cash >= 4 + reserve:
                return pick("push", max(mine, key=lambda x: (x["stars"], x["buzz"]))["n"])
            return "hold" if "hold" in ids else rng.choice(options)["id"]

        if "comp" in ids:
            return "comp"
        if 14 <= t <= 18:
            tgt = self._friday_target(s, seen)
            if s["k"][tgt - 1]["holder"] != "you" and s["spare"] < 2 and "hire" in ids and cash - 6 >= 8 + 2 * (cooks + 1):
                return "hire"
        if 13 <= t <= 18:
            starred2 = [k for k in mine if k["stars"] >= 1 and k["cooks"] == 2]
            if starred2:
                best = max(starred2, key=lambda k: (k["stars"], k["buzz"]))
                if "reinforce" in ids:
                    return pick("reinforce", best["n"])
                if "hire" in ids and cash >= 6 + reserve:
                    return "hire"
        if "leak" in ids and cash >= 6 + reserve + 6:
            return "leak"
        unv_mine = [k for k in mine if not k["visited"]]
        others_unv = [b for b in seen if b["holder"] != "you" and not b["visited"]]
        top_other = max([b["buzz"] for b in others_unv] or [0])
        house_unv = [b for b in seen if b["holder"] == "house" and not b["visited"]]
        if (not unv_mine or len(mine) < 2) and "take" in ids and cash >= 8 + reserve and house_unv:
            best = max(house_unv, key=lambda b: (b["buzz"], -b["n"]))
            return pick("take", best["n"])
        if (not unv_mine or len(mine) < 2) and "hire" in ids and s["spare"] < 2 and cash >= 8 + reserve + 6 and house_unv:
            return "hire"
        if unv_mine:
            best = max(unv_mine, key=lambda k: (k["buzz"], -k["n"]))
            if best["buzz"] >= top_other and best["cooks"] == 2 and "reinforce" in ids:
                return pick("reinforce", best["n"])
            if best["buzz"] <= top_other and "push" in ids and cash >= 4 + reserve:
                return pick("push", best["n"])
        if "hire" in ids and cash >= 6 + reserve + 6 and s["spare"] < 2 and len(mine) < 3:
            return "hire"
        if "push" in ids and cash >= 4 + reserve + 4 and unv_mine:
            return pick("push", max(unv_mine, key=lambda k: (k["buzz"], -k["n"]))["n"])
        if "hold" in ids:
            return "hold"
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
