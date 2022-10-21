# art.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import requests
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()

response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isHighlight=true&q=*")
objects = response.json()['objectIDs']
#print(random.choice(objects))


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="description",
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.command()
async def add(ctx: commands.Context, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(str(left + right))

@bot.command()
async def art(ctx: commands.Context):
    str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(objects)}"
    response = requests.get(str)
    url = response.json()['primaryImage']
    while not url:
        str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(objects)}"
        response = requests.get(str)
        url = response.json()['primaryImage']
        print("rolling again")
    print(str)
    print(url)
    
    #await ctx.send(f"here's some random art from the met {url}")
    await ctx.send(url)


bot.run(TOKEN)