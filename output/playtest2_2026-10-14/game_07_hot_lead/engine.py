"""Hot Lead: a 1928 city desk, four stringers, one of them a liar.

Rolls: FORM=11 breeding (cross two leads, inspect the draft, keep or spike),
SET=35 a 1920s newspaper, ROLE=13 spymaster (the city editor runs a ring of stringers),
LOOP=24 negotiate, bluff, or fight each encounter (pay / bluff / lean on the stringer),
CLOCK=10 unrest rises when ignored (newsroom unrest climbs on days nothing prints),
TWIST=41 one NPC always lies (one stringer; any story using their lead is false),
WIN=11 map the whole board (all 7 nodes of the crime bracket),
MAP=12 a bracket (4 rackets -> 2 lieutenants -> the Boss), TONE=9 workplace comedy.

Rulesheet (8 lines):
1. Each day one stringer brings a lead on an open node. Pay (5/7/9 cash by tier), bluff (roll 4+; 3+ if they are cleared), or lean (free and sure, but they sulk 4 days and bring nothing).
2. Cross two leads on the same node from different stringers into a draft. The fact-checker rolls 3+ (2+ if one source is cleared, no roll if both are) to call it solid or shaky; a miss is unclear.
3. Solid drafts go to press next day. Shaky drafts are burned on the spot. Unclear drafts go to press next day unless you spike them, which returns the leads.
4. True story: node mapped, +8 cash, Unrest -4, both stringers cleared. False: retraction, -6 cash, Unrest +3, and one of the two is your liar.
5. One of your four stringers always lies; any story with their lead is false. Prove who and they are fired.
6. From day 4, Unrest +1 each day nothing prints. Unrest 12 and the newsroom walks out.
7. Mapping both rackets under a lieutenant opens him; both lieutenants open the Boss; leads left on a mapped node point up at the man above. Kessler at the Bugle hunts Docks, Hooch, Numbers, Union, Cronin, Pike in that order: his scoop maps the node for Unrest +1, but he waits while you hold a draft on it; beat him to it for +4 cash. Only you can map the Boss.
8. Any day with no draft waiting you may run the gossip column instead: Unrest -2, +3 cash, counts as printing. Two failed rolls in a row open the morgue for a free, always-honest archive lead; from day 13 (election week: Kessler prints on 3+, leads cost 2 more) the morgue is open every day. Win: all 7 mapped by day 24.
"""

import os
import sys

sys.path.insert(0, r"C:\Users\Brian.Rankin\claude-workspace\projects\GM\engine")
from gm_base import Game, run  # noqa: E402

STRINGERS = ["Ox", "Fitz", "Mabel", "Lou"]
NODES = ["Docks", "Hooch", "Numbers", "Union", "Cronin", "Pike", "Gray"]
TIER = {"Docks": 1, "Hooch": 1, "Numbers": 1, "Union": 1, "Cronin": 2, "Pike": 2, "Gray": 3}
NEEDS = {"Cronin": ["Docks", "Hooch"], "Pike": ["Numbers", "Union"], "Gray": ["Cronin", "Pike"]}
LABEL = {"Docks": "the Docks racket", "Hooch": "the Hooch racket", "Numbers": "the Numbers racket",
         "Union": "the Union racket", "Cronin": "Big Eddie Cronin", "Pike": "Alderman Pike", "Gray": "Mr. Gray"}
COST = {1: 5, 2: 7, 3: 9}
KESSLER_ORDER = ["Docks", "Hooch", "Numbers", "Union", "Cronin", "Pike"]
MID = 13
UNREST_MAX = 12


