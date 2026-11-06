"""
gm_checks: the universal bug checks every generated game must pass.

gm_base._check calls run_universal() and run_rule_tests(). gm_base._turn_json calls integrity() on every
turn so a bug that slips through is reported to the GM at play time instead of being narrated over.

What is caught here, with no per-game code (a game may add BOUNDS, REACH, GATES, DERIVED and TRACKED for more):
    state that does not survive a JSON round trip (sets, tuples, int keys), NaN, runaway numbers
    stale, unformatted or wrongly pluralized text in events, option labels and the status line
    a status line that changes shape between turns, or has more than 4 fields
    hidden state leaking through visible()
    a numeric value outside BOUNDS; a value that never reaches a REACH target (a clamp bug)
    an action missing while its GATES say it is affordable, or offered while they say it is not
    a check_end that ends the game before the last action is played
    a crash at the observed minimum or maximum of any numeric state key (fuzz)
    nondeterminism: a different trace for the same seed, in process or across hash seeds
    more than 3 tracked numbers, a rule line that is too long
    a feeling priced like goods in the sheet, a label or an event ("buy 2 Morale"): SENSE
    warnings: a menu number that needs two answers (MOVE), a status line with more than 5 numbers (STATUS)

Rule tests (the executable spec) are written per game as Game.rule_tests(); see class T.
"""

import contextlib
import copy
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys

HARD_LINTS = [
    (re.compile(r"\bNone\b"), "contains 'None'"),
    (re.compile(r"\bnan\b|\binf\b", re.I), "contains nan or inf"),
    (re.compile(r"[{}]"), "contains an unformatted brace"),
    (re.compile(r"%[sdif]\b"), "contains an unformatted % field"),
    (re.compile(r"\bundefined\b|\bTODO\b|\bFIXME\b|\bXXX\b", re.I), "contains a placeholder word"),
    (re.compile(r"\+-|-\+|\+\+|(?<![\w)])--\d"), "has a doubled sign"),
]
SOFT_LINTS = [
    (re.compile(r"\b([A-Za-z]{3,}) \1\b", re.I), "repeats a word"),
]

# words that can follow a lone "1" without being a wrongly pluralized noun
_NOT_PLURAL = set(
    "is has was does holds shows burns sits goes stays wins loses lights costs gains takes makes gives needs counts adds "
    "drops rises falls works pays moves gets lets means plus minus times yes always less news series species status "
    "bonus focus lens gas boss class glass chorus campus virus kiss mess press loss cross across towards".split()
)
_LABELS = set("lantern slot layer night turn day round step tile square district node bus line row column number no item stop wave week table deck bay desk room level stage phase rule page seat site lot sector zone ring hex lane gate door floor ward".split())
_ADJ = set("lit dark last more other extra new spare free left remaining unlit good bad small big full empty open closed".split())


def plural(n, noun, many=None):
    """'1 night', '2 nights'. Use it for every count that appears in text. A multi-word noun pluralizes its last word."""
    if n == 1:
        return f"1 {noun}"
    if many is None:
        words = noun.split(" ")
        w = words[-1]
        if re.search(r"(s|x|z|ch|sh)$", w):
            w += "es"
        elif re.search(r"[^aeiou]y$", w):
            w = w[:-1] + "ies"
        else:
            w += "s"
        many = " ".join(words[:-1] + [w])
    return f"{n} {many}"


def _plural_looking(w):
    return len(w) >= 4 and w.endswith("s") and not w.endswith(("ss", "us", "is")) and w.lower() not in _NOT_PLURAL


def plural_problems(text):
    out = []
    for m in re.finditer(r"(?<![\w.,/:+-])1 ([A-Za-z]+)(?: ([A-Za-z]+))?", text):
        before = re.search(r"([A-Za-z]+) $", text[: m.start()])
        if before and ((before.group(1)[0].isupper() and len(before.group(1)) >= 3) or before.group(1).lower() in _LABELS):
            continue  # a label such as "Lantern 1 lit" or "night 1 holds"
        w1, w2 = m.group(1), m.group(2)
        if _plural_looking(w1):
            out.append(f"has the wrong plural after a count of 1 ('1 {w1}'); use plural(n, noun)")
        elif w2 and w1.lower() in _ADJ and _plural_looking(w2):
            out.append(f"has the wrong plural after a count of 1 ('1 {w1} {w2}'); use plural(n, noun)")
    return out


def text_problems(text, soft=False):
    """Problems in one piece of player-facing text."""
    if not isinstance(text, str):
        return [f"is not text ({type(text).__name__})"]
    if not text.strip():
        return ["is empty"]
    out = [msg for rx, msg in HARD_LINTS if rx.search(text)]
    out += plural_problems(text)
    if soft:
        out += [msg for rx, msg in SOFT_LINTS if rx.search(text)]
    return out


