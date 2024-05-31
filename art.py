#! /usr/bin/python3
# art.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import requests
import random
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()

response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isHighlight=true&q=*")
ids = response.json()['objectIDs']

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description="anadosbot help menu", intents=intents)

# List of users to exclude from the drawing
excluded_users = []

@bot.command()
async def exclude(ctx: commands.Context, user: discord.User):
    """Excludes a user from the movie picker drawing."""
    if user not in excluded_users:
        excluded_users.append(user)
        await ctx.send(f"{user.name} has been excluded from the movie picker drawing.")
    else:
        await ctx.send(f"{user.name} is already excluded from the movie picker drawing.")

@bot.command()
async def include(ctx: commands.Context, user: discord.User):
    """Includes a user in the movie picker drawing."""
    if user in excluded_users:
        excluded_users.remove(user)
        await ctx.send(f"{user.name} has been included in the movie picker drawing.")
    else:
        await ctx.send(f"{user.name} is already included in the movie picker drawing.")

@bot.command()
async def pick(ctx: commands.Context):
    """Picks a movie picker randomly from the Discord users."""
    members = [member for member in ctx.guild.members if not member.bot and member not in excluded_users]
    if members:
        movie_picker = random.choice(members)
        await ctx.send(f"{movie_picker.name} has been chosen to pick the movie!")
    else:
        await ctx.send("No eligible movie pickers found.")

@bot.command()
async def include_all(ctx: commands.Context):
    """Includes all users in the movie picker drawing."""
    excluded_users.clear()
    await ctx.send("All users have been included in the movie picker drawing.")

@bot.command()
async def list_included(ctx: commands.Context):
    """Lists all included users in the movie picker drawing."""
    included_users = [member.name for member in ctx.guild.members if not member.bot and member not in excluded_users]
    if included_users:
        await ctx.send("Included users: " + ", ".join(included_users))
    else:
        await ctx.send("No users are currently included in the movie picker drawing.")

word_to_guess = random.choice(['brian'])
guesses_allowed = 6
current_guesses = 0
green, yellow, black = '<:muppetfrodo1:1199098240067448954>', '<:muppetfrodoupsidedown:1199160684609548401>', '<:muppetfrodoevil2:1199162144831328256>'

def check_guess(guess):
    return ''.join([green if guess[i] == word_to_guess[i] else yellow if guess[i] in word_to_guess else black for i in range(len(guess))])

@bot.command(name='wordle')
async def wordle(ctx, *, guess: str = None):
    """See how fast you can guess the word 'brian'."""
    global current_guesses
    if not guess:
        await ctx.send('enter a guess like: !wordle guess')
        return
    guess = guess.lower()
    if guess == 'stop':
        current_guesses=0
        await ctx.send('ok '+black)
        return
    if len(guess) != len(word_to_guess):
        await ctx.send('guess has to be 5 letters')
        return
    if current_guesses < guesses_allowed:
        result = check_guess(guess)
        current_guesses += 1
        await ctx.send(f"{current_guesses}. {result}")
        if guess == word_to_guess:
            await ctx.send('yay you got it')
            current_guesses=0
            return
        if current_guesses == guesses_allowed:
            await ctx.send('game over i guess!')
            current_guesses=0
    else:
        await ctx.send('game over!!')
        current_guesses = 0

@tasks.loop(time= datetime.time(hour=16, minute=00, tzinfo=datetime.timezone.utc))
async def background_task():
    channel = bot.get_channel(713669009593204809)
    await channel.send("here's your daily art from the met")
    await art(channel)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")
    background_task.start()

# @bot.command()
# async def add(ctx: commands.Context, left: int, right: int):
    # """Adds two numbers together."""
    # await ctx.send(str(left + right))

# @bot.command()
# async def roll(ctx: commands.Context, dice: str):
    # """Rolls a die in NdN format."""
    # try:
        # rolls, limit = map(int, dice.split("d"))
    # except ValueError:
        # await ctx.send("Format has to be in NdN!")
        # return
    # result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
    # await ctx.send(result)

@bot.command()
async def art(ctx: commands.Context):
    """displays art from the met api."""
    url, title, artist, medium, date = "", "", "", "", ""
    while not url:
        str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(ids)}"
        response = requests.get(str)
        try:
            url = response.json()['primaryImage']
            title = response.json()['title'] or 'No Title'
            artist = response.json().get('artistDisplayName') or 'Unknown'
            medium = response.json()['medium'] or '(Unknown medium)'
            date = response.json()['objectDate'] or '(Unknown date)'
        except KeyError:
            print(f"keyerror i guess.\n{str}\n---")
            url=""
    url = url.replace(" ", "%20")
    print(f"{str}\n{url}")
    await ctx.send(url)
    await ctx.send(f"{title} by {artist}\n{medium} made {date}")

@bot.command()
async def artsearch(ctx: commands.Context, term: str):
    """search for a keyword and return a random result from the met"""
    ids=[]
    total=0
    tries=0
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?tags=true&q={term}"
    secondurl = f"https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&q={term}"
    response = requests.get(url)
    ids = response.json()['objectIDs']
    total=response.json()['total']
    if not ids:
        ids = []
    
    response = requests.get(secondurl)
    secondids = response.json()['objectIDs']
    if not secondids:
        secondids = []
    ids.extend(secondids)
    total+=response.json()['total']
    ids = list(set(ids))

    if total<=0:
        await ctx.send("no results")
    else: 
        url, title, artist, medium, date = "", "", "", "", ""
        while not url and tries < 10:
            str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(ids)}"
            response = requests.get(str)
            try:
                url = response.json()['primaryImage']
                title = response.json()['title'] or 'No Title'
                artist = response.json().get('artistDisplayName') or 'Unknown'
                medium = response.json()['medium'] or '(Unknown medium)'
                date = response.json()['objectDate'] or '(Unknown date)'
            except KeyError:
                print(f"keyerror\n{str}\n---")
                url=""
            tries+=1
        tries=0
        url = url.replace(" ", "%20")
        print(f"{str}\n{url}")
        if not url:
            url = "not found"
        await ctx.send(url)
        await ctx.send(f"{title} by {artist}\n{medium} made {date}")

bot.run(TOKEN)
