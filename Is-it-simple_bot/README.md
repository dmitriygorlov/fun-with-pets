Example of some easy NLP-like bot (it use translators, so it looks like NLP project :) ).

Idea: Google don't translate your sentenses properly in your vacation. (like `Let’s get hammered` translates into turkish something like `let's be beaten`)

Description: you send some phrase to bot and it translate to turkish language and back to help: *Has the meaning of the sentence remained the same?*

Instruction to launch your own version of it.

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