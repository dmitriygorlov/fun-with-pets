# Easy ChatGPT bot with pre-prompts


## Problem
Access to the chatgpt requires browser and some skills for prompt tuning. But there are some everyday tasks that can be solved with help of chatgpt.

## Idea
Create simple interface that can be used for everyday tasks that can be solved with GPT with restricted access and pre-tuned prompts.

## Description
This telegram bot helps simplify access to chatgpt and make it more user-friendly. It has some pre-tuned prompts and can be used for everyday tasks by people without any skills in programming or machine learning or even access to the chatgpt.

## How it works 
If you want to launch your own version of bot.

0. Install [docker](https://docs.docker.com/engine/install/) ~~and love it~~
1. Open terminal in this folder
```bash
cd gpt_helper_bot
```
2. Make docker image for this bot. (type it) 
```bash
docker build -t gpt_helper_bot:love.dmitrii .
```
3. Type secret API TOKEN for telegram bot as env [how make new bot](https://t.me/BotFather). Looks like `*83942530236:AHDkeuJlBy82Hs3jfFP1z2JBfjfiq7HzA*` 
```bash
export TOKEN=<here is your super duper secret code>
```
4. Run image
```bash
docker run --rm -d -e TOKEN=$TOKEN is_it_simple:love.dmitrii
```
5. You are amazing <3