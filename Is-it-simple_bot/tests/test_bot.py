import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock

from is_it_simple_bot import all_todo


class TranslationTests(unittest.IsolatedAsyncioTestCase):
    async def test_roundtrip_plain_text_and_nontext(self):
        message = NS(text="hello_*[]", answer=AsyncMock(), reply=AsyncMock())
        translate = Mock(return_value=("merhaba", "hello_*[]"))
        await all_todo(message, translate)
        translate.assert_called_once_with("hello_*[]")
        self.assertNotIn("parse_mode", message.reply.call_args.kwargs)
        message.text = None
        await all_todo(message, translate)
        self.assertEqual(translate.call_count, 1)

    async def test_failure(self):
        message = NS(text="hello", answer=AsyncMock(), reply=AsyncMock())
        await all_todo(message, Mock(side_effect=RuntimeError("private")))
        self.assertIn("unavailable", message.answer.call_args.args[0])
