# Easy ChatGPT bot with pre-prompts

## Problem
Access to the chatgpt requires a browser and some skills for prompt tuning. However, there are some everyday tasks that can be solved with the help of chatgpt.

## Idea
Create a simple interface that can be used for everyday tasks that can be solved with GPT with restricted access.

## Description
This Telegram bot helps simplify access to chatgpt and make it more user-friendly. It can be used for everyday tasks by people without any skills in programming or machine learning or even access to the chatgpt.

## How it works (for now)

### 1. Install Docker and Docker Compose
First, you need to install Docker and Docker Compose. You can find the installation guides here:
- [Docker installation guide](https://docs.docker.com/engine/install/)
- [Docker Compose installation guide](https://docs.docker.com/compose/install/)

### 2. Clone/Download the Repository
Clone or download the repository and navigate to the project folder. If you're not familiar with GitHub, you can follow this [guide](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/) to learn how to do it.

### 3. Setup .env File
Create a `.env` file in the project root directory with your bot token, bot password, OpenAI API key, and your symbols. Here's an example of what the `.env` file should look like:

```shell
TELEGRAM_BOT_TOKEN=111119999:AAEAyQjr05FpkSF_JXtr7ySDcswFfWVQYe0EEQ (here is your bot token)
OPENAI_API_KEY=sk-lOcpperjhvevhqElZDxfT3BFWTggWFig4699mEbU3lajwc4 (here is your OPENAI token)
BOT_PASSWORD=love_is_everywhere
FIRST_SYMBOL=!
CONTINUE_SYMBOL=?
```

### 4. Run the Bot
In your terminal, navigate to the project root directory and run the following command to start the bot:

```shell
docker-compose up --build
```

The bot will start running in your terminal. If everything is set up correctly, you should start seeing logs from the bot indicating its status.

### 5. Use the Bot
Open your Telegram app, and search for the bot using the bot token you set in the .env file. Once you find the bot, start a conversation and send the password you set in the .env file to the bot. If the password is correct, you will be granted access, and you can now start using the bot.

To start a new conversation with the bot, type your message starting with the `first_symbol` you set in the .env file (for example, `!Hello`). The bot will interpret this as a new conversation and respond accordingly. 

To continue a conversation, start your message with the `continue_symbol` (for example, `?What do you mean by that?`). The bot will interpret this as a continuation of the previous conversation and provide a response based on the conversation history. 

You can view the conversation history and usage statistics by checking the `conversation_history.json` and `stats.csv` files in the bot's directory. The `conversation_history.json` file contains the conversation history for each user, while the `stats.csv` file contains usage statistics, such as the number of messages sent, the last message datetime, and the number of tokens used.

### 6. Stop the Bot
When you're done using the bot, you can stop it by pressing `Ctrl+C` in the terminal where the bot is running. This will stop the bot and shut down the Docker container.

### 7. You're Amazing <3
Congratulations, your chatbot is now running! You've successfully set up and run your own AI chatbot. Remember to keep it safe and don't share your bot's password or .env file with anyone.

Keep coding, and remember: you're amazing!
