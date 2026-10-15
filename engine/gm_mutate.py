"""
gm_mutate: how strong are a game's rule tests, and what numbers hide in the code?

Mutation pass. Changes one thing at a time in the engine's own code (a number, a comparison, a plus or minus,
a true or false) inside every method of the game class except the analysis-only ones, and inside module-level
helper functions, then asks whether the rule tests or the universal checks notice. A change nothing notices is a
behavior no test pins down, so a future bug of that kind would slip through. Survivors are listed with their
line numbers so the author can add the missing test. A line that cannot matter (an equivalent mutant) can carry
the comment `# no-mutate`.

Literal report. Lists numbers written into the code (outside CONSTANTS), because the sheet cannot show them and
tuning cannot reach them. A line where the number is structural can carry `# lit-ok`.
"""

import ast
import copy
import random

# methods that only feed the analysis tools, display text or the test harness: mutating them proves nothing
EXCLUDE = {"rule_tests", "heuristic", "status_line", "visible", "rules", "resample_hidden", "__init__", "hit", "finish"}
SWAP_CMP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
SWAP_BIN = {ast.Add: ast.Sub, ast.Sub: ast.Add}
LIMIT = 160
LITERAL_OK = {0, 1, -1, 2}


def _functions(tree, class_name):
    """The game class's methods that matter, and the module-level helper functions."""
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            out += [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name not in EXCLUDE]
        elif isinstance(node, ast.FunctionDef):
            out.append(node)
    return out


def _skip_ids(fn):
    """Nodes a change could not sensibly test: loops a change could make endless. Numbers inside f-string
    expressions are kept: `{i + 1}` in a label is behavior the player reads, and a test should pin it."""
    skip = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.While):
            skip.update(id(m) for m in ast.walk(n))
    return skip


def candidates(tree, class_name, src=""):
    """Mutable nodes in a stable order."""
    lines = src.splitlines()
    out = []
    for fn in _functions(tree, class_name):
        skip = _skip_ids(fn)
        for n in ast.walk(fn):
            if id(n) in skip:
                continue
            if lines and getattr(n, "lineno", None) and "no-mutate" in lines[n.lineno - 1]:
                continue
            if isinstance(n, ast.Constant) and isinstance(n.value, bool):
                out.append(("bool", n))
            elif isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                out.append(("num", n))
            elif isinstance(n, ast.Compare) and len(n.ops) == 1 and type(n.ops[0]) in SWAP_CMP:
                out.append(("cmp", n))
            elif isinstance(n, ast.BinOp) and type(n.op) in SWAP_BIN:
                out.append(("bin", n))
            elif isinstance(n, ast.AugAssign) and type(n.op) in SWAP_BIN:
                out.append(("aug", n))
    return out


def mutate(kind, node):
    if kind == "bool":
        node.value = not node.value
    elif kind == "num":
        v = node.value
        node.value = v + 1 if isinstance(v, int) else round(v * 1.5 + 0.05, 4)
    elif kind == "cmp":
        node.ops[0] = SWAP_CMP[type(node.ops[0])]()
    elif kind in ("bin", "aug"):
        node.op = SWAP_BIN[type(node.op)]()


def describe(kind, node, src):
    seg = ast.get_source_segment(src, node) or kind
    return f"line {node.lineno} {kind} `{seg[:48]}`"


def _build(path, tree, cls_name, C):
    ast.fix_missing_locations(tree)
    ns = {"__name__": "gm_mutant", "__file__": path}
    exec(compile(tree, path, "exec"), ns)
    g = ns[cls_name]()
    g.C = copy.deepcopy(C)
    return g


def _flags_of(g, B, K):
    out = list(K.run_rule_tests(g, B))
    obs = K.observe(g, B, games=6)
    for kind, msgs in obs["problems"].items():
        out += [f"{kind}:{m}" for m in msgs]
    return out


def run_chunk(path, cls_name, C, ids):
    """Judge the mutants numbered `ids`. Returns [(id, killed, description)]."""
    import gm_base as B
    import gm_checks as K

    with open(path, encoding="utf-8") as f:
        src = f.read()
    base_cands = candidates(ast.parse(src), cls_name, src)
    baseline = set(_flags_of(_build(path, ast.parse(src), cls_name, C), B, K))
    out = []
    for i in ids:
        tree = ast.parse(src)
        kind, node = candidates(tree, cls_name, src)[i]
        desc = describe(base_cands[i][0], base_cands[i][1], src)
        mutate(kind, node)
        try:
            killed = bool(set(_flags_of(_build(path, tree, cls_name, C), B, K)) - baseline)
        except Exception:  # noqa: BLE001  a mutant that cannot even run is caught
            killed = True
        out.append((i, killed, desc))
    return out


def run_mutation(g, B, engine_path, limit=LIMIT):
    """Mutation score of the rule tests and checks for this game."""
    cls_name = type(g).__name__
    with open(engine_path, encoding="utf-8") as f:
        src = f.read()
    n = len(candidates(ast.parse(src), cls_name, src))
    ids = list(range(n))
    if n > limit:
        ids = sorted(random.Random(1).sample(ids, limit))
    results = []
    if B._parallel_ok(g) and len(ids) >= 16:
        try:
            w = B._workers()
            payloads = [("mutate", engine_path, cls_name, g.C, ids[i::w]) for i in range(w) if ids[i::w]]
            for part in B._pmap(payloads):
                results += part
        except Exception:  # noqa: BLE001
            results = []
    if not results:
        results = run_chunk(engine_path, cls_name, g.C, ids)
    results.sort()
    killed = sum(1 for _, k, _ in results if k)
    survivors = [d for _, k, d in results if not k]
    return {"tested": len(results), "killed": killed, "rate": killed / max(1, len(results)), "survivors": survivors}


def literal_report(engine_path, class_name):
    """Numbers written into the game's logic that are not in CONSTANTS. Returns short descriptions."""
    with open(engine_path, encoding="utf-8") as f:
        src = f.read()
    lines = src.splitlines()
    tree = ast.parse(src)
    out, seen = [], set()
    for fn in _functions(tree, class_name):
        skip = _skip_ids(fn)
        index_ids = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Subscript):
                index_ids.update(id(m) for m in ast.walk(n.slice))
        for n in ast.walk(fn):
            if id(n) in skip or id(n) in index_ids:
                continue
            if not (isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)):
                continue
            if n.value in LITERAL_OK or "lit-ok" in lines[n.lineno - 1]:
                continue
            key = (n.lineno, n.value)
            if key not in seen:
                seen.add(key)
                out.append(f"line {n.lineno} has {n.value} in {fn.name}")
    return out
