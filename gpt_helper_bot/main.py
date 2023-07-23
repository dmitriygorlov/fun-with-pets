import logging
import os
from datetime import datetime
import json

import openai
import pandas as pd
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_env(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing environment variable '{name}'")
    value = str(value)
    return value


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot_token = load_env("TELEGRAM_BOT_TOKEN")
if bot_token is None:
    raise ValueError("Missing environment variable 'TELEGRAM_BOT_TOKEN'")
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Load authorized users from CSV file
allowed_users_file = "allowed_users.csv"
if os.path.exists(allowed_users_file):
    allowed_users = pd.read_csv(allowed_users_file)
    allowed_users["user_id"] = allowed_users["user_id"].astype(str)
    allowed_users.set_index("user_id", inplace=True)
else:
    allowed_users = pd.DataFrame(columns=["user_id", "datetime_added"])
    allowed_users["user_id"] = allowed_users["user_id"].astype(str)
    allowed_users.set_index("user_id", inplace=True)


# Initialize stats DataFrame
stats_file = "stats.csv"
if os.path.exists(stats_file):
    stats = pd.read_csv(stats_file)
    stats["user_id"] = stats["user_id"].astype(str)
    stats.set_index("user_id", inplace=True)
else:
    stats = pd.DataFrame(
        columns=[
            "user_id",
            "message_count",
            "last_message_datetime",
            "prompt_tokens_amount",
            "completion_tokens_amount",
        ]
    )
    stats["user_id"] = stats["user_id"].astype(str)
    stats.set_index("user_id", inplace=True)

# Initialize a dictionary to store conversation history for each user
conversation_history_file = "conversation_history.json"
if os.path.exists(conversation_history_file):
    with open(conversation_history_file, "r") as f:
        conversation_history = json.load(f)
else:
    conversation_history = {}

# Some batch settings
batch_size = 2
batch_updates = []

# Pass settings to the bot
bot_password = load_env("BOT_PASSWORD")
first_symbol = load_env("FIRST_SYMBOL")
continue_symbol = load_env("CONTINUE_SYMBOL")


# Load openai settings
openai.api_key = load_env("OPENAI_API_KEY")
model = "gpt-3.5-turbo"
pre = "You are a helpful chatbot that helps people with their problems. Make short and useful answers."


# On message event handler for authorized users
@dp.message_handler(lambda message: str(message.from_user.id) in allowed_users.index)
async def handle_message(message: types.Message):
    global batch_updates
    user_id = str(message.from_user.id)

    if user_id not in conversation_history:
        logger.info(f"User {user_id} started a new conversation")
        conversation_history[user_id] = []

    if message.text.startswith(first_symbol):
        # When a new conversation starts, clear the history
        conversation_history[user_id] = [
            {"role": "system", "content": pre},
            {"role": "user", "content": message.text[len(first_symbol) :]},
        ]
    elif message.text.startswith(continue_symbol):
        # When the conversation continues, append the user's message to the history
        conversation_history[user_id].append(
            {"role": "user", "content": message.text[len(continue_symbol) :]}
        )
    else:
        # If the message does not start with a special symbol, ignore it
        await message.answer("Please start your message with a special symbol")
        return

    retrieval = openai.ChatCompletion.create(
        model=model,
        messages=conversation_history[user_id],
    )

    answer = retrieval["choices"][0]["message"]["content"]  # type: ignore

    conversation_history[user_id].append(
        {"role": "assistant", "content": answer}
    )  # Add the assistant's response to the conversation history

    # Save conversation history to file
    with open(conversation_history_file, "w") as f:
        json.dump(conversation_history, f)

    await message.answer(answer)

    prompt_tokens_amount = retrieval["usage"]["prompt_tokens"]  # type: ignore
    completion_tokens_amount = retrieval["usage"]["completion_tokens"]  # type: ignore

    logger.info(
        f"User {user_id} asked: {message.text}, we spent {prompt_tokens_amount} prompt tokens and {completion_tokens_amount} completion tokens"
    )

    # Add update to batch
    batch_updates.append(
        (
            user_id,
            datetime.now().isoformat(),
            prompt_tokens_amount,
            completion_tokens_amount,
        )
    )
    if len(batch_updates) >= int(batch_size):
        logger.info(f"Updating stats for {len(batch_updates)} requests")
        update_stats()


@dp.message_handler()
async def handle_password(message: types.Message):
    global allowed_users, stats  # Add stats here to refer to the global variable
    user_id = str(message.from_user.id)
    password = message.text

    # Check if the user is already authorized
    if user_id in allowed_users.index:
        await message.answer(
            "You are already authorized. Please use any of right first symbols."
        )
    else:
        if password == bot_password:
            # Add user to allowed users
            allowed_users.loc[user_id] = [datetime.now().isoformat()]  # type: ignore
            allowed_users.to_csv(allowed_users_file)

            # Add new user to stats
            stats.loc[user_id] = [0, None, 0, 0]  # type: ignore
            stats.to_csv(stats_file)

            await message.answer("Access granted. You can now use the bot.")
            logger.info(f"User {user_id} was granted access with password: {password}")
        else:
            await message.answer("Invalid password. Access denied.")
            logger.info(f"User {user_id} entered an invalid password: {password}")


def update_stats():
    global batch_updates, stats  # Add stats here to refer to the global variable
    for (
        user_id,
        timestamp,
        prompt_tokens_amount,
        completion_tokens_amount,
    ) in batch_updates:
        if user_id in stats.index:
            stats.at[user_id, "message_count"] += 1
            stats.at[user_id, "last_message_datetime"] = timestamp
            stats.at[user_id, "prompt_tokens_amount"] += prompt_tokens_amount
            stats.at[user_id, "completion_tokens_amount"] += completion_tokens_amount
        else:
            # Add new user to stats if not exist
            stats.loc[user_id] = [
                1,
                timestamp,
                prompt_tokens_amount,
                completion_tokens_amount,
            ]
    stats.to_csv(stats_file)
    batch_updates = []


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
