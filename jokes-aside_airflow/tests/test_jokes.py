import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dags"))
from scripts import fetch_joke


class JokeTests(unittest.TestCase):
    @patch.object(fetch_joke, "PostgresHook")
    @patch.object(fetch_joke.requests, "get")
    def test_fetch_and_html(self, get, hook):
        get.return_value.json.return_value = {"setup": "<b>", "punchline": "&"}
        hook.return_value.get_first.return_value = (True,)
        fetch_joke.fetch_and_store_joke()
        self.assertEqual(get.call_args.kwargs["timeout"], 15)
        get.return_value.raise_for_status.assert_called_once()
        self.assertEqual(
            hook.return_value.run.call_args.kwargs["parameters"], ("<b>", "&")
        )
        hook.return_value.get_first.return_value = ("<b>", "&")
        self.assertEqual(fetch_joke.fetch_joke_from_db(), "&lt;b&gt; - &amp;")
        hook.return_value.get_first.return_value = None
        with self.assertRaises(ValueError):
            fetch_joke.fetch_joke_from_db()

    @patch.object(fetch_joke, "PostgresHook")
    @patch.object(fetch_joke.requests, "get")
    def test_invalid_response_never_touches_db(self, get, hook):
        get.return_value.json.return_value = {"setup": 1}
        with self.assertRaises(ValueError):
            fetch_joke.fetch_and_store_joke()
        hook.assert_not_called()

    def test_dag_paused_email_disabled(self):
        with patch.dict(os.environ, {"ENABLE_EMAIL": "false"}):
            import joke_dag
        self.assertEqual(
            set(joke_dag.dag.task_ids), {"fetch_and_store_joke", "fetch_joke_from_db"}
        )
        self.assertTrue(joke_dag.dag.is_paused_upon_creation)

    def test_email_is_explicit_opt_in(self):
        import importlib

        import joke_dag

        with patch.dict(
            os.environ,
            {"ENABLE_EMAIL": "true", "EMAIL_FOR_REPORT": "test@example.invalid"},
        ):
            module = importlib.reload(joke_dag)
            self.assertIn("send_joke_email", module.dag.task_ids)
            self.assertEqual(
                module.dag.get_task("send_joke_email").upstream_task_ids,
                {"fetch_joke_from_db"},
            )
        with patch.dict(os.environ, {"ENABLE_EMAIL": "false"}):
            importlib.reload(joke_dag)
