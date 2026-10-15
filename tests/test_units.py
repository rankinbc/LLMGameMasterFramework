"""Unit tests for the harness itself: gm_base, gm_checks and tools/sameness.py.

Run:  python -m unittest discover -s tests -v        (from the GM folder)
"""

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GM = os.path.dirname(HERE)
ENGINE_DIR = os.path.join(GM, "engine")
sys.path.insert(0, ENGINE_DIR)
sys.path.insert(0, os.path.join(GM, "tools"))
sys.path.insert(0, os.path.join(ENGINE_DIR, "example_lantern_chain"))
EXAMPLE = os.path.join(ENGINE_DIR, "example_lantern_chain", "engine.py")

import gm_base as B  # noqa: E402
import gm_checks as K  # noqa: E402
import gm_analysis as A  # noqa: E402
import gm_mutate as M  # noqa: E402
import sameness  # noqa: E402
from engine import G as Lantern  # noqa: E402


class RngTests(unittest.TestCase):
    def test_same_seed_same_rolls(self):
        a, b = B.RNG(5), B.RNG(5)
        self.assertEqual([a.d(20) for _ in range(10)], [b.d(20) for _ in range(10)])

    def test_state_roundtrip_continues_identically(self):
        a = B.RNG(9)
        [a.d(6) for _ in range(4)]
        state = json.loads(json.dumps(a.getstate()))
        b = B.RNG(9, state)
        self.assertEqual([a.d(6) for _ in range(6)], [b.d(6) for _ in range(6)])

    def test_check_reports_roll_text(self):
        ok, text = B.RNG(1).check(1, 6, "x")
        self.assertTrue(ok)
        self.assertIn("need 1+", text)


class MatchTests(unittest.TestCase):
    opts = [
        {"id": "light", "label": "a", "args": {"lantern": 3}},
        {"id": "light", "label": "b", "args": {"lantern": 4}},
        {"id": "haul", "label": "c", "args": {}},
    ]

    def test_single_option_with_no_args_matches(self):
        self.assertEqual(B._match(self.opts, "haul", {})["label"], "c")

    def test_args_that_contradict_the_option_are_rejected(self):
        one = [{"id": "shore", "label": "s", "args": {"layer": 2}}]
        self.assertEqual(B._match(one, "shore", {"layer": 2})["label"], "s")
        self.assertEqual(B._match(one, "shore", {})["label"], "s")
        with self.assertRaises(B.IllegalAction):
            B._match(one, "shore", {"layer": 3})

    def test_same_id_needs_args(self):
        with self.assertRaises(B.IllegalAction):
            B._match(self.opts, "light", {})
        self.assertEqual(B._match(self.opts, "light", {"lantern": 4})["label"], "b")

    def test_unknown_action(self):
        with self.assertRaises(B.IllegalAction):
            B._match(self.opts, "nope", {})


class SaveTests(unittest.TestCase):
    def test_failed_save_leaves_old_state(self):
        old = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            try:
                B._save({"a": 1})
                with self.assertRaises(TypeError):
                    B._save({"a": {1, 2}})
                with open("state.json", encoding="utf-8") as f:
                    self.assertEqual(json.load(f), {"a": 1})
            finally:
                os.chdir(old)


class LintTests(unittest.TestCase):
    def test_text_problems(self):
        self.assertEqual(K.text_problems("Lantern 3 lit."), [])
        self.assertTrue(K.text_problems("Lantern None lit."))
        self.assertTrue(K.text_problems("The {column} advances"))
        self.assertTrue(K.text_problems("Oil +-3"))
        self.assertTrue(K.text_problems(""))
        self.assertTrue(K.text_problems(5))

    def test_scan_state(self):
        self.assertEqual(K.scan_state({"a": 1, "b": [1, 2], "c": {"d": "x"}}), [])
        self.assertTrue(K.scan_state({"a": float("nan")}))
        self.assertTrue(K.scan_state({"a": 10**9}))
        self.assertTrue(K.scan_state({1: "x"}))
        self.assertTrue(K.scan_state({"a": {1, 2}}))
        self.assertTrue(K.scan_state({"a": (1, 2)}))

    def test_status_labels_stable(self):
        a = K.status_labels("Oil 12 | Column 0/32 | Ridge ###.. | Wind 3")
        b = K.status_labels("Oil 4 | Column 11/32 | Ridge #.... | Wind 1,2")
        self.assertEqual(a, b)
        self.assertEqual(a, ["oil", "column", "ridge", "wind"])


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.g = Lantern()
        self.s, _ = B._new(self.g, 3)

    def test_clean_state_has_no_problems(self):
        opts = self.g.options(self.s)
        self.assertEqual(K.integrity(self.g, self.s, ["Lantern 1 lit."], opts), [])

    def test_bad_event_is_reported(self):
        opts = self.g.options(self.s)
        self.assertTrue(K.integrity(self.g, self.s, ["Oil is None"], opts))

    def test_out_of_bounds_is_reported(self):
        self.s["oil"] = 999
        self.assertTrue(K.integrity(self.g, self.s, [], self.g.options(self.s)))


class HarnessTests(unittest.TestCase):
    def test_scripted_dice_and_chances(self):
        g = Lantern()
        t = K.T(g, B)
        r = t.rng(dice=[6, 2], chances=[0.01])
        self.assertEqual(r.d(6), 6)
        self.assertEqual(r.d(6), 2)
        self.assertTrue(r.chance(0.5))

    def test_fresh_overrides_and_hidden(self):
        t = K.T(Lantern(), B)
        s = t.fresh(oil=7, hidden__stride=3)
        self.assertEqual(s["oil"], 7)
        self.assertEqual(s["hidden"]["stride"], 3)

    def test_rule_tests_of_example_pass(self):
        self.assertEqual(K.run_rule_tests(Lantern(), B), [])