# A feeling or a standing is not goods. Nobody tells a shopkeeper "I'll buy a morale for 5 Light". Actions change
# these numbers as a consequence (feeding the crew raises morale, a bribe lowers suspicion); they are never bought,
# sold or priced. Words that are also physical things (heat, standing, attention) are left out on purpose.
_ABSTRACT = frozenset(
    "morale trust nerve sanity courage composure goodwill loyalty confidence happiness mood patience suspicion".split()
)
_MARKET = frozenset(
    "buy buys buying bought sell sells selling sold purchase purchases purchasing price prices priced exchange exchanges exchanging".split()
)
_PAY_FOR = re.compile(
    r"\b(?:pay|pays|paying|paid|spend|spends|spending|spent|swap|swaps|swapping|trade|trades|trading)\b[^.;()]{0,50}?\bfor\b[^.;()]{0,25}?\b(?:%s)\b"
    % "|".join(sorted(_ABSTRACT)),
    re.I,
)


def sense_problems(text):
    """Player-facing text that prices a feeling like goods ('buy 2 Morale', 'sell it at that rate in Light')."""
    if not isinstance(text, str):
        return []
    words = re.findall(r"[a-z']+", text.lower())
    for i, w in enumerate(words):
        if w in _MARKET:
            hit = next((x for x in words[max(0, i - 5): i + 6] if x in _ABSTRACT), None)
            if hit:
                return [f"treats {hit} as goods ('{w}' next to '{hit}'); a feeling is changed by what the character does, never bought, sold or priced"]
    m = _PAY_FOR.search(text)
    if m:
        return [f"treats a feeling as goods ({m.group(0)!r}); a feeling is changed by what the character does, never bought, sold or priced"]
    return []


def followups(opts):
    """The most answers the player gives after picking a menu number: which one of a group, then each param.
    A walk is 0; 'Light lantern 3' is 1; 'lamp or cut, and how many' is 2, which is two questions for one move."""
    groups = {}
    for i, o in enumerate(opts):
        groups.setdefault(o.get("group") or ("_ungrouped", i), []).append(o)
    worst = 0
    for grp in groups.values():
        n = (1 if len(grp) > 1 else 0) + max(len(o.get("params") or {}) for o in grp)
        worst = max(worst, n)
    return worst


def status_numbers(status):
    """How many numbers the status line asks the player to read."""
    return len(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?!\w)", status))


def scan_state(s, path="state"):
    """Walk a state and report anything JSON would silently change, NaN, or a runaway number."""
    out = []
    if isinstance(s, bool) or s is None or isinstance(s, str):
        return out
    if isinstance(s, (int, float)):
        if isinstance(s, float) and (math.isnan(s) or math.isinf(s)):
            out.append(f"{path} is {s}")
        elif abs(s) > 1e7:
            out.append(f"{path} ran away to {s}")
        return out
    if isinstance(s, dict):
        for k, v in s.items():
            if not isinstance(k, str):
                out.append(f"{path} has a non-string key {k!r} (JSON turns it into a string)")
            out += scan_state(v, f"{path}.{k}")
        return out
    if isinstance(s, list):
        for i, v in enumerate(s):
            out += scan_state(v, f"{path}[{i}]")
        return out
    out.append(f"{path} is a {type(s).__name__}, which does not survive JSON")
    return out


def status_labels(status):
    labels = []
    for field in status.split("|"):
        m = re.match(r"\s*([A-Za-z][A-Za-z ]*?)\s*(?:[\d\W_]|$)", field)
        labels.append(m.group(1).strip().lower() if m else field.strip().lower())
    return labels


