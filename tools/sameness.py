"""sameness.py: find traits that repeat across games, so a repeated trait can become a roll axis.

Every finished game gets a fingerprint (one JSON line in fingerprints.jsonl): the rolled axes plus
one value for each trait in traits.json. This tool reads the series and reports what stays the same.

Usage (run from anywhere):
    python sameness.py report [--file F] [--window N]   every trait: streak, window share, flags
    python sameness.py add '<json>' [--file F]          validate, append, then report on the newest game
    python sameness.py last [--file F]                  newest game against the games before it
    python sameness.py brief [--file F]                 what the next game must differ on
    python sameness.py novelty ENGINE=3 SET=12 GROWTH=2  the roll-layer novelty check; says which axes to reroll (FORM/CURRENCY for old games)
    python sameness.py verbs haul,light,shield          the mechanics-layer check against the last 10 games
    python sameness.py backlog [--file F]               write variation_backlog.md from the current flags
    python sameness.py phrases FILE [FILE ...]          4-word phrases that recur across game transcripts

Flags:
    STREAK     the same value in the last N games (N depends on how many values the trait has)
    DOMINANT   one value fills most of the recent window
    BENT       the trait is stuck although the roll behind it keeps changing: the roll is being bent
               into the same shape, so the table or the generator is not doing its job
    UNROLLED   no roll axis sits behind the trait; any repetition is habit, so add an axis
"""

import glob
import json
import os
import random
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
GM_ROOT = os.path.dirname(HERE)
TRAITS_FILE = os.path.join(GM_ROOT, "traits.json")
DEFAULT_FILE = os.path.join(GM_ROOT, "fingerprints.jsonl")
BACKLOG_FILE = os.path.join(GM_ROOT, "variation_backlog.md")

# trait names that are info, not enumerated in traits.json
EXTRA = {"result": ["win", "loss"]}