class G(Game):
    name = "Hot Lead"
    turns = 24

    # ------------------------------------------------------------ helpers
    def is_open(self, s, node):
        if node in s["mapped"]:
            return False
        return all(n in s["mapped"] for n in NEEDS.get(node, []))

    def frontier(self, s):
        return [n for n in NODES if self.is_open(s, n)]

    def has_lead(self, s, node, src):
        return any(l["node"] == node and l["src"] == src for l in s["leads"])

    def honest(self, s, src):
        return src != s["hidden"]["liar"]

    def pick_visitor(self, s, rng):
        """A stringer who is free comes by with a lead on the node the desk is already working:
        the open node with the most leads from other sources; Kessler's target breaks ties."""
        whos = [w for w in STRINGERS if w != s["fired"] and s["sore"].get(w, 0) <= 0]
        rng.shuffle(whos)
        kt = s["kessler"]["target"]
        for who in whos:
            nodes = [n for n in self.frontier(s) if not self.has_lead(s, n, who)]
            if not nodes:
                continue
            def key(n):
                others = sum(1 for l in s["leads"] if l["node"] == n and l["src"] != who)
                return (others, 0 if n == kt else 1, -TIER[n])
            nodes.sort(key=key, reverse=True)
            top = [n for n in nodes if key(n) == key(nodes[0])]
            node = rng.choice(top)
            cost = COST[TIER[node]] + (2 if s["_turn"] >= MID else 0)
            s["visitor"] = {"who": who, "node": node, "cost": cost}
            return
        s["visitor"] = None

    def fire(self, s, who, ev):
        if s["fired"]:
            return
        s["fired"] = who
        s["leads"] = [l for l in s["leads"] if l["src"] != who]
        s["suspects"] = [x for x in s["suspects"] if x != who]
        if s["visitor"] and s["visitor"]["who"] == who:
            s["visitor"] = None
        ev.append(f"{who} is your liar. Fired on the spot; every lead of theirs goes in the bin.")

    def clear(self, s, src, ev):
        if src == "Morgue" or src in s["cleared"]:
            return
        s["cleared"].append(src)
        ev.append(f"{src} is cleared.")
        self.deduce(s, ev)

    def note_pair(self, s, x, y):
        """Record that the liar is one of x/y (Morgue never lies)."""
        pr = sorted(z for z in (x, y) if z != "Morgue")
        s.setdefault("pairs", [])
        if pr not in s["pairs"]:
            s["pairs"].append(pr)

    def deduce(self, s, ev):
        """Candidates = uncleared stringers inside every known liar pair. One left means proof."""
        if s["fired"]:
            s["suspects"] = []
            return
        cands = [w for w in STRINGERS if w not in s["cleared"]]
        pairs = s.get("pairs", [])
        for pr in pairs:
            cands = [w for w in cands if w in pr]
        s["suspects"] = cands if pairs else []
        if len(cands) == 1:
            ev.append("That narrows it to one.")
            self.fire(s, cands[0], ev)

    def drop_leads(self, s, node, ev=None):
        """Leads on a node that just got mapped point up at the man above it (none above Gray)."""
        parent = next((p for p, kids in NEEDS.items() if node in kids), None)
        moved = []
        kept = []
        for l in s["leads"]:
            if l["node"] != node:
                kept.append(l)
            elif parent and not any(k["node"] == parent and k["src"] == l["src"] for k in kept + moved):
                moved.append({"node": parent, "src": l["src"]})
        s["leads"] = kept + moved
        if moved and ev is not None:
            ev.append(f"{', '.join(m['src'] for m in moved)} now point{'s' if len(moved) == 1 else ''} up at {LABEL[parent]}.")

    def morgue_target(self, s):
        best = None
        for node in self.frontier(s):
            if self.has_lead(s, node, "Morgue"):
                continue
            n = sum(1 for l in s["leads"] if l["node"] == node)
            if n == 1:
                return node
            if best is None:
                best = node
        return best

    # ------------------------------------------------------------ contract
    def init_state(self, rng):
        s = {
            "cash": 20,
            "unrest": 1,
            "mapped": {},
            "leads": [],
            "cleared": [],
            "suspects": [],
            "pairs": [],
            "fired": None,
            "sore": {},
            "draft": None,
            "visitor": None,
            "kessler": {"target": None, "rest": 0, "done": []},
            "streak": 0,
            "printed": False,
            "hidden": {"liar": rng.choice(STRINGERS)},
        }
        s["_turn"] = 1
        self.pick_visitor(s, rng)
        return s

    def options(self, s):
        o = []
        d = s["draft"]
        if d and d["result"] == "unclear":
            o.append({"id": "spike", "label": f"Spike the unclear {d['node']} draft (leads return to the desk)"})
        v = s["visitor"]
        if v and v["who"] != s["fired"]:
            who, node, cost = v["who"], v["node"], v["cost"]
            if s["cash"] >= cost:
                o.append({"id": "pay", "label": f"Pay {who} {cost} cash for the {node} lead"})
            need = 3 if who in s["cleared"] else 4
            o.append({"id": "bluff", "label": f"Bluff {who} (roll {need}+) for the {node} lead"})
            o.append({"id": "lean", "label": f"Lean on {who}: sure lead, free, but {who} sulks 4 days"})
        if not d:
            crosses = []
            for node in self.frontier(s):
                srcs = [l["src"] for l in s["leads"] if l["node"] == node]
                for i in range(len(srcs)):
                    for j in range(i + 1, len(srcs)):
                        a, b = srcs[i], srcs[j]
                        score = sum(1 for x in (a, b) if x in s["cleared"] or x == "Morgue")
                        score -= sum(1 for x in (a, b) if x in s["suspects"])
                        crosses.append((score, node, a, b))
            crosses.sort(key=lambda t: -t[0])
            for score, node, a, b in crosses[:2]:
                o.append({"id": f"cross-{node}-{a}-{b}".lower(),
                          "label": f"Cross {a} + {b} on {node} into a draft",
                          "args": {"node": node, "a": a, "b": b}})
        if s["streak"] >= 2 or s["_turn"] >= MID:
            tgt = self.morgue_target(s)
            if tgt:
                o.append({"id": "morgue", "label": f"Hit the morgue: free archive lead on {tgt}",
                          "args": {"node": tgt}})
        if not d and s["unrest"] >= 2:
            o.append({"id": "gossip", "label": "Run the gossip column (Unrest -2, +3 cash)"})
        if not o:
            o.append({"id": "phones", "label": "Work the phones (nothing bites)"})
        return o

    def apply(self, s, a, args, rng):
        ev = []
        s["printed"] = False
        v = s["visitor"]
        if a in ("pay", "bluff", "lean"):
            who, node, cost = v["who"], v["node"], v["cost"]
            if a == "pay":
                s["cash"] -= cost
                s["leads"].append({"node": node, "src": who})
                s["streak"] = 0
                ev.append(f"Paid {who} {cost}. Lead on {node} filed.")
            elif a == "bluff":
                need = 3 if who in s["cleared"] else 4
                ok, txt = rng.check(need, label="bluff")
                if ok:
                    s["leads"].append({"node": node, "src": who})
                    s["streak"] = 0
                    ev.append(f"{txt}. {who} buys it and spills. Lead on {node} filed for free.")
                else:
                    s["streak"] += 1
                    ev.append(f"{txt}. {who} sees through you and leaves with the lead.")
            else:
                s["leads"].append({"node": node, "src": who})
                s["sore"][who] = 4
                s["streak"] = 0
                ev.append(f"You lean on {who}. Lead on {node} filed. {who} sulks for 4 days.")
            s["visitor"] = None
        elif a.startswith("cross"):
            node, x, y = args["node"], args["a"], args["b"]
            s["leads"] = [l for l in s["leads"] if not (l["node"] == node and l["src"] in (x, y))]
            truth = self.honest(s, x) and self.honest(s, y)
            known = [z for z in (x, y) if z in s["cleared"] or z == "Morgue"]
            if len(known) == 2:
                res, txt = "solid", "no roll needed, both sources cleared"
            else:
                need = 2 if len(known) == 1 else 3
                ok, txt = rng.check(need, label="fact-check")
                res = ("solid" if truth else "shaky") if ok else "unclear"
            if res == "unclear":
                s["streak"] += 1
            else:
                s["streak"] = 0
            ev.append(f"Draft on {node} from {x} + {y}. Fact-check: {txt}. Verdict: {res}.")
            if res == "shaky":
                ev.append(f"The checker kills it. One of {x}/{y} is your liar. Both leads burned.")
                self.note_pair(s, x, y)
                self.deduce(s, ev)
                s["draft"] = None
            else:
                s["draft"] = {"node": node, "a": x, "b": y, "result": res, "made": s["_turn"]}
                if res == "solid":
                    ev.append("It goes to press tomorrow.")
                else:
                    ev.append("It goes to press tomorrow unless you spike it.")
        elif a == "spike":
            d = s["draft"]
            s["leads"].append({"node": d["node"], "src": d["a"]})
            s["leads"].append({"node": d["node"], "src": d["b"]})
            s["draft"] = None
            ev.append(f"Spiked the {d['node']} draft. Both leads back on the desk.")
        elif a == "morgue":
            node = args["node"]
            s["leads"].append({"node": node, "src": "Morgue"})
            s["streak"] = 0
            ev.append(f"Archive clipping on {node} filed. The morgue never lies.")
        elif a == "gossip":
            s["unrest"] = max(0, s["unrest"] - 2)
            s["cash"] += 3
            s["printed"] = True
            ev.append("Mabel's gossip column runs. Unrest -2, cash +3.")
        elif a == "phones":
            ev.append("Nothing bites.")
        return ev

    def press(self, s, ev):
        d = s["draft"]
        s["draft"] = None
        node, x, y = d["node"], d["a"], d["b"]
        truth = self.honest(s, x) and self.honest(s, y)
        if truth:
            s["mapped"][node] = "Clarion"
            s["cash"] += 8
            s["unrest"] = max(0, s["unrest"] - 4)
            ev.append(f"PRESS: {LABEL[node]} exposed on page one. Cash +8, Unrest -4.")
            self.clear(s, x, ev)
            self.clear(s, y, ev)
            k = s["kessler"]
            if k["target"] == node:
                s["cash"] += 4
                k["target"] = None
                k["rest"] = 3
                ev.append("You beat Kessler to it. Cash +4. The Bugle licks its wounds.")
            self.drop_leads(s, node, ev)
            for n in NEEDS:
                if self.is_open(s, n) and node in NEEDS[n]:
                    ev.append(f"{LABEL[n]} is now in play.")
        else:
            s["cash"] = max(0, s["cash"] - 6)
            s["unrest"] += 3
            ev.append(f"PRESS: the {node} story falls apart by noon. Retraction. Cash -6, Unrest +3. One of {x}/{y} fed you a fake.")
            self.note_pair(s, x, y)
            self.deduce(s, ev)
        s["printed"] = True

    def advance(self, s, rng):
        ev = []
        day = s["_turn"] - 1  # the day that just ended
        d = s["draft"]
        if d and d["made"] < day:
            self.press(s, ev)
        if not s["printed"] and day >= 4:
            s["unrest"] += 1
            ev.append("Nothing printed. Unrest +1.")
        s["printed"] = False
        # Kessler
        k = s["kessler"]
        if day >= 3:
            if k["rest"] > 0:
                k["rest"] -= 1
            elif k["target"] is None:
                for n in KESSLER_ORDER:
                    if self.is_open(s, n) and n not in k["done"]:
                        k["target"] = n
                        break
                if k["target"]:
                    ev.append(f"Kessler's boys are asking around about {LABEL[k['target']]}.")
            else:
                t = k["target"]
                if not self.is_open(s, t):
                    k["target"] = None
                elif s["draft"] and s["draft"]["node"] == t:
                    ev.append(f"Kessler's boys hear your presses warming up on {LABEL[t]}. He waits.")
                else:
                    need = 3 if day >= MID else 5
                    ok, txt = rng.check(need, label="Bugle")
                    if ok:
                        s["mapped"][t] = "Bugle"
                        s["unrest"] += 1
                        k["done"].append(t)
                        k["target"] = None
                        k["rest"] = 3
                        ev.append(f"{txt}. The Bugle runs {LABEL[t]} first. It counts on the map, but Unrest +1.")
                        self.drop_leads(s, t, ev)
                        for n in NEEDS:
                            if self.is_open(s, n) and t in NEEDS[n]:
                                ev.append(f"{LABEL[n]} is now in play.")
                    else:
                        ev.append(f"{txt}. Kessler is still sniffing around {LABEL[t]}.")
        for who in list(s["sore"]):
            if s["sore"][who] > 0:
                s["sore"][who] -= 1
        if s["_turn"] == MID:
            ev.append("Day 13: election week. Kessler prints on 3+, every palm costs 2 more, and the morgue is open every day.")
        self.pick_visitor(s, rng)
        v = s["visitor"]
        if v:
            tag = " (cleared)" if v["who"] in s["cleared"] else (" (suspect)" if v["who"] in s["suspects"] else "")
            ev.append(f"{v['who']}{tag} is at your desk with something on {v['node']}.")
        return ev

    def status_line(self, s):
        return f"Cash {s['cash']} | Unrest {s['unrest']}/12 | Mapped {len(s['mapped'])}/7 | Leads {len(s['leads'])}"

    def check_end(self, s):
        if s["unrest"] >= UNREST_MAX:
            return {"result": "loss", "reason": f"unrest {s['unrest']}: the newsroom walked out"}
        if len(s["mapped"]) >= 7:
            return {"result": "win", "reason": f"all 7 mapped, Mr. Gray on page one, day {s['_turn']}"}
        if s["_turn"] > self.turns:
            return {"result": "loss", "reason": f"day 24 passed with {len(s['mapped'])}/7 mapped"}
        return None

    def heuristic(self, s, options, rng):
        ids = {o["id"]: o for o in options}
        d = s["draft"]
        if d and d["result"] == "unclear" and "spike" in ids:
            unknown = [z for z in (d["a"], d["b"]) if z not in s["cleared"] and z != "Morgue"]
            pool = [x for x in STRINGERS if x not in s["cleared"] and x != s["fired"]]
            if s["fired"]:
                p = 0.0
            else:
                p = len(unknown) / len(pool) if pool else 0.0
            if p >= 0.5:
                return "spike"
        if "morgue" in ids:
            return "morgue"
        crosses = [o for o in options if o["id"].startswith("cross")]
        if crosses:
            return crosses[0]["id"]
        if "gossip" in ids and s["unrest"] >= 9:
            return "gossip"
        v = s["visitor"]
        if v and ("pay" in ids or "bluff" in ids):
            who, cost = v["who"], v["cost"]
            if who in s["suspects"] and s["fired"] is None:
                return "bluff"
            if s["unrest"] >= 9:
                if "pay" in ids:
                    return "pay"
                if who in s["cleared"]:
                    return "bluff"
                return "lean"
            if "pay" in ids and s["cash"] >= cost + 6:
                return "pay"
            free = sum(1 for w in STRINGERS if w != s["fired"] and s["sore"].get(w, 0) <= 0)
            if s["cash"] < cost + 6 and free >= 3 and who not in s["suspects"]:
                return "lean"
            return "bluff"
        if "gossip" in ids:
            return "gossip"
        return rng.choice(options)["id"]


if __name__ == "__main__":
    run(G)
