"""Regression suite for the generation harness.

Each mutant is the reference engine with ONE injected bug of a kind that appeared in real generated games.
`engine.py check --quick` must flag every mutant, and must leave the untouched engine clean. If a change to
gm_base.py or gm_checks.py stops catching a bug class, a test here goes red.

Run:  python -m unittest discover -s tests -v        (from the GM folder; takes a few minutes)
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
GM = os.path.dirname(HERE)
ENGINE_DIR = os.path.join(GM, "engine")
EXAMPLE = os.path.join(ENGINE_DIR, "example_lantern_chain", "engine.py")

SYS_PATH_LINE = 'os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")'

# name: (replacements [(old, new)], expected substrings, one of which must appear in some flag)
MUTANTS = {
    "options_capped": (
        [("\n        return o\n\n    def apply", "\n        return o[:3]\n\n    def apply")],
        ["ACTION:", "GATE-HIDDEN:"],
    ),
    "hidden_reserve_filter": (
        [('if not on and s["oil"] >= C["LIGHT_COST"]:', 'if not on and s["oil"] >= C["LIGHT_COST"] + 4:')],
        ["GATE-HIDDEN:"],
    ),
    "offered_when_unaffordable": (
        [('if s["_turn"] >= C["SIGNAL_NIGHT"] and s["oil"] >= C["SIGNAL_COST"]:', 'if s["_turn"] >= C["SIGNAL_NIGHT"]:')],
        ["GATE-OFFERED:", "BOUNDS:"],
    ),
    "stale_none_in_event": (
        [("ev.append(f\"Lantern {args['lantern'] + 1} lit.\")", "ev.append(f\"Lantern {None} lit.\")")],
        ["TEXT:"],
    ),
    "unformatted_brace": (
        [("The column will rush tonight.", "The {{column}} will rush tonight.")],
        ["TEXT:"],
    ),
    "set_in_state": (
        [('"hidden": {"stride": rng.d(C["_STRIDES"]), "pos": pos},', '"hidden": {"stride": rng.d(C["_STRIDES"]), "pos": pos}, "seen": {1, 2},')],
        ["CRASH", "JSON:"],
    ),
    "int_keys_in_state": (
        [
            ('"hidden": {"stride": rng.d(C["_STRIDES"]), "pos": pos},', '"hidden": {"stride": rng.d(C["_STRIDES"]), "pos": pos}, "table": {1: 5},'),
            ("        C = self.C\n        ev = []\n        # wind hits tonight's targets", "        C = self.C\n        ev = []\n        _ = s[\"table\"][1]\n        # wind hits tonight's targets"),
        ],
        ["CRASH"],
    ),
    "clamped_value_never_reaches": (
        [('s["column"] += gain', 's["column"] = min(s["column"] + gain, 25)')],
        ["REACH:"],
    ),
    "code_ignores_constant": (
        [('                s["oil"] += C["HAUL_GAIN"]\n                s["fails"] = 0', '                s["oil"] += 8\n                s["fails"] = 0')],
        ["RULETEST: rule 3"],
    ),
    "uses_global_random": (
        [('if rng.chance(C["STALL_P"]):', 'if __import__("random").random() < C["STALL_P"]:')],
        ["DETERMINISM:"],
    ),
    "string_set_order": (
        [('h["pos"] = (h["pos"] + h["stride"]) % L',
          'h["pos"] = (h["pos"] + h["stride"] + sum(i for i, x in enumerate({"a1", "b2", "c3", "x4", "y5", "z6", "m7", "q8"}) if x < "n")) % L')],
        ["DETERMINISM:"],
    ),
    "visible_returns_hidden": (
        [("    def status_line(self, s):", "    def visible(self, s):\n        return dict(s)\n\n    def status_line(self, s):")],
        ["LEAK:"],
    ),
    "status_line_changes_shape": (
        [("| Wind {wind}\"", "| Wind {wind}\" + (\" | Night 5 | Extra 1\" if s[\"_turn\"] > 4 else \"\")")],
        ["STATUS:"],
    ),
    "tag_never_fires": (
        [('            self.hit("sled")\n', "")],
        ["TAG:"],
    ),
    "rule_without_test": (
        [('(8, "sled and goal", r8),', "")],
        ["RULETEST: rule 8"],
    ),
    "sheet_placeholder_typo": (
        [("3. Hauling: roll {HAUL_NEED}+", "3. Hauling: roll {HAUL_NEEDS}+")],
        ["SHEET:"],
    ),
    "constant_missing_from_sheet": (
        [('"STALL_P": 0.2,', '"STALL_P": 0.2,\n        "BONUS": 3,')],
        ["SHEET: constant BONUS"],
    ),
    "value_out_of_bounds": (
        [('"START_OIL": 12,', '"START_OIL": 200,')],
        ["BOUNDS:"],
    ),
    "declared_action_never_offered": (
        [('ACTIONS = ["light", "shield", "haul", "windbreak", "signal", "sled"]', 'ACTIONS = ["light", "shield", "haul", "windbreak", "signal", "sled", "ghost"]')],
        ["ACTION: ghost"],
    ),
    "rival_gambit_touches_nothing": (
        [('                s["wind"] = []  # the rival\'s move is undone: this is what makes it a rival gambit\n', "")],
        ["GAMBIT:"],
    ),
    "gambit_not_an_action": (
        [('GAMBITS = {"windbreak": {"rival": True}}', 'GAMBITS = {"windbreak": {"rival": True}, "parley": {}}')],
        ["GAMBIT:"],
    ),
    "rival_keys_name_a_missing_key": (
        [('RIVAL_KEYS = ["wind"]', 'RIVAL_KEYS = ["gale"]')],
        ["GAMBIT:"],
    ),
    "undeclared_action_offered": (
        [("\n        return o\n\n    def apply", "\n        o.append({\"id\": \"secret\", \"label\": \"A secret move\", \"args\": {}})\n        return o\n\n    def apply")],
        ["ACTION: secret"],
    ),
    "duplicate_option": (
        [("\n        return o\n\n    def apply", "\n        o.append(dict(o[0]))\n        return o\n\n    def apply")],
        ["CRASH"],
    ),
    "ends_when_turn_reaches_budget": (
        [('        if s["oil"] < 0:\n            return {"result": "loss", "reason": "oil ran out, every lantern went dark"}',
          '        if s["_turn"] >= self.turns and s["column"] < self.C["GOAL"]:\n            return {"result": "loss", "reason": "late"}\n'
          '        if s["oil"] < 0:\n            return {"result": "loss", "reason": "oil ran out, every lantern went dark"}')],
        ["CHECK_END:", "SHORT GAMES"],
    ),
    "label_counts_from_zero": (
        [("Light lantern {i + 1} (-", "Light lantern {i} (-")],
        ["RULETEST: rule 1"],
    ),
    "status_shows_wrong_number": (
        [("Column {s['column']}/", "Column {s['column'] + 1}/")],
        ["RULETEST: rule 1"],
    ),
    "event_names_wrong_lantern": (
        [('f"The wind snuffed lantern {i + 1}."', 'f"The wind snuffed lantern {i}."')],
        ["RULETEST: rule 5"],
    ),
    "narrates_tomorrow_after_the_end": (
        [('            self.finish(s, "loss", "oil ran out, every lantern went dark")\n            return ev  # nothing after a fatal event: no tells for a tomorrow that will not come\n',
          '            self.finish(s, "loss", "oil ran out, every lantern went dark")\n')],
        ["RULETEST: rule 4", "TEXT:"],
    ),
    "stale_word_in_end_reason": (
        [('"oil ran out, every lantern went dark"', '"oil ran out and the Wall fell, every lantern went dark"')],
        ["W:VOCAB"],
    ),
    "dusk_prepares_the_wrong_night": (
        [('tomorrow = s["_turn"] + 1', 'tomorrow = s["_turn"]')],
        ["RULETEST: rule 6"],
    ),
    "die_size_written_into_the_code": (
        [('rng.check(C["HAUL_NEED"], C["DIE"], "haul")', 'rng.check(C["HAUL_NEED"], 6, "haul")')],
        ["W:LITERAL"],
    ),
    "budget_never_scored": (
        [('    def final_check(self, s):\n        return {"result": "loss"', '    def final_check(self, s):\n        return {"result": "win"')],
        ["RULETEST: rule 8", "TOO EASY"],
    ),
    "wrong_plural_in_event": (
        [("{plural(burn, 'lit lantern')}", "{burn} lit lanterns")],
        ["TEXT:"],
    ),
    "tracked_too_many": (
        [('TRACKED = ["oil", "column", "lit"]', 'TRACKED = ["oil", "column", "lit", "fails"]')],
        ["TRACKED:"],
    ),
    "rule_line_too_long": (
        [("3. Hauling: roll {HAUL_NEED}+ on a d{DIE} to bring back {HAUL_GAIN} oil, otherwise {HAUL_FAIL}.",
          "3. Hauling: roll {HAUL_NEED}+ on a d{DIE} to bring back {HAUL_GAIN} oil, otherwise {HAUL_FAIL}, " + "and then keep going with the rest of the night " * 8)],
        ["SHEET: rule 3"],
    ),
    "prices_a_feeling_like_goods": (
        [("Haul oil from the depot (roll", "Sell the crew's morale for oil (roll")],
        ["SENSE:"],
    ),
    "param_with_no_choices": (
        [('"params": {"oil": {"choices": spend}}', '"params": {"oil": {"choices": []}}')],
        ["CRASH"],
    ),
    "heuristic_picks_illegal": (
        [('        return "haul"\n\n\nif __name__', '        return "no_such_action"\n\n\nif __name__')],
        ["CRASH"],
    ),
}


def run_check(path, cwd):
    r = subprocess.run([sys.executable, path, "check", "--quick"], capture_output=True, text=True, cwd=cwd, timeout=900)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"flags": [f"UNPARSEABLE OUTPUT: {r.stdout[-200:]} {r.stderr[-300:]}"], "verdict": "ERROR"}


def build_mutant(name, replacements, outdir):
    with open(EXAMPLE, encoding="utf-8") as f:
        src = f.read()
    for old, new in replacements:
        if old not in src:
            raise AssertionError(f"mutant {name}: text to replace not found: {old[:60]!r}")
        src = src.replace(old, new, 1)
    assert SYS_PATH_LINE in src
    src = src.replace(SYS_PATH_LINE, repr(ENGINE_DIR))
    path = os.path.join(outdir, f"mutant_{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    return path


class MutantSuite(unittest.TestCase):
    results = {}
    control = None

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="gm_mutants_")
        jobs = {}
        for name, (reps, _exp) in MUTANTS.items():
            workdir = os.path.join(cls.tmp, name)
            os.makedirs(workdir)
            jobs[name] = (build_mutant(name, reps, workdir), workdir)
        control_dir = os.path.join(cls.tmp, "control")
        os.makedirs(control_dir)
        jobs["__control__"] = (build_mutant("control", [], control_dir), control_dir)
        with ThreadPoolExecutor(max_workers=6) as pool:
            futs = {name: pool.submit(run_check, p, wd) for name, (p, wd) in jobs.items()}
            for name, fut in futs.items():
                cls.results[name] = fut.result()

    def test_control_is_clean(self):
        res = self.results["__control__"]
        self.assertEqual(res.get("flags"), [], f"the untouched reference engine must be clean: {res.get('flags')}")

    def test_every_mutant_is_caught(self):
        missed = []
        for name, (_reps, expected) in MUTANTS.items():
            res = self.results[name]
            flags = res.get("flags", [])
            warns = res.get("warnings", [])
            hit = any(exp in f for exp in expected if not exp.startswith("W:") for f in flags)
            hit = hit or any(exp[2:] in w for exp in expected if exp.startswith("W:") for w in warns)
            if not hit:
                missed.append(f"{name}: expected one of {expected}, got flags {flags[:3]} warnings {[w[:60] for w in warns[:3]]}")
        self.assertEqual(missed, [], "bug classes the harness no longer catches:\n" + "\n".join(missed))


if __name__ == "__main__":
    unittest.main()