class _Toy(B.Game):
    """A game whose options() crashes in a state normal play never reaches (turn 3 or later with n at its minimum)."""

    name = "Toy"
    turns = 6

    def init_state(self, rng):
        return {"n": 3, "hidden": {}}

    def options(self, s):
        if s["_turn"] >= 3 and s["n"] <= 3:
            raise ZeroDivisionError("boundary")
        return [{"id": "go", "label": "Go on", "args": {}}]

    def apply(self, s, a, args, rng):
        return ["You go on."]

    def advance(self, s, rng):
        s["n"] = 2 + s["_turn"]
        return ["Time passes."]

    def status_line(self, s):
        return f"N {s['n']}"

    def check_end(self, s):
        return {"result": "win", "reason": "done"} if s["_turn"] > 5 else None

    def heuristic(self, s, options, rng):
        return "go"


class FuzzTests(unittest.TestCase):
    def test_fuzz_finds_crash_in_unvisited_state(self):
        g = _Toy()
        obs = K.observe(g, B, games=10)
        self.assertEqual(obs["problems"].get("crash"), None, "normal play must not reach the crash")
        crashes, tried = K.fuzz(g, B, obs)
        self.assertTrue(crashes, "fuzz should find the boundary crash")
        self.assertGreater(tried, 0)


class ChecksOnExampleTests(unittest.TestCase):
    def test_trace_is_deterministic_and_readable(self):
        g = Lantern()
        a, b = K.trace(g, B, 7), K.trace(g, B, 7)
        self.assertEqual(a, b)
        self.assertTrue(a[-1].startswith("END"))

    def test_profile_has_expected_shape(self):
        g = Lantern()
        p = A.profile(g, 3, 6)
        self.assertIn("dilemma_share", p)
        self.assertTrue(p["turns"])

    def test_ablate_marks_haul_needed(self):
        g = Lantern()
        out = A.ablate(g, 30, 4)
        verdicts = {a["action"]: a["verdict"] for a in out["actions"]}
        self.assertEqual(verdicts["haul"], "needed")


