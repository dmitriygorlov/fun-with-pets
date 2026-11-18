import logging
import tempfile
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import httpx2 as httpx
from main import Helper
from openai import APIConnectionError


class HelperTests(unittest.IsolatedAsyncioTestCase):
    async def test_auth_history_stats_and_no_secret_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            client = NS(
                chat=NS(
                    completions=NS(
                        create=AsyncMock(
                            return_value=NS(
                                choices=[NS(message=NS(content="answer"))],
                                usage=NS(prompt_tokens=3, completion_tokens=2),
                            )
                        )
                    )
                )
            )
            helper = Helper(client, "secret-password", "!", "+", directory)
            message = NS(from_user=NS(id=1), text="wrong-password", answer=AsyncMock())
            await helper.handle(message)
            client.chat.completions.create.assert_not_called()
            message.text = "secret-password"
            await helper.handle(message)
            message.text = "!private-prompt"
            with self.assertLogs("main", level=logging.INFO) as logs:
                await helper.handle(message)
            self.assertNotIn("private-prompt", str(logs.output))
            self.assertNotIn("secret-password", str(logs.output))
            loaded = Helper(client, "secret-password", "!", "+", directory)
            self.assertEqual(loaded.stats["1"]["message_count"], "1")
            self.assertEqual(loaded.history["1"][-1]["content"], "answer")
            message.text = "+followup"
            await loaded.handle(message)
            self.assertEqual(
                len(client.chat.completions.create.call_args.kwargs["messages"]), 5
            )
            client.chat.completions.create.side_effect = APIConnectionError(
                request=httpx.Request("POST", "https://example.invalid")
            )
            before = list(loaded.history["1"])
            await loaded.handle(message)
            self.assertEqual(loaded.history["1"], before)
            message.text = None
            await loaded.handle(message)

    async def test_legacy_csv_json_state(self):
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("allowed_users.csv").write_text(
                "user_id,datetime_added\n9007199254740993,2023-01-01T00:00:00\n"
            )
            root.joinpath("stats.csv").write_text(
                "user_id,message_count,last_message_datetime,prompt_tokens_amount,completion_tokens_amount\n9007199254740993,2,2023-01-01T00:00:00,7,8\n"
            )
            root.joinpath("conversation_history.json").write_text(
                '{"9007199254740993": [{"role":"user","content":"old prompt"}, {"role":"assistant","content":"old answer"}]}'
            )
            helper = Helper(None, "password", "!", "+", directory)
            self.assertIn("9007199254740993", helper.allowed)
            self.assertEqual(
                helper.stats["9007199254740993"]["prompt_tokens_amount"], "7"
            )
            self.assertEqual(
                helper.history["9007199254740993"][-1]["content"], "old answer"
            )
