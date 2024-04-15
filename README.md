# isgptup
Check out the discord to see if OpenAI's GPT services (API, ChatGPT, Labs, Playground) are currently working properly!

# What to bring
To use isgptup, you'll need the following materials
* Python
  - You need to have Python installed, the version we tested is `3.10.12`.
* Python package
  - `discord.py` - the Discord bot framework package, which you can install like this `pip install discord`
  - `requests` - You need it to send requests to [OpenAI Status](https://status.openai.com). You can install it with `pip install requests`.
  - `python-dotenv` - used to retrieve values from the `.env` where the API key is stored. You can install it like this `pip install python-dotenv`
  - `pytz` - It's needed to handle timezone information and can be installed with `pip install pytz`.
  - `googletrans` - required to translate English issues into Korean. You can install it with `pip install googletrans==4.0.0-rc1`.
  - `feedparser` - Issues are served as RSS, which is required for parsing purposes. You can install it with `pip install feedparser`.
* API key / token values
  - Discord Bot Token: To run the Discord bot, you need a bot token, which you can get from [Discord Developer Protal](https://discord.com/developers/docs/intro).

# Enter your API key in .env
1. Open `.env.sample` with an editor.
2. `.env.sample` should look like this.
```env
DISCORD_TOKEN=
```
Where `DISCORD_BOT_TOKEN` is your Discord Bot token value. Be sure to enclose both ends in double quotes. Example:
```env
DISCORD_TOKEN="Discord_Bot_Token"
```
Or something like this.

3. Rename the `.env.sample` file to `.env`.
4. Run isgptup with `python run.py`.

# License
isgptup is distributed under the MIT licence.