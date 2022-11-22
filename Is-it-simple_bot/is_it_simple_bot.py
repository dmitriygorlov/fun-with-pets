import logging
import os

import translators as tss
from aiogram import Bot, Dispatcher, executor, types

APP_TOKEN = os.getenv("TOKEN")

# Bot itself
bot = Bot(token=APP_TOKEN)
# Dispatcher
dp = Dispatcher(bot)
# ВSome yummy loggies
logging.basicConfig(level=logging.INFO)

lang_1 = "ru"
lang_2 = "tr"


@dp.message_handler()
async def all_todo(message: types.Message):
    await message.reply(
        f"""
*I work as __{lang_1}\>{lang_2}\>{lang_1}__ by Google Translate*
    """,
        parse_mode="MarkdownV2",
    )
    text = message["text"]
    trans = tss.google(text, from_language=lang_1, to_language=lang_2)
    text_back = tss.google(trans, from_language=lang_2, to_language=lang_1)

    await message.reply(
        f"""
*Start:* {text}
*Translated:* {trans}
*Translated back:* {text_back}""",
        parse_mode="MarkdownV2",
    )

    if text == text_back:
        await message.answer(f"""Wow, like word to word""")
    else:
        await message.answer(f"""Not exactly the same, right?""")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
