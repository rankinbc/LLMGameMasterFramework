"""
gm_analysis: tension profile, autopsy, ablation and replay for /play engines.

Everything here is advisory: it produces warnings and numbers, never a pass or fail. It plays rollouts of
the engine's own heuristic, so it is only as good as that heuristic; `check` warns when the heuristic is weak.
"""

import copy
import json
import os
import random

import gm_base as B


def paired(wa, wb):
    """Mean difference of two paired outcome lists, and its standard error."""
    k = len(wa)
    diffs = [a - b for a, b in zip(wa, wb, strict=True)]
    d = sum(diffs) / k
    if k < 2:
        return d, 0.0
    var = sum((x - d) ** 2 for x in diffs) / (k - 1)
    return d, (var / k) ** 0.5


def option_label(o):
    args = o.get("args") or {}
    shown = {k: v for k, v in args.items() if o.get("params") and k in o["params"]}
    return o["label"] + (f" {shown}" if shown else "")


def turn_view(g, s, prng, k, extra=None):
    """How much the choice matters at state s. `spread` counts only when the best option is clearly better than
    the worst (2.5 standard errors), so noise does not pass for a decision. `extra` are concrete options judged
    in the same paired rollouts (the move a player actually made)."""
    opts = g.options(s)
    cands, src = [], []
    for i, o in enumerate(opts):
        for c in B._expand(o):
            cands.append(c)
            src.append(i)
    extra_idx = []
    for e in extra or []:
        for j, c in enumerate(cands):
            if B._same_option(c, e):
                extra_idx.append(j)
                break
        else:
            cands.append(e)
            src.append(next((i for i, o in enumerate(opts) if o["id"] == e["id"]), 0))
            extra_idx.append(len(cands) - 1)
    wins = B._evaluate_wins(g, s, cands, prng, k)
    rates = [sum(w) / k for w in wins]
    bi = max(range(len(cands)), key=lambda i: rates[i])
    wi = min(range(len(cands)), key=lambda i: rates[i])
    d, se = paired(wins[bi], wins[wi])
    spread = d if (d > 0 and d >= 2.5 * se) else 0.0
    by_opt = {}
    for r, i in zip(rates, src, strict=True):
        by_opt[i] = max(by_opt.get(i, 0.0), r)
    ranked = sorted(by_opt.values(), reverse=True)
    second_gap = ranked[0] - ranked[1] if len(ranked) > 1 else 1.0
    hp_rate = None
    try:
        hp = B._norm(g.heuristic(s, opts, B.RNG(prng.randrange(1, 10**9))), opts)
        for j, c in enumerate(cands):
            if B._same_option(c, hp):
                hp_rate = rates[j]
                break
    except Exception:  # noqa: BLE001
        pass
    forced = B._is_forced(opts)
    dilemma = (not forced) and spread >= B.HARD_SPREAD and (
        second_gap <= B.DILEMMA_GAP or (hp_rate is not None and rates[bi] - hp_rate >= 0.10)
    )
    return {
        "opts": opts, "cands": cands, "wins": wins, "rates": rates, "best": rates[bi], "worst": rates[wi],
        "best_i": bi, "worst_i": wi, "spread": spread, "forced": forced, "dilemma": dilemma,
        "extra_idx": extra_idx, "mean": sum(rates) / len(rates),
    }


def swing_cause(forced, before, after, picked_rate, best_rate):
    """Why the player's chances moved across one turn: their choice, or events and dice. A rise cannot be a bad
    choice, and a drop is the player's only when the move cost at least half of it against the best move."""
    if forced:
        return "no choice: the move was forced, so the swing came from events"
    if after >= before:
        return "events and dice (your chances rose)"
    cost = best_rate - picked_rate
    if cost >= 0.5 * (before - after):
        return "your choice"
    return "events and dice after your move (your move was among the best)"


def decided_turn(rows):
    """First turn of the trailing block in which the result is already fixed, or None."""
    decided = None
    for r in reversed(rows):
        if r["best"] < B.DECIDED_EDGE or r["worst"] > 1 - B.DECIDED_EDGE:
            decided = r["turn"]
        else:
            break
    return decided


# ---------------------------------------------------------------- profile


