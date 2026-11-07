"""
gm_base: the shared engine contract for /play games.

A generated game is one file, engine.py, next to this module (or importing it by path),
that defines `class G(Game)` and ends with `if __name__ == "__main__": run(G)`.

The engine owns every number, every die, the clock, the rival, and the win/lose check.
The LLM owns the words: option labels, narration, mapping free text to an action id.

CLI (run from the session folder):
    python engine.py new [seed]            create state.json; prints first turn JSON
    python engine.py options               legal actions for the current state
    python engine.py step <id> [json]      apply action, advance hidden systems, save, print turn JSON
    python engine.py step "#3" [json]      same, picking the 3rd entry of the options list
    python engine.py status                current visible state without advancing
    python engine.py rules                 the rulesheet, built from CONSTANTS (no drift)
    python engine.py check                 full tuning check: random + heuristic + lookahead + sheet + coverage + test strength
    python engine.py check --free          the same, without counting a tuning round
    python engine.py sweep K=a,b [K2=c,d]  try constants at several values; one line per combo (--lookahead adds look-ahead)
    python engine.py trace [seed] [random] [--do haul,light:lantern=3]
                                           one full game as text, optionally with the first moves scripted. Read it
    python engine.py texts [games]         every distinct event, option, status and end wording; read it once for stale words and bad grammar
    python engine.py profile [n] [k]       tension profile: how much the choice matters, turn by turn (warnings only)
    python engine.py ablate [n]            ban each action in turn; report which ones nobody misses (warnings only)
    python engine.py autopsy [k]           after a finished game: where it was decided, the swing turn, the regrets
    python engine.py replay [--apply]      re-run history.jsonl on the saved seed after an engine fix
    python engine.py fingerprint           mechanical traits of this game for the sameness detector
    python engine.py selftest [n] [policy] one policy only: random | heuristic | lookahead
    python engine.py log                   roll log since game start
    python engine.py board                 the full board (every number the player may see), one line each

Contract (everything below `options` is checked by `check`):
    CONSTANTS  dict of every number the rulesheet states. The engine reads self.C["KEY"], never a literal.
               Keys starting with "_" are tuning-only and need not appear on the sheet.
    RULES      the rulesheet text (8 lines max, about 40 words a line) with {KEY} placeholders. `rules` fills it in.
    ACTIONS    every action id the game can offer. Never offered, or offered but not listed, is a bug.
    TAGS       every twist, event, unlock and lever the game can fire. Call self.hit("tag") where it fires.
               A tag that never fires in any selftest game is a bug.
    TRACKED    state keys of the numbers on the status line, 4 at most; the board (board(s)) holds the rest.
    options    returns EVERY legal action. Several actions may share an id if their "args" differ (a "light" action
               per dark lantern); give them a "group". An action that takes a number or a pick from the player
               carries "params": {"amount": {"min": 1, "max": 6}} or {"oil": {"choices": [3, 6]}}. The player
               supplies the value in the step call; it is validated against the range. Use params for bids,
               allocations and placements instead of one option per value.
    BOUNDS     {"oil": (-10, 80)}: the range a numeric state value may take. Outside it is a bug.
    REACH      {"column": "GOAL", "oil": ("<=", -1)}: values the sheet promises can happen. Never seen is a bug
               (a clamp, a dead rule). Include every threshold the sheet names. A value may name a constant
               ("GOAL") so it follows the number when tuning moves it.
    DERIVED    {"best_pieces": fn(game, s)}: numbers computed from state (a max over a list), usable in BOUNDS/REACH.
    GATES      {"light": {"oil": "LIGHT_COST", "_if": fn(game, s)}}: when each priced or gated action must be
               offered. `check` fails if it is missing when affordable or offered when not. A key may be a state key
               or a DERIVED name.
    GAMBITS    {"raid": {"rival": True}, "dig_in": {}}: the risky moves off the main loop that the setting invites
               (raid the rival's camp, run the blockade, bribe the inspector). Each id is in ACTIONS, shows its odds
               or its stake in its label, and is offered often enough to absorb a player's off-menu idea. One marked
               "rival" must change a RIVAL_KEYS value when played; `check` fails if it never does. No GAMBITS is a
               warning: the player can only play the loop, and every idea of theirs gets "the game cannot".
    RIVAL_KEYS ["ready", "riders"]: the state keys that describe the rival (position, readiness, strength, mood).
               Required when a gambit is marked "rival".
    GROWTH     "fleet" (a state key or DERIVED name), or {"key": "fleet", "factor": 2, "by": 0.66}: the number that must
               get bigger. `check` fails when sensible play has not multiplied it by the factor by that share of the
               budget, and warns when it stops growing in the last third. A v4 game declares it.
    ECONOMY    {"income": ["ore"], "stock": ["credits"], "sinks": ["build", "refit"]}: what comes in each turn, what is
               held, and the actions that spend it (at least one sink should raise income). Keys must exist.
    LADDER     {"key": "tier", "tiers": ["sloop", "brig", "frigate"], "unlocks": {2: ["refine"], 3: ["convoy"]}}: three
               tiers the player climbs; each unlock id is in ACTIONS and gated on the tier. `check` fails when fewer
               than 70% of sensible games reach tier 2 or fewer than 40% reach tier 3.
    PATHS      {"haul": ["mine", "sell"], "raid": ["raid", "board"]}: two or more action families that can each carry a
               win. `check` fails when a family is behind fewer than 30% of wins (3 or more of its moves in the game).
    board(s)   (optional) the full board the player may ask for: up to about 8 plain numbers, one per line. The
               status line stays at 4 fields; `python engine.py board` prints this.
    rule_tests the executable spec: one test per rule line, built on class gm_checks.T. `check` fails if a rule
               has no test or a test fails.
    resample_hidden(s, rng)  for games with hidden facts: redraw them consistent with what the player has seen, so
               look-ahead, profile and autopsy do not know the answer.
    a turn  is: the player's action (apply), then dusk (advance), then the turn counter goes up. During apply, advance
               and check_end, _turn is the turn being played, so "from day 9" is _turn >= 9 in both apply and advance.
               To prepare tomorrow at dusk, look at _turn + 1. check_end runs after apply and again after advance; never
               end the game because _turn reached the budget, the last action and its dusk must be played. When the
               counter passes `turns` the runtime calls final_check(s), which scores the end of the budget (default: a
               loss "out of turns"). A fatal event inside apply or advance calls self.finish(s, "loss", "reason") and
               returns, so nothing else happens after it.
    Every turn's JSON carries "integrity": a list of engine bugs seen at play time. Non-empty means stop.

Turn JSON shape (printed by new/step/status):
{
  "turn": 3, "turns": 16, "status": "Fuel 4 | Water 9 | Standing U+2 H0 C-1 | T3/16",
  "events": ["roll 7 (need 5+) success", "Union standing +1", ...],
  "visible": {...},              # anything the player is allowed to see
  "options": [{"id": "jump", "label": "Jump to Pallas (-2 fuel)", "args": {}, "group": "move"}, ...],
  "ended": null | {"result": "win"|"loss", "reason": "..."},
  "integrity": []
}
"""

import ast
import copy
import hashlib
import importlib.util
import inspect
import itertools
import json
import math
import os
import random
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gm_checks as K  # noqa: E402
from gm_checks import plural  # noqa: E402,F401  (games import it: from gm_base import Game, run, plural)

STATE_FILE = "state.json"
LOG_FILE = "rolls.log"
TUNE_FILE = "tune.count"
HISTORY_FILE = "history.jsonl"
TUNE_CAP = 4
_LENIENT = False  # ablation only: tolerate a heuristic that picks an action that was banned

# Profile and autopsy thresholds, in win-rate points.
HARD_SPREAD = 0.20   # a turn is consequential when the best option beats the worst by this much
FLAT_SPREAD = 0.10   # a turn is flat when the spread is under this
DILEMMA_GAP = 0.15   # a dilemma: consequential, and a second option within this of the best, or the sensible default is wrong
DECIDED_EDGE = 0.05  # decided when even the best option wins under this, or the worst wins over 1 minus this

