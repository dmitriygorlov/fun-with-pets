import logging
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=str(bot_token))
dp = Dispatcher(bot)

# Load authorized users from CSV file
allowed_users = pd.DataFrame(columns=["user_id", "datetime_added"])
allowed_users.set_index("user_id", inplace=True)
allowed_users_file = "allowed_users.csv"
stats_file = "stats.csv"
batch_size = 5

if os.path.exists(allowed_users_file):
    allowed_users = pd.read_csv(allowed_users_file)
    allowed_users.set_index("user_id", inplace=True)

# Initialize stats DataFrame
stats = pd.DataFrame(columns=["user_id", "message_count", "last_message_datetime"])
stats.set_index("user_id", inplace=True)
if os.path.exists(stats_file):
    stats = pd.read_csv(stats_file)
    stats.set_index("user_id", inplace=True)

batch_updates = []


# On message event handler for authorized users
@dp.message_handler(lambda message: str(message.from_user.id) in allowed_users.index)
async def handle_message(message: types.Message):
    global batch_updates
    user_id = str(message.from_user.id)
    # Reply the same message that was received
    await message.answer(message.text)

    # Add update to batch
    batch_updates.append((user_id, datetime.now().isoformat()))
    if batch_size is not None and len(batch_updates) >= int(batch_size):
        update_stats()
        logger.info(f"Updated stats for {len(batch_updates)} users")
    else:
        update_stats()
        logger.info(f"Updated stats for user {user_id}, batch_size: {batch_updates}")

    logger.info(f"Echoed message from user {user_id}: {message.text}")


# On message event handler for non-authorized users
@dp.message_handler(commands=["add_user"])
async def handle_add_user(message: types.Message):
    user_id = str(message.from_user.id)
    # Prompt the user for the password
    await message.answer("Please enter the password:")
    logger.info(f"Prompted user {user_id} to enter the password")


@dp.message_handler()
async def handle_password(message: types.Message):
    global allowed_users, stats  # Add stats here to refer to the global variable
    user_id = str(message.from_user.id)
    password = message.text

    if password == os.getenv("BOT_PASSWORD"):
        # Add user to allowed users
        allowed_users.loc[str(user_id)] = [datetime.now().isoformat()]
        allowed_users.to_csv(allowed_users_file)

        # Add new user to stats
        stats.loc[str(user_id)] = [0, None]
        stats.to_csv(stats_file)

        await message.answer("Access granted. You can now use the bot.")
        logger.info(f"User {user_id} was granted access with password: {password}")
    else:
        await message.answer("Invalid password. Access denied.")
        logger.info(f"User {user_id} entered an invalid password: {password}")


def update_stats():
    global batch_updates, stats  # Add stats here to refer to the global variable
    for user_id, timestamp in batch_updates:
        if user_id in stats.index:
            stats.at[user_id, "message_count"] += 1
            stats.at[user_id, "last_message_datetime"] = timestamp
        else:
            # Add new user to stats if not exist
            stats.loc[user_id] = [1, timestamp]
    stats.to_csv(stats_file)
    batch_updates = []


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