def profile_games(g, seeds, k):
    """Play heuristic games and record, turn by turn, how much the choice mattered. Worker-friendly."""
    prng = random.Random(777)
    games = []
    for seed in seeds:
        prng.seed(777 + seed)
        g._hits = type(g._hits)()
        s, rng = B._new(g, seed)
        rows = []
        while not s.get("_ended"):
            s = json.loads(json.dumps(s))
            v = turn_view(g, s, prng, k)
            rows.append({
                "turn": s["_turn"], "best": v["best"], "worst": v["worst"], "spread": v["spread"],
                "forced": v["forced"], "dilemma": v["dilemma"],
            })
            pick = B._norm(g.heuristic(s, v["opts"], rng), v["opts"])
            s, _, _ = B._step(g, s, pick["id"], pick.get("args", {}))
        games.append(rows)
    return games


def profile(g, n, k):
    """Tension profile over n heuristic games."""
    if n >= 8 and B._parallel_ok(g):
        try:
            w = B._workers()
            payloads = [("profile", B._engine_file(g), type(g).__name__, g.C, list(range(1 + i, n + 1, w)), k) for i in range(w)]
            games = [row for part in B._pmap([p for p in payloads if p[4]]) for row in part]
        except Exception:  # noqa: BLE001
            games = profile_games(g, range(1, n + 1), k)
    else:
        games = profile_games(g, range(1, n + 1), k)
    per_turn = {}
    for rows in games:
        for r in rows:
            per_turn.setdefault(r["turn"], []).append(r)
    turns_out = []
    for t in sorted(per_turn):
        rs = per_turn[t]
        turns_out.append({
            "turn": t, "games": len(rs),
            "mean_spread": round(sum(r["spread"] for r in rs) / len(rs), 2),
            "consequential": round(sum(1 for r in rs if r["spread"] >= B.HARD_SPREAD) / len(rs), 2),
            "dilemma": round(sum(1 for r in rs if r["dilemma"]) / len(rs), 2),
        })
    allr = [r for rows in games for r in rows]
    nf = [r for r in allr if not r["forced"]]
    consequential = sum(1 for r in allr if r["spread"] >= B.HARD_SPREAD) / max(1, len(allr))
    dilemma = sum(1 for r in nf if r["dilemma"]) / max(1, len(nf))
    forced = 1 - len(nf) / max(1, len(allr))
    early_decided, gaps = 0, []
    for rows in games:
        d = decided_turn(rows)
        if d is not None:
            gap = rows[-1]["turn"] - d
            gaps.append(gap)
            early_decided += gap >= 3
    warnings = []
    solid = [t for t in turns_out if t["games"] >= len(games) * 0.5]
    run_start = None
    for i, t in enumerate(solid + [None]):
        flat = t is not None and t["mean_spread"] < B.FLAT_SPREAD
        if flat and run_start is None:
            run_start = t["turn"]
        if not flat and run_start is not None:
            end = solid[i - 1]["turn"]
            if end - run_start + 1 >= 3:
                where = "OPENING" if run_start <= 2 else "FINISH" if end >= solid[-1]["turn"] - 1 else "MIDDLE"
                warnings.append(f"FLAT {where}: turns {run_start} to {end} rarely change the outcome (mean spread under {B.FLAT_SPREAD:.0%})")
            run_start = None
    if early_decided / max(1, len(games)) >= 0.5:
        warnings.append(f"FLAT FINISH: {early_decided} of {len(games)} games were decided 3 or more turns before the end")
    if consequential < 0.25:
        warnings.append(f"LOW STAKES: only {consequential:.0%} of turns changed the outcome by 20 points or more (target 25 percent)")
    if dilemma < 0.15:
        warnings.append(f"FEW DILEMMAS: only {dilemma:.0%} of choices had two good options or a wrong obvious one (target 15 percent)")
    return {
        "games": len(games), "rollouts_per_option": k,
        "consequential_share": round(consequential, 2),
        "dilemma_share": round(dilemma, 2),
        "forced_share": round(forced, 2),
        "decided_early_share": round(early_decided / max(1, len(games)), 2),
        "mean_turns_decided_before_end": round(sum(gaps) / len(gaps), 1) if gaps else None,
        "turns": turns_out,
        "warnings": warnings,
        "note": (
            "Consequential: the best option clearly beats the worst by 20 points. Dilemma: consequential and a second "
            "option is within 15 points, or the sensible default is 10 points worse than the best. Advice, not gates."
        ),
    }


# ---------------------------------------------------------------- autopsy