# Difficulty bands. Random play must lose. A sensible policy should win a minority of games.
# A look-ahead policy (search with rollouts) shows what a thoughtful player can reach.
RANDOM_MAX = 0.35
HEURISTIC_BAND = (0.25, 0.55)  # v4: longer games with two paths are won more often by a sensible player
LOOKAHEAD_BAND = (0.6, 0.9)  # paired-rollout search plays near the ceiling; a human lands between the heuristic and this

# Sheet limits.
RULE_LINES_MAX = 8
RULE_WORDS_FLAG = 45
RULE_WORDS_WARN = 40


class RNG:
    """Seeded random with a roll log. Every die the game throws goes through here."""

    def __init__(self, seed, state=None):
        self.seed = seed
        self.r = random.Random(seed)
        if state is not None:
            self.r.setstate(_from_json_state(state))
        self.log = []

    def d(self, sides=6):
        v = self.r.randint(1, sides)
        self.log.append(f"d{sides}={v}")
        return v

    def roll(self, n, sides=6):
        vals = [self.r.randint(1, sides) for _ in range(n)]
        self.log.append(f"{n}d{sides}={vals}")
        return sum(vals)

    def check(self, need, sides=6, label=""):
        """Roll one die against a target. Returns (ok, text) with text ready to show the player."""
        v = self.d(sides)
        ok = v >= need
        tag = f" {label}" if label else ""
        self.log[-1] += f" need {max(1, need)}+ {'ok' if ok else 'miss'}"  # marks a player check in the roll log; selftest counts them
        return ok, f"roll {v} (need {max(1, need)}+){tag} {'success' if ok else 'fail'}"

    def choice(self, seq):
        v = self.r.choice(seq)
        self.log.append(f"choice={v!r}")
        return v

    def shuffle(self, seq):
        self.r.shuffle(seq)
        self.log.append("shuffle")
        return seq

    def chance(self, p):
        v = self.r.random()
        self.log.append(f"chance({p})={v:.2f}")
        return v < p

    def drift(self, value, lo, hi, step=1, p_up=1 / 3, p_down=1 / 3):
        """Random walk clamped to [lo, hi]. Returns the new value."""
        v = self.r.random()
        self.log.append(f"drift={v:.2f}")
        if v < p_up:
            value += step
        elif v < p_up + p_down:
            value -= step
        return max(lo, min(hi, value))

    def getstate(self):
        return _to_json_state(self.r.getstate())


def _to_json_state(st):
    return [st[0], list(st[1]), st[2]]


def _from_json_state(st):
    return (st[0], tuple(st[1]), st[2])


def _die(msg, **extra):
    extra = {k: v for k, v in extra.items() if v not in ([], None)}  # an empty options list says nothing
    raise SystemExit(json.dumps({"error": msg, **extra}))


def _posint(text, what, default=None):
    """A command-line count: a whole number of 1 or more, or a clean error."""
    if text is None:
        return default
    try:
        v = int(text)
    except ValueError:
        _die(f"{what} must be a whole number, not {text!r}")
    if v < 1:
        _die(f"{what} must be 1 or more, not {v}")
    return v


COMMANDS = [
    "new", "step", "status", "options", "rules", "check", "sweep", "trace", "texts", "profile", "ablate",
    "autopsy", "replay", "fingerprint", "selftest", "log", "board",
]


class IllegalAction(Exception):
    def __init__(self, msg, options=None):
        super().__init__(msg)
        self.msg = msg
        self.options = options or []


class Game:
    """Subclass this. Override every method marked (required)."""

    name = "Untitled"
    turns = 16

    CONSTANTS = {}  # every number the rulesheet states; read as self.C["KEY"]
    RULES = ""      # rulesheet template with {KEY} placeholders, 8 lines max
    ACTIONS = []    # every action id the game can offer
    TAGS = []       # every twist, event, unlock, lever tag the game can fire
    TRACKED = []    # state keys of the numbers on the status line (4 at most); the board holds the rest
    BOUNDS = {}     # {"oil": (-20, 60)}: the range a numeric state value may take; outside it is a bug
    REACH = {}      # {"rival": 70} or {"oil": ("<=", 0)}: values the sheet promises can happen; never seen is a bug
    GATES = {}      # {"light": {"oil": "LIGHT_COST", "_if": fn(game, s)}}: when an action must be offered
    DERIVED = {}    # {"best": fn(game, s)}: computed numbers usable in BOUNDS and REACH
    GAMBITS = {}    # {"raid": {"rival": True}, "dig_in": {}}: risky moves off the main loop; one acts on the rival
    RIVAL_KEYS = [] # state keys that describe the rival; a "rival" gambit must change one of them when played
    GROWTH = None   # "fleet" or {"key": "fleet", "factor": 2, "by": 0.66}: the number that must get bigger (v4)
    ECONOMY = None  # {"income": [keys], "stock": [keys], "sinks": [action ids]} (v4)
    LADDER = None   # {"key": "tier", "tiers": [three names], "unlocks": {2: [ids], 3: [ids]}} (v4)
    PATHS = None    # {"haul": [ids], "raid": [ids]}: two or more families that can each carry a win (v4)

    # (required by `check` when RULES is declared) One test per rule line. Return [(rule_no, "name", fn)];
    # fn(t) builds a state with t.fresh(...), calls t.apply / t.advance / t.step and asserts with t.eq / t.ok.
    def rule_tests(self):
        return []

    # (optional, needed when s["hidden"] holds facts the player is trying to learn) Redraw the hidden facts
    # consistent with what the player has seen. Look-ahead, profile and autopsy call it before every rollout.
    def resample_hidden(self, s, rng):
        return None

    def __init__(self):
        self.C = copy.deepcopy(self.CONSTANTS)
        self._hits = set()

    def hit(self, tag):
        """Record that a twist, event, unlock or lever fired. Used by `check` for coverage."""
        self._hits.add(tag)

    def finish(self, s, result, reason):
        """End the game now, from inside apply or advance. Return from the method right after calling it."""
        s["_ended"] = {"result": result, "reason": reason}

    def final_check(self, s):
        """Called once, when the turn counter passes the budget. Return {"result": "win"|"loss", "reason": "..."}."""
        return {"result": "loss", "reason": "out of turns"}

    def rules(self):
        if not self.RULES:
            return (sys.modules["__main__"].__doc__ or "").strip()
        template = re.sub(r"\{(\w+)\|([^}]+)\}", lambda m: plural(self.C[m.group(1)], m.group(2)), self.RULES.strip())
        return template.format(**self.C)

    # (required) Build the opening state. Return a plain dict (JSON-safe). Put hidden facts in s["hidden"].
    def init_state(self, rng):
        raise NotImplementedError

    # (required) EVERY legal action now. Each: {"id": str, "label": str, "args": dict, "group": str (optional),
    # "params": {name: {"min", "max", "step"} or {"choices": [...]}} (optional)}.
    # Do not cap or filter for display. The GM groups. Same id twice is fine when args differ.
    def options(self, s):
        raise NotImplementedError

    # (required) Apply the player's action. Mutate s. Return a list of event strings the player sees.
    def apply(self, s, action_id, args, rng):
        raise NotImplementedError

    # (required) Advance hidden systems after the player's action: prices, rival, clock, events.
    # Return event strings the player can perceive (the rival's tell goes here).
    def advance(self, s, rng):
        raise NotImplementedError

    # (required) One-line status. Same format every turn. 4 fields max.
    def status_line(self, s):
        raise NotImplementedError

    # (required) Return None, or {"result": "win"|"loss", "reason": "..."}. Runs twice a turn; see the module docstring.
    def check_end(self, s):
        raise NotImplementedError

    # (optional) The full board the player may ask for: one line per number, plain words. Default: every visible number.
    def board(self, s):
        lines = []
        for key, v in K.numeric_view(self, s).items():
            if key.startswith("_"):
                continue
            lines.append(f"{key.replace('_', ' ').capitalize()} {v:g}" if isinstance(v, float) else f"{key.replace('_', ' ').capitalize()} {v}")
        return "\n".join(lines)

    # (optional) Things the player may see. Default: everything except s["hidden"].
    def visible(self, s):
        return {k: v for k, v in s.items() if k not in ("hidden", "_rng", "_turn", "_ended", "_seed")}

    # (optional) A sensible-play policy for selftest. Return an option dict (with args, and param values if any),
    # or an action id string. It must use only what the player can see; never read s["hidden"].
    def heuristic(self, s, options, rng):
        return rng.choice(options)


