# Easy nlp bot for every day

Example of some easy NLP-like bot (it use translators, so it looks like NLP project :) ).

## Problem
Google don't translate your sentenses properly in your vacation. (like `Let’s get hammered` translates into turkish something like `let's be beaten`)

## Idea
Translate from the input language to another and vice versa, assuming that the translator can cope with simple words and phrases, but not with complex ones.

## Description
You send some phrase to bot and it translate to turkish language and back to help: *Has the meaning of the sentence remained the same?*

## How it works 
If you want to launch your own version of bot.

0. Install [docker](https://docs.docker.com/engine/install/) ~~and love it~~
1. Open terminal in this folder
```bash
cd is-it-simple_bot
```
2. Make docker image for this bot. (type it) 
```bash
docker build -t is_it_simple:love.dmitrii .
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

## Compatibility update (2026-11-18)

Python 3.14; aiogram 3.32.0 replaces the v2 handler/executor API. deep-translator 1.11.4 replaces translators; Russian/Turkish round trips remain. Blocking translation runs off the event loop, non-text messages and failures are handled, and replies use plain text to avoid Markdown injection. The external Google translation service remains unofficial and may change/rate-limit; only mocks were exercised, not live translations or Telegram delivery.

Offline regression checks from this project directory, after installing requirements:

```sh
python -m unittest discover -s tests -v
python -m pip check
```

See [maintenance record](../maintenance-2026.md) for container validation and limitations.