def autopsy(g, k):
    """Post-game: replay the saved decisions and measure where the game was won or lost."""
    if not os.path.exists(B.HISTORY_FILE):
        raise SystemExit("no history.jsonl: play at least one turn with `step`")
    with open(B.HISTORY_FILE, encoding="utf-8") as f:
        entries = [json.loads(ln) for ln in f if ln.strip()]
    final = B._load()
    result = (final.get("_ended") or {}).get("result")
    end_value = 1.0 if result == "win" else 0.0 if result == "loss" else None
    prng = random.Random(99)
    rows = []
    for e in entries:
        state = e["state"]
        opts = g.options(state)
        picked_opt = B._concrete_first(B._find(opts, e["id"], e.get("args", {})), e.get("args", {}))
        v = turn_view(g, state, prng, k, extra=[picked_opt])
        ci = v["extra_idx"][0]
        d, se = paired(v["wins"][v["best_i"]], v["wins"][ci])
        regret = d if (d >= 0.10 and d >= 2 * se) else 0.0
        unreliable = False
        if regret and result == "win" and v["rates"][ci] < 0.10:
            regret, unreliable = 0.0, True  # the player won through a move the rollouts rate hopeless: the rollouts are wrong
        if v["forced"]:
            regret = 0.0
        rows.append({
            "turn": e["turn"], "best": v["best"], "worst": v["worst"], "spread": round(v["spread"], 2),
            "forced": v["forced"], "dilemma": v["dilemma"], "picked": option_label(picked_opt),
            "picked_rate": round(v["rates"][ci], 2), "mean_rate": round(v["mean"], 2),
            "best_option": option_label(v["cands"][v["best_i"]]), "regret": round(regret, 2),
            "unreliable": unreliable, "events": e.get("events", []),
        })
    potential = [r["best"] for r in rows] + ([end_value] if end_value is not None else [])
    swings = [(abs(potential[i + 1] - potential[i]), i) for i in range(len(potential) - 1)]
    big = max(swings) if swings else (0.0, 0)
    decided = decided_turn(rows)
    last_turn = rows[-1]["turn"] if rows else 0
    consequential = [r["turn"] for r in rows if r["spread"] >= B.HARD_SPREAD]
    dilemmas = [r["turn"] for r in rows if r["dilemma"]]
    nonforced = [r for r in rows if not r["forced"]]
    regrets = sorted([r for r in rows if r["regret"] > 0], key=lambda r: -r["regret"])[:3]
    third = max(1, len(rows) // 3)
    flags = []
    if decided is not None and last_turn - decided >= 3:
        flags.append(f"FLAT FINISH: decided at turn {decided}, {last_turn - decided} turns before the end")
    if rows and not any(r["spread"] >= B.HARD_SPREAD for r in rows[-third:]):
        flags.append("NO HARD CHOICE in the last third")
    if rows and not any(r["spread"] >= B.HARD_SPREAD for r in rows[:third]):
        flags.append("NO HARD CHOICE in the first third")
    swing = None
    if rows and swings:
        r = rows[big[1]]
        after = potential[big[1] + 1]
        choice_effect = r["picked_rate"] - r["mean_rate"]
        luck_effect = after - r["picked_rate"]
        cause = swing_cause(r["forced"], potential[big[1]], after, r["picked_rate"], r["best"])
        swing = {
            "turn": r["turn"], "potential_before": round(potential[big[1]], 2), "potential_after": round(after, 2),
            "cause": cause, "choice_effect": round(choice_effect, 2), "luck_effect": round(luck_effect, 2),
            "picked": r["picked"], "best_option": r["best_option"], "events": r["events"],
        }
    notes = [
        "Win rates are from rollouts in which the engine's heuristic plays every move after the one being judged, "
        "so a regret reads 'if you had played on sensibly afterward'."
    ]
    if any(r["unreliable"] for r in rows):
        notes.append("A regret was dropped: the player won through a move the rollouts rate hopeless, which means the heuristic misplays that position.")
    if final.get("hidden") and type(g).resample_hidden is B.Game.resample_hidden:
        notes.append("HINDSIGHT: this game has hidden facts and no resample_hidden, so the rollouts know the answer. Treat the regrets as unreliable.")
    return {
        "result": result,
        "reason": (final.get("_ended") or {}).get("reason"),
        "turns_played": last_turn,
        "consequential_turns": consequential,
        "dilemma_turns": dilemmas,
        "forced_turns": [r["turn"] for r in rows if r["forced"]],
        "dilemma_share": round(len(dilemmas) / max(1, len(nonforced)), 2),
        "decided_at_turn": decided,
        "biggest_swing": swing,
        "top_regrets": [{"turn": r["turn"], "picked": r["picked"], "better": r["best_option"], "cost": r["regret"]} for r in regrets],
        "flags": flags,
        "notes": notes,
        "table": [{k2: r[k2] for k2 in ("turn", "best", "worst", "spread", "picked_rate", "regret", "forced", "dilemma")} for r in rows],
    }


# ---------------------------------------------------------------- ablate


def ablate(g, n, k=4):
    """Ban each action in turn and replay with look-ahead. An action nobody misses is dead or dominated."""
    names = list(g.ACTIONS)
    base_win, win_without = None, {}
    if B._parallel_ok(g):
        try:
            jobs = [
                ("games", B._engine_file(g), type(g).__name__, g.C, [a] if a else [], "lookahead", k, list(range(1, n + 1)))
                for a in [None] + names
            ]
            rates = [sum(1 for r in results if r.get("result") == "win") / n for results, _st, _tags in B._pmap(jobs)]
            base_win, win_without = rates[0], dict(zip(names, rates[1:], strict=True))
        except Exception:  # noqa: BLE001
            base_win, win_without = None, {}
    if base_win is None:
        base_sum, _ = B._selftest(g, n, "lookahead", k, banned=[])
        base_win = base_sum["win_rate"]
        for a in names:
            saved = g.options
            try:
                B._ban(g, [a])
                r, _ = B._selftest(g, n, "lookahead", k, banned=[a])
            finally:
                g.options = saved
                B._LENIENT = False
            win_without[a] = r["win_rate"]
    se = (2 * 0.25 / n) ** 0.5
    out, warnings = [], []
    for a in names:
        delta = round(base_win - win_without[a], 2)
        verdict = "needed" if delta >= 2 * se else "marginal" if delta >= se else "unproven" if delta > -2 * se else "harmful"
        out.append({"action": a, "win_without": round(win_without[a], 2), "delta": delta, "verdict": verdict})
        if verdict == "unproven":
            warnings.append(f"ACTION: banning {a} changes the win rate by {delta:+.2f}; it may be dead or dominated (unless it is a decoy on purpose)")
        if verdict == "harmful":
            warnings.append(f"ACTION: banning {a} RAISES the win rate by {-delta:.2f}; it works as a trap")
    return {"games": n, "policy": f"look-ahead ({k} rollouts per option); the baseline is look-ahead with every action, not the heuristic",
            "baseline_win": round(base_win, 2), "noise_se": round(se, 2), "actions": out, "warnings": warnings,
            "note": "Differences under about 2 x noise_se are not distinguishable from luck. Treat verdicts as leads, not proof."}


# ---------------------------------------------------------------- replay


def replay(g, apply=False):
    """Re-run history.jsonl on the saved seed with the current engine (after an engine fix)."""
    if not os.path.exists(B.HISTORY_FILE):
        raise SystemExit("no history.jsonl to replay")
    with open(B.HISTORY_FILE, encoding="utf-8") as f:
        entries = [json.loads(ln) for ln in f if ln.strip()]
    if not entries:
        raise SystemExit("history.jsonl is empty")
    seed = entries[0]["state"]["_seed"]
    s, _rng = B._new(g, seed)
    new_hist = []
    for n, e in enumerate(entries, 1):
        before = copy.deepcopy(s)
        try:
            chosen = B._match(g.options(s), e["id"], e.get("args", {}))
            s, events, _ = B._step(g, s, e["id"], e.get("args", {}))
        except B.IllegalAction as ex:
            return {"ok": False, "replayed": n - 1, "stopped_at_turn": e["turn"], "why": ex.msg,
                    "note": "the fixed engine no longer offers this move; choose again from the last good state"}
        new_hist.append({"turn": before["_turn"], "state": before, "id": chosen["id"], "args": {**chosen.get("args", {}), **e.get("args", {})},
                         "label": chosen["label"], "events": events, "ended": s["_ended"]})
    try:
        saved = B._load()
    except SystemExit:
        saved = None  # a damaged state file is exactly why one replays
    same = saved is not None and json.dumps(s, sort_keys=True) == json.dumps(saved, sort_keys=True)
    out = {"ok": True, "replayed": len(entries), "matches_saved_state": same, "status": g.status_line(s), "ended": s["_ended"]}
    if apply:
        B._save(s)
        with open(B.HISTORY_FILE, "w", encoding="utf-8") as f:
            for h in new_hist:
                f.write(json.dumps(h) + "\n")
        out["applied"] = True
    else:
        out["note"] = "dry run; add --apply to write the replayed state and history"
    return out