class SamenessTests(unittest.TestCase):
    vocab = sameness.load_vocab()

    def game(self, order, **traits):
        base = {
            "primary_bucket": "cash", "tracked_count": "3", "rival_type": "hunter", "rival_tell": "before",
            "win_shape": "threshold", "clock_shape": "upkeep", "opening_shape": "plan", "ending_shape": "flat",
            "midpoint_event": "none", "player_frame": "manager", "decision_unit": "pick-action",
            "setting_family": "workplace", "turn_band": "mid",
        }
        base.update(traits)
        return {"id": f"g{order}", "title": f"Game {order}", "order": order, "result": "win", "turns": 16,
                "rolls": {"FORM": order, "SET": order + 10, "WIN": order}, "traits": base}

    def test_validate_accepts_good_and_rejects_bad(self):
        good = self.game(1)
        self.assertEqual(sameness.validate(good, self.vocab), [])
        bad = self.game(2, rival_type="dragon")
        self.assertTrue(sameness.validate(bad, self.vocab))

    def test_streak_dominant_unrolled_and_bent(self):
        games = [self.game(i) for i in range(1, 8)]  # rival_type never changes; WIN roll changes every game
        rows = {r["trait"]: r for r in sameness.analyze(games, self.vocab)}
        rival = rows["rival_type"]
        self.assertTrue(any(f.startswith("STREAK") for f in rival["flags"]))
        self.assertIn("UNROLLED", rival["flags"])
        win = rows["win_shape"]
        self.assertTrue(any(f.startswith("BENT") for f in win["flags"]), win["flags"])

    def test_varied_series_is_not_flagged(self):
        kinds = ["hunter", "marcher", "counter", "racer", "bidder", "saboteur", "environment", "schedule"]
        games = [self.game(i + 1, rival_type=kinds[i]) for i in range(8)]
        rows = {r["trait"]: r for r in sameness.analyze(games, self.vocab)}
        self.assertEqual(rows["rival_type"]["flags"], [])

    def test_pair_similarity(self):
        a, b = self.game(1), self.game(2, rival_type="racer")
        sim, same = sameness.pair_similarity(a, b, self.vocab)
        self.assertNotIn("rival_type", same)
        self.assertGreater(sim, 0.8)

    @staticmethod
    def _lines(path):
        with open(path, encoding="utf-8") as f:
            return len(f.read().splitlines())

    def test_add_appends_and_reports(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "fp.jsonl")
            script = os.path.join(GM, "tools", "sameness.py")
            r = subprocess.run([sys.executable, script, "add", json.dumps(self.game(1)), "--file", path], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self._lines(path), 1)
            bad = subprocess.run([sys.executable, script, "add", json.dumps(self.game(2, rival_type="dragon")), "--file", path], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(self._lines(path), 1, "a rejected fingerprint must not be written")


class ParamTests(unittest.TestCase):
    opt = {"id": "bid", "label": "Bid", "args": {"lot": 3}, "params": {"amount": {"min": 1, "max": 40, "step": 1}}}
    pick = {"id": "send", "label": "Send", "args": {}, "params": {"oil": {"choices": [3, 6]}}}

    def test_missing_param_is_rejected_with_a_hint(self):
        with self.assertRaises(B.IllegalAction) as cm:
            B._match([self.opt], "bid", {})
        self.assertIn("amount", cm.exception.msg)

    def test_param_range_and_type_are_enforced(self):
        self.assertEqual(B._match([self.opt], "bid", {"amount": 12})["id"], "bid")
        for bad in (0, 41, 2.5, "7", True):
            with self.assertRaises(B.IllegalAction, msg=repr(bad)):
                B._match([self.opt], "bid", {"amount": bad})

    def test_choices_param(self):
        self.assertEqual(B._match([self.pick], "send", {"oil": 6})["id"], "send")
        with self.assertRaises(B.IllegalAction):
            B._match([self.pick], "send", {"oil": 4})

    def test_concretization_fills_params_validly(self):
        c = B._concrete_first(self.opt)
        self.assertIn(c["args"]["amount"], range(1, 41))
        self.assertEqual(c["args"]["lot"], 3)
        r = B._concrete_random(self.opt, B.RNG(3))
        B._check_params(r, r["args"])

    def test_expand_is_bounded_and_valid(self):
        variants = B._expand(self.opt)
        self.assertLessEqual(len(variants), 6)
        self.assertGreater(len(variants), 1)
        for v in variants:
            B._check_params(v, v["args"])

    def test_norm_accepts_a_heuristic_that_names_the_value(self):
        got = B._norm({"id": "bid", "args": {"amount": 9}}, [self.opt])
        self.assertEqual(got["args"], {"lot": 3, "amount": 9})
        with self.assertRaises(B.IllegalAction):
            B._norm({"id": "bid", "args": {"amount": 99}}, [self.opt])

    def test_malformed_param_spec_is_a_crash(self):
        bad = {"id": "x", "label": "X", "args": {}, "params": {"n": {"min": 5, "max": 1}}}
        with self.assertRaises(RuntimeError):
            B._validate_opts([bad], 1)


class TextLintTests(unittest.TestCase):
    def test_plural_lint(self):
        self.assertTrue(K.plural_problems("Dusk: 1 lit lanterns burned 1 oil."))
        self.assertTrue(K.plural_problems("1 nights to go"))
        self.assertEqual(K.plural_problems("Dusk: 1 lit lantern burned 1 oil."), [])
        self.assertEqual(K.plural_problems("Lantern 1 lit."), [])
        self.assertEqual(K.plural_problems("2 nights to go"), [])

    def test_plural_helper(self):
        self.assertEqual(K.plural(1, "night"), "1 night")
        self.assertEqual(K.plural(0, "night"), "0 nights")
        self.assertEqual(K.plural(3, "lit lantern"), "3 lit lanterns")
        self.assertEqual(K.plural(2, "city"), "2 cities")
        self.assertEqual(K.plural(2, "batch"), "2 batches")
        self.assertEqual(K.plural(2, "person", "people"), "2 people")


class TuneCounterTests(unittest.TestCase):
    def test_only_logic_or_number_changes_count_as_a_round(self):
        old = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            try:
                path = os.path.join(d, "e.py")

                def write(src):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(src)

                write('X = 5\nLABEL = "Hello"\n')
                self.assertEqual(B._bump_tune(path), (1, True))
                write('X = 5\nLABEL = "A different wording"\n')
                self.assertEqual(B._bump_tune(path), (1, False), "a wording edit is not a new round")
                write('X = 6\nLABEL = "A different wording"\n')
                self.assertEqual(B._bump_tune(path), (2, True), "a number change is a new round")
            finally:
                os.chdir(old)


class _EarlyEnd(_Toy):
    """check_end ends the game as soon as _turn reaches the budget."""

    def options(self, s):
        return [{"id": "go", "label": "Go on", "args": {}}]

    def check_end(self, s):
        return {"result": "win", "reason": "count"} if s["_turn"] >= self.turns else None


class _LateEnd(_Toy):
    """check_end ends the game only after the budget has been played."""

    def options(self, s):
        return [{"id": "go", "label": "Go on", "args": {}}]

    def check_end(self, s):
        return {"result": "win", "reason": "count"} if s["_turn"] > self.turns else None


class CheckEndTests(unittest.TestCase):
    def test_ending_at_the_budget_is_found(self):
        g = _EarlyEnd()
        snaps = [{"n": 3, "hidden": {}, "_turn": 4, "_ended": None}]
        self.assertTrue(K.check_end_problems(g, B, snaps))

    def test_ending_after_the_budget_is_fine(self):
        g = _LateEnd()
        snaps = [{"n": 3, "hidden": {}, "_turn": 4, "_ended": None}]
        self.assertEqual(K.check_end_problems(g, B, snaps), [])


class CliTests(unittest.TestCase):
    """The real command line, in a scratch folder: new, step with wrong args, replay, autopsy, fingerprint."""

    def run_cli(self, cwd, *args):
        env = dict(os.environ, GM_SERIAL="1")
        return subprocess.run([sys.executable, EXAMPLE, *args], capture_output=True, text=True, cwd=cwd, env=env, timeout=600)

    def test_play_replay_autopsy(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(d, "new", "5").returncode, 0)
            for _ in range(4):
                r = self.run_cli(d, "step", "haul")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(json.loads(r.stdout)["integrity"], [])
            def state_text():
                with open(os.path.join(d, "state.json"), encoding="utf-8") as f:
                    return f.read()

            before = state_text()
            bad = self.run_cli(d, "step", "light", json.dumps({"lantern": 99}))
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(state_text(), before)
            rep = json.loads(self.run_cli(d, "replay").stdout)
            self.assertTrue(rep["ok"])
            self.assertTrue(rep["matches_saved_state"])
            auto = json.loads(self.run_cli(d, "autopsy", "6").stdout)
            self.assertIn("biggest_swing", auto)
            self.assertIn("dilemma_turns", auto)

    def test_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            fp = json.loads(self.run_cli(d, "fingerprint").stdout)
            self.assertEqual(fp["tracked_count"], "3")
            self.assertIn("haul", fp["actions"])

    def test_scripted_trace_marks_unoffered_moves(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.run_cli(d, "trace", "7", "--do", "haul,signal:oil=3,haul").stdout
            self.assertIn("scripted move signal", out)


class MutationScoreTests(unittest.TestCase):
    def test_strong_tests_score_high_and_trivial_tests_score_low(self):
        os.environ["GM_SERIAL"] = "1"
        try:
            strong = M.run_mutation(Lantern(), B, EXAMPLE)
            self.assertGreaterEqual(strong["rate"], 0.7, strong["survivors"][:5])
            with open(EXAMPLE, encoding="utf-8") as f:
                src = f.read()
            weak_src = src.replace(
                "    def rule_tests(self):",
                "    def rule_tests(self):\n        return [(i, 'trivial', lambda t: None) for i in range(1, 9)]\n\n    def rule_tests_real(self):",
                1,
            )
            weak_src = weak_src.replace('os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")', repr(ENGINE_DIR))
            with tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "weak.py")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(weak_src)
                spec = importlib.util.spec_from_file_location("weak_engine", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                weak = M.run_mutation(mod.G(), B, path)
            self.assertLess(weak["rate"], 0.5, "trivial tests must not score well")
            self.assertLess(weak["rate"], strong["rate"])
        finally:
            os.environ.pop("GM_SERIAL", None)


class _Order(B.Game):
    """Records which turn number each phase sees."""

    name = "Order"
    turns = 3

    def init_state(self, rng):
        return {"seen": [], "hidden": {}}

    def options(self, s):
        return [{"id": "go", "label": "Go on", "args": {}}]

    def apply(self, s, a, args, rng):
        s["seen"].append(["apply", s["_turn"]])
        if s.get("die_now"):
            self.finish(s, "loss", "died in the action")
        return ["You go on."]

    def advance(self, s, rng):
        s["seen"].append(["dusk", s["_turn"]])
        return ["Dusk falls."]

    def status_line(self, s):
        return f"Turn {s['_turn']}"

    def check_end(self, s):
        return None

    def final_check(self, s):
        return {"result": "win", "reason": "the budget is scored"}


class StepOrderTests(unittest.TestCase):
    def test_action_and_dusk_see_the_same_turn_and_the_budget_is_scored(self):
        g = _Order()
        s, _ = B._new(g, 1)
        for _ in range(3):
            s, _, _ = B._step(g, s, "go", {})
        self.assertEqual(s["seen"], [["apply", 1], ["dusk", 1], ["apply", 2], ["dusk", 2], ["apply", 3], ["dusk", 3]])
        self.assertEqual(s["_ended"], {"result": "win", "reason": "the budget is scored", "phase": "budget"})
        self.assertEqual(s["_turn"], 4)

    def test_finish_inside_the_action_skips_dusk(self):
        g = _Order()
        s, _ = B._new(g, 1)
        s["die_now"] = True
        s, events, _ = B._step(g, s, "go", {})
        self.assertEqual(s["_ended"]["phase"], "action")
        self.assertEqual(s["_ended"]["reason"], "died in the action")
        self.assertEqual(s["seen"], [["apply", 1]])
        self.assertNotIn("Dusk falls.", events)

    def test_a_finished_game_does_not_step(self):
        g = _Order()
        s, _ = B._new(g, 1)
        s["_ended"] = {"result": "loss", "reason": "x"}
        s, events, log = B._step(g, s, "go", {})
        self.assertEqual(events, ["Game is over."])
        self.assertEqual(s["seen"], [])

    def test_the_turn_json_never_shows_a_turn_past_the_budget(self):
        g = _Order()
        s, _ = B._new(g, 1)
        for _ in range(3):
            s, _, _ = B._step(g, s, "go", {})
        self.assertEqual(B._turn_json(g, s, [])["turn"], 3)


class StrictArgTests(unittest.TestCase):
    bid = {"id": "bid", "label": "Bid", "args": {}, "params": {"amount": {"min": 1, "max": 9}}}
    plain = {"id": "haul", "label": "Haul", "args": {}}

    def test_unknown_args_are_rejected(self):
        with self.assertRaises(B.IllegalAction):
            B._match([self.plain], "haul", {"qty": 2})
        with self.assertRaises(B.IllegalAction):
            B._match([self.bid], "bid", {"amount": 3, "extra": 1})

    def test_whole_number_params_reject_fractions_and_coerce_floats(self):
        with self.assertRaises(B.IllegalAction):
            B._match([self.bid], "bid", {"amount": 1.5})
        cleaned = B._clean_args(self.bid, {"amount": 3.0})
        self.assertEqual(cleaned["amount"], 3)
        self.assertIsInstance(cleaned["amount"], int)

    def test_choices_coerce_to_the_declared_value(self):
        opt = {"id": "send", "label": "Send", "args": {}, "params": {"oil": {"choices": [3, 6]}}}
        self.assertIsInstance(B._clean_args(opt, {"oil": 6.0})["oil"], int)


class _OneChoice(B.Game):
    name = "OneChoice"
    turns = 2
    CONSTANTS = {"N": 1}
    RULES = "1. You hold {N|coin} and spend {N|coin}.\n"

    def init_state(self, rng):
        return {"hidden": {}}

    def options(self, s):
        return [{"id": "go", "label": "Go", "args": {}}]

    def apply(self, s, a, args, rng):
        return ["ok"]

    def advance(self, s, rng):
        return []

    def status_line(self, s):
        return "Turn"

    def check_end(self, s):
        return None


class MiscHarnessTests(unittest.TestCase):
    def test_rules_can_pluralize_a_constant(self):
        g = _OneChoice()
        self.assertEqual(g.rules(), "1. You hold 1 coin and spend 1 coin.")
        g.C["N"] = 3
        self.assertEqual(g.rules(), "1. You hold 3 coins and spend 3 coins.")

    def test_one_option_with_a_real_param_is_not_forced(self):
        forced = [{"id": "x", "label": "X", "args": {}, "params": {"n": {"choices": [4]}}}]
        free = [{"id": "x", "label": "X", "args": {}, "params": {"n": {"choices": [4, 5]}}}]
        self.assertTrue(B._is_forced(forced))
        self.assertFalse(B._is_forced(free))
        self.assertFalse(B._is_forced(forced + forced))

    def test_fresh_states_do_not_share_override_objects(self):
        t = K.T(Lantern(), B)
        lst = [True, True, True, False, False]
        s = t.fresh(lit=lst)
        lst.append("leak")
        self.assertEqual(len(s["lit"]), 5)

    def test_slack_at_the_cap_turns_a_small_band_miss_into_a_warning(self):
        g = Lantern()
        results = [{"seed": i, "result": "win" if i <= 47 else "loss", "turn": 16, "reason": "x"} for i in range(1, 101)]
        stats = {"n_opts": [3], "offered": B.Counter(), "picked": B.Counter()}
        strict, _ = B._summarize(g, 100, "heuristic", results, stats, B.Counter(), slack=0.0)
        slack, _ = B._summarize(g, 100, "heuristic", results, stats, B.Counter(), slack=0.1)
        self.assertTrue(any("TOO EASY" in f for f in strict["flags"]))
        self.assertFalse(any("TOO EASY" in f for f in slack["flags"]))
        self.assertTrue(any("TOO EASY" in w for w in slack["warnings"]))
        results = [{"seed": i, "result": "win" if i <= 60 else "loss", "turn": 16, "reason": "x"} for i in range(1, 101)]
        far, _ = B._summarize(g, 100, "heuristic", results, stats, B.Counter(), slack=0.1)
        self.assertTrue(any("TOO EASY" in f for f in far["flags"]), "a miss beyond the slack is still a flag")

    def test_the_engine_hash_ignores_text_and_rule_tests(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, c = (os.path.join(d, n) for n in ("a.py", "b.py", "c.py"))
            base = "class G:\n    def apply(self):\n        return {n}\n    def rule_tests(self):\n        return {t}\n"
            for path, n, tests in ((a, 5, "[1]"), (b, 5, "[1, 2, 3, 4]"), (c, 6, "[1]")):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(base.format(n=n, t=tests))
            self.assertEqual(B._engine_hash(a), B._engine_hash(b), "more tests are not a new tuning round")
            hd, he = os.path.join(d, "hd.py"), os.path.join(d, "he.py")
            heur = "class G:\n    def apply(self):\n        return 5\n    def rule_tests(self):\n        return [1]\n    def heuristic(self):\n        return {pick!r}\n"
            for path, pick in ((hd, "haul"), (he, "shield")):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(heur.format(pick=pick))
            self.assertEqual(B._engine_hash(hd), B._engine_hash(he), "a better heuristic is not a new tuning round")
            self.assertNotEqual(B._engine_hash(a), B._engine_hash(c), "a changed number is")


class _Tie(B.Game):
    """Every move loses, so every rollout ties; look-ahead must fall back to the heuristic's pick."""

    name = "Tie"
    turns = 2

    def init_state(self, rng):
        return {"hidden": {}}

    def options(self, s):
        return [{"id": "a", "label": "A", "args": {}}, {"id": "b", "label": "B", "args": {}}, {"id": "c", "label": "C", "args": {}}]

    def apply(self, s, a, args, rng):
        return ["ok"]

    def advance(self, s, rng):
        return []

    def status_line(self, s):
        return "Turn"

    def check_end(self, s):
        return None

    def heuristic(self, s, options, rng):
        return "c"


class LookaheadTests(unittest.TestCase):
    def test_ties_go_to_the_heuristic_not_the_first_option(self):
        import random
        g = _Tie()
        s, _ = B._new(g, 1)
        picks = {B._lookahead(g, s, g.options(s), random.Random(i), 4)["id"] for i in range(10)}
        self.assertEqual(picks, {"c"})

    def test_the_heuristics_param_value_is_always_a_candidate(self):
        import random

        class Param(_Tie):
            def options(self, s):
                return [{"id": "bid", "label": "Bid", "args": {}, "params": {"amount": {"min": 1, "max": 99}}}]

            def heuristic(self, s, options, rng):
                return {"id": "bid", "args": {"amount": 13}}

        g = Param()
        s, _ = B._new(g, 1)
        pick = B._lookahead(g, s, g.options(s), random.Random(3), 4)
        self.assertEqual(pick["args"]["amount"], 13)


MUTATE_SRC = """
class G:
    def apply(self, s):
        x = s["a"] + 7
        y = s["b"] * 11  # lit-ok
        z = s["c"] + 9  # no-mutate
        return helper(x)

    def heuristic(self, s):
        return s["a"] + 13


def helper(n):
    return n + 5
"""


class MutationScopeTests(unittest.TestCase):
    def test_helpers_are_mutated_and_markers_and_excluded_methods_are_skipped(self):
        import ast
        cands = M.candidates(ast.parse(MUTATE_SRC), "G", MUTATE_SRC)
        lines = {n.lineno for _, n in cands}
        text = MUTATE_SRC.splitlines()
        self.assertTrue(any("n + 5" in text[ln - 1] for ln in lines), "module-level helpers must be mutated")
        self.assertFalse(any("no-mutate" in text[ln - 1] for ln in lines), "# no-mutate lines must be skipped")
        self.assertFalse(any("13" in text[ln - 1] for ln in lines), "the heuristic is not mutated")

    def test_literal_report_finds_hidden_numbers_and_honors_lit_ok(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "g.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(MUTATE_SRC)
            report = " ".join(M.literal_report(path, "G"))
            self.assertIn("7", report)
            self.assertIn("5", report)
            self.assertNotIn("11", report)


class CliHostileInputTests(unittest.TestCase):
    """Garbage on the command line is refused cleanly: no traceback, nothing written."""

    def run_cli(self, cwd, *args):
        env = dict(os.environ, GM_SERIAL="1")
        return subprocess.run([sys.executable, EXAMPLE, *args], capture_output=True, text=True, cwd=cwd, env=env, timeout=600)

    @staticmethod
    def read(d, name):
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return f.read()

    def test_bad_input_is_refused_without_a_traceback_and_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(d, "new", "5").returncode, 0)
            self.assertEqual(self.run_cli(d, "step", "haul").returncode, 0)
            before = {n: self.read(d, n) for n in ("state.json", "history.jsonl", "rolls.log")}
            hostile = [
                ("step", "haul", "{bad"), ("step", "haul", "null"), ("step", "haul", "[1]"), ("step", "haul", '"x"'),
                ("step", "haul", '{"qty": 2}'), ("step", "nope"), ("step", "#99"), ("step", "#abc"), ("step", "#0"),
                ("step", "light", "{}"), ("step", "light", '{"lantern": 99}'), ("new", "abc"), ("new", "1.5"),
                ("check", "BAR0=19"), ("bogus",),
            ]
            for args in hostile:
                if args[0] == "new":
                    continue  # `new` legitimately rewrites state; only its error text is checked below
                r = self.run_cli(d, *args)
                self.assertNotEqual(r.returncode, 0, args)
                self.assertNotIn("Traceback", r.stderr, args)
            for args in (("new", "abc"), ("new", "1.5")):
                r = self.run_cli(d, *args)
                self.assertNotEqual(r.returncode, 0, args)
                self.assertNotIn("Traceback", r.stderr, args)
            after = {n: self.read(d, n) for n in ("state.json", "history.jsonl", "rolls.log")}
            self.assertEqual(before, after, "a refused command must not change state, history or the roll log")

    def test_a_finished_game_refuses_further_steps_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli(d, "new", "5")
            for _ in range(20):
                r = self.run_cli(d, "step", "haul")
                if r.returncode != 0 or json.loads(r.stdout)["ended"]:
                    break
            self.assertTrue(json.loads(self.run_cli(d, "status").stdout)["ended"])
            before = {n: self.read(d, n) for n in ("state.json", "history.jsonl", "rolls.log")}
            r = self.run_cli(d, "step", "haul")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("over", r.stderr)
            self.assertEqual(json.loads(self.run_cli(d, "options").stdout), [])
            self.assertEqual(before, {n: self.read(d, n) for n in ("state.json", "history.jsonl", "rolls.log")})
            auto = json.loads(self.run_cli(d, "autopsy", "4").stdout)
            self.assertLessEqual(auto["turns_played"], 16)

    def test_the_roll_log_names_the_turn_that_was_played(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli(d, "new", "5")
            self.run_cli(d, "step", "haul")
            self.assertIn("turn 1 haul", self.read(d, "rolls.log"))


class _Vocab(B.Game):
    """An end reason uses a word the sheet never mentions."""

    name = "Vocab"
    turns = 2
    RULES = "1. You gather dens in the valley.\n"

    def init_state(self, rng):
        return {"hidden": {}}

    def options(self, s):
        return [{"id": "go", "label": "Gather a den", "args": {}}]

    def apply(self, s, a, args, rng):
        return ["You gather a den. Then the Wall stands firm."]

    def advance(self, s, rng):
        return []

    def status_line(self, s):
        return "Dens"

    def check_end(self, s):
        return None


class VocabularyTests(unittest.TestCase):
    def test_a_word_from_an_earlier_draft_is_listed(self):
        obs = K.observe(_Vocab(), B, games=3)
        self.assertTrue(any(w.startswith("Wall") for w in obs["stat"]["vocab"]), obs["stat"]["vocab"])

    def test_words_the_sheet_or_options_use_are_not_listed(self):
        obs = K.observe(Lantern(), B, games=10)
        self.assertEqual(obs["stat"]["vocab"], [])


class ScriptedDriftTests(unittest.TestCase):
    def test_drift_follows_the_script_and_clamps(self):
        r = K._scripted(B, 1, None, None, None, [1, -1, 0, 1])
        self.assertEqual(r.drift(5, 0, 6), 6)
        self.assertEqual(r.drift(0, 0, 6), 0)
        self.assertEqual(r.drift(3, 0, 6), 3)
        self.assertEqual(r.drift(6, 0, 6, step=2), 6)


class EarlyWinRuleTests(unittest.TestCase):
    def test_a_rare_lucky_random_win_is_not_a_flag_but_a_heuristic_one_is(self):
        g = Lantern()
        stats = {"n_opts": [3], "offered": B.Counter(), "picked": B.Counter()}
        results = [{"seed": i, "result": "loss", "turn": 16, "reason": "x"} for i in range(1, 101)]
        results[0] = {"seed": 1, "result": "win", "turn": 5, "reason": "lucky"}
        rnd, _ = B._summarize(g, 100, "random", results, stats, B.Counter())
        heur, _ = B._summarize(g, 100, "heuristic", results, stats, B.Counter())
        self.assertFalse(any("EARLY WIN" in f for f in rnd["flags"]))
        self.assertTrue(any("EARLY WIN" in f for f in heur["flags"]))


class BoolArgTests(unittest.TestCase):
    def test_true_is_not_the_number_one(self):
        opts = [{"id": "light", "label": "L", "args": {"lantern": 1}}, {"id": "light", "label": "M", "args": {"lantern": 2}}]
        with self.assertRaises(B.IllegalAction):
            B._match(opts, "light", {"lantern": True})
        self.assertEqual(B._match(opts, "light", {"lantern": 1.0})["label"], "L")


class BalanceTests(unittest.TestCase):
    def test_a_hidden_starting_value_that_decides_the_game_is_reported(self):
        g = Lantern()
        stats = {"n_opts": [3], "offered": B.Counter(), "picked": B.Counter()}
        results = []
        for i in range(1, 121):
            style = i % 3
            win = (i % 7 < 6) if style == 0 else (i % 7 < 1) if style == 1 else (i % 7 < 3)
            results.append({"seed": i, "result": "win" if win else "loss", "turn": 16, "reason": "x", "h0": {"style": style}})
        summary, _ = B._summarize(g, 120, "heuristic", results, stats, B.Counter())
        self.assertTrue(summary["hidden_balance"], "a 0.14 to 0.86 spread must be reported")
        self.assertEqual(summary["hidden_balance"][0][0], "style")
        even = [dict(r, h0={"style": r["seed"] % 3}, result="win" if r["seed"] % 2 else "loss") for r in results]
        summary, _ = B._summarize(g, 120, "heuristic", even, stats, B.Counter())
        self.assertEqual(summary["hidden_balance"], [])


class TextsReportTests(unittest.TestCase):
    def test_every_wording_is_listed_once_with_numbers_masked(self):
        lines = K.texts_report(Lantern(), B, games=12)
        text = "\n".join(lines)
        self.assertIn("-- event wordings", text)
        self.assertIn("The wind snuffed lantern #.", text)
        self.assertIn("Oil # | Column #/# | Ridge", text)
        self.assertTrue(any(ln.strip().endswith("column stopped at #, needed #") or "oil ran out" in ln for ln in lines))


class _Gated(B.Game):
    name = "Gated"
    turns = 4
    CONSTANTS = {"N": 2, "GOAL": 5}
    RULES = "1. You keep {N|coin} and win at {GOAL}.\n"
    BOUNDS = {"pile": (0, "GOAL")}
    REACH = {"pile": "GOAL"}
    DERIVED = {"twice": lambda g, s: 2 * s["pile"]}
    GATES = {"spend": {"twice": 4}}

    def init_state(self, rng):
        return {"pile": 2, "hidden": {}}

    def options(self, s):
        o = [{"id": "gain", "label": "Gain one", "args": {}}]
        if 2 * s["pile"] >= 4:
            o.append({"id": "spend", "label": "Spend", "args": {}})
        return o

    def apply(self, s, a, args, rng):
        s["pile"] = min(s["pile"] + 1, self.C["GOAL"]) if a == "gain" else s["pile"] - 1
        return ["ok"]

    def advance(self, s, rng):
        return []

    def status_line(self, s):
        return f"Pile {s['pile']}"

    def check_end(self, s):
        return {"result": "win", "reason": "enough"} if s["pile"] >= self.C["GOAL"] else None


class ConstantNameTests(unittest.TestCase):
    def test_a_pluralized_constant_counts_as_on_the_sheet(self):
        flags, _ = B._sheet_flags(_Gated())
        self.assertEqual([f for f in flags if "not on the rulesheet" in f], [])

    def test_gates_may_use_derived_values_and_bounds_may_name_constants(self):
        g = _Gated()
        obs = K.observe(g, B, games=10)
        self.assertEqual(obs["problems"].get("hidden"), None)
        self.assertEqual(obs["problems"].get("ungated"), None)
        self.assertEqual(obs["problems"].get("bounds"), None)
        self.assertEqual(K.bounds_problems(g, {"pile": 9}), ["pile is 9, outside its declared range 0 to 5"])

    def test_texts_keep_the_sign(self):
        class Signs(_Gated):
            def apply(self, s, a, args, rng):
                s["pile"] = min(s["pile"] + 1, self.C["GOAL"])
                return ["Gold +3.", "Gold -3."]

        lines = K.texts_report(Signs(), B, games=4)
        self.assertTrue(any("Gold +#." in ln for ln in lines))
        self.assertTrue(any("Gold -#." in ln for ln in lines))


class NoGameTests(unittest.TestCase):
    def test_a_missing_state_file_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, EXAMPLE, "status"], capture_output=True, text=True, cwd=d, timeout=120)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("no game in progress", r.stderr)
            self.assertNotIn("Traceback", r.stderr)


class SwingCauseTests(unittest.TestCase):
    def test_a_drop_after_the_best_move_is_not_blamed_on_the_player(self):
        self.assertIn("events and dice", A.swing_cause(False, 0.62, 0.17, 0.62, 0.62))

    def test_a_drop_after_a_costly_move_is_the_players(self):
        self.assertEqual(A.swing_cause(False, 0.62, 0.17, 0.20, 0.62), "your choice")

    def test_a_rise_is_events_and_a_forced_move_is_no_choice(self):
        self.assertIn("events and dice", A.swing_cause(False, 0.20, 0.60, 0.20, 0.20))
        self.assertIn("no choice", A.swing_cause(True, 0.60, 0.20, 0.60, 0.60))


class DevCommandInputTests(unittest.TestCase):
    def run_cli(self, cwd, *args):
        env = dict(os.environ, GM_SERIAL="1")
        return subprocess.run([sys.executable, EXAMPLE, *args], capture_output=True, text=True, cwd=cwd, env=env, timeout=300)

    def test_bad_dev_input_is_a_clean_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            for args in (("selftest", "abc"), ("selftest", "0"), ("selftest", "-1"), ("selftest", "5", "bogus"),
                         ("sweep", "GOAL=abc"), ("ablate", "abc"), ("autopsy", "abc"), ("profile", "x"), ("bogus",)):
                r = self.run_cli(d, *args)
                self.assertNotEqual(r.returncode, 0, args)
                self.assertNotIn("Traceback", r.stderr, args)
                self.assertNotIn("engine crash", r.stderr, args)

    def test_unknown_command_lists_the_commands_and_param_errors_have_no_empty_options(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_cli(d, "bogus")
            self.assertIn("commands", r.stderr)
            self.assertIn("selftest", r.stderr)
            self.run_cli(d, "new", "5")
            r = self.run_cli(d, "step", "light", '{"lantern": 99}')
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn('"options": []', r.stderr)


class ArgNormalizationTests(unittest.TestCase):
    def test_the_engine_sees_the_options_own_value_not_the_callers_float(self):
        opt = {"id": "scan", "label": "Scan", "args": {"reach": 1}}
        self.assertIsInstance(B._clean_args(opt, {"reach": 1.0})["reach"], int)

    def test_nan_and_infinity_are_refused_cleanly(self):
        opt = {"id": "push", "label": "Push", "args": {}, "params": {"n": {"min": 1, "max": 5}}}
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(B.IllegalAction):
                B._clean_args(opt, {"n": bad})

    def test_a_roll_never_prints_need_zero(self):
        ok, text = B.RNG(1).check(0, 6)
        self.assertTrue(ok)
        self.assertIn("need 1+", text)

    def test_possessives_are_not_unknown_words(self):
        self.assertEqual(K._sentence_words("Then the Ferryman's barge leaves."), ["Ferryman"])

    def test_t_offered_and_label_do_not_need_the_param_value(self):
        t = K.T(Lantern(), B)
        s = t.fresh(oil=30, wind=[4])
        s["_turn"] = 9
        self.assertTrue(t.offered(s, "signal"))
        self.assertIn("Signal", t.label(s, "signal"))


class DamagedStateTests(unittest.TestCase):
    def run_cli(self, cwd, *args):
        env = dict(os.environ, GM_SERIAL="1")
        return subprocess.run([sys.executable, EXAMPLE, *args], capture_output=True, text=True, cwd=cwd, env=env, timeout=300)

    def test_a_truncated_state_file_is_named_and_replay_rebuilds_it(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli(d, "new", "5")
            for _ in range(3):
                self.run_cli(d, "step", "haul")
            path = os.path.join(d, "state.json")
            with open(path, encoding="utf-8") as f:
                good = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(good[: len(good) // 2])
            r = self.run_cli(d, "status")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("damaged", r.stderr)
            self.assertNotIn("command line", r.stderr)
            rep = json.loads(self.run_cli(d, "replay", "--apply").stdout)
            self.assertTrue(rep["ok"])
            self.assertEqual(json.loads(self.run_cli(d, "status").stdout)["turn"], 4)

    def test_every_refusal_inside_step_says_the_state_is_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli(d, "new", "5")
            for args in (("step", "haul", "{bad"), ("step", "haul", "[1]"), ("step", "#abc"), ("step", "nope"), ("step",)):
                r = self.run_cli(d, *args)
                self.assertNotEqual(r.returncode, 0, args)
                self.assertIn("state_unchanged", r.stderr, args)


class InOrderTests(unittest.TestCase):
    def test_in_order_passes_in_order_and_fails_out_of_order(self):
        t = K.T(Lantern(), B)
        t.in_order(["a happens", "then b", "last c"], ["a happens", "last c"])
        with self.assertRaises(AssertionError):
            t.in_order(["then b", "a happens"], ["a happens", "then b"])
        with self.assertRaises(AssertionError):
            t.in_order(["a happens"], ["a happens", "a happens"])


if __name__ == "__main__":
    unittest.main()