def load_vocab():
    with open(TRAITS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_games(path):
    games = []
    if not os.path.exists(path):
        return games
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                g = json.loads(line)
            except ValueError as e:
                raise SystemExit(f"{path} line {n}: not JSON ({e})") from None
            g.setdefault("order", n)
            games.append(g)
    games.sort(key=lambda g: g["order"])
    return games


def series(games, vocab):
    """Return {trait_name: {"values": [...], "k": int, "roll": axis or None, "enum": [...] or None, "kind": str}}"""
    out = {}
    for axis, k in vocab["roll_sizes"].items():
        out[f"roll.{axis}"] = {
            "values": [g.get("rolls", {}).get(axis) for g in games],
            "k": k, "roll": axis, "enum": None, "kind": "roll",
        }
    for name, spec in vocab["traits"].items():
        out[name] = {
            "values": [g.get("traits", {}).get(name) for g in games],
            "k": len(spec["values"]), "roll": spec.get("roll"), "enum": spec["values"], "kind": "trait",
        }
    out["result"] = {"values": [g.get("result") for g in games], "k": 2, "roll": None, "enum": EXTRA["result"], "kind": "info"}
    return out


def streak_threshold(k, vocab):
    t = vocab["thresholds"]["streak_min_by_cardinality"]
    return t["le3"] if k <= 3 else t["le8"] if k <= 8 else t["gt8"]


def runs(values):
    """Yield (value, start_index, length) for each run of equal non-None values."""
    i = 0
    while i < len(values):
        v = values[i]
        if v is None:
            i += 1
            continue
        j = i
        while j + 1 < len(values) and values[j + 1] == v:
            j += 1
        yield v, i, j - i + 1
        i = j + 1


def analyze(games, vocab, window=None):
    th = vocab["thresholds"]
    window = window or th["dominant_window"]
    ser = series(games, vocab)
    rows = []
    for name, s in ser.items():
        vals = s["values"]
        known = [v for v in vals if v is not None]
        if not known:
            continue
        thr = streak_threshold(s["k"], vocab)
        # current streak
        cur_v, cur_n = None, 0
        if vals and vals[-1] is not None:
            cur_v = vals[-1]
            for v in reversed(vals):
                if v == cur_v:
                    cur_n += 1
                else:
                    break
        # longest run
        longest = max(runs(vals), key=lambda r: r[2], default=(None, 0, 0))
        # window share
        win_vals = [v for v in vals[-window:] if v is not None]
        top_v, top_n = (Counter(win_vals).most_common(1)[0] if win_vals else (None, 0))
        share = top_n / len(win_vals) if win_vals else 0.0
        share_thr = th["dominant_share_le3"] if s["k"] <= 3 else th["dominant_share_gt3"]
        flags = []
        if cur_n >= thr:
            flags.append(f"STREAK({cur_n})")
        dominant = len(win_vals) >= th["dominant_min_games"] and share >= share_thr
        if dominant:
            flags.append(f"DOMINANT({share:.0%})")
        # BENT: a derived trait stays put while its roll keeps changing
        if s["kind"] == "trait" and s["roll"] and (cur_n >= thr or dominant):
            roll_vals = [g.get("rolls", {}).get(s["roll"]) for g in games][-window:]
            roll_vals = [v for v in roll_vals if v is not None]
            if len(roll_vals) >= 4 and len(set(roll_vals)) >= 0.6 * len(roll_vals):
                flags.append(f"BENT({s['roll']} varies, {len(set(roll_vals))} of {len(roll_vals)} distinct)")
        if s["kind"] == "trait" and not s["roll"] and flags:
            flags.append("UNROLLED")
        rows.append({
            "trait": name, "k": s["k"], "kind": s["kind"], "roll": s["roll"], "enum": s["enum"],
            "last": cur_v, "streak": cur_n, "longest": longest[2], "longest_value": longest[0],
            "longest_start": longest[1] + 1 if longest[2] else None,
            "top": top_v, "share": share, "n_window": len(win_vals), "flags": flags, "thr": thr,
        })
    return rows


def pair_similarity(a, b, vocab):
    names = list(vocab["traits"])
    same = [n for n in names if a.get("traits", {}).get(n) is not None and a["traits"].get(n) == b.get("traits", {}).get(n)]
    return len(same) / len(names), same


def print_report(rows, games, vocab, only_flagged=False):
    print(f"{len(games)} games. window {vocab['thresholds']['dominant_window']}. flags need streak >= k-based threshold or window share.")
    head = f"{'trait':18} {'k':>3} {'last':>13} {'run':>4} {'longest':>8} {'window top':>20}  flags"
    print(head)
    print("-" * len(head))
    for r in rows:
        if only_flagged and not r["flags"]:
            continue
        top = f"{r['top']} {r['share']:.0%} of {r['n_window']}" if r["top"] is not None else "-"
        lg = f"{r['longest']}x {r['longest_value']}" if r["longest"] > 1 else "1"
        print(f"{r['trait']:18} {r['k']:>3} {str(r['last']):>13} {r['streak']:>4} {lg:>8} {top:>20}  {' '.join(r['flags'])}")


def print_similar(games, vocab):
    if len(games) < 2:
        return
    last = games[-1]
    th = vocab["thresholds"]["similar_to_previous"]
    print()
    print(f"Newest game: {last.get('title', last.get('id'))}")
    prev = games[-6:-1]
    for g in reversed(prev):
        sim, same = pair_similarity(last, g, vocab)
        mark = "  <- TOO SIMILAR" if sim >= th else ""
        print(f"  vs {g.get('title', g.get('id'))}: {sim:.0%} of traits identical ({', '.join(same) or 'none'}){mark}")


def print_pairs(games, vocab):
    th = vocab["thresholds"]["similar_to_previous"]
    pairs = []
    for i in range(len(games)):
        for j in range(i + 1, len(games)):
            sim, same = pair_similarity(games[i], games[j], vocab)
            pairs.append((sim, i, j, same))
    if not pairs:
        return
    avg = sum(p[0] for p in pairs) / len(pairs)
    print()
    print(f"Pairwise: average {avg:.0%} of traits identical across {len(pairs)} pairs. Pairs at or above {th:.0%}:")
    hot = sorted([p for p in pairs if p[0] >= th], reverse=True)[:12]
    if not hot:
        print("  none")
    for sim, i, j, same in hot:
        print(f"  {sim:.0%}  {games[i].get('title')}  /  {games[j].get('title')}  ({', '.join(same)})")


def brief(rows, vocab):
    rng = random.SystemRandom()
    flagged = [r for r in rows if r["flags"] and r["kind"] != "info"]
    if not flagged:
        print("No trait is stuck. No forced differences for the next game.")
        return
    print("The next game must differ on:")
    for r in flagged:
        tail = ""
        if r["enum"]:
            others = [v for v in r["enum"] if v != r["last"] and v != r["top"]]
            if others:
                tail = f"  try: {', '.join(rng.sample(others, min(3, len(others))))}"
        how = "reroll the axis" if r["kind"] == "roll" else ("reroll the axis it comes from, then do not bend it back" if r["roll"] else "choose it on purpose")
        print(f"  {r['trait']}: not {r['last']} ({' '.join(r['flags'])}). {how}.{tail}")


def novelty(games, rolls):
    """The roll-layer novelty rules of the skill, run mechanically against the fingerprints."""
    out = []
    recent15, recent5, recent3 = games[-15:], games[-5:], games[-3:]
    # v4 games have an ENGINE spine and a GROWTH number; older games had FORM and CURRENCY. Whichever is given is checked.
    spine = "ENGINE" if "ENGINE" in rolls else "FORM"
    second = "GROWTH" if "GROWTH" in rolls else "CURRENCY"
    form, setting, cur = rolls.get(spine), rolls.get("SET"), rolls.get(second)
    for g in recent15:
        gr = g.get("rolls", {})
        if form is not None and setting is not None and gr.get(spine) == form and gr.get("SET") == setting:
            out.append(f"REROLL SET: {spine} {form} + SET {setting} matches '{g.get('title')}'")
            break
    if form is not None:
        n = sum(1 for g in recent5 if g.get("rolls", {}).get(spine) == form)
        if n >= 3:
            out.append(f"REROLL {spine}: {spine} {form} appears in {n} of the last 5 games")
    if cur is not None:
        n = sum(1 for g in recent3 if g.get("rolls", {}).get(second) == cur)
        if n >= 2:
            out.append(f"REROLL {second}: {second} {cur} appears in {n} of the last 3 games")
    skel = [g.get("traits", {}).get("skeleton") for g in recent3]
    if len(skel) == 3 and skel[0] and skel.count(skel[0]) == 3:
        out.append(f"SKELETON: the last 3 games were all {skel[0]}; build a different shape this time whatever the rolls say")
    return out or ["OK: no roll needs rerolling"]


def verbs(games, ids):
    """Mechanics layer: a game whose action ids mostly appear in one earlier game is a repackage."""
    ids = set(ids)
    worst = None
    for g in games[-10:]:
        prior = set(g.get("actions", []))
        if not prior:
            continue
        share = len(ids & prior) / max(1, len(ids))
        if worst is None or share > worst[0]:
            worst = (share, g.get("title"), sorted(ids & prior))
    if worst is None:
        return ["OK: no earlier game has recorded actions to compare with"]
    share, title, common = worst
    if share > 0.5:
        return [f"REPACKAGE: {share:.0%} of this game's actions ({', '.join(common)}) also appear in '{title}'. Change the FORM interpretation or the LOOP until the verbs differ"]
    return [f"OK: the most overlap is {share:.0%} with '{title}'"]


def write_backlog(rows, games, vocab, path):
    today = games[-1].get("date", "") if games else ""
    lines = [
        "# Variation backlog",
        "",
        f"Generated by tools/sameness.py from {len(games)} games, newest {today}. Regenerated on every run; the fingerprints hold the history.",
        "",
        "A trait lands here when it stays the same for too long. An UNROLLED trait has no dice behind it, so it is a candidate for a new roll axis. A BENT trait has a roll but the generator bends the roll back into the same shape.",
        "",
    ]
    flagged = [r for r in rows if r["flags"] and r["kind"] != "info"]
    if not flagged:
        lines.append("No trait is stuck.")
    else:
        lines += ["| Trait | Flags | Stuck on | Proposed action |", "|-------|-------|----------|-----------------|"]
        for r in flagged:
            spec = vocab["traits"].get(r["trait"], {})
            if spec.get("hint"):
                action = spec["hint"]
            elif "UNROLLED" in r["flags"]:
                vals = [v for v in r["enum"] if v not in spec.get("roll_exclude", [])]
                action = f"Add a roll axis d{len(vals)}: {', '.join(vals)}."
            elif any(f.startswith("BENT") for f in r["flags"]):
                action = f"Reroll {r['roll']} harder or write down how {r['roll']} must map to {r['trait']}; the table changes nothing today."
            elif r["kind"] == "roll":
                action = "Reroll rule already exists; check that it fires."
            else:
                action = f"Reroll {r['roll']} and force a different {r['trait']}."
            lines.append(f"| {r['trait']} | {' '.join(r['flags'])} | {r['top'] if r['share'] >= 0.6 else r['last']} | {action} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {path}")


def validate(g, vocab):
    errs = []
    for key in ("title", "result", "traits", "rolls"):
        if key not in g:
            errs.append(f"missing {key}")
    for name, spec in vocab["traits"].items():
        v = g.get("traits", {}).get(name)
        if v is None:
            errs.append(f"traits.{name} missing")
        elif str(v) not in spec["values"]:
            errs.append(f"traits.{name}={v!r} not in {spec['values']}")
    for axis, k in vocab["roll_sizes"].items():
        v = g.get("rolls", {}).get(axis)
        if v is not None and not (isinstance(v, int) and 1 <= v <= k):
            errs.append(f"rolls.{axis}={v!r} not in 1..{k}")
    if g.get("result") not in ("win", "loss"):
        errs.append("result must be win or loss")
    return errs


STOP = set("a an the of to and in on at is it you your he she they we i for with as but or if that this was were be by from not no so up out his her their its".split())


# words from the skill's fixed scaffolding (menus, roll header, save prompt); a phrase with one is not a voice rut
SCAFFOLD = set("player anything library twist clock loop role tone form playthrough rolls status turns".split())


def phrases(files, vocab, need=None):
    expanded = []
    for pat in files:
        expanded += sorted(glob.glob(os.path.join(GM_ROOT, pat))) if not os.path.isabs(pat) else sorted(glob.glob(pat))
    files = expanded
    need = need or vocab["thresholds"]["phrase_min_games"]
    df = Counter()
    total = Counter()
    for fp in files:
        with open(fp, encoding="utf-8", errors="replace") as f:
            words = re.findall(r"[a-z']+", f.read().lower())
        grams = set()
        for i in range(len(words) - 3):
            g = tuple(words[i:i + 4])
            if sum(1 for w in g if w in STOP) >= 3 or any(w in SCAFFOLD for w in g):
                continue
            grams.add(g)
            total[g] += 1
        for g in grams:
            df[g] += 1
    hot = [(d, total[g], " ".join(g)) for g, d in df.items() if d >= need]
    hot.sort(reverse=True)
    print(f"4-word phrases in {need} or more of {len(files)} files (files, total uses, phrase):")
    for d, t, p in hot[:30]:
        print(f"  {d:>2} {t:>3}  {p}")
    if not hot:
        print("  none")


def parse_args(argv):
    path, window, rest = DEFAULT_FILE, None, []
    i = 0
    while i < len(argv):
        if argv[i] == "--file" and i + 1 < len(argv):
            path = argv[i + 1]
            i += 2
        elif argv[i] == "--window" and i + 1 < len(argv):
            window = int(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    return path, window, rest


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return
    cmd = argv[0]
    path, window, rest = parse_args(argv[1:])
    vocab = load_vocab()

    if cmd == "phrases":
        need = None
        if "--min" in rest:
            i = rest.index("--min")
            need = int(rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        phrases(rest, vocab, need)
        return

    if cmd == "add":
        if not rest:
            raise SystemExit("usage: add '<json>'")
        g = json.loads(rest[0])
        errs = validate(g, vocab)
        if errs:
            raise SystemExit("fingerprint rejected:\n  " + "\n  ".join(errs))
        games = load_games(path)
        g.setdefault("order", (games[-1]["order"] + 1) if games else 1)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
        games.append(g)
        rows = analyze(games, vocab, window)
        print_report(rows, games, vocab, only_flagged=True)
        print_similar(games, vocab)
        return

    games = load_games(path)
    if cmd == "novelty":
        rolls = {}
        for a in rest:
            if "=" in a:
                k, v = a.split("=", 1)
                rolls[k.upper()] = int(v)
        print(chr(10).join(novelty(games, rolls)))
        return
    if cmd == "verbs":
        print(chr(10).join(verbs(games, [x for a in rest for x in a.split(",") if x])))
        return
    if not games:
        raise SystemExit(f"no fingerprints in {path}")
    rows = analyze(games, vocab, window)

    if cmd == "report":
        print_report(rows, games, vocab)
        print_pairs(games, vocab)
        print_similar(games, vocab)
    elif cmd == "last":
        print_report(rows, games, vocab, only_flagged=True)
        print_similar(games, vocab)
    elif cmd == "brief":
        brief(rows, vocab)
    elif cmd == "backlog":
        write_backlog(rows, games, vocab, BACKLOG_FILE)
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
