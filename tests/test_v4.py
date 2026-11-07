"""Unit tests for the v4 contract: GROWTH, LADDER, PATHS, ECONOMY checks and the board command.

Run:  python -m unittest discover -s tests -v        (from the GM folder)
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GM = os.path.dirname(HERE)
ENGINE_DIR = os.path.join(GM, "engine")
sys.path.insert(0, ENGINE_DIR)

import gm_base as B  # noqa: E402
import gm_checks as K  # noqa: E402


class _Grower(B.Game):
    """A toy whose fleet grows one a turn: GROWTH holds, the ladder is climbed, two paths both win."""

    name = "Grower"
    turns = 30
    ACTIONS = ["mine", "sell", "raid", "build"]
    GROWTH = "fleet"
    ECONOMY = {"income": ["ore"], "stock": ["credits"], "sinks": ["build"]}
    LADDER = {"key": "tier", "tiers": ["sloop", "brig", "frigate"], "unlocks": {2: ["raid"], 3: ["build"]}}
    PATHS = {"haul": ["mine", "sell"], "raid": ["raid"]}

    def init_state(self, rng):
        return {"fleet": 2, "ore": 0, "credits": 0, "tier": 1, "hidden": {}}

    def options(self, s):
        return [{"id": a, "label": f"Do {a}", "args": {}} for a in self.ACTIONS]

    def apply(self, s, a, args, rng):
        return [f"You {a}."]

    def advance(self, s, rng):
        s["fleet"] += 1
        return []

    def status_line(self, s):
        return f"Fleet {s['fleet']} | Tier {s['tier']}"

    def check_end(self, s):
        return None

    def heuristic(self, s, options, rng):
        return "mine"


def rows_growth(start, mid, end, n=20):
    return [{"start": start, "mid": mid, "end": end} for _ in range(n)]


class GrowthTests(unittest.TestCase):
    def test_undeclared_is_a_warning_not_a_flag(self):
        g = B.Game()
        f, w = K.growth_problems(g, [])
        self.assertEqual(f, [])
        self.assertTrue(any("GROWTH not declared" in x for x in w))

    def test_growth_that_doubles_passes(self):
        f, w = K.growth_problems(_Grower(), rows_growth(2, 5, 8))
        self.assertEqual((f, w), ([], []))

    def test_growth_that_stalls_is_flagged(self):
        f, _w = K.growth_problems(_Grower(), rows_growth(2, 3, 3))
        self.assertTrue(f and "GROWTH:" in f[0] and "does not grow" in f[0], f)

    def test_plateau_in_the_last_third_is_a_warning(self):
        f, w = K.growth_problems(_Grower(), rows_growth(2, 6, 6))
        self.assertEqual(f, [])
        self.assertTrue(any("stops growing" in x for x in w), w)

    def test_a_zero_start_counts_as_one(self):
        f, _w = K.growth_problems(_Grower(), rows_growth(0, 2, 3))
        self.assertEqual(f, [])
        f, _w = K.growth_problems(_Grower(), rows_growth(0, 1, 3))
        self.assertTrue(f)

    def test_spec_forms(self):
        g = _Grower()
        self.assertEqual(K.growth_spec(g), {"key": "fleet", "factor": K.GROWTH_FACTOR, "by": K.GROWTH_BY})
        g.GROWTH = {"key": "fleet", "factor": 3}
        self.assertEqual(K.growth_spec(g)["factor"], 3)
        self.assertEqual(K.growth_mark(g), int(30 * K.GROWTH_BY))
        self.assertEqual(K.growth_value(g, {"fleet": 7}), 7)

    def test_too_few_games_is_silent(self):
        self.assertEqual(K.growth_problems(_Grower(), rows_growth(2, 2, 2, n=5)), ([], []))


def rows_ladder(t2_share, t3_share, n=20, t2_turn=8):
    rows = []
    for i in range(n):
        tier = 3 if i < t3_share * n else 2 if i < t2_share * n else 1
        rows.append({"tier_max": tier, "tier2_turn": t2_turn if tier >= 2 else None})
    return rows


class LadderTests(unittest.TestCase):
    def test_undeclared_is_a_warning(self):
        f, w = K.ladder_problems(B.Game(), [])
        self.assertEqual(f, [])
        self.assertTrue(any("LADDER not declared" in x for x in w))

    def test_a_climbed_ladder_passes(self):
        self.assertEqual(K.ladder_problems(_Grower(), rows_ladder(0.9, 0.6)), ([], []))

    def test_unreached_tiers_are_flagged(self):
        f, _w = K.ladder_problems(_Grower(), rows_ladder(0.5, 0.1))
        self.assertEqual(len(f), 2, f)
        self.assertIn("tier 2", f[0])
        self.assertIn("tier 3", f[1])

    def test_a_slow_ladder_is_a_warning(self):
        f, w = K.ladder_problems(_Grower(), rows_ladder(0.9, 0.6, t2_turn=20))
        self.assertEqual(f, [])
        self.assertTrue(any("past the midpoint" in x for x in w), w)

    def test_unlock_must_be_an_action(self):
        g = _Grower()
        g.LADDER = {"key": "tier", "tiers": ["a", "b", "c"], "unlocks": {2: ["nope"]}}
        f, _w = K.ladder_problems(g, rows_ladder(0.9, 0.6))
        self.assertTrue(any("not in ACTIONS" in x for x in f), f)

    def test_two_tiers_are_not_a_ladder(self):
        g = _Grower()
        g.LADDER = {"key": "tier", "tiers": ["a", "b"]}
        f, _w = K.ladder_problems(g, [])
        self.assertTrue(f)


def rows_paths(haul_wins, raid_wins, losses=5):
    rows = [{"result": "win", "picks": {"mine": 10, "sell": 8, "raid": 0}} for _ in range(haul_wins)]
    rows += [{"result": "win", "picks": {"mine": 4, "sell": 2, "raid": 6}} for _ in range(raid_wins)]
    rows += [{"result": "loss", "picks": {"mine": 3}} for _ in range(losses)]
    return rows


class PathsTests(unittest.TestCase):
    def test_undeclared_is_a_warning(self):
        f, w = K.paths_problems(B.Game(), [])
        self.assertEqual(f, [])
        self.assertTrue(any("PATHS not declared" in x for x in w))

    def test_two_live_paths_pass(self):
        self.assertEqual(K.paths_problems(_Grower(), rows_paths(10, 8)), ([], []))

    def test_a_dead_path_is_flagged(self):
        f, _w = K.paths_problems(_Grower(), rows_paths(18, 1))
        self.assertTrue(f and "raid path" in f[0], f)

    def test_too_few_wins_is_silent(self):
        self.assertEqual(K.paths_problems(_Grower(), rows_paths(4, 0)), ([], []))

    def test_family_ids_must_be_actions(self):
        g = _Grower()
        g.PATHS = {"a": ["mine"], "b": ["fly"]}
        f, _w = K.paths_problems(g, [])
        self.assertTrue(any("not in ACTIONS" in x for x in f), f)

    def test_one_family_is_not_paths(self):
        g = _Grower()
        g.PATHS = {"a": ["mine"]}
        f, _w = K.paths_problems(g, [])
        self.assertTrue(f)


class EconomyAndDeclarationTests(unittest.TestCase):
    def test_economy_parts_must_exist(self):
        g = _Grower()
        s0, _ = B._new(g, 1)
        self.assertEqual(K.economy_problems(g, s0), ([], []))
        g.ECONOMY = {"income": ["gold"], "stock": [], "sinks": ["fly"]}
        f, _w = K.economy_problems(g, s0)
        self.assertEqual(len(f), 3, f)

    def test_undeclared_economy_is_a_warning(self):
        f, w = K.economy_problems(B.Game(), None)
        self.assertEqual(f, [])
        self.assertTrue(w)

    def test_growth_and_ladder_keys_must_be_numbers(self):
        g = _Grower()
        s0, _ = B._new(g, 1)
        self.assertEqual(K.declaration_problems(g, s0), [])
        g.GROWTH = "ships"
        g.LADDER = {"key": "rank", "tiers": ["a", "b", "c"]}
        self.assertEqual(len(K.declaration_problems(g, s0)), 2)


class RecordingTests(unittest.TestCase):
    """_play records the growth row, the tier reach and the picks for every game."""

    def test_selftest_rows_carry_growth_tier_and_picks(self):
        g = _Grower()
        g.turns = 12
        results, _stats, _tags = B._run_games(g, range(1, 4), "heuristic", 2)
        for r in results:
            self.assertEqual(r["growth"]["start"], 2)
            self.assertEqual(r["growth"]["mid"], 2 + K.growth_mark(g) - 1)
            self.assertEqual(r["growth"]["end"], 2 + 12)
            self.assertEqual(r["tier_max"], 1)
            self.assertIsNone(r["tier2_turn"])
            self.assertEqual(r["picks"], {"mine": 12})

    def test_board_default_lists_every_visible_number(self):
        g = _Grower()
        s0, _ = B._new(g, 1)
        board = g.board(s0)
        self.assertIn("Fleet 2", board)
        self.assertIn("Tier 1", board)
        self.assertNotIn("_turn", board)
        self.assertIn("board", B.COMMANDS)


class BandTests(unittest.TestCase):
    def test_heuristic_band_is_wider_in_v4(self):
        self.assertEqual(B.HEURISTIC_BAND, (0.25, 0.55))


if __name__ == "__main__":
    unittest.main()
