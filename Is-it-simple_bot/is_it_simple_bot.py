import asyncio
import os

from aiogram import Bot, Dispatcher
from deep_translator import GoogleTranslator


def round_trip(text):
    translated = GoogleTranslator(source="ru", target="tr").translate(text)
    return translated, GoogleTranslator(source="tr", target="ru").translate(translated)


async def all_todo(message, translate=round_trip):
    if not message.text:
        await message.answer("Please send text.")
        return
    if len(message.text) > 4000:
        await message.answer("Please send at most 4000 characters.")
        return
    try:
        translated, back = await asyncio.to_thread(translate, message.text)
    except Exception:  # noqa: BLE001 - external translator failures must not leak user text
        await message.answer("Translation service unavailable. Please try later.")
        return
    # Plain text avoids treating user input as Telegram Markdown.
    output = f"Russian > Turkish > Russian\nStart: {message.text}\nTranslated: {translated}\nTranslated back: {back}"
    for offset in range(0, len(output), 4000):
        await message.reply(output[offset : offset + 4000])
    await message.answer(
        "Wow, like word to word"
        if message.text == back
        else "Not exactly the same, right?"
    )


async def main():
    bot = Bot(token=os.environ["TOKEN"])
    dp = Dispatcher()
    dp.message.register(all_todo)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