def numeric_view(g, s):
    """Top-level numbers of a state, plus any DERIVED values the game declares (maxes, counts over lists)."""
    out = {k: v for k, v in s.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_")}
    for name, fn in getattr(g, "DERIVED", {}).items():
        try:
            v = fn(g, s)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[name] = v
    return out


def _cv(g, x):
    """A BOUNDS, REACH or GATES value may name a constant ("GOAL") so it follows the number when tuning moves it."""
    return g.C[x] if isinstance(x, str) else x


def bounds_problems(g, s):
    out = []
    view = numeric_view(g, s)
    for key, bound in getattr(g, "BOUNDS", {}).items():
        lo, hi = _cv(g, bound[0]), _cv(g, bound[1])
        v = view.get(key)
        if v is not None and not (lo <= v <= hi):
            out.append(f"{key} is {v}, outside its declared range {lo} to {hi}")
    return out


def hidden_leaks(g, s):
    """Strings from s['hidden'] that appear in what the player is shown."""
    hidden = s.get("hidden")
    if not isinstance(hidden, (dict, list)):
        return []
    vis = g.visible(s)
    if isinstance(vis, dict) and "hidden" in vis:
        return ["visible() returns the hidden section"]  # certain
    shown = []

    def collect(x, into):
        if isinstance(x, str):
            into.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                collect(v, into)
        elif isinstance(x, list):
            for v in x:
                collect(v, into)

    secret = []
    collect(hidden, secret)
    collect(vis, shown)
    leaks = [x for x in secret if len(x) >= 6 and any(x in v for v in shown)]
    return [f"LEAK?: hidden text {x!r} also appears in what the player sees; make sure that is intended" for x in leaks]


def integrity(g, s, events, opts):
    """Called after every turn at play time. A non-empty result means stop and fix the engine."""
    out = []
    if events is not None:
        if not isinstance(events, list):
            out.append("events is not a list")
        else:
            for ev in events:
                for p in text_problems(ev):
                    out.append(f"event {ev!r} {p}")
    for o in opts or []:
        for p in text_problems(o.get("label")):
            out.append(f"option label {o.get('label')!r} {p}")
    try:
        status = g.status_line(s)
    except Exception as e:  # noqa: BLE001
        status = ""
        out.append(f"status_line crashed: {e!r}")
    for p in text_problems(status):
        out.append(f"status line {p}")
    if status and len(status.split("|")) > 4:
        out.append("status line has more than 4 fields")
    out += bounds_problems(g, s)
    out += scan_state({k: v for k, v in s.items() if k != "_rng"})
    out += [p for p in hidden_leaks(g, s) if not p.startswith("LEAK?")]
    if not s.get("_ended") and not opts:
        out.append("no legal options in a live game")
    return out


# ---------------------------------------------------------------- gates


def _gate_val(g, v):
    return g.C[v] if isinstance(v, str) else v


def gate_state(g, action, s):
    """True if the declared gates say `action` should be offered at s; None if no gates declared."""
    gate = getattr(g, "GATES", {}).get(action)
    if gate is None:
        return None
    for key, need in gate.items():
        if key == "_if":
            if not need(g, s):
                return False
        elif key.startswith("!"):
            if s.get(key[1:]):
                return False
        else:
            val = numeric_view(g, s).get(key)  # a state key or a DERIVED value
            if val is None and isinstance(s.get(key), (int, float)) and not isinstance(s.get(key), bool):
                val = s[key]  # an engine key such as _turn
            if val is None or val < _gate_val(g, need):
                return False
    return True


# ---------------------------------------------------------------- observe, fuzz, determinism


def _pick(g, B, s, opts, rng, policy):
    if policy == "random":
        return B._concrete_random(rng.choice(opts), rng)
    return B._norm(g.heuristic(s, opts, rng), opts)


def _brief(s):
    return ", ".join(f"{k}={v}" for k, v in s.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_"))[:120]


def _choices(opts):
    """How many choices the player sees: options sharing a group collapse into one."""
    groups = set()
    n = 0
    for o in opts:
        gp = o.get("group")
        if gp:
            groups.add(gp)
        else:
            n += 1
    return n + len(groups)


_WORD = re.compile(r"[A-Za-z]{4,}")


def _sentence_words(text):
    """Capitalized words that are not the first word of a sentence."""
    out = []
    for sent in re.split(r"(?<=[.!?:;])\s+", text):
        words = [re.sub(r"'s?$", "", w) for w in re.findall(r"[A-Za-z']+", sent)]  # a possessive is its owner's word
        out += [w for w in words[1:] if len(w) >= 4 and w[0].isupper() and not w.isupper()]
    return out


def vocabulary_hints(g, event_words, known_text):
    """Capitalized words in events that nothing the player is shown up front uses: often a word left over
    from an earlier draft of the game ("the Wall stands" in a game of dens). Rarest first."""
    known = {w.lower() for w in _WORD.findall(known_text)}
    out = []
    for word, n in sorted(event_words.items(), key=lambda kv: kv[1]):
        if word.lower().rstrip("s") not in {k.rstrip("s") for k in known}:
            out.append(f"{word} ({n})")
    return out[:8]


def _collect_strings(x, into):
    if isinstance(x, str):
        into.append(x)
    elif isinstance(x, dict):
        for v in x.values():
            _collect_strings(v, into)
    elif isinstance(x, list):
        for v in x:
            _collect_strings(v, into)


def observe(g, B, games=80):
    """Play many games with a round trip through JSON on every step, recording everything."""
    probs = {}
    minmax = {}
    snaps = []
    srng = random.Random(2024)
    labels0 = None
    stat = {"states": 0, "forced": 0, "max_choices": 0, "hidden_seen": False, "max_followups": 0, "max_status_numbers": 0,
            "gambit_states": {}, "gambit_played": {}, "rival_touched": {}}
    gambits = getattr(g, "GAMBITS", {}) or {}
    rival_keys = list(getattr(g, "RIVAL_KEYS", []) or [])
    event_words = {}
    known_parts = [g.name, " ".join(getattr(g, "ACTIONS", [])), " ".join(getattr(g, "TAGS", []))]
    with contextlib.suppress(Exception):
        known_parts.append(g.rules())

    def add(kind, msg):
        lst = probs.setdefault(kind, [])
        if msg not in lst and len(lst) < 3:
            lst.append(msg)

    def record(s):
        for k, v in numeric_view(g, s).items():
            lo, hi = minmax.get(k, (v, v))
            minmax[k] = (min(lo, v), max(hi, v))

    for i in range(games):
        policy = "heuristic" if i % 2 == 0 else "random"
        s, rng = B._new(g, 5000 + i)
        g._hits = type(g._hits)()
        guard = 0
        try:
            while not s.get("_ended") and guard < g.turns + 5:
                guard += 1
                try:
                    s = json.loads(json.dumps(s))
                except TypeError as e:
                    add("json", f"state is not JSON-safe: {e}")
                    break
                for p in scan_state({k: v for k, v in s.items() if k != "_rng"}):
                    add("state", p)
                for p in bounds_problems(g, s):
                    add("bounds", p)
                for p in hidden_leaks(g, s):
                    add("leak_hint" if p.startswith("LEAK?") else "leak", p)
                if s.get("hidden"):
                    stat["hidden_seen"] = True
                opts = g.options(s)
                for o in opts:
                    for p in text_problems(o.get("label"), soft=False):
                        add("text", f"option label {o.get('label')!r} {p}")
                    for p in sense_problems(o.get("label")):
                        add("sense", f"option label {o.get('label')!r} {p}")
                    known_parts.append(f"{o.get('label', '')} {o.get('group', '')}")
                stat["states"] += 1
                stat["forced"] += B._is_forced(opts)
                stat["max_choices"] = max(stat["max_choices"], _choices(opts))
                stat["max_followups"] = max(stat["max_followups"], followups(opts))
                status = g.status_line(s)
                stat["max_status_numbers"] = max(stat["max_status_numbers"], status_numbers(status))
                known_parts.append(status)
                for p in text_problems(status):
                    add("text", f"status line {status!r} {p}")
                labs = status_labels(status)
                if len(labs) > 4:
                    add("status", f"status line has {len(labs)} fields; the limit is 4")
                if labels0 is None:
                    labels0 = labs
                elif len(labs) != len(labels0):
                    add("status", f"status line changed shape: {labels0} then {labs}")
                elif labs != labels0:
                    add("status_soft", f"status field labels change between turns: {labels0} then {labs} (fine for a day name or a map; not for a number)")
                offered = {o["id"] for o in opts}
                for gid in gambits:
                    if gid in offered:
                        stat["gambit_states"][gid] = stat["gambit_states"].get(gid, 0) + 1
                for a in getattr(g, "GATES", {}):
                    ok = gate_state(g, a, s)
                    if ok and a not in offered:
                        add("hidden", f"{a} is not offered at turn {s['_turn']} although its gates are met (state {_brief(s)})")
                    if ok is False and a in offered:
                        add("ungated", f"{a} is offered at turn {s['_turn']} although its gates are not met (state {_brief(s)})")
                record(s)
                if len(snaps) < 120 and srng.random() < 0.08:
                    snaps.append(copy.deepcopy(s))
                if not opts:
                    add("crash", f"no legal options at turn {s['_turn']}")
                    break
                pick = _pick(g, B, s, opts, rng, policy)
                if pick["id"] in gambits:
                    stat["gambit_played"][pick["id"]] = stat["gambit_played"].get(pick["id"], 0) + 1
                    if gambits[pick["id"]].get("rival") and rival_keys:
                        # the action alone, on a copy, with the same dice: did it touch the rival at all?
                        trial = copy.deepcopy(s)
                        g.apply(trial, pick["id"], dict(pick.get("args", {})), B.RNG(s["_seed"], s["_rng"]))
                        if any(trial.get(k) != s.get(k) for k in rival_keys):
                            stat["rival_touched"][pick["id"]] = stat["rival_touched"].get(pick["id"], 0) + 1
                s, events, _ = B._step(g, s, pick["id"], pick.get("args", {}))
                secret = []
                _collect_strings(s.get("hidden"), secret)
                for ev in events + ([s["_ended"]["reason"]] if s.get("_ended") and s["_ended"].get("reason") else []):
                    for p in text_problems(ev):
                        add("text", f"event {ev!r} {p}")
                    for p in sense_problems(ev):
                        add("sense", f"event {ev!r} {p}")
                    for w in secret:
                        if len(w) >= 4 and w.isalpha() and w.lower() in ev.lower():
                            add("leak_hint", f"LEAK?: hidden text {w!r} appears in the event {ev!r}; make sure the player may know it by then")
                    for w in _sentence_words(ev):
                        event_words[w] = event_words.get(w, 0) + 1
                if s.get("_ended") and s["_turn"] < g.turns:
                    nxt = s["_turn"] + 1
                    ahead = re.compile(r"\btomorrow\b|\b(?:night|day|turn|week|round)\s+%d\b" % nxt, re.I)
                    for ev in events:
                        if ahead.search(ev):
                            add("after_end", f"the game ended on turn {s['_turn']} but an event still looks ahead: {ev!r}; end the dusk with self.finish(...) before announcing tomorrow")
                record(s)  # the state after the move, including the final one
                for p in bounds_problems(g, s):
                    add("bounds", p)
        except Exception as e:  # noqa: BLE001
            add("crash", f"{type(e).__name__}: {e}")
    stat["vocab"] = vocabulary_hints(g, event_words, " ".join(known_parts))
    return {"problems": probs, "minmax": minmax, "snapshots": snaps, "stat": stat}


def texts_report(g, B, games=120, limit=160):
    """Every distinct wording the game can show, numbers replaced by #, most common first. A human or a reviewer
    reads this list once: stale words, bad agreement, "+0 from 0 dens" and 0-based numbers jump out."""
    counts = {}

    def note(kind, text):
        masked = re.sub(r"\d+(?:\.\d+)?", "#", text)  # keep the sign: a gain and a loss are different wordings
        masked = re.sub(r"(?<!\S)[#.\-_*]{4,}(?!\S)", "~", masked)  # a drawn board or bar is one wording, not many
        key = (kind, masked)
        counts[key] = counts.get(key, 0) + 1

    for i in range(games):
        policy = "heuristic" if i % 2 == 0 else "random"
        s, rng = B._new(g, 9000 + i)
        guard = 0
        try:
            while not s.get("_ended") and guard < g.turns + 5:
                guard += 1
                s = json.loads(json.dumps(s))
                opts = g.options(s)
                note("status", g.status_line(s))
                for o in opts:
                    note("option", o["label"] + (f"  [{o['group']}]" if o.get("group") else ""))
                pick = _pick(g, B, s, opts, rng, policy)
                s, events, _ = B._step(g, s, pick["id"], pick.get("args", {}))
                for ev in events:
                    note("event", ev)
            end = s.get("_ended") or {}
            if end.get("reason"):
                note("end", f"{end.get('result')}: {end['reason']}")
        except Exception:  # noqa: BLE001
            continue
    lines = []
    for kind in ("status", "option", "event", "end"):
        rows = sorted(((n, text) for (k, text), n in counts.items() if k == kind), reverse=True)
        lines.append(f"-- {kind} wordings ({len(rows)} distinct) --")
        lines += [f"{n:5d}  {text}" for n, text in rows[:limit]]
    return lines


def check_end_problems(g, B, snaps):
    """check_end runs twice a turn: after the action (_turn is this turn) and after dusk (_turn is the next turn).
    If it ends a game that is live at turn 1 merely because _turn reached the budget, the last action is never played."""
    for snap in snaps:
        if snap.get("_ended"):
            continue
        early, last = copy.deepcopy(snap), copy.deepcopy(snap)
        early["_turn"], last["_turn"] = 1, g.turns
        try:
            e1, e2 = g.check_end(early), g.check_end(last)
        except Exception:  # noqa: BLE001
            continue
        if e1 is None and e2 is not None:
            return [
                f"check_end ends a live game as soon as _turn == {g.turns} (reason: {e2.get('reason')}); "
                f"the last action would never be played. Score the final result at _turn > {g.turns}, never at _turn >= {g.turns}"
            ]
    return []


def fuzz(g, B, obs, cap=4000):
    """Put each numeric key at its observed minimum, maximum and zero, then try every legal option."""
    crashes = []
    tried = 0
    for snap in obs["snapshots"][:60]:
        for key, (lo, hi) in obs["minmax"].items():
            cur = snap.get(key)
            if not isinstance(cur, (int, float)) or isinstance(cur, bool):
                continue
            for val in sorted({lo, hi, 0 if lo <= 0 <= hi else lo}):
                if val == cur:
                    continue
                m = copy.deepcopy(snap)
                m[key] = val
                try:
                    opts = g.options(m)
                    for o in opts[:10]:
                        tried += 1
                        c = B._concrete_first(o)
                        B._step(g, copy.deepcopy(m), c["id"], c.get("args", {}))
                except Exception as e:  # noqa: BLE001
                    crashes.append(f"{key}={val} at turn {snap.get('_turn')}: {type(e).__name__}: {e}")
                if tried >= cap:
                    return crashes[:3], tried
    return crashes[:3], tried


def _parse_script(script):
    """'haul,light:lantern=3,gift:steading=2:amount=4' -> [(id, {args})]"""
    out = []
    for raw in (script or "").split(","):
        tok = raw.strip()
        if not tok:
            continue
        parts = tok.split(":")
        args = {}
        for kv in parts[1:]:
            if "=" in kv:
                k, v = kv.split("=", 1)
                with contextlib.suppress(ValueError):
                    v = json.loads(v)
                args[k] = v
        out.append((parts[0], args))
    return out


def trace(g, B, seed=7, policy="heuristic", script=None):
    """One full game as text. `script` ('haul,light:lantern=3') forces the player's first moves."""
    s, rng = B._new(g, seed)
    g._hits = type(g._hits)()
    scripted = _parse_script(script)
    lines = [f"seed {seed} policy {policy}", f"T{s['_turn']} | {g.status_line(s)}"]
    guard = 0
    while not s.get("_ended") and guard < g.turns + 5:
        guard += 1
        opts = g.options(s)
        pick = None
        if scripted:
            sid, sargs = scripted.pop(0)
            try:
                pick = B._concrete_first(B._match(opts, sid, sargs), sargs)
            except B.IllegalAction:
                lines.append(f"  (scripted move {sid} {sargs} is not offered here; the {policy} policy plays instead)")
        if pick is None:
            pick = _pick(g, B, s, opts, rng, policy)
        s, events, _ = B._step(g, s, pick["id"], pick.get("args", {}))
        label = pick["label"] + (f"  {pick['args']}" if pick.get("params") else "")
        lines.append(f"  do: {label}")
        for ev in events:
            lines.append(f"    - {ev}")
        lines.append(f"T{min(s['_turn'], g.turns)} | {g.status_line(s)}")
    end = s.get("_ended") or {}
    note = ""
    if end.get("phase") == "dusk" and s["_turn"] < g.turns:
        note = f"  [ended at dusk of turn {s['_turn']}; the other {plural(g.turns - s['_turn'], 'turn')} were never played]"
    elif end.get("phase") == "action" and s["_turn"] < g.turns:
        note = f"  [ended right after the action of turn {s['_turn']}, before its dusk]"
    lines.append(f"END {end.get('result')}: {end.get('reason')}{note}")
    return lines


def trace_hash(lines):
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()[:12]


def determinism(g, B, engine_path=None):
    """Same seed, same trace: in process, and across processes with different hash seeds."""
    problems = []
    try:
        a = trace_hash(trace(g, B, 7))
        b = trace_hash(trace(g, B, 7))
    except Exception as e:  # noqa: BLE001
        return [f"a full game could not be traced: {type(e).__name__}: {e}"]
    if a != b:
        problems.append("the same seed produced two different games in one process (the engine uses randomness or state outside rng)")
        return problems
    path = engine_path or os.path.abspath(sys.argv[0])
    if not (path.endswith(".py") and os.path.exists(path)):
        return problems
    outs = []
    for hs in ("11", "222"):
        env = dict(os.environ, PYTHONHASHSEED=hs)
        try:
            r = subprocess.run([sys.executable, path, "trace", "7", "--hash"], capture_output=True, text=True, env=env, timeout=120, check=False)
            outs.append(r.stdout.strip() or ("ERR " + r.stderr.strip()[-120:]))
        except Exception as e:  # noqa: BLE001
            outs.append(f"ERR {e!r}")
    if outs[0] != outs[1]:
        problems.append(f"the same seed gives different games under different hash seeds ({outs[0]} vs {outs[1]}); iterate sorted lists, not sets or dicts of strings")
    elif outs[0].startswith("ERR"):
        problems.append(f"trace subprocess failed: {outs[0]}")
    return problems


# ---------------------------------------------------------------- rule tests


class T:
    """Harness for rule tests. A test builds a state, calls the game's own apply or advance, and asserts.

    Scripted randomness is consumed in the order the engine calls it: `dice` feeds rng.d / rng.roll / rng.check,
    `chances` feeds rng.chance (a value below p means success), `choices` feeds rng.choice, `drifts` feeds
    rng.drift (1 up, -1 down, 0 stay)."""

    def __init__(self, g, B):
        self.g, self.B = g, B

    def fresh(self, seed=1, **over):
        """A new state. Override top-level keys with keyword arguments; use hidden__key for hidden facts."""
        s, _ = self.B._new(self.g, seed)
        for k, given in over.items():
            v = copy.deepcopy(given)  # a test must never share an object with another state
            if "__" in k:
                a, b = k.split("__", 1)
                s[a][b] = v
            else:
                s[k] = v
        return s

    def copy(self, s):
        return copy.deepcopy(s)

    def rng(self, seed=1, dice=None, chances=None, choices=None, drifts=None):
        return _scripted(self.B, seed, dice, chances, choices, drifts)

    def offered(self, s, action_id, **args):
        """True if exactly this action (id and args) is legal at s."""
        try:
            o = self.B._find(self.g.options(s), action_id, args)
            self.B._concrete_first(o, args)  # a param you name must be legal; one you leave out is filled in
            return True
        except self.B.IllegalAction:
            return False

    def ids(self, s):
        return sorted({o["id"] for o in self.g.options(s)})

    def label(self, s, action_id, **args):
        """The exact label the player sees for this option."""
        return self.B._find(self.g.options(s), action_id, args)["label"]

    def labels(self, s):
        return [o["label"] for o in self.g.options(s)]

    def status(self, s):
        return self.g.status_line(s)

    def apply(self, s, action_id, args=None, seed=1, dice=None, chances=None, choices=None, drifts=None):
        """Run Game.apply on s (in place). The action must be legal at s. Returns the events."""
        o = self.B._match(self.g.options(s), action_id, args or {})
        merged = self.B._clean_args(o, {**o.get("args", {}), **(args or {})})
        return list(self.g.apply(s, action_id, merged, self.rng(seed, dice, chances, choices, drifts)) or [])

    def advance(self, s, turn=None, seed=1, dice=None, chances=None, choices=None, drifts=None):
        """Run Game.advance on s (in place): dusk of the turn `turn` (set as s['_turn'] first), before the counter goes up."""
        if turn is not None:
            s["_turn"] = turn
        return list(self.g.advance(s, self.rng(seed, dice, chances, choices, drifts)) or [])

    def step(self, s, action_id, args=None):
        """The full runtime step (apply, end check, advance). Returns (state, events)."""
        s2, events, _ = self.B._step(self.g, s, action_id, args or {})
        return s2, events

    def eq(self, got, want, msg=""):
        if got != want:
            raise AssertionError(f"{msg or 'value'}: got {got!r}, expected {want!r}")

    def ok(self, cond, msg="condition false"):
        if not cond:
            raise AssertionError(msg)

    def in_order(self, events, fragments, msg=""):
        """Each fragment appears in the events, and in this order (a cause is narrated before its effect)."""
        at = -1
        for frag in fragments:
            idx = next((i for i, e in enumerate(events) if i > at and frag in e), None)
            if idx is None:
                raise AssertionError(f"{msg or 'order'}: {frag!r} does not come after the previous fragment in {events!r}")
            at = idx

    def has(self, events, fragment, msg=""):
        if not any(fragment in e for e in events):
            raise AssertionError(f"{msg or 'event'}: no event contains {fragment!r}; got {events!r}")


def _scripted(B, seed, dice, chances, choices=None, drifts=None):
    drifts = list(drifts or [])  # each: 1 up, -1 down, 0 stay
    dice = list(dice or [])
    chances = list(chances or [])
    choices = list(choices or [])

    class Scripted(B.RNG):
        def d(self, sides=6):
            if dice:
                v = dice.pop(0)
                self.log.append(f"d{sides}={v}(scripted)")
                return v
            return super().d(sides)

        def roll(self, n, sides=6):
            if len(dice) >= n:
                vals = [dice.pop(0) for _ in range(n)]
                self.log.append(f"{n}d{sides}={vals}(scripted)")
                return sum(vals)
            return super().roll(n, sides)

        def chance(self, p):
            if chances:
                v = chances.pop(0)
                self.log.append(f"chance({p})={v}(scripted)")
                return v < p
            return super().chance(p)

        def drift(self, value, lo, hi, step=1, p_up=1 / 3, p_down=1 / 3):
            if drifts:
                d = drifts.pop(0)
                self.log.append(f"drift={d}(scripted)")
                return max(lo, min(hi, value + d * step))
            return super().drift(value, lo, hi, step, p_up, p_down)

        def choice(self, seq):
            if choices:
                v = choices.pop(0)
                if v not in seq:
                    raise AssertionError(f"scripted choice {v!r} is not among {list(seq)!r}")
                self.log.append(f"choice={v!r}(scripted)")
                return v
            return super().choice(seq)

    return Scripted(seed)


def run_rule_tests(g, B):
    flags = []
    if not g.RULES:
        return flags
    try:
        lines = [ln for ln in g.rules().splitlines() if ln.strip()]
        tests = list(g.rule_tests() or [])
    except Exception as e:  # noqa: BLE001
        return [f"RULETEST: the rules or the tests could not be built: {type(e).__name__}: {e}"]
    if not tests:
        return ["RULETEST: no rule_tests written; add one test per rule line (see the example engine)"]
    covered = {t[0] for t in tests}
    for i, ln in enumerate(lines, 1):
        if i not in covered:
            flags.append(f"RULETEST: rule {i} has no test ({ln.strip()[:60]}...)")
    for no, name, fn in tests:
        if not isinstance(no, int) or no < 1 or no > len(lines):
            flags.append(f"RULETEST: test {name!r} names rule {no}, but the sheet has {len(lines)} rules")
            continue
        saved = type(g._hits)(g._hits)
        g._hits = type(g._hits)()  # each test starts with no tags fired
        try:
            fn(T(g, B))
        except AssertionError as e:
            flags.append(f"RULETEST: rule {no} ({name}) failed: {e}")
        except Exception as e:  # noqa: BLE001
            flags.append(f"RULETEST: rule {no} ({name}) crashed: {type(e).__name__}: {e}")
        finally:
            g._hits = saved
    return flags


# ---------------------------------------------------------------- the combined run


GAMBIT_OFFER_MIN = 0.25  # a gambit offered in fewer states than this cannot absorb the player's off-menu ideas


def gambit_problems(g, stat, s0=None):
    """Flags and warnings for GAMBITS and RIVAL_KEYS, from what `observe` recorded. Pure, so the tests can feed it."""
    flags, warnings = [], []
    gambits = getattr(g, "GAMBITS", {}) or {}
    rival_keys = list(getattr(g, "RIVAL_KEYS", []) or [])
    if not isinstance(gambits, dict) or not all(isinstance(v, dict) for v in gambits.values()):
        return [f"GAMBIT: GAMBITS must be a dict of id -> {{}} or {{'rival': True}}, got {gambits!r}"], warnings
    if not gambits:
        warnings.append(
            "GAMBIT: no GAMBITS declared, so the player can only play the loop and every idea of theirs gets 'the game cannot'. "
            "Declare two or three risky moves the setting invites, one of them against the rival (see the contract)"
        )
        return flags, warnings
    if s0 is not None:
        for k in rival_keys:
            if k not in s0:
                flags.append(f"GAMBIT: RIVAL_KEYS names {k!r}, which is not a key of the state")
    rival_gambits = [gid for gid, spec in gambits.items() if spec.get("rival")]
    if rival_gambits and not rival_keys:
        flags.append(f"GAMBIT: {', '.join(rival_gambits)} marked rival, but RIVAL_KEYS is empty; name the state keys that describe the rival")
    if not rival_gambits:
        warnings.append("GAMBIT: no gambit acts on the rival, so the rival is untouchable; mark one {'rival': True} and make it change a RIVAL_KEYS value")
    states = max(1, stat.get("states", 0))
    for gid in gambits:
        share = stat.get("gambit_states", {}).get(gid, 0) / states
        if share < GAMBIT_OFFER_MIN:
            warnings.append(
                f"GAMBIT: {gid} is offered in {share:.0%} of states (under {GAMBIT_OFFER_MIN:.0%}); a gambit that is rarely on the table "
                "cannot catch the player's off-menu ideas. Widen when it is legal, or it is a lever, not a gambit"
            )
    for gid in rival_gambits:
        if not rival_keys:
            continue
        played = stat.get("gambit_played", {}).get(gid, 0)
        if played and not stat.get("rival_touched", {}).get(gid):
            flags.append(
                f"GAMBIT: {gid} is marked rival but in {played} plays it never changed any of RIVAL_KEYS {rival_keys}; "
                "the rival is untouchable in practice. Make the gambit move, delay, blind or weaken the rival"
            )
    return flags, warnings


def run_universal(g, B, engine_path=None):
    flags, warnings = [], []
    try:
        obs = observe(g, B)
    except Exception as e:  # noqa: BLE001
        return [f"CRASH: the observation pass failed: {type(e).__name__}: {e}"], warnings, {}
    s_first, _ = B._new(g, 1)
    gf, gw = gambit_problems(g, obs["stat"], s_first)
    flags += gf
    warnings += gw
    names = {
        "json": "JSON", "state": "STATE", "bounds": "BOUNDS", "leak": "LEAK", "text": "TEXT",
        "status": "STATUS", "hidden": "GATE-HIDDEN", "ungated": "GATE-OFFERED", "crash": "CRASH", "after_end": "TEXT",
        "sense": "SENSE",
    }
    soft = {"leak_hint": "", "status_soft": "STATUS: "}
    for kind, msgs in obs["problems"].items():
        for m in msgs:
            if kind in soft:
                warnings.append(f"{soft[kind]}{m}")
            else:
                flags.append(f"{names.get(kind, kind.upper())}: {m}")
    # the rulesheet is read first by the player: it must not price a feeling either
    try:
        sheet_lines = g.rules().splitlines()
    except Exception:  # noqa: BLE001
        sheet_lines = []
    for line in sheet_lines:
        for p in sense_problems(line):
            flags.append(f"SENSE: rule {line[:70]!r} {p}")
    # REACH: promised values must actually occur somewhere (catches clamps and dead thresholds)
    for key, target in getattr(g, "REACH", {}).items():
        op, val = target if isinstance(target, (tuple, list)) else (">=", target)
        val = _cv(g, val)
        lo, hi = obs["minmax"].get(key, (None, None))
        if lo is None:
            flags.append(f"REACH: {key} is not a numeric state value (declare it in DERIVED if it is computed)")
        elif op == ">=" and hi < val:
            flags.append(f"REACH: {key} never reached {val} in 80 games (highest {hi}); a clamp or a dead rule is hiding it")
        elif op == "<=" and lo > val:
            flags.append(f"REACH: {key} never fell to {val} in 80 games (lowest {lo})")
    # the game must still be live when the player is about to take the last action
    flags += [f"CHECK_END: {p}" for p in check_end_problems(g, B, obs["snapshots"])]
    # TRACKED: the numbers and boards the player must manage; at most 3
    tracked = list(getattr(g, "TRACKED", []))
    if len(tracked) > 3:
        flags.append(f"TRACKED: {len(tracked)} tracked numbers ({', '.join(tracked)}); the limit is 3. A board with rules counts as one")
    elif not tracked:
        warnings.append("TRACKED not declared; list every number or board the player must manage (3 at most), including ones kept off the status line")
    else:
        s0, _ = B._new(g, 1)
        for key in tracked:
            if key not in s0:
                flags.append(f"TRACKED: {key} is not a key of the state")
    try:
        crashes, tried = fuzz(g, B, obs)
    except Exception as e:  # noqa: BLE001
        crashes, tried = [f"fuzz pass failed: {type(e).__name__}: {e}"], 0
    for c in crashes:
        flags.append(f"FUZZ: {c}")
    for p in determinism(g, B, engine_path):
        flags.append(f"DETERMINISM: {p}")
    if not getattr(g, "BOUNDS", None):
        warnings.append("BOUNDS not declared; declare the range each numeric value may take so a runaway or clamp bug is caught")
    if not getattr(g, "REACH", None):
        warnings.append("REACH not declared; declare the values the sheet promises can happen (rival thresholds, win totals)")
    if not getattr(g, "GATES", None):
        warnings.append("GATES not declared; declare each action's affordability so a hidden-filter bug is caught")
    st = obs["stat"]
    forced_share = st["forced"] / max(1, st["states"])
    if forced_share > 0.15:
        warnings.append(f"FORCED: {forced_share:.0%} of turns offered a single legal option; those turns are not decisions")
    if st["max_followups"] > 1:
        warnings.append(
            f"MOVE: a menu number can need {st['max_followups']} answers before the move is known (a verb and an amount, say). "
            "One move should take one answer: give each verb its own choice, or drop the amount"
        )
    if st["max_status_numbers"] > 5:
        warnings.append(
            f"STATUS: the status line shows up to {st['max_status_numbers']} numbers. A player reads and juggles all of them; "
            "5 or fewer, or fold the rest into the options"
        )
    if st["max_choices"] > 8:
        warnings.append(f"MENU: up to {st['max_choices']} choices after grouping; give same-verb actions a group, or use params for amounts")
    if st["vocab"]:
        warnings.append(
            "VOCAB: capitalized words in events or end reasons that the sheet, the options and the status never use: "
            + ", ".join(st["vocab"]) + ". A word left over from an earlier draft reads as a bug; a name the player meets in play is fine"
        )
    info = {
        "observed_games": 80, "fuzz_steps": tried, "numeric_keys": sorted(obs["minmax"]),
        "forced_share": round(forced_share, 2), "max_choices": st["max_choices"], "hidden_seen": st["hidden_seen"],
        "gambits": {
            gid: {
                "offered_share": round(st["gambit_states"].get(gid, 0) / max(1, st["states"]), 2),
                "played": st["gambit_played"].get(gid, 0),
                "rival_touched": st["rival_touched"].get(gid, 0),
            } for gid in (getattr(g, "GAMBITS", {}) or {})
        },
    }
    return flags, warnings, info
