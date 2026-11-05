import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import dockergame


ROOT = Path(__file__).resolve().parents[1]


class ExerciseTests(unittest.TestCase):
    def test_existing_exercise_catalog_and_files_are_loaded(self):
        exercises = dockergame.load_exercises(ROOT)

        self.assertEqual(len(exercises), 15)
        self.assertEqual(exercises[0].id, "core-01")
        self.assertEqual(exercises[-1].id, "core-15")
        self.assertEqual(exercises[1].depends_on, "core-01")
        for exercise in exercises:
            self.assertTrue((ROOT / "exercises" / exercise.id / "prompt.md").is_file())
            self.assertTrue((ROOT / "exercises" / exercise.id / "hint.md").is_file())
        self.assertTrue((ROOT / "exercises" / "core-15" / "app" / "app.py").is_file())

    def test_dependency_gate(self):
        exercise = dockergame.Exercise("core-02", "Run Nginx", "core", "core-01")

        self.assertFalse(dockergame.dependency_is_complete(exercise, set()))
        self.assertTrue(dockergame.dependency_is_complete(exercise, {"core-01"}))

    def test_native_checker_runs_without_bash(self):
        exercise = dockergame.Exercise("core-03", "Output and Logs", "core", "core-02")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exercise_dir = root / "exercises" / exercise.id
            exercise_dir.mkdir(parents=True)
            (exercise_dir / "logs.txt").write_text(
                "Starting process...\nProcess is running.\nProcess finished.\n",
                encoding="utf-8",
            )
            with patch("dockergame.find_bash", side_effect=AssertionError):
                dockergame.run_check(root, exercise)

    def test_core_03_accepts_windows_powershell_utf16_logs(self):
        exercise = dockergame.Exercise("core-03", "Output and Logs", "core", "core-02")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exercise_dir = root / "exercises" / exercise.id
            exercise_dir.mkdir(parents=True)
            (exercise_dir / "logs.txt").write_bytes(
                "Starting process...\r\n"
                "Process is running.\r\n"
                "Process finished.\r\n".encode("utf-16")
            )

            dockergame.run_core_03(root, exercise)

    def test_core_03_reports_unknown_log_encoding_as_check_error(self):
        exercise = dockergame.Exercise("core-03", "Output and Logs", "core", "core-02")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exercise_dir = root / "exercises" / exercise.id
            exercise_dir.mkdir(parents=True)
            (exercise_dir / "logs.txt").write_bytes(b"\xff\xfe\x00")

            with self.assertRaisesRegex(
                dockergame.CheckError, "expected UTF-8 or BOM-marked UTF-16"
            ):
                dockergame.run_core_03(root, exercise)

    def test_watch_displays_hint_and_returns_to_list(self):
        output = StringIO()
        with patch("dockergame.ProgressStore") as store_factory:
            store_factory.return_value.load.return_value = set()
            with patch("builtins.input", side_effect=["1", "h", "l", "q"]):
                with redirect_stdout(output):
                    result = dockergame.main(["watch"])

        self.assertEqual(result, 0)
        self.assertIn("Hello Docker", output.getvalue())
        self.assertIn("HINT: Hello World", output.getvalue())
        self.assertIn("DOCKERGAME: THE CONTAINER QUEST", output.getvalue())

    def test_locked_level_cannot_be_entered(self):
        output = StringIO()
        with patch("dockergame.ProgressStore") as store_factory:
            store_factory.return_value.load.return_value = set()
            with patch("builtins.input", side_effect=["2", "q"]):
                with redirect_stdout(output):
                    result = dockergame.main(["play"])

        self.assertEqual(result, 0)
        self.assertIn("Level locked", output.getvalue())
        self.assertNotIn("LEVEL 02", output.getvalue())


class ProgressTests(unittest.TestCase):
    def test_default_progress_is_local_to_this_clone(self):
        self.assertEqual(
            dockergame.ProgressStore().path,
            ROOT / ".dockerlings" / "progress.json",
        )

    def test_progress_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            store = dockergame.ProgressStore(Path(directory) / "progress.json")

            self.assertEqual(store.load(), set())
            store.save({"core-02", "core-01"})

            self.assertEqual(store.load(), {"core-01", "core-02"})
            saved = json.loads(store.path.read_text(encoding="utf-8"))
            self.assertEqual(saved, {"completed_ids": ["core-01", "core-02"]})

    def test_invalid_progress_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text('{"completed_ids": "core-01"}', encoding="utf-8")

            with self.assertRaises(dockergame.AppError):
                dockergame.ProgressStore(path).load()


if __name__ == "__main__":
    unittest.main()
