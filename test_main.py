import tempfile
import unittest
from pathlib import Path

from main import (
    move,
    greedy_policy,
    random_policy,
    run_episode,
    run_experiment,
    summarize_results,
    save_experiment,
    load_experiment,
)


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.start = {"x": 0, "y": 0}
        self.goal = {"x": 3, "y": 2}

    def test_move_right(self):
        state = {"x": 1, "y": 2}

        result = move(state, "RIGHT", 7, 7)

        self.assertEqual(result, {"x": 2, "y": 2})
        self.assertEqual(state, {"x": 1, "y": 2})

    def test_boundary(self):
        cases = [
            ({"x": 0, "y": 2}, "LEFT"),
            ({"x": 6, "y": 2}, "RIGHT"),
            ({"x": 2, "y": 0}, "DOWN"),
            ({"x": 2, "y": 6}, "UP"),
        ]

        for state, action in cases:
            with self.subTest(state=state, action=action):
                result = move(state, action, 7, 7)
                self.assertEqual(result, state)

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            move(self.start, "JUMP", 7, 7)

    def test_greedy_reaches_goal(self):
        result = run_episode(
            start=self.start,
            goal=self.goal,
            width=7,
            height=7,
            policy=greedy_policy,
            seed=0,
            max_steps=30,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["steps"], 5)
        self.assertEqual(result["final_distance"], 0)
        self.assertEqual(result["trajectory"][0], self.start)
        self.assertEqual(result["trajectory"][-1], self.goal)
        self.assertEqual(len(result["trajectory"]), 6)

    def test_max_steps(self):
        result = run_episode(
            start=self.start,
            goal=self.goal,
            width=7,
            height=7,
            policy=greedy_policy,
            seed=0,
            max_steps=3,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["steps"], 3)
        self.assertEqual(len(result["trajectory"]), 4)

    def test_start_at_goal(self):
        result = run_episode(
            start=self.goal,
            goal=self.goal,
            width=7,
            height=7,
            policy=greedy_policy,
            seed=0,
            max_steps=30,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["steps"], 0)
        self.assertEqual(result["final_distance"], 0)
        self.assertEqual(result["trajectory"], [self.goal])

    def test_random_seed_reproducibility(self):
        results = []

        for _ in range(2):
            result = run_episode(
                start=self.start,
                goal=self.goal,
                width=7,
                height=7,
                policy=random_policy,
                seed=42,
                max_steps=30,
            )
            results.append(result)

        self.assertEqual(results[0], results[1])

    def test_save_and_load(self):
        results = run_experiment(
            start=self.start,
            goal=self.goal,
            width=7,
            height=7,
            policy=greedy_policy,
            episodes=3,
            seed=0,
            max_steps=30,
        )

        summary = summarize_results(results)

        self.assertEqual(summary["episodes"], 3)
        self.assertEqual(summary["successes"], 3)
        self.assertEqual(summary["success_rate"], 1.0)
        self.assertEqual(summary["average_steps"], 5.0)

        config = {
            "start": self.start,
            "goal": self.goal,
            "width": 7,
            "height": 7,
            "policy": "greedy_policy",
            "episodes": 3,
            "seed": 0,
            "max_steps": 30,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "experiment"

            save_experiment(
                output_dir=output_dir,
                config=config,
                results=results,
                summary=summary,
            )

            loaded_config, loaded_results, saved_summary = (
                load_experiment(output_dir)
            )

            self.assertEqual(loaded_config, config)
            self.assertEqual(loaded_results, results)

            recomputed_summary = summarize_results(
                loaded_results
            )
            self.assertEqual(recomputed_summary, summary)

            for key, value in summary.items():
                with self.subTest(metric=key):
                    expected_text = (
                        "" if value is None else str(value)
                    )
                    self.assertEqual(
                        saved_summary[key],
                        expected_text,
                    )

if __name__ == "__main__":
    unittest.main()