# ---------------------------------------------------------------- params


def _frange(lo, hi, step):
    n = int(round((hi - lo) / step))
    return [round(lo + i * step, 10) for i in range(n + 1)]


def _param_values(spec, cap=7):
    """Candidate values for one param: every value if there are few, otherwise the ends, middle and quartiles."""
    if "choices" in spec:
        return list(spec["choices"])
    lo, hi = spec["min"], spec["max"]
    step = spec.get("step", 1)
    vals = _frange(lo, hi, step) if (isinstance(step, float) or isinstance(lo, float)) else list(range(lo, hi + 1, step))
    if len(vals) <= cap:
        return vals
    n = len(vals)
    return sorted({vals[0], vals[-1], vals[n // 2], vals[n // 4], vals[(3 * n) // 4]})


def _describe(spec):
    if "choices" in spec:
        return f"one of {spec['choices']}"
    s = f", step {spec['step']}" if spec.get("step") else ""
    return f"{spec['min']} to {spec['max']}{s}"


def _clean_args(option, args):
    """Validate the args for an option and return them cleaned: only keys the option or its params define,
    every param present and in range, whole numbers as ints."""
    params = option.get("params") or {}
    allowed = set(option.get("args", {})) | set(params)
    unknown = sorted(k for k in args if k not in allowed)
    if unknown:
        raise IllegalAction(f"unknown arg {unknown} for {option['id']!r}; it takes {sorted(allowed) or 'no args'}", [])
    out = dict(args)
    for k, v in option.get("args", {}).items():
        if k in out:
            out[k] = v  # the caller's 1.0 matched the option's 1: the engine always sees the option's own value
    for name, spec in params.items():
        if name not in out:
            raise IllegalAction(f"{option['id']!r} needs {name}: {_describe(spec)}", [])
        v = out[name]
        if "choices" in spec:
            match = [c for c in spec["choices"] if c == v and not isinstance(v, bool)]
            if not match:
                raise IllegalAction(f"{name}={v!r} is not allowed for {option['id']!r}; use {_describe(spec)}", [])
            out[name] = match[0]
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v):
            raise IllegalAction(f"{name}={v!r} must be a finite number ({_describe(spec)})", [])
        whole = isinstance(spec["min"], int) and isinstance(spec["max"], int) and isinstance(spec.get("step", 1), int)
        if whole:
            if v != int(v):
                raise IllegalAction(f"{name}={v} must be a whole number ({_describe(spec)}) for {option['id']!r}", [])
            v = int(v)
            out[name] = v
        if not (spec["min"] <= v <= spec["max"]):
            raise IllegalAction(f"{name}={v} is outside {_describe(spec)} for {option['id']!r}", [])
        step = spec.get("step", 1 if whole else None)
        if step and abs(((v - spec["min"]) / step) - round((v - spec["min"]) / step)) > 1e-9:
            raise IllegalAction(f"{name}={v} is not on the step of {_describe(spec)} for {option['id']!r}", [])
    return out


def _check_params(option, args):
    _clean_args(option, args)


def _suggest(spec):
    vals = _param_values(spec)
    return vals[len(vals) // 2]


def _concrete_first(option, given=None):
    """The option with every param filled in: from `given`, else a middle value. Validated."""
    args = dict(option.get("args", {}))
    args.update(given or {})
    for name, spec in (option.get("params") or {}).items():
        if name not in args:
            args[name] = _suggest(spec)
    out = {**option, "args": args}
    out["args"] = _clean_args(out, args)
    return out


def _concrete_random(option, rng):
    if not option.get("params"):
        return option
    args = dict(option.get("args", {}))
    for name, spec in option["params"].items():
        args[name] = rng.choice(_param_values(spec))
    return {**option, "args": args}


def _expand(option, cap=8):
    """Concrete variants of an option for look-ahead. An option without params is its own variant."""
    params = option.get("params")
    if not params:
        return [option]
    names = list(params)
    combos = list(itertools.product(*[_param_values(params[n]) for n in names]))
    if len(combos) > cap:
        idx = sorted({round(i * (len(combos) - 1) / (cap - 1)) for i in range(cap)})
        combos = [combos[i] for i in idx]
    out = []
    for combo in combos:
        args = dict(option.get("args", {}))
        args.update(dict(zip(names, combo, strict=True)))
        out.append({**option, "args": args})
    return out


def _same_option(a, b):
    return a["id"] == b["id"] and json.dumps(a.get("args", {}), sort_keys=True) == json.dumps(b.get("args", {}), sort_keys=True)


# ---------------------------------------------------------------- runtime


def _load():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        _die("there is no game in progress in this folder: run `python engine.py new` first")
    except ValueError:
        _die("state.json is damaged (it is not valid JSON): run `python engine.py replay --apply` to rebuild it "
             "from history.jsonl, or `python engine.py new <seed>` to start again")


def _save(s):
    """Atomic: serialize first, so a non-JSON state raises before the old state.json is touched."""
    data = json.dumps(s, indent=1)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
    os.replace(tmp, STATE_FILE)


def _append_log(lines):
    if not lines:
        return
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


def _turn_json(g, s, events):
    opts = g.options(s) if not s.get("_ended") else []
    return {
        "turn": min(s["_turn"], g.turns),
        "turns": g.turns,
        "status": g.status_line(s),
        "events": events,
        "visible": g.visible(s),
        "options": opts,
        "ended": s.get("_ended"),
        # anything here means the engine has a bug: stop, do not narrate over it, fix the engine
        "integrity": K.integrity(g, s, events, opts),
    }


def _new(g, seed):
    rng = RNG(seed)
    s = g.init_state(rng)
    s["_seed"] = seed
    s["_turn"] = 1
    s["_ended"] = None
    s["_rng"] = rng.getstate()
    return s, rng


def _find(opts, action_id, args):
    """The one option with this id whose args do not contradict `args`. Params are not checked here."""
    args = args or {}
    cands = [o for o in opts if o["id"] == action_id]
    if not cands:
        raise IllegalAction(f"illegal action {action_id!r}", [o["id"] for o in opts])

    def conflicts(o):
        oa = o.get("args", {})
        return [k for k, v in args.items() if k in oa and (oa[k] != v or isinstance(oa[k], bool) != isinstance(v, bool))]

    ok = [o for o in cands if not conflicts(o)]
    if len(ok) == 1:
        return ok[0]
    shown = [o.get("args", {}) for o in cands]
    if not ok:
        raise IllegalAction(f"action {action_id!r} is offered with {shown}, not with {args}", shown)
    raise IllegalAction(f"action {action_id!r} has {len(ok)} options; pass args to pick one", [o.get("args", {}) for o in ok])


def _match(opts, action_id, args):
    """The one legal option for (id, args), with params validated. Same-id options are told apart by args;
    args that contradict the option's own args, or a param outside its range, are rejected."""
    o = _find(opts, action_id, args)
    merged = dict(o.get("args", {}))
    merged.update(args or {})
    _clean_args(o, merged)
    return o


def _norm(pick, opts):
    """Turn whatever a policy returned into one concrete option dict (params filled in) from opts."""
    try:
        if isinstance(pick, dict):
            o, extra = _find(opts, pick["id"], pick.get("args", {})), pick.get("args", {})
        elif isinstance(pick, (tuple, list)) and len(pick) == 2:
            o, extra = _find(opts, pick[0], pick[1]), pick[1]
        else:
            cands = [x for x in opts if x["id"] == pick]
            if not cands:
                raise IllegalAction(f"policy returned illegal action {pick!r}", [x["id"] for x in opts])
            o, extra = cands[0], {}
        return _concrete_first(o, extra)
    except IllegalAction:
        if _LENIENT:  # ablation: a banned action was the heuristic's pick; fall back to the first legal option
            return _concrete_first(opts[0])
        raise


def _is_forced(opts):
    """One option, and no real choice inside it (a param with a single legal value is no choice)."""
    if len(opts) != 1:
        return False
    return not any(len(_param_values(spec)) > 1 for spec in (opts[0].get("params") or {}).values())


def _step(g, s, action_id, args):
    """One turn: the player's action, then dusk, then the turn counter goes up. `_turn` is the turn being played
    during apply, advance and check_end."""
    if s.get("_ended"):
        return s, ["Game is over."], []
    rng = RNG(s["_seed"], s["_rng"])
    chosen = _match(g.options(s), action_id, args)
    merged = _clean_args(chosen, {**chosen.get("args", {}), **(args or {})})
    events = list(g.apply(s, action_id, merged, rng) or [])
    end = s.get("_ended") or g.check_end(s)
    phase = "action"
    if not end:
        events += list(g.advance(s, rng) or [])
        end = s.get("_ended") or g.check_end(s)
        phase = "dusk"
        if not end:
            s["_turn"] += 1
            if s["_turn"] > g.turns:
                end = g.final_check(s)
                phase = "budget"
    if end:
        s["_ended"] = {**end, "phase": phase}
    s["_rng"] = rng.getstate()
    return s, events, rng.log


# ---------------------------------------------------------------- policies


def _rollout(g, s, option, prng):
    """Play one option, then the heuristic to the end, from a copy of s. Return 1 for a win."""
    return _rollout_seeded(g, s, option, prng.randrange(1, 10**9), prng.randrange(1, 10**9))


def _rollout_seeded(g, s, option, dice_seed, policy_seed):
    saved = list(g._hits)
    try:
        s2 = copy.deepcopy(s)
        s2["_rng"] = RNG(dice_seed).getstate()
        g.resample_hidden(s2, RNG(dice_seed ^ 0x5BD1E995))
        hrng = RNG(policy_seed)
        s2, _, _ = _step(g, s2, option["id"], option.get("args", {}))
        guard = 0
        while not s2.get("_ended") and guard < g.turns + 3:
            opts = g.options(s2)
            if not opts:
                break
            pick = _norm(g.heuristic(s2, opts, hrng), opts)
            s2, _, _ = _step(g, s2, pick["id"], pick.get("args", {}))
            guard += 1
        end = s2.get("_ended")
        return 1 if end and end["result"] == "win" else 0
    finally:
        g._hits = type(g._hits)(saved)


def _evaluate_wins(g, s, opts, prng, k):
    """Per option, a list of k outcomes (1 win, 0 loss). Every option sees the same k dice seeds
    (paired rollouts), so a difference between options is the option, not luck."""
    seeds = [(prng.randrange(1, 10**9), prng.randrange(1, 10**9)) for _ in range(k)]
    return [[_rollout_seeded(g, s, o, a, b) for a, b in seeds] for o in opts]


def _evaluate(g, s, opts, prng, k):
    return [sum(w) / k for w in _evaluate_wins(g, s, opts, prng, k)]


def _lookahead(g, s, opts, prng, k):
    """Pick the concrete option whose rollouts win most. The heuristic's own pick is always a candidate. Big menus
    get a cheap first pass, then the top three (plus the heuristic's pick) are re-judged with twice the rollouts.
    Ties go to the heuristic's pick, then to chance, never to list order."""
    hp = _norm(g.heuristic(s, opts, RNG(prng.randrange(1, 10**9))), opts)
    cands = [c for o in opts for c in _expand(o)]
    hp_i = next((i for i, c in enumerate(cands) if _same_option(c, hp)), None)
    if hp_i is None:
        cands.append(hp)
        hp_i = len(cands) - 1
    scores = _evaluate(g, s, cands, prng, k if len(cands) <= 8 else max(3, k // 2))
    if len(cands) > 3:
        order = sorted(range(len(cands)), key=lambda i: (-scores[i], prng.random()))[:3]
        if hp_i not in order:
            order[-1] = hp_i
        fine = _evaluate(g, s, [cands[i] for i in order], prng, k * 2)
        for i, sc in zip(order, fine, strict=True):
            scores[i] = 1.0 + sc  # finalists outrank everything judged only once
    top = max(scores)
    best = [i for i, sc in enumerate(scores) if sc == top]
    if hp_i in best:
        return cands[hp_i]
    return cands[prng.choice(best)]


def _validate_opts(opts, turn):
    seen = []
    for o in opts:
        if "id" not in o or "label" not in o:
            raise RuntimeError(f"malformed option at turn {turn}: {o!r}")
        key = (o["id"], json.dumps(o.get("args", {}), sort_keys=True))
        if key in seen:
            raise RuntimeError(f"duplicate option {key} at turn {turn}")
        seen.append(key)
        for name, spec in (o.get("params") or {}).items():
            if "choices" in spec:
                if not spec["choices"]:
                    raise RuntimeError(f"option {o['id']!r} param {name!r} has no choices at turn {turn}")
            elif not ("min" in spec and "max" in spec and spec["min"] <= spec["max"]):
                raise RuntimeError(f"option {o['id']!r} param {name!r} has a bad range at turn {turn}: {spec}")


def _play(g, seed, policy, k, prng, stats):
    g._hits = type(g._hits)()
    s, rng = _new(g, seed)
    stats["h0"] = {
        k: v for k, v in (s.get("hidden") or {}).items()
        if isinstance(v, (int, str)) and not isinstance(v, bool) and len(str(v)) <= 12
    }
    game = {"picks": Counter(), "growth": {"start": K.growth_value(g, s), "mid": None, "end": None}, "tier_max": None, "tier2_turn": None}
    mark = K.growth_mark(g)
    ladder = getattr(g, "LADDER", None) or {}
    while not s.get("_ended"):
        s = json.loads(json.dumps(s))  # real play saves and reloads every turn; so does selftest
        if mark and game["growth"]["mid"] is None and s["_turn"] >= mark:
            game["growth"]["mid"] = K.growth_value(g, s)
        _note_tier(g, s, ladder, game)
        opts = g.options(s)
        if not opts:
            raise RuntimeError(f"no legal options at turn {s['_turn']}")
        _validate_opts(opts, s["_turn"])
        stats["n_opts"].append(len(opts))
        for o in opts:
            stats["offered"][o["id"]] += 1
        if policy == "random":
            pick = _concrete_random(rng.choice(opts), rng)
        elif policy == "lookahead":
            pick = _lookahead(g, s, opts, prng, k)
        else:
            pick = _norm(g.heuristic(s, opts, rng), opts)
        stats["picked"][pick["id"]] += 1
        game["picks"][pick["id"]] += 1
        s, _, log = _step(g, s, pick["id"], pick.get("args", {}))
        stats["checks"] += sum(1 for ln in log if " need " in ln)  # dice the player rolled against a target
        if s["_turn"] > g.turns + 2:
            raise RuntimeError("turn counter ran past budget; check_end never fired")
    _note_tier(g, s, ladder, game)
    game["growth"]["end"] = K.growth_value(g, s)
    if mark and game["growth"]["mid"] is None:
        game["growth"]["mid"] = game["growth"]["end"]  # the game ended before the mark
    game["picks"] = dict(game["picks"])
    stats["game"] = game
    return s


def _note_tier(g, s, ladder, game):
    if not ladder:
        return
    v = K.numeric_view(g, s).get(ladder.get("key"))
    if v is None:
        return
    if game["tier_max"] is None or v > game["tier_max"]:
        game["tier_max"] = v
    if v >= 2 and game["tier2_turn"] is None:  # lit-ok: tier 2 is the second rung by definition
        game["tier2_turn"] = s["_turn"]


# ---------------------------------------------------------------- selftest (serial and parallel)


def _run_games(g, seeds, policy, k):
    results = []
    stats = {"n_opts": [], "offered": Counter(), "picked": Counter(), "checks": 0}
    tag_games = Counter()
    for seed in seeds:
        prng = random.Random(4242 + seed)
        try:
            s = _play(g, seed, policy, k, prng, stats)
        except Exception as e:  # noqa: BLE001
            results.append({"seed": seed, "crash": f"{type(e).__name__}: {e}"})
            continue
        for t in g._hits:
            tag_games[t] += 1
        game = stats.pop("game", {})
        results.append({
            "seed": seed, "result": s["_ended"]["result"], "turn": s["_turn"], "reason": s["_ended"]["reason"],
            "h0": stats.pop("h0", {}), "picks": game.get("picks", {}), "growth": game.get("growth"),
            "tier_max": game.get("tier_max"), "tier2_turn": game.get("tier2_turn"),
        })
    return results, stats, tag_games


def _summarize(g, n, policy, results, stats, tag_games, slack=0.0):
    wins = [r for r in results if r.get("result") == "win"]
    crashes = [r for r in results if "crash" in r]
    turns = [min(r["turn"], g.turns) for r in results if "turn" in r and r["turn"]]
    played = max(1, n - len(crashes))
    early_cut = int(g.turns * 0.7)
    early = sum(1 for t in turns if t < early_cut)
    summary = {
        "policy": policy,
        "games": n,
        "wins": len(wins),
        "win_rate": round(len(wins) / n, 2),
        "crashes": len(crashes),
        "turn_min": min(turns) if turns else None,
        "turn_avg": round(sum(turns) / len(turns), 1) if turns else None,
        "turn_max": max(turns) if turns else None,
        "early_wins_before_half": sum(1 for r in wins if r["turn"] < g.turns * 0.5),
        "early_end_rate": round(early / n, 2),
        "options_avg": round(sum(stats["n_opts"]) / len(stats["n_opts"]), 1) if stats["n_opts"] else None,
        "options_max": max(stats["n_opts"]) if stats["n_opts"] else None,
        "dice_per_game": round(stats.get("checks", 0) / played, 2),
        "sample_crashes": crashes[:3],
        "sample_reasons": sorted({r.get("reason", "") for r in results})[:8],
    }
    flags, soft = [], []

    def band(msg, miss):
        """A miss within `slack` (granted once the tuning cap is reached) is a warning, not a flag."""
        (soft if miss <= slack else flags).append(msg + (" (accepted: within the tuning-cap slack)" if miss <= slack else ""))

    if crashes:
        flags.append(f"CRASH: fix before presenting ({crashes[0]['crash'][:140]})")
    if policy == "random" and summary["win_rate"] > RANDOM_MAX:
        band(f"TOO EASY: random play wins {summary['win_rate']:.0%}, more than {RANDOM_MAX:.0%}", summary["win_rate"] - RANDOM_MAX)
    if policy == "heuristic":
        lo, hi = HEURISTIC_BAND
        if summary["win_rate"] < lo:
            band(f"TOO HARD: sensible play wins {summary['win_rate']:.0%}, under {lo:.0%}", lo - summary["win_rate"])
        if summary["win_rate"] > hi:
            band(f"TOO EASY: sensible play wins {summary['win_rate']:.0%}, over {hi:.0%}", summary["win_rate"] - hi)
        if summary["early_end_rate"] > 0.15:
            flags.append(f"SHORT GAMES: more than 15 percent ended before turn {early_cut} (70 percent of the budget)")
        if turns and summary["turn_avg"] < 0.75 * g.turns:
            flags.append(f"SHORT GAMES: heuristic turn_avg {summary['turn_avg']} is under 75 percent of the {g.turns}-turn budget")
    early_wins = summary["early_wins_before_half"]
    if early_wins and (policy != "random" or early_wins / n > 0.03):  # an occasional lucky random win is not a design flaw
        flags.append(f"EARLY WIN: {early_wins} {policy} win(s) landed before the midpoint; lengthen the goal or slow the economy")
    imbalance = []
    for key in sorted({k for r in results for k in r.get("h0", {})}):
        groups = {}
        for r in results:
            if key in r.get("h0", {}) and "result" in r:
                groups.setdefault(r["h0"][key], []).append(r["result"] == "win")
        if 2 <= len(groups) <= 6 and all(len(v) >= 20 for v in groups.values()):
            rates = {str(k): round(sum(v) / len(v), 2) for k, v in groups.items()}
            if max(rates.values()) - min(rates.values()) > 0.35:
                imbalance.append([key, rates])
    summary["hidden_balance"] = imbalance
    summary["flags"] = flags
    summary["warnings"] = soft
    raw = {"stats": stats, "tag_games": tag_games, "played": played, "results": results}
    return summary, raw


DICE_RANDOM_MIN = 1.0   # the game has player checks when random play meets at least this many a game
DICE_SENSIBLE_MIN = 0.5  # and sensible play that rolls fewer than this a game is dodging every one of them


def dice_warning(random_summary, heuristic_summary, lookahead_summary=None):
    """The game has rolls, but a sensible player never takes one: the drama is in the dice and nobody meets them.
    Low Wells (2026-11-06): militia were the only roll and the winning line walked around every one."""
    r = random_summary.get("dice_per_game") or 0
    h = heuristic_summary.get("dice_per_game") or 0
    lk = (lookahead_summary or {}).get("dice_per_game")
    if r < DICE_RANDOM_MIN or h >= DICE_SENSIBLE_MIN:
        return None
    if lk is not None and lk >= DICE_SENSIBLE_MIN:
        return None  # the search finds the rolls worth taking; the heuristic is just timid
    return (
        f"DICE: random play rolls {r:.1f} dice a game against a target, sensible play {h:.1f}; every roll is avoidable, so the "
        "dice never come out. Put a roll on the main line, or make the risky move pay enough that a sensible player takes it"
    )


def _engine_file(g):
    try:
        path = inspect.getsourcefile(type(g))
        return os.path.abspath(path) if path and os.path.exists(path) else None
    except (TypeError, OSError):
        return None


_GAMES = {}


def _load_game(path, cls_name, C, banned=None):
    """Import the engine file in this process and build a game (used by worker processes)."""
    key = (path, cls_name)
    if key not in _GAMES:
        spec = importlib.util.spec_from_file_location("gm_engine_worker", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["gm_engine_worker"] = mod
        spec.loader.exec_module(mod)
        _GAMES[key] = getattr(mod, cls_name)
    g = _GAMES[key]()
    g.C = copy.deepcopy(C)
    if banned:
        _ban(g, banned)
    return g


def _ban(g, banned):
    """Make `banned` action ids unavailable (ablation). Never leaves the player with no option."""
    global _LENIENT
    base = g.options

    def filtered(s):
        opts = base(s)
        kept = [o for o in opts if o["id"] not in banned]
        return kept or opts

    g.options = filtered
    _LENIENT = True


def _worker(payload):
    kind = payload[0]
    if kind == "games":
        _, path, cls_name, C, banned, policy, k, seeds = payload
        g = _load_game(path, cls_name, C, banned)
        results, stats, tags = _run_games(g, seeds, policy, k)
        return results, {"n_opts": stats["n_opts"], "offered": dict(stats["offered"]), "picked": dict(stats["picked"]), "checks": stats["checks"]}, dict(tags)
    if kind == "profile":
        import gm_analysis
        _, path, cls_name, C, seeds, k = payload
        return gm_analysis.profile_games(_load_game(path, cls_name, C), seeds, k)
    if kind == "mutate":
        import gm_mutate
        _, path, cls_name, C, ids = payload
        return gm_mutate.run_chunk(path, cls_name, C, ids)
    raise ValueError(kind)


def _workers():
    return max(1, min(os.cpu_count() or 2, 8))


def _parallel_ok(g):
    return _engine_file(g) is not None and _workers() > 1 and not os.environ.get("GM_SERIAL")


def _pmap(payloads):
    with ProcessPoolExecutor(max_workers=min(len(payloads), _workers())) as ex:
        return list(ex.map(_worker, payloads))


def _selftest(g, n, policy, k=6, banned=None, slack=0.0):
    """Play n games with one policy. Returns (public summary, raw counters for `check`).
    Uses worker processes when the engine is a file and there are enough games."""
    if banned is None and n >= 16 and _parallel_ok(g):
        try:
            w = _workers()
            payloads = [("games", _engine_file(g), type(g).__name__, g.C, None, policy, k, list(range(1 + i, n + 1, w))) for i in range(w)]
            parts = _pmap([p for p in payloads if p[-1]])
            results, stats, tags = [], {"n_opts": [], "offered": Counter(), "picked": Counter(), "checks": 0}, Counter()
            for r, st, tg in parts:
                results += r
                stats["n_opts"] += st["n_opts"]
                stats["offered"].update(st["offered"])
                stats["picked"].update(st["picked"])
                stats["checks"] += st.get("checks", 0)
                tags.update(tg)
            results.sort(key=lambda r: r["seed"])
            return _summarize(g, n, policy, results, stats, tags, slack)
        except Exception:  # noqa: BLE001  fall back to one process
            pass
    results, stats, tags = _run_games(g, range(1, n + 1), policy, k)
    return _summarize(g, n, policy, results, stats, tags, slack)


# ---------------------------------------------------------------- check and sweep


def _sheet_flags(g):
    flags, warnings = [], []
    if g.RULES:
        text = ""
        try:
            text = g.rules()
        except (KeyError, IndexError, ValueError) as e:
            flags.append(f"SHEET: RULES template does not format against CONSTANTS ({e!r})")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if len(lines) > RULE_LINES_MAX:
            flags.append(f"SHEET: {len(lines)} rule lines; the limit is {RULE_LINES_MAX}")
        for i, ln in enumerate(lines, 1):
            words = len(ln.split())
            if words > RULE_WORDS_FLAG:
                flags.append(f"SHEET: rule {i} has {words} words; the limit is {RULE_WORDS_FLAG}. Split a mechanic out or cut one")
            elif words > RULE_WORDS_WARN:
                warnings.append(f"SHEET: rule {i} has {words} words; aim for {RULE_WORDS_WARN} or fewer, about two mechanics a line")
        for key in g.C:
            if key.startswith("_"):
                continue
            if not re.search(r"\{" + re.escape(key) + r"[}:!\[.|]", g.RULES):
                flags.append(f"SHEET: constant {key} is not on the rulesheet (list it, or rename _{key} if tuning-only)")
    else:
        warnings.append("SHEET: no RULES template, so the sheet can drift from the code; move it into RULES")
    return flags, warnings


def _tune_count():
    try:
        with open(TUNE_FILE, encoding="utf-8") as f:
            return int(f.read().partition(":")[0] or 0)
    except (OSError, ValueError):
        return 0


def _engine_hash(path):
    """A hash of the engine's logic and numbers that ignores text, the rule tests and the heuristic, so a wording
    edit, a new test or a better heuristic is not a new tuning round."""
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in ("rule_tests", "heuristic"):
                node.body = [ast.Pass()]  # new tests and a better heuristic are not a new tuning of the game
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                node.value = ""
        return hashlib.sha1(ast.dump(tree).encode("utf-8")).hexdigest()[:10]
    except Exception:  # noqa: BLE001
        return None


def _bump_tune(engine_path):
    """Count a tuning round only when the engine's logic or numbers changed since the last counted run."""
    n, last = 0, None
    try:
        with open(TUNE_FILE, encoding="utf-8") as f:
            raw = f.read().strip()
        n_text, _, last = raw.partition(":")
        n = int(n_text or "0")
    except (OSError, ValueError):
        n, last = 0, None
    h = _engine_hash(engine_path) if engine_path else None
    if h is not None and h == last and n > 0:
        return n, False
    n += 1
    try:
        with open(TUNE_FILE, "w", encoding="utf-8") as f:
            f.write(f"{n}:{h or ''}")
    except OSError:
        pass
    return n, True


def _heuristic_reads_hidden(g):
    try:
        src = inspect.getsource(type(g).heuristic)
    except (TypeError, OSError):
        return False
    return bool(re.search(r"""["']hidden["']|\.hidden\b""", src))


def _check(g, free=False, engine_path=None, quick=False):
    rnd = None
    counted = True
    engine_path = engine_path or _engine_file(g)
    if not free:
        rnd, counted = _bump_tune(engine_path)
    n_r, n_h, n_l, k_l = (100, 100, 10, 6) if quick else (300, 300, 100, 8)  # quick is for the regression suite
    if quick:
        os.environ["GM_SERIAL"] = "1"
    n_now = rnd if rnd is not None else _tune_count()
    slack = 0.10 if n_now >= TUNE_CAP else 0.0  # at the cap, a band miss within 0.1 is accepted, as the cap note says
    r, rr = _selftest(g, n_r, "random", slack=slack)
    h, hr = _selftest(g, n_h, "heuristic", slack=slack)
    lk, lr = _selftest(g, n_l, "lookahead", k=k_l)
    flags = [f"random: {f}" for f in r["flags"]] + [f"heuristic: {f}" for f in h["flags"]]
    flags += [f"lookahead: {f}" for f in lk["flags"] if f.startswith(("CRASH", "EARLY"))]
    warnings = [f"random: {w}" for w in r["warnings"]] + [f"heuristic: {w}" for w in h["warnings"]]
    for key, rates in h.get("hidden_balance", []):
        warnings.append(
            f"BALANCE: the heuristic's win rate depends on the hidden starting value `{key}`: {rates}. "
            "One setting makes the game much easier or harder than the others; the sheet promises one game"
        )

    dice = dice_warning(r, h, lk)
    if dice:
        warnings.append(dice)

    sheet_flags, sheet_warn = _sheet_flags(g)
    flags += sheet_flags
    warnings += sheet_warn

    me = sys.modules[__name__]
    uni_flags, uni_warn, uni_info = K.run_universal(g, me, engine_path)
    flags += uni_flags
    warnings += uni_warn
    flags += K.run_rule_tests(g, me)

    offered = set(rr["stats"]["offered"]) | set(hr["stats"]["offered"]) | set(lr["stats"]["offered"])
    if g.ACTIONS:
        for a in g.ACTIONS:
            if a not in offered:
                flags.append(f"ACTION: {a} was never offered in any selftest game (dead, or hidden by a filter)")
        for a in sorted(offered - set(g.ACTIONS)):
            flags.append(f"ACTION: {a} is offered but not in ACTIONS (so the sheet may not name it)")
    else:
        warnings.append("ACTIONS not declared, so hidden or dead actions cannot be detected; list every id")

    tag_hits = Counter()
    for raw in (rr, hr, lr):
        tag_hits.update(raw["tag_games"])
    if g.TAGS:
        for t in g.TAGS:
            if tag_hits[t] == 0:
                flags.append(f"TAG: {t} never fired in any selftest game (unreachable)")
        for t in sorted(set(tag_hits) - set(g.TAGS)):
            flags.append(f"TAG: {t} fired but is not in TAGS (typo?)")
        for t in g.TAGS:
            frac = hr["tag_games"][t] / hr["played"]
            if tag_hits[t] > 0 and frac < 0.05:
                warnings.append(f"TAG: {t} fires in {frac:.0%} of heuristic games (rare; fine for a twist, a problem for a core rule)")
    else:
        warnings.append("TAGS not declared, so unreachable twists and levers cannot be detected")

    # v4: growth, ladder, paths, from the games already played
    h_rows = [r for r in hr.get("results", []) if "result" in r]
    gf, gw = K.growth_problems(g, [dict(r.get("growth") or {}) for r in h_rows])
    flags += gf
    warnings += gw
    lf, lw = K.ladder_problems(g, h_rows)
    flags += lf
    warnings += lw
    pf, pw = K.paths_problems(g, h_rows + [r for r in lr.get("results", []) if "result" in r])
    flags += pf
    warnings += pw
    if getattr(g, "GROWTH", None) and not (24 <= g.turns <= 40):  # lit-ok: the v4 turn range
        warnings.append(f"TURNS: a game that grows wants 24 to 40 turns to compound; this one has {g.turns}")

    for gid in getattr(g, "GAMBITS", {}) or {}:
        if g.ACTIONS and gid not in g.ACTIONS:
            flags.append(f"GAMBIT: {gid} is declared in GAMBITS but not in ACTIONS")
        elif gid in offered and hr["stats"]["picked"][gid] == 0 and lr["stats"]["picked"][gid] == 0:
            warnings.append(f"GAMBIT: nobody ever plays {gid}; a gambit no sensible player takes is a decoy, so make its prize worth the risk")

    for a in sorted(offered):
        h_pick, l_pick = hr["stats"]["picked"][a], lr["stats"]["picked"][a]
        l_off = lr["stats"]["offered"][a]
        if h_pick == 0 and l_pick == 0 and hr["stats"]["offered"][a] > 0:
            warnings.append(f"ACTION: {a} is offered but neither the heuristic nor look-ahead ever picks it (dead or dominated)")
        elif l_pick == 0 and l_off >= 20:
            warnings.append(f"ACTION: look-ahead never picks {a} in {l_off} offers (dominated?)")
        elif h_pick == 0 and l_pick > 0:
            warnings.append(f"ACTION: the heuristic never picks {a} but look-ahead does ({l_pick} times); teach the heuristic or the sheet")

    lo, hi = LOOKAHEAD_BAND
    se = (0.25 / max(1, n_l)) ** 0.5
    if lk["win_rate"] < lo:
        warnings.append(f"BAND: look-ahead wins {lk['win_rate']:.0%}, under {lo:.0%}; a thoughtful player may find it too hard")
    if lk["win_rate"] > hi:
        warnings.append(f"BAND: look-ahead wins {lk['win_rate']:.0%}, over {hi:.0%}; the best line is too obvious")
    if lk["win_rate"] + se < h["win_rate"]:
        warnings.append("BAND: look-ahead does clearly worse than the heuristic; choices may not matter, or the heuristic is the better player")
    if lk["win_rate"] < lo and n_l >= 60:
        warnings.append(f"BAND: look-ahead searches {k_l} rollouts per option; a game with many options can look harder than it is (20 rollouts raised one game from 48% to 75%)")
    if lk["win_rate"] - h["win_rate"] > 0.45:
        warnings.append(
            f"HEURISTIC: look-ahead wins {lk['win_rate']:.0%} against the heuristic's {h['win_rate']:.0%}. The heuristic is weak; "
            "profile and autopsy use it for everything after a move, so strengthen it"
        )
    if uni_info.get("hidden_seen") and type(g).resample_hidden is Game.resample_hidden:
        warnings.append(
            "HIDDEN: the state holds hidden facts but resample_hidden is not defined, so look-ahead, profile and autopsy know the answer. "
            "Define resample_hidden(self, s, rng) to redraw the hidden facts consistent with what the player has seen"
        )
    if _heuristic_reads_hidden(g):
        warnings.append("HEURISTIC: the heuristic reads hidden state; a policy that cheats makes the bands and the autopsy meaningless")

    if engine_path:
        try:
            import gm_mutate
            lits = gm_mutate.literal_report(engine_path, type(g).__name__)
            if lits:
                warnings.append(
                    "LITERAL: numbers written into the code instead of CONSTANTS (the sheet cannot show them, tuning cannot reach them): "
                    + "; ".join(lits[:6]) + " (add `# lit-ok` to a line where the number is structural)"
                )
        except Exception:  # noqa: BLE001
            pass

    mutation = None
    if not quick and engine_path:
        try:
            import gm_mutate
            mutation = gm_mutate.run_mutation(g, me, engine_path)
        except Exception as e:  # noqa: BLE001
            warnings.append(f"TESTSTRENGTH: the mutation pass failed: {type(e).__name__}: {e}")
        if mutation and mutation["tested"] >= 10:
            shown = "; ".join(mutation["survivors"][:5])
            msg = f"TESTSTRENGTH: the rule tests and checks caught {mutation['killed']} of {mutation['tested']} code mutations ({mutation['rate']:.0%}). Survivors: {shown}"
            if mutation["rate"] < 0.5:
                flags.append(msg + ". Add rule tests that pin these behaviors")
            elif mutation["rate"] < 0.85:
                warnings.append(msg)

    out = {
        "verdict": "CLEAN" if not flags else "FLAGS",
        "flags": flags,
        "warnings": warnings,
        "random": {"win": r["win_rate"], "turn_avg": r["turn_avg"], "dice": r["dice_per_game"], "reasons": r["sample_reasons"][:4]},
        "heuristic": {"win": h["win_rate"], "turn_avg": h["turn_avg"], "dice": h["dice_per_game"], "reasons": h["sample_reasons"][:4]},
        "lookahead": {"win": lk["win_rate"], "turn_avg": lk["turn_avg"], "dice": lk["dice_per_game"]},
        "options": {"avg": h["options_avg"], "max": max(r["options_max"] or 0, h["options_max"] or 0)},
        "universal": uni_info,
    }
    if mutation:
        out["mutation"] = {
            "tested": mutation["tested"], "killed": mutation["killed"], "rate": round(mutation["rate"], 2),
            "survivors": mutation["survivors"][:10],
        }
    if rnd is not None:
        out["tuning_round"] = f"{rnd} of {TUNE_CAP}" + ("" if counted else " (same logic and numbers as the last counted run; not a new round)")
        if rnd >= TUNE_CAP:
            out["note"] = (
                "TUNING CAP: stop tuning after this round. Fix crash, sheet, action and tag flags only. "
                "Accept band misses within 0.1 and list the remaining warnings to the player as known rough edges, "
                "or fix the design instead of the numbers. Wording edits and `check --free` do not count as rounds."
            )
    return out


def _cast(old, text):
    if isinstance(old, bool):
        return text.strip().lower() in ("1", "true", "yes")
    if isinstance(old, int):
        return int(text)
    if isinstance(old, float):
        return float(text)
    try:
        return json.loads(text)
    except ValueError:
        return text


def _sweep(g, specs, n, lookahead=False):
    keys, grids = [], []
    for spec in specs:
        if "=" not in spec:
            raise SystemExit(f"sweep: expected KEY=v1,v2 but got {spec!r}")
        k, vals = spec.split("=", 1)
        if k not in g.C:
            raise SystemExit(f"sweep: {k} is not in CONSTANTS ({sorted(g.C)})")
        keys.append(k)
        grids.append([_cast(g.C[k], v) for v in vals.split(",")])
    combos = list(itertools.product(*grids))
    if len(combos) > 30:
        raise SystemExit(f"sweep: {len(combos)} combinations; keep it to 30 or fewer")
    base = dict(g.C)
    lines = []
    for combo in combos:
        g.C = dict(base)
        g.C.update(dict(zip(keys, combo, strict=True)))
        r, _ = _selftest(g, n, "random")
        h, _ = _selftest(g, n, "heuristic")
        label = " ".join(f"{k}={v}" for k, v in zip(keys, combo, strict=True))
        flag_n = len(r["flags"]) + len(h["flags"])
        line = (
            f"{label} | random {r['win_rate']:.2f} | heuristic {h['win_rate']:.2f} turns {h['turn_avg']} "
            f"early {h['early_end_rate']:.2f}"
        )
        if lookahead:
            n_lk = max(24, n // 4)
            lk, _ = _selftest(g, n_lk, "lookahead", k=8)
            line += f" | look-ahead {lk['win_rate']:.2f} (+/-{(0.25 / n_lk) ** 0.5:.2f}, {n_lk} games)"
        lines.append(line + f" | flags {flag_n}")
    g.C = base
    return lines


def _fingerprint(g):
    """Mechanical traits for the sameness detector. The GM adds the judged traits."""
    s, _ = _new(g, 1)
    opts = g.options(s)
    summary, raw = _selftest(g, 24, "heuristic")
    has_params = any(o.get("params") for o in opts) or any(
        o.get("params") for o in g.options(_new(g, 2)[0])
    )
    n = len(getattr(g, "TRACKED", []))
    return {
        "actions": list(g.ACTIONS),
        "tracked_count": str(n) if 1 <= n <= 3 else None,
        "turn_band": "short" if g.turns <= 14 else "mid" if g.turns <= 18 else "long",
        "decision_unit_hint": "allocate, bid or place (options carry params)" if has_params else "pick-action unless the options are groups of targets (then assign or route)",
        "options_avg": summary["options_avg"],
        "turns": g.turns,
    }


def run(game_cls):
    try:
        _run(game_cls)
    except SystemExit:
        raise
    except IllegalAction as e:
        _die(e.msg, options=e.options)
    except ValueError as e:  # a number or value on the command line that does not parse
        _die("a value on the command line could not be read", detail=str(e))
    except Exception as e:  # noqa: BLE001 - a clean error, never a traceback, for the GM to read
        _die("engine crash", detail=f"{type(e).__name__}: {e}")


def _run(game_cls):
    g = game_cls()
    argv = sys.argv[1:]
    cmd = argv[0] if argv else "status"
    if cmd not in COMMANDS:
        _die(f"unknown command {cmd!r}", commands=COMMANDS)

    if cmd == "new":
        try:
            seed = int(argv[1]) if len(argv) > 1 else random.randrange(1, 10**6)
        except ValueError:
            _die(f"the seed must be a whole number, not {argv[1]!r}")
        s, rng = _new(g, seed)
        _save(s)
        for stale in (LOG_FILE, HISTORY_FILE):
            if os.path.exists(stale):
                os.remove(stale)
        _append_log([f"seed {seed}"] + rng.log)
        print(json.dumps(_turn_json(g, s, []), indent=1))
        return

    if cmd in ("profile", "ablate", "replay", "autopsy"):
        import gm_analysis

    if cmd == "profile":
        n = _posint(argv[1] if len(argv) > 1 else None, "games", 24)
        k = _posint(argv[2] if len(argv) > 2 else None, "rollouts", 20)
        print(json.dumps(gm_analysis.profile(g, n, k), indent=1))
        return

    if cmd == "ablate":
        n = _posint(argv[1] if len(argv) > 1 else None, "games", 60)
        print(json.dumps(gm_analysis.ablate(g, n), indent=1))
        return

    if cmd == "rules":
        print(g.rules())
        return

    if cmd == "selftest":
        n = _posint(argv[1] if len(argv) > 1 else None, "games", 200)
        policy = argv[2] if len(argv) > 2 else "random"
        if policy not in ("random", "heuristic", "lookahead"):
            _die(f"the policy must be random, heuristic or lookahead, not {policy!r}")
        summary, _ = _selftest(g, n, policy)
        print(json.dumps(summary, indent=1))
        return

    if cmd == "check":
        unknown = [a for a in argv[1:] if a not in ("--free", "--quick")]
        if unknown:
            _die(f"check takes only --free or --quick, not {unknown}; change CONSTANTS in the file, or use sweep to try values")
        try:
            result = _check(g, free="--free" in argv or "--quick" in argv, engine_path=os.path.abspath(sys.argv[0]), quick="--quick" in argv)
        except Exception as e:  # noqa: BLE001 - the checker must never die silently; a crash is a finding
            result = {"verdict": "FLAGS", "flags": [f"CRASH: check itself failed: {type(e).__name__}: {e}"], "warnings": []}
        print(json.dumps(result, indent=1))
        return

    if cmd == "trace":
        seed = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 7
        script = argv[argv.index("--do") + 1] if "--do" in argv and argv.index("--do") + 1 < len(argv) else None
        lines = K.trace(g, sys.modules[__name__], seed, "random" if "random" in argv else "heuristic", script)
        print(K.trace_hash(lines) if "--hash" in argv else "\n".join(lines))
        return

    if cmd == "texts":
        n = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 120
        print("\n".join(K.texts_report(g, sys.modules[__name__], n)))
        return

    if cmd == "fingerprint":
        print(json.dumps(_fingerprint(g), indent=1))
        return

    if cmd == "sweep":
        n = 150
        specs = []
        rest = argv[1:]
        i = 0
        while i < len(rest):
            if rest[i] == "--n" and i + 1 < len(rest):
                n = _posint(rest[i + 1], "--n")
                i += 2
            elif rest[i] == "--lookahead":
                i += 1
            else:
                specs.append(rest[i])
                i += 1
        if not specs:
            raise SystemExit("usage: sweep KEY=v1,v2 [KEY2=v1,v2] [--n 150] [--lookahead]")
        print("\n".join(_sweep(g, specs, n, lookahead="--lookahead" in argv)))
        return

    if cmd == "log":
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, encoding="utf-8") as f:
                print(f.read())
        return

    if cmd == "replay":
        print(json.dumps(gm_analysis.replay(g, apply="--apply" in argv), indent=1))
        return

    s = _load()

    if cmd == "status":
        print(json.dumps(_turn_json(g, s, []), indent=1))
        return

    if cmd == "board":
        print(g.board(s))
        return

    if cmd == "autopsy":
        k = _posint(argv[1] if len(argv) > 1 else None, "rollouts", 40)
        print(json.dumps(gm_analysis.autopsy(g, k), indent=1))
        return

    if cmd == "options":
        print(json.dumps([] if s.get("_ended") else g.options(s), indent=1))
        return

    if cmd == "step":
        if len(argv) < 2 or len(argv) > 3:
            _die("usage: step <action_id | #N> ['<json args>']; quote the JSON so it stays one argument", state_unchanged=True)
        if s.get("_ended"):
            _die("the game is over", ended=s["_ended"], state_unchanged=True)
        try:
            args = json.loads(argv[2]) if len(argv) > 2 else {}
        except ValueError:
            _die(f"the args must be a JSON object such as '{{\"name\": 3}}', not {argv[2]!r}", state_unchanged=True)
        if not isinstance(args, dict):
            _die(f"the args must be a JSON object, not {type(args).__name__}", state_unchanged=True)
        aid = argv[1]
        try:
            if aid.startswith("#"):
                opts = g.options(s)
                try:
                    idx = int(aid[1:]) - 1
                except ValueError:
                    _die(f"{aid!r} is not an option number; use #1, #2, ...", state_unchanged=True)
                if not 0 <= idx < len(opts):
                    raise IllegalAction(f"no option {aid}", [f"#{i + 1} {o['id']}" for i, o in enumerate(opts)])
                chosen = opts[idx]
                aid = chosen["id"]
                clash = [k for k in args if k in chosen.get("args", {}) and chosen["args"][k] != args[k]]
                if clash:
                    _die(f"{'#' + str(idx + 1)} already fixes {clash}; the JSON may only add the values of its params", state_unchanged=True)
                args = {**chosen.get("args", {}), **args}
            chosen = _match(g.options(s), aid, args)
            args = _clean_args(chosen, {**chosen.get("args", {}), **args})
            before = copy.deepcopy(s)
            s, events, log = _step(g, s, aid, args)
        except IllegalAction as e:
            _die(e.msg, options=e.options, state_unchanged=True)
        except Exception as e:  # noqa: BLE001 - an engine bug; the saved state is untouched
            _die("engine crash", detail=f"{type(e).__name__}: {e}", state_unchanged=True)
        # everything that can fail is done before anything is written, so a failure leaves state and history alone
        record = json.dumps({
            "turn": before["_turn"], "state": before, "id": chosen["id"], "args": args,
            "label": chosen["label"], "events": events, "ended": s["_ended"],
        })
        output = json.dumps(_turn_json(g, s, events), indent=1)
        json.dumps(s)
        with open(HISTORY_FILE, "a", encoding="utf-8") as hf:
            hf.write(record + "\n")
        _append_log([f"turn {before['_turn']} {aid}"] + log)
        _save(s)
        print(output)
        return

    _die(f"unknown command {cmd!r}", commands=COMMANDS)
