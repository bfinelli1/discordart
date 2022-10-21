# art.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import requests
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isHighlight=true&q=*")
ids = response.json()['objectIDs']


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="anadosbot help menu",
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


@bot.command()
async def add(ctx: commands.Context, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(str(left + right))

@bot.command()
async def art(ctx: commands.Context):
    """displays art from the met api."""
    url = ""
    while not url:
        str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(ids)}"
        response = requests.get(str)
        try:
            url = response.json()['primaryImage']
        except KeyError:
            print(f"keyerror i guess.\n{str}\n---")
            url=""
    url = url.replace(" ", "%20")
    print(f"{str}\n{url}")
    #await ctx.send(f"here's some random art from the met {url}")
    await ctx.send(url)


bot.run(TOKEN)