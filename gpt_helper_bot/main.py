"""Single-process Telegram helper. Importing this module makes no network calls."""

import asyncio
import csv
import hmac
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError

logger = logging.getLogger(__name__)


def read_csv(path):
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["user_id"]: row for row in csv.DictReader(handle)}


def write_csv(path, rows, fields):
    temp = path.with_suffix(".tmp")
    with temp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows.values())
    temp.replace(path)


class Helper:
    def __init__(
        self,
        client,
        password,
        first_symbol,
        continue_symbol,
        directory=".",
        model="gpt-4.1-mini",
    ):
        if (
            not password
            or not first_symbol
            or not continue_symbol
            or first_symbol == continue_symbol
        ):
            raise ValueError("Password and distinct command prefixes are required")
        self.client, self.password, self.model = client, password, model
        self.first, self.continue_symbol = first_symbol, continue_symbol
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.allowed = read_csv(self.directory / "allowed_users.csv")
        self.stats = read_csv(self.directory / "stats.csv")
        history_path = self.directory / "conversation_history.json"
        self.history = (
            json.loads(history_path.read_text(encoding="utf-8"))
            if history_path.exists()
            else {}
        )
        self.lock = asyncio.Lock()

    async def handle(self, message):
        if message.from_user is None or not message.text:
            await message.answer("Please send text.")
            return
        # Serializes CSV/JSON writes and same-user conversations in this single-process bot.
        async with self.lock:
            await self._handle(message)

    async def _handle(self, message):
        uid = str(message.from_user.id)
        now = datetime.now(UTC).isoformat()
        if uid not in self.allowed:
            if hmac.compare_digest(message.text.encode(), self.password.encode()):
                self.allowed[uid] = {"user_id": uid, "datetime_added": now}
                write_csv(
                    self.directory / "allowed_users.csv",
                    self.allowed,
                    ["user_id", "datetime_added"],
                )
                await message.answer("Access granted. You can now use the bot.")
            else:
                await message.answer("Invalid password. Access denied.")
            return
        if message.text.startswith(self.first):
            history = [{"role": "system", "content": "Give short and useful answers."}]
            prompt = message.text[len(self.first) :]
        elif message.text.startswith(self.continue_symbol):
            history = list(
                self.history.get(
                    uid,
                    [{"role": "system", "content": "Give short and useful answers."}],
                )
            )
            prompt = message.text[len(self.continue_symbol) :]
        else:
            await message.answer("Please start your message with a special symbol")
            return
        if not prompt.strip():
            await message.answer("Please include a prompt after the symbol.")
            return
        history.append({"role": "user", "content": prompt})
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=history
            )
        except OpenAIError:
            # Exceptions can contain request content; do not log them.
            logger.warning("Model request failed")
            await message.answer("The model request failed. Please try again later.")
            return
        answer = response.choices[0].message.content
        if not answer:
            await message.answer("The model returned no text.")
            return
        history.append({"role": "assistant", "content": answer})
        self.history[uid] = history
        temporary = self.directory / "conversation_history.tmp"
        temporary.write_text(
            json.dumps(self.history, ensure_ascii=False), encoding="utf-8"
        )
        temporary.replace(self.directory / "conversation_history.json")
        row = self.stats.setdefault(
            uid,
            {
                "user_id": uid,
                "message_count": 0,
                "last_message_datetime": "",
                "prompt_tokens_amount": 0,
                "completion_tokens_amount": 0,
            },
        )
        row["message_count"] = int(row["message_count"]) + 1
        row["last_message_datetime"] = now
        for field, attribute in [
            ("prompt_tokens_amount", "prompt_tokens"),
            ("completion_tokens_amount", "completion_tokens"),
        ]:
            row[field] = int(row[field]) + (getattr(response.usage, attribute, 0) or 0)
        write_csv(
            self.directory / "stats.csv",
            self.stats,
            [
                "user_id",
                "message_count",
                "last_message_datetime",
                "prompt_tokens_amount",
                "completion_tokens_amount",
            ],
        )
        logger.info("Model request completed")
        for offset in range(0, len(answer), 4000):
            await message.answer(answer[offset : offset + 4000])


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.WARNING)
    async with AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"], timeout=60, max_retries=2
    ) as client:
        helper = Helper(
            client,
            os.environ["BOT_PASSWORD"],
            os.environ["FIRST_SYMBOL"],
            os.environ["CONTINUE_SYMBOL"],
            os.getenv("DATA_DIR", "."),
            os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        )
        bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
        dp = Dispatcher()
        dp.message.register(helper.handle)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
